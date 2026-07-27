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

PARTITION=""
REPETITIONS=""
MAX_ATTEMPTS=""
BATCH_ID=""
MODEL="${AEGIS_AGENTIC_BENCHMARK_MODEL:-}"
OUTPUT_ROOT=""
ARMS="baseline-no-aegis,aegis-auto"
DRY_RUN=0
CASES=()

usage() {
    cat <<'EOF'
Usage: run-agentic-benchmark.sh --partition <development|held-out|held-out-normal|held-out-boundary> \
  --repetitions <n> --max-attempts <n> --batch-id <id> --model <model> [options]

Options:
  --case <id>          Restrict to a case in the selected partition; repeatable.
  --arms <ids>         Must remain baseline-no-aegis,aegis-auto.
  --output-root <dir>  Repo-local .tmp directory for private evidence.
  --dry-run            Freeze and print the schedule; make zero model calls.

Environment for a real run:
  AEGIS_AGENTIC_BENCHMARK_LIVE=1   Required for every paid run.
  AEGIS_AGENTIC_BENCHMARK_FULL=1   Additionally required for held-out.
  AEGIS_AGENTIC_BENCHMARK_MODEL    Alternative to --model.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --partition) PARTITION="$2"; shift 2 ;;
        --case) CASES+=("$2"); shift 2 ;;
        --arms) ARMS="$2"; shift 2 ;;
        --repetitions) REPETITIONS="$2"; shift 2 ;;
        --max-attempts) MAX_ATTEMPTS="$2"; shift 2 ;;
        --batch-id) BATCH_ID="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --output-root) OUTPUT_ROOT="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --help|-h) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
done

if [[ -z "$PARTITION" || -z "$REPETITIONS" || -z "$MAX_ATTEMPTS" || -z "$BATCH_ID" ]]; then
    echo "ERROR: partition, repetitions, max-attempts and batch-id are required." >&2
    usage
    exit 2
fi
if [[ "$ARMS" != "baseline-no-aegis,aegis-auto" ]]; then
    echo "ERROR: benchmark arms are frozen as baseline-no-aegis,aegis-auto." >&2
    exit 2
fi
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
    --partition "$PARTITION"
    --repetitions "$REPETITIONS"
    --max-attempts "$MAX_ATTEMPTS"
    --batch-id "$BATCH_ID"
    --model "$MODEL"
    --output-root "$OUTPUT_ROOT"
)
for case_id in "${CASES[@]}"; do
    prepare_args+=(--case "$case_id")
done

if [[ "$DRY_RUN" == "1" ]]; then
    "${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py "${prepare_args[@]}"
    "${PYTHON_CMD[@]}" - "$OUTPUT_ROOT/batch.json" <<'PY'
import json
import sys
from pathlib import Path

batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(json.dumps({
    "batchId": batch["batchId"],
    "caseCount": batch["caseCount"],
    "targetRuns": batch["targetRunCount"],
    "maxAttempts": batch["maxAttempts"],
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
if [[ "$PARTITION" == "held-out" && "${AEGIS_AGENTIC_BENCHMARK_FULL:-0}" != "1" ]]; then
    echo "ERROR: set AEGIS_AGENTIC_BENCHMARK_FULL=1 for the complete held-out batch." >&2
    exit 91
fi

if [[ ! -f "$OUTPUT_ROOT/batch.json" ]]; then
    "${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py "${prepare_args[@]}"
fi
"${PYTHON_CMD[@]}" - "$OUTPUT_ROOT/batch.json" "$PARTITION" "$BATCH_ID" "$MODEL" "$REPETITIONS" "$MAX_ATTEMPTS" "${CASES[@]}" <<'PY'
import json
import sys
from pathlib import Path

batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
partition, batch_id, model = sys.argv[2:5]
repetitions, max_attempts = map(int, sys.argv[5:7])
requested_cases = sorted(sys.argv[7:])
assert batch["partition"] == partition, "prepared batch partition differs from this invocation"
assert batch["batchId"] == batch_id, "prepared batch id differs from this invocation"
assert batch["modelPolicy"]["requestedModel"] == model, "prepared batch model differs from this invocation"
assert batch["repetitions"] == repetitions, "prepared batch repetitions differ from this invocation"
assert batch["maxAttempts"] == max_attempts, "prepared batch attempt ceiling differs from this invocation"
assert batch["requestedCaseIds"] == requested_cases, "prepared batch case selection differs from this invocation"
PY
"${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py run --output-root "$OUTPUT_ROOT"
