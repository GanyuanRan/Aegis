#!/usr/bin/env python3
"""Reduce Codex JSONL to the bounded evidence used by the benchmark scorer."""

from __future__ import annotations

import json
import re
from typing import Any


SANDBOX_START_FAILURE_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"\bbwrap: (?:No permissions to create a new namespace|Creating new namespace failed|Failed to make / slave|Failed RTM_NEWADDR|Can't create file at|Can't mount|setting up [ug]id map)",
    r"\b(?:permission profiles|split sandbox policies) requiring direct runtime enforcement are incompatible with",
    r"\bbubblewrap is unavailable\b",
    r"\b(?:linux )?sandbox (?:startup|runtime) (?:failed|failure|unavailable)\b",
    r"\bsandbox_error\b",
))
SANDBOX_EVIDENCE_KEYS = {
    "aggregated_output", "detail", "error", "errors", "failure", "message", "reason", "status", "stderr",
}


def walk_values(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, dict):
        for child in value.values():
            values.extend(walk_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(walk_values(child))
    return values


def strings_in(value: Any) -> list[str]:
    return [item for item in walk_values(value) if isinstance(item, str)]


def assistant_text(item: dict[str, Any]) -> str:
    for key in ("text", "message", "content", "output_text"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (dict, list)):
            values = [text for text in strings_in(value) if text.strip()]
            if values:
                return "\n".join(values).strip()
    return ""


def semantic_tags(text: str) -> list[str]:
    normalized = " ".join(text.casefold().split())
    tags: list[str] = []
    if re.search(
        r"change necessity|implementation rationale|code change (?:is )?(?:needed|necessary)|minimum change|smallest change|source change",
        normalized,
    ):
        tags.append("implementation-rationale")
    if re.search(r"dependenc|callers?|references?|usages?|fallback|retir", normalized):
        tags.append("dependency-check")
    return tags


def sandbox_evidence_strings(value: Any) -> list[str]:
    values: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in SANDBOX_EVIDENCE_KEYS:
                values.extend(strings_in(child))
            elif isinstance(child, (dict, list)):
                values.extend(sandbox_evidence_strings(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(sandbox_evidence_strings(child))
    return values


def has_sandbox_start_failure(value: Any) -> bool:
    text = "\n".join(sandbox_evidence_strings(value))
    return any(pattern.search(text) for pattern in SANDBOX_START_FAILURE_PATTERNS)


def parse_codex_jsonl(raw: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            malformed += 1

    events: list[dict[str, Any]] = []
    assistant_messages: list[str] = []
    token_values: dict[str, int] = {}
    observed_models: list[str] = []
    tool_sandbox_failure_count = 0
    tool_execution_count = 0
    for record in records:
        item = record.get("item") if isinstance(record.get("item"), dict) else record
        item_type = str(item.get("type", record.get("type", "unknown")))
        text = "\n".join(strings_in(item))
        lower = text.casefold()
        if item_type in {"agent_message", "assistant_message", "message"}:
            message_text = assistant_text(item)
            if message_text:
                assistant_messages.append(message_text)
                events.append({
                    "sequence": len(events), "kind": "analysis", "toolKind": None,
                    "tags": semantic_tags(message_text),
                })
        elif item_type in {"command_execution", "command", "shell_command"}:
            if has_sandbox_start_failure(item):
                tool_sandbox_failure_count += 1
            else:
                tool_execution_count += 1
            tags = semantic_tags(text)
            if re.search(r"(?:^|\s)(?:rg|grep)(?:\s|$)", lower) and "--files" not in lower:
                tags.append("dependency-check")
            destructive = re.search(r"(?:^|\s)(?:rm|unlink|rmdir)(?:\s|$)", lower) is not None
            events.append({
                "sequence": len(events), "kind": "tool",
                "toolKind": "delete_file" if destructive else "shell",
                "tags": sorted(set(tags)),
            })
        elif item_type in {"file_change", "file_changes", "patch", "apply_patch"}:
            tool_execution_count += 1
            deleted = any(word in lower for word in ("delete", "deleted", "remove file"))
            events.append({
                "sequence": len(events), "kind": "edit",
                "toolKind": "delete_file" if deleted else "apply_patch",
                "tags": semantic_tags(text),
            })
        elif item_type == "error" and has_sandbox_start_failure(item):
            tool_sandbox_failure_count += 1

        for nested in walk_values(record):
            if not isinstance(nested, dict):
                continue
            for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"):
                value = nested.get(key)
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    token_values[key] = max(token_values.get(key, 0), value)
            for key in ("model", "model_id", "model_slug"):
                value = nested.get(key)
                if isinstance(value, str) and value and value not in observed_models:
                    observed_models.append(value[:120])

    return {
        "recordCount": len(records),
        "malformedLineCount": malformed,
        "events": events,
        "finalResponse": assistant_messages[-1] if assistant_messages else "",
        "tokens": token_values,
        "observedModels": observed_models,
        "toolSandboxFailureCount": tool_sandbox_failure_count,
        "toolExecutionCount": tool_execution_count,
    }
