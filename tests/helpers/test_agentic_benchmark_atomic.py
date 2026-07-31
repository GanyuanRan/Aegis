#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentic_benchmark_atomic import atomic_json, atomic_text


class AgenticBenchmarkAtomicTest(unittest.TestCase):
    def test_predictable_tmp_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory(prefix="agentic-atomic-") as value:
            root = Path(value)
            victim = root / "victim.txt"
            victim.write_text("preserve\n", encoding="utf-8")
            predictable = root / "report.json.tmp"
            try:
                predictable.symlink_to(victim)
            except OSError:
                self.skipTest("symlink creation is unavailable")

            target = root / "report.json"
            atomic_json(target, {"ok": True})

            self.assertEqual(victim.read_text(encoding="utf-8"), "preserve\n")
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})

    def test_failed_replace_removes_random_temporary_file(self):
        with tempfile.TemporaryDirectory(prefix="agentic-atomic-") as value:
            root = Path(value)
            target = root / "report.txt"
            with mock.patch("agentic_benchmark_atomic.os.replace", side_effect=OSError("blocked")):
                with self.assertRaises(OSError):
                    atomic_text(target, "payload\n")
            self.assertEqual(list(root.glob(".report.txt.*.tmp")), [])
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
