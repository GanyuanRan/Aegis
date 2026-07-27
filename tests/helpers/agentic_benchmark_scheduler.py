#!/usr/bin/env python3
"""Deterministic bounded scheduling for the agentic benchmark."""

from __future__ import annotations

import json
import math
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable


INVALID_REASONS = {
    "timeout",
    "infrastructure",
    "scorer-unknown",
    "credential-exposure",
}
TRANSPORT_INVALID_REASONS = {
    "timeout",
    "infrastructure",
    "credential-exposure",
}
POLICY_FIELDS = (
    "profileId",
    "workers",
    "wallClockBudgetSeconds",
    "perAttemptTimeoutSeconds",
    "infrastructureFailureLimit",
    "maxAttempts",
    "schedule",
)

Executor = Callable[[dict[str, Any], int, float], dict[str, Any]]
MonotonicClock = Callable[[], float]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _positive_number(value: Any, label: str) -> float:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} must be a number")
    _require(math.isfinite(value), f"{label} must be finite")
    _require(value > 0, f"{label} must be positive")
    return float(value)


def _positive_integer(value: Any, label: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    _require(value > 0, f"{label} must be positive")
    return value


def _validate_policy(batch: dict[str, Any]) -> None:
    for field in POLICY_FIELDS:
        _require(field in batch, f"batch scheduler policy is missing {field}")
    _require(isinstance(batch["profileId"], str) and batch["profileId"], "profileId must be a non-empty string")
    workers = _positive_integer(batch["workers"], "workers")
    _positive_number(batch["wallClockBudgetSeconds"], "wallClockBudgetSeconds")
    _positive_number(batch["perAttemptTimeoutSeconds"], "perAttemptTimeoutSeconds")
    failure_limit = _positive_integer(batch["infrastructureFailureLimit"], "infrastructureFailureLimit")
    max_attempts = _positive_integer(batch["maxAttempts"], "maxAttempts")
    schedule = batch["schedule"]
    _require(isinstance(schedule, list) and len(schedule) >= 2, "schedule must contain a paired canary")
    _require(max_attempts >= len(schedule), "maxAttempts cannot be smaller than the frozen schedule")
    _require(workers >= 2, "workers must allow the paired canary to run concurrently")
    _require(failure_limit <= workers, "infrastructureFailureLimit cannot exceed workers")
    first, second = schedule[:2]
    _require(isinstance(first, dict) and isinstance(second, dict), "schedule targets must be objects")
    _require(first.get("caseId") == second.get("caseId"), "paired canary targets must use the same case")
    _require(first.get("repetition") == second.get("repetition"), "paired canary targets must use the same repetition")
    _require(
        {first.get("arm"), second.get("arm")} == {"baseline-no-aegis", "aegis-auto"},
        "paired canary targets must use opposite benchmark arms",
    )
    target_ids: list[str] = []
    for target in schedule:
        _require(isinstance(target, dict), "schedule targets must be objects")
        for field in ("targetId", "caseId", "scenarioClass", "partition", "repetition", "arm"):
            _require(field in target, f"schedule target is missing {field}")
        _require(isinstance(target["targetId"], str) and target["targetId"], "targetId must be a non-empty string")
        target_ids.append(target["targetId"])
    _require(len(target_ids) == len(set(target_ids)), "schedule targetId values must be unique")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _set_status(ledger: dict[str, Any], status: str, reason: str | None = None) -> None:
    state: dict[str, Any] = {"status": status, "authority": "advisory-execution-state"}
    if reason is not None:
        state["reason"] = reason
    ledger["scheduler"] = state


def _attempt_record(target: dict[str, Any], attempt_number: int, wave_number: int) -> dict[str, Any]:
    return {
        "attemptNumber": attempt_number,
        "waveNumber": wave_number,
        "targetId": target["targetId"],
        "caseId": target["caseId"],
        "scenarioClass": target["scenarioClass"],
        "partition": target["partition"],
        "repetition": target["repetition"],
        "arm": target["arm"],
        "status": "launched",
    }


def _recover_interrupted(ledger: dict[str, Any]) -> bool:
    recovered = False
    for attempt in ledger["attempts"]:
        if attempt.get("status") == "launched":
            attempt.update(
                {
                    "status": "invalid",
                    "invalidReason": "infrastructure",
                    "recovery": "interrupted-before-final-record",
                }
            )
            recovered = True
    return recovered


def _replay_queue(batch: dict[str, Any], ledger: dict[str, Any]) -> list[dict[str, Any]]:
    queue = list(batch["schedule"])
    for index, attempt in enumerate(ledger["attempts"], start=1):
        _require(attempt.get("attemptNumber") == index, "ledger attempt numbers must be contiguous and ordered")
        _require(queue, "ledger contains more attempts than the frozen schedule can produce")
        expected = queue.pop(0)
        _require(attempt.get("targetId") == expected["targetId"], "ledger attempt order does not match deterministic queue replay")
        _require(attempt.get("status") in {"valid", "invalid"}, "ledger attempt has no terminal status")
        if attempt["status"] == "invalid":
            _require(attempt.get("invalidReason") in INVALID_REASONS, "ledger attempt has an invalid reason")
            queue.append(expected)
    return queue


def _terminal_transport_count(attempts: list[dict[str, Any]]) -> int:
    return sum(
        attempt.get("status") == "invalid" and attempt.get("invalidReason") in TRANSPORT_INVALID_REASONS
        for attempt in attempts
    )


def _existing_stop_reason(batch: dict[str, Any], ledger: dict[str, Any]) -> tuple[str, str] | None:
    attempts = ledger["attempts"]
    if len(attempts) >= 2 and _terminal_transport_count(attempts[:2]):
        return "stopped", "paired-canary-transport-failure"
    waves: dict[int, list[dict[str, Any]]] = {}
    for attempt in attempts[2:]:
        wave_number = attempt.get("waveNumber")
        if isinstance(wave_number, int) and wave_number > 1:
            waves.setdefault(wave_number, []).append(attempt)
    if any(_terminal_transport_count(wave) >= batch["infrastructureFailureLimit"] for wave in waves.values()):
        return "stopped", "infrastructure-circuit-open"
    return None


def _run_wave(
    executor: Executor,
    attempts: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    timeout_seconds: float,
    workers: int,
) -> dict[int, dict[str, Any]]:
    results: dict[int, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(workers, len(attempts))) as pool:
        futures = {
            pool.submit(executor, target, attempt["attemptNumber"], timeout_seconds): attempt["attemptNumber"]
            for target, attempt in zip(targets, attempts)
        }
        for future in as_completed(futures):
            attempt_number = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # fail closed while retaining the attempt record
                result = {
                    "status": "invalid",
                    "invalidReason": "infrastructure",
                    "errorType": type(exc).__name__,
                }
            _require(isinstance(result, dict), "executor must return an attempt result object")
            _require(result.get("status") in {"valid", "invalid"}, "executor returned an invalid attempt status")
            if result["status"] == "invalid":
                _require(result.get("invalidReason") in INVALID_REASONS, "executor returned an invalid reason")
            results[attempt_number] = result
    return results


def execute_schedule(
    batch: dict[str, Any],
    ledger: dict[str, Any],
    ledger_path: Path,
    executor: Executor,
    *,
    monotonic: MonotonicClock = time.monotonic,
) -> dict[str, Any]:
    """Execute the frozen target queue in deterministic bounded waves."""

    _validate_policy(batch)
    _require(isinstance(ledger.get("attempts"), list), "ledger attempts must be a list")
    cumulative = ledger.get("cumulativeWallSeconds")
    _require(
        isinstance(cumulative, (int, float))
        and not isinstance(cumulative, bool)
        and math.isfinite(cumulative)
        and cumulative >= 0,
        "ledger cumulativeWallSeconds must be a non-negative finite number",
    )
    if _recover_interrupted(ledger):
        _set_status(ledger, "recovered", "interrupted-launched-attempts-invalidated")
        _atomic_json(ledger_path, ledger)

    queue = _replay_queue(batch, ledger)
    existing_stop = _existing_stop_reason(batch, ledger)
    if existing_stop is not None:
        _set_status(ledger, *existing_stop)
        _atomic_json(ledger_path, ledger)
        return ledger
    if queue and 0 < len(ledger["attempts"]) < 2:
        raise SystemExit("ledger contains an incomplete paired canary wave")

    wave_number = max(
        (attempt.get("waveNumber", 0) for attempt in ledger["attempts"] if isinstance(attempt.get("waveNumber"), int)),
        default=0,
    )
    while queue and len(ledger["attempts"]) < batch["maxAttempts"]:
        remaining_wall = float(batch["wallClockBudgetSeconds"]) - float(ledger["cumulativeWallSeconds"])
        if remaining_wall <= 0:
            _set_status(ledger, "stopped", "cumulative-wall-budget-exhausted")
            _atomic_json(ledger_path, ledger)
            return ledger
        available_attempts = batch["maxAttempts"] - len(ledger["attempts"])
        wave_size = 2 if not ledger["attempts"] else min(batch["workers"], len(queue), available_attempts)
        _require(wave_size > 0, "scheduler could not form a positive wave")
        targets = [queue.pop(0) for _ in range(wave_size)]
        wave_number += 1
        first_attempt_number = len(ledger["attempts"]) + 1
        attempts = [
            _attempt_record(target, first_attempt_number + offset, wave_number)
            for offset, target in enumerate(targets)
        ]
        ledger["attempts"].extend(attempts)
        _set_status(ledger, "running", "wave-frozen")
        _atomic_json(ledger_path, ledger)

        timeout_seconds = min(float(batch["perAttemptTimeoutSeconds"]), remaining_wall)
        _require(timeout_seconds > 0, "executor timeout must be positive")
        started = monotonic()
        results = _run_wave(executor, attempts, targets, timeout_seconds, batch["workers"])
        finished = monotonic()
        _require(finished >= started, "monotonic clock moved backwards")
        for attempt in attempts:
            attempt.update(results[attempt["attemptNumber"]])
        ledger["cumulativeWallSeconds"] = float(ledger["cumulativeWallSeconds"]) + (finished - started)
        _set_status(ledger, "running", "wave-committed")
        _atomic_json(ledger_path, ledger)

        for target, attempt in zip(targets, attempts):
            if attempt["status"] == "invalid":
                queue.append(target)

        transport_failures = _terminal_transport_count(attempts)
        if wave_number == 1 and transport_failures:
            _set_status(ledger, "stopped", "paired-canary-transport-failure")
            _atomic_json(ledger_path, ledger)
            return ledger
        if wave_number > 1 and transport_failures >= batch["infrastructureFailureLimit"]:
            _set_status(ledger, "stopped", "infrastructure-circuit-open")
            _atomic_json(ledger_path, ledger)
            return ledger

    if not queue:
        _set_status(ledger, "complete", "frozen-targets-complete")
    elif len(ledger["attempts"]) >= batch["maxAttempts"]:
        _set_status(ledger, "stopped", "paid-attempt-ceiling-exhausted")
    else:
        _set_status(ledger, "stopped", "scheduler-ended-with-pending-targets")
    _atomic_json(ledger_path, ledger)
    return ledger
