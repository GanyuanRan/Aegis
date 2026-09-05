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
elif mutation == "live-tier-in-progress":
    for tier in matrix["evaluationTiers"]:
        if tier["id"] == "opt-in-live-held-out":
            tier["implementationStatus"] = "implementation-in-progress"
            break
elif mutation in {
    "standard-valid-run-target",
    "standard-paid-attempt-ceiling",
    "standard-workers",
    "standard-wall-budget",
    "extended-wall-budget",
    "standard-preflight-timeout",
    "standard-attempt-timeout",
    "standard-infrastructure-limit",
    "standard-repeat-overclaim",
    "development-publication",
    "development-valid-run-target",
    "extended-repeat-evidence",
    "extended-repetitions",
    "profile-integer-as-boolean",
    "profile-boolean-as-integer",
    "profile-list-as-string",
    "maximum-supported-workers",
    "missing-run-profile",
    "tier-duplicate-shape",
    "live-required-evidence",
    "matrix-top-level-repetitions",
    "legacy-live-tier-alias",
    "live-score-source",
    "live-supports-promotion",
}:
    live = next(tier for tier in matrix["evaluationTiers"] if tier["id"] == "opt-in-live-held-out")
    profiles = {profile["id"]: profile for profile in matrix["runProfiles"]}
    if mutation == "standard-valid-run-target":
        profiles["standard-held-out"]["validRunTarget"] = 39
    elif mutation == "standard-paid-attempt-ceiling":
        profiles["standard-held-out"]["paidAttemptCeiling"] = 43
    elif mutation == "standard-workers":
        profiles["standard-held-out"]["workers"] = 13
    elif mutation == "standard-wall-budget":
        profiles["standard-held-out"]["wallClockBudgetSeconds"] = 3599
    elif mutation == "extended-wall-budget":
        profiles["extended-held-out"]["wallClockBudgetSeconds"] = 8999
    elif mutation == "standard-preflight-timeout":
        profiles["standard-held-out"]["preflightTimeoutSeconds"] = 31
    elif mutation == "standard-attempt-timeout":
        profiles["standard-held-out"]["perAttemptTimeoutSeconds"] = 481
    elif mutation == "standard-infrastructure-limit":
        profiles["standard-held-out"]["infrastructureFailureLimit"] = 3
    elif mutation == "standard-repeat-overclaim":
        profiles["standard-held-out"]["unsupportedEvidence"] = []
    elif mutation == "development-publication":
        profiles["development-pilot"]["publicationEligible"] = True
    elif mutation == "development-valid-run-target":
        profiles["development-pilot"]["validRunTarget"] = 1
    elif mutation == "extended-repeat-evidence":
        profiles["extended-held-out"]["supportedEvidence"].remove("repeated-run-evidence")
    elif mutation == "extended-repetitions":
        profiles["extended-held-out"]["repetitionsPerCase"] = 2
    elif mutation == "profile-integer-as-boolean":
        profiles["standard-held-out"]["repetitionsPerCase"] = True
    elif mutation == "profile-boolean-as-integer":
        profiles["standard-held-out"]["publicationEligible"] = 1
    elif mutation == "profile-list-as-string":
        profiles["standard-held-out"]["unsupportedEvidence"] = "repeated-run-evidence"
    elif mutation == "maximum-supported-workers":
        matrix["maximumSupportedWorkers"] = 13
    elif mutation == "missing-run-profile":
        matrix["runProfiles"] = [
            profile for profile in matrix["runProfiles"] if profile["id"] != "standard-held-out"
        ]
    elif mutation == "tier-duplicate-shape":
        live["workers"] = 8
    elif mutation == "live-required-evidence":
        live["requiredEvidence"] = ["held-out-evidence"]
    elif mutation == "matrix-top-level-repetitions":
        matrix["repetitions"] = 3
    elif mutation == "legacy-live-tier-alias":
        live["id"] = "opt-in-live-repeated-held-out"
    elif mutation == "live-score-source":
        live["scoreSource"] = "static-transcript-contract-analysis"
    elif mutation == "live-supports-promotion":
        live["supportsPromotionEvidence"] = True
elif mutation in {"portfolio-case-count", "portfolio-status", "portfolio-repetitions", "portfolio-workers"}:
    field, value = {
        "portfolio-case-count": ("caseCount", 29),
        "portfolio-status": ("implementationStatus", "contract-only"),
        "portfolio-repetitions": ("repetitions", 3),
        "portfolio-workers": ("workers", 8),
    }[mutation]
    matrix["casePortfolio"][field] = value
elif mutation == "report-authority-overclaim":
    matrix["reportBoundaries"]["forbiddenClaims"].remove("aegis-grants-completion-authority")
elif mutation == "automatic-promotion":
    matrix["promotionPolicy"]["authority"] = "automatic"
elif mutation == "quality-composite-score":
    matrix["benchmarkQualityPolicy"]["compositeScore"] = "weighted"
elif mutation == "quality-sentinel-overclaim":
    matrix["benchmarkQualityPolicy"]["caseRoles"]["sentinelDefinition"] = "arm discrimination evidence"
elif mutation == "quality-discriminator-overclaim":
    matrix["benchmarkQualityPolicy"]["caseRoles"]["discriminatorDefinition"] = "guaranteed arm separation"
elif mutation == "quality-role-scoring-pass":
    matrix["benchmarkQualityPolicy"]["caseRoles"]["roleIsScoringPass"] = True
