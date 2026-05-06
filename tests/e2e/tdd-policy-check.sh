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
brainstorming_skill="skills/brainstorming/SKILL.md"
writing_plans_skill="skills/writing-plans/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
process_baseline="docs/current/AEGIS_PROCESS_BASELINE.md"

assert_contains "$using_aegis" "contract|cross-module|shared module|core logic" \
    "using-aegis routes contract and cross-module changes into TDD"
assert_contains "$using_aegis" "classify task complexity" \
    "using-aegis classifies task complexity before implementation"
assert_contains "$using_aegis" "medium/high-complexity work needs planning" \
    "using-aegis prevents medium/high-complexity work from entering TDD first"
assert_contains "$using_aegis" "Aegis Project Workspace.*hard binary rule" \
    "using-aegis defines hard binary workspace creation rule"
assert_contains "$discipline_ref" "Low complexity|Medium complexity|High complexity" \
    "discipline reference details task complexity levels"
assert_contains "$discipline_ref" "TDD is the implementation discipline.*atomic tasks" \
    "discipline reference keeps TDD after planning for medium/high-complexity work"
assert_contains "$discipline_ref" "work/<slug>" \
    "discipline reference details task-scoped workspace records"

assert_contains "$tdd_skill" "contract|cross-module|shared module|core logic" \
    "TDD applies to contracts, cross-module changes, and core logic"
assert_contains "$tdd_skill" "Preflight Gate" \
    "TDD has a preflight gate before implementation"
assert_contains "$tdd_skill" "baseline read-set, plan, and atomic tasks before TDD" \
    "TDD requires planning artifacts before medium/high-complexity implementation"
assert_contains "$tdd_skill" "multiple files, modules, pages, screens, services, or owners" \
    "TDD detects multi-owner work as planning-gated"
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

assert_contains "$brainstorming_skill" "Aegis Project Workspace" \
    "brainstorming writes specs through the Aegis workspace boundary"
assert_contains "$writing_plans_skill" "Aegis Project Workspace" \
    "writing-plans defines the Aegis workspace structure"
assert_contains "$writing_plans_skill" "INDEX.md" \
    "writing-plans records workspace initialization steps"
assert_contains "$process_baseline" "TDD is the implementation discipline.*not the first entry" \
    "process baseline states TDD is the implementation discipline, not the first entrypoint"

if (( failures > 0 )); then
    echo ""
    echo "TDD policy check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "TDD policy check passed."
