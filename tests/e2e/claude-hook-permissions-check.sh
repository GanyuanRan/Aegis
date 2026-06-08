#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

mode_for() {
    local path="$1"
    git ls-files -s "$path" | awk '{print $1}'
}

assert_mode() {
    local path="$1"
    local expected="$2"
    local actual
    actual="$(mode_for "$path")"

    if [[ "$actual" != "$expected" ]]; then
        echo "[FAIL] $path must be tracked as $expected, got ${actual:-missing}"
        exit 1
    fi

    echo "[PASS] $path tracked as $expected"
}

assert_mode "hooks/run-hook.cmd" "100755"
assert_mode "hooks/session-start" "100755"

command="$(
    "${PYTHON_CMD[@]}" - <<'PY'
import json
from pathlib import Path

data = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
print(data["hooks"]["SessionStart"][0]["hooks"][0]["command"])
PY
)"

if [[ "$command" != '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" session-start' ]]; then
    echo "[FAIL] Claude Code SessionStart hook must use hooks/run-hook.cmd"
    echo "  got: $command"
    exit 1
fi

echo "[PASS] Claude Code SessionStart hook uses hooks/run-hook.cmd"