elif mutation == "quality-role-counts":
    matrix["benchmarkQualityPolicy"]["caseRoles"]["counts"] = {"development": 10, "sentinel": 11, "discriminator": 9}
elif mutation == "quality-freeze-after-edit":
    matrix["benchmarkQualityPolicy"]["heldOutFreezePoint"] = "after-candidate-skill-edits"
elif mutation == "quality-field-validation-off":
    matrix["benchmarkQualityPolicy"]["fieldValidationRequired"] = False
elif mutation in {
    "controlled-default-ci",
    "live-default-ci",
    "blind-default-ci",
    "blind-not-sampled",
    "deterministic-supports-promotion",
    "controlled-score-source",
    "controlled-repetitions-per-case",
}:
    tier_id, field, value = {
        "controlled-default-ci": ("controlled-replay", "defaultCi", True),
        "live-default-ci": ("opt-in-live-held-out", "defaultCi", True),
        "blind-default-ci": ("sampled-blind-human-review", "defaultCi", True),
        "blind-not-sampled": ("sampled-blind-human-review", "sampled", False),
        "deterministic-supports-promotion": ("deterministic-static", "supportsPromotionEvidence", True),
        "controlled-score-source": ("controlled-replay", "scoreSource", "inferred-score"),
        "controlled-repetitions-per-case": ("controlled-replay", "repetitionsPerCase", 1),
    }[mutation]
    tiers = {tier["id"]: tier for tier in matrix["evaluationTiers"]}
    tiers[tier_id][field] = value
elif mutation == "promotion-candidate-scope":
    matrix["promotionPolicy"]["candidateScope"] = "any-change"
elif mutation == "missing-blind-unsupported-claim":
    controlled = next(tier for tier in matrix["evaluationTiers"] if tier["id"] == "controlled-replay")
    controlled["unsupportedClaims"].remove("blind-review-evidence")
elif mutation == "blind-missing-escalation-trigger":
    tier_id, field, value = (
        "sampled-blind-human-review",
        "escalationTriggers",
        "non-discriminating-assertions",
    )
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
elif mutation == "missing-required-scenario":
    matrix["scenarioClasses"] = [
        scenario for scenario in matrix["scenarioClasses"]
        if scenario["id"] != "long-task-boundary-preservation"
    ]
elif mutation == "invalid-scenario-id":
    for scenario in matrix["scenarioClasses"]:
        if scenario["id"] == "long-task-boundary-preservation":
            scenario["id"] = None
            break
elif mutation == "extra-scenario":
    extra_scenario = copy.deepcopy(matrix["scenarioClasses"][0])
    extra_scenario["id"] = "unexpected-matrix-v7-scenario"
    matrix["scenarioClasses"].append(extra_scenario)
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

make_negative_portfolio_case() {
    local mutation="$1"
    local output="$coverage_negative_root/portfolio-$mutation.json"

    cp "$case_manifest" "$output"
    "${PYTHON_CMD[@]}" - "$mutation" "$output" <<'PY'
import copy
import json
import sys
from pathlib import Path

mutation, output_arg = sys.argv[1:]
output = Path(output_arg)
manifest = json.loads(output.read_text(encoding="utf-8"))

if mutation == "missing-case":
    manifest["cases"].pop()
elif mutation == "extra-case":
    extra = copy.deepcopy(manifest["cases"][-1])
    extra["id"] = "unexpected-extra-case"
    manifest["cases"].append(extra)
elif mutation == "duplicate-id":
    manifest["cases"][1]["id"] = manifest["cases"][0]["id"]
elif mutation == "wrong-partition":
    manifest["cases"][0]["partition"] = "held-out-normal"
elif mutation == "fourth-variant":
    manifest["cases"][0]["variant"] = "fourth"
elif mutation == "arm-drift":
    manifest["arms"] = ["baseline-no-aegis", "aegis-explicit"]
elif mutation == "repetition-drift":
    manifest["repetitions"] = 3
elif mutation == "path-escape":
    manifest["cases"][0]["promptPath"] = "/tmp/agentic-benchmark-prompt.txt"
elif mutation == "outcome-inside-project":
    case = manifest["cases"][0]
    case["outcomeContractPath"] = f'{case["seedProjectPath"]}/expected-outcome.json'
elif mutation == "metric-outside-scenario":
    manifest["cases"][0]["benchmarkMetrics"].append("diff-size")
elif mutation == "live-ineligible":
    manifest["cases"][0]["liveEligible"] = False
elif mutation == "case-role-drift":
    case = next(item for item in manifest["cases"] if item["id"] == "completion-normal")
    case["caseRole"] = "discriminator"
else:
    raise SystemExit(f"unknown portfolio mutation: {mutation}")

output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

    printf '%s\n' "$output"
}

assert_negative_portfolio_case() {
    local mutation="$1"
    local label="$2"
    local expected_error="$3"
    local mutated_manifest
    local validator_output

    mutated_manifest="$(make_negative_portfolio_case "$mutation")"
    if validator_output="$("${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_cases.py \
        "$mutated_manifest" --schema-only 2>&1)"; then
        fail "$label rejected by case portfolio validator"
    elif grep -qF "$expected_error" <<<"$validator_output"; then
        pass "$label rejected by case portfolio validator"
    else
        fail "$label produced the expected case portfolio rejection"
    fi
}

echo "=== Agentic Benchmark Check ==="

