#!/usr/bin/env python3
"""Validate the Aegis agentic benchmark design fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_ARMS = {"baseline-no-aegis", "aegis-auto"}

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
}

REQUIRED_SCENARIOS = {
    "ambiguous-feature-shaping",
    "shared-owner-bug-repair",
    "completion-claim-with-missing-evidence",
    "fallback-retirement-cleanup",
    "tiny-fast-path",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def string_set(data: dict[str, Any], key: str) -> set[str]:
    value = data.get(key, [])
    require(isinstance(value, list), f"{key} must be a list")
    require(all(isinstance(item, str) for item in value), f"{key} must contain strings")
    return set(value)


def validate_arms(data: dict[str, Any]) -> None:
    arms = data.get("arms", [])
    require(isinstance(arms, list), "arms must be a list")
    arm_ids = {arm.get("id") for arm in arms if isinstance(arm, dict)}
    missing = sorted(REQUIRED_ARMS - arm_ids)
    require(not missing, f"missing benchmark arms: {', '.join(missing)}")
    for arm in arms:
        require(isinstance(arm, dict), "each arm must be an object")
        require(arm.get("requiresIsolatedConfig") is True, f"{arm.get('id')} must isolate config")


def validate_metrics(data: dict[str, Any]) -> None:
    metrics = string_set(data, "primaryMetrics")
    missing = sorted(REQUIRED_PRIMARY_METRICS - metrics)
    require(not missing, f"missing primary metrics: {', '.join(missing)}")
    supporting = string_set(data, "supportingMetrics")
    require("diff-size" in supporting, "supporting metrics should allow diff-size without making it primary")
    require("diff-size" not in metrics, "diff-size must not be a primary Aegis success metric")


def validate_scenarios(data: dict[str, Any]) -> None:
    scenarios = data.get("scenarioClasses", [])
    require(isinstance(scenarios, list), "scenarioClasses must be a list")
    by_id = {item.get("id"): item for item in scenarios if isinstance(item, dict)}
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
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data.get("version") == 1, "version must be 1")
    require(data.get("status") == "draft", "status must be draft")
    require("runtime authority" in data.get("primaryQuestion", ""), "primary question must name runtime authority boundary")
    validate_arms(data)
    validate_metrics(data)
    validate_scenarios(data)
    validate_isolation_and_boundary(data)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: validate_agentic_benchmark_matrix.py <matrix-json>")
    validate_matrix(Path(argv[1]))
    print("  [PASS] agentic benchmark matrix preserves metrics, isolation, scenarios, and authority boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
