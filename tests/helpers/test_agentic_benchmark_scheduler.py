#!/usr/bin/env python3
"""Offline fake-executor tests for deterministic bounded benchmark scheduling."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_benchmark_scheduler import execute_schedule, validate_ledger


ARMS = ("baseline-no-aegis", "aegis-auto")


class TickClock:
    def __init__(self, step: float = 1.0):
        self.value = 0.0
        self.step = step

    def __call__(self) -> float:
        value = self.value
        self.value += self.step
        return value


def targets(case_count: int) -> list[dict]:
    result = []
    for case_number in range(1, case_count + 1):
        for arm in ARMS:
            result.append(
                {
                    "targetId": f"case-{case_number}-{arm}",
                    "caseId": f"case-{case_number}",
                    "scenarioClass": f"scenario-{case_number}",
                    "partition": "development",
                    "repetition": 1,
                    "arm": arm,
                }
            )
    return result


def batch(
    *,
    case_count: int = 3,
    workers: int = 3,
    max_attempts: int | None = None,
    wall: float = 100.0,
    timeout: float = 10.0,
    failure_limit: int = 2,
) -> dict:
    schedule = targets(case_count)
    return {
        "profileId": "fake-profile",
        "workers": workers,
        "wallClockBudgetSeconds": wall,
        "perAttemptTimeoutSeconds": timeout,
        "infrastructureFailureLimit": failure_limit,
        "maxAttempts": max_attempts if max_attempts is not None else len(schedule) + 4,
        "schedule": schedule,
    }


def ledger(*, cumulative: float = 0.0) -> dict:
    return {"cumulativeWallSeconds": cumulative, "attempts": []}


def valid(_target: dict | None = None) -> dict:
    return {"status": "valid", "contractPass": True}


def attempt_record(target: dict, number: int, wave: int, status: str, **extra) -> dict:
    record = {
        "attemptNumber": number,
        "waveNumber": wave,
        "targetId": target["targetId"],
        "caseId": target["caseId"],
        "scenarioClass": target["scenarioClass"],
        "partition": target["partition"],
        "repetition": target["repetition"],
        "arm": target["arm"],
        "status": status,
    }
    record.update(extra)
    return record


def active_wave(*, wave: int, first_attempt: int, count: int, reserved: float, pre_wave: float) -> dict:
    return {
        "waveNumber": wave,
        "firstAttemptNumber": first_attempt,
        "attemptCount": count,
        "reservedWallSeconds": reserved,
        "preWaveCumulativeWallSeconds": pre_wave,
    }


class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        (self.root / ".tmp").mkdir(exist_ok=True)

    def execute(self, frozen_batch: dict, state: dict, executor, *, clock=None) -> dict:
        with tempfile.TemporaryDirectory(prefix="agentic-scheduler-test-", dir=self.root / ".tmp") as value:
            return execute_schedule(
                frozen_batch,
                state,
                Path(value) / "ledger.json",
                executor,
                monotonic=clock or TickClock(),
            )

    def test_full_success_uses_bounded_concurrency(self):
        frozen = batch(case_count=4, workers=3, max_attempts=8)
        lock = threading.Lock()
        release = threading.Event()
        active = 0
        maximum = 0

        def executor(target, _attempt_number, _timeout_seconds):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
                if active >= 2:
                    release.set()
            self.assertTrue(release.wait(2), "paired executor calls did not overlap")
            with lock:
                active -= 1
            return valid(target)

        state = self.execute(frozen, ledger(), executor)
        self.assertEqual(len(state["attempts"]), 8)
        self.assertEqual(state["scheduler"]["status"], "complete")
        self.assertGreater(maximum, 1)
        self.assertLessEqual(maximum, frozen["workers"])
        self.assertEqual(state["cumulativeWallSeconds"], 3.0)

    def test_paired_canary_transport_failure_stops_before_fanout(self):
        frozen = batch(case_count=3)
        calls = []

        def executor(_target, attempt_number, _timeout_seconds):
            calls.append(attempt_number)
            if attempt_number == 1:
                return {"status": "invalid", "invalidReason": "infrastructure"}
            return valid()

        state = self.execute(frozen, ledger(), executor)
        self.assertEqual(sorted(calls), [1, 2])
        self.assertEqual(len(state["attempts"]), 2)
        self.assertEqual(state["scheduler"]["reason"], "paired-canary-transport-failure")

    def test_scorer_unknown_canary_does_not_block_fanout(self):
        frozen = batch(case_count=2, workers=2, max_attempts=5)

        def executor(_target, attempt_number, _timeout_seconds):
            if attempt_number == 1:
                return {"status": "invalid", "invalidReason": "scorer-unknown"}
            return valid()

        state = self.execute(frozen, ledger(), executor)
        self.assertEqual(len(state["attempts"]), 5)
        self.assertEqual(state["scheduler"]["status"], "complete")
        self.assertEqual(state["attempts"][-1]["targetId"], frozen["schedule"][0]["targetId"])

    def test_out_of_order_completion_commits_and_retries_in_attempt_order(self):
        frozen = batch(case_count=3, workers=3, max_attempts=9)
        fourth_completed = threading.Event()
        completion_order = []
        frozen_wave_observations = []

        with tempfile.TemporaryDirectory(prefix="agentic-scheduler-order-", dir=self.root / ".tmp") as value:
            ledger_path = Path(value) / "ledger.json"

            def executor(_target, attempt_number, _timeout_seconds):
                if attempt_number >= 3:
                    persisted = json.loads(ledger_path.read_text(encoding="utf-8"))
                    wave = persisted["attempts"][-min(3, len(persisted["attempts"])) :]
                    frozen_wave_observations.append(
                        all(item["status"] == "launched" for item in wave)
                        and persisted["activeWave"]["waveNumber"] == wave[0]["waveNumber"]
                    )
                if attempt_number == 3:
                    self.assertTrue(fourth_completed.wait(2))
                    completion_order.append(3)
                    return {"status": "invalid", "invalidReason": "timeout"}
                if attempt_number == 4:
                    completion_order.append(4)
                    fourth_completed.set()
                    return {"status": "invalid", "invalidReason": "scorer-unknown"}
                return valid()

            state = execute_schedule(frozen, ledger(), ledger_path, executor, monotonic=TickClock())

        self.assertLess(completion_order.index(4), completion_order.index(3))
        self.assertTrue(all(frozen_wave_observations))
        expected = [target["targetId"] for target in frozen["schedule"]]
        expected.extend([frozen["schedule"][2]["targetId"], frozen["schedule"][3]["targetId"]])
        self.assertEqual([attempt["targetId"] for attempt in state["attempts"]], expected)
        self.assertEqual([attempt["attemptNumber"] for attempt in state["attempts"]], list(range(1, 9)))

    def test_invalid_retry_consumes_ceiling_until_exhausted(self):
        frozen = batch(case_count=2, workers=2, max_attempts=6)

        def executor(_target, attempt_number, _timeout_seconds):
            if attempt_number in {3, 5, 6}:
                return {"status": "invalid", "invalidReason": "scorer-unknown"}
            return valid()

        state = self.execute(frozen, ledger(), executor)
        retry_id = frozen["schedule"][2]["targetId"]
        self.assertEqual([item["targetId"] for item in state["attempts"]].count(retry_id), 3)
        self.assertEqual(len(state["attempts"]), 6)
        self.assertEqual(state["scheduler"]["reason"], "paid-attempt-ceiling-exhausted")

    def test_interrupted_launched_wave_is_recovered_as_terminal_invalid(self):
        frozen = batch(case_count=3)
        state = ledger(cumulative=10.0)
        state["attempts"] = [
            attempt_record(frozen["schedule"][0], 1, 1, "launched"),
            attempt_record(frozen["schedule"][1], 2, 1, "launched"),
        ]
        state["activeWave"] = active_wave(wave=1, first_attempt=1, count=2, reserved=10.0, pre_wave=0.0)
        calls = []
        state = self.execute(frozen, state, lambda *_args: calls.append(True) or valid())
        self.assertEqual(calls, [])
        self.assertTrue(all(item["invalidReason"] == "infrastructure" for item in state["attempts"]))
        self.assertTrue(all(item["recovery"] == "interrupted-before-final-record" for item in state["attempts"]))
        self.assertEqual(state["cumulativeWallSeconds"], 10.0)
        self.assertNotIn("activeWave", state)
        self.assertEqual(state["scheduler"]["reason"], "paired-canary-transport-failure")

    def test_non_canary_recovery_keeps_reservation_and_bounds_next_wave(self):
        frozen = batch(case_count=2, workers=3, max_attempts=7, wall=6.0, timeout=4.0, failure_limit=3)
        state = ledger(cumulative=5.0)
        state["attempts"] = [
            attempt_record(frozen["schedule"][0], 1, 1, "valid", contractPass=True),
            attempt_record(frozen["schedule"][1], 2, 1, "valid", contractPass=True),
            attempt_record(frozen["schedule"][2], 3, 2, "launched"),
            attempt_record(frozen["schedule"][3], 4, 2, "launched"),
        ]
        state["activeWave"] = active_wave(wave=2, first_attempt=3, count=2, reserved=4.0, pre_wave=1.0)
        timeouts = []

        def executor(_target, attempt_number, timeout_seconds):
            timeouts.append(timeout_seconds)
            if attempt_number == 5:
                return {"status": "invalid", "invalidReason": "scorer-unknown"}
            return valid()

        state = self.execute(frozen, state, executor, clock=TickClock(step=1.0))
        self.assertEqual(timeouts, [1.0, 1.0])
        self.assertEqual(state["cumulativeWallSeconds"], 6.0)
        self.assertEqual(state["scheduler"]["reason"], "cumulative-wall-budget-exhausted")
        self.assertTrue(all(item["recovery"] == "interrupted-before-final-record" for item in state["attempts"][2:4]))
        self.assertNotIn("activeWave", state)

    def test_resume_matches_attempt_order_and_preserves_cumulative_wall(self):
        frozen = batch(case_count=2, workers=2, max_attempts=5)

        def executor(_target, attempt_number, _timeout_seconds):
            if attempt_number == 3:
                return {"status": "invalid", "invalidReason": "scorer-unknown"}
            return valid()

        uninterrupted = self.execute(frozen, ledger(), executor, clock=TickClock(step=2.0))
        resumed = ledger(cumulative=4.0)
        resumed["attempts"] = copy.deepcopy(uninterrupted["attempts"][:4])
        resumed = self.execute(frozen, resumed, executor, clock=TickClock(step=2.0))
        self.assertEqual(
            [item["targetId"] for item in resumed["attempts"]],
            [item["targetId"] for item in uninterrupted["attempts"]],
        )
        self.assertEqual(resumed["cumulativeWallSeconds"], uninterrupted["cumulativeWallSeconds"])
        self.assertEqual(resumed["cumulativeWallSeconds"], 6.0)

    def test_cumulative_wall_stops_and_timeout_is_bounded_by_remaining(self):
        frozen = batch(case_count=3, workers=2, max_attempts=6, wall=5.0, timeout=4.0)
        timeouts = {}

        def executor(_target, attempt_number, timeout_seconds):
            timeouts[attempt_number] = timeout_seconds
            return valid()

        state = self.execute(frozen, ledger(), executor, clock=TickClock(step=3.0))
        self.assertEqual([timeouts[number] for number in (1, 2)], [4.0, 4.0])
        self.assertEqual([timeouts[number] for number in (3, 4)], [2.0, 2.0])
        self.assertEqual(len(state["attempts"]), 4)
        self.assertEqual(state["cumulativeWallSeconds"], 6.0)
        self.assertEqual(state["scheduler"]["reason"], "cumulative-wall-budget-exhausted")

        stopped = ledger(cumulative=5.0)
        calls = []
        stopped = self.execute(frozen, stopped, lambda *_args: calls.append(True) or valid())
        self.assertEqual(calls, [])
        self.assertEqual(stopped["scheduler"]["reason"], "cumulative-wall-budget-exhausted")

    def test_infrastructure_failure_limit_opens_after_completed_wave(self):
        frozen = batch(case_count=4, workers=3, max_attempts=10, failure_limit=2)

        def executor(_target, attempt_number, _timeout_seconds):
            if attempt_number in {3, 4}:
                return {"status": "invalid", "invalidReason": "credential-exposure" if attempt_number == 3 else "timeout"}
            return valid()

        state = self.execute(frozen, ledger(), executor)
        self.assertEqual(len(state["attempts"]), 5)
        self.assertEqual(state["scheduler"]["reason"], "infrastructure-circuit-open")
        self.assertEqual([item["attemptNumber"] for item in state["attempts"]], [1, 2, 3, 4, 5])

    def test_missing_and_invalid_policy_fail_closed(self):
        complete = batch()
        for field in (
            "profileId",
            "workers",
            "wallClockBudgetSeconds",
            "perAttemptTimeoutSeconds",
            "infrastructureFailureLimit",
            "maxAttempts",
            "schedule",
        ):
            with self.subTest(missing=field):
                frozen = copy.deepcopy(complete)
                frozen.pop(field)
                with self.assertRaises(SystemExit):
                    self.execute(frozen, ledger(), lambda *_args: valid())

        for field, value in (
            ("profileId", ""),
            ("workers", 0),
            ("workers", True),
            ("wallClockBudgetSeconds", 0),
            ("perAttemptTimeoutSeconds", -1),
            ("infrastructureFailureLimit", 4),
            ("maxAttempts", 1),
        ):
            with self.subTest(invalid=field, value=value):
                frozen = copy.deepcopy(complete)
                frozen[field] = value
                with self.assertRaises(SystemExit):
                    self.execute(frozen, ledger(), lambda *_args: valid())

        unpaired = copy.deepcopy(complete)
        unpaired["schedule"][1]["caseId"] = "different-case"
        with self.assertRaises(SystemExit):
            self.execute(unpaired, ledger(), lambda *_args: valid())

    def test_executor_cannot_overwrite_scheduler_owned_identity(self):
        frozen = batch(case_count=2, workers=2, max_attempts=4)
        state = ledger()

        def executor(target, _attempt_number, _timeout_seconds):
            return {**valid(target), "targetId": "forged-target", "attemptNumber": 99}

        with self.assertRaises(SystemExit):
            self.execute(frozen, state, executor)
        self.assertEqual(
            [attempt["targetId"] for attempt in state["attempts"]],
            [target["targetId"] for target in frozen["schedule"][:2]],
        )
        self.assertTrue(all(attempt["status"] == "launched" for attempt in state["attempts"]))
        self.assertIn("activeWave", state)

    def test_terminal_replay_rejects_wave_and_identity_forgery(self):
        frozen = batch(case_count=4, workers=3, max_attempts=10, failure_limit=2)

        def executor(_target, attempt_number, _timeout_seconds):
            if attempt_number in {3, 4}:
                return {"status": "invalid", "invalidReason": "infrastructure"}
            return valid()

        state = self.execute(frozen, ledger(), executor)
        self.assertEqual(state["scheduler"]["reason"], "infrastructure-circuit-open")

        split_failures = copy.deepcopy(state)
        split_failures["attempts"][3]["waveNumber"] = 3
        with self.assertRaises(SystemExit):
            validate_ledger(frozen, split_failures)

        forged_identity = copy.deepcopy(state)
        forged_identity["attempts"][2]["caseId"] = "forged-case"
        with self.assertRaises(SystemExit):
            validate_ledger(frozen, forged_identity)

        continued = copy.deepcopy(state)
        continued_targets = [
            *frozen["schedule"][5:8],
            frozen["schedule"][2],
            frozen["schedule"][3],
        ]
        for offset, target in enumerate(continued_targets, start=6):
            wave = 3 if offset <= 8 else 4
            continued["attempts"].append(attempt_record(target, offset, wave, "valid", contractPass=True))
        with self.assertRaises(SystemExit):
            validate_ledger(frozen, continued)

        active_after_stop = copy.deepcopy(state)
        pre_wave = active_after_stop["cumulativeWallSeconds"]
        for offset, target in enumerate(frozen["schedule"][5:8], start=6):
            active_after_stop["attempts"].append(attempt_record(target, offset, 3, "launched"))
        active_after_stop["activeWave"] = active_wave(
            wave=3,
            first_attempt=6,
            count=3,
            reserved=10.0,
            pre_wave=pre_wave,
        )
        active_after_stop["cumulativeWallSeconds"] = pre_wave + 10.0
        with self.assertRaises(SystemExit):
            validate_ledger(frozen, active_after_stop)

    def test_missing_and_malformed_active_wave_fail_closed(self):
        frozen = batch(case_count=2, workers=3, max_attempts=7, wall=6.0, timeout=4.0, failure_limit=3)
        launched = ledger(cumulative=5.0)
        launched["attempts"] = [
            attempt_record(frozen["schedule"][0], 1, 1, "valid", contractPass=True),
            attempt_record(frozen["schedule"][1], 2, 1, "valid", contractPass=True),
            attempt_record(frozen["schedule"][2], 3, 2, "launched"),
            attempt_record(frozen["schedule"][3], 4, 2, "launched"),
        ]
        with self.assertRaises(SystemExit):
            self.execute(frozen, copy.deepcopy(launched), lambda *_args: valid())

        canonical = copy.deepcopy(launched)
        canonical["activeWave"] = active_wave(wave=2, first_attempt=3, count=2, reserved=4.0, pre_wave=1.0)
        mutations = (
            lambda state: state["activeWave"].update({"reservedWallSeconds": 3.0}),
            lambda state: state.update({"cumulativeWallSeconds": 4.0}),
            lambda state: state["activeWave"].update({"attemptCount": 1}),
            lambda state: state["activeWave"].update({"unexpected": True}),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                malformed = copy.deepcopy(canonical)
                mutate(malformed)
                with self.assertRaises(SystemExit):
                    self.execute(frozen, malformed, lambda *_args: valid())

        orphaned = ledger(cumulative=4.0)
        orphaned["activeWave"] = active_wave(wave=1, first_attempt=1, count=2, reserved=4.0, pre_wave=0.0)
        with self.assertRaises(SystemExit):
            self.execute(frozen, orphaned, lambda *_args: valid())


if __name__ == "__main__":
    unittest.main()
