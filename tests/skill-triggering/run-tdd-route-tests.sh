#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCTOR="$REPO_ROOT/scripts/aegis-doctor.py"
REPETITIONS="${AEGIS_TDD_ROUTE_REPETITIONS:-1}"

export CODEX_SMOKE_SUFFIX=""
source "$REPO_ROOT/tests/helpers/codex-cli.sh"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codex-tdd-route.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

run_case() {
    local id="$1"
    local mode="$2"
    local prompt="$3"
    local expected_decision="$4"
    local expected_authority="$5"
    local forbidden_pattern="$6"
    local attempt
    local route_request

    route_request="$prompt Return exactly these labeled fields: TDD Route, Mode, Decision, Strict authority, Strict signals, Light eligibility, and Reason. Do not implement or modify files."

    for attempt in $(seq 1 "$REPETITIONS"); do
        local case_root="$TMP_ROOT/$id-$attempt"
        local project_root="$case_root/project"
        local config_path="$case_root/config.toml"
        local agents_path="$project_root/AGENTS.md"
        local state_path="$case_root/agents-md-state.json"
        local log_path="$case_root/codex-output.log"
        local route_tail="$case_root/route-tail.log"
        mkdir -p "$project_root/.agents/skills"
        cp -R "$REPO_ROOT/skills/using-aegis" "$project_root/.agents/skills/using-aegis"
        cp -R "$REPO_ROOT/skills/brainstorming" "$project_root/.agents/skills/brainstorming"
        cp -R "$REPO_ROOT/skills/writing-plans" "$project_root/.agents/skills/writing-plans"
        cp -R "$REPO_ROOT/skills/systematic-debugging" "$project_root/.agents/skills/systematic-debugging"
        cp -R "$REPO_ROOT/skills/test-driven-development" "$project_root/.agents/skills/test-driven-development"

        codex_python "$DOCTOR" tdd-mode "$mode" \
            --config "$config_path" \
            --agents-md "$agents_path" \
            --agents-md-state "$state_path" \
            >/dev/null

        run_codex_exec_capture "$route_request" "$project_root" "$log_path"
        tail -n 80 "$log_path" >"$route_tail"

        if ! grep -aEqi "(Decision|TDD Route):[[:space:]]*($expected_decision)([[:space:]]|$)" "$route_tail"; then
            echo "[FAIL] $id attempt $attempt did not record Decision: $expected_decision"
            sed -n '1,220p' "$log_path"
            return 1
        fi
        if [[ -n "$expected_authority" ]] && \
            ! grep -aEqi "Strict authority:[[:space:]]*($expected_authority)([[:space:];,.]|$)" "$route_tail"; then
            echo "[FAIL] $id attempt $attempt did not record the expected strict authority"
            sed -n '1,220p' "$log_path"
            return 1
        fi
        if [[ -n "$forbidden_pattern" ]] && grep -aEqi "$forbidden_pattern" "$route_tail"; then
            echo "[FAIL] $id attempt $attempt emitted forbidden route rationale"
            grep -aEni "$forbidden_pattern" "$log_path" | head -20
            sed -n '1,220p' "$log_path"
            return 1
        fi
        echo "[PASS] $id attempt $attempt"
    done
}

echo "=== Codex TDD Route Smoke ==="

run_case \
    "auto-high-risk" \
    "auto" \
    "The behavior, acceptance criteria, and design are already approved. Record only the TDD route for a production change across a shared authorization core, a database migration, permissions, and a producer/consumer API contract." \
    "strict" \
    "recorded auto decision|.*auto-routing (policy|rule)|auto mode" \
    "Decision:[[:space:]]*light([[:space:]]|$)|user.*(did not|didn't|has not).*explicit.*TDD"

run_case \
    "auto-tiny" \
    "auto" \
    "Record only the TDD route for a hypothetical one-word README spelling correction. It is tiny, single-owner, changes no behavior, and has an obvious one-line readback." \
    "light|skipped" \
    "not applicable|none|absent|not invoked|no strict authority" \
    "Decision:[[:space:]]*strict"

run_case \
    "off-high-risk" \
    "off" \
    "Record only the TDD route for a hypothetical risky producer/consumer contract repair with focused regression coverage. I am not requesting test-first development." \
    "skipped" \
    "not applicable|none|absent|not invoked|no strict authority" \
    "Decision:[[:space:]]*strict"

run_case \
    "off-explicit-strict" \
    "off" \
    "Record only the TDD route for a hypothetical atomic behavior fix. I explicitly require strict TDD: write and observe the failing test before production code." \
    "strict" \
    "explicit.*(user|project)|(user|project).*(explicit|strict.*request|required)|direct user" \
    ""

echo "Codex TDD route smoke passed for $REPETITIONS repetition(s) per case."
