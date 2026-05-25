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

    if grep -qF -- "$pattern" "$file"; then
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
HELPER_TEXT_OUT="$TMP_ROOT/helper-path.txt"
ACTIVATION_TEXT_OUT="$TMP_ROOT/activation-mode.txt"
ACTIVATION_JSON_OUT="$TMP_ROOT/activation-mode.json"
TDD_TEXT_OUT="$TMP_ROOT/tdd-mode.txt"
TDD_JSON_OUT="$TMP_ROOT/tdd-mode.json"
PRESERVE_CONFIG_PATH="$TMP_ROOT/preserve-config.toml"

DOCTOR="$REPO_ROOT/scripts/aegis-doctor.py"

echo "=== Aegis Doctor Check ==="

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "Aegis method-pack repository must not ship a live docs/aegis workspace"
fi
pass "repository has no precreated docs/aegis workspace"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --write-config >"$TEXT_OUT"
assert_contains "$TEXT_OUT" "Aegis doctor check passed" "doctor text mode passes"
assert_contains "$TEXT_OUT" "using-aegis-hot-path-current: ok" "doctor verifies current using-aegis hot path"
assert_contains "$TEXT_OUT" "Trigger health baseline:" "doctor text mode reports trigger health baseline"
assert_contains "$TEXT_OUT" "Trigger health layers:" "doctor text mode reports trigger health layers"
assert_contains "$CONFIG_PATH" "activation_mode = \"auto\"" "doctor writes activation mode"
assert_contains "$CONFIG_PATH" "tdd_mode = \"auto\"" "doctor writes TDD mode"
assert_contains "$CONFIG_PATH" "method_pack_root =" "doctor writes method-pack root"
assert_contains "$CONFIG_PATH" "workspace_helper =" "doctor writes workspace support path"

"${PYTHON_CMD[@]}" "$DOCTOR" helper-path --config "$CONFIG_PATH" >"$HELPER_TEXT_OUT"
assert_contains "$HELPER_TEXT_OUT" "Aegis workspace helper path:" "helper-path text mode reports helper path"
assert_contains "$HELPER_TEXT_OUT" "--root <target-project-root>" "helper-path text mode preserves target root hint"

cat >"$PRESERVE_CONFIG_PATH" <<'EOF'
activation_mode = "explicit"
tdd_mode = "off"
EOF
"${PYTHON_CMD[@]}" "$DOCTOR" --config "$PRESERVE_CONFIG_PATH" --write-config >/dev/null
assert_contains "$PRESERVE_CONFIG_PATH" "activation_mode = \"explicit\"" \
    "doctor write-config preserves an existing explicit activation mode"
assert_contains "$PRESERVE_CONFIG_PATH" "tdd_mode = \"off\"" \
    "doctor write-config preserves an existing off TDD mode"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --json >"$JSON_OUT"
assert_contains "$JSON_OUT" '"ok": true' "doctor JSON mode reports ok"
assert_contains "$JSON_OUT" '"workspaceSupport": "available"' "doctor JSON mode reports workspace support"
assert_contains "$JSON_OUT" '"configStatus": "configured"' "doctor JSON mode reports configured status"
assert_contains "$JSON_OUT" '"tddMode": "auto"' "doctor JSON mode reports TDD mode"
assert_contains "$JSON_OUT" '"triggerHealth": {' "doctor JSON mode reports trigger health block"
assert_contains "$JSON_OUT" '"host discovery"' "doctor JSON mode reports host discovery trigger layer"
assert_contains "$JSON_OUT" '"context pressure and re-entry"' "doctor JSON mode reports context-pressure trigger layer"
assert_contains "$JSON_OUT" '"name": "using-aegis-hot-path-current"' "doctor JSON mode reports hot-path freshness"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --discovery-root "$REPO_ROOT/skills" >"$TMP_ROOT/discovery.txt"
assert_contains "$TMP_ROOT/discovery.txt" "discovery-root-current: ok" "doctor verifies host discovery root points at current skills"

"${PYTHON_CMD[@]}" "$DOCTOR" activation-mode explicit --config "$CONFIG_PATH" >"$ACTIVATION_TEXT_OUT"
assert_contains "$ACTIVATION_TEXT_OUT" "Aegis activation mode set to explicit" \
    "activation-mode text command sets explicit mode"
assert_contains "$ACTIVATION_TEXT_OUT" "Restart or start a new host session" \
    "activation-mode text command states restart boundary"
assert_contains "$CONFIG_PATH" "activation_mode = \"explicit\"" \
    "activation-mode command writes explicit mode"

"${PYTHON_CMD[@]}" "$DOCTOR" activation-mode auto --config "$CONFIG_PATH" --json >"$ACTIVATION_JSON_OUT"
assert_contains "$ACTIVATION_JSON_OUT" '"ok": true' "activation-mode JSON reports ok"
assert_contains "$ACTIVATION_JSON_OUT" '"activationMode": "auto"' "activation-mode JSON reports auto mode"
assert_contains "$ACTIVATION_JSON_OUT" '"restartRequired": true' "activation-mode JSON reports restart boundary"
assert_contains "$CONFIG_PATH" "activation_mode = \"auto\"" \
    "activation-mode command writes auto mode"
assert_contains "$CONFIG_PATH" "tdd_mode = \"auto\"" \
    "activation-mode command preserves TDD mode"

"${PYTHON_CMD[@]}" "$DOCTOR" tdd-mode off --config "$CONFIG_PATH" >"$TDD_TEXT_OUT"
assert_contains "$TDD_TEXT_OUT" "Aegis TDD mode set to off" \
    "tdd-mode text command sets off mode"
assert_contains "$TDD_TEXT_OUT" "verification-before-completion still applies" \
    "tdd-mode text command preserves completion verification boundary"
assert_contains "$CONFIG_PATH" "tdd_mode = \"off\"" \
    "tdd-mode command writes off mode"
assert_contains "$CONFIG_PATH" "activation_mode = \"auto\"" \
    "tdd-mode command preserves activation mode"

"${PYTHON_CMD[@]}" "$DOCTOR" tdd-mode auto --config "$CONFIG_PATH" --json >"$TDD_JSON_OUT"
assert_contains "$TDD_JSON_OUT" '"ok": true' "tdd-mode JSON reports ok"
assert_contains "$TDD_JSON_OUT" '"tddMode": "auto"' "tdd-mode JSON reports auto mode"
assert_contains "$TDD_JSON_OUT" '"restartRequired": true' "tdd-mode JSON reports restart boundary"
assert_contains "$CONFIG_PATH" "tdd_mode = \"auto\"" \
    "tdd-mode command writes auto mode"

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "doctor must not create docs/aegis in the Aegis method-pack repository"
fi
pass "doctor only writes to temporary target projects and optional config"

echo ""
echo "Aegis doctor check passed."
