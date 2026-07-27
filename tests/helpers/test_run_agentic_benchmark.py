#!/usr/bin/env python3
"""Offline fake-host contract tests for the repeated agentic benchmark runner."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from run_agentic_benchmark import (
    ARMS,
    AUTHORITY_BOUNDARY,
    aggregate,
    execute_schedule,
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
    def execute(self, batch: dict, executor):
        ledger = initial_ledger(batch)
        root = Path(__file__).resolve().parents[2]
        (root / ".tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="agentic-runner-test-", dir=root / ".tmp") as value:
            execute_schedule(batch, ledger, Path(value) / "ledger.json", executor)
        return ledger

    def test_full_success(self):
        batch = fake_batch()
        ledger = self.execute(batch, lambda target, _: valid_result(target))
        report = aggregate(batch, ledger)
        self.assertEqual(report["completeness"], "complete")
        self.assertEqual(report["attempts"]["valid"], 4)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], 100.0)
        self.assertEqual(report["overall"]["arms"]["aegis-auto"]["unsafeOutcomeRate"], 0.0)

    def test_timeout_retry(self):
        batch = fake_batch(max_attempts=5)
        calls = 0

        def executor(target, _):
            nonlocal calls
            calls += 1
            if calls == 1:
                return {"status": "invalid", "invalidReason": "timeout"}
            return valid_result(target)

        ledger = self.execute(batch, executor)
        report = aggregate(batch, ledger)
        self.assertEqual(report["completeness"], "complete")
        self.assertEqual(report["attempts"]["total"], 5)
        self.assertEqual(report["attempts"]["invalidReasons"], {"timeout": 1})

    def test_resume_replays_the_same_retry_queue(self):
        batch = fake_batch(max_attempts=5)
        calls = 0

        def uninterrupted_executor(target, _):
            nonlocal calls
            calls += 1
            if calls == 1:
                return {"status": "invalid", "invalidReason": "timeout"}
            return valid_result(target)

        uninterrupted = self.execute(batch, uninterrupted_executor)
        first = batch["schedule"][0]
        resumed = initial_ledger(batch)
        resumed["attempts"].append(
            {
                "attemptNumber": 1,
                "targetId": first["targetId"],
                "caseId": first["caseId"],
                "scenarioClass": first["scenarioClass"],
                "partition": first["partition"],
                "repetition": first["repetition"],
                "arm": first["arm"],
                "status": "invalid",
                "invalidReason": "timeout",
            }
        )
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-resume-test-", dir=root / ".tmp") as value:
            execute_schedule(batch, resumed, Path(value) / "ledger.json", lambda target, _: valid_result(target))
        self.assertEqual(
            [attempt["targetId"] for attempt in resumed["attempts"]],
            [attempt["targetId"] for attempt in uninterrupted["attempts"]],
        )

    def test_ceiling_exhaustion(self):
        batch = fake_batch()
        ledger = self.execute(batch, lambda _target, _number: {"status": "invalid", "invalidReason": "timeout"})
        report = aggregate(batch, ledger)
        self.assertEqual(report["completeness"], "partial")
        self.assertEqual(report["attempts"]["total"], batch["maxAttempts"])
        self.assertEqual(report["attempts"]["valid"], 0)

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
        ledger = self.execute(
            batch,
            lambda target, _: valid_result(target) if target["caseId"] == "case-one" else {"status": "invalid", "invalidReason": "infrastructure"},
        )
        report = aggregate(batch, ledger)
        flags = {flag["id"] for flag in report["review"]["flags"]}
        self.assertIn("partial-batch", flags)
        self.assertEqual(report["review"]["status"], "unknown")

    def test_negative_delta_is_preserved(self):
        batch = fake_batch()
        ledger = self.execute(batch, lambda target, _: valid_result(target, reverse=True))
        report = aggregate(batch, ledger)
        self.assertEqual(report["overall"]["deltaPercentagePoints"], -100.0)

    def test_scorer_unknown_requires_review(self):
        batch = fake_batch(max_attempts=4)
        ledger = self.execute(
            batch,
            lambda target, _: valid_result(target) if target["caseId"] == "case-one" else {"status": "invalid", "invalidReason": "scorer-unknown"},
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


if __name__ == "__main__":
    unittest.main()
