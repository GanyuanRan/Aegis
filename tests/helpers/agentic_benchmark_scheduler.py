#!/usr/bin/env python3
"""Deterministic bounded scheduling for the agentic benchmark."""

from __future__ import annotations

import json
import math
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath
from typing import Any, Callable


INVALID_REASONS = {
    "timeout",
    "infrastructure",
    "scorer-unknown",
    "credential-exposure",
    "proxy-exposure",
}
TRANSPORT_INVALID_REASONS = {
    "timeout",
    "infrastructure",
    "credential-exposure",
    "proxy-exposure",
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
ACTIVE_WAVE_FIELDS = {
    "waveNumber",
    "firstAttemptNumber",
    "attemptCount",
    "reservedWallSeconds",
    "preWaveCumulativeWallSeconds",
}
ACTIVE_BUDGET_STAGE_FIELDS = {
    "stage",
    "maximumWallSeconds",
    "reservedWallSeconds",
    "preStageCumulativeWallSeconds",
}
ATTEMPT_IDENTITY_FIELDS = (
    "targetId",
    "caseId",
    "scenarioClass",
    "partition",
    "repetition",
    "arm",
)
SCHEDULER_OWNED_ATTEMPT_FIELDS = {"attemptNumber", "waveNumber", *ATTEMPT_IDENTITY_FIELDS}
COMMON_RESULT_FIELDS = {"status", "elapsedSeconds", "hostExit"}
VALID_RESULT_FIELDS = {
    *COMMON_RESULT_FIELDS,
    "contractPass",
    "checkCounts",
    "triggeredVetoes",
    "tokens",
    "costUsd",
    "observedModels",
    "artifactRoot",
}
INVALID_RESULT_FIELDS = {*COMMON_RESULT_FIELDS, "invalidReason", "errorType"}

# Executors must enforce the supplied timeout and return only after their child
# process and workspace cleanup have reached a terminal state. Python worker
# threads are a concurrency primitive here, not a process termination boundary.
Executor = Callable[[dict[str, Any], int, float], dict[str, Any]]
MonotonicClock = Callable[[], float]
BudgetedStage = Callable[[float], Any]


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
        for field in ATTEMPT_IDENTITY_FIELDS:
            _require(field in target, f"schedule target is missing {field}")
        for field in ("targetId", "caseId", "scenarioClass", "partition", "arm"):
            _require(isinstance(target[field], str) and target[field], f"{field} must be a non-empty string")
        _positive_integer(target["repetition"], "repetition")
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
        directory_descriptor = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
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


def _validate_result(result: dict[str, Any], *, allow_recovery: bool = False) -> dict[str, Any]:
    _require(isinstance(result, dict), "attempt result must be an object")
    forbidden = sorted(set(result) & SCHEDULER_OWNED_ATTEMPT_FIELDS)
    _require(not forbidden, f"attempt result cannot overwrite scheduler-owned fields: {', '.join(forbidden)}")
    status = result.get("status")
    _require(status in {"valid", "invalid"}, "attempt result status must be valid or invalid")
    allowed = VALID_RESULT_FIELDS if status == "valid" else INVALID_RESULT_FIELDS
    if allow_recovery and status == "invalid":
        allowed = {*allowed, "recovery"}
    unknown = sorted(set(result) - allowed)
    _require(not unknown, f"attempt result fields are invalid: {', '.join(unknown)}")
    if "elapsedSeconds" in result:
        elapsed = result["elapsedSeconds"]
        _require(
            isinstance(elapsed, (int, float))
            and not isinstance(elapsed, bool)
            and math.isfinite(elapsed)
            and elapsed >= 0,
            "elapsedSeconds must be a non-negative finite number",
        )
    if "hostExit" in result:
        _require(isinstance(result["hostExit"], int) and not isinstance(result["hostExit"], bool), "hostExit must be an integer")
    if status == "valid":
        _require(isinstance(result.get("contractPass"), bool), "valid attempt result requires boolean contractPass")
        if "checkCounts" in result:
            counts = result["checkCounts"]
            _require(isinstance(counts, dict) and set(counts) == {"pass", "fail", "unknown"}, "checkCounts fields are invalid")
            _require(
                all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in counts.values()),
                "checkCounts values must be non-negative integers",
            )
        if "triggeredVetoes" in result:
            vetoes = result["triggeredVetoes"]
            _require(isinstance(vetoes, list) and all(isinstance(value, str) and value for value in vetoes), "triggeredVetoes must contain non-empty strings")
        if "tokens" in result:
            tokens = result["tokens"]
            _require(isinstance(tokens, dict) and all(isinstance(key, str) and key for key in tokens), "tokens must be an object with string keys")
            _require(
                all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in tokens.values()),
                "token counts must be non-negative integers",
            )
        if "costUsd" in result and result["costUsd"] is not None:
            cost = result["costUsd"]
            _require(
                isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost) and cost >= 0,
                "costUsd must be null or a non-negative finite number",
            )
        if "observedModels" in result:
            models = result["observedModels"]
            _require(isinstance(models, list) and all(isinstance(value, str) and value for value in models), "observedModels must contain non-empty strings")
        if "artifactRoot" in result:
            artifact_root = result["artifactRoot"]
            _require(isinstance(artifact_root, str) and artifact_root, "artifactRoot must be a non-empty relative path")
            artifact_path = PurePosixPath(artifact_root)
            _require(not artifact_path.is_absolute() and ".." not in artifact_path.parts, "artifactRoot must be a safe relative path")
    else:
        _require(result.get("invalidReason") in INVALID_REASONS, "invalid attempt result requires an allowed invalidReason")
        if "errorType" in result:
            _require(isinstance(result["errorType"], str) and result["errorType"], "errorType must be a non-empty string")
        if "recovery" in result:
            _require(allow_recovery, "executor result cannot set recovery")
            _require(
                result["recovery"] == "interrupted-before-final-record"
                and result["invalidReason"] == "infrastructure",
                "recovery marker requires an infrastructure-invalid attempt",
            )
    return dict(result)


