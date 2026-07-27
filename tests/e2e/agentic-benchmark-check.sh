#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

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

make_negative_coverage_case() {
    local mutation="$1"
    local case_dir="$coverage_negative_root/$mutation"
    local case_matrix="$case_dir/agentic-benchmark-matrix.json"
    local case_manifest="$case_dir/replay-samples.json"
    local matrix_rel="${case_matrix#"$REPO_ROOT/"}"
    local manifest_rel="${case_manifest#"$REPO_ROOT/"}"

    mkdir -p "$case_dir"
    cp "$matrix" "$case_matrix"
    cp "$replay_manifest" "$case_manifest"

    "${PYTHON_CMD[@]}" - "$mutation" "$case_matrix" "$case_manifest" "$matrix_rel" "$manifest_rel" <<'PY'
import copy
import json
import sys
from pathlib import Path

mutation, matrix_arg, manifest_arg, matrix_rel, manifest_rel = sys.argv[1:]
matrix_path = Path(matrix_arg)
manifest_path = Path(manifest_arg)
matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
scenarios = {scenario["id"]: scenario for scenario in matrix["scenarioClasses"]}

matrix["coverageSources"]["controlledReplayManifest"] = manifest_rel
manifest["benchmarkMatrix"] = matrix_rel

if mutation == "coordinated-fourth-replay":
    scenarios["ambiguous-feature-shaping"]["coverage"] = {
        "workflowQualityFixtureRefs": ["ambiguous-feature"],
        "controlledReplaySampleRefs": ["unexpected-fourth-replay"],
        "liveReplayEligible": True,
    }
    extra_sample = copy.deepcopy(manifest["samples"][0])
    extra_sample["id"] = "unexpected-fourth-replay"
    extra_sample["scenarioClass"] = "ambiguous-feature-shaping"
    manifest["samples"].append(extra_sample)
elif mutation == "coordinated-wrong-scenario":
    scenarios["quick-bug-change-necessity"]["coverage"]["controlledReplaySampleRefs"] = []
    scenarios["quick-bug-change-necessity"]["coverage"]["liveReplayEligible"] = False
    scenarios["tiny-fast-path"]["coverage"]["controlledReplaySampleRefs"] = [
        "change-necessity-before-edit"
    ]
    scenarios["tiny-fast-path"]["coverage"]["liveReplayEligible"] = True
    for sample in manifest["samples"]:
        if sample["id"] == "change-necessity-before-edit":
            sample["scenarioClass"] = "tiny-fast-path"
            break
elif mutation == "refs-without-live-eligibility":
    scenarios["quick-bug-change-necessity"]["coverage"]["liveReplayEligible"] = False
elif mutation == "controlled-replay-held-out":
    manifest["samples"][0]["datasetPartition"] = "held-out"
elif mutation == "live-tier-implemented":
    for tier in matrix["evaluationTiers"]:
        if tier["id"] == "opt-in-live-repeated-held-out":
            tier["implementationStatus"] = "implemented"
            break
elif mutation in {
    "live-valid-run-target",
    "live-paid-attempt-ceiling",
    "live-score-source",
    "live-supports-promotion",
}:
    live = next(tier for tier in matrix["evaluationTiers"] if tier["id"] == "opt-in-live-repeated-held-out")
    field, value = {
        "live-valid-run-target": ("validRunTarget", 119),
        "live-paid-attempt-ceiling": ("paidAttemptCeiling", 120),
        "live-score-source": ("scoreSource", "static-transcript-contract-analysis"),
        "live-supports-promotion": ("supportsPromotionEvidence", True),
    }[mutation]
    live[field] = value
elif mutation in {"portfolio-case-count", "portfolio-status"}:
    field, value = {
        "portfolio-case-count": ("caseCount", 29),
        "portfolio-status": ("implementationStatus", "implemented"),
    }[mutation]
    matrix["casePortfolio"][field] = value
elif mutation == "report-authority-overclaim":
    matrix["reportBoundaries"]["forbiddenClaims"].remove("aegis-grants-completion-authority")
elif mutation == "automatic-promotion":
    matrix["promotionPolicy"]["authority"] = "automatic"
elif mutation in {
    "controlled-default-ci",
    "live-default-ci",
    "blind-default-ci",
    "blind-not-sampled",
    "deterministic-supports-promotion",
    "controlled-score-source",
}:
    tier_id, field, value = {
        "controlled-default-ci": ("controlled-replay", "defaultCi", True),
        "live-default-ci": ("opt-in-live-repeated-held-out", "defaultCi", True),
        "blind-default-ci": ("sampled-blind-human-review", "defaultCi", True),
        "blind-not-sampled": ("sampled-blind-human-review", "sampled", False),
        "deterministic-supports-promotion": ("deterministic-static", "supportsPromotionEvidence", True),
        "controlled-score-source": ("controlled-replay", "scoreSource", "inferred-score"),
    }[mutation]
    tiers = {tier["id"]: tier for tier in matrix["evaluationTiers"]}
    tiers[tier_id][field] = value
elif mutation == "promotion-candidate-scope":
    matrix["promotionPolicy"]["candidateScope"] = "any-change"
elif mutation == "missing-blind-unsupported-claim":
    controlled = next(tier for tier in matrix["evaluationTiers"] if tier["id"] == "controlled-replay")
    controlled["unsupportedClaims"].remove("blind-review-evidence")
elif mutation in {"live-missing-required-evidence", "blind-missing-escalation-trigger"}:
    tier_id, field, value = {
        "live-missing-required-evidence": (
            "opt-in-live-repeated-held-out",
            "requiredEvidence",
            "held-out-evidence",
        ),
        "blind-missing-escalation-trigger": (
            "sampled-blind-human-review",
            "escalationTriggers",
            "non-discriminating-assertions",
        ),
    }[mutation]
    tiers = {tier["id"]: tier for tier in matrix["evaluationTiers"]}
    tiers[tier_id][field].remove(value)
elif mutation == "previous-arm-in-current-replay":
    previous_arm = copy.deepcopy(manifest["samples"][0]["arms"][0])
    previous_arm["id"] = "previous-aegis"
    manifest["samples"][0]["arms"].append(previous_arm)
elif mutation == "previous-arm-implemented":
    previous_arm = next(arm for arm in matrix["arms"] if arm["id"] == "previous-aegis")
    previous_arm["implementationStatus"] = "implemented"
elif mutation == "current-comparison-drift":
    manifest["samples"][0]["comparisons"][0]["strongerArm"] = "baseline-no-aegis"
elif mutation == "duplicate-previous-arm":
    previous_arm = next(arm for arm in matrix["arms"] if arm["id"] == "previous-aegis")
    matrix["arms"].append(copy.deepcopy(previous_arm))
elif mutation == "invalid-arm-object":
    matrix["arms"].append("invalid-arm")
elif mutation == "missing-required-arm":
    matrix["arms"] = [arm for arm in matrix["arms"] if arm["id"] != "aegis-explicit"]
elif mutation in {"baseline-expected-pass-true", "aegis-expected-pass-false"}:
    arm_id, expected_pass = {
        "baseline-expected-pass-true": ("baseline-no-aegis", True),
        "aegis-expected-pass-false": ("aegis-auto", False),
    }[mutation]
    arm = next(arm for arm in manifest["samples"][0]["arms"] if arm["id"] == arm_id)
    arm["expectedContractPass"] = expected_pass
else:
    raise SystemExit(f"unknown mutation: {mutation}")

matrix_path.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

    printf '%s\n%s\n' "$case_matrix" "$case_manifest"
}

