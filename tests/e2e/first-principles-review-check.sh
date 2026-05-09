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

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== First Principles Review Check ==="

skill="skills/first-principles-review/SKILL.md"
using_aegis="skills/using-aegis/SKILL.md"
process_doc="docs/current/AEGIS_PROCESS_BASELINE.md"
readme_en="README.md"
readme_zh="README.zh-CN.md"

if [[ -f "$skill" ]]; then
    pass "first-principles-review skill exists"
else
    fail "first-principles-review skill exists"
fi

assert_contains "$skill" "^name: first-principles-review$" \
    "skill frontmatter name is stable"
assert_contains "$skill" "description: Use when" \
    "skill description uses trigger-only wording"
assert_contains "$skill" "explicitly asks for first principles|first-principles|第一性原理|Occam|奥卡姆" \
    "skill has explicit first-principles triggers"
assert_contains "$skill" "complexity|ambiguous|competing constraints|repeated fixes|fallback|duplicate owner" \
    "skill has decision-point triggers"
assert_contains "$skill" "Do Not Use" \
    "skill defines non-trigger cases"
assert_contains "$skill" "not a standalone workflow|Do not replace" \
    "skill is compositional rather than standalone"
assert_contains "$skill" "First Principle|Non-negotiables|Assumptions to Drop|Smallest Sufficient Path|Escalation Signal" \
    "skill keeps a compact output shape"
assert_contains "$skill" "advisory|does not grant completion authority|not grant completion authority" \
    "skill preserves method-pack authority boundary"
assert_contains "$skill" "brainstorming|systematic-debugging|writing-plans|requesting-code-review|verification-before-completion" \
    "skill documents composition with other Aegis skills"
assert_not_contains "$skill" "must use for all|use for every task|use every turn|required before every" \
    "skill avoids universal trigger language"
assert_contains "$skill" "As a required step for every task, every turn, or every TDD cycle" \
    "skill explicitly rejects universal trigger usage"

assert_not_contains "$using_aegis" "first-principles-review" \
    "using-aegis hot path does not preload first-principles-review"
assert_contains "$process_doc" "first-principles-review" \
    "process baseline lists the projection target"
assert_contains "$readme_en" "first-principles-review" \
    "English README links the new skill"
assert_contains "$readme_zh" "first-principles-review" \
    "Chinese README links the new skill"

if (( failures > 0 )); then
    echo ""
    echo "First principles review check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "First principles review check passed."
