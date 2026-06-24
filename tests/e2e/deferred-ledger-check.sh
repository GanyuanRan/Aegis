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

echo "=== Deferred Ledger Check ==="

if [[ ! -f docs/current/AEGIS_DEFERRED_LEDGER.md ]]; then
    echo "missing docs/current/AEGIS_DEFERRED_LEDGER.md"
    exit 1
fi

grep -q "AEGIS_DEFERRED_LEDGER.md" docs/current/README.md
"${PYTHON_CMD[@]}" tests/helpers/test_aegis_deferred_ledger.py
"${PYTHON_CMD[@]}" scripts/aegis-deferred-ledger.py --root . --json --fail-on-vague >/dev/null

echo "  [PASS] deferred ledger docs, parser tests, and repository scan passed"
echo ""
echo "Deferred ledger check passed."
