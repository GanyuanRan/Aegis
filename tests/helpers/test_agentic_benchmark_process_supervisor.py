#!/usr/bin/env python3
"""Adversarial local-process tests for the benchmark supervisor."""

from __future__ import annotations

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

import agentic_benchmark_process_supervisor
from agentic_benchmark_process_supervisor import MAX_RESULT_BYTES, communicate_with_timeout, supervise_attempt, supervise_confidential_cleanup, supervise_operation, supervise_process, supervise_stage
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
    if phase == 'nested-new-session':
        os.setsid()
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    while True:
        time.sleep(60)
Path(pid_path).write_text(str(child), encoding='utf-8')
print('ready', flush=True)
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

    def test_nested_new_session_escape_is_observed_and_killed(self):
        with tempfile.TemporaryDirectory(prefix="agentic-supervisor-escape-", dir=self.root / ".tmp") as value:
            directory = Path(value)
            pid_path = directory / "escape.pid"
            started = time.monotonic()
            outcome = supervise_process(
                [sys.executable, str(self._hang_script(directory)), "nested-new-session", str(pid_path)],
                "{}",
                0.5,
            )
            self.assertLess(time.monotonic() - started, 0.5)
            self.assertTrue(outcome["timedOut"])
            self._assert_process_gone(int(pid_path.read_text(encoding="utf-8")))

    def test_immediate_leader_exit_cannot_escape_subreaper_containment_in_80_trials(self):
        script = """
import os
import signal
import sys
import time

child = os.fork()
if child == 0:
    os.setsid()
    sink = os.open(os.devnull, os.O_RDWR)
    for descriptor in (0, 1, 2):
        os.dup2(sink, descriptor)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    with open(sys.argv[1], "w", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    while True:
        time.sleep(60)
os._exit(0)
"""
        with tempfile.TemporaryDirectory(prefix="agentic-immediate-exit-", dir=self.root / ".tmp") as value:
            directory = Path(value)
            for trial in range(80):
                pid_path = directory / f"{trial}.pid"
                pid: int | None = None
                try:
                    outcome = supervise_process(
                        [sys.executable, "-c", script, str(pid_path)],
                        "{}",
                        0.2,
                    )
                    deadline = time.monotonic() + 0.2
                    while (not pid_path.exists() or not pid_path.read_text(encoding="utf-8")) and time.monotonic() < deadline:
                        time.sleep(0.001)
                    self.assertTrue(pid_path.exists() and pid_path.read_text(encoding="utf-8"), f"trial {trial} did not publish its child pid")
                    pid = int(pid_path.read_text(encoding="utf-8"))
                    self.assertTrue(outcome["timedOut"], f"trial {trial} returned before its adopted child exited")
                    self._assert_process_gone(pid)
                finally:
                    if pid is not None:
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

    def test_live_worker_can_wait_for_an_adopted_zombie_to_be_reaped(self):
        script = """
import os
import signal
import sys
import time

pid_read, pid_write = os.pipe()
release_read, release_write = os.pipe()
intermediate = os.fork()
if intermediate == 0:
    os.close(pid_read)
    os.close(release_write)
    leaf = os.fork()
    if leaf == 0:
        os.close(pid_write)
        os.read(release_read, 1)
        os._exit(0)
    os.close(release_read)
    os.write(pid_write, str(leaf).encode())
    os.close(pid_write)
    os._exit(0)

os.close(pid_write)
os.close(release_read)
leaf = int(os.read(pid_read, 32))
os.close(pid_read)
os.waitpid(intermediate, 0)
leaf_pidfd = os.pidfd_open(leaf)
with open(sys.argv[1], 'w', encoding='utf-8') as stream:
    stream.write(str(leaf))
os.write(release_write, b'x')
os.close(release_write)
deadline = time.monotonic() + 2
while time.monotonic() < deadline:
    try:
        signal.pidfd_send_signal(leaf_pidfd, 0)
    except ProcessLookupError:
        os.close(leaf_pidfd)
        raise SystemExit(0)
    time.sleep(0.002)
os.close(leaf_pidfd)
raise SystemExit(9)
"""
        with tempfile.TemporaryDirectory(prefix="agentic-adopted-zombie-", dir=self.root / ".tmp") as value:
            pid_path = Path(value) / "leaf.pid"
            started = time.monotonic()
            outcome = supervise_process(
                [sys.executable, "-c", script, str(pid_path)],
                "{}",
                0.5,
            )
            self.assertFalse(outcome["timedOut"])
            self.assertEqual(outcome["returncode"], 0)
            self.assertLess(time.monotonic() - started, 0.5)
            self.assertTrue(pid_path.is_file())
            self._assert_process_gone(int(pid_path.read_text(encoding="utf-8")))

    def test_reap_exempts_the_worker_pid_only_until_poll_reaps_that_worker(self):
        command_fd = agentic_benchmark_process_supervisor._sealed_memfd(
            "test-containment-command",
            json.dumps({"command": ["fake-worker"], "passFds": []}).encode(),
        )
        child = SimpleNamespace(pid=42, poll=mock.Mock(side_effect=[None, 0]))
        try:
            with mock.patch.object(agentic_benchmark_process_supervisor, "_enable_child_subreaper"), mock.patch.object(
                agentic_benchmark_process_supervisor.subprocess,
                "Popen",
                return_value=child,
            ), mock.patch.object(
                agentic_benchmark_process_supervisor.signal,
                "signal",
            ), mock.patch.object(
                agentic_benchmark_process_supervisor,
                "_direct_child_pids",
                side_effect=[{42, 99}, {42}],
            ), mock.patch.object(
                agentic_benchmark_process_supervisor,
                "_descendant_pids",
                side_effect=[{42}, set(), set()],
            ), mock.patch.object(
                agentic_benchmark_process_supervisor.os,
                "waitpid",
            ) as waitpid, mock.patch.object(
                agentic_benchmark_process_supervisor.time,
                "sleep",
            ):
                result = agentic_benchmark_process_supervisor._contain_process(command_fd)
        finally:
            os.close(command_fd)
        self.assertEqual(result, 0)
        self.assertEqual(
            waitpid.call_args_list,
            [mock.call(99, os.WNOHANG), mock.call(42, os.WNOHANG)],
        )

    def test_monitor_exception_reaps_trampoline_and_immediate_exit_adoptee(self):
        script = """
import os
import signal
import sys
import time

child = os.fork()
if child == 0:
    os.setsid()
    sink = os.open(os.devnull, os.O_RDWR)
    for descriptor in (0, 1, 2):
        os.dup2(sink, descriptor)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    with open(sys.argv[1], "w", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    while True:
        time.sleep(60)
os._exit(0)
"""
        with tempfile.TemporaryDirectory(prefix="agentic-subreeaper-error-", dir=self.root / ".tmp") as value:
            directory = Path(value)
            pid_path = directory / "adoptee.pid"
            launched: list[subprocess.Popen[str]] = []
            real_popen = subprocess.Popen

            def capture_popen(*args, **kwargs):
                process = real_popen(*args, **kwargs)
                launched.append(process)
                return process

            def fail_after_adoption(_root: Path) -> bool:
                if pid_path.exists() and pid_path.read_text(encoding="utf-8"):
                    raise OSError("monitor failed")
                return False

            with mock.patch.object(agentic_benchmark_process_supervisor.subprocess, "Popen", side_effect=capture_popen), mock.patch.object(
                agentic_benchmark_process_supervisor, "artifact_limit_observed", side_effect=fail_after_adoption
            ), self.assertRaises(SystemExit) as caught:
                supervise_process(
                    [sys.executable, "-c", script, str(pid_path)],
                    "{}",
                    0.5,
                    artifact_root=directory,
                )
            self.assertEqual(str(caught.exception), "process supervision failed")
            self.assertTrue(pid_path.exists() and pid_path.read_text(encoding="utf-8"))
            self._assert_process_gone(int(pid_path.read_text(encoding="utf-8")))
            self.assertEqual(len(launched), 1)
            self.assertIsNotNone(launched[0].returncode)
            self._assert_process_gone(launched[0].pid)

    def test_capture_and_monitor_exceptions_sweep_children_and_close_pidfds(self):
        for failure_source in ("capture", "monitor"):
            with self.subTest(failure_source=failure_source), tempfile.TemporaryDirectory(
                prefix=f"agentic-supervisor-{failure_source}-", dir=self.root / ".tmp"
            ) as value:
                directory = Path(value)
                pid_path = directory / "child.pid"
                process = subprocess.Popen(
                    [sys.executable, str(self._hang_script(directory)), "nested-new-session", str(pid_path)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
                deadline = time.monotonic() + 1.0
                while not pid_path.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(pid_path.exists())
                opened_pidfds: list[int] = []
                real_pidfd_open = os.pidfd_open

                def track_pidfd(pid: int) -> int:
                    descriptor = real_pidfd_open(pid)
                    opened_pidfds.append(descriptor)
                    return descriptor

                patches = [mock.patch.object(agentic_benchmark_process_supervisor.os, "pidfd_open", side_effect=track_pidfd)]
                if failure_source == "capture":
                    patches.append(mock.patch.object(agentic_benchmark_process_supervisor.os, "read", side_effect=OSError("capture failed")))
                else:
                    patches.append(mock.patch.object(agentic_benchmark_process_supervisor, "artifact_limit_observed", side_effect=OSError("monitor failed")))
                started = time.monotonic()
                with patches[0], patches[1], self.assertRaises(SystemExit) as caught:
                    communicate_with_timeout(
                        process,
                        0.5,
                        artifact_root=directory if failure_source == "monitor" else None,
                    )
                self.assertEqual(str(caught.exception), "process supervision failed")
                self.assertLess(time.monotonic() - started, 0.5)
                self._assert_process_gone(int(pid_path.read_text(encoding="utf-8")))
                self.assertTrue(process.stdout.closed)
                self.assertTrue(process.stderr.closed)
                self.assertTrue(opened_pidfds)
                for descriptor in opened_pidfds:
                    with self.assertRaises(OSError):
                        os.fstat(descriptor)

    def test_terminal_worker_with_live_grandchild_is_timed_out_and_swept(self):
        with tempfile.TemporaryDirectory(prefix="agentic-supervisor-terminal-", dir=self.root / ".tmp") as value:
            pid_path = Path(value) / "grandchild.pid"
            script = """
import os
import signal
import sys
import time

child = os.fork()
if child == 0:
    os.setsid()
    sink = os.open(os.devnull, os.O_RDWR)
    for descriptor in (0, 1, 2):
        os.dup2(sink, descriptor)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(60)
else:
    with open(sys.argv[1], 'w', encoding='utf-8') as stream:
        stream.write(str(child))
    time.sleep(0.15)
"""
            outcome = supervise_process([sys.executable, "-c", script, str(pid_path)], "{}", 1.0)
            self.assertTrue(outcome["timedOut"])
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
        started = time.monotonic()
        outcome = supervise_process(command, "{}", 1.0)
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertFalse(outcome["timedOut"])
        self.assertTrue(outcome["outputExceeded"])
        self.assertEqual(outcome["stdout"], "")

    def test_legal_output_that_looks_like_an_old_sentinel_is_not_misclassified(self):
        text = "benchmark-output-limit-exceeded"
        outcome = supervise_process(
            [sys.executable, "-c", f"import sys; sys.stdin.read(); print({text!r})"],
            "{}",
            1.0,
        )
        self.assertEqual(outcome["returncode"], 0)
        self.assertFalse(outcome["timedOut"])
        self.assertFalse(outcome["outputExceeded"])
        self.assertEqual(outcome["stdout"].strip(), text)

    def test_stable_artifact_limit_observation_terminates_before_worker_completion(self):
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-growth-", dir=self.root / ".tmp") as value:
            artifact_root = Path(value) / "attempt"
            artifact_root.mkdir()
            script = (
                "import pathlib,sys,time; "
                "path=pathlib.Path(sys.argv[1]); "
                "path.write_bytes(b'x'*4096); "
                "time.sleep(60)"
            )
            started = time.monotonic()
            with mock.patch("agentic_benchmark_provider_preflight.MAX_ARTIFACT_FILE_BYTES", 1024), mock.patch(
                "agentic_benchmark_provider_preflight.MAX_ARTIFACT_TOTAL_BYTES", 1024
            ):
                outcome = supervise_process(
                    [sys.executable, "-c", script, str(artifact_root / "growing.bin")],
                    "{}",
                    1.0,
                    artifact_root=artifact_root,
                )
            self.assertLess(time.monotonic() - started, 1.0)
            self.assertTrue(outcome["artifactLimitObserved"])
            self.assertFalse(outcome["timedOut"])

    def test_sampled_artifact_monitor_does_not_claim_deleted_transient_peaks(self):
        with tempfile.TemporaryDirectory(prefix="agentic-artifact-transient-", dir=self.root / ".tmp") as value:
            artifact_root = Path(value)
            transient = artifact_root / "transient.bin"
            transient.write_bytes(b"x" * 4096)
            transient.unlink()
            with mock.patch("agentic_benchmark_provider_preflight.MAX_ARTIFACT_FILE_BYTES", 1024):
                self.assertFalse(agentic_benchmark_process_supervisor.artifact_limit_observed(artifact_root))

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
            cleanup_calls: list[tuple[float, bool]] = []

            def cleanup(seconds: float, uncertain: bool) -> None:
                cleanup_calls.append((seconds, uncertain))

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
            self.assertEqual(len(cleanup_calls), 1)
            self.assertGreater(cleanup_calls[0][0], 0)
            self.assertLessEqual(cleanup_calls[0][0], 0.3)
            self.assertEqual(cleanup_calls[0][1], side_effect is not None)

    def test_attempt_supervisor_maps_failures_to_stable_non_payload_error_types(self):
        private_detail = "PRIVATE_PROVIDER_DETAIL"
        base = {
            "returncode": 0,
            "stdout": '{"status":"valid","contractPass":true}',
            "elapsedSeconds": 0.125,
            "timedOut": False,
            "outputExceeded": False,
            "artifactLimitObserved": False,
        }
        for label, overrides, expected in (
            ("output", {"outputExceeded": True, "stdout": private_detail}, "supervisor-output-limit"),
            ("artifact", {"artifactLimitObserved": True}, "supervisor-artifact-limit"),
            ("worker-exit", {"returncode": 9, "stdout": private_detail}, "supervisor-worker-exit"),
            ("json", {"stdout": private_detail}, "supervisor-result-invalid-json"),
            ("shape", {"stdout": "[]"}, "supervisor-result-invalid-shape"),
        ):
            outcome = {**base, **overrides}
            with self.subTest(label=label), mock.patch.object(
                agentic_benchmark_process_supervisor,
                "supervise_process",
                return_value=outcome,
            ):
                result = supervise_operation("attempt", {}, 1.0)
            self.assertEqual(
                result,
                {
                    "status": "invalid",
                    "invalidReason": "infrastructure",
                    "errorType": expected,
                    "elapsedSeconds": 0.125,
                },
            )
            self.assertNotIn(private_detail, json.dumps(result, sort_keys=True))

    def test_credential_markers_use_worker_stdin_and_never_argv_or_result(self):
        secret = "private-refresh-token-value"
        captured: dict[str, object] = {}

        def fake_supervise(
            command: list[str],
            payload: str,
            timeout_seconds: float,
            *,
            pass_fds: tuple[int, ...] = (),
            artifact_root: Path | None = None,
        ) -> dict:
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

    def test_purge_untrusted_unlinks_a_root_symlink_without_following_its_target(self):
        with tempfile.TemporaryDirectory(prefix="agentic-purge-link-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            outside = output_root / "outside"
            secret = outside / "secret.txt"
            outside.mkdir()
            secret.write_text("external-secret", encoding="utf-8")
            attempts_link = output_root / "attempts"
            attempts_link.symlink_to(outside, target_is_directory=True)
            exposure = supervise_confidential_cleanup(
                {"root": str(self.root), "treeRoot": str(attempts_link), "mode": "purge-untrusted"},
                1.0,
            )
            self.assertIsNone(exposure)
            self.assertFalse(attempts_link.is_symlink())
            self.assertEqual(secret.read_text(encoding="utf-8"), "external-secret")

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

    def test_setup_passes_the_verified_proxy_policy_only_to_prompt_isolation_owner(self):
        with tempfile.TemporaryDirectory(prefix="agentic-setup-policy-test-", dir=self.root / ".tmp") as value:
            output_root = Path(value)
            batch = {"caseIds": ["case"], "frozenCases": []}
            proxy_policy = object()
            captured: dict[str, object] = {}

            def capture_audit(**arguments):
                captured.update(arguments)
                return {"safe": True}

            runner = SimpleNamespace(
                repo_root=lambda: self.root,
                resolve_tmp_child=lambda _root, path, _label: path,
                verify_batch=lambda *_args: proxy_policy,
                validate_auth_mount_file=lambda _path: None,
                credential_policy_from_markers=lambda _markers: object(),
                load_batch_and_ledger=lambda _root: (batch, {"attempts": []}),
                agentic_benchmark_scheduler=SimpleNamespace(validate_ledger=lambda *_args: None),
                scrub_stale_confidential_artifacts=lambda *_args: None,
                remove_tmp_artifact_entry=lambda *_args: None,
                resolve_tool=lambda name, _variable: Path(f"/tool/{name}"),
                find_case=lambda *_args: {"caseId": "case", "frozenPromptPath": "prompt.txt", "frozenSeedProjectPath": "project"},
                relative_repo_path=lambda _root, path: str(path),
                run_isolation_audit=capture_audit,
                validate_live_isolation_report=lambda *_args: None,
                atomic_json=lambda *_args: None,
            )
            result = agentic_benchmark_process_supervisor._execute_isolation_setup(
                runner,
                {
                    "root": str(self.root),
                    "outputRoot": str(output_root),
                    "batch": batch,
                    "authFile": "/safe/auth",
                    "credentialMarkers": [],
                    "timeoutSeconds": 1.0,
                },
            )
            self.assertIs(captured["proxy_policy"], proxy_policy)
            self.assertTrue(captured["process_group_supervised"])
            self.assertEqual(result["authFile"], "/safe/auth")


if __name__ == "__main__":
    unittest.main()