baseline="docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md"
current_index="docs/current/README.md"
workflow_quality="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
matrix="tests/e2e/fixtures/agentic-benchmark-matrix.json"
case_manifest="tests/e2e/fixtures/agentic-benchmark-cases.json"
replay_manifest="tests/e2e/fixtures/replay-samples.json"
workflow_matrix="tests/e2e/fixtures/workflow-quality-matrix.json"
repeated_runner="tests/e2e/run-agentic-benchmark.sh"

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

if [[ -f "$case_manifest" ]]; then
    pass "agentic benchmark case manifest exists"
else
    fail "agentic benchmark case manifest exists"
fi

if [[ -f "$replay_manifest" ]]; then
    pass "controlled replay manifest exists"
else
    fail "controlled replay manifest exists"
fi

if [[ -x "$repeated_runner" ]]; then
    pass "repeated benchmark runner exists and is executable"
else
    fail "repeated benchmark runner exists and is executable"
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
assert_contains "$baseline" "same requested model and reasoning effort across both arms" \
    "benchmark baseline freezes model and reasoning effort fairly across arms"
assert_contains "$baseline" "one frozen Codex permission profile" \
    "benchmark baseline assigns one agent-tool sandbox owner"
assert_contains "$baseline" "machine-observed command/edit event is infrastructure-invalid" \
    "benchmark baseline rejects unobserved tool execution"
assert_contains "$baseline" 'Legacy Landlock, `danger-full-access`, sandbox bypass and dual-path' \
    "benchmark baseline retires unsafe sandbox fallbacks"
assert_contains "$baseline" "must not say" \
    "benchmark baseline forbids overclaiming"
assert_contains "$baseline" "completion authority" \
    "benchmark baseline preserves completion authority boundary"
assert_contains "$baseline" "activeInvocation.*reservation|reservation.*active invocation" \
    "benchmark baseline makes the full remaining invocation reservation explicit"
assert_contains "$baseline" "requires a new batch" \
    "benchmark baseline refuses wall-budget recovery after interruption"
assert_contains "$baseline" "Only the outer supervisor may settle.*zero exit" \
    "benchmark baseline keeps settlement behind clean zero-exit supervision"
assert_contains "$baseline" "Timeout or any nonzero exit retains" \
    "benchmark baseline retains invocation reservations on every nonzero exit"
assert_contains "$baseline" "sampled artifact" \
    "benchmark baseline labels aggregate artifact monitoring as sampled"
assert_contains "$baseline" "sampling does not guarantee detection" \
    "benchmark baseline disclaims transient artifact peak detection"
assert_contains "$baseline" "RLIMIT_FSIZE.*hard kernel-enforced ceiling" \
    "benchmark baseline preserves the hard per-file kernel limit"
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
assert_contains "$baseline" "All eleven minimum scenario classes" \
    "benchmark baseline defines deterministic coverage for all minimum scenarios"
assert_contains "$baseline" "explicit coverage gap" \
    "benchmark baseline keeps missing replay coverage explicit"
assert_contains "$baseline" "live eligibility is not live execution evidence" \
    "benchmark baseline distinguishes eligibility from evidence"
assert_contains "$baseline" "deterministic-static" \
    "benchmark baseline defines deterministic static tier"
assert_contains "$baseline" "opt-in-live-held-out" \
    "benchmark baseline keeps held-out evaluation opt-in"
assert_contains "$baseline" "development-pilot" \
    "benchmark baseline defines the bounded development profile"
assert_contains "$baseline" "standard-held-out" \
    "benchmark baseline defines the standard held-out profile"
assert_contains "$baseline" "extended-held-out" \
    "benchmark baseline defines the extended held-out profile"
assert_contains "$baseline" "repeated-run-evidence.*unsupported" \
    "benchmark baseline forbids repeated-run claims from the standard profile"
assert_contains "$baseline" "maximum supported worker count is 12" \
    "benchmark baseline caps supported concurrency"
assert_not_contains "$baseline" "opt-in-live-repeated-held-out" \
    "benchmark baseline retires the old repeated held-out tier name"
assert_contains "$baseline" "sampled-blind-human-review" \
    "benchmark baseline defines blind human escalation tier"
assert_contains "$baseline" "previous-aegis" \
    "benchmark baseline defines conditional previous Aegis arm"
assert_contains "$baseline" "does not provide variance, held-out, blind-review, or candidate" \
    "benchmark baseline rejects single static replay overclaims"
assert_contains "$baseline" "automatically promote a candidate" \
    "benchmark baseline keeps candidate promotion advisory"
assert_contains "$baseline" "exactly 33 cases" \
    "benchmark baseline defines the concrete thirty-three-case target"
assert_contains "$baseline" "arm-neutral and observable-outcome-based" \
    "benchmark baseline requires fair live outcome scoring"
assert_contains "$baseline" "48- or 144-attempt ceiling" \
    "benchmark baseline bounds paid retry attempts"
assert_contains "$baseline" "sanitized, path-independent advisory report" \
    "benchmark baseline defines a public-safe report projection"
assert_contains "$baseline" "requested reasoning effort and whether model identity was observable" \
    "benchmark baseline records the public model policy and host-event limitation"

"${PYTHON_CMD[@]}" tests/helpers/validate_workflow_quality_matrix.py "$workflow_matrix"
"${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_matrix.py "$matrix"
"${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_cases.py "$case_manifest"
"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py --validate-only

mkdir -p "$REPO_ROOT/.tmp"
coverage_negative_root="$(mktemp -d "$REPO_ROOT/.tmp/agentic-coverage-negative.XXXXXX")"
trap 'rm -rf -- "$coverage_negative_root"' EXIT

