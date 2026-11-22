#!/usr/bin/env bash
# Shared helpers for Aegis shell checks.
#
# Source this file after the check has set REPO_ROOT and changed into it:
#
#     source "$REPO_ROOT/tests/helpers/check-lib.sh"
#
# It provides the pass/fail counters, grep-based assertions, and the Python
# interpreter selection that each check previously redefined. Checks that need
# different semantics (for example a fail() that exits immediately) define
# their own function after sourcing, which overrides the shared one.

: "${failures:=0}"

# Prefer python3, then the Windows launcher, then python.
if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

# assert_contains FILE EXTENDED_REGEX LABEL
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

# assert_not_contains FILE EXTENDED_REGEX LABEL
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
