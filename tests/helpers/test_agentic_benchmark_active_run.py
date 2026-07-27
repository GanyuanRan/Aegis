#!/usr/bin/env python3
"""Offline orchestration tests for the benchmark's absolute invocation deadline."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agentic_benchmark_active_run as active_run
import agentic_benchmark_scheduler as scheduler_owner
import agentic_benchmark_process_supervisor as process_supervisor
import run_agentic_benchmark as benchmark_runner
from agentic_benchmark_provider_preflight import CredentialPolicy


EMPTY_CREDENTIAL_POLICY = CredentialPolicy(())


def frozen_batch(wall_seconds: float = 2.0) -> dict:
    targets = [
        {
            "targetId": f"case-{arm}",
            "caseId": "case",
            "scenarioClass": "scenario",
            "partition": "development",
            "repetition": 1,
            "arm": arm,
        }
        for arm in ("baseline-no-aegis", "aegis-auto")
    ]
    return {
        "profileId": "development-pilot",
        "workers": 2,
        "wallClockBudgetSeconds": wall_seconds,
        "preflightTimeoutSeconds": wall_seconds,
        "perAttemptTimeoutSeconds": wall_seconds,
        "infrastructureFailureLimit": 2,
        "maxAttempts": 2,
        "schedule": targets,
    }


def initial_ledger() -> dict:
    return {"cumulativeWallSeconds": 0.0, "attempts": []}


class ActiveRunTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        (self.root / ".tmp").mkdir(exist_ok=True)

    def runner(self, output_root: Path, batch: dict, ledger: dict, frozen_auth: mock.Mock) -> SimpleNamespace:
        scheduler = SimpleNamespace(
            validate_ledger=lambda *_args: None,
            execute_budgeted_stage=mock.Mock(),
            execute_schedule=mock.Mock(),
        )
        return SimpleNamespace(
            repo_root=lambda: self.root,
            resolve_tmp_child=lambda _root, path, _label: Path(path),
            load_batch_and_ledger=mock.Mock(return_value=(batch, ledger)),
            agentic_benchmark_scheduler=scheduler,
            require_execution_opt_in=mock.Mock(),
            freeze_auth_file=mock.Mock(return_value=frozen_auth),
            require=lambda condition, message: None if condition else (_ for _ in ()).throw(SystemExit(message)),
            atomic_json=mock.Mock(),
        )

    @staticmethod
    def frozen_auth() -> mock.Mock:
        value = mock.Mock()
        value.mount_path = Path("/proc/self/fd/9")
        value.descriptor = 9
        value.credential_policy = EMPTY_CREDENTIAL_POLICY
        value.drift_guard.return_value = {"source": "/safe/auth", "fingerprint": "a" * 64}
        return value

    def prepare_short_batch(self, output_root: Path, wall_seconds: float, cumulative: float = 0.0) -> tuple[dict, dict]:
        benchmark_runner.prepare_batch(
            argparse.Namespace(
                matrix=Path("tests/e2e/fixtures/agentic-benchmark-matrix.json"),
                manifest=Path("tests/e2e/fixtures/agentic-benchmark-cases.json"),
                profile="development-pilot",
                case=["tiny-fast-dev"],
                batch_id=f"offline-active-{output_root.name[-12:]}",
                model="offline-test-model",
                output_root=output_root,
            )
        )
        matrix_path = output_root / "frozen-contracts/matrix.json"
        matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
        profile = next(item for item in matrix["runProfiles"] if item["id"] == "development-pilot")
        profile["wallClockBudgetSeconds"] = wall_seconds
        profile["preflightTimeoutSeconds"] = wall_seconds
        profile["perAttemptTimeoutSeconds"] = wall_seconds
        benchmark_runner.atomic_json(matrix_path, matrix)
        batch_path = output_root / "batch.json"
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        batch["wallClockBudgetSeconds"] = wall_seconds
        batch["preflightTimeoutSeconds"] = wall_seconds
        batch["perAttemptTimeoutSeconds"] = wall_seconds
        batch["matrixHash"] = benchmark_runner.file_hash(matrix_path)
        batch["batchDigest"] = benchmark_runner.batch_digest(batch)
        ledger = benchmark_runner.initial_ledger(batch)
        ledger["cumulativeWallSeconds"] = cumulative
        benchmark_runner.atomic_json(batch_path, batch)
        benchmark_runner.atomic_json(output_root / "ledger.json", ledger)
        benchmark_runner.atomic_json(
            output_root / "active-budget.json",
            {
                "version": 1,
                "profileId": batch["profileId"],
                "batchDigest": batch["batchDigest"],
                "wallClockBudgetSeconds": wall_seconds,
            },
        )
        return batch, ledger

    @staticmethod
    def write_outer_worker(directory: Path) -> Path:
        script = directory / "outer-worker.py"
        script.write_text(
            """
