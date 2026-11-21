#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/tests/helpers/check-lib.sh"

echo "=== Host Instruction Invariants Check ==="

"${PYTHON_CMD[@]}" \
    tests/helpers/validate_host_instruction_invariants.py \
    "$REPO_ROOT" \
    tests/e2e/fixtures/host-instruction-invariants.json

echo ""
echo "Host instruction invariants check passed."
