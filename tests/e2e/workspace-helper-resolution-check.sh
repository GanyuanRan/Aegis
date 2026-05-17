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

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE -- "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE -- "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== Workspace Helper Resolution Check ==="

mkdir -p "$REPO_ROOT/.tmp"
TMP_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/workspace-helper-resolution.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

CONFIG_PATH="$TMP_ROOT/config.toml"
HELPER_JSON="$TMP_ROOT/helper-path.json"
MISSING_OUT="$TMP_ROOT/missing-workspace.out"
DOCTOR="$REPO_ROOT/scripts/aegis-doctor.py"

"${PYTHON_CMD[@]}" "$DOCTOR" --config "$CONFIG_PATH" --write-config --json >"$TMP_ROOT/doctor.json"
"${PYTHON_CMD[@]}" "$DOCTOR" helper-path --config "$CONFIG_PATH" --json >"$HELPER_JSON"

assert_contains "$HELPER_JSON" '"ok": true' "helper-path JSON reports ok"
assert_contains "$HELPER_JSON" '"workspaceHelper":' "helper-path JSON exposes workspace helper"
assert_contains "$HELPER_JSON" '"source": "config"' "helper-path prefers configured helper"
assert_contains "$HELPER_JSON" '"targetProjectRootArgument": "--root <target-project-root>"' "helper-path documents target root argument"
assert_contains "$HELPER_JSON" '"shellHint":' "helper-path provides shell hint"

TARGET_ROOT="$TMP_ROOT/target-project"
mkdir -p "$TARGET_ROOT"
HELPER_PATH="$("${PYTHON_CMD[@]}" - "$HELPER_JSON" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data["workspaceHelper"])
PY
)"

if "${PYTHON_CMD[@]}" "$HELPER_PATH" check --root "$TARGET_ROOT" >"$MISSING_OUT" 2>&1; then
    fail "helper check should report missing docs/aegis for uninitialized target"
else
    assert_contains "$MISSING_OUT" "missing workspace directory: docs/aegis" "missing target workspace is reported as uninitialized"
fi

assert_contains "skills/using-aegis/references/skill-discipline.md" \
    "Aegis workspace helper belongs to the installed method-pack root" \
    "discipline reference separates helper owner from target project"
assert_contains "skills/using-aegis/references/skill-discipline.md" \
    "<aegis-workspace-helper>.*--root <target-project-root>" \
    "discipline reference uses installed-helper placeholder"

for file in \
    skills/brainstorming/SKILL.md \
    skills/writing-plans/SKILL.md \
    skills/test-driven-development/SKILL.md \
    skills/systematic-debugging/SKILL.md \
    skills/long-task-continuation/SKILL.md \
    skills/verification-before-completion/SKILL.md \
    docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md \
    docs/current/AEGIS_PROCESS_BASELINE.md; do
    assert_contains "$file" "<aegis-workspace-helper>" "$file uses installed-helper placeholder"
    assert_not_contains "$file" "scripts/aegis-workspace.py" "$file does not imply target-project helper ownership"
done

if (( failures > 0 )); then
    echo ""
    echo "Workspace helper resolution check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workspace helper resolution check passed."