assert_negative_coverage_case() {
    local mutation="$1"
    local label="$2"
    local expected_error="$3"
    local validator_scope="${4:-both}"
    local paths
    local case_matrix
    local case_manifest
    local validator_output

    paths="$(make_negative_coverage_case "$mutation")"
    case_matrix="$(printf '%s\n' "$paths" | sed -n '1p')"
    case_manifest="$(printf '%s\n' "$paths" | sed -n '2p')"

    if validator_output="$("${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_matrix.py "$case_matrix" 2>&1)"; then
        fail "$label rejected by benchmark matrix validator"
    elif grep -qF "$expected_error" <<<"$validator_output"; then
        pass "$label rejected by benchmark matrix validator"
    else
        fail "$label produced the expected benchmark matrix rejection"
    fi

    if [[ "$validator_scope" == "both" ]]; then
        if validator_output="$("${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
            --manifest "$case_manifest" --validate-only 2>&1)"; then
            fail "$label rejected by controlled replay validator"
        elif grep -qF "$expected_error" <<<"$validator_output"; then
            pass "$label rejected by controlled replay validator"
        else
            fail "$label produced the expected controlled replay rejection"
        fi
    else
        pass "$label remains owned by the benchmark matrix validator"
    fi
}

echo "=== Agentic Benchmark Check ==="

