#!/usr/bin/env python3
"""Adversarial local-process tests for the benchmark supervisor."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agentic_benchmark_process_supervisor
from agentic_benchmark_process_supervisor import MAX_RESULT_BYTES, supervise_attempt, supervise_confidential_cleanup, supervise_operation, supervise_process, supervise_stage
from agentic_benchmark_scheduler import execute_budgeted_stage
from agentic_benchmark_provider_preflight import freeze_auth_file
from agentic_benchmark_isolation import remove_tmp_artifact_entry


def fake_batch(wall: float = 1.0) -> dict:
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
        "profileId": "fake",
        "workers": 2,
        "wallClockBudgetSeconds": wall,
        "perAttemptTimeoutSeconds": wall,
        "infrastructureFailureLimit": 2,
        "maxAttempts": 2,
        "schedule": targets,
    }


class ProcessSupervisorTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        (self.root / ".tmp").mkdir(exist_ok=True)

    def _hang_script(self, directory: Path) -> Path:
        script = directory / "hang-worker.py"
        script.write_text(
            """
import os
import signal
import sys
import time
from pathlib import Path

phase, pid_path = sys.argv[1:]
child = os.fork()
if child == 0:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    while True:
        time.sleep(60)
Path(pid_path).write_text(str(child), encoding='utf-8')
signal.signal(signal.SIGTERM, signal.SIG_IGN)
sys.stdin.read()
while True:
    time.sleep(60)
