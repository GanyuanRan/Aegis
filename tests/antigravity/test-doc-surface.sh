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

fail() {
    echo "  [FAIL] $1"
    exit 1
}

pass() {
    echo "  [PASS] $1"
}

echo "=== Antigravity Doc Surface Check ==="

if bash tests/e2e/antigravity-host-boundary-check.sh >/tmp/aegis-antigravity-boundary.out 2>&1; then
    pass "boundary contract stays aligned"
else
    cat /tmp/aegis-antigravity-boundary.out
    fail "boundary contract stays aligned"
fi

mkdir -p "$REPO_ROOT/.tmp"
TMP_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/antigravity-doc.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

REGISTRY="$TMP_ROOT/installations.json"

"${PYTHON_CMD[@]}" scripts/aegis-update.py register \
    --registry "$REGISTRY" \
    --host antigravity-cli \
    --method-pack-root "$REPO_ROOT" \
    --sync-mode repo-only \
    --reload-hint "restart or reload Antigravity CLI" \
    --json >"$TMP_ROOT/register.json"

"${PYTHON_CMD[@]}" scripts/aegis-update.py status \
    --registry "$REGISTRY" \
    --json >"$TMP_ROOT/status.json"

"${PYTHON_CMD[@]}" - "$TMP_ROOT/status.json" <<'PY'
import json
import sys
from pathlib import Path

status = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if isinstance(status, list):
    items = status
elif isinstance(status, dict):
    items = status.get("installations", [])
else:
    raise SystemExit("unexpected status payload type")
if len(items) != 1:
    raise SystemExit("expected exactly one registered installation")
entry = items[0]
checks = {
    "host": "antigravity-cli",
    "syncMode": "repo-only",
    "discoveryShape": "host-managed",
}
for key, expected in checks.items():
    actual = entry.get(key)
    if actual != expected:
        raise SystemExit(f"{key} mismatch: expected {expected!r}, got {actual!r}")
if "reloadHint" not in entry or "Antigravity CLI" not in entry["reloadHint"]:
    raise SystemExit("missing Antigravity-specific reload hint")
PY

pass "host-scoped Antigravity registration contract is stable"

echo ""
echo "Antigravity doc surface check passed."
