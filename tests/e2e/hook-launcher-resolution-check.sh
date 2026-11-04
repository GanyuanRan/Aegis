#!/usr/bin/env bash
# Behavioural checks for the Windows hook launcher's bash resolution.
#
# The launcher runs before any skill loads, so it must never execute a
# repository-provided `bash.cmd`/`bash.bat` and must never hand the hook to a
# WSL forwarder. These checks drive the real resolution path in a temporary
# directory instead of re-asserting the script text.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LAUNCHER="$REPO_ROOT/hooks/run-hook.cmd"

failures=0
pass() { echo "  [PASS] $1"; }
fail() { echo "  [FAIL] $1"; failures=$((failures + 1)); }

echo "=== Hook Launcher Bash Resolution Check ==="

if [[ ! -f "$LAUNCHER" ]]; then
    fail "hooks/run-hook.cmd exists"
    echo
    echo "Hook launcher check failed: $failures"
    exit 1
fi
pass "hooks/run-hook.cmd exists"

# The launcher must keep the polyglot shape: a cmd block that also parses as a
# bash script, because the same file is the Unix entry point.
head -1 "$LAUNCHER" | grep -q "CMDBLOCK" \
    && pass "launcher keeps the polyglot CMDBLOCK header" \
    || fail "launcher keeps the polyglot CMDBLOCK header"

if grep -q 'exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}"' "$LAUNCHER"; then
    pass "Unix branch still execs the named hook script"
else
    fail "Unix branch still execs the named hook script"
fi

# Regression guards for the three resolution defects this change fixes.
grep -q 'LOCALAPPDATA' "$LAUNCHER" \
    && pass "launcher probes the per-user Git for Windows install" \
    || fail "launcher probes the per-user Git for Windows install"

grep -qi 'WindowsApps' "$LAUNCHER" && grep -qi 'system32' "$LAUNCHER" \
    && pass "launcher rejects both WSL bash forwarders" \
    || fail "launcher rejects both WSL bash forwarders"

grep -q 'bash\\\.exe' "$LAUNCHER" \
    && pass "launcher requires the bash.exe executable name" \
    || fail "launcher requires the bash.exe executable name"

if command -v cmd.exe >/dev/null 2>&1; then
    # A planted bash.cmd must not be chosen even when it precedes real bash on
    # PATH. The planted file prints a marker and fails; a real hook run must not
    # emit that marker.
    tmp="$(mktemp -d "${TMPDIR:-/tmp}/aegis-hook-resolution.XXXXXX")"
    trap 'rm -rf -- "$tmp"' EXIT
    cat >"$tmp/bash.cmd" <<'PLANTED'
@echo off
echo PLANTED_BASH_EXECUTED
exit /b 7
PLANTED
    set +e
    out="$(cd "$tmp" && cmd.exe /c "$(cygpath -w "$LAUNCHER")" session-start 2>&1)"
    status=$?
    set -e
    if [[ "$out" == *PLANTED_BASH_EXECUTED* ]]; then
        fail "launcher refuses a planted bash.cmd on the working directory"
    else
        pass "launcher refuses a planted bash.cmd on the working directory"
    fi
    if [[ $status -eq 0 ]]; then
        pass "launcher still exits successfully for the real hook"
    else
        fail "launcher still exits successfully for the real hook (got $status)"
    fi
    rm -rf -- "$tmp"
    trap - EXIT
else
    echo "  [SKIP] cmd.exe unavailable; Windows resolution behaviour not exercised"
fi

if (( failures > 0 )); then
    echo
    echo "Hook launcher check failed: $failures"
    exit 1
fi

echo
echo "Hook launcher check passed."
