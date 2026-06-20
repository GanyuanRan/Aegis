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

echo "=== TDD Policy Check ==="

tdd_skill="skills/test-driven-development/SKILL.md"
using_aegis="skills/using-aegis/SKILL.md"
verification_skill="skills/verification-before-completion/SKILL.md"
brainstorming_skill="skills/brainstorming/SKILL.md"
writing_plans_skill="skills/writing-plans/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
process_baseline="docs/current/AEGIS_PROCESS_BASELINE.md"
tdd_mode_doc="docs/current/AEGIS_TDD_MODE.md"
systematic_debugging_skill="skills/systematic-debugging/SKILL.md"
scenario_b_behavior="tests/e2e/scenarios/scenario-B-bug-fix/expected-behavior.json"
codex_guide="docs/README.codex.md"
codex_install=".codex/INSTALL.md"

assert_contains "$using_aegis" "contract|cross-module|shared module|core logic" \
    "using-aegis routes contract and cross-module changes into TDD"
assert_contains "$using_aegis" "Classify before implementation" \
    "using-aegis classifies task complexity before implementation"
assert_contains "$using_aegis" "TDD Route" \
    "using-aegis routes implementation through TDD Route instead of unconditional TDD"
assert_contains "$using_aegis" "Medium/high: baseline read-set[[:space:]]*\\+ plan" \
    "using-aegis prevents medium/high-complexity work from entering TDD first"
assert_contains "$using_aegis" "Spec Brief or Design Spec only" \
    "using-aegis keeps spec/design conditional by complexity"
assert_contains "$using_aegis" "Workspace support is lazy" \
    "using-aegis defines lazy workspace creation rule"
assert_contains "$discipline_ref" "Low complexity|Medium complexity|High complexity" \
    "discipline reference details task complexity levels"
assert_contains "$discipline_ref" "TDD is the implementation discipline.*atomic tasks" \
    "discipline reference keeps TDD after planning for medium/high-complexity work"
assert_contains "$discipline_ref" "TDD Route" \
    "discipline reference documents TDD Route"
assert_contains "$discipline_ref" "work/<slug>" \
    "discipline reference details task-scoped workspace records"

assert_contains "$tdd_mode_doc" 'tdd_mode = "auto"' \
    "TDD mode doc defines auto mode"
assert_contains "$tdd_mode_doc" 'tdd_mode = "off"' \
    "TDD mode doc defines off mode"
assert_contains "$tdd_mode_doc" 'strict.*light.*skipped|strict.*skipped.*light|strict.*`light`.*skipped' \
    "TDD mode doc defines strict, light, and skipped routing"
assert_contains "$tdd_mode_doc" "verification-before-completion" \
    "TDD mode doc states verification-before-completion still applies"
assert_contains "$tdd_mode_doc" "native skill discovery|semantic matcher" \
    "TDD mode doc records native skill discovery boundary"
assert_contains "$codex_guide" "AEGIS_TDD_MODE=off" \
    "Codex guide documents TDD mode caveat"
assert_contains "$codex_guide" "does not directly control Codex's native matcher|does not override Codex's own semantic matcher" \
    "Codex guide explains TDD mode does not control native matcher"
assert_contains "$codex_guide" "TDD Route: strict|strict TDD|test-first|RED / GREEN / REFACTOR" \
    "Codex guide narrows TDD trigger wording to literal markers"
assert_contains "$codex_install" "AEGIS_TDD_MODE=off" \
    "Codex install surface documents TDD mode caveat"
assert_contains "$codex_install" "TDD Route: strict|strict TDD|test-first|RED / GREEN / REFACTOR" \
    "Codex install surface narrows TDD trigger wording to literal markers"

assert_contains "$tdd_skill" "contract|cross-module|shared module|core logic" \
    "TDD applies to contracts, cross-module changes, and core logic"
assert_contains "$tdd_skill" "TDD Mode" \
    "TDD skill defines TDD Mode"
assert_contains "$tdd_skill" "TDD Route" \
    "TDD skill defines TDD Route"
assert_contains "$tdd_skill" 'description: Use when the user explicitly requests strict or test-first TDD, or when the current conversation already contains an explicit `TDD Route: strict` decision from another Aegis workflow\.' \
    "TDD skill keeps a narrow native trigger boundary"
assert_not_contains "$tdd_skill" "description: Use when implementing any feature or bugfix, before writing implementation code" \
    "TDD skill no longer broad-matches every implementation request"
assert_contains "$tdd_skill" "False-positive entry on a native-direct-skill host" \
    "TDD skill exits when native host loading does not carry an explicit TDD signal"
assert_contains "$tdd_skill" "TDD Route: strict|strict TDD|test-first|RED / GREEN / REFACTOR" \
    "TDD skill anchors native-host entry to literal conversation markers"
assert_contains "$tdd_skill" "auto.*strict.*light.*skipped|strict.*light.*skipped" \
    "TDD skill defines AUTO route decisions"
assert_contains "$tdd_skill" "off.*automatic TDD|automatic TDD.*off" \
    "TDD skill defines OFF as disabling automatic TDD"
assert_contains "$tdd_skill" "verification-before-completion" \
    "TDD skill preserves completion verification when TDD is off"
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
assert_contains "$process_baseline" "Ripple Signal Triage" \
    "process baseline defines Ripple Signal Triage"
assert_contains "$systematic_debugging_skill" "Before fixing, run Patch-Shape Triage and Ripple Signal Triage" \
    "systematic debugging triggers patch-shape and ripple triage before risky fixes"
assert_contains "$tdd_skill" "Ripple Signal Triage fired|Ripple signal hit" \
    "TDD broadens verification when Ripple Signal Triage fires"
assert_contains "$scenario_b_behavior" "assistantMustContain" \
    "scenario B verifies assistant-side ripple triage under quick bug-fix pressure"

assert_contains "$verification_skill" "target test|related regression" \
    "verification asks for target test and related regression evidence"
assert_contains "$verification_skill" "manual verification|manual steps" \
    "verification asks for manual steps when automation is blocked"

assert_contains "$brainstorming_skill" "Aegis Project Workspace" \
    "brainstorming writes specs through the Aegis workspace boundary"
assert_contains "$brainstorming_skill" "Do not force this workflow onto low-complexity work" \
    "brainstorming no longer makes every small change a design ceremony"
assert_contains "$writing_plans_skill" "Aegis Project Workspace" \
    "writing-plans defines the Aegis workspace structure"
assert_contains "$writing_plans_skill" "INDEX.md" \
    "writing-plans records workspace initialization steps"
assert_contains "$process_baseline" "TDD is the implementation discipline.*not the first entry" \
    "process baseline states TDD is the implementation discipline, not the first entrypoint"
assert_contains "$process_baseline" "TDD Mode" \
    "process baseline documents TDD Mode"
assert_contains "$process_baseline" "TDD Mode controls test-first discipline, not completion evidence" \
    "process baseline separates TDD mode from completion evidence"

if (( failures > 0 )); then
    echo ""
    echo "TDD policy check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "TDD policy check passed."
