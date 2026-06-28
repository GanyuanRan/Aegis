#!/usr/bin/env python3
"""Normalize live host replay output for the transcript analyzer."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Iterable


def load_parse_codex_module():
    module_path = Path(__file__).with_name("parse_codex_skills.py")
    spec = importlib.util.spec_from_file_location("parse_codex_skills", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for item in value.values():
            yield from flatten_strings(item)
        return
    if isinstance(value, list):
        for item in value:
            yield from flatten_strings(item)


def normalize_claude(raw_log: Path, prompt_path: Path, transcript_path: Path) -> None:
    entries = []
    saw_user_prompt = False
    for raw_line in raw_log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") == "user":
            text = "\n".join(flatten_strings(entry))
            if prompt_path.read_text(encoding="utf-8").strip() in text:
                saw_user_prompt = True
        entries.append(entry)

    if not saw_user_prompt:
        entries.insert(
            0,
            {
                "type": "user",
                "message": {
                    "content": [
                        {"type": "text", "text": prompt_path.read_text(encoding="utf-8")}
                    ]
                },
            },
        )

    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries),
        encoding="utf-8",
    )


def extract_codex_assistant_text(lines: list[str]) -> str:
    chunks: list[str] = []
    for index, line in enumerate(lines):
        if line.strip() != "codex":
            continue
        if index + 1 < len(lines):
            candidate = lines[index + 1].strip()
            if candidate:
                chunks.append(candidate)
    if chunks:
        return "\n".join(chunks)

    tail = "\n".join(lines[-80:])
    return tail.strip()


def normalize_codex(raw_log: Path, prompt_path: Path, transcript_path: Path) -> None:
    parser = load_parse_codex_module()
    lines = raw_log.read_text(encoding="utf-8", errors="replace").splitlines()
    skills = list(parser.iter_loaded_skills(lines))
    assistant_text = extract_codex_assistant_text(lines)

    entries: list[dict[str, Any]] = [
        {
            "type": "user",
            "message": {
                "content": [
                    {"type": "text", "text": prompt_path.read_text(encoding="utf-8")}
                ]
            },
        }
    ]
    for skill in skills:
        entries.append(
            {
                "type": "user",
                "toolUseResult": {
                    "name": "Skill",
                    "skill": skill,
                    "prompt": "Detected from live Codex replay log",
                },
            }
        )
    entries.append(
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text", "text": assistant_text}
                ]
            },
        }
    )

    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(
        "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in entries),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["claude", "codex"], required=True)
    parser.add_argument("--raw-log", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    args = parser.parse_args()

    if args.host == "claude":
        normalize_claude(args.raw_log, args.prompt, args.transcript)
    else:
        normalize_codex(args.raw_log, args.prompt, args.transcript)
    print(f"Normalized live replay transcript: {args.transcript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
