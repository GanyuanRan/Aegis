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

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qF "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

mkdir -p "$REPO_ROOT/.tmp"
TMP_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/aegis-doctor.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

CONFIG_PATH="$TMP_ROOT/config.toml"
TEXT_OUT="$TMP_ROOT/doctor.txt"
JSON_OUT="$TMP_ROOT/doctor.json"

DOCTOR="$REPO_ROOT/scripts/aegis-doctor.py"

echo "=== Aegis Doctor Check ==="

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "Aegis method-pack repository must not ship a live docs/aegis workspace"
fi
pass "repository has no precreated docs/aegis workspace"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --write-config >"$TEXT_OUT"
assert_contains "$TEXT_OUT" "Aegis doctor check passed" "doctor text mode passes"
assert_contains "$TEXT_OUT" "using-aegis-hot-path-current: ok" "doctor verifies current using-aegis hot path"
assert_contains "$CONFIG_PATH" "activation_mode = \"auto\"" "doctor writes activation mode"
assert_contains "$CONFIG_PATH" "method_pack_root =" "doctor writes method-pack root"
assert_contains "$CONFIG_PATH" "workspace_helper =" "doctor writes workspace support path"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --json >"$JSON_OUT"
assert_contains "$JSON_OUT" '"ok": true' "doctor JSON mode reports ok"
assert_contains "$JSON_OUT" '"workspaceSupport": "available"' "doctor JSON mode reports workspace support"
assert_contains "$JSON_OUT" '"configStatus": "configured"' "doctor JSON mode reports configured status"
assert_contains "$JSON_OUT" '"name": "using-aegis-hot-path-current"' "doctor JSON mode reports hot-path freshness"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --discovery-root "$REPO_ROOT/skills" >"$TMP_ROOT/discovery.txt"
assert_contains "$TMP_ROOT/discovery.txt" "discovery-root-current: ok" "doctor verifies host discovery root points at current skills"

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "doctor must not create docs/aegis in the Aegis method-pack repository"
fi
pass "doctor only writes to temporary target projects and optional config"

echo ""
echo "Aegis doctor check passed."
