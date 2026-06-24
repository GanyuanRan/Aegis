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

echo "=== Bootstrap Adapter Contract Check ==="

"${PYTHON_CMD[@]}" \
    tests/helpers/validate_bootstrap_adapter_contract.py \
    "$REPO_ROOT" \
    tests/e2e/fixtures/bootstrap-adapter-contract.json

echo ""
echo "Bootstrap adapter contract check passed."
