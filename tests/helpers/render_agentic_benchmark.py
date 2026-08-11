#!/usr/bin/env python3
"""Validate, sanitize, and deterministically project agentic benchmark reports."""

from __future__ import annotations

import argparse
import functools
import hashlib
import html
import json
import math
import random
import re
import tempfile
import xml.etree.ElementTree as ElementTree
from collections import defaultdict
from pathlib import Path
from typing import Any

from agentic_benchmark_atomic import atomic_text
from agentic_benchmark_scheduler import INVALID_REASONS


PRIVATE_REPORT_TYPE = "agentic-benchmark-private-report"
PUBLIC_REPORT_TYPE = "agentic-benchmark-sanitized-report"
AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
ARMS = ("baseline-no-aegis", "aegis-auto")
SCENARIOS = (
    "ambiguous-feature-shaping",
    "completion-claim-with-missing-evidence",
    "destructive-cleanup-hard-stop",
    "fallback-retirement-cleanup",
    "negative-fast-path-no-trace-digest",
    "quick-bug-change-necessity",
    "requested-white-box-trace-digest",
    "shared-owner-bug-repair",
    "tiny-fast-path",
    "tiny-new-source-path-change-necessity",
)
UNSUPPORTED_CLAIMS = (
    "runtime-authority",
    "automatic-candidate-promotion",
    "universal-agent-quality",
    "causal-proof-outside-this-benchmark",
    "statistical-independence-of-repetitions",
)
PROFILE_CONTRACTS = {
    "standard-held-out": {
        "datasetPartitions": ["held-out-normal", "held-out-boundary"],
        "caseCount": 20,
        "arms": list(ARMS),
        "repetitions": 1,
        "targetRuns": 40,
        "maxAttempts": 44,
        "publicationEligible": True,
        "publicationAuthority": "advisory-only",
        "supportedEvidence": ["held-out-evidence"],
        "unsupportedEvidence": ["repeated-run-evidence"],
        "limitations": [
            "repeated-run-evidence-unsupported",
            "not-independent-universal-causal-promotion-runtime-or-completion-authority",
        ],
    },
    "extended-held-out": {
        "datasetPartitions": ["held-out-normal", "held-out-boundary"],
        "caseCount": 20,
        "arms": list(ARMS),
        "repetitions": 3,
        "targetRuns": 120,
        "maxAttempts": 132,
        "publicationEligible": True,
        "publicationAuthority": "advisory-only",
        "supportedEvidence": ["held-out-evidence", "repeated-run-evidence"],
        "unsupportedEvidence": [],
        "limitations": [
            "bounded-advisory-repeated-run-evidence",
            "repetitions-case-clustered-not-statistically-independent",
            "not-universal-causal-promotion-runtime-or-completion-authority",
        ],
    },
}
PRIVATE_KEYS = re.compile(
    r"(?:auth|config)(?:file|path)?$|session(?:id)?$|rollout(?:id)?$|raw(?:reasoning|hostlog|log)$|prompt(?:text|content)?$|credentials?$|secret$|password$|(?:access|refresh|id|api)?token$",
    re.IGNORECASE,
)
ABSOLUTE_PATH = re.compile(r"(?:^|[\s\"'=(])(?:/(?!/)[^/\s\"']+(?:/[^/\s\"']+)*|[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/][^\s]+)")
PRIVATE_IDENTIFIER = re.compile(r"(?i)\b(?:session|rollout)[_-]?(?:id[_-]?)?[a-z0-9-]{6,}\b")
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)(?:access_token|refresh_token|id_token|api_key)\s*[:=]\s*[\"']?[^\"'\s]{8,}"),
)
GOLDEN_HASHES = {
    "standard-held-out-positive": "d5c8213bf7f9ac9f62db3afc048cc83157bb602784f971e32a3189e0f72b629b",
    "standard-held-out-neutral": "8347ba9d10e894ed7c516326c19aab894d1c81aa6ea532f279e286fc79358943",
    "standard-held-out-negative": "849a8be55c1ab42b1f0ba1d08d846d04e96e1c6ef438b7dc55f04077d525c726",
    "extended-held-out-positive": "ad3383608b63a733d46c2749d2992cf2a371bbdeacd0f61d38b9273f8a683468",
    "extended-held-out-neutral": "12c60881897140511692bd0963ab8c4541928b6aa1aafb2845bd2127ef42759c",
    "extended-held-out-negative": "7133e2df38bfac28411d9d547f5522a19afc5bab36ddc254c881f98431544d18",
}
OUTPUT_PRIVATE_PATTERN = re.compile(
    r"/(?:home|Users|tmp|workspace)/|(?:^|[\s\"'=(])(?:[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/])|session[_-]?id|rollout[_-]?id|sk-[A-Za-z0-9_-]{16,}",
    re.IGNORECASE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_path(value: Path, label: str, *, must_exist: bool = False) -> Path:
    root = repo_root()
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve()
    require(root == resolved or root in resolved.parents, f"{label} must stay inside the repo: {value}")
    if must_exist:
        require(resolved.is_file(), f"{label} must reference an existing file: {value}")
    return resolved


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read {label} {path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} must contain a JSON object")
    return value


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"cannot serialize canonical JSON: {exc}") from exc


def walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    values = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            require(isinstance(key, str), f"report object key must be a string at {path}")
            values.extend(walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            values.extend(walk(child, f"{path}[{index}]"))
    return values


def reject_private_material(report: dict[str, Any]) -> None:
    for path, value in walk(report):
        key = path.rsplit(".", 1)[-1]
        require(PRIVATE_KEYS.fullmatch(key) is None, f"report contains private field: {path}")
        if not isinstance(value, str):
            continue
        require(ABSOLUTE_PATH.search(value) is None, f"report contains an absolute machine path: {path}")
        require(PRIVATE_IDENTIFIER.search(value) is None, f"report contains a session or rollout identifier: {path}")
        require(all(pattern.search(value) is None for pattern in SECRET_PATTERNS), f"report contains credential-like material: {path}")


def numeric(value: Any, label: str, *, minimum: float = 0.0, maximum: float = 100.0) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be numeric")
    result = float(value)
    require(minimum <= result <= maximum, f"{label} must be between {minimum} and {maximum}")
    return result


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    passes = sum(item["contractPass"] is True for item in records)
    unsafe = sum(item["unsafeOutcome"] is True for item in records)
    count = len(records)
    return {
        "validRuns": count,
        "passes": passes,
        "fails": count - passes,
        "passRate": round(passes / count * 100, 2),
        "unsafeOutcomes": unsafe,
        "unsafeOutcomeRate": round(unsafe / count * 100, 2),
    }


def cluster_interval(records: list[dict[str, Any]], seed: str, iterations: int = 4000) -> dict[str, Any]:
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_case[record["caseId"]].append(record)
    case_ids = sorted(by_case)
    generator = random.Random(seed)
    deltas: list[float] = []
    for _ in range(iterations):
        sampled = [generator.choice(case_ids) for _ in case_ids]
        by_arm = {arm: [] for arm in ARMS}
        for case_id in sampled:
            for record in by_case[case_id]:
                by_arm[record["arm"]].append(record)
        rates = {
            arm: sum(item["contractPass"] is True for item in by_arm[arm]) / len(by_arm[arm])
            for arm in ARMS
        }
        deltas.append((rates["aegis-auto"] - rates["baseline-no-aegis"]) * 100)
    return {
        "method": "case-cluster-bootstrap",
        "iterations": iterations,
        "seed": seed,
        "lower": round(percentile(deltas, 0.025), 2),
        "upper": round(percentile(deltas, 0.975), 2),
    }


def validate_matrix_profile_contracts_value(matrix: dict[str, Any]) -> None:
    require(matrix.get("version") == 6, "renderer requires benchmark matrix version 6")
    run_profiles = matrix.get("runProfiles")
    require(isinstance(run_profiles, list), "benchmark matrix runProfiles must be a list")
    profiles = {
        item.get("id"): item
        for item in run_profiles
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    field_map = {
        "datasetPartitions": "datasetPartitions",
        "caseCount": "caseCount",
        "arms": "arms",
        "repetitions": "repetitionsPerCase",
        "targetRuns": "validRunTarget",
        "maxAttempts": "paidAttemptCeiling",
        "publicationEligible": "publicationEligible",
        "publicationAuthority": "publicationAuthority",
        "supportedEvidence": "supportedEvidence",
        "unsupportedEvidence": "unsupportedEvidence",
    }
    for profile_id, contract in PROFILE_CONTRACTS.items():
        require(sum(isinstance(item, dict) and item.get("id") == profile_id for item in run_profiles) == 1, f"renderer profile must appear exactly once in matrix v5: {profile_id}")
        require(profile_id in profiles, f"renderer profile is missing from matrix v5: {profile_id}")
        matrix_profile = profiles[profile_id]
        for contract_field, matrix_field in field_map.items():
            actual = matrix_profile.get(matrix_field)
            expected = contract[contract_field]
            if type(expected) is int:
                require(type(actual) is int, f"matrix {profile_id}.{matrix_field} must be an integer")
            elif type(expected) is bool:
                require(type(actual) is bool, f"matrix {profile_id}.{matrix_field} must be a boolean")
            elif isinstance(expected, list):
                require(isinstance(actual, list) and all(isinstance(item, str) for item in actual), f"matrix {profile_id}.{matrix_field} must be a string list")
            elif isinstance(expected, str):
                require(isinstance(actual, str), f"matrix {profile_id}.{matrix_field} must be a string")
            require(actual == expected, f"renderer profile contract drifted from matrix v5: {profile_id}.{matrix_field}")


@functools.lru_cache(maxsize=1)
def validate_matrix_profile_contracts() -> None:
    matrix = load_json(repo_root() / "tests/e2e/fixtures/agentic-benchmark-matrix.json", "benchmark matrix")
    validate_matrix_profile_contracts_value(matrix)


def profile_contract(report: dict[str, Any]) -> dict[str, Any]:
    validate_matrix_profile_contracts()
    profile_id = report.get("profileId")
    require(isinstance(profile_id, str) and profile_id in PROFILE_CONTRACTS, "only standard-held-out or extended-held-out reports can be projected")
    return PROFILE_CONTRACTS[profile_id]


def derived_metrics(report: dict[str, Any]) -> dict[str, Any]:
    profile = profile_contract(report)
    records = report.get("caseResults")
    expected_runs = profile["targetRuns"]
    expected_repetitions = profile["repetitions"]
    require(isinstance(records, list) and len(records) == expected_runs, f"caseResults must contain exactly {expected_runs} held-out results")
    normalized: list[dict[str, Any]] = []
    identities: set[tuple[str, int, str]] = set()
    case_scenarios: dict[str, str] = {}
    for index, record in enumerate(records):
        label = f"caseResults[{index}]"
        require(isinstance(record, dict), f"{label} must be an object")
        require(set(record) == {"caseId", "scenarioClass", "repetition", "arm", "contractPass", "unsafeOutcome"}, f"{label} fields drifted")
        case_id = record["caseId"]
        scenario = record["scenarioClass"]
        repetition = record["repetition"]
        arm = record["arm"]
        require(isinstance(case_id, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", case_id) is not None, f"{label}.caseId is invalid")
        require(scenario in SCENARIOS, f"{label}.scenarioClass is invalid")
        require(isinstance(repetition, int) and not isinstance(repetition, bool) and 1 <= repetition <= expected_repetitions, f"{label}.repetition is invalid")
        require(arm in ARMS, f"{label}.arm is invalid")
        require(type(record["contractPass"]) is bool, f"{label}.contractPass must be boolean")
        require(type(record["unsafeOutcome"]) is bool, f"{label}.unsafeOutcome must be boolean")
        identity = (case_id, repetition, arm)
        require(identity not in identities, f"duplicate case result: {identity}")
        identities.add(identity)
        require(case_id not in case_scenarios or case_scenarios[case_id] == scenario, f"case scenario drifted: {case_id}")
        case_scenarios[case_id] = scenario
        normalized.append(dict(record))
    require(len(case_scenarios) == 20, "caseResults must contain exactly 20 held-out cases")
    require(set(case_scenarios.values()) == set(SCENARIOS), "caseResults must cover all ten scenario classes")
    for scenario in SCENARIOS:
        require(sum(value == scenario for value in case_scenarios.values()) == 2, f"scenario must contain exactly two held-out cases: {scenario}")
    expected_identities = {
        (case_id, repetition, arm)
        for case_id in case_scenarios
        for repetition in range(1, expected_repetitions + 1)
        for arm in ARMS
    }
    require(identities == expected_identities, "caseResults do not match the frozen profile repetitions and arms")

    arms = {arm: summarize([item for item in normalized if item["arm"] == arm]) for arm in ARMS}
    delta = round(
        (
            arms["aegis-auto"]["passes"] / arms["aegis-auto"]["validRuns"]
            - arms["baseline-no-aegis"]["passes"] / arms["baseline-no-aegis"]["validRuns"]
        )
        * 100,
        2,
    )
    per_scenario: dict[str, Any] = {}
    for scenario in SCENARIOS:
        values = [item for item in normalized if item["scenarioClass"] == scenario]
        summaries = {arm: summarize([item for item in values if item["arm"] == arm]) for arm in ARMS}
        per_scenario[scenario] = {
            "arms": summaries,
            "deltaPercentagePoints": round(
                (
                    summaries["aegis-auto"]["passes"] / summaries["aegis-auto"]["validRuns"]
                    - summaries["baseline-no-aegis"]["passes"] / summaries["baseline-no-aegis"]["validRuns"]
                )
                * 100,
                2,
            ),
        }
    interval = report.get("overall", {}).get("deltaInterval95")
    require(isinstance(interval, dict), "overall.deltaInterval95 must be an object")
    seed = interval.get("seed")
    require(isinstance(seed, str) and re.fullmatch(r"[0-9a-f]{64}", seed) is not None, "bootstrap seed must be a SHA-256 value")
    expected_interval = cluster_interval(normalized, seed)
    return {
        "records": sorted(normalized, key=lambda item: (item["caseId"], item["repetition"], item["arm"])),
        "overall": {"arms": arms, "deltaPercentagePoints": delta, "deltaInterval95": expected_interval},
        "perScenarioClass": per_scenario,
    }


def validate_common(report: dict[str, Any], expected_type: str) -> dict[str, Any]:
    require(report.get("version") == 1, "report version must be 1")
    require(report.get("reportType") == expected_type, f"report type must be {expected_type}")
    require(report.get("authorityBoundary") == AUTHORITY_BOUNDARY, "report authority boundary drifted")
    reject_private_material(report)
    require(isinstance(report.get("batchId"), str) and re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,79}", report["batchId"]) is not None, "batchId is invalid")
    require(isinstance(report.get("batchDigest"), str) and re.fullmatch(r"[0-9a-f]{64}", report["batchDigest"]) is not None, "batchDigest must be a SHA-256 value")
    require(report.get("partition") == "held-out", "only a complete held-out report can be projected")
    profile = profile_contract(report)

    versions = report.get("versions")
    require(isinstance(versions, dict) and set(versions) == {"aegis", "codex", "bwrap"}, "versions must record Aegis, Codex and bwrap")
    require(isinstance(versions["aegis"], str) and re.fullmatch(r"v?[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?", versions["aegis"]) is not None, "Aegis version is invalid")
    require(isinstance(versions["codex"], str) and re.fullmatch(r"codex-cli [0-9A-Za-z.+-]+", versions["codex"]) is not None, "Codex version is invalid")
    require(isinstance(versions["bwrap"], str) and re.fullmatch(r"bubblewrap [0-9A-Za-z.+-]+", versions["bwrap"]) is not None, "bubblewrap version is invalid")
    model = report.get("model")
    require(isinstance(model, dict) and set(model) == {"requested", "reasoningEffort", "observed", "observedStatus"}, "model identity fields drifted")
    require(isinstance(model.get("requested"), str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}", model["requested"]) is not None, "requested model identifier is invalid")
    require(isinstance(model.get("reasoningEffort"), str) and re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", model["reasoningEffort"]) is not None, "reasoning effort is invalid")
    observed_status = model.get("observedStatus")
    require(observed_status in {"recorded", "unavailable-from-host-events"}, "observed model identity status is invalid")
    observed = model.get("observed")
    require(isinstance(observed, list) and all(isinstance(item, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}", item) is not None for item in observed), "observed model identifiers are invalid")
    require((observed_status == "recorded") is bool(observed), "observed model identity and status disagree")

    design = report.get("design")
    require(isinstance(design, dict), "design must be an object")
    design_fields = {"portfolioCaseCount", "caseCount", "arms", "repetitions", "targetRuns", "maxAttempts", "clusterUnit"}
    require(set(design) == design_fields, "design fields drifted")
    for field in ("portfolioCaseCount", "caseCount", "repetitions", "targetRuns", "maxAttempts"):
        require(type(design[field]) is int, f"design.{field} must be an integer")
    require(isinstance(design["arms"], list), "design.arms must be a list")
    require(isinstance(design["clusterUnit"], str), "design.clusterUnit must be a string")
    expected_design = {
        "portfolioCaseCount": 30,
        "caseCount": profile["caseCount"],
        "arms": profile["arms"],
        "repetitions": profile["repetitions"],
        "targetRuns": profile["targetRuns"],
        "maxAttempts": profile["maxAttempts"],
        "clusterUnit": "case",
    }
    require(design == expected_design, "design must preserve the frozen profile contract")
    attempts = report.get("attempts")
    require(isinstance(attempts, dict), "attempts must be an object")
    require(set(attempts) == {"total", "valid", "passes", "fails", "invalid", "invalidReasons", "remaining"}, "attempt fields drifted")
    for field in ("total", "valid", "passes", "fails", "invalid", "remaining"):
        require(type(attempts.get(field)) is int and attempts[field] >= 0, f"attempts.{field} must be a non-negative integer")
    require(profile["targetRuns"] <= attempts["total"] <= profile["maxAttempts"], "attempt total must stay within the frozen ceiling")
    require(attempts["valid"] == profile["targetRuns"] and attempts["remaining"] == 0, "report must contain every valid target")
    require(attempts["passes"] + attempts["fails"] == profile["targetRuns"], "pass/fail counts must sum to the profile target")
    require(attempts["total"] == attempts["valid"] + attempts["invalid"], "attempt total must include every invalid attempt")
    invalid_reasons = attempts.get("invalidReasons")
    require(isinstance(invalid_reasons, dict), "attempts.invalidReasons must be an object")
    require(set(invalid_reasons).issubset(INVALID_REASONS), "attempts.invalidReasons contains an unsupported reason")
    require(all(type(value) is int and value > 0 for value in invalid_reasons.values()), "invalid reason counts must be positive integers")
    require(sum(invalid_reasons.values()) == attempts["invalid"], "invalid reason counts must match attempts.invalid")
    require(report.get("completeness") == "complete", "partial benchmark reports cannot be projected")
    require(tuple(report.get("unsupportedClaims", ())) == UNSUPPORTED_CLAIMS, "unsupported claim boundary drifted")

    derived = derived_metrics(report)
    require(report.get("overall") == derived["overall"], "overall values must be derived from caseResults")
    require(report.get("perScenarioClass") == derived["perScenarioClass"], "scenario values must be derived from caseResults")
    require(attempts["passes"] == sum(item["contractPass"] for item in derived["records"]), "attempt pass count drifted from caseResults")

    review = report.get("review")
    require(isinstance(review, dict) and set(review) == {"status", "flags"} and review.get("status") in {"clear", "unknown"} and isinstance(review.get("flags"), list), "review status and flags must be explicit")
    for index, flag in enumerate(review["flags"]):
        require(isinstance(flag, dict) and isinstance(flag.get("id"), str) and flag.get("status") in {"resolved", "unresolved"}, f"review.flags[{index}] is invalid")
        require(flag["id"] in {"mixed-within-case-results", "non-discriminating-arm-outcomes", "scorer-unknown"}, f"review.flags[{index}].id is unsupported")
        if flag["id"] == "scorer-unknown":
            count_field = "count"
        else:
            count_field = "subjects" if expected_type == PRIVATE_REPORT_TYPE else "subjectCount"
        require(set(flag) == {"id", "status", count_field}, f"review.flags[{index}] fields drifted")
        if count_field == "subjects":
            require(isinstance(flag[count_field], list) and flag[count_field] and all(isinstance(item, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}(?::(?:baseline-no-aegis|aegis-auto))?", item) is not None for item in flag[count_field]), f"review.flags[{index}].subjects is invalid")
        else:
            require(type(flag[count_field]) is int and flag[count_field] > 0, f"review.flags[{index}].{count_field} must be a positive integer")
    unresolved = any(flag["status"] == "unresolved" for flag in review["flags"])
    require((review["status"] == "unknown") is unresolved, "review status must reflect unresolved flags")
    require(review["status"] == "clear" and not unresolved, "public projection requires a clear review with no unresolved flags")
    resource = report.get("resourceUse")
    require(isinstance(resource, dict) and set(resource) == {"tokens", "costUsd", "costStatus"}, "resourceUse fields drifted")
    require(isinstance(resource["tokens"], dict) and all(re.fullmatch(r"[a-z][a-z0-9_]{0,39}", key) is not None and type(value) is int and value >= 0 for key, value in resource["tokens"].items()), "resource token counts must use safe names and non-negative integers")
    cost = resource["costUsd"]
    require(cost is None or (type(cost) in {int, float} and math.isfinite(float(cost)) and cost >= 0), "resource cost must be null or a finite non-negative number")
    require(resource["costStatus"] in {"unavailable-from-host-events", "reported-by-host"}, "resource cost status is invalid")
    publication = report.get("publication")
    require(isinstance(publication, dict) and set(publication) == {"authorized", "eligible", "reason"} and type(publication.get("authorized")) is bool and type(publication.get("eligible")) is bool and isinstance(publication.get("reason"), str), "publication boundary must be explicit")
    require(publication["reason"] in {"separate-publication-authorization-required", "publication-approved", "synthetic-test-only"}, "publication reason is invalid")
    require(not publication["eligible"] or (publication["authorized"] and review["status"] == "clear"), "eligible publication requires authorization and clear review")
    return derived


def sanitize_private(report: dict[str, Any]) -> dict[str, Any]:
    expected_keys = {
        "version", "reportType", "authorityBoundary", "batchId", "batchDigest", "profileId", "partition",
        "versions", "model", "design", "attempts", "overall", "perScenarioClass", "caseResults",
        "resourceUse", "review", "completeness", "publication", "unsupportedClaims",
    }
    require(set(report) == expected_keys, "private report fields drifted")
    derived = validate_common(report, PRIVATE_REPORT_TYPE)
    flags = []
    for value in report["review"]["flags"]:
        require(isinstance(value, dict) and isinstance(value.get("id"), str) and value.get("status") in {"resolved", "unresolved"}, "review flag is invalid")
        flag = {"id": value["id"], "status": value["status"]}
        if isinstance(value.get("count"), int):
            flag["count"] = value["count"]
        if isinstance(value.get("subjects"), list):
            flag["subjectCount"] = len(value["subjects"])
        flags.append(flag)
    review_limitations = []
    if flags and all(flag["status"] == "resolved" for flag in flags):
        review_limitations = [
            "deterministic-response-contracts-may-count-semantic-paraphrases-as-failures",
            "arm-hidden-technical-review-not-independent-human-review",
        ]
    public = {
        "version": 1,
        "reportType": PUBLIC_REPORT_TYPE,
        "authorityBoundary": report["authorityBoundary"],
        "batchId": report["batchId"],
        "batchDigest": report["batchDigest"],
        "profileId": report["profileId"],
        "partition": report["partition"],
        "versions": report["versions"],
        "model": report["model"],
        "design": report["design"],
        "attempts": report["attempts"],
        "overall": derived["overall"],
        "perScenarioClass": derived["perScenarioClass"],
        "caseResults": derived["records"],
        "resourceUse": report["resourceUse"],
        "review": {"status": report["review"]["status"], "flags": flags},
        "completeness": report["completeness"],
        "publication": report["publication"],
        "limitations": [
            *profile_contract(report)["limitations"],
            *review_limitations,
            *(["observed-model-identity-unavailable-from-host-events"] if report["model"]["observedStatus"] == "unavailable-from-host-events" else []),
        ],
        "unsupportedClaims": list(UNSUPPORTED_CLAIMS),
    }
    validate_common(public, PUBLIC_REPORT_TYPE)
    return public


def validate_public(report: dict[str, Any]) -> dict[str, Any]:
    derived = validate_common(report, PUBLIC_REPORT_TYPE)
    expected_keys = {
        "version", "reportType", "authorityBoundary", "batchId", "batchDigest", "profileId", "partition",
        "versions", "model", "design", "attempts", "overall", "perScenarioClass", "caseResults",
        "resourceUse", "review", "completeness", "publication", "limitations", "unsupportedClaims",
    }
    require(set(report) == expected_keys, "sanitized report fields drifted")
    review_flags = report["review"]["flags"]
    review_limitations = []
    if review_flags and all(flag["status"] == "resolved" for flag in review_flags):
        review_limitations = [
            "deterministic-response-contracts-may-count-semantic-paraphrases-as-failures",
            "arm-hidden-technical-review-not-independent-human-review",
        ]
    expected_limitations = [
        *profile_contract(report)["limitations"],
        *review_limitations,
        *(["observed-model-identity-unavailable-from-host-events"] if report["model"]["observedStatus"] == "unavailable-from-host-events" else []),
    ]
    require(report["limitations"] == expected_limitations, "profile limitations drifted")
    return derived


def percent(value: float) -> str:
    return f"{value:.2f}%"


def delta(value: float) -> str:
    return f"{value:+.2f} pp"


def limitation_texts(report: dict[str, Any], language: str) -> list[str]:
    messages = {
        "en": {
            "repeated-run-evidence-unsupported": "Repeated-run evidence is unsupported: this profile has one observation per case.",
            "bounded-advisory-repeated-run-evidence": "Repeated-run evidence is bounded and advisory only.",
            "repetitions-case-clustered-not-statistically-independent": "Repetitions are clustered by case and are not statistically independent.",
            "not-independent-universal-causal-promotion-runtime-or-completion-authority": "This does not establish statistical independence, universal quality, causal proof, candidate promotion, runtime authority, or completion authority.",
            "not-universal-causal-promotion-runtime-or-completion-authority": "This does not establish universal quality, causal proof, candidate promotion, runtime authority, or completion authority.",
            "deterministic-response-contracts-may-count-semantic-paraphrases-as-failures": "Deterministic response contracts are conservative and may count semantically acceptable paraphrases as failures.",
            "arm-hidden-technical-review-not-independent-human-review": "Resolved flags received arm-hidden technical review, not independent human review.",
            "observed-model-identity-unavailable-from-host-events": "The host did not emit observed model identity; the requested model and reasoning effort were frozen and preflight-validated.",
        },
        "zh": {
            "repeated-run-evidence-unsupported": "不支持重复运行证据：此配置中每个案例只有一次观测。",
            "bounded-advisory-repeated-run-evidence": "重复运行证据仅为有界、建议性证据。",
            "repetitions-case-clustered-not-statistically-independent": "重复运行按案例聚簇，不具备统计独立性。",
            "not-independent-universal-causal-promotion-runtime-or-completion-authority": "这不构成独立性、普遍质量、因果证明、候选晋升、运行时权威或完成权威。",
            "not-universal-causal-promotion-runtime-or-completion-authority": "这不构成普遍质量、因果证明、候选晋升、运行时权威或完成权威。",
            "deterministic-response-contracts-may-count-semantic-paraphrases-as-failures": "确定性响应合同较为保守，语义可接受的改写仍可能被计为失败。",
            "arm-hidden-technical-review-not-independent-human-review": "已解决的复核项经过 arm-hidden 技术复核，但并非独立人工评审。",
            "observed-model-identity-unavailable-from-host-events": "宿主事件未返回实际模型身份；报告仅记录已冻结并通过预检的请求模型与推理档位。",
        },
    }
    return [messages[language][item] for item in report["limitations"]]


def markdown(report: dict[str, Any], language: str) -> str:
    derived = validate_public(report)
    overall = derived["overall"]
    target_runs = report["design"]["targetRuns"]
    if language == "en":
        title = "Agentic benchmark result"
        note = "Advisory held-out evidence; not runtime or completion authority."
        metric, baseline, aegis, change = "Metric", "Without Aegis", "With Aegis", "Difference"
        contract, unsafe = "Contract pass rate", "Unsafe outcome rate (lower is better)"
        scenario_title = "Scenario class"
        profile_line = f"Profile: `{report['profileId']}` · `{report['model']['requested']}` / `{report['model']['reasoningEffort']}` · n={target_runs} runs / 20 cases."
        limitations_title = "Limitations:"
    else:
        title = "Agentic Benchmark 结果"
        note = "仅作为 held-out 建议性证据，不构成运行时或完成权威。"
        metric, baseline, aegis, change = "指标", "不使用 Aegis", "使用 Aegis", "差值"
        contract, unsafe = "合同通过率", "不安全结果率（越低越好）"
        scenario_title = "场景类别"
        profile_line = f"配置：`{report['profileId']}` · `{report['model']['requested']}` / `{report['model']['reasoningEffort']}` · n={target_runs} 次运行 / 20 个案例。"
        limitations_title = "限制："
    rows = [
        f"### {title}",
        "",
        note,
        "",
        profile_line,
        "",
        limitations_title,
        "",
        *(f"- {item}" for item in limitation_texts(report, language)),
        "",
        f"| {metric} | {baseline} | {aegis} | {change} |",
        "|---|---:|---:|---:|",
        f"| {contract} | {percent(overall['arms']['baseline-no-aegis']['passRate'])} | {percent(overall['arms']['aegis-auto']['passRate'])} | {delta(overall['deltaPercentagePoints'])} |",
        f"| {unsafe} | {percent(overall['arms']['baseline-no-aegis']['unsafeOutcomeRate'])} | {percent(overall['arms']['aegis-auto']['unsafeOutcomeRate'])} | {delta(overall['arms']['aegis-auto']['unsafeOutcomeRate'] - overall['arms']['baseline-no-aegis']['unsafeOutcomeRate'])} |",
        "",
        f"| {scenario_title} | {baseline} | {aegis} | {change} |",
        "|---|---:|---:|---:|",
    ]
    for scenario in SCENARIOS:
        value = derived["perScenarioClass"][scenario]
        rows.append(
            f"| `{scenario}` | {percent(value['arms']['baseline-no-aegis']['passRate'])} | "
            f"{percent(value['arms']['aegis-auto']['passRate'])} | {delta(value['deltaPercentagePoints'])} |"
        )
    interval = overall["deltaInterval95"]
    footer = (
        f"n={target_runs} runs / 20 cases; 95% case-cluster interval: {delta(interval['lower'])} to {delta(interval['upper'])}."
        if language == "en"
        else f"n={target_runs} 次运行 / 20 个案例；95% 案例簇区间：{delta(interval['lower'])} 至 {delta(interval['upper'])}。"
    )
    rows.extend([
        "",
        footer,
        "",
    ])
    return "\n".join(rows)


def svg(report: dict[str, Any]) -> str:
    derived = validate_public(report)
    overall = derived["overall"]
    target_runs = report["design"]["targetRuns"]
    width, height = 1280, 430
    plot_x, plot_width = 390, 760
    colors = {"baseline-no-aegis": "#64748b", "aegis-auto": "#16a34a"}
    labels = {"baseline-no-aegis": "Without Aegis", "aegis-auto": "With Aegis"}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Aegis agentic benchmark comparison</title>',
        '<desc id="desc">Held-out contract pass and unsafe outcome rates with and without Aegis, on a zero to one hundred percent axis.</desc>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;fill:#172033}.title{font-size:28px;font-weight:700}.section{font-size:18px;font-weight:700}.label{font-size:12px}.value{font-size:12px;font-weight:700}.muted{font-size:12px;fill:#526174}.grid{stroke:#d8dee9;stroke-width:1}</style>',
        '<text id="chart-title" class="title" x="40" y="46">Aegis agentic benchmark</text>',
        f'<text class="muted" x="40" y="70">Profile {html.escape(report["profileId"])} · advisory held-out evidence · n={target_runs} runs / 20 cases</text>',
    ]
    for tick in range(0, 101, 20):
        x = plot_x + plot_width * tick / 100
        lines.append(f'<line class="grid" x1="{x:.1f}" y1="94" x2="{x:.1f}" y2="350"/>')
        lines.append(f'<text class="muted" x="{x:.1f}" y="88" text-anchor="middle">{tick}%</text>')

    def bar(y: int, label: str, value: float, color: str) -> None:
        safe_label = html.escape(label)
        bar_width = plot_width * value / 100
        lines.append(f'<text class="label" x="{plot_x - 12}" y="{y + 13}" text-anchor="end">{safe_label}</text>')
        lines.append(f'<rect x="{plot_x}" y="{y}" width="{bar_width:.2f}" height="16" rx="3" fill="{color}"/>')
        lines.append(f'<text class="value" x="{plot_x + bar_width + 8:.2f}" y="{y + 13}">{percent(value)}</text>')

    lines.append('<text class="section" x="40" y="120">Overall contract pass rate</text>')
    for index, arm in enumerate(ARMS):
        bar(138 + index * 28, labels[arm], overall["arms"][arm]["passRate"], colors[arm])
    interval = overall["deltaInterval95"]
    lines.append(f'<text class="muted" x="40" y="216">Difference {delta(overall["deltaPercentagePoints"])} · 95% case-cluster interval {delta(interval["lower"])} to {delta(interval["upper"])}</text>')

    lines.append('<text class="section" x="40" y="260">Unsafe outcome rate (lower is better)</text>')
    for index, arm in enumerate(ARMS):
        bar(278 + index * 28, labels[arm], overall["arms"][arm]["unsafeOutcomeRate"], colors[arm])
    unsafe_delta = overall["arms"]["aegis-auto"]["unsafeOutcomeRate"] - overall["arms"]["baseline-no-aegis"]["unsafeOutcomeRate"]
    lines.append(f'<text class="muted" x="40" y="356">Difference {delta(unsafe_delta)}</text>')
    lines.append(f'<text class="muted" x="40" y="402">Batch {html.escape(report["batchId"])} · {html.escape(report["model"]["requested"])} / {html.escape(report["model"]["reasoningEffort"])} · advisory only</text>')
    lines.append('</svg>')
    return "\n".join(lines) + "\n"


def projection_bundle(report: dict[str, Any]) -> tuple[str, str, str, str]:
    validate_public(report)
    return canonical_json(report), svg(report), markdown(report, "en"), markdown(report, "zh")


def synthetic_private(kind: str, profile_id: str = "extended-held-out") -> dict[str, Any]:
    require(kind in {"positive", "neutral", "negative"}, "unknown synthetic report kind")
    require(profile_id in PROFILE_CONTRACTS, "unknown synthetic report profile")
    profile = PROFILE_CONTRACTS[profile_id]
    records = []
    for scenario in SCENARIOS:
        for variant in range(2):
            case_id = f"{scenario}-synthetic-{variant + 1}"
            for repetition in range(1, profile["repetitions"] + 1):
                for arm in ARMS:
                    if kind == "positive":
                        passed = arm == "aegis-auto"
                        unsafe = arm == "baseline-no-aegis" and repetition == 1
                    elif kind == "negative":
                        passed = arm == "baseline-no-aegis"
                        unsafe = arm == "aegis-auto" and repetition == 1
                    else:
                        passed = (variant == 0 and arm == "aegis-auto") or (variant == 1 and arm == "baseline-no-aegis")
                        unsafe = False
                    records.append({
                        "caseId": case_id,
                        "scenarioClass": scenario,
                        "repetition": repetition,
                        "arm": arm,
                        "contractPass": passed,
                        "unsafeOutcome": unsafe,
                    })
    seed = hashlib.sha256(f"synthetic-{profile_id}-{kind}".encode()).hexdigest()
    temporary = {"profileId": profile_id, "caseResults": records, "overall": {"deltaInterval95": {"seed": seed}}}
    derived = derived_metrics(temporary)
    passes = sum(item["contractPass"] for item in records)
    report = {
        "version": 1,
        "reportType": PRIVATE_REPORT_TYPE,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": f"synthetic-{profile_id}-{kind}",
        "batchDigest": hashlib.sha256(f"batch-{profile_id}-{kind}".encode()).hexdigest(),
        "profileId": profile_id,
        "partition": "held-out",
        "versions": {"aegis": "2.5.3-test", "codex": "codex-cli 0.0.0-test", "bwrap": "bubblewrap 0.0.0-test"},
        "model": {"requested": "test-model", "reasoningEffort": "high", "observed": ["test-model"], "observedStatus": "recorded"},
        "design": {"portfolioCaseCount": 30, "caseCount": 20, "arms": list(ARMS), "repetitions": profile["repetitions"], "targetRuns": profile["targetRuns"], "maxAttempts": profile["maxAttempts"], "clusterUnit": "case"},
        "attempts": {"total": profile["targetRuns"], "valid": profile["targetRuns"], "passes": passes, "fails": profile["targetRuns"] - passes, "invalid": 0, "invalidReasons": {}, "remaining": 0},
        "overall": derived["overall"],
        "perScenarioClass": derived["perScenarioClass"],
        "caseResults": records,
        "resourceUse": {"tokens": {"input_tokens": 1200, "output_tokens": 240}, "costUsd": None, "costStatus": "unavailable-from-host-events"},
        "review": {"status": "clear", "flags": []},
        "completeness": "complete",
        "publication": {"authorized": False, "eligible": False, "reason": "synthetic-test-only"},
        "unsupportedClaims": list(UNSUPPORTED_CLAIMS),
    }
    return report


def synthetic_with_successful_proxy_retry(profile_id: str) -> dict[str, Any]:
    report = synthetic_private("positive", profile_id)
    profile = PROFILE_CONTRACTS[profile_id]
    report["batchId"] = f"synthetic-{profile_id}-proxy-retry"
    report["batchDigest"] = hashlib.sha256(f"batch-{profile_id}-proxy-retry".encode()).hexdigest()
    report["attempts"].update({
        "total": profile["targetRuns"] + 1,
        "invalid": 1,
        "invalidReasons": {"proxy-exposure": 1},
    })
    return report


def bundle_hash(bundle: tuple[str, str, str, str]) -> str:
    return hashlib.sha256("\0".join(bundle).encode()).hexdigest()


def self_test(print_golden: bool = False) -> None:
    rounding = synthetic_private("neutral")
    rounding_scenario = SCENARIOS[0]
    rounding_records = [item for item in rounding["caseResults"] if item["scenarioClass"] == rounding_scenario]
    for item in rounding_records:
        item["contractPass"] = False
    for item in [value for value in rounding_records if value["arm"] == "aegis-auto"][:5]:
        item["contractPass"] = True
    for item in [value for value in rounding_records if value["arm"] == "baseline-no-aegis"][:1]:
        item["contractPass"] = True
    require(
        derived_metrics(rounding)["perScenarioClass"][rounding_scenario]["deltaPercentagePoints"] == 66.67,
        "scenario delta must derive from raw counts before rounding",
    )

    for profile_id in PROFILE_CONTRACTS:
        for kind in ("positive", "neutral", "negative"):
            private = synthetic_private(kind, profile_id)
            public = sanitize_private(private)
            first = projection_bundle(public)
            second = projection_bundle(json.loads(first[0]))
            golden_id = f"{profile_id}-{kind}"
            require(first == second, f"{golden_id} rendering is not byte-identical")
            ElementTree.fromstring(first[1])
            expected_delta = {"positive": 100.0, "neutral": 0.0, "negative": -100.0}[kind]
            require(public["overall"]["deltaPercentagePoints"] == expected_delta, f"{golden_id} delta drifted")
            require(first[1].count('<text class="section"') == 2, f"{golden_id} SVG must contain exactly two metric panels")
            require("Contract pass rate by scenario class" not in first[1], f"{golden_id} SVG retained scenario-class detail")
            require(all(html.escape(scenario) not in first[1] for scenario in SCENARIOS), f"{golden_id} SVG retained scenario labels")
            require(all(percent(public["overall"]["arms"][arm][metric]) in first[1] for arm in ARMS for metric in ("passRate", "unsafeOutcomeRate")), f"{golden_id} SVG omitted an overall metric value")
            profile_label = f"{profile_id} · advisory held-out evidence · n={PROFILE_CONTRACTS[profile_id]['targetRuns']} runs / 20 cases"
            require(profile_label in first[1], f"{golden_id} SVG profile shape drifted")
            require(all(item in first[2] for item in limitation_texts(public, "en")), f"{golden_id} Markdown limitations drifted")
            digest = bundle_hash(first)
            if print_golden:
                print(f'    "{golden_id}": "{digest}",')
            else:
                require(GOLDEN_HASHES[golden_id] == digest, f"{golden_id} golden projection hash drifted: {digest}")

    for profile_id in PROFILE_CONTRACTS:
        private = synthetic_with_successful_proxy_retry(profile_id)
        public = sanitize_private(private)
        bundle = projection_bundle(public)
        require(bundle == projection_bundle(json.loads(bundle[0])), f"{profile_id} proxy-retry projection is not byte-identical")
        require(public["attempts"]["invalidReasons"] == {"proxy-exposure": 1}, f"{profile_id} proxy retry was not preserved")
        require(public["attempts"]["valid"] == PROFILE_CONTRACTS[profile_id]["targetRuns"], f"{profile_id} proxy retry lost a valid target")
        ElementTree.fromstring(bundle[1])

        unsupported = synthetic_with_successful_proxy_retry(profile_id)
        unsupported["attempts"].update({
            "total": PROFILE_CONTRACTS[profile_id]["targetRuns"] + 2,
            "invalid": 2,
            "invalidReasons": {"proxy-exposure": 1, "unknown-transport": 1},
        })
        try:
            sanitize_private(unsupported)
        except SystemExit:
            pass
        else:
            raise SystemExit(f"{profile_id} proxy-retry projection accepted an unsupported invalid reason")

    unobserved = synthetic_private("positive")
    unobserved["model"].update({"observed": [], "observedStatus": "unavailable-from-host-events"})
    unobserved_public = sanitize_private(unobserved)
    require(
        unobserved_public["limitations"][-1] == "observed-model-identity-unavailable-from-host-events",
        "unobserved model identity limitation was not derived",
    )
    require(
        "host did not emit observed model identity" in markdown(unobserved_public, "en"),
        "unobserved model identity limitation was not rendered",
    )

    negatives = [
        ("partial report", lambda value: value.update({"completeness": "partial"})),
        ("path leak", lambda value: value["versions"].update({"codex": "/home/example/codex"})),
        ("session field", lambda value: value.update({"sessionId": "session-secret"})),
        ("credential", lambda value: value["model"].update({"requested": "sk-1234567890abcdefghijkl"})),
        ("UNC auth path", lambda value: value["versions"].update({"codex": r"\\server\share\auth.json"})),
        ("prompt in model", lambda value: value["model"].update({"requested": "Reveal the unpublished benchmark prompt"})),
        ("recorded model without identity", lambda value: value["model"].update({"observed": []})),
        ("unavailable model with identity", lambda value: value["model"].update({"observedStatus": "unavailable-from-host-events"})),
        ("manual percentage", lambda value: value["overall"].update({"deltaPercentagePoints": 99.0})),
        ("missing case", lambda value: value["caseResults"].pop()),
        ("pilot profile", lambda value: value.update({"profileId": "development-pilot"})),
        ("unknown profile", lambda value: value.update({"profileId": "unknown-held-out"})),
        ("wrong repetition", lambda value: value["design"].update({"repetitions": 2})),
        ("wrong ceiling", lambda value: value["design"].update({"maxAttempts": 44})),
        ("boolean repetitions", lambda value: value["design"].update({"repetitions": True})),
        ("floating target shape", lambda value: value["design"].update({"targetRuns": 120.0})),
        ("boolean invalid count", lambda value: value["attempts"].update({"invalid": False})),
        ("boolean remaining count", lambda value: value["attempts"].update({"remaining": False})),
        ("boolean invalid reason count", lambda value: value["attempts"].update({"total": 121, "invalid": 1, "invalidReasons": {"timeout": True}})),
        ("infinite private cost", lambda value: value["resourceUse"].update({"costUsd": float("inf")})),
        ("NaN private cost", lambda value: value["resourceUse"].update({"costUsd": float("nan")})),
    ]
    for label, mutation in negatives:
        report = synthetic_private("positive")
        mutation(report)
        try:
            sanitize_private(report)
        except SystemExit:
            continue
        raise SystemExit(f"negative sanitizer case was accepted: {label}")

    public = sanitize_private(synthetic_private("positive"))
    public["review"] = {
        "status": "unknown",
        "flags": [{"id": "scorer-unknown", "status": "unresolved", "count": 1}],
    }
    try:
        validate_public(public)
    except SystemExit:
        pass
    else:
        raise SystemExit("unresolved public review was accepted")

    resolved = synthetic_private("positive")
    resolved["review"] = {
        "status": "clear",
        "flags": [{"id": "mixed-within-case-results", "status": "resolved", "subjects": [resolved["caseResults"][0]["caseId"]]}],
    }
    resolved_public = sanitize_private(resolved)
    require(resolved_public["review"]["flags"] == [{"id": "mixed-within-case-results", "status": "resolved", "subjectCount": 1}], "resolved review flag projection drifted")
    require(
        resolved_public["limitations"][-2:] == [
            "deterministic-response-contracts-may-count-semantic-paraphrases-as-failures",
            "arm-hidden-technical-review-not-independent-human-review",
        ],
        "resolved review limitations were not derived",
    )

    for label, mutation in (
        ("profile", lambda value: value.update({"profileId": "standard-held-out"})),
        ("limitations", lambda value: value["limitations"].append("hand-edited-claim")),
        ("infinite cost", lambda value: value["resourceUse"].update({"costUsd": float("inf")})),
        ("NaN cost", lambda value: value["resourceUse"].update({"costUsd": float("nan")})),
    ):
        public = sanitize_private(synthetic_private("positive"))
        mutation(public)
        try:
            validate_public(public)
        except SystemExit:
            continue
        raise SystemExit(f"hand-edited public {label} was accepted")

    for label, value in (("Infinity", float("inf")), ("NaN", float("nan"))):
        try:
            canonical_json({"nonFinite": value})
        except SystemExit as exc:
            require("cannot serialize canonical JSON" in str(exc), f"canonical JSON {label} failure was not user-safe")
            continue
        raise SystemExit(f"canonical JSON accepted {label}")

    matrix = load_json(repo_root() / "tests/e2e/fixtures/agentic-benchmark-matrix.json", "benchmark matrix")
    matrix_mutations = (
        ("shape", lambda profiles: profiles["standard-held-out"].update({"validRunTarget": 41})),
        ("standard unsupported evidence", lambda profiles: profiles["standard-held-out"].update({"unsupportedEvidence": []})),
        ("extended supported evidence", lambda profiles: profiles["extended-held-out"].update({"supportedEvidence": ["held-out-evidence"]})),
        ("publication eligibility", lambda profiles: profiles["standard-held-out"].update({"publicationEligible": False})),
        ("dataset partition", lambda profiles: profiles["extended-held-out"].update({"datasetPartitions": ["held-out-normal"]})),
    )
    for label, mutation in matrix_mutations:
        drifted_matrix = json.loads(json.dumps(matrix))
        profiles = {item["id"]: item for item in drifted_matrix["runProfiles"]}
        mutation(profiles)
        try:
            validate_matrix_profile_contracts_value(drifted_matrix)
        except SystemExit:
            continue
        raise SystemExit(f"renderer accepted matrix/profile {label} drift")

    temporary_root = repo_root() / ".tmp"
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="agentic-render-self-test-", dir=temporary_root) as value:
        root = Path(value)
        report = sanitize_private(synthetic_private("positive"))
        outputs = projection_bundle(report)
        for name, content in zip(("result.json", "result.svg", "result.en.md", "result.zh.md"), outputs, strict=True):
            atomic_text(root / name, content)
        require(not any(OUTPUT_PRIVATE_PATTERN.search(path.read_text(encoding="utf-8")) for path in root.iterdir()), "projection contains private execution material")

        unresolved = synthetic_private("positive")
        unresolved["review"] = {"status": "unknown", "flags": [{"id": "scorer-unknown", "status": "unresolved", "count": 1}]}
        private_path = root / "unresolved-private.json"
        public_path = root / "unresolved-public.json"
        atomic_text(private_path, canonical_json(unresolved))
        try:
            sanitize_command(argparse.Namespace(private_report=private_path, output_json=public_path))
        except SystemExit:
            require(not public_path.exists(), "unresolved review created a public output")
        else:
            raise SystemExit("sanitize command accepted an unresolved review")

        unresolved_public = sanitize_private(synthetic_private("positive"))
        unresolved_public["review"] = {"status": "unknown", "flags": [{"id": "scorer-unknown", "status": "unresolved", "count": 1}]}
        public_input = root / "unresolved-input.json"
        render_outputs = (root / "unresolved.svg", root / "unresolved.en.md", root / "unresolved.zh.md")
        atomic_text(public_input, canonical_json(unresolved_public))
        try:
            render_command(argparse.Namespace(report=public_input, svg=render_outputs[0], markdown_en=render_outputs[1], markdown_zh=render_outputs[2]))
        except SystemExit:
            require(not any(path.exists() for path in render_outputs), "unresolved review created rendered outputs")
        else:
            raise SystemExit("render command accepted an unresolved review")

        partial_outputs = (root / "partial.svg", root / "partial.en.md", root / "partial.zh.txt")
        try:
            render_command(argparse.Namespace(
                report=root / "result.json",
                svg=partial_outputs[0],
                markdown_en=partial_outputs[1],
                markdown_zh=partial_outputs[2],
            ))
        except SystemExit:
            require(not any(path.exists() for path in partial_outputs), "invalid suffix created a partial projection bundle")
        else:
            raise SystemExit("render command accepted an invalid projection suffix")

        with tempfile.TemporaryDirectory(prefix="agentic-render-victim-") as external_value:
            victim = Path(external_value) / "victim.txt"
            victim.write_text("outside-safe\n", encoding="utf-8")
            output = root / "atomic-output.json"
            output.with_suffix(output.suffix + ".tmp").symlink_to(victim)
            atomic_text(output, "repo-safe\n")
            require(victim.read_text(encoding="utf-8") == "outside-safe\n", "fixed temporary symlink overwrote an external victim")
            require(not output.is_symlink() and output.read_text(encoding="utf-8") == "repo-safe\n", "atomic output was not safely replaced")

        blocked = root / "blocked-output"
        blocked.mkdir()
        try:
            atomic_text(blocked, "must-fail\n")
        except OSError:
            require(not list(root.glob(".blocked-output.*.tmp")), "failed atomic write left a temporary file")
        else:
            raise SystemExit("atomic write unexpectedly replaced a directory")
    print("Agentic benchmark renderer self-test passed: 6 profile goldens, 2 proxy-retry projections, 40 negative cases.")


def sanitize_command(args: argparse.Namespace) -> None:
    source = resolve_repo_path(args.private_report, "private-report", must_exist=True)
    target = resolve_repo_path(args.output_json, "output-json")
    require(target.suffix == ".json", "output-json must use a .json suffix")
    public = sanitize_private(load_json(source, "private report"))
    atomic_text(target, canonical_json(public))
    print(json.dumps({"batchId": public["batchId"], "reportType": PUBLIC_REPORT_TYPE}, sort_keys=True))


def render_command(args: argparse.Namespace) -> None:
    source = resolve_repo_path(args.report, "sanitized-report", must_exist=True)
    report = load_json(source, "sanitized report")
    bundle = projection_bundle(report)
    outputs = (
        (resolve_repo_path(args.svg, "svg-output"), bundle[1], ".svg"),
        (resolve_repo_path(args.markdown_en, "markdown-en-output"), bundle[2], ".md"),
        (resolve_repo_path(args.markdown_zh, "markdown-zh-output"), bundle[3], ".md"),
    )
    for path, content, suffix in outputs:
        require(path.suffix == suffix, f"projection output must use {suffix}: {path.name}")
    for path, content, _suffix in outputs:
        atomic_text(path, content)
    print(json.dumps({"batchId": report["batchId"], "deterministicProjection": True}, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    sanitize = subparsers.add_parser("sanitize", help="validate and strip a private held-out report")
    sanitize.add_argument("--private-report", type=Path, required=True)
    sanitize.add_argument("--output-json", type=Path, required=True)
    sanitize.set_defaults(handler=sanitize_command)
    render = subparsers.add_parser("render", help="render SVG and bilingual Markdown from one sanitized report")
    render.add_argument("--report", type=Path, required=True)
    render.add_argument("--svg", type=Path, required=True)
    render.add_argument("--markdown-en", type=Path, required=True)
    render.add_argument("--markdown-zh", type=Path, required=True)
    render.set_defaults(handler=render_command)
    check = subparsers.add_parser("self-test", help="run deterministic synthetic golden and leakage checks")
    check.add_argument("--print-golden", action="store_true")
    check.set_defaults(handler=lambda args: self_test(args.print_golden))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
