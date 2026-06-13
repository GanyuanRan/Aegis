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

SKIP_EXIT=80
CLI_MODE=""
CLI_BIN=""

skip_blocker() {
    echo "  [SKIP] $1"
    exit $SKIP_EXIT
}

fail() {
    echo "  [FAIL] $1"
    exit 1
}

pass() {
    echo "  [PASS] $1"
}

resolve_cli() {
    if [[ -n "${ANTIGRAVITY_CMD:-}" ]]; then
        CLI_MODE="direct"
        CLI_BIN="$ANTIGRAVITY_CMD"
        return 0
    fi

    if command -v agy >/dev/null 2>&1; then
        CLI_MODE="direct"
        CLI_BIN="$(command -v agy)"
        return 0
    fi

    if command -v powershell.exe >/dev/null 2>&1; then
        if powershell.exe -NoProfile -Command '& { $cmd = Get-Command agy -ErrorAction SilentlyContinue; if ($cmd) { exit 0 } else { exit 1 } }' >/tmp/aegis-antigravity-version.out 2>&1; then
            CLI_MODE="powershell-bridge"
            CLI_BIN="agy"
            return 0
        fi
    fi

    return 1
}

probe_cli_version() {
    case "$CLI_MODE" in
        direct)
            "$CLI_BIN" --version
            ;;
        powershell-bridge)
            powershell.exe -NoProfile -Command '& { $cmd = Get-Command agy -ErrorAction Stop; & $cmd.Source --version; exit $LASTEXITCODE }'
            ;;
        *)
            return 127
            ;;
    esac
}

probe_plugin_surface() {
    case "$CLI_MODE" in
        direct)
            "$CLI_BIN" plugin list
            ;;
        powershell-bridge)
            powershell.exe -NoProfile -Command '& { $cmd = Get-Command agy -ErrorAction Stop; & $cmd.Source plugin list; exit $LASTEXITCODE }'
            ;;
        *)
            return 127
            ;;
    esac
}

echo "=== Antigravity CLI Surface Check ==="

if ! resolve_cli; then
    skip_blocker "Antigravity CLI executable not found; set ANTIGRAVITY_CMD or install agy"
fi

if version_out="$(probe_cli_version 2>&1)"; then
    pass "CLI runnable probe succeeded"
else
    skip_blocker "Antigravity CLI exists but '--version' failed: $version_out"
fi

if plugin_out="$(probe_plugin_surface 2>&1)"; then
    pass "plugin surface probe succeeded"
else
    if grep -Eiq "unknown command|unknown subcommand|invalid choice|not recognized|unrecognized option|no such command" <<<"$plugin_out"; then
        fail "documented plugin surface is missing from the local Antigravity CLI"
    fi
    skip_blocker "plugin surface probe blocked by local runtime/auth/profile conditions: $plugin_out"
fi

mkdir -p "$REPO_ROOT/.tmp"
TMP_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/antigravity-cli.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

if ! "${PYTHON_CMD[@]}" scripts/aegis-doctor.py \
    --write-config \
    --config "$TMP_ROOT/config.toml" \
    --json >"$TMP_ROOT/doctor.json"; then
    fail "aegis-doctor.py complete-install readback failed"
fi

"${PYTHON_CMD[@]}" - "$TMP_ROOT/doctor.json" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
if data.get("ok") is not True:
    raise SystemExit("doctor did not report ok: true")
if data.get("workspaceSupport") != "available":
    raise SystemExit("doctor did not report workspaceSupport: available")
if data.get("configStatus") != "configured":
    raise SystemExit("doctor did not report configStatus: configured")
PY

pass "Aegis complete-install readback is healthy from the method-pack root"

echo ""
echo "Antigravity CLI surface check passed."
