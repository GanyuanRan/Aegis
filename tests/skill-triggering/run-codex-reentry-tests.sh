#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPETITIONS="${AEGIS_CODEX_REENTRY_REPETITIONS:-1}"
AUTO_COMPACT_LIMIT="${AEGIS_CODEX_AUTO_COMPACT_TOKEN_LIMIT:-2000}"
TIMESTAMP="$(date +%s)"
OUTPUT_ROOT="${AEGIS_CODEX_REENTRY_OUTPUT_DIR:-$REPO_ROOT/.tmp/aegis-tests/$TIMESTAMP/codex-reentry}"

export CODEX_SMOKE_SUFFIX=""
source "$REPO_ROOT/tests/helpers/codex-cli.sh"

if ! [[ "$REPETITIONS" =~ ^[1-9][0-9]*$ ]]; then
    echo "AEGIS_CODEX_REENTRY_REPETITIONS must be a positive integer" >&2
    exit 2
fi
if ! [[ "$AUTO_COMPACT_LIMIT" =~ ^[1-9][0-9]*$ ]]; then
    echo "AEGIS_CODEX_AUTO_COMPACT_TOKEN_LIMIT must be a positive integer" >&2
    exit 2
fi
if [ -e "$OUTPUT_ROOT" ]; then
    echo "Codex re-entry output already exists: $OUTPUT_ROOT" >&2
    exit 2
fi

prepare_project() {
    local project_root="$1"

    mkdir -p "$project_root/.agents/skills"
    cp -R "$REPO_ROOT/skills/using-aegis" \
        "$project_root/.agents/skills/using-aegis"
    cp -R "$REPO_ROOT/skills/systematic-debugging" \
        "$project_root/.agents/skills/systematic-debugging"
}

require_current_turn_route() {
    local case_id="$1"
    local log_file="$2"
    local missing_status="${3:-10}"
    local result_label="NEGATIVE"

    if [ "$missing_status" = "20" ]; then
        result_label="INVALID"
    fi

    if ! codex_log_records_route "systematic-debugging" "$log_file"; then
        echo "[$result_label] $case_id did not record systematic-debugging in the current turn"
        print_codex_json_first_assistant_excerpt "$log_file" || true
        return "$missing_status"
    fi
}

run_work_type_shift() {
    local attempt="$1"
    local case_id="work-type-shift-$attempt"
    local case_root="$OUTPUT_ROOT/$case_id"
    local project_root="$case_root/project"
    local turn1_log="$case_root/turn1.jsonl"
    local turn2_log="$case_root/turn2.jsonl"
    local thread_id

    if ! mkdir -p "$case_root" || ! prepare_project "$project_root"; then
        echo "[INVALID] $case_id could not prepare its isolated project"
        return 20
    fi

    run_codex_persistent_exec_capture \
        "Give a short implementation outline for a CSV report exporter that accepts a collection of records and writes a downloadable file. Do not modify files." \
        "$project_root" "$turn1_log" || {
            echo "[INVALID] $case_id initial Codex turn failed"
            return 20
        }
    thread_id="$(codex_thread_id_from_log "$turn1_log")" || {
        echo "[INVALID] $case_id has no unique thread id"
        return 20
    }

    if codex_log_records_route "systematic-debugging" "$turn1_log" 2>/dev/null; then
        echo "[INVALID] $case_id recorded systematic-debugging before any anomaly appeared"
        return 20
    fi

    run_codex_resume_capture "$thread_id" \
        "The exported report stops after 10 rows even though the source has 363. Investigate what happened and explain the repair direction. Do not modify files." \
        "$turn2_log" || {
            echo "[INVALID] $case_id resumed Codex turn failed"
            return 20
        }
    print_codex_session_evidence "$thread_id" false || {
        echo "[INVALID] $case_id persisted session evidence is incomplete"
        return 20
    }
    require_current_turn_route "$case_id" "$turn2_log" || return $?
    echo "[PASS] $case_id"
}

run_compaction_reentry() {
    local attempt="$1"
    local case_id="compaction-reentry-$attempt"
    local case_root="$OUTPUT_ROOT/$case_id"
    local project_root="$case_root/project"
    local turn1_log="$case_root/turn1.jsonl"
    local turn2_log="$case_root/turn2.jsonl"
    local thread_id

    if ! mkdir -p "$case_root" || ! prepare_project "$project_root"; then
        echo "[INVALID] $case_id could not prepare its isolated project"
        return 20
    fi

    run_codex_persistent_exec_capture \
        "A hypothetical CSV report export stops after 10 rows although its input contains 363. Explain what evidence you would inspect first. Do not modify files." \
        "$project_root" "$turn1_log" "$AUTO_COMPACT_LIMIT" || {
            echo "[INVALID] $case_id initial Codex turn failed"
            return 20
        }
    thread_id="$(codex_thread_id_from_log "$turn1_log")" || {
        echo "[INVALID] $case_id has no unique thread id"
        return 20
    }
    require_current_turn_route "$case_id turn 1" "$turn1_log" 20 || return $?

    run_codex_resume_capture "$thread_id" \
        "Continue. Based on that situation, state the next investigation step and why. Do not modify files." \
        "$turn2_log" "$AUTO_COMPACT_LIMIT" || {
            echo "[INVALID] $case_id resumed Codex turn failed"
            return 20
        }
    print_codex_session_evidence "$thread_id" true || {
        echo "[INVALID] $case_id has no proven compaction before its second root turn"
        return 20
    }
    require_current_turn_route "$case_id turn 2" "$turn2_log" || return $?
    echo "[PASS] $case_id"
}

mkdir -p "$OUTPUT_ROOT"
echo "=== Codex Multi-Turn Route Re-entry Smoke ==="
echo "Output: $OUTPUT_ROOT"
echo "Repetitions per case: $REPETITIONS"

observed_positive=0
observed_negative=0
invalid_unobserved=0
for attempt in $(seq 1 "$REPETITIONS"); do
    if run_work_type_shift "$attempt"; then
        observed_positive=$((observed_positive + 1))
    else
        status=$?
        if [ "$status" = "10" ]; then
            observed_negative=$((observed_negative + 1))
        else
            invalid_unobserved=$((invalid_unobserved + 1))
        fi
    fi
    if run_compaction_reentry "$attempt"; then
        observed_positive=$((observed_positive + 1))
    else
        status=$?
        if [ "$status" = "10" ]; then
            observed_negative=$((observed_negative + 1))
        else
            invalid_unobserved=$((invalid_unobserved + 1))
        fi
    fi
done

echo "Summary: observed-positive=$observed_positive observed-negative=$observed_negative invalid-unobserved=$invalid_unobserved requested=$((REPETITIONS * 2))"

if [ "$observed_negative" -ne 0 ] || [ "$invalid_unobserved" -ne 0 ]; then
    echo "Codex route re-entry smoke completed without an all-positive result."
    exit 1
fi

echo "Codex route re-entry smoke passed for $REPETITIONS repetition(s) per case."
