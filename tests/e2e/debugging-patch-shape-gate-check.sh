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

echo "=== Debugging Patch-Shape Gate Check ==="

debugging_skill="skills/systematic-debugging/SKILL.md"
process_baseline="docs/current/AEGIS_PROCESS_BASELINE.md"

assert_contains "$debugging_skill" "drill upward through diagnostic layers" \
    "debugging hot path uses source-oriented diagnostic wording"
assert_contains "$debugging_skill" "Patch-Shape Triage" \
    "debugging defines patch-shape triage before editing"
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
assert_contains "$debugging_skill" "Minimality Check" \
    "debugging defines minimality check for stable repair"
assert_contains "$debugging_skill" "smallest textual diff|textual diff" \
    "debugging distinguishes smallest textual diff from sufficient repair"
assert_contains "$debugging_skill" "sufficient repair \\| local patch \\| needs first-principles review" \
    "debugging classifies local patch versus sufficient repair"
assert_contains "$debugging_skill" "not the smallest textual diff" \
    "debugging states minimal fix is not smallest textual diff"
assert_contains "$debugging_skill" "H7.*keyword, phrase, regex" \
    "debugging quality gate adds H7 keyword/phrase/regex signal"
assert_contains "$debugging_skill" "H10.*re-parses raw text|H10.*re-infers action/state" \
    "debugging quality gate adds H10 downstream re-inference signal"
assert_contains "$debugging_skill" "H13.*observed sample" \
    "debugging quality gate adds sample-only patch signal"
assert_contains "$debugging_skill" "H14.*topology is.*conjunctive-cluster.*member set is not enumerated" \
    "debugging quality gate adds H14 cluster member enumeration signal"
assert_contains "$debugging_skill" "H15.*anti-disguise check" \
    "debugging quality gate adds H15 anti-disguise check signal"
assert_contains "$debugging_skill" "Pre-Claim Gate" \
    "debugging defines Pre-Claim Gate before claiming root cause"
assert_contains "$debugging_skill" "Causal Topology Gate" \
    "debugging defines Causal Topology Gate for multi-root classification"
assert_contains "$debugging_skill" "anti-disguise check" \
    "debugging requires anti-disguise check before accepting a cluster"
assert_contains "$debugging_skill" "necessity test" \
    "debugging requires member necessity test for cluster and compound"
assert_contains "$debugging_skill" "D6.*topology is explicitly classified" \
    "debugging depth gate adds D6 explicit topology classification"
assert_contains "$debugging_skill" "D7.*anti-disguise check has been run" \
    "debugging depth gate adds D7 anti-disguise check executed"

assert_contains "$process_baseline" "keyword, phrase, regex, negation-word list" \
    "process baseline defines patch-shape ripple signals"
assert_contains "$process_baseline" "downstream logic re-parses raw text|re-infers action/state" \
    "process baseline defines downstream re-inference signal"
assert_contains "$process_baseline" "PatchShape.*CanonicalOwner.*UpwardDrillSignal.*Decision" \
    "process baseline requires patch-shape triage output"
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