baseline="docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md"
current_index="docs/current/README.md"
workflow_quality="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
matrix="tests/e2e/fixtures/agentic-benchmark-matrix.json"
replay_manifest="tests/e2e/fixtures/replay-samples.json"
workflow_matrix="tests/e2e/fixtures/workflow-quality-matrix.json"

if [[ -f "$baseline" ]]; then
    pass "agentic benchmark baseline exists"
else
    fail "agentic benchmark baseline exists"
fi

if [[ -f "$matrix" ]]; then
    pass "agentic benchmark matrix exists"
else
    fail "agentic benchmark matrix exists"
fi

if [[ -f "$replay_manifest" ]]; then
    pass "controlled replay manifest exists"
else
    fail "controlled replay manifest exists"
fi

assert_contains "$current_index" "AEGIS_AGENTIC_BENCHMARK_BASELINE.md" \
    "current docs index lists agentic benchmark baseline"
assert_contains "$workflow_quality" "agentic benchmark" \
    "workflow quality baseline references agentic benchmark"
assert_contains "$baseline" "baseline-no-aegis" \
    "benchmark baseline defines no-Aegis arm"
assert_contains "$baseline" "aegis-auto" \
    "benchmark baseline defines Aegis auto arm"
assert_contains "$baseline" "route-correctness" \
    "benchmark baseline prioritizes route correctness"
assert_contains "$baseline" "false-completion-rate" \
    "benchmark baseline measures false completion"
assert_contains "$baseline" "owner-fix-accuracy" \
    "benchmark baseline measures owner fix accuracy"
assert_contains "$baseline" "retirement-track-coverage" \
    "benchmark baseline measures retirement coverage"
assert_contains "$baseline" "workspace-laziness" \
    "benchmark baseline measures workspace laziness"
assert_contains "$baseline" "isolated workspace and configuration boundary|isolate host config" \
    "benchmark baseline requires run isolation"
assert_contains "$baseline" "must not say" \
    "benchmark baseline forbids overclaiming"
assert_contains "$baseline" "completion authority" \
    "benchmark baseline preserves completion authority boundary"
assert_contains "$baseline" "Controlled Replay Samples" \
    "benchmark baseline describes controlled replay sample layer"
assert_contains "$baseline" "does not run a live host agent" \
    "benchmark baseline keeps replay separate from live host execution"
assert_contains "$baseline" "Live Replay Capture" \
    "benchmark baseline describes opt-in live replay capture"
assert_contains "$baseline" "AEGIS_LIVE_REPLAY=1" \
    "benchmark baseline gates live capture behind explicit opt-in"
assert_contains "$baseline" "must not fabricate a no-Aegis baseline" \
    "benchmark baseline forbids fabricated live no-Aegis baseline"
assert_contains "$baseline" "All ten minimum scenario classes" \
    "benchmark baseline defines deterministic coverage for all minimum scenarios"
assert_contains "$baseline" "explicit coverage gap" \
    "benchmark baseline keeps missing replay coverage explicit"
assert_contains "$baseline" "live eligibility is not live execution evidence" \
    "benchmark baseline distinguishes eligibility from evidence"
assert_contains "$baseline" "deterministic-static" \
    "benchmark baseline defines deterministic static tier"
assert_contains "$baseline" "opt-in-live-repeated-held-out" \
    "benchmark baseline keeps repeated held-out evaluation opt-in"
assert_contains "$baseline" "sampled-blind-human-review" \
    "benchmark baseline defines blind human escalation tier"
assert_contains "$baseline" "previous-aegis" \
    "benchmark baseline defines conditional previous Aegis arm"
assert_contains "$baseline" "does not provide variance, held-out, blind-review, or candidate" \
    "benchmark baseline rejects single static replay overclaims"
assert_contains "$baseline" "automatically promote a candidate" \
    "benchmark baseline keeps candidate promotion advisory"
assert_contains "$baseline" "exactly 30 cases" \
    "benchmark baseline defines the concrete thirty-case target"
