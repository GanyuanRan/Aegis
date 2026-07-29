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

assert_line() {
    local file="$1"
    local expected="$2"
    local label="$3"

    if grep -qxF -- "$expected" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

echo "=== Debugging Patch-Shape Gate Check ==="

debugging_skill="skills/systematic-debugging/SKILL.md"
debugging_advanced="skills/systematic-debugging/advanced-debugging-governance.md"
root_cause_contract="skills/systematic-debugging/root-cause-claim-contract.md"
process_baseline="docs/current/AEGIS_PROCESS_BASELINE.md"

assert_contains "$debugging_skill" "drill upward through diagnostic layers" \
    "debugging hot path uses source-oriented diagnostic wording"
assert_contains "$debugging_skill" "Patch-Shape Triage" \
    "debugging defines patch-shape triage before editing"
assert_contains "$debugging_skill" "Before fixing, run Patch-Shape Triage and Ripple Signal Triage" \
    "debugging hot path composes patch-shape and ripple triage before fixing"
assert_contains "$debugging_skill" "keyword, phrase, regex, negation-word list, or sample-text exception" \
    "debugging treats keyword/phrase/regex fixes as patch-shape signals"
assert_contains "$debugging_skill" "local guard, extra conditional.*one-off branch" \
    "debugging treats local guards and one-off branches as patch-shape signals"
assert_contains "$debugging_skill" "fallback, adapter, compatibility branch, prompt branch, or legacy path expansion" \
    "debugging treats fallback and adapter growth as patch-shape signals"
assert_contains "$debugging_skill" "consumer/caller/readiness/presentation-layer patch" \
    "debugging treats consumer/readiness/presentation patches as patch-shape signals"
assert_contains "$debugging_skill" "typed intent, normalized state,.*contract, or another source-of-truth" \
    "debugging catches downstream re-inference despite typed source of truth"
assert_contains "$debugging_skill" "artifact/download/export/readback/cache" \
    "debugging catches artifact/export/cache symptom patches"
assert_contains "$debugging_skill" "PatchShape:" \
    "debugging requires PatchShape output before editing"
assert_contains "$debugging_skill" "CanonicalOwner:" \
    "debugging requires CanonicalOwner output before editing"
assert_contains "$debugging_skill" "UpwardDrillSignal:" \
    "debugging requires UpwardDrillSignal output before editing"
assert_contains "$debugging_skill" "Decision: fix owner \\| continue investigation \\| escalate" \
    "debugging requires Decision output before editing"
assert_contains "$debugging_skill" "locally green test does not erase" \
    "debugging retains patch-shape state after a local pass"
assert_contains "$debugging_skill" "carrier is not a new direction" \
    "debugging compares direction semantically instead of by carrier name"
assert_contains "$debugging_skill" "Minimality Check" \
    "debugging defines minimality check for stable repair"
assert_contains "$debugging_skill" "smallest textual diff|textual diff" \
    "debugging distinguishes smallest textual diff from sufficient repair"
assert_contains "$debugging_skill" "sufficient repair \\| local patch \\| needs first-principles review" \
    "debugging classifies local patch versus sufficient repair"
assert_contains "$debugging_skill" "not the smallest textual diff" \
    "debugging states minimal fix is not smallest textual diff"
assert_contains "$debugging_skill" "not a RED gate or a prerequisite for production edits" \
    "debugging hot path keeps TDD-off reproduction diagnostic"
assert_contains "$debugging_skill" "aegis-workspace-helper.*new-work" \
    "debugging hot path retains workspace new-work command"
assert_contains "$debugging_skill" "aegis-workspace-helper.*add-evidence" \
    "debugging hot path retains workspace add-evidence command"
assert_contains "$debugging_skill" "aegis-workspace-helper.*check" \
    "debugging hot path retains workspace check command"
assert_contains "$debugging_skill" "Fast bug fix or quick bug fix pressure" \
    "debugging hot path keeps quick-fix workspace pressure rule"
assert_contains "$debugging_skill" "Triage fires, record it before editing" \
    "debugging hot path keeps ripple-before-editing rule"
assert_contains "$debugging_skill" "repair-added patch-shape" \
    "debugging hot path routes repair-added patch-shape evidence to advanced governance"
assert_contains "$debugging_skill" "wrong-owner/downstream repair" \
    "debugging hot path routes H3/H9 wrong-owner repairs"
assert_contains "$debugging_skill" "multi-site/one-regression" \
    "debugging hot path routes H2-style regression gaps"
assert_contains "$debugging_skill" "uninspected same-symptom fix" \
    "debugging hot path routes H6-style repeated-fix history"
assert_contains "$debugging_skill" "pattern/anomaly/duplicate/wrong-owner/downstream repair" \
    "debugging hot path routes remaining closure evidence"
assert_contains "$debugging_skill" "missing compound" \
    "debugging hot path begins the compound-proof trigger"
assert_contains "$debugging_skill" "member/necessity/anti-disguise" \
    "debugging hot path routes compound-proof gaps"
assert_contains "$debugging_skill" "unclear/disputed stop" \
    "debugging hot path routes unclear layer stops"
assert_contains "$debugging_skill" "outside-repo authority.*unmigrated" \
    "debugging hot path routes external authority and contract T-class signals"
assert_contains "$debugging_skill" "published-contract break" \
    "debugging hot path completes the contract T-class trigger"
assert_contains "$debugging_skill" "undefined spec.*missing permission/info" \
    "debugging hot path routes specification and permission T-class signals"
assert_contains "$debugging_advanced" "H7.*keyword, phrase, regex" \
    "advanced debugging owner keeps H7 keyword/phrase/regex signal"
assert_contains "$debugging_advanced" "H10.*re-parses raw text|H10.*re-infers action/state" \
    "advanced debugging owner keeps H10 downstream re-inference signal"
assert_contains "$debugging_advanced" "H13.*observed sample" \
    "advanced debugging owner keeps H13 sample-only patch signal"
assert_contains "$debugging_advanced" "H14.*topology is.*conjunctive-cluster.*member set is not enumerated" \
    "advanced debugging owner keeps H14 cluster member enumeration signal"
assert_contains "$debugging_advanced" "H15.*anti-disguise check" \
    "advanced debugging owner keeps H15 anti-disguise signal"
assert_contains "$root_cause_contract" "Pre-Claim Gate" \
    "root-cause contract owns Pre-Claim Gate"
assert_contains "$root_cause_contract" "Causal Topology Gate" \
    "root-cause contract owns Causal Topology Gate"
assert_contains "$root_cause_contract" "Falsifier Checked" \
    "root-cause contract owns falsifier proof"
assert_contains "$root_cause_contract" "anti-disguise check" \
    "root-cause contract owns compound anti-disguise proof"
assert_contains "$root_cause_contract" "necessity test" \
    "root-cause contract owns member necessity proof"
assert_line "$root_cause_contract" "#### Conjunctive cluster proof" \
    "root-cause contract defines conjunctive member proof"
assert_line "$root_cause_contract" "#### Independent compound proof" \
    "root-cause contract defines independent member proof"
assert_contains "$root_cause_contract" "overall symptom may persist through" \
    "independent compound proof does not reuse conjunctive disappearance"
assert_not_contains "$root_cause_contract" "For.*conjunctive-cluster.*and.*independent-compound" \
    "root-cause contract does not collapse topology-specific member proofs"
assert_line "$root_cause_contract" "- Candidate: independent-compound" \
    "root-cause example classifies independently sufficient paths exactly"
assert_line "$root_cause_contract" "- Same-incident active roots: A, B" \
    "root-cause example records simultaneous root activity"
assert_line "$root_cause_contract" "- Anti-disguise result: shared upstream L7 Spec Gap" \
    "root-cause example records the shared upstream"
assert_line "$root_cause_contract" "- Final: single-root-multi-symptom" \
    "root-cause example records the exact anti-disguise collapse"
assert_line "$root_cause_contract" "- independent-compound: multiple active roots in same incident" \
    "root-cause contract distinguishes simultaneous compound activity"
assert_line "$root_cause_contract" "- disjunctive-or: one active root plus alternative sufficient roots" \
    "root-cause contract distinguishes alternative sufficient roots"
assert_contains "$debugging_advanced" "D6.*topology is explicitly classified" \
    "advanced debugging owner keeps D6 topology closeout signal"
assert_contains "$debugging_advanced" "D7.*anti-disguise check has been run" \
    "advanced debugging owner keeps D7 anti-disguise closeout signal"

assert_contains "$process_baseline" "keyword, phrase, regex, negation-word list" \
    "process baseline defines patch-shape ripple signals"
assert_contains "$process_baseline" "downstream logic re-parses raw text|re-infers action/state" \
    "process baseline defines downstream re-inference signal"
assert_contains "$process_baseline" "PatchShape.*CanonicalOwner.*UpwardDrillSignal.*Decision" \
    "process baseline requires patch-shape triage output"
assert_contains "$process_baseline" "locally green verification does not erase triage state" \
    "process baseline preserves triage state after local verification"
assert_contains "$process_baseline" "new carrier name alone does not prove a new direction" \
    "process baseline prevents carrier-name disguise"
assert_contains "$process_baseline" "Minimal Necessary Change means the smallest sufficient change" \
    "process baseline defines minimal necessary change as sufficient repair"
assert_contains "$process_baseline" "correct owner and abstraction layer" \
    "process baseline ties minimality to owner and abstraction layer"
assert_contains "$process_baseline" "Diagnosis must drill upward layer by layer" \
    "process baseline uses upward drilling wording"

assert_not_contains "$debugging_skill" "Drill Down Through Diagnostic Layers|drill down through diagnostic layers|before descending|Continue drilling|Re-drill" \
    "debugging skill retired conflicting downward-drill wording"
assert_not_contains "$process_baseline" "Diagnosis must drill down|not yet drilled down" \
    "process baseline retired conflicting downward-drill wording"

if (( failures > 0 )); then
    echo ""
    echo "Debugging patch-shape gate check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Debugging patch-shape gate check passed."
