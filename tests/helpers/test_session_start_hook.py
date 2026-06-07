import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / "hooks" / "session-start"


def resolve_bash_command():
    candidates = [
        Path(r"C:\Program Files\Git\bin\bash.exe"),
        Path(r"C:\Program Files (x86)\Git\bin\bash.exe"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return [str(candidate)]

    return None


class SessionStartHookTests(unittest.TestCase):
    def run_hook(self, extra_env=None):
        bash_command = resolve_bash_command()
        if bash_command is None:
            self.skipTest("Git Bash not available on this host")

        env = os.environ.copy()
        env["HOME"] = tempfile.mkdtemp(prefix="aegis-hook-home-")
        if extra_env:
            env.update(extra_env)

        result = subprocess.run(
            bash_command + [str(HOOK_PATH)],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def test_compact_json_style_emits_single_line_additional_context(self):
        output = self.run_hook(
            {
                "AEGIS_HOOK_JSON_STYLE": "compact",
                "COPILOT_CLI": "1",
            }
        )

        self.assertEqual(output.count("\n"), 1)
        payload = json.loads(output)
        self.assertIn("additionalContext", payload)
        self.assertIn("You have Aegis.", payload["additionalContext"])

    def test_claude_shape_still_uses_nested_hook_specific_output(self):
        output = self.run_hook(
            {
                "CLAUDE_PLUGIN_ROOT": str(REPO_ROOT),
            }
        )

        payload = json.loads(output)
        self.assertIn("hookSpecificOutput", payload)
        self.assertEqual(
            payload["hookSpecificOutput"]["hookEventName"], "SessionStart"
        )


if __name__ == "__main__":
    unittest.main()
