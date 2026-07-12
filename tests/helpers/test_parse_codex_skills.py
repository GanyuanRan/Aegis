#!/usr/bin/env python3

import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("parse_codex_skills.py")
SPEC = importlib.util.spec_from_file_location("parse_codex_skills", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ParseCodexSkillsTests(unittest.TestCase):
    def test_extracts_real_skill_load_commands(self) -> None:
        lines = [
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/using-aegis/SKILL.md' "
            "-TotalCount 220\" in X:\\repo\\Aegis",
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'skills/systematic-debugging/SKILL.md' -TotalCount 320\" "
            "in X:\\repo\\Aegis",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["using-aegis", "systematic-debugging"],
        )

    def test_extracts_namespaced_codex_skill_paths(self) -> None:
        lines = [
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content 'C:\\\\Users\\\\Example\\\\.codex\\\\skills\\\\aegis\\\\using-aegis\\\\SKILL.md' "
            "-Raw\" in X:\\repo\\Aegis",
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content 'C:\\\\Users\\\\Example\\\\.codex\\\\skills\\\\aegis\\\\systematic-debugging\\\\SKILL.md' "
            "-Raw\" in X:\\repo\\Aegis",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["using-aegis", "systematic-debugging"],
        )

    def test_extracts_multiple_skill_loads_from_one_command(self) -> None:
        lines = [
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Raw 'C:\\\\Users\\\\Example\\\\.codex\\\\aegis\\\\skills\\\\using-aegis\\\\SKILL.md'; "
            "Get-Content -Raw 'C:\\\\Users\\\\Example\\\\.codex\\\\aegis\\\\skills\\\\brainstorming\\\\SKILL.md'\" "
            "in X:\\repo\\Aegis",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["using-aegis", "brainstorming"],
        )
        self.assertEqual(MODULE.first_skill_load_line(lines, "brainstorming"), 1)

    def test_keeps_bare_skill_path_fallback(self) -> None:
        lines = [
            "skills/verification-before-completion/SKILL.md",
            "skills/verification-before-completion/SKILL.md",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["verification-before-completion"],
        )

    def test_ignores_indented_skill_paths_from_shell_listings(self) -> None:
        lines = [
            "        skills/example/SKILL.md",
            "skills/verification-before-completion/SKILL.md",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["verification-before-completion"],
        )

    def test_ignores_nested_skill_paths_quoted_inside_transcript_reads(self) -> None:
        lines = [
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command '$i=0; "
            "Get-Content -Path '\"'\"'X:/repo/Aegis/.tmp/aegis-tests/"
            "1777180626/explicit-skill-requests/systematic-debugging/codex-output.log'\"'\"' "
            "| ForEach-Object { \"'$i++; if($_ -match '\"'\"'use systematic-debugging to figure "
            "out what''s wrong|Get-Content -Path '\"'\"''\"'\"'X:/repo/Aegis/"
            "skills/systematic-debugging/SKILL.md'\"'\"''\"'\"'') { '{0}:{1}' -f \"'$i, $_ } }' "
            "in X:\\repo\\Aegis\\.tmp\\aegis-tests\\1777180626\\explicit-skill-requests\\systematic-debugging\\project",
            "3059:\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/systematic-debugging/SKILL.md' "
            "-TotalCount 260\" in X:\\repo\\Aegis\\.tmp\\aegis-tests\\1777180626\\explicit-skill-requests\\systematic-debugging\\project",
        ]

        self.assertEqual(list(MODULE.iter_loaded_skills(lines)), [])

    def test_first_skill_load_line_skips_transcript_noise(self) -> None:
        lines = [
            "3059:\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/systematic-debugging/SKILL.md' "
            "-TotalCount 260\" in X:\\repo\\Aegis\\.tmp\\aegis-tests\\1777180626\\explicit-skill-requests\\systematic-debugging\\project",
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/using-aegis/SKILL.md' "
            "-TotalCount 220\" in X:\\repo\\Aegis",
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/systematic-debugging/SKILL.md' "
            "-TotalCount 260\" in X:\\repo\\Aegis",
        ]

        self.assertEqual(MODULE.first_skill_load_line(lines, "systematic-debugging"), 3)

    def test_extracts_long_task_continuation_skill(self) -> None:
        lines = [
            "\"C:\\\\Program Files\\\\PowerShell\\\\7\\\\pwsh.exe\" -Command "
            "\"Get-Content -Path 'X:/repo/Aegis/skills/long-task-continuation/SKILL.md' "
            "-TotalCount 260\" in X:\\repo\\Aegis",
        ]

        self.assertEqual(
            list(MODULE.iter_loaded_skills(lines)),
            ["long-task-continuation"],
        )


if __name__ == "__main__":
    unittest.main()