# The static gate must stay host-neutral while still proving that dry-run
# batches freeze both a launcher and its packaged native runtime identity.
# This fixture is hashed during preparation but never makes a model call.
offline_codex="$("${PYTHON_CMD[@]}" - "$coverage_negative_root/offline-codex" <<'PY'
import platform
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
launcher = root / "bin" / "codex.js"
launcher.parent.mkdir(parents=True)
launcher.write_text("#!/bin/sh\nprintf '%s\\n' 'codex-cli 0.0.0-offline-test'\n", encoding="utf-8")
launcher.chmod(0o755)

target = {
    "x86_64": "x86_64-unknown-linux-musl",
    "aarch64": "aarch64-unknown-linux-musl",
}.get(platform.machine())
if target is None:
    raise SystemExit("offline Codex fixture platform is unsupported")
native = root / "node_modules" / "@openai" / "codex-offline-test" / "vendor" / target / "bin" / "codex"
native.parent.mkdir(parents=True)
shutil.copy2(Path(sys.executable).resolve(), native)
native.chmod(0o755)
print(launcher)
PY
)"
export AEGIS_BENCHMARK_CODEX="$offline_codex"

while IFS='|' read -r mutation label expected_error validator_scope; do
    assert_negative_coverage_case "$mutation" "$label" "$expected_error" "$validator_scope"
done <<'CASES'
coordinated-fourth-replay|coordinated fourth replay drift|controlled replay refs must match the public baseline
coordinated-wrong-scenario|coordinated replay scenario remap|controlled replay refs must match the public baseline
refs-without-live-eligibility|controlled refs without live eligibility|live replay eligibility must equal controlled replay availability
controlled-replay-held-out|controlled replay held-out overclaim|must use development partition
live-tier-in-progress|live harness implementation status regression|live held-out harness must be implemented after its offline gates pass
standard-valid-run-target|standard valid-run target drift|standard-held-out.validRunTarget must be 44|matrix-only
standard-paid-attempt-ceiling|standard paid-attempt ceiling drift|standard-held-out.paidAttemptCeiling must be 48|matrix-only
standard-workers|unsupported standard worker count|standard-held-out.workers must be 8|matrix-only
standard-wall-budget|standard wall budget drift|standard-held-out.wallClockBudgetSeconds must be 7200|matrix-only
extended-wall-budget|extended wall budget drift|extended-held-out.wallClockBudgetSeconds must be 18000|matrix-only
standard-preflight-timeout|standard preflight timeout drift|standard-held-out.preflightTimeoutSeconds must be 30|matrix-only
standard-attempt-timeout|standard attempt timeout drift|standard-held-out.perAttemptTimeoutSeconds must be 960|matrix-only
standard-infrastructure-limit|standard infrastructure failure limit drift|standard-held-out.infrastructureFailureLimit must be 2|matrix-only
standard-repeat-overclaim|standard repeated-run evidence overclaim|standard-held-out.unsupportedEvidence must be ['repeated-run-evidence']|matrix-only
development-publication|development publication drift|development-pilot.publicationEligible must be False|matrix-only
development-valid-run-target|development valid-run target drift|development-pilot.validRunTarget must be 2|matrix-only
extended-repeat-evidence|extended repeated-run evidence drift|extended-held-out.supportedEvidence must be ['held-out-evidence', 'repeated-run-evidence']|matrix-only
extended-repetitions|extended repetitions drift|extended-held-out.repetitionsPerCase must be 3|matrix-only
profile-integer-as-boolean|integer profile field encoded as boolean|standard-held-out.repetitionsPerCase must be an integer|matrix-only
profile-boolean-as-integer|boolean profile field encoded as integer|standard-held-out.publicationEligible must be a boolean|matrix-only
profile-list-as-string|list profile field encoded as string|standard-held-out.unsupportedEvidence must be a list|matrix-only
maximum-supported-workers|maximum supported workers drift|maximumSupportedWorkers must be 12|matrix-only
missing-run-profile|missing exact run profile|runProfiles must define development-pilot, standard-held-out, and extended-held-out exactly|matrix-only
tier-duplicate-shape|tier duplicate shape owner|opt-in-live-held-out must contain exactly its canonical evaluation tier fields|matrix-only
live-required-evidence|live tier semantic shape alias|opt-in-live-held-out must contain exactly its canonical evaluation tier fields|matrix-only
matrix-top-level-repetitions|matrix top-level legacy repetitions alias|matrix top-level fields must match the exact v7 schema; unexpected: ['repetitions']|matrix-only
legacy-live-tier-alias|retired live tier alias|evaluationTiers must define the four-tier contract exactly|matrix-only
live-score-source|arm-biased live scorer drift|live held-out scorer must remain arm-neutral and outcome-based|matrix-only
live-supports-promotion|live promotion overclaim|live held-out tier cannot support promotion evidence by itself|matrix-only
portfolio-case-count|portfolio case-count drift|casePortfolio case count must be 33|matrix-only
portfolio-status|portfolio implementation status regression|casePortfolio must be implemented after concrete manifest validation|matrix-only
portfolio-repetitions|case portfolio repetitions alias|casePortfolio must contain exactly the canonical portfolio fields|matrix-only
portfolio-workers|case portfolio workers alias|casePortfolio must contain exactly the canonical portfolio fields|matrix-only
report-authority-overclaim|report authority overclaim|missing forbidden claims: aegis-grants-completion-authority|matrix-only
automatic-promotion|automatic candidate promotion claim|promotionPolicy must remain advisory-only
quality-composite-score|benchmark composite score overclaim|benchmark composite score must remain forbidden|matrix-only
quality-sentinel-overclaim|sentinel discrimination overclaim|sentinel role definition drifted|matrix-only
quality-discriminator-overclaim|discriminator guaranteed-separation overclaim|discriminator role definition drifted|matrix-only
quality-role-scoring-pass|case role scoring overclaim|case role must never be a scoring pass|matrix-only
quality-role-counts|case role count drift|case role counts drifted|matrix-only
quality-freeze-after-edit|late held-out freeze drift|held-out freeze point drifted|matrix-only
quality-field-validation-off|field validation bypass|field validation must precede candidate held-out evidence|matrix-only
controlled-default-ci|controlled replay default CI drift|controlled-replay must not be the default CI tier
live-default-ci|live tier default CI drift|live held-out tier must be opt-in outside default CI
blind-default-ci|blind review default CI drift|blind human review tier must not run in default CI
blind-not-sampled|blind review sampling drift|human review must be sampled and blind
promotion-candidate-scope|candidate promotion scope drift|promotionPolicy candidate scope drifted
missing-blind-unsupported-claim|missing blind-review unsupported claim|controlled-replay must forbid variance, held-out, blind-review, and promotion claims
previous-arm-in-current-replay|previous Aegis arm in current replay|current controlled replay arms must be exactly baseline-no-aegis and aegis-auto
previous-arm-implemented|previous Aegis arm implemented early|previous-aegis must remain contract-only
current-comparison-drift|current controlled replay comparison drift|current controlled replay comparison must be aegis-auto over baseline-no-aegis
deterministic-supports-promotion|deterministic promotion evidence overclaim|deterministic-static cannot support promotion evidence
controlled-score-source|controlled replay score source drift|controlled-replay score source drifted
controlled-repetitions-per-case|controlled replay repetitions alias|controlled-replay must contain exactly its canonical evaluation tier fields|matrix-only
blind-missing-escalation-trigger|blind review missing assertion escalation|blind human review must cover variance and non-discriminating assertion escalation
duplicate-previous-arm|duplicate previous Aegis arm|arms must contain unique object ids
invalid-arm-object|invalid benchmark arm object|each arm must be an object
missing-required-arm|missing required benchmark arm|missing benchmark arms: aegis-explicit
missing-required-scenario|missing matrix-v7 scenario|scenarioClasses must define the exact matrix-v7 scenario set|matrix-only
invalid-scenario-id|invalid matrix-v7 scenario id|id must be a non-empty string|matrix-only
extra-scenario|extra matrix-v7 scenario|scenarioClasses must define the exact matrix-v7 scenario set|matrix-only
baseline-expected-pass-true|baseline expected pass drift|baseline-no-aegis expectedContractPass must be false
aegis-expected-pass-false|Aegis expected pass drift|aegis-auto expectedContractPass must be true
CASES

