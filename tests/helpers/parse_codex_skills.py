#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Iterable, Iterator


SKILL_LOAD_COMMAND_RE = re.compile(
    r"""^\s*"
    [^"\r\n]*?(?:pwsh|powershell)\.exe"
    \s+-Command\s+
    ["']
    Get-Content\b
    .*?
    (?:[^'"\r\n]*[\\/])?skills(?:[\\/]+[A-Za-z0-9._-]+)*[\\/]+(?P<skill>[A-Za-z0-9._-]+)[\\/]+SKILL\.md
    """,
    re.IGNORECASE | re.VERBOSE,
)

SKILL_PATH_LINE_RE = re.compile(
    r"""^skills[/\\](?P<skill>[A-Za-z0-9._-]+)[/\\]SKILL\.md\s*$""",
    re.IGNORECASE,
)


def extract_skill_from_line(line: str) -> str | None:
    command_match = SKILL_LOAD_COMMAND_RE.search(line)
    if command_match:
        return command_match.group("skill")

    path_match = SKILL_PATH_LINE_RE.search(line)
    if path_match:
        return path_match.group("skill")

    return None


def iter_loaded_skills(lines: Iterable[str]) -> Iterator[str]:
    seen: set[str] = set()
    for line in lines:
        skill = extract_skill_from_line(line)
        if skill and skill not in seen:
            seen.add(skill)
            yield skill


def first_skill_load_line(lines: Iterable[str], skill_name: str) -> int | None:
    for line_number, line in enumerate(lines, start=1):
        skill = extract_skill_from_line(line)
        if skill == skill_name:
            return line_number
    return None


def read_lines(log_file: pathlib.Path) -> list[str]:
    return log_file.read_text(encoding="utf-8", errors="replace").splitlines()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse Codex skill-load lines from a smoke transcript.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    loaded_skills = subparsers.add_parser("loaded-skills")
    loaded_skills.add_argument("log_file", type=pathlib.Path)

    first_line = subparsers.add_parser("first-skill-load-line")
    first_line.add_argument("log_file", type=pathlib.Path)
    first_line.add_argument("skill_name")

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    lines = read_lines(args.log_file)

    if args.command == "loaded-skills":
        for skill in iter_loaded_skills(lines):
            print(skill)
        return 0

    if args.command == "first-skill-load-line":
        line_number = first_skill_load_line(lines, args.skill_name)
        if line_number is not None:
            print(line_number)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
