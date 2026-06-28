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
    require(matrix.get("authorityBoundary") == AUTHORITY_BOUNDARY, "benchmark matrix boundary drifted")
    return matrix


def validate_prompt(prompt_path: Path, sample_id: str) -> None:
    prompt_lower = prompt_path.read_text(encoding="utf-8").lower()
    hits = sorted(term for term in FORBIDDEN_PROMPT_TERMS if term in prompt_lower)
    require(not hits, f"{sample_id} prompt discloses expected route terms: {', '.join(hits)}")


def validate_manifest(root: Path, manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(manifest.get("version") == 1, "replay manifest version must be 1")
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
    for sample in samples:
        require(isinstance(sample, dict), "each replay sample must be an object")
        sample_id = sample.get("id")
        require(isinstance(sample_id, str) and sample_id, "sample id must be a non-empty string")

        scenario_class = sample.get("scenarioClass")
        require(scenario_class in scenario_ids, f"{sample_id} scenarioClass is not in benchmark matrix")

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
        sample_arm_ids = {arm.get("id") for arm in arms if isinstance(arm, dict)}
        require({"baseline-no-aegis", "aegis-auto"}.issubset(sample_arm_ids), f"{sample_id} must include baseline-no-aegis and aegis-auto")

        for arm in arms:
            require(isinstance(arm, dict), f"{sample_id} arm entries must be objects")
            arm_id = arm.get("id")
            require(arm_id in arm_ids, f"{sample_id} arm is not in benchmark matrix: {arm_id}")
            require(isinstance(arm.get("expectedContractPass"), bool), f"{sample_id}/{arm_id} expectedContractPass must be boolean")
            for field in ("transcriptPath", "expectedBehaviorPath", "expectedArtifactsPath"):
                path = resolve_repo_path(root, arm.get(field, ""), f"{sample_id}/{arm_id}.{field}")
                require(path.is_file(), f"{sample_id}/{arm_id}.{field} must exist")

        comparisons = sample.get("comparisons", [])
        require(isinstance(comparisons, list) and comparisons, f"{sample_id} comparisons must be non-empty")
        for comparison in comparisons:
            require(comparison.get("strongerArm") in sample_arm_ids, f"{sample_id} comparison strongerArm missing")
            require(comparison.get("weakerArm") in sample_arm_ids, f"{sample_id} comparison weakerArm missing")
            require(
                comparison.get("expectation") == "stronger-passes-and-scores-higher",
                f"{sample_id} comparison expectation must be stronger-passes-and-scores-higher",
            )

    return matrix, samples


def remove_tree_under(root: Path, target: Path, allowed_parent: Path, label: str) -> None:
    resolved = target.resolve()
    allowed = allowed_parent.resolve()
    require(
        resolved == allowed or allowed in resolved.parents,
        f"{label} must stay under {allowed}: {target}",
    )
    if resolved.exists():
        shutil.rmtree(resolved, onerror=remove_readonly)


def reset_workspace(root: Path, workspace_root: Path) -> None:
    resolved = workspace_root.resolve()
    allowed_root = (root / ".tmp").resolve()
    require(
        resolved == allowed_root or allowed_root in resolved.parents,
        f"workspace root must be under .tmp: {workspace_root}",
    )
    remove_tree_under(root, resolved, allowed_root, "workspace root")
    resolved.mkdir(parents=True)


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
    return len(summary.get("matchedSkillSequence", [])) + len(summary.get("requiredArtifactsPresent", []))


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


def run_samples(root: Path, manifest: dict[str, Any], samples: list[dict[str, Any]], workspace_root: Path) -> None:
    reset_workspace(root, workspace_root)
    bash_path = find_bash()
    summary_by_sample: dict[str, dict[str, dict[str, Any]]] = {}
    failures: list[str] = []

    for sample in samples:
        sample_id = sample["id"]
        seed_path = resolve_repo_path(root, sample["seedProjectPath"], f"{sample_id}.seedProjectPath")
        summary_by_sample[sample_id] = {}

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

            if not summary_path.is_file():
                failures.append(
                    f"{sample_id}/{arm_id}: transcript analysis did not write summary\n"
                    f"{completed.stdout}{completed.stderr}"
                )
                continue

            summary = load_json(summary_path)
            summary_by_sample[sample_id][arm_id] = summary
            expected_pass = arm["expectedContractPass"]
            actual_pass = completed.returncode == 0
            if actual_pass != expected_pass:
                failures.append(
                    f"{sample_id}/{arm_id}: expected contract pass={expected_pass}, got {actual_pass}\n"
                    f"{completed.stdout}{completed.stderr}"
                )
            status = "PASS" if actual_pass else "WEAKER"
            print(f"  [{status}] {arm_id} score={replay_score(summary)} workspace={relative_path(root, workspace_path)}")

        for comparison in sample["comparisons"]:
            if (
                comparison["strongerArm"] not in summary_by_sample[sample_id]
                or comparison["weakerArm"] not in summary_by_sample[sample_id]
            ):
                failures.append(f"{sample_id}: comparison skipped because an arm summary is missing")
                continue
            stronger = summary_by_sample[sample_id][comparison["strongerArm"]]
            weaker = summary_by_sample[sample_id][comparison["weakerArm"]]
            stronger_score = replay_score(stronger)
            weaker_score = replay_score(weaker)
            comparison_pass = stronger.get("overallPass") is True and stronger_score > weaker_score
            if not comparison_pass:
                failures.append(
                    f"{sample_id}: {comparison['strongerArm']} score {stronger_score} did not beat "
                    f"{comparison['weakerArm']} score {weaker_score}"
                )
            print(
                f"  [COMPARE] {comparison['strongerArm']}={stronger_score} "
                f"{comparison['weakerArm']}={weaker_score}"
            )
        print("")

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
        resolved_workspace_root == allowed_root or allowed_root in resolved_workspace_root.parents,
        f"workspace root must be under .tmp: {workspace_root}",
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
    parser.add_argument("--sample", help="Replay sample id used with --prepare-live-run.")
    parser.add_argument("--arm", default="aegis-auto", help="Benchmark arm id used with --prepare-live-run.")
    args = parser.parse_args(argv)

    root = repo_root()
    manifest_path = resolve_repo_path(root, args.manifest, "manifest")
    manifest = load_json(manifest_path)
    _, samples = validate_manifest(root, manifest)

    if args.validate_only:
        print(f"Controlled replay manifest is valid: {relative_path(root, manifest_path)}")
        return 0

    workspace_root = resolve_repo_path(root, args.workspace_root, "workspace-root")
    if args.prepare_live_run:
        require(bool(args.sample), "--sample is required with --prepare-live-run")
        prepare_live_run(root, manifest, samples, args.sample, args.arm, workspace_root)
        return 0

    run_samples(root, manifest, samples, workspace_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
