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
CONFIG="$TMP_ROOT/config.toml"
DISCOVERY_ROOT="$TMP_ROOT/discovery-skills"

"${PYTHON_CMD[@]}" scripts/aegis-update.py register \
    --registry "$REGISTRY" \
    --config "$CONFIG" \
    --host antigravity-cli \
    --method-pack-root "$REPO_ROOT" \
    --discovery-root "$DISCOVERY_ROOT" \
    --sync-mode junction \
    --discovery-shape direct-child \
    --reload-hint "restart or reload Antigravity CLI" \
    --json >"$TMP_ROOT/register.json"

"${PYTHON_CMD[@]}" scripts/aegis-update.py status \
    --registry "$REGISTRY" \
    --json >"$TMP_ROOT/status.json"

"${PYTHON_CMD[@]}" - "$TMP_ROOT/register.json" "$TMP_ROOT/status.json" "$REPO_ROOT" "$TMP_ROOT" <<'PY'
import json
import sys
from pathlib import Path

register = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
status = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
repo_root = Path(sys.argv[3]).resolve()
tmp_root = Path(sys.argv[4]).resolve()

if register.get("status") != "registered":
    raise SystemExit("register did not report status: registered")
sync = register.get("sync", "")
if "direct-child links current" not in sync:
    raise SystemExit(f"register sync readback unexpected: {sync!r}")
if register.get("verified") is not True:
    raise SystemExit("register did not report verified: true")
doctor = register.get("doctor", {})
if doctor.get("ok") is not True:
    raise SystemExit("register doctor did not report ok: true")
if doctor.get("discoveryShapeStatus") != "current":
    raise SystemExit("register doctor did not report discoveryShapeStatus: current")

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
    "syncMode": "junction",
    "discoveryShape": "direct-child",
}
for key, expected in checks.items():
    actual = entry.get(key)
    if actual != expected:
        raise SystemExit(f"{key} mismatch: expected {expected!r}, got {actual!r}")
expected_root = (tmp_root / "discovery-skills").as_posix()
if entry.get("discoveryRoot") != expected_root:
    raise SystemExit(
        f"discoveryRoot mismatch: expected {expected_root!r}, got {entry.get('discoveryRoot')!r}"
    )
if "reloadHint" not in entry or "Antigravity CLI" not in entry["reloadHint"]:
    raise SystemExit("missing Antigravity-specific reload hint")

source_skills = repo_root / "skills"
discovery_root = Path(entry["discoveryRoot"])
expected = sorted(
    child.name
    for child in source_skills.iterdir()
    if child.is_dir() and (child / "SKILL.md").is_file()
)
if not expected:
    raise SystemExit("canonical skills tree is empty")
children = sorted(child for child in discovery_root.iterdir() if child.is_dir())
if [child.name for child in children] != expected:
    raise SystemExit("direct-child exposure does not match the canonical skills tree")
for child in children:
    if child.resolve() != (source_skills / child.name).resolve():
        raise SystemExit(f"{child.name} does not resolve into the canonical skills tree")
PY

pass "host-scoped Antigravity direct-child registration/readback is stable"

echo ""
echo "Antigravity doc surface check passed."