import json
import sys
import time
from pathlib import Path

mode, helper_root, events_path = sys.argv[1:]
request = json.loads(sys.stdin.read())
sys.path.insert(0, helper_root)
import agentic_benchmark_scheduler as scheduler
output_root = Path(request["outputRoot"])
batch = json.loads((output_root / "batch.json").read_text(encoding="utf-8"))
ledger = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
events = Path(events_path)
if mode == "timeout":
    scheduler.checkpoint_invocation(
        batch,
        ledger,
        output_root / "ledger.json",
        request["invocationId"],
        time.monotonic() - request["startedMonotonicSeconds"],
    )
    secret = output_root / "attempts/001-timeout/workspace/secret.txt"
    secret.parent.mkdir(parents=True)
    secret.write_text("transient credential", encoding="utf-8")
    events.write_text("checkpoint\\n", encoding="utf-8")
    time.sleep(60)
    raise SystemExit(0)
events.write_text("auth-close\\n", encoding="utf-8")
completeness = "incomplete" if mode == "incomplete" else "complete"
print(json.dumps({"batchId": batch["batchId"], "completeness": completeness}), flush=True)
with events.open("a", encoding="utf-8") as stream:
    stream.write("summary\\n")
scheduler.checkpoint_invocation(
    batch,
    ledger,
    output_root / "ledger.json",
    request["invocationId"],
    time.monotonic() - request["startedMonotonicSeconds"],
)
with events.open("a", encoding="utf-8") as stream:
    stream.write("checkpoint\\n")
if mode == "incomplete":
    secret = output_root / "attempts/001-incomplete/workspace/secret.txt"
    secret.parent.mkdir(parents=True)
    secret.write_text("transient credential", encoding="utf-8")
    raise SystemExit(75)