while IFS='|' read -r mutation label expected_error; do
    assert_negative_portfolio_case "$mutation" "$label" "$expected_error"
done <<'CASES'
missing-case|32-case portfolio|case manifest must contain exactly 33 cases
extra-case|34-case portfolio|case manifest must contain exactly 33 cases
duplicate-id|duplicate portfolio case id|case manifest ids must be unique
wrong-partition|wrong case partition|does not match the fixed scenario/partition case id
fourth-variant|fourth case variant|variant does not match its partition
arm-drift|case portfolio arm drift|case manifest arms must be exactly baseline-no-aegis and aegis-auto
repetition-drift|case portfolio duplicate shape owner|case manifest must not define matrix-owned run shape fields: repetitions
path-escape|case prompt path escape|must be repo-relative
outcome-inside-project|outcome contract copied into agent project|outcome contract must stay outside the seed project
metric-outside-scenario|case metric outside scenario contract|benchmark metrics must exactly match its scenario required metrics
live-ineligible|case silently excluded from live portfolio|must be live eligible
case-role-drift|sentinel case role drift|completion-normal case role drifted
CASES

route_leak_prompt="$coverage_negative_root/route-leak-prompt.txt"
"${PYTHON_CMD[@]}" - "$route_leak_prompt" <<'PY'
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    "Use Aegis systematic-debugging and satisfy the expected outcome scorer.\n",
    encoding="utf-8",
)
PY
if route_leak_output="$("${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_cases.py \
    --check-prompt-text "$route_leak_prompt" \
    --scenario-class ambiguous-feature-shaping 2>&1)"; then
    fail "route-disclosing prompt rejected by case portfolio validator"
elif grep -qF "discloses hidden route or scoring material" <<<"$route_leak_output"; then
    pass "route-disclosing prompt rejected by case portfolio validator"
else
    fail "route-disclosing prompt produced the expected case portfolio rejection"
fi

if "${PYTHON_CMD[@]}" tests/helpers/test_run_agentic_benchmark.py >/dev/null; then
    pass "repeated runner fake-host contracts"
else
    fail "repeated runner fake-host contracts"
fi

if "${PYTHON_CMD[@]}" tests/helpers/test_agentic_benchmark_codex_events.py >/dev/null; then
    pass "Codex event reduction contracts"
else
    fail "Codex event reduction contracts"
fi

