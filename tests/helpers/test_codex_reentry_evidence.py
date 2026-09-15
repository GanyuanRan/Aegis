#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("codex_reentry_evidence.py")
SPEC = importlib.util.spec_from_file_location("codex_reentry_evidence", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


THREAD_ID = "019fd442-7d6e-7d02-948b-524ff1fc7c2f"


class CodexReentryEvidenceTests(unittest.TestCase):
    def test_extracts_thread_id_while_ignoring_non_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = pathlib.Path(temp_dir) / "turn.jsonl"
            log_path.write_text(
                "launcher note\n"
                + json.dumps({"type": "thread.started", "thread_id": THREAD_ID})
                + "\n",
                encoding="utf-8",
            )

            self.assertEqual(MODULE.extract_thread_id(log_path), THREAD_ID)

    def test_finds_current_turn_route_in_assistant_message(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = pathlib.Path(temp_dir) / "turn.jsonl"
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": "I’ll use the Aegis debugging workflow before repair.",
                    },
                }
            ]
            log_path.write_text(
                "\n".join(json.dumps(event) for event in events) + "\n",
                encoding="utf-8",
            )

            self.assertTrue(
                MODULE.route_recorded(log_path, "systematic-debugging")
            )

    def test_does_not_count_a_failed_skill_read_as_a_route_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = pathlib.Path(temp_dir) / "turn.jsonl"
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": "I could not load systematic-debugging.",
                    },
                }
            ]
            log_path.write_text(
                "\n".join(json.dumps(event) for event in events) + "\n",
                encoding="utf-8",
            )

            self.assertFalse(
                MODULE.route_recorded(log_path, "systematic-debugging")
            )

    def test_does_not_count_a_late_route_mention(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = pathlib.Path(temp_dir) / "turn.jsonl"
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": "I’ll inspect the output first.",
                    },
                },
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": "I’ll use systematic-debugging now.",
                    },
                },
            ]
            log_path.write_text(
                "\n".join(json.dumps(event) for event in events) + "\n",
                encoding="utf-8",
            )

            self.assertFalse(
                MODULE.route_recorded(log_path, "systematic-debugging")
            )

    def test_does_not_count_a_negated_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = pathlib.Path(temp_dir) / "turn.jsonl"
            event = {
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": "I’ll use ordinary analysis, not systematic-debugging.",
                },
            }
            log_path.write_text(json.dumps(event) + "\n", encoding="utf-8")

            self.assertFalse(
                MODULE.route_recorded(log_path, "systematic-debugging")
            )

    def test_summarizes_real_compaction_between_two_turns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rollout = pathlib.Path(temp_dir) / f"rollout-now-{THREAD_ID}.jsonl"
            records = [
                {
                    "ordinal": 0,
                    "type": "session_meta",
                    "payload": {
                        "cli_version": "0.154.0",
                        "model_provider": "openai",
                    },
                },
                {
                    "ordinal": 7,
                    "type": "turn_context",
                    "payload": {"model": "gpt-test", "root_turn_id": "turn-1"},
                },
                {"ordinal": 18, "type": "compacted", "payload": {}},
                {
                    "ordinal": 20,
                    "type": "turn_context",
                    "payload": {"model": "gpt-test", "root_turn_id": "turn-1"},
                },
                {
                    "ordinal": 27,
                    "type": "turn_context",
                    "payload": {"model": "gpt-test", "root_turn_id": "turn-2"},
                },
            ]
            rollout.write_text(
                "\n".join(json.dumps(record) for record in records) + "\n",
                encoding="utf-8",
            )

            summary = MODULE.summarize_session(rollout)

            self.assertEqual(summary["cli_version"], "0.154.0")
            self.assertEqual(summary["models"], ["gpt-test"])
            self.assertEqual(summary["turn_count"], 2)
            self.assertEqual(summary["compaction_count"], 1)
            self.assertTrue(summary["compacted_before_second_turn"])
            MODULE.validate_session_summary(summary, require_compaction=True)

    def test_does_not_treat_late_compaction_as_between_turns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rollout = pathlib.Path(temp_dir) / f"rollout-now-{THREAD_ID}.jsonl"
            records = [
                {
                    "ordinal": 0,
                    "type": "session_meta",
                    "payload": {
                        "cli_version": "0.154.0",
                        "model_provider": "openai",
                    },
                },
                {
                    "ordinal": 2,
                    "type": "turn_context",
                    "payload": {
                        "root_turn_id": "turn-1",
                        "model": "gpt-test",
                    },
                },
                {
                    "ordinal": 4,
                    "type": "turn_context",
                    "payload": {
                        "root_turn_id": "turn-2",
                        "model": "gpt-test",
                    },
                },
                {"ordinal": 6, "type": "compacted", "payload": {}},
            ]
            rollout.write_text(
                "\n".join(json.dumps(record) for record in records) + "\n",
                encoding="utf-8",
            )

            summary = MODULE.summarize_session(rollout)

            self.assertFalse(summary["compacted_before_second_turn"])

            with self.assertRaisesRegex(
                MODULE.EvidenceError, "no Codex compacted record"
            ):
                MODULE.validate_session_summary(summary, require_compaction=True)

    def test_validation_requires_two_turns_and_metadata(self) -> None:
        incomplete = {
            "cli_version": "unknown",
            "models": [],
            "turn_count": 1,
            "compacted_before_second_turn": False,
        }

        with self.assertRaisesRegex(MODULE.EvidenceError, "two root turns"):
            MODULE.validate_session_summary(incomplete, require_compaction=False)

    def test_find_rollout_requires_one_exact_thread_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = pathlib.Path(temp_dir)
            session_dir = codex_home / "sessions" / "2026" / "09" / "15"
            session_dir.mkdir(parents=True)
            expected = session_dir / f"rollout-now-{THREAD_ID}.jsonl"
            expected.write_text("", encoding="utf-8")
            (session_dir / "rollout-unrelated.jsonl").write_text(
                THREAD_ID, encoding="utf-8"
            )

            self.assertEqual(MODULE.find_rollout(codex_home, THREAD_ID), expected)


if __name__ == "__main__":
    unittest.main()
