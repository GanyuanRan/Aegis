#!/usr/bin/env python3
"""Evaluate Kimi stream-JSON output for Aegis Skill tool routing."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


class EvaluationError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot parse JSON {path}: {exc}") from exc


def skill_calls(path: Path) -> list[str]:
    calls: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvaluationError(f"cannot read Kimi output {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"{path}:{line_number}: invalid stream JSON: {exc.msg}") from exc
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        tool_calls = message.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            raise EvaluationError(f"{path}:{line_number}: tool_calls must be a list")
        for call in tool_calls:
            if not isinstance(call, dict):
                continue
            function = call.get("function")
            if not isinstance(function, dict) or function.get("name") != "Skill":
                continue
            arguments = function.get("arguments", "{}")
            try:
                parsed = json.loads(arguments) if isinstance(arguments, str) else arguments
            except json.JSONDecodeError as exc:
                raise EvaluationError(
                    f"{path}:{line_number}: invalid Skill arguments: {exc.msg}"
                ) from exc
            if not isinstance(parsed, dict) or not isinstance(parsed.get("skill"), str):
                raise EvaluationError(f"{path}:{line_number}: Skill call is missing string argument skill")
            calls.append(parsed["skill"])
    return calls


def fixture_cases(path: Path) -> list[dict[str, Any]]:
    fixture = load_json(path)
    if not isinstance(fixture, dict) or fixture.get("version") != 1:
        raise EvaluationError("Kimi trigger fixture must use version 1")
    cases = fixture.get("cases")
    if not isinstance(cases, list) or len(cases) != 5:
        raise EvaluationError("Kimi trigger fixture must contain exactly five cases")
    if not all(isinstance(case, dict) for case in cases):
        raise EvaluationError("every Kimi trigger fixture case must be an object")
    case_ids = [case.get("id") for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise EvaluationError("Kimi trigger fixture case ids must be unique")
    return cases


def evaluate_case(case: dict[str, Any], result_path: Path) -> tuple[int, int, int]:
    case_id = case.get("id")
    expected = case.get("expectedSkill")
    if not isinstance(case_id, str) or not case_id:
        raise EvaluationError("fixture case id must be a non-empty string")
    if expected is not None and not isinstance(expected, str):
        raise EvaluationError(f"{case_id}: expectedSkill must be a string or null")
    calls = skill_calls(result_path)
    counts = Counter(calls)
    duplicates = sum(count - 1 for count in counts.values() if count > 1)
    false_negative = int(expected is not None and expected not in counts)
    unexpected = calls if expected is None else [skill for skill in calls if skill != expected]
    false_positive = int(bool(unexpected))
    print(f"  [{case_id}] expected={expected!r} actual={calls}")
    return false_negative, false_positive, duplicates


def evaluate_resume(path: Path, expected: str) -> None:
    calls = skill_calls(path)
    unexpected = [skill for skill in calls if skill != expected]
    if unexpected:
        raise EvaluationError(f"resume output invoked unexpected skills: {unexpected}")
    if calls.count(expected) > 1:
        raise EvaluationError(f"resume output invoked {expected} more than once: {calls}")
    print(f"  [resume] allowed={expected!r} actual={calls}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--results-dir", required=True, type=Path)
    parser.add_argument("--resume-result", type=Path)
    parser.add_argument("--resume-expected", default="systematic-debugging")
    args = parser.parse_args()

    try:
        cases = fixture_cases(args.fixtures)
        totals = [0, 0, 0]
        for case in cases:
            case_id = case["id"]
            outcome = evaluate_case(case, args.results_dir / f"{case_id}.jsonl")
            totals = [left + right for left, right in zip(totals, outcome)]
        if args.resume_result is not None:
            evaluate_resume(args.resume_result, args.resume_expected)
        false_negatives, false_positives, duplicates = totals
        print(
            "Kimi trigger smoke totals: "
            f"false_negatives={false_negatives} "
            f"false_positives={false_positives} duplicates={duplicates}"
        )
        if any(totals):
            return 1
    except EvaluationError as exc:
        print(f"Kimi trigger smoke evaluation failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