def _validate_attempt_identity(attempt: dict[str, Any], target: dict[str, Any]) -> None:
    for field in ATTEMPT_IDENTITY_FIELDS:
        _require(
            type(attempt.get(field)) is type(target[field]) and attempt.get(field) == target[field],
            f"ledger attempt {field} does not match the frozen target",
        )


def _terminal_transport_count(attempts: list[dict[str, Any]]) -> int:
    return sum(
        attempt.get("status") == "invalid" and attempt.get("invalidReason") in TRANSPORT_INVALID_REASONS
        for attempt in attempts
    )


def _wave_stop_reason(batch: dict[str, Any], wave_number: int, wave: list[dict[str, Any]]) -> str | None:
    transport_failures = _terminal_transport_count(wave)
    if wave_number == 1 and transport_failures:
        return "paired-canary-transport-failure"
    if wave_number > 1 and transport_failures >= batch["infrastructureFailureLimit"]:
        return "infrastructure-circuit-open"
    return None


def _replay_queue(
    batch: dict[str, Any],
    ledger: dict[str, Any],
) -> tuple[list[dict[str, Any]], str | None]:
    queue = list(batch["schedule"])
    attempts = ledger["attempts"]
    _require(len(attempts) <= batch["maxAttempts"], "ledger exceeds the paid attempt ceiling")
    position = 0
    wave_number = 1
    terminal_stop: str | None = None
    while position < len(attempts):
        _require(queue, "ledger contains attempts after all frozen targets completed")
        available_attempts = batch["maxAttempts"] - position
        wave_size = 2 if position == 0 else min(batch["workers"], len(queue), available_attempts)
        _require(len(attempts) - position >= wave_size, "ledger ends with an incomplete terminal wave")
        wave = attempts[position : position + wave_size]
        targets = queue[:wave_size]
        queue = queue[wave_size:]
        for offset, (attempt, target) in enumerate(zip(wave, targets)):
            _require(isinstance(attempt, dict), "ledger attempts must be objects")
            _require(attempt.get("attemptNumber") == position + offset + 1, "ledger attempt numbers must be contiguous and ordered")
            _require(attempt.get("waveNumber") == wave_number, "ledger wave numbers must be contiguous and deterministic")
            _validate_attempt_identity(attempt, target)
            result = {key: value for key, value in attempt.items() if key not in SCHEDULER_OWNED_ATTEMPT_FIELDS}
            _validate_result(result, allow_recovery=True)
        for target, attempt in zip(targets, wave):
            if attempt["status"] == "invalid":
                queue.append(target)
        stop_reason = _wave_stop_reason(batch, wave_number, wave)
        if stop_reason is not None:
            _require(
                position + wave_size == len(attempts),
                "ledger contains terminal attempts after a scheduler stop condition",
            )
            terminal_stop = stop_reason
        position += wave_size
        wave_number += 1
    return queue, terminal_stop


