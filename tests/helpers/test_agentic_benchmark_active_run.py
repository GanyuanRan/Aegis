#!/usr/bin/env python3
"""Offline orchestration tests for the benchmark's absolute invocation deadline."""

from __future__ import annotations

import argparse
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


if __name__ == "__main__":
    unittest.main()
