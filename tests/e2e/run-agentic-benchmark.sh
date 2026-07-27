#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

PROFILE=""
BATCH_ID=""
MODEL="${AEGIS_AGENTIC_BENCHMARK_MODEL:-}"
OUTPUT_ROOT=""
DRY_RUN=0
CASE_ID=""

usage() {
    cat <<'EOF'
Usage: run-agentic-benchmark.sh --profile <development-pilot|standard-held-out|extended-held-out> \
  --batch-id <id> [--model <model>] [options]

Options:
  --case <id>          Required exactly once for development-pilot; forbidden otherwise.
  --output-root <dir>  Repo-local .tmp directory for private evidence.
  --dry-run            Freeze and print the schedule; make zero model calls.

Environment for a real run:
  AEGIS_AGENTIC_BENCHMARK_LIVE=1       Required for every paid run.
  AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1   Additionally required for held-out profiles.
  AEGIS_AGENTIC_BENCHMARK_EXTENDED=1   Additionally required for extended-held-out.
  AEGIS_AGENTIC_BENCHMARK_MODEL        Alternative to --model.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile) PROFILE="$2"; shift 2 ;;
        --case)
            if [[ -n "$CASE_ID" ]]; then
                echo "ERROR: --case may be provided only once." >&2
                exit 2
            fi
            CASE_ID="$2"; shift 2 ;;
        --batch-id) BATCH_ID="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --help|-h) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$PROFILE" || -z "$BATCH_ID" ]]; then
    echo "ERROR: profile and batch-id are required." >&2
    usage
    exit 2
fi
case "$PROFILE" in
    development-pilot)
        if [[ -z "$CASE_ID" ]]; then
            echo "ERROR: development-pilot requires exactly one --case." >&2
            exit 2
        fi ;;
    standard-held-out|extended-held-out)
        if [[ -n "$CASE_ID" ]]; then
            echo "ERROR: $PROFILE does not accept --case." >&2
            exit 2
        fi ;;
    *) echo "ERROR: unknown benchmark profile: $PROFILE" >&2; exit 2 ;;
esac
if [[ -z "$MODEL" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
        MODEL="dry-run-pinned-model"
    else
        echo "ERROR: --model or AEGIS_AGENTIC_BENCHMARK_MODEL is required." >&2
        exit 2
    fi
fi
if [[ -z "$OUTPUT_ROOT" ]]; then
    OUTPUT_ROOT=".tmp/agentic-benchmark-${BATCH_ID}"
fi

prepare_args=(
    prepare
    --profile "$PROFILE"
    --batch-id "$BATCH_ID"
    --model "$MODEL"
    --output-root "$OUTPUT_ROOT"
)
if [[ -n "$CASE_ID" ]]; then
    prepare_args+=(--case "$CASE_ID")
fi

if [[ "$DRY_RUN" == "1" ]]; then
    "${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py "${prepare_args[@]}"
    "${PYTHON_CMD[@]}" - "$OUTPUT_ROOT/batch.json" <<'PY'
import json
import sys
from pathlib import Path

batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(json.dumps({
    "batchId": batch["batchId"],
    "profileId": batch["profileId"],
    "caseCount": batch["caseCount"],
    "targetRuns": batch["targetRunCount"],
    "maxAttempts": batch["maxAttempts"],
    "workers": batch["workers"],
    "wallClockBudgetSeconds": batch["wallClockBudgetSeconds"],
    "modelCalls": 0,
    "dryRun": True,
}, sort_keys=True))
PY
    exit 0
fi

if [[ "${AEGIS_AGENTIC_BENCHMARK_LIVE:-0}" != "1" ]]; then
    echo "ERROR: set AEGIS_AGENTIC_BENCHMARK_LIVE=1 for paid benchmark execution." >&2
    exit 90
fi
if [[ "$PROFILE" != "development-pilot" && "${AEGIS_AGENTIC_BENCHMARK_HELD_OUT:-0}" != "1" ]]; then
    echo "ERROR: set AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 for held-out execution." >&2
    exit 91
fi
if [[ "$PROFILE" == "extended-held-out" && "${AEGIS_AGENTIC_BENCHMARK_EXTENDED:-0}" != "1" ]]; then
    echo "ERROR: set AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 for extended execution." >&2
    exit 92
fi

if [[ ! -f "$OUTPUT_ROOT/batch.json" ]]; then
    "${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py "${prepare_args[@]}"
fi
"${PYTHON_CMD[@]}" - "$OUTPUT_ROOT/batch.json" "$PROFILE" "$BATCH_ID" "$MODEL" "$CASE_ID" <<'PY'
import json
import sys
from pathlib import Path

batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
profile, batch_id, model, case_id = sys.argv[2:6]
requested_cases = [case_id] if case_id else []
assert batch["profileId"] == profile, "prepared batch profile differs from this invocation"
assert batch["batchId"] == batch_id, "prepared batch id differs from this invocation"
assert batch["modelPolicy"]["requestedModel"] == model, "prepared batch model differs from this invocation"
assert batch["requestedCaseIds"] == requested_cases, "prepared batch case selection differs from this invocation"
PY
"${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py run --output-root "$OUTPUT_ROOT"
