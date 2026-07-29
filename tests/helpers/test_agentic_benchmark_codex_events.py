#!/usr/bin/env python3
"""Contract tests for private Codex JSONL evidence reduction."""

from __future__ import annotations

import json
import unittest

from agentic_benchmark_codex_events import parse_codex_jsonl


class CodexEventReductionTest(unittest.TestCase):
    def test_jsonl_is_reduced_without_private_sandbox_detail(self):
        raw = "\n".join(json.dumps(value) for value in (
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": "rg fallback src",
                "aggregated_output": "bwrap: No permissions to create a new namespace; PRIVATE_DETAIL",
            }},
            {"type": "item.completed", "item": {
                "type": "file_change", "changes": [{"kind": "delete", "path": "old.py"}],
            }},
            {"type": "item.completed", "item": {
                "type": "agent_message", "text": "The code change is necessary. Continue?",
            }},
            {"type": "turn.completed", "usage": {"input_tokens": 10, "output_tokens": 3}},
        ))
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(parsed["finalResponse"], "The code change is necessary. Continue?")
        self.assertEqual(parsed["tokens"]["input_tokens"], 10)
        self.assertEqual(parsed["toolSandboxFailureCount"], 1)
        self.assertEqual(parsed["toolExecutionCount"], 1)
        self.assertIn("dependency-check", parsed["events"][0]["tags"])
        self.assertEqual(parsed["events"][1]["toolKind"], "delete_file")
        self.assertNotIn("PRIVATE_DETAIL", json.dumps(parsed, sort_keys=True))

    def test_structured_sandbox_failures_do_not_count_as_tool_execution(self):
        for item in (
            {"type": "command_execution", "status": "failed", "error": {
                "code": "sandbox_error", "detail": "private detail",
            }},
            {"type": "command_execution", "status": "failed", "stderr": (
                "bwrap: Failed to make / slave: Operation not permitted; private detail"
            )},
            {"type": "error", "message": (
                "permission profiles requiring direct runtime enforcement are incompatible with backend"
            )},
        ):
            with self.subTest(item=item["type"]):
                parsed = parse_codex_jsonl(json.dumps({"type": "item.completed", "item": item}))
                self.assertEqual(parsed["toolSandboxFailureCount"], 1)
                self.assertEqual(parsed["toolExecutionCount"], 0)
                self.assertNotIn("private detail", json.dumps(parsed, sort_keys=True))

    def test_ordinary_nonzero_command_is_still_observed_agent_execution(self):
        raw = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "status": "failed", "exit_code": 1,
            "aggregated_output": "test assertion failed",
        }})
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(parsed["toolSandboxFailureCount"], 0)
        self.assertEqual(parsed["toolExecutionCount"], 1)

    def test_sandbox_error_search_text_is_not_a_sandbox_failure(self):
        raw = json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "status": "completed",
            "command": "rg 'sandbox_error|bwrap: Can\\'t mount' tests",
        }})
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(parsed["toolSandboxFailureCount"], 0)
        self.assertEqual(parsed["toolExecutionCount"], 1)


if __name__ == "__main__":
    unittest.main()