def _validate_active_wave(batch: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any] | None:
    launched = [attempt for attempt in ledger["attempts"] if attempt.get("status") == "launched"]
    active = ledger.get("activeWave")
    if active is None:
        _require(not launched, "launched attempts require an activeWave reservation")
        return None
    _require(isinstance(active, dict), "activeWave must be an object")
    _require(set(active) == ACTIVE_WAVE_FIELDS, "activeWave fields are invalid")
    wave_number = _positive_integer(active["waveNumber"], "activeWave.waveNumber")
    first_attempt = _positive_integer(active["firstAttemptNumber"], "activeWave.firstAttemptNumber")
    attempt_count = _positive_integer(active["attemptCount"], "activeWave.attemptCount")
    reserved = _positive_number(active["reservedWallSeconds"], "activeWave.reservedWallSeconds")
    pre_wave = active["preWaveCumulativeWallSeconds"]
    _require(
        isinstance(pre_wave, (int, float))
        and not isinstance(pre_wave, bool)
        and math.isfinite(pre_wave)
        and pre_wave >= 0,
        "activeWave.preWaveCumulativeWallSeconds must be a non-negative finite number",
    )
    _require(first_attempt + attempt_count - 1 == len(ledger["attempts"]), "activeWave must describe the final attempt records")
    prefix = ledger["attempts"][: first_attempt - 1]
    active_attempts = ledger["attempts"][first_attempt - 1 :]
    _require(len(active_attempts) == attempt_count, "activeWave attempt count does not match the ledger")
    _require(active_attempts == launched, "activeWave attempts must all remain launched")
    _require(
        all(set(attempt) == {*SCHEDULER_OWNED_ATTEMPT_FIELDS, "status"} for attempt in active_attempts),
        "launched attempt fields are invalid",
    )
    _require(
        all(attempt.get("attemptNumber") == first_attempt + offset for offset, attempt in enumerate(active_attempts)),
        "activeWave attempt numbers must be contiguous",
    )
    _require(
        all(attempt.get("waveNumber") == wave_number for attempt in active_attempts),
        "activeWave wave number does not match its attempts",
    )
    prior_wave = max(
        (attempt.get("waveNumber", 0) for attempt in prefix if isinstance(attempt.get("waveNumber"), int)),
        default=0,
    )
    _require(wave_number == prior_wave + 1, "activeWave wave number is not sequential")
    pending, prefix_stop = _replay_queue(batch, {"attempts": prefix})
    _require(prefix_stop is None, "activeWave cannot follow a terminal scheduler stop condition")
    available_attempts = batch["maxAttempts"] - len(prefix)
    expected_count = 2 if not prefix else min(batch["workers"], len(pending), available_attempts)
    _require(attempt_count == expected_count, "activeWave size does not match the deterministic next wave")
    for attempt, target in zip(active_attempts, pending[:attempt_count]):
        _validate_attempt_identity(attempt, target)
    expected_reservation = min(
        float(batch["perAttemptTimeoutSeconds"]),
        float(batch["wallClockBudgetSeconds"]) - float(pre_wave),
    )
    _require(expected_reservation > 0, "activeWave cannot reserve an exhausted wall budget")
    _require(reserved == expected_reservation, "activeWave reservation does not match the bounded executor timeout")
    _require(
        float(ledger["cumulativeWallSeconds"]) == float(pre_wave) + reserved,
        "activeWave reservation does not match cumulativeWallSeconds",
    )
    return active


