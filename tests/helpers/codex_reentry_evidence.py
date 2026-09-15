#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections.abc import Iterator
from typing import Any


THREAD_ID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
ROUTE_PATTERNS = {
    "systematic-debugging": re.compile(
        r"(?:\bI(?:['’]ll| will)\s+(?:use|follow|apply)|"
        r"\bI(?:['’]m| am)\s+using|"
        r"\bWe(?:['’]ll| will)\s+(?:use|follow|apply)|"
        r"\bUsing|\bRoute\s*:|\bWorkflow\s*:)[^.\n]{0,180}"
        r"\b(?:systematic[- ]debugging|Aegis(?: systematic)? debugging "
        r"(?:workflow|guidance))\b",
        re.IGNORECASE,
    )
}
NEGATED_ROUTE_RE = re.compile(
    r"\b(?:not|never|neither|cannot|could not|unable to)\b", re.IGNORECASE
)


class EvidenceError(RuntimeError):
    pass


def iter_json_objects(path: pathlib.Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                yield value


def extract_thread_id(log_path: pathlib.Path) -> str:
    ids = {
        str(event.get("thread_id"))
        for event in iter_json_objects(log_path)
        if event.get("type") == "thread.started"
        and THREAD_ID_RE.fullmatch(str(event.get("thread_id", "")))
    }
    if len(ids) != 1:
        raise EvidenceError(
            f"expected exactly one thread.started id in {log_path.name}; found {len(ids)}"
        )
    return ids.pop()


def route_recorded(log_path: pathlib.Path, skill_name: str) -> bool:
    pattern = ROUTE_PATTERNS.get(skill_name)
    if pattern is None:
        raise EvidenceError(f"unsupported route name: {skill_name}")

    for event in iter_json_objects(log_path):
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        item = item if isinstance(item, dict) else {}
        if item.get("type") != "agent_message":
            continue
        text = item.get("text")
        if not isinstance(text, str):
            return False
        match = pattern.search(text)
        return match is not None and NEGATED_ROUTE_RE.search(match.group(0)) is None
    return False


def first_assistant_excerpt(log_path: pathlib.Path, limit: int = 500) -> str:
    for event in iter_json_objects(log_path):
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        item = item if isinstance(item, dict) else {}
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            return item["text"][:limit]
    return ""


def find_rollout(codex_home: pathlib.Path, thread_id: str) -> pathlib.Path:
    if not THREAD_ID_RE.fullmatch(thread_id):
        raise EvidenceError("thread id is not a UUID")

    session_root = codex_home / "sessions"
    matches = sorted(session_root.glob(f"**/rollout-*-{thread_id}.jsonl"))
    if len(matches) != 1:
        raise EvidenceError(
            f"expected exactly one persisted rollout for thread {thread_id}; "
            f"found {len(matches)}"
        )
    return matches[0]


def summarize_session(rollout_path: pathlib.Path) -> dict[str, Any]:
    cli_version: str | None = None
    model_provider: str | None = None
    models: list[str] = []
    root_turn_ordinals: dict[str, int] = {}
    compacted_ordinals: list[int] = []

    for record in iter_json_objects(rollout_path):
        record_type = record.get("type")
        payload = record.get("payload")
        payload = payload if isinstance(payload, dict) else {}
        ordinal = record.get("ordinal")

        if record_type == "session_meta":
            cli_version = str(payload.get("cli_version") or "unknown")
            model_provider = str(payload.get("model_provider") or "unknown")
        elif record_type == "turn_context" and isinstance(ordinal, int):
            root_turn_id = payload.get("root_turn_id") or payload.get("turn_id")
            root_turn_key = str(root_turn_id or f"ordinal:{ordinal}")
            root_turn_ordinals.setdefault(root_turn_key, ordinal)
            model = payload.get("model")
            if isinstance(model, str) and model not in models:
                models.append(model)
        elif record_type == "compacted" and isinstance(ordinal, int):
            compacted_ordinals.append(ordinal)

    distinct_turn_ordinals = list(root_turn_ordinals.values())
    compacted_before_second_turn = False
    if len(distinct_turn_ordinals) >= 2:
        compacted_before_second_turn = any(
            distinct_turn_ordinals[0] < compacted < distinct_turn_ordinals[1]
            for compacted in compacted_ordinals
        )

    return {
        "cli_version": cli_version or "unknown",
        "model_provider": model_provider or "unknown",
        "models": models,
        "turn_count": len(distinct_turn_ordinals),
        "compaction_count": len(compacted_ordinals),
        "compacted_before_second_turn": compacted_before_second_turn,
    }


def validate_session_summary(
    summary: dict[str, Any], *, require_compaction: bool
) -> None:
    if summary["turn_count"] < 2:
        raise EvidenceError("persisted session does not contain two root turns")
    if summary["cli_version"] == "unknown" or not summary["models"]:
        raise EvidenceError("Codex CLI version or model metadata is unavailable")
    if require_compaction and not summary["compacted_before_second_turn"]:
        raise EvidenceError(
            "no Codex compacted record was observed before the second root turn"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract bounded evidence from Codex multi-turn smoke artifacts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    thread_id = subparsers.add_parser("thread-id")
    thread_id.add_argument("log_path", type=pathlib.Path)

    route_record = subparsers.add_parser("route-record")
    route_record.add_argument("--skill", required=True)
    route_record.add_argument("log_path", type=pathlib.Path)

    assistant_excerpt = subparsers.add_parser("assistant-excerpt")
    assistant_excerpt.add_argument("log_path", type=pathlib.Path)

    summary = subparsers.add_parser("session-summary")
    summary.add_argument("--codex-home", required=True, type=pathlib.Path)
    summary.add_argument("--thread-id", required=True)
    summary.add_argument(
        "--require-compaction", choices=("true", "false"), default="false"
    )

    return parser


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "thread-id":
            print(extract_thread_id(args.log_path))
            return 0

        if args.command == "route-record":
            if not route_recorded(args.log_path, args.skill):
                raise EvidenceError(
                    f"no current-turn route record for {args.skill} was found"
                )
            return 0

        if args.command == "assistant-excerpt":
            print(first_assistant_excerpt(args.log_path))
            return 0

        rollout_path = find_rollout(args.codex_home, args.thread_id)
        summary = summarize_session(rollout_path)
        validate_session_summary(
            summary, require_compaction=args.require_compaction == "true"
        )
        print(json.dumps(summary, sort_keys=True))
        return 0
    except (EvidenceError, OSError) as error:
        print(f"evidence error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
