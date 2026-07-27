#!/usr/bin/env python3
"""Validate controlled replay samples against the agentic benchmark contract."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
SOURCE_PROJECT_POLICY = "controlled-fixture-projects-only"
WORKSPACE_POLICY = "copy-seed-to-temp-per-arm"
COVERAGE_MAPPING_POLICY = "exact-bidirectional-with-benchmark-matrix"
CONTROLLED_REPLAY_TIER = "controlled-replay"
DEVELOPMENT_PARTITION = "development"
REPORT_VERSION = 1
REPORT_TYPE = "controlled-replay-advisory"
SCORE_SOURCE = "static-transcript-contract-analysis"

REQUIRED_SAMPLE_CONTROLS = {
    "fresh-temporary-workspace-per-run",
    "same-prompt-and-seeded-repo-per-arm",
    "preserve-transcripts-and-diffs",
}

FORBIDDEN_PROMPT_TERMS = {
    "aegis",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "verification-before-completion",
    "requirement ready check",
    "change necessity",
}

EXPECTED_CONTROLLED_REPLAY_MAPPING = {
    "change-necessity-before-edit": "quick-bug-change-necessity",
    "shared-owner-bug-repair": "shared-owner-bug-repair",
    "completion-evidence-boundary": "completion-claim-with-missing-evidence",
}

REQUIRED_EVALUATION_TIERS = {
    "deterministic-static",
    CONTROLLED_REPLAY_TIER,
    "opt-in-live-repeated-held-out",
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

REQUIRED_ARMS = {"baseline-no-aegis", "aegis-auto", "aegis-explicit", "previous-aegis"}
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(root: Path, value: str, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a non-empty string")
    path = (root / value).resolve()
    require(root == path or root in path.parents, f"{label} must stay inside the repo: {value}")
    return path


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def load_benchmark_contract(root: Path, matrix_path: str) -> dict[str, Any]:
    matrix = load_json(resolve_repo_path(root, matrix_path, "benchmarkMatrix"))
    require(matrix.get("version") == 2, "benchmark matrix version must be 2")
    require(matrix.get("authorityBoundary") == AUTHORITY_BOUNDARY, "benchmark matrix boundary drifted")
    validate_evaluation_contract(matrix)
    return matrix


def validate_evaluation_contract(matrix: dict[str, Any]) -> None:
    arms = matrix.get("arms", [])
    require(isinstance(arms, list), "benchmark arms must be a list")
    require(all(isinstance(arm, dict) for arm in arms), "each arm must be an object")
    arm_ids = [arm.get("id") for arm in arms]
    require(all(isinstance(arm_id, str) and arm_id for arm_id in arm_ids), "arm ids must be non-empty strings")
    require(len(arm_ids) == len(set(arm_ids)), "arms must contain unique object ids")
    missing_arms = sorted(REQUIRED_ARMS - set(arm_ids))
    require(not missing_arms, f"missing benchmark arms: {', '.join(missing_arms)}")
    arms_by_id = {arm["id"]: arm for arm in arms}
    for arm in arms:
        require(arm.get("requiresIsolatedConfig") is True, f"{arm.get('id')} must isolate config")
    previous = arms_by_id.get("previous-aegis")
    require(isinstance(previous, dict), "benchmark matrix must define previous-aegis")
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

    tiers = matrix.get("evaluationTiers", [])
    require(isinstance(tiers, list), "evaluationTiers must be a list")
    tiers_by_id = {tier.get("id"): tier for tier in tiers if isinstance(tier, dict)}
    require(len(tiers_by_id) == len(tiers), "evaluationTiers must contain unique object ids")
    require(set(tiers_by_id) == REQUIRED_EVALUATION_TIERS, "evaluationTiers must define the four-tier contract exactly")

    deterministic = tiers_by_id["deterministic-static"]
    require(
        deterministic.get("implementationStatus") == "implemented" and deterministic.get("defaultCi") is True,
        "deterministic-static must be the implemented default CI tier",
    )
    require(deterministic.get("supportsPromotionEvidence") is False, "deterministic-static cannot support promotion evidence")
    controlled = tiers_by_id[CONTROLLED_REPLAY_TIER]
    require(controlled.get("implementationStatus") == "implemented", "controlled-replay must be implemented")
    require(controlled.get("defaultCi") is False, "controlled-replay must not be the default CI tier")
    require(controlled.get("executionShape") == "single-static-captured-transcript", "controlled-replay must remain single static replay")
    require(controlled.get("datasetPartitions") == [DEVELOPMENT_PARTITION], "controlled-replay must remain development-only")
    require(controlled.get("scoreSource") == SCORE_SOURCE, "controlled-replay score source drifted")
    require(controlled.get("supportsPromotionEvidence") is False, "controlled-replay cannot support promotion evidence")
    require(
        {"variance-evidence", "held-out-evidence", "blind-review-evidence", "candidate-promotion-evidence"}.issubset(
            set(controlled.get("unsupportedClaims", []))
        ),
        "controlled-replay must forbid variance, held-out, blind-review, and promotion claims",
    )
    live = tiers_by_id["opt-in-live-repeated-held-out"]
    require(live.get("implementationStatus") == "contract-only", "live repeated/held-out tier must remain contract-only")
    require(
        live.get("defaultCi") is False and live.get("optIn") is True,
        "live repeated/held-out tier must be opt-in outside default CI",
    )
    require(
        {"repeated-run-evidence", "held-out-evidence"}.issubset(set(live.get("requiredEvidence", []))),
        "live repeated/held-out tier must require repeated and held-out evidence",
    )
    blind = tiers_by_id["sampled-blind-human-review"]
    require(blind.get("implementationStatus") == "contract-only", "blind human review tier must remain contract-only")
    require(blind.get("defaultCi") is False, "blind human review tier must not run in default CI")
    require(
        blind.get("sampled") is True and blind.get("armIdentityBlinded") is True,
        "human review must be sampled and blind",
    )
    require(
        REQUIRED_PROMOTION_REVIEWS.issubset(set(blind.get("escalationTriggers", []))),
        "blind human review must cover variance and non-discriminating assertion escalation",
    )

    promotion = matrix.get("promotionPolicy", {})
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
        {"promote-candidate", "modify-skill-or-workflow", "modify-baseline"}.issubset(
            set(promotion.get("automaticActionsForbidden", []))
        ),
        "promotionPolicy must forbid automatic promotion and skill/baseline modification",
    )


def validate_prompt(prompt_path: Path, sample_id: str) -> None:
    prompt_lower = prompt_path.read_text(encoding="utf-8").lower()
    hits = sorted(term for term in FORBIDDEN_PROMPT_TERMS if term in prompt_lower)
    require(not hits, f"{sample_id} prompt discloses expected route terms: {', '.join(hits)}")


def validate_manifest(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(manifest.get("version") == 2, "replay manifest version must be 2")
    require(manifest.get("status") == "draft", "replay manifest status must be draft")
    require(manifest.get("authorityBoundary") == AUTHORITY_BOUNDARY, "replay manifest boundary drifted")
    require(
        manifest.get("sourceProjectPolicy") == SOURCE_PROJECT_POLICY,
        f"sourceProjectPolicy must be {SOURCE_PROJECT_POLICY}",
    )
    require(
        manifest.get("workspacePolicy") == WORKSPACE_POLICY,
        f"workspacePolicy must be {WORKSPACE_POLICY}",
    )
    require(
        manifest.get("coverageMappingPolicy") == COVERAGE_MAPPING_POLICY,
        f"coverageMappingPolicy must be {COVERAGE_MAPPING_POLICY}",
    )
    live_execution = manifest.get("liveExecution", {})
    require(isinstance(live_execution, dict), "liveExecution must be an object when present")
    if live_execution:
        require(live_execution.get("status") == "opt-in", "liveExecution.status must be opt-in")
        require(live_execution.get("requiresEnv") == "AEGIS_LIVE_REPLAY=1", "liveExecution must require AEGIS_LIVE_REPLAY=1")
        require(live_execution.get("defaultArm") == "aegis-auto", "liveExecution.defaultArm must be aegis-auto")
        require(live_execution.get("baselineNoAegisStatus") == "not-created-by-default", "liveExecution must not create no-Aegis baseline by default")
        require(live_execution.get("outputPolicy") == "repo-local-tmp-only", "liveExecution outputPolicy must be repo-local-tmp-only")
        require(live_execution.get("authorityBoundary") == AUTHORITY_BOUNDARY, "liveExecution boundary drifted")
        entrypoint = resolve_repo_path(root, live_execution.get("entrypoint", ""), "liveExecution.entrypoint")
        require(entrypoint.is_file(), "liveExecution.entrypoint must exist")

    matrix = load_benchmark_contract(root, manifest.get("benchmarkMatrix", ""))
    arm_ids = {arm.get("id") for arm in matrix.get("arms", []) if isinstance(arm, dict)}
    scenario_ids = {
        scenario.get("id"): scenario
        for scenario in matrix.get("scenarioClasses", [])
        if isinstance(scenario, dict)
    }
    primary_metrics = set(matrix.get("primaryMetrics", []))

    samples = manifest.get("samples", [])
    require(isinstance(samples, list) and samples, "samples must be a non-empty list")

    seed_root = (root / "tests/e2e/fixtures/replay-projects").resolve()
    sample_mapping: dict[str, str] = {}
    for sample in samples:
        require(isinstance(sample, dict), "each replay sample must be an object")
        sample_id = sample.get("id")
        require(isinstance(sample_id, str) and sample_id, "sample id must be a non-empty string")
        require(sample_id not in sample_mapping, f"duplicate replay sample id: {sample_id}")

        scenario_class = sample.get("scenarioClass")
        require(scenario_class in scenario_ids, f"{sample_id} scenarioClass is not in benchmark matrix")
        require(sample.get("evaluationTier") == CONTROLLED_REPLAY_TIER, f"{sample_id} must use controlled-replay tier")
        require(sample.get("datasetPartition") == DEVELOPMENT_PARTITION, f"{sample_id} must use development partition")
        sample_mapping[sample_id] = scenario_class

        prompt_path = resolve_repo_path(root, sample.get("promptPath", ""), f"{sample_id}.promptPath")
        require(prompt_path.is_file(), f"{sample_id} promptPath must exist")
        validate_prompt(prompt_path, sample_id)

        seed_path = resolve_repo_path(root, sample.get("seedProjectPath", ""), f"{sample_id}.seedProjectPath")
        require(seed_path.is_dir(), f"{sample_id} seedProjectPath must exist")
        require(seed_root == seed_path or seed_root in seed_path.parents, f"{sample_id} seed project must use fixtures")

        controls = set(sample.get("isolationControls", []))
        missing_controls = sorted(REQUIRED_SAMPLE_CONTROLS - controls)
        require(not missing_controls, f"{sample_id} missing isolation controls: {', '.join(missing_controls)}")

        metrics = set(sample.get("benchmarkMetrics", []))
        require(metrics, f"{sample_id} benchmarkMetrics must be non-empty")
        require(metrics.issubset(primary_metrics), f"{sample_id} uses metrics outside primary benchmark metrics")

        scenario_metrics = set(scenario_ids[scenario_class].get("requiredMetrics", []))
        require(metrics & scenario_metrics, f"{sample_id} must cover at least one scenario required metric")

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

        for arm in arms:
            require(isinstance(arm, dict), f"{sample_id} arm entries must be objects")
            arm_id = arm.get("id")
            require(arm_id in arm_ids, f"{sample_id} arm is not in benchmark matrix: {arm_id}")
            for field in ("transcriptPath", "expectedBehaviorPath", "expectedArtifactsPath"):
                path = resolve_repo_path(root, arm.get(field, ""), f"{sample_id}/{arm_id}.{field}")
                require(path.is_file(), f"{sample_id}/{arm_id}.{field} must exist")

        comparisons = sample.get("comparisons", [])
        require(
            comparisons == [CURRENT_CONTROLLED_REPLAY_COMPARISON],
            f"{sample_id} current controlled replay comparison must be aegis-auto over baseline-no-aegis",
        )

    matrix_mapping: dict[str, str] = {}
    for scenario_id, scenario in scenario_ids.items():
        coverage = scenario.get("coverage")
        require(isinstance(coverage, dict), f"{scenario_id}.coverage must be an object")
        replay_refs = coverage.get("controlledReplaySampleRefs")
        require(isinstance(replay_refs, list), f"{scenario_id}.controlledReplaySampleRefs must be a list")
        require(
            all(isinstance(ref, str) and ref for ref in replay_refs),
            f"{scenario_id}.controlledReplaySampleRefs must contain non-empty strings",
        )
        require(
            len(replay_refs) == len(set(replay_refs)),
            f"{scenario_id}.controlledReplaySampleRefs must not contain duplicates",
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
        require(isinstance(live_eligible, bool), f"{scenario_id}.liveReplayEligible must be boolean")
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

    missing_matrix_refs = sorted(sample_mapping.keys() - matrix_mapping.keys())
    extra_matrix_refs = sorted(matrix_mapping.keys() - sample_mapping.keys())
    require(not missing_matrix_refs, f"replay samples missing from matrix coverage: {', '.join(missing_matrix_refs)}")
    require(not extra_matrix_refs, f"matrix coverage references unknown replay samples: {', '.join(extra_matrix_refs)}")
    require(
        sample_mapping == EXPECTED_CONTROLLED_REPLAY_MAPPING,
        "replay manifest mappings must exactly match the public baseline",
    )
    mismatched = sorted(
        sample_id
        for sample_id, scenario_id in sample_mapping.items()
        if matrix_mapping[sample_id] != scenario_id
    )
    require(not mismatched, f"replay scenario mappings disagree with matrix coverage: {', '.join(mismatched)}")

    return matrix, samples


def remove_tree_under(root: Path, target: Path, allowed_parent: Path, label: str) -> None:
    resolved = target.resolve()
    allowed = allowed_parent.resolve()
    require(
        allowed in resolved.parents,
        f"{label} must be a strict child of {allowed}: {target}",
    )
    if resolved.exists():
        shutil.rmtree(resolved, onerror=remove_readonly)


def reset_workspace(root: Path, workspace_root: Path) -> None:
    resolved = workspace_root.resolve()
    allowed_root = (root / ".tmp").resolve()
    require(
        allowed_root in resolved.parents,
        f"workspace root must be a strict child of repo .tmp: {workspace_root}",
    )
    remove_tree_under(root, resolved, allowed_root, "workspace root")
    resolved.mkdir(parents=True)


def resolve_tmp_output_path(root: Path, value: str, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a non-empty string")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    allowed_root = (root / ".tmp").resolve()
    require(allowed_root in resolved.parents, f"{label} must stay under repo .tmp: {value}")
    return resolved


def remove_readonly(function: Any, path: str, _excinfo: Any) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def copy_seed_project(seed_path: Path, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(seed_path, target_path)


def init_git_workspace(target_path: Path) -> bool:
    if shutil.which("git") is None:
        return False
    commands = [
        ["git", "init"],
        ["git", "config", "user.email", "aegis-replay@example.invalid"],
        ["git", "config", "user.name", "Aegis Replay"],
        ["git", "add", "."],
        ["git", "commit", "-m", "Initial controlled replay seed"],
    ]
    for command in commands:
        completed = subprocess.run(command, cwd=target_path, text=True, capture_output=True)
        if completed.returncode != 0:
            raise SystemExit(f"git workspace setup failed in {target_path}: {' '.join(command)}\n{completed.stderr}")
    return True


def replay_score(summary: dict[str, Any]) -> int:
    skill_score = max(
        len(summary.get("matchedSkillSequence", [])),
        len(summary.get("requiredSkillsPresent", [])),
    )
    return skill_score + len(summary.get("requiredArtifactsPresent", []))


def find_bash() -> str:
    candidates = []
    env_bash = os.environ.get("AEGIS_BASH")
    if env_bash:
        candidates.append(env_bash)

    path_bash = shutil.which("bash")
    if path_bash and "system32" not in path_bash.lower():
        candidates.append(path_bash)

    candidates.extend(
        [
            "C:/Program Files/Git/bin/bash.exe",
            "C:/Program Files/Git/usr/bin/bash.exe",
            "/usr/bin/bash",
            "/bin/bash",
        ]
    )

    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate

    return "bash"


def run_transcript_analysis(
    root: Path,
    bash_path: str,
    transcript_path: Path,
    expected_behavior_path: Path,
    expected_artifacts_path: Path,
    summary_path: Path,
) -> subprocess.CompletedProcess[str]:
    command = [
        bash_path,
        (root / "tests/e2e/analyze-transcript.sh").as_posix(),
        "--transcript",
        transcript_path.as_posix(),
        "--expected-behavior",
        expected_behavior_path.as_posix(),
        "--expected-artifacts",
        expected_artifacts_path.as_posix(),
        "--summary-json",
        summary_path.as_posix(),
        "--quiet",
    ]
    return subprocess.run(command, cwd=root, text=True, capture_output=True)


def run_samples(
    root: Path,
    manifest: dict[str, Any],
    samples: list[dict[str, Any]],
    workspace_root: Path,
    report_path: Path | None,
) -> None:
    reset_workspace(root, workspace_root)
    bash_path = find_bash()
    summary_by_sample: dict[str, dict[str, dict[str, Any]]] = {}
    failures: list[str] = []
    report_samples: list[dict[str, Any]] = []

    for sample in samples:
        sample_id = sample["id"]
        seed_path = resolve_repo_path(root, sample["seedProjectPath"], f"{sample_id}.seedProjectPath")
        summary_by_sample[sample_id] = {}
        report_sample = {
            "id": sample_id,
            "scenarioClass": sample["scenarioClass"],
            "evaluationTier": sample["evaluationTier"],
            "datasetPartition": sample["datasetPartition"],
            "arms": [],
            "comparisons": [],
            "failures": [],
        }
        report_samples.append(report_sample)

        print(f"Running controlled replay sample: {sample_id}")
        for arm in sample["arms"]:
            arm_id = arm["id"]
            arm_root = workspace_root / sample_id / arm_id
            workspace_path = arm_root / "workspace"
            summary_path = arm_root / "summary.json"
            metadata_path = arm_root / "replay-metadata.json"

            copy_seed_project(seed_path, workspace_path)
            git_initialized = init_git_workspace(workspace_path)

            metadata = {
                "sampleId": sample_id,
                "arm": arm_id,
                "sourceProjectPolicy": manifest["sourceProjectPolicy"],
                "workspacePolicy": manifest["workspacePolicy"],
                "seedProjectPath": relative_path(root, seed_path),
                "workspacePath": relative_path(root, workspace_path),
                "gitInitialized": git_initialized,
                "authorityBoundary": manifest["authorityBoundary"],
            }
            metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

            completed = run_transcript_analysis(
                root,
                bash_path,
                resolve_repo_path(root, arm["transcriptPath"], f"{sample_id}/{arm_id}.transcriptPath"),
                resolve_repo_path(root, arm["expectedBehaviorPath"], f"{sample_id}/{arm_id}.expectedBehaviorPath"),
                resolve_repo_path(root, arm["expectedArtifactsPath"], f"{sample_id}/{arm_id}.expectedArtifactsPath"),
                summary_path,
            )

            expected_pass = arm["expectedContractPass"]
            actual_pass = completed.returncode == 0

            if not summary_path.is_file():
                report_sample["arms"].append(
                    {
                        "id": arm_id,
                        "actualContractPass": actual_pass,
                        "expectedContractPass": expected_pass,
                        "score": None,
                    }
                )
                failures.append(
                    f"{sample_id}/{arm_id}: transcript analysis did not write summary\n"
                    f"{completed.stdout}{completed.stderr}"
                )
                report_sample["failures"].append({"kind": "missing-summary", "arm": arm_id})
                continue

            summary = load_json(summary_path)
            summary_by_sample[sample_id][arm_id] = summary
            score = replay_score(summary)
            report_sample["arms"].append(
                {
                    "id": arm_id,
                    "actualContractPass": actual_pass,
                    "expectedContractPass": expected_pass,
                    "score": score,
                }
            )
            if actual_pass != expected_pass:
                failures.append(
                    f"{sample_id}/{arm_id}: expected contract pass={expected_pass}, got {actual_pass}\n"
                    f"{completed.stdout}{completed.stderr}"
                )
                report_sample["failures"].append(
                    {
                        "kind": "arm-contract-mismatch",
                        "arm": arm_id,
                        "expectedContractPass": expected_pass,
                        "actualContractPass": actual_pass,
                    }
                )
            status = "PASS" if actual_pass else "WEAKER"
            print(f"  [{status}] {arm_id} score={score} workspace={relative_path(root, workspace_path)}")

        for comparison in sample["comparisons"]:
            if (
                comparison["strongerArm"] not in summary_by_sample[sample_id]
                or comparison["weakerArm"] not in summary_by_sample[sample_id]
            ):
                report_sample["comparisons"].append(
                    {
                        "strongerArm": comparison["strongerArm"],
                        "weakerArm": comparison["weakerArm"],
                        "scoreDelta": None,
                        "pass": False,
                    }
                )
                failures.append(f"{sample_id}: comparison skipped because an arm summary is missing")
                report_sample["failures"].append({"kind": "comparison-skipped-missing-summary"})
                continue
            stronger = summary_by_sample[sample_id][comparison["strongerArm"]]
            weaker = summary_by_sample[sample_id][comparison["weakerArm"]]
            stronger_score = replay_score(stronger)
            weaker_score = replay_score(weaker)
            comparison_pass = stronger.get("overallPass") is True and stronger_score > weaker_score
            report_sample["comparisons"].append(
                {
                    "strongerArm": comparison["strongerArm"],
                    "weakerArm": comparison["weakerArm"],
                    "scoreDelta": stronger_score - weaker_score,
                    "pass": comparison_pass,
                }
            )
            if not comparison_pass:
                failures.append(
                    f"{sample_id}: {comparison['strongerArm']} score {stronger_score} did not beat "
                    f"{comparison['weakerArm']} score {weaker_score}"
                )
                report_sample["failures"].append(
                    {
                        "kind": "comparison-failed",
                        "strongerArm": comparison["strongerArm"],
                        "weakerArm": comparison["weakerArm"],
                    }
                )
            print(
                f"  [COMPARE] {comparison['strongerArm']}={stronger_score} "
                f"{comparison['weakerArm']}={weaker_score}"
            )
        report_sample["overallPass"] = not report_sample["failures"]
        print("")

    if report_path is not None:
        report_failures = [
            {"sampleId": sample["id"], **failure}
            for sample in report_samples
            for failure in sample["failures"]
        ]
        report = {
            "version": REPORT_VERSION,
            "reportType": REPORT_TYPE,
            "authorityBoundary": manifest["authorityBoundary"],
            "evaluationTier": CONTROLLED_REPLAY_TIER,
            "datasetPartition": DEVELOPMENT_PARTITION,
            "runCount": 1,
            "scoreSource": SCORE_SOURCE,
            "overallPass": not report_failures,
            "failures": report_failures,
            "samples": report_samples,
            "unknowns": [
                "tokens",
                "cost",
                "variance",
                "held-out-evidence",
                "blind-human-review-evidence",
            ],
            "promotionStatus": "not-evaluated",
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Controlled replay report: {relative_path(root, report_path)}")

    if failures:
        raise SystemExit("\n".join(failures))

    print(f"Controlled replay samples passed: {len(samples)}")


def find_sample(samples: list[dict[str, Any]], sample_id: str) -> dict[str, Any]:
    for sample in samples:
        if sample["id"] == sample_id:
            return sample
    raise SystemExit(f"unknown replay sample: {sample_id}")


def find_arm(sample: dict[str, Any], arm_id: str) -> dict[str, Any]:
    for arm in sample["arms"]:
        if arm["id"] == arm_id:
            return arm
    raise SystemExit(f"unknown arm for {sample['id']}: {arm_id}")


def prepare_live_run(root: Path, manifest: dict[str, Any], samples: list[dict[str, Any]], sample_id: str, arm_id: str, workspace_root: Path) -> None:
    allowed_root = (root / ".tmp").resolve()
    resolved_workspace_root = workspace_root.resolve()
    require(
        allowed_root in resolved_workspace_root.parents,
        f"workspace root must be a strict child of repo .tmp: {workspace_root}",
    )

    sample = find_sample(samples, sample_id)
    arm = find_arm(sample, arm_id)
    seed_path = resolve_repo_path(root, sample["seedProjectPath"], f"{sample_id}.seedProjectPath")
    prompt_path = resolve_repo_path(root, sample["promptPath"], f"{sample_id}.promptPath")
    arm_root = workspace_root / sample_id / arm_id
    workspace_path = arm_root / "workspace"
    raw_log_path = arm_root / "raw-live-output.log"
    normalized_transcript_path = arm_root / "normalized-transcript.jsonl"
    summary_path = arm_root / "summary.json"
    metadata_path = arm_root / "replay-metadata.json"

    remove_tree_under(root, arm_root, allowed_root, "live replay arm root")
    workspace_path.parent.mkdir(parents=True, exist_ok=True)
    copy_seed_project(seed_path, workspace_path)
    git_initialized = init_git_workspace(workspace_path)

    metadata = {
        "sampleId": sample_id,
        "arm": arm_id,
        "mode": "live-replay-capture",
        "sourceProjectPolicy": manifest["sourceProjectPolicy"],
        "workspacePolicy": manifest["workspacePolicy"],
        "seedProjectPath": relative_path(root, seed_path),
        "promptPath": relative_path(root, prompt_path),
        "workspacePath": relative_path(root, workspace_path),
        "rawLogPath": relative_path(root, raw_log_path),
        "normalizedTranscriptPath": relative_path(root, normalized_transcript_path),
        "summaryPath": relative_path(root, summary_path),
        "expectedBehaviorPath": arm["expectedBehaviorPath"],
        "expectedArtifactsPath": arm["expectedArtifactsPath"],
        "gitInitialized": git_initialized,
        "authorityBoundary": manifest["authorityBoundary"],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    output = dict(metadata)
    output["outputRoot"] = relative_path(root, arm_root)
    output["metadataPath"] = relative_path(root, metadata_path)
    print(json.dumps(output, indent=2))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default="tests/e2e/fixtures/replay-samples.json",
        help="Replay sample manifest path, relative to repo root.",
    )
    parser.add_argument(
        "--workspace-root",
        default=".tmp/e2e-controlled-replay",
        help="Temporary workspace root, relative to repo root. Must stay under .tmp.",
    )
    parser.add_argument("--validate-only", action="store_true", help="Validate manifest without preparing workspaces.")
    parser.add_argument("--prepare-live-run", action="store_true", help="Prepare a temporary workspace for one live replay run.")
    parser.add_argument(
        "--report-json",
        help="Optional structured controlled replay report path. Must stay under repo .tmp.",
    )
    parser.add_argument("--sample", help="Replay sample id used with --prepare-live-run.")
    parser.add_argument("--arm", default="aegis-auto", help="Benchmark arm id used with --prepare-live-run.")
    args = parser.parse_args(argv)

    root = repo_root()
    manifest_path = resolve_repo_path(root, args.manifest, "manifest")
    manifest = load_json(manifest_path)
    _, samples = validate_manifest(root, manifest)

    if args.report_json:
        require(
            not args.validate_only and not args.prepare_live_run,
            "--report-json is only supported when running controlled replay samples",
        )
        report_path = resolve_tmp_output_path(root, args.report_json, "report-json")
    else:
        report_path = None

    if args.validate_only:
        print(f"Controlled replay manifest is valid: {relative_path(root, manifest_path)}")
        return 0

    workspace_root = resolve_repo_path(root, args.workspace_root, "workspace-root")
    if args.prepare_live_run:
        require(bool(args.sample), "--sample is required with --prepare-live-run")
        prepare_live_run(root, manifest, samples, args.sample, args.arm, workspace_root)
        return 0

    run_samples(root, manifest, samples, workspace_root, report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