def _validate_active_budget_stage(batch: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any] | None:
    active = ledger.get("activeBudgetStage")
    if active is None:
        return None
    _require("activeWave" not in ledger, "active budget stage cannot overlap an active wave")
    _require(isinstance(active, dict), "activeBudgetStage must be an object")
    _require(set(active) == ACTIVE_BUDGET_STAGE_FIELDS, "activeBudgetStage fields are invalid")
    _require(isinstance(active["stage"], str) and active["stage"], "activeBudgetStage.stage must be non-empty")
    maximum = _positive_number(active["maximumWallSeconds"], "activeBudgetStage.maximumWallSeconds")
    reserved = _positive_number(active["reservedWallSeconds"], "activeBudgetStage.reservedWallSeconds")
    pre_stage = active["preStageCumulativeWallSeconds"]
    _require(
        isinstance(pre_stage, (int, float))
        and not isinstance(pre_stage, bool)
        and math.isfinite(pre_stage)
        and pre_stage >= 0,
        "activeBudgetStage.preStageCumulativeWallSeconds must be a non-negative finite number",
    )
    expected = min(maximum, float(batch["wallClockBudgetSeconds"]) - float(pre_stage))
    _require(expected > 0, "activeBudgetStage cannot reserve an exhausted wall budget")
    _require(reserved == expected, "activeBudgetStage reservation does not match its bounded timeout")
    _require(
        float(ledger["cumulativeWallSeconds"]) == float(pre_stage) + reserved,
        "activeBudgetStage reservation does not match cumulativeWallSeconds",
    )
    return active


def _recover_interrupted(batch: dict[str, Any], ledger: dict[str, Any]) -> bool:
    active = _validate_active_wave(batch, ledger)
    if active is None:
        return False
    first_attempt = active["firstAttemptNumber"]
    for attempt in ledger["attempts"][first_attempt - 1 :]:
        attempt.update(
            {
                "status": "invalid",
                "invalidReason": "infrastructure",
                "recovery": "interrupted-before-final-record",
            }
        )
    del ledger["activeWave"]
    return True


def validate_ledger(batch: dict[str, Any], ledger: dict[str, Any]) -> None:
    """Fail closed unless persisted attempts match the frozen scheduler contract."""

    _validate_policy(batch)
    _require(isinstance(ledger, dict), "ledger must be an object")
    _require(isinstance(ledger.get("attempts"), list), "ledger attempts must be a list")
    cumulative = ledger.get("cumulativeWallSeconds")
    _require(
        isinstance(cumulative, (int, float))
        and not isinstance(cumulative, bool)
        and math.isfinite(cumulative)
        and cumulative >= 0,
        "ledger cumulativeWallSeconds must be a non-negative finite number",
    )
    _require(
        float(cumulative) <= float(batch["wallClockBudgetSeconds"]),
        "ledger cumulativeWallSeconds exceeds the wall-clock budget",
    )
    _validate_active_budget_stage(batch, ledger)
    active = _validate_active_wave(batch, ledger)
    if active is None:
        _replay_queue(batch, ledger)


