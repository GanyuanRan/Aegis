#!/usr/bin/env python3
"""Reduce Codex JSONL to the bounded evidence used by the benchmark scorer."""

from __future__ import annotations

import json
import posixpath
import re
import shlex
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
MAX_STRUCTURED_COMMAND_CHARS = 16_384
MAX_STRUCTURED_COMMAND_ARGS = 256


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


def is_assistant_message(item_type: str, item: dict[str, Any]) -> bool:
    role = item.get("role")
    if item_type == "message":
        return role == "assistant"
    if item_type in {"agent_message", "assistant_message"}:
        return role is None or role in {"agent", "assistant"}
    return False


def assistant_text(item: dict[str, Any]) -> str:
    for key in ("text", "message", "output_text", "content"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    content = item.get("content")
    blocks = content if isinstance(content, list) else [content]
    block_texts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") not in {"output_text", "text"}:
            continue
        for key in ("text", "output_text", "content"):
            value = block.get(key)
            if isinstance(value, str) and value.strip():
                block_texts.append(value.strip())
                break
    if block_texts:
        return "\n".join(block_texts)
    return ""


# A "minimum/minimal/smallest change|fix|edit|patch" phrase is genuine change
# rationale only when the model is *committing* to the minimal change. The same
# words appear when the phrase is negated ("do not make the smallest fix; a
# broader repair is needed") or quoted from the task/policy ("the policy says:
# make the smallest fix"). Negated and quoted mentions are references, not the
# model's own rationale, and are intentionally rejected so they cannot satisfy
# the change-necessity-before-edit contract. Word boundaries keep unrelated
# words (e.g. "resource change") from matching "source change".
_MINIMUM_CHANGE_PHRASE = re.compile(
    r"\b(?:minimum|minimal|smallest) (?:[\w-]+ ){0,2}(?:change|fix|edit|patch)\b"
)
_CLAUSE_BOUNDARY = re.compile(r"[.;!?]")
_MINIMUM_CHANGE_NEGATIONS = frozenset({
    "not", "no", "never", "without", "avoid", "avoids", "avoided", "avoiding",
    "don't", "doesn't", "didn't", "isn't", "aren't", "wasn't", "weren't",
    "shouldn't", "mustn't", "won't", "wouldn't", "can't", "cannot", "couldn't",
})
_MINIMUM_CHANGE_NEGATION_PHRASE = re.compile(r"\b(?:rather than|instead of)\b(?:\s+\S+){0,3}\s*$")
_MINIMUM_CHANGE_QUOTATIONS = frozenset({
    "says", "say", "said", "states", "state", "stated", "stating",
    "reads", "read", "quote", "quotes", "quoted", "quoting", "cites", "cite",
    "citing", "instruction", "instructions", "policy", "rubric", "guideline",
    "guidelines", "prompt",
})


def _clause_before(normalized: str, index: int) -> str:
    """Return the clause preceding ``index`` (text since the last . ; ! ?)."""
    start = 0
    for boundary in _CLAUSE_BOUNDARY.finditer(normalized, 0, index):
        start = boundary.end()
    return normalized[start:index]


def _committed_minimum_change(normalized: str) -> bool:
    """True when a minimum-change phrase is the model committing to the minimal
    change, not a negated ("do not make the smallest fix") or quoted ("the policy
    says: make the smallest fix") mention. Negation is checked in the four words
    before the phrase; quotation in the five words before it."""
    for match in _MINIMUM_CHANGE_PHRASE.finditer(normalized):
        clause = _clause_before(normalized, match.start())
        words = [word.strip("\"'`,:;()[]") for word in clause.split()]
        if any(word in _MINIMUM_CHANGE_NEGATIONS for word in words[-4:]):
            continue
        if _MINIMUM_CHANGE_NEGATION_PHRASE.search(clause):
            continue
        if any(word in _MINIMUM_CHANGE_QUOTATIONS for word in words[-5:]):
            continue
        return True
    return False


def semantic_tags(text: str) -> list[str]:
    normalized = " ".join(text.casefold().split())
    tags: list[str] = []
    explicit_rationale = bool(
        re.search(
            r"change necessity|implementation rationale"
            r"|code change (?:is )?(?:needed|necessary)|\bsource change\b",
            normalized,
        )
        or _committed_minimum_change(normalized)
    )
    code_change_decision = re.search(r"\bdecision\s*:\s*code(?:[-_\s]+)change\b", normalized)
    meta_value = r"(?:a |an |the )?(?:required|field|label|template|policy|phrase|token)\b"
    template_frame = re.search(
        r"^(?:policy template|quoted (?:review )?form|quoted template|template (?:quote|example)|example template)\s*:",
        normalized,
    )
    placeholder_claim = re.search(
        r"\b(?:root cause|canonical owner|(?:minimum|minimal) "
        r"(?:repair|change|edit|patch|boundary))\s*(?::|is)\s+"
        r"(?:<[^>]+>|(?:tbd|todo|unknown|n/?a))(?=\s*(?:[.,;]|$))",
        normalized,
    )
    rationale_claims = sum(bool(re.search(pattern, normalized)) for pattern in (
        rf"\broot cause\s*(?::|is)\s+(?!{meta_value})\S+",
        rf"\bcanonical owner\s*(?::|is)\s+(?!{meta_value})\S+|\b(?:[\w`./-]+\s+){{1,5}}is the canonical owner\b",
        rf"\b(?:minimum|minimal) (?:repair|change|edit|patch|boundary)\s*(?::|is)\s+(?!{meta_value})\S+",
    ))
    if explicit_rationale or (
        code_change_decision and rationale_claims >= 2 and not template_frame and not placeholder_claim
    ):
        tags.append("implementation-rationale")
    if re.search(r"dependenc|callers?|references?|usages?|fallback|retir", normalized):
        tags.append("dependency-check")
    return tags


def bounded_shell_tokens(command: str) -> list[str]:
    if not command or len(command) > MAX_STRUCTURED_COMMAND_CHARS:
        return []
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = ""
        arguments: list[str] = []
        total_chars = 0
        for argument in lexer:
            total_chars += len(argument)
            if (
                len(arguments) >= MAX_STRUCTURED_COMMAND_ARGS
                or total_chars > MAX_STRUCTURED_COMMAND_CHARS
            ):
                return []
            arguments.append(argument)
    except ValueError:
        return []
    return arguments if arguments and arguments[0] else []


def bounded_argv_tokens(command: list[Any]) -> list[str]:
    if not command or len(command) > MAX_STRUCTURED_COMMAND_ARGS:
        return []
    arguments: list[str] = []
    total_chars = 0
    for argument in command:
        if not isinstance(argument, str):
            return []
        total_chars += len(argument)
        if total_chars > MAX_STRUCTURED_COMMAND_CHARS:
            return []
        arguments.append(argument)
    return arguments if arguments[0] else []


def split_command_segments(arguments: list[str]) -> list[list[str]]:
    separators = {";", "&&", "||", "|", "&"}
    segments: list[list[str]] = []
    current: list[str] = []
    for argument in arguments:
        if argument in separators:
            if current:
                segments.append(current)
                current = []
        else:
            current.append(argument)
    if current:
        segments.append(current)
    return segments


def structured_command_segments(item: dict[str, Any]) -> list[list[str]]:
    """Return bounded executable segments, unwrapping only fixed safe shell forms."""
    command = item.get("command")
    is_shell_text = isinstance(command, str)
    if is_shell_text:
        arguments = bounded_shell_tokens(command)
    elif isinstance(command, list):
        arguments = bounded_argv_tokens(command)
    else:
        return []
    if not arguments:
        return []

    executable = posixpath.basename(arguments[0]).casefold()
    if executable in {"bash", "sh"}:
        if len(arguments) != 3 or arguments[1] not in {"-c", "-lc"}:
            return []
        script_arguments = bounded_shell_tokens(arguments[2])
        return split_command_segments(script_arguments) if script_arguments else []
    return split_command_segments(arguments) if is_shell_text else [arguments]


def is_dependency_search(segments: list[list[str]]) -> bool:
    for arguments in segments:
        if not arguments or posixpath.basename(arguments[0]).casefold() not in {"rg", "grep"}:
            continue
        inventory = False
        for argument in arguments[1:]:
            if argument == "--":
                break
            if argument == "--files":
                inventory = True
                break
        if not inventory:
            return True
    return False


def is_shell_write(segments: list[list[str]]) -> bool:
    """Return True when a shell command mutates workspace file content.

    Codex's edit tool may be invoked as a shell program (apply_patch), and
    files may be rewritten through redirection (`>` / `>>`), in-place editors
    (`sed -i`), or `tee`. Treating these machine-observed writes as edit
    events keeps the before-first-edit contract model-agnostic.
    """
    for arguments in segments:
        if not arguments:
            continue
        executable = posixpath.basename(arguments[0]).casefold()
        if executable in {"apply_patch", "applypatch"}:
            return True
        if executable == "sed" and any(
            argument == "-i" or argument.startswith("-i") for argument in arguments[1:]
        ):
            return True
        if executable == "tee" and any(
            not argument.startswith("-") for argument in arguments[1:]
        ):
            return True
        for index, argument in enumerate(arguments[1:], start=1):
            if argument not in {">", ">>"}:
                continue
            if index + 1 >= len(arguments):
                continue
            target = arguments[index + 1]
            if target.startswith("/"):
                continue
            if target == ".git" or target.startswith(".git/") or "/.git/" in target:
                continue
            if target in {"&", "|", ";", "&&", "||"}:
                continue
            return True
    return False



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
        if is_assistant_message(item_type, item):
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
            tags: list[str] = []
            command_segments = structured_command_segments(item)
            if is_dependency_search(command_segments):
                tags.append("dependency-check")
            destructive = any(
                segment and posixpath.basename(segment[0]).casefold() in {"rm", "unlink", "rmdir"}
                for segment in command_segments
            )
            if destructive:
                tool_kind = "delete_file"
            elif is_shell_write(command_segments):
                tool_kind = "edit"
            else:
                tool_kind = "shell"
            events.append({
                "sequence": len(events), "kind": "tool",
                "toolKind": tool_kind,
                "tags": sorted(set(tags)),
            })
        elif item_type in {"file_change", "file_changes", "patch", "apply_patch"}:
            tool_execution_count += 1
            changes = item.get("changes")
            if not isinstance(changes, list):
                changes = [{key: item[key] for key in ("kind", "path", "change_type") if key in item}]
            change_text = "\n".join(strings_in(changes)).casefold()
            deleted = any(word in change_text for word in ("delete", "deleted", "remove file"))
            events.append({
                "sequence": len(events), "kind": "edit",
                "toolKind": "delete_file" if deleted else "apply_patch",
                "tags": [],
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
