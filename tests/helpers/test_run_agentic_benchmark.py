#!/usr/bin/env python3
"""Offline fake-host contract tests for the repeated agentic benchmark runner."""

from __future__ import annotations

import copy
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_agentic_benchmark as benchmark_runner
import agentic_benchmark_provider_preflight
from run_agentic_benchmark import (
    ARMS,
    AUTHORITY_BOUNDARY,
    aggregate,
    communicate_with_timeout,
    execute_target,
    initial_ledger,
    parse_codex_jsonl,
    redact_credential_output,
    require_execution_opt_in,
    resolve_auth_file,
    schedule_targets,
    validate_live_isolation_report,
)
from agentic_benchmark_isolation import resolve_proxy_policy


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
        "datasetPartitions": ["development"],
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
        self.assertEqual(report["profileId"], "fake-profile")
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

    def test_execution_opt_ins_are_profile_specific_and_full_is_retired(self):
        require_execution_opt_in("development-pilot", {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"})
        with self.assertRaises(SystemExit):
            require_execution_opt_in(
                "standard-held-out",
                {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_FULL": "1"},
            )
        require_execution_opt_in(
            "standard-held-out",
            {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1"},
        )
        with self.assertRaises(SystemExit):
            require_execution_opt_in(
                "extended-held-out",
                {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1", "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1"},
            )
        require_execution_opt_in(
            "extended-held-out",
            {
                "AEGIS_AGENTIC_BENCHMARK_LIVE": "1",
                "AEGIS_AGENTIC_BENCHMARK_HELD_OUT": "1",
                "AEGIS_AGENTIC_BENCHMARK_EXTENDED": "1",
            },
        )

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

    def test_auth_cli_path_rejects_a_symlink_before_resolve(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(prefix="agentic-auth-link-test-", dir=root / ".tmp") as value:
            directory = Path(value)
            auth = directory / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            link = directory / "auth-link.json"
            link.symlink_to(auth)
            with self.assertRaises(SystemExit) as caught:
                resolve_auth_file(link)
        self.assertEqual(str(caught.exception), "Codex auth file must not be a symlink")

    def test_attempt_artifacts_are_scrubbed_before_any_result_returns(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                for relative in ("isolated/home/.codex/cache", "isolated/cache.bin", "workspace/result.txt", "codex-stderr.log"):
                    path = attempt_root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(f"before {proxy} after".encode())
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 2.5}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                result = execute_target(
                    root=root,
                    output_root=output_root,
                    batch={},
                    target=target,
                    attempt_number=1,
                    auth_file=output_root / "auth",
                    bwrap=output_root / "bwrap",
                    codex=output_root / "codex",
                    timeout_seconds=1,
                    proxy_policy=policy,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 2.5})
            self.assertFalse((attempt_root / "isolated/home").exists())
            for path in attempt_root.rglob("*"):
                if path.is_file():
                    self.assertNotIn(proxy.encode(), path.read_bytes())

            def exposed_error(**_kwargs):
                exposed_path = attempt_root / "workspace/error.txt"
                exposed_path.parent.mkdir(parents=True, exist_ok=True)
                exposed_path.write_text(proxy, encoding="utf-8")
                raise RuntimeError("original error")

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=exposed_error):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 0.0})

    def test_attempt_cleanup_preserves_normal_result_and_reraises_original_errors(self):
        root = Path(__file__).resolve().parents[2]
        policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-flow-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"
            expected = {"status": "invalid", "invalidReason": "infrastructure", "elapsedSeconds": 1.0}

            def normal(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                (attempt_root / "workspace").mkdir()
                (attempt_root / "workspace/result.txt").write_text("safe", encoding="utf-8")
                return expected

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=normal):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy,
                )
            self.assertIs(result, expected)
            self.assertFalse((attempt_root / "isolated/home").exists())

        for label, error in (("parse", ValueError("parse detail")), ("scorer", RuntimeError("scorer detail")), ("popen", OSError("popen detail"))):
            with self.subTest(label=label), tempfile.TemporaryDirectory(prefix="agentic-artifact-error-test-", dir=root / ".tmp") as value:
                output_root = Path(value)
                attempt_root = output_root / "attempts/001-fake-target"

                def failing(**_kwargs):
                    (attempt_root / "isolated/home").mkdir(parents=True)
                    (attempt_root / "workspace").mkdir()
                    (attempt_root / "workspace/result.txt").write_text("safe", encoding="utf-8")
                    raise error

                with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=failing):
                    with self.assertRaises(type(error)) as caught:
                        execute_target(
                            root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                            auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                            timeout_seconds=1, proxy_policy=policy,
                        )
                self.assertIs(caught.exception, error)
                self.assertFalse((attempt_root / "isolated/home").exists())

    def test_attempt_proxy_symlink_is_materialized_and_invalidates_result(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        target = {"targetId": "symlink-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-link-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-symlink-target"
            proxy_link = attempt_root / "workspace/proxy-link"
            safe_link = attempt_root / "workspace/safe-link"

            def fake_inner(**_kwargs):
                proxy_link.parent.mkdir(parents=True)
                os.symlink(proxy.encode() + b"\xff-tail", os.fsencode(proxy_link))
                safe_link.symlink_to("unrelated-target")
                return {"status": "valid", "contractPass": True, "elapsedSeconds": 1.25}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner):
                result = execute_target(
                    root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                    auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                    timeout_seconds=1, proxy_policy=policy,
                )
            self.assertEqual(result, {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": 1.25})
            self.assertFalse(proxy_link.is_symlink())
            self.assertEqual(proxy_link.read_bytes(), b"[REDACTED_PROXY]\xff-tail")
            self.assertTrue(safe_link.is_symlink())
            self.assertEqual(os.readlink(os.fsencode(safe_link)), b"unrelated-target")

    def test_scrub_failure_deletes_attempt_root_and_fails_closed(self):
        root = Path(__file__).resolve().parents[2]
        policy = resolve_proxy_policy({"HTTP_PROXY": "http://proxy.invalid:8080"})
        target = {"targetId": "fake-target"}
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-failure-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                (attempt_root / "workspace").mkdir()
                return {"status": "valid", "contractPass": True}

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                agentic_benchmark_provider_preflight, "scrub_proxy_artifact_tree", side_effect=OSError("private proxy detail")
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=policy,
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertFalse(attempt_root.exists())

        with tempfile.TemporaryDirectory(prefix="agentic-home-cleanup-failure-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-fake-target"

            def fake_inner(**_kwargs):
                (attempt_root / "isolated/home").mkdir(parents=True)
                return {"status": "valid", "contractPass": True}

            real_remove = benchmark_runner.remove_tmp_directory
            calls = 0

            def fail_home_once(path: Path, repo: Path):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("private home cleanup detail")
                return real_remove(path, repo)

            with mock.patch.object(benchmark_runner, "_execute_target_unscrubbed", side_effect=fake_inner), mock.patch.object(
                benchmark_runner, "remove_tmp_directory", side_effect=fail_home_once
            ):
                with self.assertRaises(SystemExit) as caught:
                    execute_target(
                        root=root, output_root=output_root, batch={}, target=target, attempt_number=1,
                        auth_file=output_root / "auth", bwrap=output_root / "bwrap", codex=output_root / "codex",
                        timeout_seconds=1, proxy_policy=policy,
                    )
            self.assertEqual(str(caught.exception), "benchmark attempt artifact cleanup failed")
            self.assertFalse(attempt_root.exists())

    def test_stale_attempts_are_scrubbed_before_scheduler_recovery(self):
        root = Path(__file__).resolve().parents[2]
        proxy = "http://proxy.invalid:8080"
        policy = resolve_proxy_policy({"HTTP_PROXY": proxy})
        with tempfile.TemporaryDirectory(prefix="agentic-stale-artifact-test-", dir=root / ".tmp") as value:
            output_root = Path(value)
            attempt_root = output_root / "attempts/001-stale"
            home_cache = attempt_root / "isolated/home/.codex/cache"
            workspace = attempt_root / "workspace/result.txt"
            proxy_link = attempt_root / "workspace/proxy-link"
            safe_link = attempt_root / "workspace/safe-link"
            home_cache.parent.mkdir(parents=True)
            workspace.parent.mkdir(parents=True)
            home_cache.write_text(proxy, encoding="utf-8")
            workspace.write_text(proxy, encoding="utf-8")
            os.symlink(b"prefix-" + proxy.encode() + b"-\xff", os.fsencode(proxy_link))
            safe_link.symlink_to("unrelated-target")
            agentic_benchmark_provider_preflight.scrub_stale_proxy_artifacts(
                output_root / "attempts",
                policy,
                lambda path: benchmark_runner.remove_tmp_directory(path, root),
            )
            self.assertFalse((attempt_root / "isolated/home").exists())
            self.assertEqual(workspace.read_text(encoding="utf-8"), "[REDACTED_PROXY]")
            self.assertFalse(proxy_link.is_symlink())
            self.assertEqual(proxy_link.read_bytes(), b"prefix-[REDACTED_PROXY]-\xff")
            self.assertTrue(safe_link.is_symlink())
            self.assertEqual(os.readlink(os.fsencode(safe_link)), b"unrelated-target")

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
