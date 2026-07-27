#!/usr/bin/env python3
"""Validate the Aegis agentic benchmark design fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_ARMS = {"baseline-no-aegis", "aegis-auto", "aegis-explicit", "previous-aegis"}

REQUIRED_EVALUATION_TIERS = {
    "deterministic-static",
    "controlled-replay",
    "opt-in-live-held-out",
    "sampled-blind-human-review",
}

REQUIRED_PROMOTION_EVIDENCE = {
    "held-out-evidence",
    "repeated-run-evidence",
    "no-primary-metric-regression",
}

REQUIRED_PROMOTION_REVIEWS = {
    "high-variance-results",
    "non-discriminating-assertions",
}

FORBIDDEN_AUTOMATIC_PROMOTION_ACTIONS = {
    "promote-candidate",
    "modify-skill-or-workflow",
    "modify-baseline",
}

CURRENT_CONTROLLED_REPLAY_ARMS = {"baseline-no-aegis", "aegis-auto"}
CURRENT_CONTROLLED_REPLAY_EXPECTED_PASS = {
    "baseline-no-aegis": False,
    "aegis-auto": True,
}
CURRENT_CONTROLLED_REPLAY_COMPARISON = {
    "strongerArm": "aegis-auto",
    "weakerArm": "baseline-no-aegis",
    "expectation": "stronger-passes-and-scores-higher",
}

REQUIRED_PRIMARY_METRICS = {
    "route-correctness",
    "evidence-freshness",
    "authority-boundary",
    "false-completion-rate",
    "owner-fix-accuracy",
    "retirement-track-coverage",
    "workspace-laziness",
    "prompt-bloat-risk",
    "task-completeness",
    "trace-digest-coverage",
    "rule-effect-attribution",
    "skill-call-stability",
}

REQUIRED_SCENARIOS = {
    "ambiguous-feature-shaping",
    "shared-owner-bug-repair",
    "quick-bug-change-necessity",
    "tiny-new-source-path-change-necessity",
    "completion-claim-with-missing-evidence",
    "fallback-retirement-cleanup",
    "tiny-fast-path",
    "requested-white-box-trace-digest",
    "negative-fast-path-no-trace-digest",
    "destructive-cleanup-hard-stop",
}

REQUIRED_ISOLATION_CONTROLS = {
    "fresh-temporary-workspace-per-run",
    "isolated-host-config-per-arm",
    "isolated-plugin-dir-per-arm",
    "same-prompt-and-seeded-repo-per-arm",
    "record-model-host-seed-timeout-tool-policy",
    "preserve-transcripts-and-diffs",
    "scorer-selftests-before-scoring",
    "invalidate-contaminated-results",
}

FORBIDDEN_CLAIMS = {
    "aegis-grants-completion-authority",
    "benchmark-proves-final-evidence-sufficiency",
    "host-fully-compatible-from-one-benchmark",
    "fixed-percent-cost-time-or-code-savings-for-arbitrary-projects",
}

EXPECTED_CONTROLLED_REPLAY_MAPPING = {
    "change-necessity-before-edit": "quick-bug-change-necessity",
    "shared-owner-bug-repair": "shared-owner-bug-repair",
    "completion-evidence-boundary": "completion-claim-with-missing-evidence",
}

EXPECTED_LIVE_PARTITIONS = ["held-out-normal", "held-out-boundary"]
EXPECTED_LIVE_ARMS = ["baseline-no-aegis", "aegis-auto"]
EXPECTED_PORTFOLIO_PARTITIONS = {
    "development": 10,
    "held-out-normal": 10,
    "held-out-boundary": 10,
}
MAXIMUM_SUPPORTED_WORKERS = 12
PROFILE_FIELDS = {
    "id",
    "datasetPartitions",
    "caseCount",
    "arms",
    "repetitionsPerCase",
    "validRunTarget",
    "paidAttemptCeiling",
    "workers",
    "wallClockBudgetSeconds",
    "preflightTimeoutSeconds",
    "perAttemptTimeoutSeconds",
    "infrastructureFailureLimit",
    "publicationEligible",
    "publicationAuthority",
    "supportedEvidence",
    "unsupportedEvidence",
}
PROFILE_SHAPE_FIELDS = PROFILE_FIELDS - {"id"}
EXPECTED_RUN_PROFILES = {
    "development-pilot": {
        "datasetPartitions": ["development"],
        "caseCount": 1,
        "arms": EXPECTED_LIVE_ARMS,
        "repetitionsPerCase": 1,
        "validRunTarget": 2,
        "paidAttemptCeiling": 2,
        "workers": 2,
        "wallClockBudgetSeconds": 300,
        "preflightTimeoutSeconds": 30,
        "perAttemptTimeoutSeconds": 240,
        "infrastructureFailureLimit": 2,
        "publicationEligible": False,
        "publicationAuthority": "none",
        "supportedEvidence": [],
        "unsupportedEvidence": ["held-out-evidence", "repeated-run-evidence"],
    },
    "standard-held-out": {
        "datasetPartitions": EXPECTED_LIVE_PARTITIONS,
        "caseCount": 20,
        "arms": EXPECTED_LIVE_ARMS,
        "repetitionsPerCase": 1,
        "validRunTarget": 40,
        "paidAttemptCeiling": 44,
        "workers": 8,
        "wallClockBudgetSeconds": 2700,
        "preflightTimeoutSeconds": 30,
        "perAttemptTimeoutSeconds": 240,
        "infrastructureFailureLimit": 2,
        "publicationEligible": True,
        "publicationAuthority": "advisory-only",
        "supportedEvidence": ["held-out-evidence"],
        "unsupportedEvidence": ["repeated-run-evidence"],
    },
    "extended-held-out": {
        "datasetPartitions": EXPECTED_LIVE_PARTITIONS,
        "caseCount": 20,
        "arms": EXPECTED_LIVE_ARMS,
        "repetitionsPerCase": 3,
        "validRunTarget": 120,
        "paidAttemptCeiling": 132,
        "workers": 8,
        "wallClockBudgetSeconds": 2700,
        "preflightTimeoutSeconds": 30,
        "perAttemptTimeoutSeconds": 240,
        "infrastructureFailureLimit": 2,
        "publicationEligible": True,
        "publicationAuthority": "advisory-only",
        "supportedEvidence": ["held-out-evidence", "repeated-run-evidence"],
        "unsupportedEvidence": [],
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def string_set(data: dict[str, Any], key: str) -> set[str]:
    value = data.get(key, [])
    require(isinstance(value, list), f"{key} must be a list")
    require(all(isinstance(item, str) for item in value), f"{key} must contain strings")
    return set(value)


def string_list(data: dict[str, Any], key: str, label: str) -> list[str]:
    value = data.get(key)
    require(isinstance(value, list), f"{label}.{key} must be a list")
    require(
        all(isinstance(item, str) and item for item in value),
        f"{label}.{key} must contain non-empty strings",
    )
    require(len(value) == len(set(value)), f"{label}.{key} must not contain duplicates")
    return value


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain a JSON object")
    return data


def resolve_repo_path(root: Path, value: Any, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a non-empty string")
    path = (root / value).resolve()
    require(root == path or root in path.parents, f"{label} must stay inside the repo: {value}")
    require(path.is_file(), f"{label} must reference an existing file: {value}")
    return path


def validate_arms(data: dict[str, Any]) -> None:
    arms = data.get("arms", [])
    require(isinstance(arms, list), "arms must be a list")
    require(all(isinstance(arm, dict) for arm in arms), "each arm must be an object")
    arm_id_list = [arm.get("id") for arm in arms]
    require(all(isinstance(arm_id, str) and arm_id for arm_id in arm_id_list), "arm ids must be non-empty strings")
    require(len(arm_id_list) == len(set(arm_id_list)), "arms must contain unique object ids")
    by_id = {arm["id"]: arm for arm in arms}
    arm_ids = set(arm_id_list)
    missing = sorted(REQUIRED_ARMS - arm_ids)
    require(not missing, f"missing benchmark arms: {', '.join(missing)}")
    for arm in arms:
        require(arm.get("requiresIsolatedConfig") is True, f"{arm.get('id')} must isolate config")

    previous = by_id["previous-aegis"]
    require(previous.get("implementationStatus") == "contract-only", "previous-aegis must remain contract-only")
    require(previous.get("availability") == "conditional", "previous-aegis must be conditional")
    require(
        previous.get("useWhen") == "evaluating-candidate-skill-or-workflow-revision",
        "previous-aegis must only evaluate candidate skill or workflow revisions",
    )
    require(
        previous.get("requiredInControlledReplaySamples") is False,
        "previous-aegis must not be required in current controlled replay samples",
    )


def validate_evaluation_contract(data: dict[str, Any]) -> None:
    tiers = data.get("evaluationTiers")
    require(isinstance(tiers, list), "evaluationTiers must be a list")
    by_id = {tier.get("id"): tier for tier in tiers if isinstance(tier, dict)}
    require(len(by_id) == len(tiers), "evaluationTiers must contain unique object ids")
    require(set(by_id) == REQUIRED_EVALUATION_TIERS, "evaluationTiers must define the four-tier contract exactly")

    deterministic = by_id["deterministic-static"]
    require(deterministic.get("implementationStatus") == "implemented", "deterministic-static must be implemented")
    require(deterministic.get("defaultCi") is True, "deterministic-static must be the default CI tier")
    require(deterministic.get("supportsPromotionEvidence") is False, "deterministic-static cannot support promotion evidence")

    controlled = by_id["controlled-replay"]
    require(controlled.get("implementationStatus") == "implemented", "controlled-replay must be implemented")
    require(controlled.get("defaultCi") is False, "controlled-replay must not be the default CI tier")
    require(
        controlled.get("executionShape") == "single-static-captured-transcript",
        "controlled-replay must declare its single static transcript shape",
    )
    require(controlled.get("datasetPartitions") == ["development"], "controlled-replay must be development-only")
    require(controlled.get("scoreSource") == "static-transcript-contract-analysis", "controlled-replay score source drifted")
    require(controlled.get("supportsPromotionEvidence") is False, "controlled-replay cannot support promotion evidence")
    unsupported = set(controlled.get("unsupportedClaims", []))
    require(
        {"variance-evidence", "held-out-evidence", "blind-review-evidence", "candidate-promotion-evidence"}.issubset(unsupported),
        "controlled-replay must forbid variance, held-out, blind-review, and promotion claims",
    )

    live = by_id["opt-in-live-held-out"]
    require(
        live.get("implementationStatus") == "implemented",
        "live held-out harness must be implemented after its offline gates pass",
    )
    require(
        live.get("defaultCi") is False and live.get("optIn") is True,
        "live held-out tier must be opt-in outside default CI",
    )
    require(
        live.get("scoreSource") == "arm-neutral-observable-outcome-analysis",
        "live held-out scorer must remain arm-neutral and outcome-based",
    )
    require(live.get("requiresFrozenBatch") is True, "live held-out tier must freeze each batch")
    require(live.get("supportsPromotionEvidence") is False, "live held-out tier cannot support promotion evidence by itself")
    require(
        PROFILE_SHAPE_FIELDS.isdisjoint(live),
        "live held-out tier must not duplicate matrix-owned run profile fields",
    )

    blind = by_id["sampled-blind-human-review"]
    require(blind.get("implementationStatus") == "contract-only", "blind human review tier must remain contract-only")
    require(blind.get("defaultCi") is False, "blind human review tier must not run in default CI")
    require(blind.get("sampled") is True and blind.get("armIdentityBlinded") is True, "human review must be sampled and blind")
    require(
        REQUIRED_PROMOTION_REVIEWS.issubset(set(blind.get("escalationTriggers", []))),
        "blind human review must cover variance and non-discriminating assertion escalation",
    )

    promotion = data.get("promotionPolicy")
    require(isinstance(promotion, dict), "promotionPolicy must be an object")
    require(promotion.get("authority") == "advisory-only", "promotionPolicy must remain advisory-only")
    require(promotion.get("candidateScope") == "skill-or-workflow-revision", "promotionPolicy candidate scope drifted")
    require(
        REQUIRED_PROMOTION_EVIDENCE.issubset(set(promotion.get("requiredEvidence", []))),
        "promotionPolicy must require held-out, repeated, and no-primary-regression evidence",
    )
    require(
        REQUIRED_PROMOTION_REVIEWS.issubset(set(promotion.get("reviewTriggers", []))),
        "promotionPolicy must review high variance and non-discriminating assertions",
    )
    require(
        FORBIDDEN_AUTOMATIC_PROMOTION_ACTIONS.issubset(set(promotion.get("automaticActionsForbidden", []))),
        "promotionPolicy must forbid automatic promotion and skill/baseline modification",
    )


def validate_case_portfolio_contract(data: dict[str, Any]) -> None:
    portfolio = data.get("casePortfolio")
    require(isinstance(portfolio, dict), "casePortfolio must be an object")
    manifest_path = portfolio.get("manifestPath")
    require(
        manifest_path == "tests/e2e/fixtures/agentic-benchmark-cases.json",
        "casePortfolio manifest path drifted",
    )
    require(
        portfolio.get("implementationStatus") == "implemented",
        "casePortfolio must be implemented after concrete manifest validation",
    )
    require(portfolio.get("schemaVersion") == 1, "casePortfolio schema version must be 1")
    require(portfolio.get("caseCount") == 30, "casePortfolio case count must be 30")
    require(portfolio.get("scenarioClassCount") == 10, "casePortfolio scenario class count must be 10")
    require(portfolio.get("partitions") == EXPECTED_PORTFOLIO_PARTITIONS, "casePortfolio partitions drifted")
    require(portfolio.get("arms") == EXPECTED_LIVE_ARMS, "casePortfolio arms drifted")


def validate_run_profiles(data: dict[str, Any]) -> None:
    require(
        data.get("maximumSupportedWorkers") == MAXIMUM_SUPPORTED_WORKERS,
        "maximumSupportedWorkers must be 12",
    )
    profiles = data.get("runProfiles")
    require(isinstance(profiles, list), "runProfiles must be a list")
    require(all(isinstance(profile, dict) for profile in profiles), "runProfiles entries must be objects")
    profile_ids = [profile.get("id") for profile in profiles]
    require(
        all(isinstance(profile_id, str) and profile_id for profile_id in profile_ids),
        "run profile ids must be non-empty strings",
    )
    require(len(profile_ids) == len(set(profile_ids)), "runProfiles must contain unique ids")
    require(
        set(profile_ids) == set(EXPECTED_RUN_PROFILES),
        "runProfiles must define development-pilot, standard-held-out, and extended-held-out exactly",
    )

    for profile in profiles:
        profile_id = profile["id"]
        require(set(profile) == PROFILE_FIELDS, f"{profile_id} must contain exactly the run profile fields")
        expected = EXPECTED_RUN_PROFILES[profile_id]
        for field, expected_value in expected.items():
            require(
                profile.get(field) == expected_value,
                f"{profile_id}.{field} must be {expected_value!r}",
            )
        require(
            profile["workers"] <= data["maximumSupportedWorkers"],
            f"{profile_id}.workers exceeds maximumSupportedWorkers",
        )
        derived_target = profile["caseCount"] * profile["repetitionsPerCase"] * len(profile["arms"])
        require(
            profile["validRunTarget"] == derived_target,
            f"{profile_id}.validRunTarget must equal cases x repetitions x arms",
        )
        require(
            profile["paidAttemptCeiling"] >= profile["validRunTarget"],
            f"{profile_id}.paidAttemptCeiling must cover the valid target",
        )


def validate_metrics(data: dict[str, Any]) -> None:
    metrics = string_set(data, "primaryMetrics")
    missing = sorted(REQUIRED_PRIMARY_METRICS - metrics)
    require(not missing, f"missing primary metrics: {', '.join(missing)}")
    supporting = string_set(data, "supportingMetrics")
    require("diff-size" in supporting, "supporting metrics should allow diff-size without making it primary")
    require("diff-size" not in metrics, "diff-size must not be a primary Aegis success metric")


def validate_scenarios(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenarios = data.get("scenarioClasses", [])
    require(isinstance(scenarios, list), "scenarioClasses must be a list")
    by_id = {item.get("id"): item for item in scenarios if isinstance(item, dict)}
    require(len(by_id) == len(scenarios), "scenarioClasses must contain unique object ids")
    missing = sorted(REQUIRED_SCENARIOS - by_id.keys())
    require(not missing, f"missing scenario classes: {', '.join(missing)}")
    for scenario_id, item in by_id.items():
        require(item.get("promptShape"), f"{scenario_id} must define promptShape")
        positive = item.get("expectedPositiveBehavior", [])
        negative = item.get("expectedNegativeBehavior", [])
        required_metrics = item.get("requiredMetrics", [])
        require(len(positive) >= 2, f"{scenario_id} needs at least two positive behaviors")
        require(len(negative) >= 2, f"{scenario_id} needs at least two negative behaviors")
        require(bool(required_metrics), f"{scenario_id} must define requiredMetrics")
        require(
            set(required_metrics).issubset(REQUIRED_PRIMARY_METRICS),
            f"{scenario_id} uses non-primary required metrics",
        )
    return by_id


def fixture_ids(data: dict[str, Any], collection: str, label: str) -> set[str]:
    entries = data.get(collection, [])
    require(isinstance(entries, list), f"{label}.{collection} must be a list")
    ids: list[str] = []
    for entry in entries:
        require(isinstance(entry, dict), f"{label}.{collection} entries must be objects")
        entry_id = entry.get("id")
        require(isinstance(entry_id, str) and entry_id, f"{label} entry id must be a non-empty string")
        ids.append(entry_id)
    require(len(ids) == len(set(ids)), f"{label} entry ids must be unique")
    return set(ids)


def validate_coverage(
    root: Path,
    matrix_path: Path,
    data: dict[str, Any],
    scenarios: dict[str, dict[str, Any]],
) -> None:
    sources = data.get("coverageSources")
    require(isinstance(sources, dict), "coverageSources must be an object")
    workflow_path = resolve_repo_path(
        root,
        sources.get("workflowQualityMatrix"),
        "coverageSources.workflowQualityMatrix",
    )
    replay_path = resolve_repo_path(
        root,
        sources.get("controlledReplayManifest"),
        "coverageSources.controlledReplayManifest",
    )

    workflow_ids = fixture_ids(load_json(workflow_path), "samples", "workflow quality matrix")
    replay_manifest = load_json(replay_path)
    require(replay_manifest.get("version") == 2, "controlled replay manifest version must be 2")
    require(
        replay_manifest.get("authorityBoundary") == data.get("authorityBoundary"),
        "controlled replay manifest authority boundary must match the benchmark matrix",
    )
    require(
        replay_manifest.get("coverageMappingPolicy") == "exact-bidirectional-with-benchmark-matrix",
        "controlled replay manifest must require exact bidirectional coverage mapping",
    )
    reverse_matrix_path = resolve_repo_path(
        root,
        replay_manifest.get("benchmarkMatrix"),
        "controlledReplayManifest.benchmarkMatrix",
    )
    require(
        reverse_matrix_path == matrix_path.resolve(),
        "controlled replay manifest must point back to the validated benchmark matrix",
    )
    replay_samples = replay_manifest.get("samples", [])
    require(isinstance(replay_samples, list), "controlled replay manifest samples must be a list")

    manifest_mapping: dict[str, str] = {}
    for sample in replay_samples:
        require(isinstance(sample, dict), "controlled replay samples must be objects")
        sample_id = sample.get("id")
        scenario_id = sample.get("scenarioClass")
        require(isinstance(sample_id, str) and sample_id, "controlled replay sample id must be a non-empty string")
        require(sample_id not in manifest_mapping, f"duplicate controlled replay sample id: {sample_id}")
        require(scenario_id in scenarios, f"{sample_id} references unknown scenario class: {scenario_id}")
        require(sample.get("evaluationTier") == "controlled-replay", f"{sample_id} must use controlled-replay tier")
        require(sample.get("datasetPartition") == "development", f"{sample_id} must use development partition")
        arms = sample.get("arms", [])
        require(isinstance(arms, list) and arms, f"{sample_id} arms must be a non-empty list")
        sample_arm_ids = [arm.get("id") for arm in arms if isinstance(arm, dict)]
        require(len(sample_arm_ids) == len(arms), f"{sample_id} arm entries must be objects")
        require(len(sample_arm_ids) == len(set(sample_arm_ids)), f"{sample_id} arm ids must be unique")
        require(
            set(sample_arm_ids) == CURRENT_CONTROLLED_REPLAY_ARMS,
            f"{sample_id} current controlled replay arms must be exactly baseline-no-aegis and aegis-auto",
        )
        sample_arms_by_id = {arm["id"]: arm for arm in arms}
        for arm_id, expected_pass in CURRENT_CONTROLLED_REPLAY_EXPECTED_PASS.items():
            require(
                sample_arms_by_id[arm_id].get("expectedContractPass") is expected_pass,
                f"{sample_id}/{arm_id} expectedContractPass must be {str(expected_pass).lower()}",
            )
        require(
            sample.get("comparisons") == [CURRENT_CONTROLLED_REPLAY_COMPARISON],
            f"{sample_id} current controlled replay comparison must be aegis-auto over baseline-no-aegis",
        )
        manifest_mapping[sample_id] = scenario_id

    matrix_mapping: dict[str, str] = {}
    for scenario_id, scenario in scenarios.items():
        coverage = scenario.get("coverage")
        require(isinstance(coverage, dict), f"{scenario_id}.coverage must be an object")
        workflow_refs = string_list(
            coverage,
            "workflowQualityFixtureRefs",
            f"{scenario_id}.coverage",
        )
        require(workflow_refs, f"{scenario_id} must reference deterministic workflow-quality coverage")
        missing_workflow_refs = sorted(set(workflow_refs) - workflow_ids)
        require(
            not missing_workflow_refs,
            f"{scenario_id} references unknown workflow-quality fixtures: {', '.join(missing_workflow_refs)}",
        )

        replay_refs = string_list(
            coverage,
            "controlledReplaySampleRefs",
            f"{scenario_id}.coverage",
        )
        expected_replay_refs = {
            sample_id
            for sample_id, expected_scenario_id in EXPECTED_CONTROLLED_REPLAY_MAPPING.items()
            if expected_scenario_id == scenario_id
        }
        require(
            set(replay_refs) == expected_replay_refs,
            f"{scenario_id} controlled replay refs must match the public baseline: "
            f"expected {sorted(expected_replay_refs)}, got {sorted(replay_refs)}",
        )
        live_eligible = coverage.get("liveReplayEligible")
        require(isinstance(live_eligible, bool), f"{scenario_id}.coverage.liveReplayEligible must be boolean")
        require(
            live_eligible == bool(replay_refs),
            f"{scenario_id} live replay eligibility must equal controlled replay availability",
        )
        for replay_ref in replay_refs:
            require(
                replay_ref not in matrix_mapping,
                f"controlled replay sample is mapped by multiple scenarios: {replay_ref}",
            )
            matrix_mapping[replay_ref] = scenario_id

    missing_matrix_refs = sorted(manifest_mapping.keys() - matrix_mapping.keys())
    extra_matrix_refs = sorted(matrix_mapping.keys() - manifest_mapping.keys())
    require(not missing_matrix_refs, f"controlled replay samples missing from matrix coverage: {', '.join(missing_matrix_refs)}")
    require(not extra_matrix_refs, f"matrix coverage references unknown controlled replay samples: {', '.join(extra_matrix_refs)}")
    require(
        manifest_mapping == EXPECTED_CONTROLLED_REPLAY_MAPPING,
        "controlled replay manifest mappings must exactly match the public baseline",
    )
    mismatched = sorted(
        sample_id
        for sample_id, scenario_id in manifest_mapping.items()
        if matrix_mapping[sample_id] != scenario_id
    )
    require(not mismatched, f"controlled replay scenario mappings disagree: {', '.join(mismatched)}")


def validate_isolation_and_boundary(data: dict[str, Any]) -> None:
    controls = string_set(data, "isolationControls")
    missing_controls = sorted(REQUIRED_ISOLATION_CONTROLS - controls)
    require(not missing_controls, f"missing isolation controls: {', '.join(missing_controls)}")

    require(
        data.get("authorityBoundary") == "advisory-method-pack-evidence-not-completion-authority",
        "authorityBoundary must preserve method-pack advisory scope",
    )
    boundaries = data.get("reportBoundaries", {})
    require(isinstance(boundaries, dict), "reportBoundaries must be an object")
    forbidden = set(boundaries.get("forbiddenClaims", []))
    missing_forbidden = sorted(FORBIDDEN_CLAIMS - forbidden)
    require(not missing_forbidden, f"missing forbidden claims: {', '.join(missing_forbidden)}")


def validate_matrix(path: Path) -> None:
    data = load_json(path)
    require(data.get("version") == 4, "version must be 4")
    require(data.get("status") == "draft", "status must be draft")
    require("runtime authority" in data.get("primaryQuestion", ""), "primary question must name runtime authority boundary")
    validate_arms(data)
    validate_evaluation_contract(data)
    validate_case_portfolio_contract(data)
    validate_run_profiles(data)
    validate_metrics(data)
    scenarios = validate_scenarios(data)
    validate_coverage(repo_root(), path, data, scenarios)
    validate_isolation_and_boundary(data)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: validate_agentic_benchmark_matrix.py <matrix-json>")
    validate_matrix(Path(argv[1]))
    print("  [PASS] agentic benchmark matrix preserves metrics, isolation, scenario coverage, replay mappings, and authority boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
