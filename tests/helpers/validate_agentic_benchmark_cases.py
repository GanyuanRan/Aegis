#!/usr/bin/env python3
"""Validate the concrete Aegis agentic benchmark case portfolio."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from score_agentic_benchmark_outcome import validate_contract as validate_outcome_contract


AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
BENCHMARK_MATRIX_PATH = "tests/e2e/fixtures/agentic-benchmark-matrix.json"
EXPECTED_ARMS = ["baseline-no-aegis", "aegis-auto"]
EXPECTED_PARTITIONS = {
    "development": 10,
    "held-out-normal": 10,
    "held-out-boundary": 10,
}
EXPECTED_VARIANTS = {
    "development": "development",
    "held-out-normal": "normal",
    "held-out-boundary": "boundary",
}
EXPECTED_CASE_FIELDS = {
    "id",
    "scenarioClass",
    "partition",
    "variant",
    "promptPath",
    "seedProjectPath",
    "outcomeContractPath",
    "benchmarkMetrics",
    "liveEligible",
}
EXPECTED_TOP_LEVEL_FIELDS = {
    "version",
    "status",
    "benchmarkMatrix",
    "authorityBoundary",
    "partitions",
    "repetitions",
    "arms",
    "cases",
}
EXPECTED_CASES = {
    "ambiguous-feature-shaping": {
        "development": "ambiguous-feature-dev",
        "held-out-normal": "ambiguous-feature-api-option",
        "held-out-boundary": "ambiguous-feature-cross-module",
    },
    "shared-owner-bug-repair": {
        "development": "shared-owner-bug-repair",
        "held-out-normal": "shared-owner-normal",
        "held-out-boundary": "shared-owner-boundary",
    },
    "quick-bug-change-necessity": {
        "development": "change-necessity-before-edit",
        "held-out-normal": "quick-bug-normal",
        "held-out-boundary": "quick-bug-boundary",
    },
    "tiny-new-source-path-change-necessity": {
        "development": "tiny-source-dev",
        "held-out-normal": "tiny-source-normal",
        "held-out-boundary": "tiny-source-boundary",
    },
    "completion-claim-with-missing-evidence": {
        "development": "completion-evidence-boundary",
        "held-out-normal": "completion-normal",
        "held-out-boundary": "completion-boundary",
    },
    "fallback-retirement-cleanup": {
        "development": "fallback-retirement-dev",
        "held-out-normal": "fallback-retirement-normal",
        "held-out-boundary": "fallback-retirement-boundary",
    },
    "tiny-fast-path": {
        "development": "tiny-fast-dev",
        "held-out-normal": "tiny-fast-normal",
        "held-out-boundary": "tiny-fast-boundary",
    },
    "requested-white-box-trace-digest": {
        "development": "trace-digest-dev",
        "held-out-normal": "trace-digest-normal",
        "held-out-boundary": "trace-digest-boundary",
    },
    "negative-fast-path-no-trace-digest": {
        "development": "no-trace-dev",
        "held-out-normal": "no-trace-normal",
        "held-out-boundary": "no-trace-boundary",
    },
    "destructive-cleanup-hard-stop": {
        "development": "destructive-stop-dev",
        "held-out-normal": "destructive-stop-normal",
        "held-out-boundary": "destructive-stop-boundary",
    },
}
REUSED_DEVELOPMENT_PATHS = {
    "shared-owner-bug-repair": (
        "tests/e2e/replay-samples/shared-owner-bug-repair/prompt.txt",
        "tests/e2e/fixtures/replay-projects/shared-owner-bug-repair",
    ),
    "change-necessity-before-edit": (
        "tests/e2e/replay-samples/change-necessity-before-edit/prompt.txt",
        "tests/e2e/fixtures/replay-projects/change-necessity-before-edit",
    ),
    "completion-evidence-boundary": (
        "tests/e2e/replay-samples/completion-evidence-boundary/prompt.txt",
        "tests/e2e/fixtures/replay-projects/completion-evidence-boundary",
    ),
}
FORBIDDEN_PROMPT_PATTERNS = {
    "Aegis product name": r"\baegis\b",
    "benchmark identity": r"\bbenchmark\b",
    "baseline arm identity": r"baseline-no-aegis",
    "Aegis arm identity": r"aegis-auto",
    "scorer implementation": r"\bscor(?:e[sd]?|er|ing)\b",
    "expected outcome contract": r"expected[- ]outcome",
    "brainstorming route": r"\bbrainstorming\b",
    "systematic debugging route": r"systematic[- ]debugging",
    "verification route": r"verification[- ]before[- ]completion",
    "anti-entropy route": r"anti[- ]entropy[- ]governance",
    "first-principles route": r"first[- ]principles[- ]review",
    "long-task route": r"long[- ]task[- ]continuation",
    "execution-plan route": r"executing[- ]plans",
    "Aegis router": r"using[- ]aegis",
    "change-necessity artifact": r"change[- ]necessity",
    "spec-brief artifact": r"spec[- ]brief",
    "design-spec artifact": r"design[- ]spec",
    "gate-decision artifact": r"gate[- ]decision",
    "policy-snapshot artifact": r"policy[- ]snapshot",
}
FORBIDDEN_PROJECT_PATTERN = re.compile(
    r"\baegis\b|baseline-no-aegis|aegis-auto|expected[-_ ]outcome|"
    r"benchmarkMetrics|contractPass|scoreSource|systematic[- ]debugging|"
    r"verification[- ]before[- ]completion|anti[- ]entropy[- ]governance",
    flags=re.IGNORECASE,
)
PROJECT_FILE_SIZE_LIMIT = 65536


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read {label} {path}: {exc}") from exc
    require(isinstance(data, dict), f"{label} must contain a JSON object")
    return data


def resolve_repo_path(root: Path, value: Any, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a non-empty string")
    relative = Path(value)
    require(not relative.is_absolute(), f"{label} must be repo-relative: {value}")
    path = (root / relative).resolve()
    require(root == path or root in path.parents, f"{label} must stay inside the repo: {value}")
    return path


def validate_prompt_text(text: str, label: str, scenario_class: str | None) -> None:
    normalized_text = " ".join(text.split())
    for term_label, pattern in FORBIDDEN_PROMPT_PATTERNS.items():
        require(
            re.search(pattern, normalized_text, flags=re.IGNORECASE) is None,
            f"{label} discloses hidden route or scoring material: {term_label}",
        )
    if scenario_class != "requested-white-box-trace-digest":
        require(
            re.search(r"trace[- ]digest", normalized_text, flags=re.IGNORECASE) is None,
            f"{label} discloses hidden route or scoring material: trace digest",
        )
    else:
        require(
            re.search(r"trace[- ]digest", normalized_text, flags=re.IGNORECASE) is not None,
            f"{label} must explicitly request the trace digest being evaluated",
        )


def validate_seed_project(project_path: Path, case_id: str) -> None:
    for path in sorted(project_path.rglob("*")):
        relative_path = path.relative_to(project_path)
        if set(relative_path.parts) & {".pytest_cache", "__pycache__"}:
            continue
        relative = relative_path.as_posix()
        require(not path.is_symlink(), f"{case_id} seed project must not contain symlinks: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"{case_id} seed project contains unsupported file type: {relative}")
        require(path.stat().st_size <= PROJECT_FILE_SIZE_LIMIT, f"{case_id} seed project file exceeds size limit: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"{case_id} seed project files must be UTF-8 text: {relative}") from exc
        require(
            FORBIDDEN_PROJECT_PATTERN.search(" ".join(text.split())) is None,
            f"{case_id} seed project exposes hidden route or scoring material: {relative}",
        )


def matrix_scenarios(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    require(matrix.get("version") == 3, "benchmark matrix version must be 3")
    scenarios = matrix.get("scenarioClasses")
    require(isinstance(scenarios, list), "benchmark matrix scenarioClasses must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        require(isinstance(scenario, dict), "benchmark matrix scenarios must be objects")
        scenario_id = scenario.get("id")
        require(isinstance(scenario_id, str) and scenario_id, "benchmark matrix scenario ids must be strings")
        require(scenario_id not in by_id, f"duplicate benchmark matrix scenario id: {scenario_id}")
        by_id[scenario_id] = scenario
    require(set(by_id) == set(EXPECTED_CASES), "benchmark matrix scenario classes drifted from case portfolio")
    return by_id


def validate_matrix_contract(matrix: dict[str, Any]) -> None:
    portfolio = matrix.get("casePortfolio")
    require(isinstance(portfolio, dict), "benchmark matrix casePortfolio must be an object")
    require(portfolio.get("manifestPath") == "tests/e2e/fixtures/agentic-benchmark-cases.json", "casePortfolio manifest path drifted")
    require(portfolio.get("schemaVersion") == 1, "casePortfolio schema version must be 1")
    require(portfolio.get("caseCount") == 30, "casePortfolio case count must be 30")
    require(portfolio.get("scenarioClassCount") == 10, "casePortfolio scenario class count must be 10")
    require(portfolio.get("partitions") == EXPECTED_PARTITIONS, "casePortfolio partitions drifted")
    require(portfolio.get("arms") == EXPECTED_ARMS, "casePortfolio arms drifted")


def expected_paths(case_id: str) -> tuple[str, str, str]:
    case_root = f"tests/e2e/agentic-benchmark-cases/{case_id}"
    prompt_path, project_path = REUSED_DEVELOPMENT_PATHS.get(
        case_id,
        (f"{case_root}/prompt.txt", f"{case_root}/project"),
    )
    return prompt_path, project_path, f"{case_root}/expected-outcome.json"


def validate_case(
    case: dict[str, Any],
    scenarios: dict[str, dict[str, Any]],
    root: Path,
    schema_only: bool,
) -> None:
    case_id = case.get("id")
    require(isinstance(case_id, str) and case_id, "case id must be a non-empty string")
    require(set(case) == EXPECTED_CASE_FIELDS, f"{case_id} must contain exactly the case portfolio fields")

    scenario_class = case.get("scenarioClass")
    partition = case.get("partition")
    require(scenario_class in EXPECTED_CASES, f"{case_id} uses unknown scenario class: {scenario_class}")
    require(partition in EXPECTED_PARTITIONS, f"{case_id} uses unknown partition: {partition}")
    require(
        EXPECTED_CASES[scenario_class][partition] == case_id,
        f"{case_id} does not match the fixed scenario/partition case id",
    )
    require(case.get("variant") == EXPECTED_VARIANTS[partition], f"{case_id} variant does not match its partition")
    require(case.get("liveEligible") is True, f"{case_id} must be live eligible")

    metrics = case.get("benchmarkMetrics")
    require(isinstance(metrics, list) and metrics, f"{case_id}.benchmarkMetrics must be a non-empty list")
    require(all(isinstance(metric, str) and metric for metric in metrics), f"{case_id}.benchmarkMetrics must contain strings")
    require(len(metrics) == len(set(metrics)), f"{case_id}.benchmarkMetrics must not contain duplicates")
    required_metrics = scenarios[scenario_class].get("requiredMetrics")
    require(
        isinstance(required_metrics, list) and set(metrics) == set(required_metrics),
        f"{case_id} benchmark metrics must exactly match its scenario required metrics",
    )

    prompt_path = resolve_repo_path(root, case.get("promptPath"), f"{case_id}.promptPath")
    project_path = resolve_repo_path(root, case.get("seedProjectPath"), f"{case_id}.seedProjectPath")
    outcome_path = resolve_repo_path(root, case.get("outcomeContractPath"), f"{case_id}.outcomeContractPath")
    require(project_path != outcome_path and project_path not in outcome_path.parents, f"{case_id} outcome contract must stay outside the seed project")

    expected_prompt, expected_project, expected_outcome = expected_paths(case_id)
    require(case.get("promptPath") == expected_prompt, f"{case_id} prompt path drifted")
    require(case.get("seedProjectPath") == expected_project, f"{case_id} seed project path drifted")
    require(case.get("outcomeContractPath") == expected_outcome, f"{case_id} outcome contract path drifted")

    if schema_only:
        return
    require(prompt_path.is_file(), f"{case_id} prompt file is missing: {case['promptPath']}")
    require(project_path.is_dir(), f"{case_id} seed project directory is missing: {case['seedProjectPath']}")
    require(outcome_path.is_file(), f"{case_id} outcome contract is missing: {case['outcomeContractPath']}")
    validate_prompt_text(prompt_path.read_text(encoding="utf-8"), f"{case_id} prompt", scenario_class)
    validate_seed_project(project_path, case_id)
    validate_outcome_contract(load_json(outcome_path, f"{case_id} outcome contract"), case_id)


def validate_manifest(manifest_path: Path, schema_only: bool) -> None:
    root = repo_root()
    manifest = load_json(manifest_path, "case manifest")
    require(set(manifest) == EXPECTED_TOP_LEVEL_FIELDS, "case manifest must contain exactly the portfolio fields")
    require(manifest.get("version") == 1, "case manifest version must be 1")
    require(manifest.get("status") == "draft", "case manifest status must be draft until fixture completion")
    require(manifest.get("benchmarkMatrix") == BENCHMARK_MATRIX_PATH, "case manifest benchmark matrix path drifted")
    require(manifest.get("authorityBoundary") == AUTHORITY_BOUNDARY, "case manifest authority boundary drifted")
    require(manifest.get("partitions") == EXPECTED_PARTITIONS, "case manifest partitions drifted")
    require(manifest.get("repetitions") == 3, "case manifest repetitions must be 3")
    require(manifest.get("arms") == EXPECTED_ARMS, "case manifest arms must be exactly baseline-no-aegis and aegis-auto")

    matrix_path = resolve_repo_path(root, manifest["benchmarkMatrix"], "benchmarkMatrix")
    require(matrix_path.is_file(), f"benchmark matrix is missing: {manifest['benchmarkMatrix']}")
    matrix = load_json(matrix_path, "benchmark matrix")
    validate_matrix_contract(matrix)
    scenarios = matrix_scenarios(matrix)

    cases = manifest.get("cases")
    require(isinstance(cases, list), "case manifest cases must be a list")
    require(len(cases) == 30, "case manifest must contain exactly 30 cases")
    require(all(isinstance(case, dict) for case in cases), "case manifest entries must be objects")

    ids = [case.get("id") for case in cases]
    require(all(isinstance(case_id, str) and case_id for case_id in ids), "case ids must be non-empty strings")
    require(len(ids) == len(set(ids)), "case manifest ids must be unique")

    for case in cases:
        validate_case(case, scenarios, root, schema_only)

    require(set(ids) == {case_id for group in EXPECTED_CASES.values() for case_id in group.values()}, "case manifest fixed case ids drifted")
    partition_counts = Counter(case["partition"] for case in cases)
    require(dict(partition_counts) == EXPECTED_PARTITIONS, "case manifest must contain exactly ten cases per partition")
    scenario_counts = Counter(case["scenarioClass"] for case in cases)
    require(set(scenario_counts) == set(EXPECTED_CASES) and set(scenario_counts.values()) == {3}, "case manifest must contain exactly three cases per scenario class")

    for field in ("promptPath", "seedProjectPath", "outcomeContractPath"):
        values = [case[field] for case in cases]
        require(len(values) == len(set(values)), f"case manifest {field} values must be unique")

    mode = "schema-only" if schema_only else "full"
    print(f"Agentic benchmark case manifest valid ({mode}): 30 cases, 10 scenarios, 10/10/10 partitions")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path)
    parser.add_argument("--schema-only", action="store_true")
    parser.add_argument("--check-prompt-text", type=Path)
    parser.add_argument("--scenario-class", choices=sorted(EXPECTED_CASES))
    args = parser.parse_args()
    require(bool(args.manifest) ^ bool(args.check_prompt_text), "provide either a manifest or --check-prompt-text")
    require(not (args.schema_only and args.check_prompt_text), "--schema-only cannot be combined with --check-prompt-text")
    require(not (args.manifest and args.scenario_class), "--scenario-class is only valid with --check-prompt-text")
    return args


def main() -> None:
    args = parse_args()
    if args.check_prompt_text:
        try:
            prompt_text = args.check_prompt_text.read_text(encoding="utf-8")
        except OSError as exc:
            raise SystemExit(f"cannot read prompt text {args.check_prompt_text}: {exc}") from exc
        validate_prompt_text(prompt_text, str(args.check_prompt_text), args.scenario_class)
        print(f"Agentic benchmark prompt text valid: {args.check_prompt_text}")
        return
    validate_manifest(args.manifest, args.schema_only)


if __name__ == "__main__":
    main()
