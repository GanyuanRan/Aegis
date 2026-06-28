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

echo "=== Controlled Replay Check ==="
"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest tests/e2e/fixtures/replay-samples.json \
    --workspace-root .tmp/e2e-controlled-replay

echo ""
echo "Controlled replay check passed."
