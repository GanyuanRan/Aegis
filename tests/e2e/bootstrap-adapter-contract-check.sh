#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/tests/helpers/check-lib.sh"

echo "=== Bootstrap Adapter Contract Check ==="

"${PYTHON_CMD[@]}" \
    tests/helpers/validate_bootstrap_adapter_contract.py \
    "$REPO_ROOT" \
    tests/e2e/fixtures/bootstrap-adapter-contract.json

echo ""
echo "Bootstrap adapter contract check passed."
