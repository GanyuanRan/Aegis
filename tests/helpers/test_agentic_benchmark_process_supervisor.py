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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_benchmark_process_supervisor import MAX_RESULT_BYTES, supervise_process
from agentic_benchmark_scheduler import execute_budgeted_stage


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


if __name__ == "__main__":
    unittest.main()
