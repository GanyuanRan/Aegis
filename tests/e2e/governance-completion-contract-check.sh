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
verification_expanded="skills/verification-before-completion/expanded-closeout.md"

assert_contains "$verification_skill" \
    "governance/cleanup/migration/compat/retirement" \
    "verification main routes the canonical governance category family"

assert_contains "$verification_expanded" \
    "governance, cleanup, migration, compatibility, namespace cutover, public release, deprecation, policy boundary, or retirement" \
    "verification detail preserves the complete governance category family"

assert_contains "$verification_expanded" "Repair Track" \
    "verification gate requires Repair Track for governance closure"

assert_contains "$verification_expanded" "Retirement Track" \
    "verification gate requires Retirement Track for governance closure"

assert_contains "$verification_expanded" "Residual Risk|residual risk" \
    "verification gate requires residual-risk semantics for governance closure"

assert_contains "$verification_skill" "single completion closeout" \
    "verification gate keeps a single completion closeout aggregator"

assert_contains "$verification_expanded" "no card here is a second final owner|another completion report" \
    "verification gate prevents adjacent structures from replacing the receipt"

assert_contains "$verification_skill" "output conformance, not a routing trigger" \
    "verification gate does not turn receipt aggregation into a routing trigger"

assert_contains "$verification_skill" "Output and Prompt Hygiene" \
    "verification gate requires user-language output for completion cards"

assert_contains "$verification_skill" "section labels, field labels, and explanatory prose" \
    "verification gate localizes labels fields and prose"

assert_contains "$verification_expanded" "Architecture Alignment" \
    "verification gate requires Architecture Alignment for durable architecture closure"

assert_contains "$verification_expanded" "aligned | Design Defect | Implementation Drift" \
    "architecture alignment uses shared defect drift result vocabulary"

assert_contains "$verification_skill" "Localize section labels, field labels, and explanatory prose" \
    "verification gate requires user-language localized output"

assert_contains "$verification_expanded" "even when implementation was small" \
    "verification gate prevents small changes from bypassing dual-track closure"

if (( failures > 0 )); then
    echo ""
    echo "Governance completion contract check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Governance completion contract check passed."
