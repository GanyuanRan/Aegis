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

echo "=== Host Instruction Invariants Check ==="

"${PYTHON_CMD[@]}" \
    tests/helpers/validate_host_instruction_invariants.py \
    "$REPO_ROOT" \
    tests/e2e/fixtures/host-instruction-invariants.json

echo ""
echo "Host instruction invariants check passed."
