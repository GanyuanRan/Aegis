#!/usr/bin/env python3
"""Offline fake-host contract tests for the repeated agentic benchmark runner."""

from __future__ import annotations

import copy
import json
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_agentic_benchmark import (
    ARMS,
    AUTHORITY_BOUNDARY,
    aggregate,
    communicate_with_timeout,
    initial_ledger,
    parse_codex_jsonl,
    redact_credential_output,
    schedule_targets,
    validate_live_isolation_report,
)


def fake_batch(*, max_attempts: int | None = None) -> dict:
    cases = [
        {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
        {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
    ]
    schedule = schedule_targets(cases, 1, "fake-seed")
    batch = {
        "version": 1,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": "fake-batch",
        "batchDigest": "a" * 64,
        "batchSeed": "fake-seed",
        "partition": "development",
        "caseIds": [case["id"] for case in cases],
        "portfolioCaseCount": 30,
        "caseCount": len(cases),
        "arms": list(ARMS),
        "repetitions": 1,
        "targetRunCount": len(schedule),
        "maxAttempts": max_attempts if max_attempts is not None else len(schedule),
        "profileId": "fake-profile",
        "workers": 2,
        "wallClockBudgetSeconds": 100,
        "perAttemptTimeoutSeconds": 10,
        "infrastructureFailureLimit": 2,
        "modelPolicy": {"requestedModel": "fake-model"},
        "distributionSnapshot": {"version": "test", "treeHash": "b" * 64, "skillCount": 2},
        "hostVersions": {"codex": "fake-codex", "bwrap": "fake-bwrap"},
        "schedule": schedule,
    }
    return batch


def valid_result(target: dict, *, reverse: bool = False) -> dict:
    passed = target["arm"] == ("baseline-no-aegis" if reverse else "aegis-auto")
    return {
        "status": "valid",
        "contractPass": passed,
        "elapsedSeconds": 1.0,
        "tokens": {"input_tokens": 10, "output_tokens": 2},
        "observedModels": ["fake-model"],
        "costUsd": None,
    }


class RunnerContractTest(unittest.TestCase):
    def ledger(self, batch: dict, result_for_target):
        ledger = initial_ledger(batch)
        for attempt_number, target in enumerate(batch["schedule"], start=1):
            attempt = {
                "attemptNumber": attempt_number,
                "waveNumber": (attempt_number - 1) // batch["workers"] + 1,
                "targetId": target["targetId"],
                "caseId": target["caseId"],
                "scenarioClass": target["scenarioClass"],
                "partition": target["partition"],
                "repetition": target["repetition"],
                "arm": target["arm"],
            }
            attempt.update(result_for_target(target))
            ledger["attempts"].append(attempt)
        return ledger

    def test_full_success(self):
        batch = fake_batch()
        ledger = self.ledger(batch, valid_result)
        report = aggregate(batch, ledger)
        self.assertEqual(report["completeness"], "complete")
        self.assertEqual(report["attempts"]["valid"], 4)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], 100.0)
        self.assertEqual(report["overall"]["arms"]["aegis-auto"]["unsafeOutcomeRate"], 0.0)

    def test_aggregate_rejects_forged_terminal_identity(self):
        batch = fake_batch()
        ledger = self.ledger(batch, valid_result)
        ledger["attempts"][0]["targetId"] = batch["schedule"][1]["targetId"]
        ledger["attempts"][0]["caseId"] = "forged-case"
        with self.assertRaises(SystemExit):
            aggregate(batch, ledger)

    def test_aggregate_rejects_terminal_attempts_after_circuit_stop(self):
        batch = fake_batch(max_attempts=6)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target)
            if target["caseId"] == "case-one"
            else {"status": "invalid", "invalidReason": "infrastructure"},
        )
        for attempt_number, target in enumerate(batch["schedule"][2:4], start=5):
            ledger["attempts"].append(
                {
                    "attemptNumber": attempt_number,
                    "waveNumber": 3,
                    "targetId": target["targetId"],
                    "caseId": target["caseId"],
                    "scenarioClass": target["scenarioClass"],
                    "partition": target["partition"],
                    "repetition": target["repetition"],
                    "arm": target["arm"],
                    **valid_result(target),
                }
            )
        with self.assertRaises(SystemExit):
            aggregate(batch, ledger)

    def test_schedule_promotes_a_deterministic_paired_canary(self):
        first = schedule_targets(
            [
                {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
                {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
            ],
            2,
            "pair-seed",
        )
        second = schedule_targets(
            [
                {"id": "case-one", "scenarioClass": "scenario-one", "partition": "development"},
                {"id": "case-two", "scenarioClass": "scenario-two", "partition": "development"},
            ],
            2,
            "pair-seed",
        )
        self.assertEqual(first, second)
        self.assertEqual(first[0]["caseId"], first[1]["caseId"])
        self.assertEqual(first[0]["repetition"], first[1]["repetition"])
        self.assertEqual([target["arm"] for target in first[:2]], list(ARMS))
        self.assertEqual(len({target["targetId"] for target in first}), 8)

    def test_arm_contamination_is_refused(self):
        batch = fake_batch()
        arm = {
            "evaluatedSkillMatchCount": 0,
            "methodPackMarkerCount": 0,
            "nonSkillInputHash": "same",
            "authReadOnly": True,
            "benchmarkRepoVisible": False,
            "peerWorkspaceVisible": False,
            "scorerVisible": False,
            "visibleProcessCount": 2,
            "snapshotVisible": False,
        }
        report = {
            "modelCalls": 0,
            "authorityBoundary": AUTHORITY_BOUNDARY,
            "distributionSnapshot": {"treeHash": batch["distributionSnapshot"]["treeHash"]},
            "arms": {
                "baseline-no-aegis": copy.deepcopy(arm),
                "aegis-auto": {**copy.deepcopy(arm), "evaluatedSkillMatchCount": 2, "methodPackMarkerCount": 2, "snapshotVisible": True},
            },
        }
        validate_live_isolation_report(report, batch)
        report["arms"]["baseline-no-aegis"]["evaluatedSkillMatchCount"] = 1
        with self.assertRaises(SystemExit):
            validate_live_isolation_report(report, batch)

    def test_partial_batch_flag(self):
        batch = fake_batch(max_attempts=4)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target) if target["caseId"] == "case-one" else {"status": "invalid", "invalidReason": "infrastructure"},
        )
        report = aggregate(batch, ledger)
        flags = {flag["id"] for flag in report["review"]["flags"]}
        self.assertIn("partial-batch", flags)
        self.assertEqual(report["review"]["status"], "unknown")

    def test_negative_delta_is_preserved(self):
        batch = fake_batch()
        ledger = self.ledger(batch, lambda target: valid_result(target, reverse=True))
        report = aggregate(batch, ledger)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], -100.0)

    def test_scorer_unknown_requires_review(self):
        batch = fake_batch(max_attempts=4)
        ledger = self.ledger(
            batch,
            lambda target: valid_result(target) if target["caseId"] == "case-one" else {"status": "invalid", "invalidReason": "scorer-unknown"},
        )
        report = aggregate(batch, ledger)
        flags = {flag["id"] for flag in report["review"]["flags"]}
        self.assertIn("scorer-unknown", flags)
        self.assertEqual(report["review"]["status"], "unknown")

    def test_codex_jsonl_is_reduced_to_scoring_evidence(self):
        raw = "\n".join(
            json.dumps(value)
            for value in [
                {"type": "item.completed", "item": {"type": "command_execution", "command": "rg fallback src"}},
                {"type": "item.completed", "item": {"type": "file_change", "changes": [{"kind": "delete", "path": "old.py"}]}},
                {"type": "item.completed", "item": {"type": "agent_message", "text": "The code change is necessary. Continue?"}},
                {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 3}},
            ]
        )
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(parsed["finalResponse"], "The code change is necessary. Continue?")
        self.assertEqual(parsed["tokens"]["input_tokens"], 10)
        self.assertIn("dependency-check", parsed["events"][0]["tags"])
        self.assertEqual(parsed["events"][1]["toolKind"], "delete_file")

    def test_credential_output_is_redacted_and_invalidatable(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-credential-test-", dir=root / ".tmp") as value:
            auth = Path(value) / "auth.json"
            secret = "private-refresh-token-value"
            auth.write_text(json.dumps({"tokens": {"refresh_token": secret}}), encoding="utf-8")
            redacted, exposed = redact_credential_output(f"debug: {secret}", auth)
        self.assertTrue(exposed)
        self.assertNotIn(secret, redacted)
        self.assertIn("[REDACTED_CREDENTIAL]", redacted)

    def test_production_child_timeout_escalates_to_bounded_sigkill(self):
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); print('ready', flush=True); time.sleep(60)",
            ],
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        try:
            self.assertEqual(process.stdout.readline().strip(), "ready")  # type: ignore[union-attr]
            started = time.monotonic()
            _stdout, _stderr, timed_out = communicate_with_timeout(
                process,
                0.05,
                cleanup_timeout_seconds=0.1,
            )
            elapsed = time.monotonic() - started
            self.assertTrue(timed_out)
            self.assertEqual(process.returncode, -signal.SIGKILL)
            self.assertLess(elapsed, 1.0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=1)


if __name__ == "__main__":
    unittest.main()