if retired_shape_output="$("${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py prepare \
    --profile standard-held-out \
    --partition held-out \
    --batch-id retired-shape-flag \
    --model dry-run-model \
    --reasoning-effort dry-run-effort \
    --output-root "$coverage_negative_root/retired-shape-flag" 2>&1)"; then
    fail "profile-only runner rejects retired raw shape flags"
elif grep -qF "unrecognized arguments: --partition held-out" <<<"$retired_shape_output"; then
    pass "profile-only runner rejects retired raw shape flags"
else
    fail "retired raw shape flag emits the expected argparse diagnostic"
fi

retired_wrapper_flags_ok=1
for retired_flag in --partition --repetitions --max-attempts --arms --timeout-seconds; do
    if bash "$repeated_runner" --profile standard-held-out --batch-id "retired-${retired_flag#--}" \
        --model dry-run-model --reasoning-effort dry-run-effort \
        --output-root "$coverage_negative_root/retired-${retired_flag#--}" \
        "$retired_flag" retired >/dev/null 2>&1; then
        retired_wrapper_flags_ok=0
    fi
done
if [[ "$retired_wrapper_flags_ok" == "1" ]]; then
    pass "profile-only wrapper rejects every retired raw shape flag"
else
    fail "profile-only wrapper rejects every retired raw shape flag"
fi

if bash "$repeated_runner" --dry-run --profile development-pilot --batch-id pilot-without-case \
    --output-root "$coverage_negative_root/pilot-without-case" >/dev/null 2>&1; then
    fail "development profile requires exactly one case"
else
    pass "development profile requires exactly one case"
fi
if bash "$repeated_runner" --dry-run --profile standard-held-out --case ambiguous-feature-dev \
    --batch-id held-out-with-case --output-root "$coverage_negative_root/held-out-with-case" >/dev/null 2>&1; then
    fail "held-out profiles reject case selection"
else
    pass "held-out profiles reject case selection"
fi

pilot_dry_run_root="$coverage_negative_root/pilot-dry-run"
standard_dry_run_root="$coverage_negative_root/standard-dry-run"
dry_run_root="$coverage_negative_root/repeated-dry-run"
if bash "$repeated_runner" --dry-run --profile development-pilot \
    --case ambiguous-feature-dev \
    --batch-id offline-pilot \
    --output-root "$pilot_dry_run_root" >/dev/null \
    && bash "$repeated_runner" --dry-run --profile standard-held-out \
    --batch-id offline-standard \
    --output-root "$standard_dry_run_root" >/dev/null \
    && bash "$repeated_runner" --dry-run --profile extended-held-out \
    --batch-id offline-contract \
    --output-root "$dry_run_root" >/dev/null \
    && "${PYTHON_CMD[@]}" - "$pilot_dry_run_root/batch.json" "$standard_dry_run_root/batch.json" "$dry_run_root/batch.json" <<'PY'
import json
import os
import sys
from pathlib import Path

