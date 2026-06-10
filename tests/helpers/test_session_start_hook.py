import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / "hooks" / "session-start"
COPILOT_HOOK_PATH = REPO_ROOT / "hooks" / "copilot-session-start.ps1"


def resolve_bash_command():
    candidates = [
        Path(r"C:\Program Files\Git\bin\bash.exe"),
        Path(r"C:\Program Files (x86)\Git\bin\bash.exe"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return [str(candidate)]

    return None


def resolve_powershell_command():
    for candidate in ("pwsh", "powershell"):
        command = shutil.which(candidate)
        if command:
            return [command, "-NoProfile", "-File"]

    return None


class SessionStartHookTests(unittest.TestCase):
    def build_env(self, extra_env=None, home_dir=None):
        if home_dir is None:
            home_dir = Path(tempfile.mkdtemp(prefix="aegis-hook-home-"))

        env = os.environ.copy()
        env["HOME"] = str(home_dir)
        if extra_env:
            env.update(extra_env)

        return env

    def run_hook(self, extra_env=None, home_dir=None):
        bash_command = resolve_bash_command()
        if bash_command is None:
            self.skipTest("Git Bash not available on this host")

        env = self.build_env(extra_env=extra_env, home_dir=home_dir)

        result = subprocess.run(
            bash_command + [str(HOOK_PATH)],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def run_copilot_powershell_hook(self, extra_env=None, home_dir=None):
        powershell_command = resolve_powershell_command()
        if powershell_command is None:
            self.skipTest("PowerShell not available on this host")

        env = self.build_env(extra_env=extra_env, home_dir=home_dir)
        result = subprocess.run(
            powershell_command + [str(COPILOT_HOOK_PATH)],
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

    def test_legacy_skill_warning_uses_host_neutral_guidance(self):
        home_dir = Path(tempfile.mkdtemp(prefix="aegis-hook-home-"))
        (home_dir / ".config" / "aegis" / "skills").mkdir(parents=True)

        output = self.run_hook(
            {
                "AEGIS_HOOK_JSON_STYLE": "compact",
                "COPILOT_CLI": "1",
            },
            home_dir=home_dir,
        )

        payload = json.loads(output)
        self.assertIn("current host's supported skills surface", payload["additionalContext"])
        self.assertIn("~/.copilot/skills", payload["additionalContext"])
        self.assertNotIn(
            "Move custom skills to ~/.claude/skills instead.",
            payload["additionalContext"],
        )

    def test_copilot_powershell_wrapper_emits_single_line_additional_context(self):
        output = self.run_copilot_powershell_hook()

        self.assertEqual(output.count("\n"), 1)
        payload = json.loads(output)
        self.assertIn("additionalContext", payload)
        self.assertIn("You have Aegis.", payload["additionalContext"])

    def test_copilot_powershell_wrapper_without_bash_still_emits_additional_context(self):
        output = self.run_copilot_powershell_hook(
            {
                "AEGIS_COPILOT_SKIP_BASH": "1",
            }
        )

        self.assertEqual(output.count("\n"), 1)
        payload = json.loads(output)
        self.assertIn("additionalContext", payload)
        self.assertIn("You have Aegis.", payload["additionalContext"])


if __name__ == "__main__":
    unittest.main()
