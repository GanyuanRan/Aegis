#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
source "$REPO_ROOT/tests/helpers/check-lib.sh"

echo "=== Host Adapter Smoke Check ==="

"${PYTHON_CMD[@]}" tests/helpers/validate_host_adapter_smoke.py "$REPO_ROOT"

echo ""
echo "Host adapter smoke check passed."