""".strip()
            + "\n",
            encoding="utf-8",
        )
        return script

    def test_initial_load_and_auth_failures_purge_untrusted_attempts(self):
        for stage in ("load", "auth"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory(
                prefix=f"agentic-active-{stage}-", dir=self.root / ".tmp"
            ) as value:
                output_root = Path(value)
                leaked = output_root / "attempts/001-old/workspace/secret.txt"
                leaked.parent.mkdir(parents=True)
                leaked.write_text("old credential", encoding="utf-8")
                failure = SystemExit(f"private {stage} failure")
                frozen = self.frozen_auth()
                runner = self.runner(output_root, frozen_batch(), initial_ledger(), frozen)
                if stage == "load":
                    runner.load_batch_and_ledger.side_effect = failure
                else:
                    runner.freeze_auth_file.side_effect = failure

                def purge(request: dict, _seconds: float) -> None:
                    benchmark_runner.remove_tmp_artifact_entry(Path(request["treeRoot"]), self.root)

                with mock.patch.object(active_run, "supervise_confidential_cleanup", side_effect=purge):
                    with self.assertRaises(SystemExit) as caught:
                        active_run.run_active(
                            runner,
                            argparse.Namespace(output_root=output_root, auth_file=Path("/private/auth")),
                        )
                self.assertIs(caught.exception, failure)
                self.assertFalse((output_root / "attempts").exists())
                frozen.close.assert_not_called()

    def test_missing_opt_in_starts_no_worker_and_deletes_nothing(self):
        with tempfile.TemporaryDirectory(prefix="agentic-active-opt-in-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            completed = output_root / "attempts/001-complete/result.json"
            completed.parent.mkdir(parents=True)
            completed.write_text('{"status":"valid"}', encoding="utf-8")
            frozen = self.frozen_auth()
            runner = self.runner(output_root, frozen_batch(), initial_ledger(), frozen)
            runner.require_execution_opt_in.side_effect = SystemExit("missing opt-in")
            with mock.patch.object(active_run, "supervise_confidential_cleanup") as cleanup, mock.patch.object(
                active_run, "supervise_stage"
            ) as stage:
                with self.assertRaises(SystemExit):
                    active_run.run_active(
                        runner,
                        argparse.Namespace(output_root=output_root, auth_file=Path("/safe/auth")),
                    )
            self.assertEqual(completed.read_text(encoding="utf-8"), '{"status":"valid"}')
            cleanup.assert_not_called()
            stage.assert_not_called()
            runner.freeze_auth_file.assert_not_called()
            frozen.close.assert_not_called()

    def test_initial_harness_and_proxy_drift_purge_attempts_and_close_auth(self):
        for stage in ("harness", "proxy"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory(
                prefix=f"agentic-active-{stage}-", dir=self.root / ".tmp"
            ) as value:
                output_root = Path(value)
                leaked = output_root / "attempts/001-old/workspace/secret.txt"
                leaked.parent.mkdir(parents=True)
                leaked.write_text("old credential", encoding="utf-8")
                frozen = self.frozen_auth()
                runner = self.runner(output_root, frozen_batch(), initial_ledger(), frozen)
                failure = SystemExit(f"{stage} drift")

                def execute_stage(_batch, _ledger, _path, _name, maximum, callback):
                    return callback(maximum)

                def fail_setup(_operation, _request, _seconds, cleanup):
                    cleanup(0.2, True)
                    raise failure

                def cleanup(request: dict, _seconds: float) -> None:
                    if request["mode"] == "purge-untrusted":
                        benchmark_runner.remove_tmp_artifact_entry(Path(request["treeRoot"]), self.root)

                runner.agentic_benchmark_scheduler.execute_budgeted_stage.side_effect = execute_stage
                with mock.patch.object(active_run, "supervise_stage", side_effect=fail_setup), mock.patch.object(
                    active_run, "supervise_confidential_cleanup", side_effect=cleanup
                ):
                    with self.assertRaises(SystemExit) as caught:
                        active_run.run_active(
                            runner,
                            argparse.Namespace(output_root=output_root, auth_file=Path("/safe/auth")),
                        )
                self.assertIs(caught.exception, failure)
                self.assertFalse((output_root / "attempts").exists())
                frozen.close.assert_called_once_with()

    def test_setup_failure_attempts_both_derived_tree_cleanups_before_failing_closed(self):
        for failed_mode in ("purge-untrusted", "stage"):
            with self.subTest(failed_mode=failed_mode), tempfile.TemporaryDirectory(
                prefix=f"agentic-active-cleanup-{failed_mode}-", dir=self.root / ".tmp"
            ) as value:
                output_root = Path(value)
                frozen = self.frozen_auth()
                runner = self.runner(output_root, frozen_batch(), initial_ledger(), frozen)
                calls: list[str] = []

                def execute_stage(_batch, _ledger, _path, _name, maximum, callback):
                    return callback(maximum)

                def fail_setup(_operation, _request, _seconds, cleanup):
                    cleanup(0.2, True)
                    raise AssertionError("cleanup failure must replace the private setup error")

                def cleanup(request: dict, _seconds: float) -> None:
                    calls.append(request["mode"])
                    if request["mode"] == failed_mode:
                        raise SystemExit("private cleanup detail")

                runner.agentic_benchmark_scheduler.execute_budgeted_stage.side_effect = execute_stage
                with mock.patch.object(active_run, "supervise_stage", side_effect=fail_setup), mock.patch.object(
                    active_run, "supervise_confidential_cleanup", side_effect=cleanup
                ):
                    with self.assertRaises(SystemExit) as caught:
                        active_run.run_active(
                            runner,
                            argparse.Namespace(output_root=output_root, auth_file=Path("/safe/auth")),
                        )
                self.assertEqual(str(caught.exception), "benchmark isolation setup cleanup failed")
                self.assertEqual(calls, ["purge-untrusted", "stage"])
                frozen.close.assert_called_once_with()

    def test_control_files_reject_fifo_symlink_and_oversize_without_blocking(self):
        with tempfile.TemporaryDirectory(prefix="agentic-control-files-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            target = output_root / "target.json"
            target.write_text("{}", encoding="utf-8")
            cases = ("fifo", "symlink", "oversize")
            for case in cases:
                with self.subTest(case=case):
                    batch_path = output_root / "batch.json"
                    if batch_path.exists() or batch_path.is_symlink():
                        batch_path.unlink()
                    if case == "fifo":
                        os.mkfifo(batch_path)
                    elif case == "symlink":
                        batch_path.symlink_to(target)
                    else:
                        with batch_path.open("wb") as stream:
                            stream.truncate(benchmark_runner.MAX_CONTROL_FILE_BYTES + 1)
                    started = time.monotonic()
                    with self.assertRaises(SystemExit):
                        benchmark_runner.load_batch_and_ledger(output_root)
                    self.assertLess(time.monotonic() - started, 0.2)

    def test_cpu_load_keeps_actual_setup_timeout_return_inside_profile_wall(self):
        wall_seconds = 1.2
        with tempfile.TemporaryDirectory(prefix="agentic-active-deadline-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            frozen = self.frozen_auth()
            runner = self.runner(output_root, frozen_batch(wall_seconds), initial_ledger(), frozen)

            def execute_stage(_batch, _ledger, _path, _name, maximum, callback):
                return callback(maximum)

            def hanging_operation(_operation: str, _request: dict, seconds: float):
                outcome = process_supervisor.supervise_process(
                    [sys.executable, "-c", "import time; time.sleep(60)"],
                    "{}",
                    seconds,
                )
                if outcome["timedOut"]:
                    raise SystemExit("setup timed out")
                return {}

            runner.agentic_benchmark_scheduler.execute_budgeted_stage.side_effect = execute_stage
            burners = [
                subprocess.Popen(
                    [sys.executable, "-c", "while True: pass"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                for _ in range(2)
            ]
            started = time.monotonic()
            try:
                with mock.patch.object(
                    process_supervisor, "supervise_operation", side_effect=hanging_operation
                ), mock.patch.object(active_run, "supervise_confidential_cleanup", return_value=None):
                    with self.assertRaises(SystemExit):
                        active_run.run_active(
                            runner,
                            argparse.Namespace(output_root=output_root, auth_file=Path("/safe/auth")),
                        )
            finally:
                for burner in burners:
                    try:
                        os.killpg(burner.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    burner.wait(timeout=2)
            self.assertLess(time.monotonic() - started, wall_seconds)
            frozen.close.assert_called_once_with()

    def test_real_outer_timeout_keeps_reservation_and_next_reserve_consumes_it(self):
        wall_seconds = 0.5
        with tempfile.TemporaryDirectory(prefix="agentic-outer-timeout-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            batch, _ledger = self.prepare_short_batch(output_root, wall_seconds)
            worker = self.write_outer_worker(output_root)
            events = output_root / "events.txt"
            args = argparse.Namespace(output_root=output_root, auth_file=output_root / "unused-auth.json")
            command = [sys.executable, str(worker), "timeout", str(Path(__file__).resolve().parent), str(events)]
            started = time.monotonic()
            with mock.patch.dict(os.environ, {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"}), mock.patch.object(
                active_run, "_active_worker_command", return_value=command
            ), self.assertRaises(SystemExit):
                active_run.run_supervised(args)
            elapsed = time.monotonic() - started
            self.assertLessEqual(elapsed, wall_seconds + 0.05)
            persisted = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertIn("activeInvocation", persisted)
            self.assertEqual(events.read_text(encoding="utf-8").splitlines(), ["checkpoint"])
            self.assertFalse((output_root / "attempts").exists())
            with self.assertRaises(SystemExit) as caught:
                process_supervisor._execute_reserve_invocation(
                    benchmark_runner,
                    {
                        "root": str(self.root),
                        "outputRoot": str(output_root),
                        "invocationId": "replacement",
                        "timeoutSeconds": wall_seconds,
                    },
                )
            recovered = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertIn("new batch", str(caught.exception))
            self.assertNotIn("activeInvocation", recovered)
            self.assertEqual(recovered["cumulativeWallSeconds"], batch["wallClockBudgetSeconds"])

    def test_real_outer_success_settles_after_close_and_summary_with_total_elapsed(self):
        wall_seconds = 1.0
        with tempfile.TemporaryDirectory(prefix="agentic-outer-success-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            self.prepare_short_batch(output_root, wall_seconds)
            worker = self.write_outer_worker(output_root)
            events = output_root / "events.txt"
            args = argparse.Namespace(output_root=output_root, auth_file=output_root / "unused-auth.json")
            command = [sys.executable, str(worker), "success", str(Path(__file__).resolve().parent), str(events)]
            started = time.monotonic()
            with mock.patch.dict(os.environ, {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"}), mock.patch.object(
                active_run, "_active_worker_command", return_value=command
            ):
                active_run.run_supervised(args)
            outer_elapsed = time.monotonic() - started
            persisted = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(events.read_text(encoding="utf-8").splitlines(), ["auth-close", "summary", "checkpoint"])
            self.assertNotIn("activeInvocation", persisted)
            self.assertGreater(persisted["cumulativeWallSeconds"], 0)
            self.assertLessEqual(abs(persisted["cumulativeWallSeconds"] - outer_elapsed), 0.08)

    def test_active_worker_logic_closes_and_prints_then_checkpoints_without_settlement(self):
        wall_seconds = 1.0
        with tempfile.TemporaryDirectory(prefix="agentic-worker-settle-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            batch = frozen_batch(wall_seconds)
            ledger = initial_ledger()
            ledger["activeInvocation"] = {
                "invocationId": "invocation-1",
                "preInvocationCumulativeWallSeconds": 0.0,
                "reservedWallSeconds": wall_seconds,
            }
            events: list[str] = []
            frozen = self.frozen_auth()
            frozen.close.side_effect = lambda: events.append("auth-close")

            def execute_stage(_batch, _ledger, _path, stage, _maximum, _callback):
                if stage == "isolation-and-setup":
                    return {"authFile": "/proc/self/fd/9", "bwrap": "/safe/bwrap", "codex": "/safe/codex"}
                if stage == "provider-preflight":
                    return {"status": "ready"}
                if stage == "finalize":
                    return {"batchId": "fake", "attempts": {}, "completeness": "complete"}
                self.fail(f"unexpected stage {stage}")

            def checkpoint(*args):
                scheduler_owner.checkpoint_invocation(*args)
                events.append("checkpoint")

            scheduler = SimpleNamespace(
                validate_ledger=scheduler_owner.validate_ledger,
                checkpoint_invocation=checkpoint,
                settle_invocation=lambda *_args: self.fail("active child must never settle its reservation"),
                execute_budgeted_stage=execute_stage,
                execute_schedule=lambda *_args: None,
            )
            runner = self.runner(output_root, batch, ledger, frozen)
            runner.agentic_benchmark_scheduler = scheduler
            started = time.monotonic() - 0.05
            with mock.patch("builtins.print", side_effect=lambda *_args, **_kwargs: events.append("summary")):
                active_run.run_active(
                    runner,
                    argparse.Namespace(output_root=output_root, auth_file=Path("/safe/auth")),
                    invocation_id="invocation-1",
                    started_monotonic_seconds=started,
                    reserved_wall_seconds=wall_seconds,
                )
            persisted = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(events[-3:], ["auth-close", "summary", "checkpoint"])
            self.assertIn("activeInvocation", persisted)
            self.assertGreaterEqual(persisted["cumulativeWallSeconds"], 0.05)

    def test_bootstrap_prior_cumulative_tightens_reservation_deadline(self):
        wall_seconds = 0.1
        with tempfile.TemporaryDirectory(prefix="agentic-outer-prior-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            self.prepare_short_batch(output_root, wall_seconds, cumulative=0.05)
            args = argparse.Namespace(output_root=output_root, auth_file=output_root / "unused-auth.json")
            captured: list[float] = []

            def reserve(_operation: str, _request: dict, timeout_seconds: float):
                captured.append(timeout_seconds)
                outcome = process_supervisor.supervise_process(
                    [sys.executable, "-c", "import time; time.sleep(60)"],
                    "{}",
                    timeout_seconds,
                )
                self.assertTrue(outcome["timedOut"])
                raise SystemExit("simulated slow reservation control")

            started = time.monotonic()
            with mock.patch.dict(os.environ, {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"}), mock.patch.object(
                active_run, "supervise_operation", side_effect=reserve
            ), self.assertRaises(SystemExit):
                active_run.run_supervised(args)
            self.assertLess(captured[0], wall_seconds - 0.05)
            self.assertLessEqual(time.monotonic() - started, wall_seconds)

    def test_incomplete_exit_75_keeps_reservation_and_purges_attempt_secrets(self):
        with tempfile.TemporaryDirectory(prefix="agentic-outer-incomplete-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            self.prepare_short_batch(output_root, 1.0)
            worker = self.write_outer_worker(output_root)
            events = output_root / "events.txt"
            args = argparse.Namespace(output_root=output_root, auth_file=output_root / "unused-auth.json")
            command = [sys.executable, str(worker), "incomplete", str(Path(__file__).resolve().parent), str(events)]
            with mock.patch.dict(os.environ, {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"}), mock.patch.object(
                active_run, "_active_worker_command", return_value=command
            ), self.assertRaises(SystemExit) as caught:
                active_run.run_supervised(args)
            self.assertEqual(caught.exception.code, 75)
            persisted = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertIn("activeInvocation", persisted)
            self.assertFalse((output_root / "attempts").exists())

    def test_cleanup_failure_returns_safe_error_without_settling_reservation(self):
        with tempfile.TemporaryDirectory(prefix="agentic-outer-cleanup-fail-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            self.prepare_short_batch(output_root, 0.5)
            worker = self.write_outer_worker(output_root)
            events = output_root / "events.txt"
            args = argparse.Namespace(output_root=output_root, auth_file=output_root / "unused-auth.json")
            command = [sys.executable, str(worker), "timeout", str(Path(__file__).resolve().parent), str(events)]
            with mock.patch.dict(os.environ, {"AEGIS_AGENTIC_BENCHMARK_LIVE": "1"}), mock.patch.object(
                active_run, "_active_worker_command", return_value=command
            ), mock.patch.object(
                active_run, "supervise_confidential_cleanup", side_effect=SystemExit("private cleanup detail")
            ), self.assertRaises(SystemExit) as caught:
                active_run.run_supervised(args)
            self.assertEqual(str(caught.exception), "benchmark active invocation cleanup failed")
            persisted = json.loads((output_root / "ledger.json").read_text(encoding="utf-8"))
            self.assertIn("activeInvocation", persisted)
            self.assertTrue((output_root / "attempts/001-timeout/workspace/secret.txt").exists())
            with self.assertRaises(SystemExit) as replacement:
                process_supervisor._execute_reserve_invocation(
                    benchmark_runner,
                    {
                        "root": str(self.root),
                        "outputRoot": str(output_root),
                        "invocationId": "replacement-after-cleanup-failure",
                        "timeoutSeconds": 0.5,
                    },
                )
            self.assertIn("new batch", str(replacement.exception))
            self.assertFalse((output_root / "attempts").exists())


if __name__ == "__main__":
    unittest.main()
