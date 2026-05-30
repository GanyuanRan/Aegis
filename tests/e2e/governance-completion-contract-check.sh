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

echo "=== Governance Completion Contract Check ==="

verification_skill="skills/verification-before-completion/SKILL.md"

assert_contains "$verification_skill" \
    "governance|cleanup|migration|compatibility|namespace cutover|public release|deprecation|policy boundary|retirement" \
    "verification gate detects governance and retirement-category work"

assert_contains "$verification_skill" "Repair Track" \
    "verification gate requires Repair Track for governance closure"

assert_contains "$verification_skill" "Retirement Track" \
    "verification gate requires Retirement Track for governance closure"

assert_contains "$verification_skill" "Residual Risk" \
    "verification gate requires Residual Risk for governance closure"

assert_contains "$verification_skill" "User-Language Output" \
    "verification gate requires user-language output for completion cards"

assert_contains "$verification_skill" "section labels, field labels, and explanatory prose" \
    "verification gate localizes labels fields and prose"

assert_contains "$verification_skill" "Architecture Alignment" \
    "verification gate requires Architecture Alignment for durable architecture closure"

assert_contains "$verification_skill" "aligned | Design Defect | Implementation Drift" \
    "architecture alignment uses shared defect drift result vocabulary"

assert_contains "$verification_skill" "Localize section labels and prose to the user's language" \
    "verification gate requires user-language localized output"

assert_contains "$verification_skill" "Do not skip this structure just because the implementation was small" \
    "verification gate prevents small changes from bypassing dual-track closure"

if (( failures > 0 )); then
    echo ""
    echo "Governance completion contract check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Governance completion contract check passed."