assert_contains "$baseline" "arm-neutral and observable-outcome based" \
    "benchmark baseline requires fair live outcome scoring"
assert_contains "$baseline" "hard ceiling of 132 paid attempts" \
    "benchmark baseline bounds paid retry attempts"
assert_contains "$baseline" "sanitized, path-independent advisory report" \
    "benchmark baseline defines a public-safe report projection"

"${PYTHON_CMD[@]}" tests/helpers/validate_workflow_quality_matrix.py "$workflow_matrix"
"${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_matrix.py "$matrix"
"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py --validate-only

mkdir -p "$REPO_ROOT/.tmp"
coverage_negative_root="$(mktemp -d "$REPO_ROOT/.tmp/agentic-coverage-negative.XXXXXX")"
trap 'rm -rf -- "$coverage_negative_root"' EXIT

while IFS='|' read -r mutation label expected_error validator_scope; do
    assert_negative_coverage_case "$mutation" "$label" "$expected_error" "$validator_scope"
done <<'CASES'
coordinated-fourth-replay|coordinated fourth replay drift|controlled replay refs must match the public baseline
coordinated-wrong-scenario|coordinated replay scenario remap|controlled replay refs must match the public baseline
refs-without-live-eligibility|controlled refs without live eligibility|live replay eligibility must equal controlled replay availability
controlled-replay-held-out|controlled replay held-out overclaim|must use development partition
live-tier-implemented|early live implementation claim|live repeated/held-out tier must remain implementation-in-progress until harness completion
live-valid-run-target|live valid-run target drift|live repeated/held-out valid run target must be 120|matrix-only
live-paid-attempt-ceiling|live paid-attempt ceiling drift|live repeated/held-out paid attempt ceiling must be 132|matrix-only
live-score-source|arm-biased live scorer drift|live repeated/held-out scorer must remain arm-neutral and outcome-based|matrix-only
live-supports-promotion|in-progress live promotion overclaim|in-progress live tier cannot support promotion evidence|matrix-only
portfolio-case-count|portfolio case-count drift|casePortfolio case count must be 30|matrix-only
portfolio-status|portfolio implementation overclaim|casePortfolio must remain contract-only until the concrete manifest exists|matrix-only
report-authority-overclaim|report authority overclaim|missing forbidden claims: aegis-grants-completion-authority|matrix-only
automatic-promotion|automatic candidate promotion claim|promotionPolicy must remain advisory-only
controlled-default-ci|controlled replay default CI drift|controlled-replay must not be the default CI tier
live-default-ci|live tier default CI drift|live repeated/held-out tier must be opt-in outside default CI
blind-default-ci|blind review default CI drift|blind human review tier must not run in default CI
blind-not-sampled|blind review sampling drift|human review must be sampled and blind
promotion-candidate-scope|candidate promotion scope drift|promotionPolicy candidate scope drifted
missing-blind-unsupported-claim|missing blind-review unsupported claim|controlled-replay must forbid variance, held-out, blind-review, and promotion claims
previous-arm-in-current-replay|previous Aegis arm in current replay|current controlled replay arms must be exactly baseline-no-aegis and aegis-auto
previous-arm-implemented|previous Aegis arm implemented early|previous-aegis must remain contract-only
current-comparison-drift|current controlled replay comparison drift|current controlled replay comparison must be aegis-auto over baseline-no-aegis
deterministic-supports-promotion|deterministic promotion evidence overclaim|deterministic-static cannot support promotion evidence
controlled-score-source|controlled replay score source drift|controlled-replay score source drifted
live-missing-required-evidence|live tier missing held-out evidence requirement|live repeated/held-out tier must require repeated and held-out evidence
blind-missing-escalation-trigger|blind review missing assertion escalation|blind human review must cover variance and non-discriminating assertion escalation
duplicate-previous-arm|duplicate previous Aegis arm|arms must contain unique object ids
invalid-arm-object|invalid benchmark arm object|each arm must be an object
missing-required-arm|missing required benchmark arm|missing benchmark arms: aegis-explicit
baseline-expected-pass-true|baseline expected pass drift|baseline-no-aegis expectedContractPass must be false
aegis-expected-pass-false|Aegis expected pass drift|aegis-auto expectedContractPass must be true
CASES

if (( failures > 0 )); then
    echo ""
    echo "Agentic benchmark check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Agentic benchmark check passed."
