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
brainstorming_skill="skills/brainstorming/SKILL.md"
plans_skill="skills/writing-plans/SKILL.md"
readme_en="README.md"
readme_zh="README.zh-CN.md"
workflow_en="docs/current/AEGIS_WORKFLOW_GUIDE.md"
workflow_zh="docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md"

if [[ -f "$skill" ]]; then
    pass "first-principles-review skill exists"
else
    fail "first-principles-review skill exists"
fi

assert_contains "$skill" "^name: first-principles-review$" \
    "skill frontmatter name is stable"
assert_contains "$skill" "description: Use when" \
    "skill description uses trigger-oriented wording"
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
assert_contains "$skill" "Decision Hygiene Review|first-principles invariants|Owner / retirement matrix|Falsification matrix" \
    "skill owns the decision hygiene escalation template"
assert_contains "$skill" "Adopt / revise / reject / needs evidence|needs evidence" \
    "skill gives advisory verdict options without runtime authority"
assert_contains "$skill" "multiple plausible paths|new owner|fallback|adapter|compat-only|unverified assumption|long-term stable|长期稳定" \
    "skill has explicit escalation risk signals"
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
assert_contains "$brainstorming_skill" "first-principles-review|Decision Hygiene Review" \
    "brainstorming routes risky approach selection through first-principles review"
assert_contains "$brainstorming_skill" "[Bb]efore approach selection|before recommending|before selecting" \
    "brainstorming performs review before approach selection"
assert_contains "$plans_skill" "first-principles-review|Decision Hygiene Review" \
    "writing-plans routes risky task decomposition through first-principles review"
assert_contains "$plans_skill" "before task|before writing tasks" \
    "writing-plans names pre-task timing"
assert_contains "$plans_skill" "decomposition|task decomposition" \
    "writing-plans performs review before task decomposition"
assert_contains "$process_doc" "first-principles-review" \
    "process baseline lists the projection target"
assert_contains "$workflow_en" "decision hygiene review|falsification checks" \
    "English workflow guide documents decision hygiene review"
assert_contains "$workflow_zh" "decision hygiene review|反证场景" \
    "Chinese workflow guide documents decision hygiene review"
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
