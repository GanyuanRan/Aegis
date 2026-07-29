#!/usr/bin/env python3
"""Contract tests for private Codex JSONL evidence reduction."""

from __future__ import annotations

import json
import unittest

from agentic_benchmark_codex_events import (
    MAX_STRUCTURED_COMMAND_ARGS,
    MAX_STRUCTURED_COMMAND_CHARS,
    parse_codex_jsonl,
)


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

    def test_tool_output_and_file_content_cannot_create_semantic_tags(self):
        raw = "\n".join(json.dumps(value) for value in (
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": "python tests/run.py",
                "aggregated_output": "Change necessity and fallback callers",
                "stderr": "Implementation rationale: retire dependencies",
                "detail": {"nested": "minimum change; search references and usages"},
            }},
            {"type": "item.completed", "item": {
                "type": "file_change", "changes": [{
                    "kind": "update", "path": "src/example.py",
                    "content": "source change is necessary; fallback dependency",
                }],
            }},
        ))
        parsed = parse_codex_jsonl(raw)
        self.assertEqual([event["tags"] for event in parsed["events"]], [[], []])

    def test_assistant_rationale_and_structured_search_keep_owned_tags(self):
        raw = "\n".join(json.dumps(value) for value in (
            {"type": "item.completed", "item": {
                "type": "agent_message", "text": "The code change is necessary.",
            }},
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": ["rg", "fallback", "src"],
            }},
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": ["rg", "--files", "src"],
            }},
        ))
        parsed = parse_codex_jsonl(raw)
        self.assertIn("implementation-rationale", parsed["events"][0]["tags"])
        self.assertEqual(parsed["events"][1]["tags"], ["dependency-check"])
        self.assertEqual(parsed["events"][2]["tags"], [])

    def test_only_owned_assistant_message_shapes_create_semantic_tags(self):
        rationale = "The minimum source change is necessary; inspect fallback dependencies."
        raw = "\n".join(json.dumps({"type": "item.completed", "item": item}) for item in (
            {"type": "message", "role": "user", "text": rationale},
            {"type": "message", "role": "developer", "text": rationale},
            {"type": "message", "role": "tool", "text": rationale},
            {"type": "agent_message", "role": "user", "text": rationale},
            {"type": "agent_message", "role": "developer", "text": rationale},
            {"type": "assistant_message", "role": "tool", "text": rationale},
            {"type": "agent_message", "metadata": {"input_text": rationale}},
            {"type": "message", "role": "assistant", "content": [
                {"type": "input_text", "text": rationale},
                {"type": "output_text", "text": "The code change is necessary."},
            ]},
        ))
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(len(parsed["events"]), 1)
        self.assertEqual(parsed["finalResponse"], "The code change is necessary.")
        self.assertEqual(parsed["events"][0]["tags"], ["implementation-rationale"])

    def test_dependency_search_requires_a_bounded_structured_executable(self):
        commands = (
            ("echo rg fallback src", []),
            (["rg", "--files", "src"], []),
            (["rg", "--files-with-matches", "fallback", "src"], ["dependency-check"]),
            (["rg", "--", "--files"], ["dependency-check"]),
            (["rg", "fallback phrase", "src"], ["dependency-check"]),
            (["/usr/bin/grep", "fallback", "src"], ["dependency-check"]),
            ("rg 'unterminated", []),
            ("", []),
            ([], []),
            (["rg", 7, "src"], []),
            (["rg", ["fallback"], "src"], []),
            ("rg " + "x" * MAX_STRUCTURED_COMMAND_CHARS, []),
            (["rg", "x" * MAX_STRUCTURED_COMMAND_CHARS], []),
            (["rg"] + ["x"] * MAX_STRUCTURED_COMMAND_ARGS, []),
        )
        for command, expected_tags in commands:
            with self.subTest(command=repr(command)[:80]):
                parsed = parse_codex_jsonl(json.dumps({
                    "type": "item.completed",
                    "item": {"type": "command_execution", "command": command},
                }))
                self.assertEqual(parsed["events"][0]["tags"], expected_tags)

    def test_dependency_search_supports_only_fixed_real_shell_wrappers(self):
        commands = (
            ("/bin/bash -lc 'rg fallback src'", ["dependency-check"]),
            ("/bin/bash -lc 'pwd && rg fallback src'", ["dependency-check"]),
            (["/bin/sh", "-c", "rg fallback src"], ["dependency-check"]),
            (["bash", "-lc", "rg --files | rg fallback src"], ["dependency-check"]),
            (["bash", "-lc", "echo rg fallback src"], []),
            (["bash", "-lc", "rg --files src"], []),
            (["bash", "-lc", "rg 'fallback|retir' src"], ["dependency-check"]),
            (["bash", "-lc", "echo 'rg|grep fallback'"], []),
            (["python", "-c", "rg fallback src"], []),
            (["bash", "-x", "rg fallback src"], []),
            (["bash", "-lc", "rg fallback src", "positional"], []),
            ("bash -lc 'rg fallback src' positional", []),
        )
        for command, expected_tags in commands:
            with self.subTest(command=repr(command)):
                parsed = parse_codex_jsonl(json.dumps({
                    "type": "item.completed",
                    "item": {"type": "command_execution", "command": command},
                }))
                self.assertEqual(parsed["events"][0]["tags"], expected_tags)

    def test_nonsemantic_evidence_and_execution_counters_are_preserved(self):
        raw = "\n".join(json.dumps(value) for value in (
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": "rm old.py",
            }},
            {"type": "item.completed", "item": {
                "type": "command_execution", "command": "python tests/run.py",
            }},
            {"type": "item.completed", "item": {
                "type": "command_execution", "stderr": "sandbox_error",
            }},
            {"type": "item.completed", "item": {
                "type": "file_change", "changes": [{"kind": "update", "path": "src/a.py"}],
            }},
            {"type": "item.completed", "item": {
                "type": "assistant_message", "text": "Final response",
            }},
            {"type": "turn.completed", "usage": {
                "input_tokens": 11, "output_tokens": 7, "model": "gpt-test",
            }},
        ))
        parsed = parse_codex_jsonl(raw)
        self.assertEqual(parsed["tokens"], {"input_tokens": 11, "output_tokens": 7})
        self.assertEqual(parsed["observedModels"], ["gpt-test"])
        self.assertEqual(parsed["finalResponse"], "Final response")
        self.assertEqual(parsed["events"][0]["toolKind"], "delete_file")
        self.assertEqual(parsed["toolExecutionCount"], 3)
        self.assertEqual(parsed["toolSandboxFailureCount"], 1)

    def test_pilot_counterfactual_keeps_skill_output_separate_from_assistant_intent(self):
        skill_excerpt = (
            "Change Necessity: explain the implementation rationale, then search "
            "dependencies, callers, references, fallback, and retirement paths."
        )
        output_only = parse_codex_jsonl(json.dumps({
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "sed -n '1,80p' SKILL.md",
                "aggregated_output": skill_excerpt,
            },
        }))
        with_assistant = parse_codex_jsonl("\n".join((
            json.dumps({
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "sed -n '1,80p' SKILL.md",
                    "aggregated_output": skill_excerpt,
                },
            }),
            json.dumps({
                "type": "item.completed",
                "item": {
                    "type": "agent_message",
                    "text": "The minimum source change is necessary.",
                },
            }),
        )))

        self.assertEqual(output_only["events"][0]["tags"], [])
        self.assertNotIn("implementation-rationale", output_only["events"][0]["tags"])
        self.assertIn("implementation-rationale", with_assistant["events"][1]["tags"])


if __name__ == "__main__":
    unittest.main()