""".strip()
            + "\n",
            encoding="utf-8",
        )
        return script

    def _assert_process_gone(self, pid: int) -> None:
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.02)
        self.fail(f"supervised descendant {pid} survived timeout cleanup")

    def test_parse_score_and_cleanup_hangs_are_cut_off_without_orphans(self):
        with tempfile.TemporaryDirectory(prefix="agentic-supervisor-hang-", dir=self.root / ".tmp") as value:
            directory = Path(value)
            script = self._hang_script(directory)
            for phase in ("parse", "score", "cleanup"):
                with self.subTest(phase=phase):
                    pid_path = directory / f"{phase}.pid"
                    started = time.monotonic()
                    outcome = supervise_process(
                        [sys.executable, str(script), phase, str(pid_path)],
                        json.dumps({"phase": phase}),
                        0.4,
                    )
                    elapsed = time.monotonic() - started
                    self.assertTrue(outcome["timedOut"])
                    self.assertLessEqual(elapsed, 0.55)
                    self.assertTrue(pid_path.is_file())
                    self._assert_process_gone(int(pid_path.read_text(encoding="utf-8")))

    def test_real_hanging_setup_callback_is_bounded_and_charged(self):
        with tempfile.TemporaryDirectory(prefix="agentic-supervisor-stage-", dir=self.root / ".tmp") as value:
            directory = Path(value)
            script = self._hang_script(directory)
            ledger_path = directory / "ledger.json"
            ledger = {"cumulativeWallSeconds": 0.0, "attempts": []}

            def stage(remaining: float) -> None:
                persisted = json.loads(ledger_path.read_text(encoding="utf-8"))
                self.assertEqual(persisted["cumulativeWallSeconds"], 0.5)
                outcome = supervise_process(
                    [sys.executable, str(script), "setup", str(directory / "setup.pid")],
                    "{}",
                    remaining,
                )
                self.assertTrue(outcome["timedOut"])
                raise SystemExit("setup timed out")

            started = time.monotonic()
            with self.assertRaises(SystemExit):
                execute_budgeted_stage(fake_batch(0.5), ledger, ledger_path, "setup", 0.5, stage)
            self.assertLessEqual(time.monotonic() - started, 0.65)
            self.assertLessEqual(ledger["cumulativeWallSeconds"], 0.5)
            self.assertNotIn("activeBudgetStage", ledger)
            self._assert_process_gone(int((directory / "setup.pid").read_text(encoding="utf-8")))

    def test_worker_result_output_is_capped(self):
        command = [sys.executable, "-c", f"import sys; sys.stdin.read(); print('x' * {MAX_RESULT_BYTES + 1})"]
        outcome = supervise_process(command, "{}", 1.0)
        self.assertFalse(outcome["timedOut"])
        self.assertTrue(outcome["outputExceeded"])
        self.assertEqual(outcome["stdout"], "")

    def test_parent_timeout_cleanup_promotes_residual_credential_exposure(self):
        cleanup_calls = 0

        cleanup_budget = 0.0

        def cleanup(seconds: float, uncertain: bool) -> str:
            nonlocal cleanup_calls
            nonlocal cleanup_budget
            cleanup_calls += 1
            cleanup_budget = seconds
            self.assertTrue(uncertain)
            return "credential-exposure"

        outcome = {
            "returncode": -9,
            "stdout": "",
            "elapsedSeconds": 0.5,
            "timedOut": True,
            "outputExceeded": False,
        }
        with mock.patch.object(agentic_benchmark_process_supervisor, "supervise_process", return_value=outcome):
            result = supervise_attempt({"safe": True}, 1.0, cleanup)
        self.assertEqual(cleanup_calls, 1)
        self.assertGreater(cleanup_budget, 0)
        self.assertLessEqual(cleanup_budget, 1 / 3)
        self.assertEqual(result, {"status": "invalid", "invalidReason": "credential-exposure", "elapsedSeconds": 0.5})

    def test_attempt_base_exceptions_always_run_bounded_cleanup_then_reraise(self):
        for error in (OSError("spawn failed"), SystemExit("worker failed")):
            cleanup_calls: list[tuple[float, bool]] = []

            def cleanup(seconds: float, uncertain: bool) -> None:
                cleanup_calls.append((seconds, uncertain))

            with self.subTest(error=type(error).__name__), mock.patch.object(
                agentic_benchmark_process_supervisor, "supervise_operation", side_effect=error
            ):
                with self.assertRaises(type(error)) as caught:
                    supervise_attempt({}, 0.9, cleanup)
            self.assertIs(caught.exception, error)
            self.assertEqual(len(cleanup_calls), 1)
            self.assertTrue(cleanup_calls[0][1])
            self.assertGreater(cleanup_calls[0][0], 0)
            self.assertLessEqual(cleanup_calls[0][0], 0.3)

    def test_attempt_cleanup_failure_has_security_priority_without_exception_chaining(self):
        operation_error = OSError("private spawn detail")
        cleanup_error = SystemExit("benchmark attempt artifact cleanup failed")

        def cleanup(_seconds: float, _uncertain: bool) -> None:
            raise cleanup_error

        with mock.patch.object(agentic_benchmark_process_supervisor, "supervise_operation", side_effect=operation_error):
            with self.assertRaises(SystemExit) as caught:
                supervise_attempt({}, 0.9, cleanup)
        self.assertIs(caught.exception, cleanup_error)
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn("private spawn detail", str(caught.exception))

    def test_stage_cleanup_runs_after_success_and_crash_with_a_reserved_deadline(self):
        for label, side_effect in (("success", None), ("crash", SystemExit("worker crashed"))):
            cleanup_budgets: list[float] = []

            def cleanup(seconds: float) -> None:
                cleanup_budgets.append(seconds)

            with self.subTest(label=label), mock.patch.object(
                agentic_benchmark_process_supervisor,
                "supervise_operation",
                return_value={"status": "ready"} if side_effect is None else mock.DEFAULT,
                side_effect=side_effect,
            ):
                if side_effect is None:
                    result = supervise_stage("provider-preflight", {}, 0.9, cleanup)
                    self.assertEqual(result, {"status": "ready"})
                else:
                    with self.assertRaises(SystemExit):
                        supervise_stage("provider-preflight", {}, 0.9, cleanup)
            self.assertEqual(len(cleanup_budgets), 1)
            self.assertGreater(cleanup_budgets[0], 0)
            self.assertLessEqual(cleanup_budgets[0], 0.3)

    def test_credential_markers_use_worker_stdin_and_never_argv_or_result(self):
        secret = "private-refresh-token-value"
        captured: dict[str, object] = {}

        def fake_supervise(command: list[str], payload: str, timeout_seconds: float, *, pass_fds: tuple[int, ...] = ()) -> dict:
            captured.update(command=command, payload=payload, timeout=timeout_seconds, pass_fds=pass_fds)
            return {
                "returncode": 0,
                "stdout": '{"status":"valid","contractPass":true}',
                "elapsedSeconds": 0.1,
                "timedOut": False,
                "outputExceeded": False,
            }

        auth_fd = os.memfd_create("test-auth")
        try:
            with mock.patch.object(agentic_benchmark_process_supervisor, "supervise_process", side_effect=fake_supervise):
                result = supervise_operation(
                    "attempt",
                    {"authFd": auth_fd, "authFile": f"/proc/self/fd/{auth_fd}", "credentialMarkers": [secret]},
                    1.0,
                )
        finally:
            os.close(auth_fd)
        self.assertNotIn(secret, " ".join(captured["command"]))  # type: ignore[arg-type]
        self.assertIn(secret, captured["payload"])  # type: ignore[operator]
        self.assertEqual(captured["pass_fds"], (auth_fd,))
        self.assertNotIn(secret, json.dumps(result, sort_keys=True))

    def test_real_cleanup_worker_deletes_stage_but_preserves_sanitized_sibling_report(self):
        with tempfile.TemporaryDirectory(prefix="agentic-stage-cleanup-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            auth = output_root / "auth.json"
            auth.write_text('{"OPENAI_API_KEY":"abc"}', encoding="utf-8")
            auth.chmod(0o600)
            report = output_root / "isolation-report.json"
            report.write_text('{"status":"safe"}', encoding="utf-8")
            frozen = freeze_auth_file(auth)
            try:
                for name, payload, expected in (
                    ("isolation-audit", "safe", None),
                    ("provider-preflight-isolated", "copied abc credential", "credential-exposure"),
                ):
                    stage_root = output_root / name
                    stage_root.mkdir()
                    (stage_root / "result.txt").write_text(payload, encoding="utf-8")
                    exposure = supervise_confidential_cleanup(
                        {
                            "root": str(self.root),
                            "treeRoot": str(stage_root),
                            "mode": "stage",
                            "authGuard": frozen.drift_guard(),
                            "credentialMarkers": list(frozen.credential_policy.in_memory_markers()),
                        },
                        1.0,
                    )
                    self.assertEqual(exposure, expected)
                    self.assertFalse(stage_root.exists())
                    self.assertEqual(report.read_text(encoding="utf-8"), '{"status":"safe"}')
                attempt_root = output_root / "attempts/001-auth-drift"
                attempt_root.mkdir(parents=True)
                (attempt_root / "result.txt").write_text("safe", encoding="utf-8")
                auth.write_text('{"OPENAI_API_KEY":"rotated"}', encoding="utf-8")
                exposure = supervise_confidential_cleanup(
                    {
                        "root": str(self.root),
                        "treeRoot": str(attempt_root),
                        "mode": "auth-check",
                        "authGuard": frozen.drift_guard(),
                        "credentialMarkers": list(frozen.credential_policy.in_memory_markers()),
                    },
                    1.0,
                )
                self.assertEqual(exposure, "auth-drift")
                self.assertFalse(attempt_root.exists())
            finally:
                frozen.close()

    def test_purge_untrusted_deletes_only_the_attempt_tree_without_auth_context(self):
        with tempfile.TemporaryDirectory(prefix="agentic-purge-untrusted-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            attempts_root = output_root / "attempts"
            leaked = attempts_root / "001-unknown/workspace/secret.txt"
            leaked.parent.mkdir(parents=True)
            leaked.write_text("unknown prior credential", encoding="utf-8")
            batch = output_root / "batch.json"
            batch.write_text('{"trusted":"sibling"}', encoding="utf-8")
            exposure = supervise_confidential_cleanup(
                {"root": str(self.root), "treeRoot": str(attempts_root), "mode": "purge-untrusted"},
                1.0,
            )
            self.assertIsNone(exposure)
            self.assertFalse(attempts_root.exists())
            self.assertEqual(batch.read_text(encoding="utf-8"), '{"trusted":"sibling"}')

    def test_unverifiable_ledger_deletes_the_entire_untrusted_attempt_tree(self):
        with tempfile.TemporaryDirectory(prefix="agentic-untrusted-ledger-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            attempts_root = output_root / "attempts"
            leaked = attempts_root / "001-unknown/workspace/secret.txt"
            leaked.parent.mkdir(parents=True)
            leaked.write_text("old unknown credential", encoding="utf-8")
            runner = SimpleNamespace(
                repo_root=lambda: self.root,
                resolve_tmp_child=lambda _root, path, _label: path,
                verify_batch=lambda *_args: object(),
                validate_auth_mount_file=lambda _path: None,
                credential_policy_from_markers=lambda _markers: object(),
                load_batch_and_ledger=mock.Mock(side_effect=SystemExit("ledger invalid")),
                remove_tmp_artifact_entry=lambda path, root: remove_tmp_artifact_entry(path, root),
            )
            request = {
                "root": str(self.root),
                "outputRoot": str(output_root),
                "batch": {},
                "authFile": "/safe/auth",
                "credentialMarkers": [],
            }
            with self.assertRaises(SystemExit) as caught:
                agentic_benchmark_process_supervisor._execute_isolation_setup(runner, request)
            self.assertEqual(str(caught.exception), "ledger invalid")
            self.assertFalse(attempts_root.exists())

    def test_setup_retention_whitelist_excludes_launched_and_recovered_attempts(self):
        with tempfile.TemporaryDirectory(prefix="agentic-ledger-whitelist-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            batch: dict = {}
            ledger = {
                "attempts": [
                    {"attemptNumber": 1, "targetId": "valid", "status": "valid"},
                    {"attemptNumber": 2, "targetId": "invalid", "status": "invalid"},
                    {"attemptNumber": 3, "targetId": "recovered", "status": "invalid", "recovery": "interrupted-before-final-record"},
                    {"attemptNumber": 4, "targetId": "launched", "status": "launched"},
                ]
            }
            captured: list[set[str]] = []

            def capture(_root, completed, *_args):
                captured.append(completed)
                raise SystemExit("captured")

            runner = SimpleNamespace(
                repo_root=lambda: self.root,
                resolve_tmp_child=lambda _root, path, _label: path,
                verify_batch=lambda *_args: object(),
                validate_auth_mount_file=lambda _path: None,
                credential_policy_from_markers=lambda _markers: object(),
                load_batch_and_ledger=lambda _root: (batch, ledger),
                agentic_benchmark_scheduler=SimpleNamespace(validate_ledger=lambda *_args: None),
                scrub_stale_confidential_artifacts=capture,
                remove_tmp_artifact_entry=lambda path, root: remove_tmp_artifact_entry(path, root),
            )
            request = {
                "root": str(self.root), "outputRoot": str(output_root), "batch": batch,
                "authFile": "/safe/auth", "credentialMarkers": [],
            }
            with self.assertRaises(SystemExit) as caught:
                agentic_benchmark_process_supervisor._execute_isolation_setup(runner, request)
            self.assertEqual(str(caught.exception), "captured")
            self.assertEqual(captured, [{"001-valid", "002-invalid"}])


if __name__ == "__main__":
    unittest.main()