profiles = {
    "development-pilot": (1, 2, 2, 2, 1200),
    "standard-held-out": (22, 44, 48, 8, 7200),
    "extended-held-out": (22, 132, 144, 8, 18000),
}
for path in sys.argv[1:]:
    batch_path = Path(path)
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    ledger = json.loads((batch_path.parent / "ledger.json").read_text(encoding="utf-8"))
    active_budget = json.loads((batch_path.parent / "active-budget.json").read_text(encoding="utf-8"))
    case_count, target_count, ceiling, workers, wall = profiles[batch["profileId"]]
    assert (batch["caseCount"], batch["targetRunCount"], batch["maxAttempts"]) == (case_count, target_count, ceiling)
    assert (batch["workers"], batch["wallClockBudgetSeconds"]) == (workers, wall)
    assert batch["preflightTimeoutSeconds"] == 30
    assert batch["modelPolicy"] == {
        "requestedModel": "dry-run-pinned-model",
        "reasoningEffort": "dry-run-pinned-effort",
        "mustMatchAcrossArms": True,
    }
    assert set(batch["hostExecutableIdentities"]) == {"codex", "auditBwrap", "permissionBackendBwrap"}
    for identities in batch["hostExecutableIdentities"].values():
        assert identities
        assert identities[0]["role"] == "launcher"
        assert all(set(identity) == {"role", "sha256", "sizeBytes"} for identity in identities)
        assert all(len(identity["sha256"]) == 64 and identity["sizeBytes"] > 0 for identity in identities)
        assert not any("path" in identity for identity in identities)
    assert any(identity["role"] == "native-runtime" for identity in batch["hostExecutableIdentities"]["codex"])
    assert len({target["targetId"] for target in batch["schedule"]}) == target_count
    assert set(batch["networkPolicy"]) == {"mode", "keys", "schemes", "fingerprint"}
    assert batch["networkPolicy"]["mode"] in {"direct", "proxy"}
    assert batch["networkPolicy"]["keys"] == sorted(batch["networkPolicy"]["keys"])
    assert set(batch["networkPolicy"]["keys"]) <= {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"}
    assert batch["networkPolicy"]["schemes"] == sorted(batch["networkPolicy"]["schemes"])
    assert len(batch["networkPolicy"]["fingerprint"]) == 64
    assert ledger["attempts"] == []
    assert active_budget == {
        "version": 1,
        "profileId": batch["profileId"],
        "batchDigest": batch["batchDigest"],
        "wallClockBudgetSeconds": batch["wallClockBudgetSeconds"],
    }
    assert not any((batch_path.parent / name).exists() for name in ("attempts", "provider-preflight.json", "isolation-report.json"))
def strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in strings(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in strings(child)]
    return []
stored_strings = {item for path in sys.argv[1:] for item in strings(json.loads(Path(path).read_text(encoding="utf-8")))}
for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy", "NO_PROXY", "no_proxy"):
    value = os.environ.get(key)
    if value:
        assert value not in stored_strings
PY
then
    pass "profile dry-runs freeze exact 2/44/132 target shapes with zero model calls"
else
    fail "profile dry-runs freeze exact bounded shapes"
fi

profile_drift_root="$coverage_negative_root/profile-drift"
cp -a "$standard_dry_run_root" "$profile_drift_root"
"${PYTHON_CMD[@]}" - "$profile_drift_root" <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tests/helpers").resolve()))
from run_agentic_benchmark import batch_digest

root = Path(sys.argv[1])
batch_path = root / "batch.json"
ledger_path = root / "ledger.json"
active_budget_path = root / "active-budget.json"
batch = json.loads(batch_path.read_text(encoding="utf-8"))
ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
active_budget = json.loads(active_budget_path.read_text(encoding="utf-8"))
batch["workers"] = 7
batch["batchDigest"] = batch_digest(batch)
ledger["batchDigest"] = batch["batchDigest"]
active_budget["batchDigest"] = batch["batchDigest"]
batch_path.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
active_budget_path.write_text(json.dumps(active_budget, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
if profile_drift_output="$("${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py aggregate \
    --output-root "$profile_drift_root" 2>&1)"; then
    fail "batch projection drift is rejected against the frozen matrix profile"
elif grep -qF "batch profile fields drifted from the frozen matrix" <<<"$profile_drift_output"; then
    pass "batch projection drift is rejected against the frozen matrix profile"
else
    fail "batch projection drift emits the expected diagnostic"
fi

resume_checks_ok=1
if resume_output="$(PYTHONOPTIMIZE=1 AEGIS_AGENTIC_BENCHMARK_LIVE=1 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 \
    bash "$repeated_runner" --profile standard-held-out --batch-id offline-contract --model dry-run-pinned-model \
    --reasoning-effort dry-run-pinned-effort --output-root "$dry_run_root" 2>&1)"; then
    resume_checks_ok=0
elif ! grep -qF "prepared batch profile differs" <<<"$resume_output"; then
    resume_checks_ok=0
fi
if resume_output="$(PYTHONOPTIMIZE=1 AEGIS_AGENTIC_BENCHMARK_LIVE=1 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 \
    bash "$repeated_runner" --profile extended-held-out --batch-id changed-batch --model dry-run-pinned-model \
    --reasoning-effort dry-run-pinned-effort --output-root "$dry_run_root" 2>&1)"; then
    resume_checks_ok=0
elif ! grep -qF "prepared batch id differs" <<<"$resume_output"; then
    resume_checks_ok=0
fi
if resume_output="$(PYTHONOPTIMIZE=1 AEGIS_AGENTIC_BENCHMARK_LIVE=1 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 \
    bash "$repeated_runner" --profile extended-held-out --batch-id offline-contract --model changed-model \
    --reasoning-effort dry-run-pinned-effort --output-root "$dry_run_root" 2>&1)"; then
    resume_checks_ok=0
elif ! grep -qF "prepared batch model differs" <<<"$resume_output"; then
    resume_checks_ok=0
fi
if resume_output="$(PYTHONOPTIMIZE=1 AEGIS_AGENTIC_BENCHMARK_LIVE=1 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 \
    bash "$repeated_runner" --profile extended-held-out --batch-id offline-contract --model dry-run-pinned-model \
    --reasoning-effort changed-effort --output-root "$dry_run_root" 2>&1)"; then
    resume_checks_ok=0
elif ! grep -qF "prepared batch reasoning effort differs" <<<"$resume_output"; then
    resume_checks_ok=0
fi
if resume_output="$(PYTHONOPTIMIZE=1 AEGIS_AGENTIC_BENCHMARK_LIVE=1 bash "$repeated_runner" --profile development-pilot \
    --case shared-owner-bug-repair --batch-id offline-pilot --model dry-run-pinned-model \
    --reasoning-effort dry-run-pinned-effort --output-root "$pilot_dry_run_root" 2>&1)"; then
    resume_checks_ok=0
elif ! grep -qF "prepared batch case selection differs" <<<"$resume_output"; then
    resume_checks_ok=0
fi
if [[ "$resume_checks_ok" == "1" ]]; then
    pass "optimized Python resume rejects profile, batch, model, reasoning effort, and case invocation drift before execution"
else
    fail "optimized Python resume rejects profile, batch, model, and case invocation drift before execution"
fi

if full_only_output="$(AEGIS_AGENTIC_BENCHMARK_LIVE=0 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=0 AEGIS_AGENTIC_BENCHMARK_EXTENDED=0 AEGIS_AGENTIC_BENCHMARK_FULL=1 bash "$repeated_runner" \
    --profile standard-held-out --batch-id full-alone --model dry-run-model \
    --reasoning-effort dry-run-effort --output-root "$coverage_negative_root/full-alone" 2>&1)"; then
    fail "retired FULL variable cannot authorize a held-out run"
elif grep -qF "AEGIS_AGENTIC_BENCHMARK_LIVE=1" <<<"$full_only_output"; then
    pass "retired FULL variable cannot authorize a held-out run"
else
    fail "FULL-only rejection names the live opt-in"
fi

if full_live_output="$(AEGIS_AGENTIC_BENCHMARK_LIVE=1 AEGIS_AGENTIC_BENCHMARK_HELD_OUT=0 AEGIS_AGENTIC_BENCHMARK_EXTENDED=0 AEGIS_AGENTIC_BENCHMARK_FULL=1 bash "$repeated_runner" \
    --profile standard-held-out --batch-id full-with-live --model dry-run-model \
    --reasoning-effort dry-run-effort --output-root "$coverage_negative_root/full-with-live" 2>&1)"; then
    fail "retired FULL variable cannot replace held-out opt-in"
elif grep -qF "AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1" <<<"$full_live_output"; then
    pass "retired FULL variable cannot replace held-out opt-in"
else
    fail "held-out opt-in rejection names the current variable"
fi

if proxy_drift_output="$(HTTP_PROXY=http://drift.invalid:8080 http_proxy=http://drift.invalid:8080 "${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py aggregate \
    --output-root "$dry_run_root" 2>&1)"; then
    fail "frozen batch rejects host proxy drift"
elif grep -qF "host proxy policy does not match the frozen batch metadata" <<<"$proxy_drift_output"; then
    pass "frozen batch rejects host proxy drift without exposing values"
else
    fail "proxy drift rejection emits the expected safe diagnostic"
fi

dry_run_batch_hash="$("${PYTHON_CMD[@]}" - "$dry_run_root/batch.json" <<'PY'
import hashlib
import sys
from pathlib import Path

print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
if bash "$repeated_runner" --dry-run \
    --profile extended-held-out \
    --batch-id offline-contract \
    --output-root "$dry_run_root" >/dev/null 2>&1; then
    fail "dry-run refuses to replace preserved batch evidence"
elif [[ "$dry_run_batch_hash" == "$("${PYTHON_CMD[@]}" - "$dry_run_root/batch.json" <<'PY'
import hashlib
import sys
from pathlib import Path

print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)" ]]; then
    pass "dry-run refuses to replace preserved batch evidence"
else
    fail "dry-run refusal preserves the existing batch bytes"
fi

frozen_prompt="$("${PYTHON_CMD[@]}" - "$dry_run_root/batch.json" "$dry_run_root" <<'PY'
import json
import sys
from pathlib import Path

batch = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(Path(sys.argv[2]) / batch["frozenCases"][0]["frozenPromptPath"])
PY
)"
"${PYTHON_CMD[@]}" - "$frozen_prompt" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(path.read_text(encoding="utf-8") + "\nfrozen-drift\n", encoding="utf-8")
PY
if frozen_drift_output="$("${PYTHON_CMD[@]}" tests/helpers/run_agentic_benchmark.py aggregate \
    --output-root "$dry_run_root" 2>&1)"; then
    fail "frozen batch input drift is rejected before aggregation"
elif grep -qF "frozen prompt drifted" <<<"$frozen_drift_output"; then
    pass "frozen batch input drift is rejected before aggregation"
else
    fail "frozen batch input drift emits the expected diagnostic"
fi

PROVIDER_TMP="$(mktemp -d "$REPO_ROOT/.tmp/provider-config-test.XXXXXX")"
cat > "$PROVIDER_TMP/provider-config.toml" <<'EOF'
model_provider = "custom"
model_catalog_json = "/tmp/stale-model-catalog.json"
model = "DeepSeek-V4-Flash-0731"
model_reasoning_effort = "max"

[model_providers]
[model_providers.custom]
name = "custom"
wire_api = "responses"
requires_openai_auth = false
base_url = "https://example.invalid/api/v1"
experimental_bearer_token = "QC-benchmark-test-token"
EOF
cat > "$PROVIDER_TMP/model-catalog.json" <<'EOF'
{"models": [{"slug": "DeepSeek-V4-Flash-0731", "supported_reasoning_levels": [{"effort": "max"}]}]}
EOF
if AEGIS_BENCHMARK_CODEX_CONFIG="$PROVIDER_TMP/provider-config.toml" \
   AEGIS_BENCHMARK_MODEL_CATALOG="$PROVIDER_TMP/model-catalog.json" \
   "${PYTHON_CMD[@]}" - "$PROVIDER_TMP" <<'PY'
import os
import sys
from pathlib import Path

sys.path.insert(0, "tests/helpers")

import agentic_benchmark_isolation as isolation

root = Path(sys.argv[1])
config = isolation.arm_codex_config()
assert 'approval_policy = "never"' in config, "neutral config must be preserved"
assert "[model_providers.custom]" in config, "provider config must be merged"
assert 'model_catalog_json = "~/.codex/model_catalog.json"' in config, "catalog path must be HOME-relative"
home_codex = root / "home" / ".codex"
isolation.write_arm_codex_home(home_codex)
assert (home_codex / "config.toml").is_file()
assert (home_codex / "model_catalog.json").is_file()
assert (home_codex / "model_catalog.json").read_text(encoding="utf-8").strip() == '{"models": [{"slug": "DeepSeek-V4-Flash-0731", "supported_reasoning_levels": [{"effort": "max"}]}]}'
print("  [PASS] custom provider config merges into isolated arm homes")
PY
then
    :
else
    fail "custom provider config merge into isolated arm homes"
fi
rm -rf -- "$PROVIDER_TMP"

if (( failures > 0 )); then
    echo ""
    echo "Agentic benchmark check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Agentic benchmark check passed."
