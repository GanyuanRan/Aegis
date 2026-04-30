#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

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

    if grep -qE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

echo "=== TDD Policy Check ==="

tdd_skill="skills/test-driven-development/SKILL.md"
using_aegis="skills/using-aegis/SKILL.md"
verification_skill="skills/verification-before-completion/SKILL.md"

assert_contains "$using_aegis" "contract|cross-module|shared module|core logic" \
    "using-aegis routes contract and cross-module changes into TDD"

assert_contains "$tdd_skill" "contract|cross-module|shared module|core logic" \
    "TDD applies to contracts, cross-module changes, and core logic"
assert_contains "$tdd_skill" "input.*output|output.*input" \
    "TDD requires defining input and output before tests"
assert_contains "$tdd_skill" "existing test|baseline" \
    "TDD requires checking existing tests and baseline first"
assert_contains "$tdd_skill" "end-to-end|integration" \
    "TDD covers feature-level end-to-end or integration tests"
assert_contains "$tdd_skill" "spike" \
    "TDD defines spike-to-test closure"
assert_contains "$tdd_skill" "hotfix|emergency|urgent" \
    "TDD defines emergency hotfix regression follow-up"
assert_contains "$tdd_skill" "manual verification|manual steps" \
    "TDD defines manual verification when automation is blocked"

assert_contains "$verification_skill" "target test|related regression" \
    "verification asks for target test and related regression evidence"
assert_contains "$verification_skill" "manual verification|manual steps" \
    "verification asks for manual steps when automation is blocked"

if (( failures > 0 )); then
    echo ""
    echo "TDD policy check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "TDD policy check passed."