def execute_budgeted_stage(
    batch: dict[str, Any],
    ledger: dict[str, Any],
    ledger_path: Path,
    stage: str,
    maximum_seconds: float,
    callback: BudgetedStage,
    *,
    monotonic: MonotonicClock = time.monotonic,
) -> Any:
    """Persistently reserve and settle one pre-schedule active-run stage."""

    validate_ledger(batch, ledger)
    _require(isinstance(stage, str) and stage, "budget stage name must be non-empty")
    maximum = _positive_number(maximum_seconds, "budget stage maximum")
    if _recover_interrupted(batch, ledger):
        _set_status(ledger, "recovered", "interrupted-launched-attempts-invalidated")
        _atomic_json(ledger_path, ledger)
        _queue, stop_reason = _replay_queue(batch, ledger)
        if stop_reason is not None:
            _set_status(ledger, "stopped", stop_reason)
            _atomic_json(ledger_path, ledger)
            raise SystemExit("benchmark cannot resume setup after a terminal interrupted wave")
    interrupted = _validate_active_budget_stage(batch, ledger)
    if interrupted is not None:
        del ledger["activeBudgetStage"]
        _set_status(ledger, "recovered", "interrupted-budget-stage-reservation-consumed")
        _atomic_json(ledger_path, ledger)
    remaining = float(batch["wallClockBudgetSeconds"]) - float(ledger["cumulativeWallSeconds"])
    if remaining <= 0:
        _set_status(ledger, "stopped", "cumulative-wall-budget-exhausted")
        _atomic_json(ledger_path, ledger)
        raise SystemExit("benchmark cumulative wall-clock budget is exhausted")
    reservation = min(maximum, remaining)
    pre_stage = float(ledger["cumulativeWallSeconds"])
    ledger["activeBudgetStage"] = {
        "stage": stage,
        "maximumWallSeconds": maximum,
        "reservedWallSeconds": reservation,
        "preStageCumulativeWallSeconds": pre_stage,
    }
    ledger["cumulativeWallSeconds"] = pre_stage + reservation
    _set_status(ledger, "running", f"{stage}-reserved")
    _atomic_json(ledger_path, ledger)
    started = monotonic()
    try:
        result = callback(reservation)
    except BaseException:
        finished = monotonic()
        _require(finished >= started, "monotonic clock moved backwards")
        ledger["cumulativeWallSeconds"] = pre_stage + min(finished - started, reservation)
        del ledger["activeBudgetStage"]
        _set_status(ledger, "stopped", f"{stage}-failed")
        _atomic_json(ledger_path, ledger)
        raise
    finished = monotonic()
    _require(finished >= started, "monotonic clock moved backwards")
    elapsed = finished - started
    ledger["cumulativeWallSeconds"] = pre_stage + min(elapsed, reservation)
    del ledger["activeBudgetStage"]
    _set_status(ledger, "running", f"{stage}-complete")
    _atomic_json(ledger_path, ledger)
    if elapsed >= reservation:
        _set_status(ledger, "stopped", "cumulative-wall-budget-exhausted")
        _atomic_json(ledger_path, ledger)
        raise SystemExit(f"benchmark {stage} exceeded the remaining wall-clock budget")
    return result


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
            results[attempt_number] = _validate_result(result)
    return results


def execute_schedule(
    batch: dict[str, Any],
    ledger: dict[str, Any],
    ledger_path: Path,
    executor: Executor,
    *,
    monotonic: MonotonicClock = time.monotonic,
) -> dict[str, Any]:
    """Execute waves using an executor that enforces its supplied timeout."""

    validate_ledger(batch, ledger)
    if _recover_interrupted(batch, ledger):
        _set_status(ledger, "recovered", "interrupted-launched-attempts-invalidated")
        _atomic_json(ledger_path, ledger)

    queue, existing_stop = _replay_queue(batch, ledger)
    if existing_stop is not None:
        _set_status(ledger, "stopped", existing_stop)
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
        timeout_seconds = min(float(batch["perAttemptTimeoutSeconds"]), remaining_wall)
        _require(timeout_seconds > 0, "executor timeout must be positive")
        pre_wave_cumulative = float(ledger["cumulativeWallSeconds"])
        ledger["attempts"].extend(attempts)
        ledger["activeWave"] = {
            "waveNumber": wave_number,
            "firstAttemptNumber": first_attempt_number,
            "attemptCount": len(attempts),
            "reservedWallSeconds": timeout_seconds,
            "preWaveCumulativeWallSeconds": pre_wave_cumulative,
        }
        ledger["cumulativeWallSeconds"] = pre_wave_cumulative + timeout_seconds
        _set_status(ledger, "running", "wave-frozen")
        _atomic_json(ledger_path, ledger)

        started = monotonic()
        results = _run_wave(executor, attempts, targets, timeout_seconds, batch["workers"])
        finished = monotonic()
        _require(finished >= started, "monotonic clock moved backwards")
        for attempt in attempts:
            attempt.update(results[attempt["attemptNumber"]])
        ledger["cumulativeWallSeconds"] = pre_wave_cumulative + min(finished - started, timeout_seconds)
        del ledger["activeWave"]
        _set_status(ledger, "running", "wave-committed")
        _atomic_json(ledger_path, ledger)

        for target, attempt in zip(targets, attempts):
            if attempt["status"] == "invalid":
                queue.append(target)

        stop_reason = _wave_stop_reason(batch, wave_number, attempts)
        if stop_reason is not None:
            _set_status(ledger, "stopped", stop_reason)
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
