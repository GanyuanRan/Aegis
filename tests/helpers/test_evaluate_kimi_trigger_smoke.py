from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests.helpers.evaluate_kimi_trigger_smoke import (
    EvaluationError,
    evaluate_case,
    evaluate_resume,
    fixture_cases,
    skill_calls,
)


def assistant_stream(*skills: str) -> str:
    tool_calls = [
        {
            "function": {
                "name": "Skill",
                "arguments": json.dumps({"skill": skill}),
            }
        }
        for skill in skills
    ]
    return json.dumps({"role": "assistant", "tool_calls": tool_calls}) + "\n"


class KimiTriggerSmokeEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_extracts_only_assistant_skill_calls(self) -> None:
        path = self.write(
            "stream.jsonl",
            json.dumps({"role": "user", "tool_calls": []})
            + "\n"
            + assistant_stream("brainstorming"),
        )
        self.assertEqual(skill_calls(path), ["brainstorming"])

    def test_expected_skill_has_no_errors(self) -> None:
        path = self.write("stream.jsonl", assistant_stream("brainstorming"))
        self.assertEqual(
            evaluate_case({"id": "feature", "expectedSkill": "brainstorming"}, path),
            (0, 0, 0),
        )

    def test_missing_extra_and_duplicate_calls_are_counted(self) -> None:
        missing = self.write("missing.jsonl", assistant_stream("systematic-debugging"))
        self.assertEqual(
            evaluate_case({"id": "feature", "expectedSkill": "brainstorming"}, missing),
            (1, 1, 0),
        )
        duplicate = self.write(
            "duplicate.jsonl", assistant_stream("brainstorming", "brainstorming")
        )
        self.assertEqual(
            evaluate_case({"id": "feature", "expectedSkill": "brainstorming"}, duplicate),
            (0, 0, 1),
        )

    def test_negative_case_rejects_any_skill(self) -> None:
        path = self.write("stream.jsonl", assistant_stream("using-aegis"))
        self.assertEqual(
            evaluate_case({"id": "factual", "expectedSkill": None}, path),
            (0, 1, 0),
        )

    def test_resume_allows_zero_or_one_expected_call_only(self) -> None:
        evaluate_resume(self.write("none.jsonl", ""), "systematic-debugging")
        evaluate_resume(
            self.write("one.jsonl", assistant_stream("systematic-debugging")),
            "systematic-debugging",
        )
        with self.assertRaises(EvaluationError):
            evaluate_resume(
                self.write("extra.jsonl", assistant_stream("brainstorming")),
                "systematic-debugging",
            )

    def test_fixture_rejects_non_object_case(self) -> None:
        fixture = {"version": 1, "cases": [{"id": str(index)} for index in range(4)] + [None]}
        path = self.write("fixtures.json", json.dumps(fixture))
        with self.assertRaises(EvaluationError):
            fixture_cases(path)


if __name__ == "__main__":
    unittest.main()
