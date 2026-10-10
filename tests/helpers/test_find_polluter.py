"""Run the shipped diagnostic against isolated tests and npm fixtures."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
GIT_BASH = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
BASH = str(GIT_BASH) if os.name == "nt" and GIT_BASH.is_file() else shutil.which("bash")


@unittest.skipUnless(BASH, "Bash required")
class PolluterTests(unittest.TestCase):
    def run_fixture(self, *, tests=("src/a.test.ts",), runner="exit 0", existing=False,
                    pattern="./src/*.test.ts", expected_args=None):
        with tempfile.TemporaryDirectory(prefix="aegis-polluter-") as tmp:
            root = Path(tmp)
            for name in tests:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            (root / "bin").mkdir()
            if runner is not None:
                npm = root / "bin/npm"
                npm.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@" > runner-args\n' + runner + "\n", encoding="utf-8")
                npm.chmod(0o755)
            if existing:
                (root / "pollution").write_text("user state", encoding="utf-8")
            result = subprocess.run(
                [BASH, "--noprofile", "--norc", "-c",
                 'fixture_bin=$(cd "$1" && pwd); '
                 'if [[ "$5" == missing ]]; then export PATH="$fixture_bin"; '
                 'else export PATH="$fixture_bin:/usr/bin:/bin"; fi; '
                 'cd "$2"; exec "$BASH" "$3" pollution "$4"',
                 "polluter-test", (root / "bin").as_posix(), root.as_posix(),
                 (ROOT / "skills/systematic-debugging/find-polluter.sh").as_posix(), pattern,
                 "missing" if runner is None else "fixture"],
                text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=15,
            )
            preserved = (root / "pollution").read_text() if existing else None
            if expected_args is not None:
                self.assertTrue((root / "runner-args").is_file(), result.stdout)
                self.assertEqual((root / "runner-args").read_text().splitlines(), expected_args)
            return result.returncode, result.stdout + result.stderr, preserved

    def test_no_matches_is_inconclusive(self):
        code, output, _ = self.run_fixture(tests=())
        self.assertEqual(code, 2, output)
        self.assertNotIn("all tests clean", output)

    def test_existing_pollution_is_preserved_and_inconclusive(self):
        code, output, preserved = self.run_fixture(existing=True)
        self.assertEqual(code, 2, output)
        self.assertEqual(preserved, "user state")

    def test_unavailable_runner_is_inconclusive(self):
        code, output, _ = self.run_fixture(runner=None)
        self.assertEqual(code, 2, output)
        self.assertIn("npm is unavailable", output)

    def test_failed_test_can_still_identify_polluter(self):
        code, output, _ = self.run_fixture(runner="touch pollution; exit 1")
        self.assertEqual(code, 1, output)
        self.assertIn("FOUND POLLUTER", output)

    def test_failed_runner_without_pollution_is_inconclusive(self):
        code, output, _ = self.run_fixture(runner="exit 127")
        self.assertEqual(code, 2, output)

    def test_nonzero_tests_without_pollution_are_inconclusive(self):
        code, output, _ = self.run_fixture(runner="exit 1")
        self.assertEqual(code, 2, output)

    def test_file_with_spaces_is_one_argument_and_relative_glob_matches(self):
        code, output, _ = self.run_fixture(
            tests=("src/a test.test.ts",),
            pattern="src/*.test.ts",
            expected_args=["test", "--", "./src/a test.test.ts"],
            runner='[[ "$#" == 3 && "$1" == test && "$2" == -- && "$3" == "./src/a test.test.ts" ]] || exit 9',
        )
        self.assertEqual(code, 0, output)
        self.assertIn("1 test", output)


if __name__ == "__main__":
    unittest.main()
