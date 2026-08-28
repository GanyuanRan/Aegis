#!/usr/bin/env python3

from __future__ import annotations

import argparse
import pathlib
import re
import shlex
import sys
from typing import Iterable, Iterator


POWERSHELL_COMMAND_PREFIX_RE = re.compile(
    r"""^\s*"
    [^"\r\n]*?(?:pwsh|powershell)\.exe"
    \s+-Command\s+["']
    """,
    re.IGNORECASE | re.VERBOSE,
)

POSIX_SHELL_COMMAND_PREFIX_RE = re.compile(
    r"""^\s*(?:/(?:usr/)?bin/)?(?:bash|sh)\s+-lc\s+["']""",
    re.IGNORECASE,
)

CMD_COMMAND_PREFIX_RE = re.compile(
    r'''^\s*"[^"\r\n]*?cmd\.exe"\s+/(?:d\s+/)?c\s+["']''',
    re.IGNORECASE,
)

SKILL_PATH_RE = re.compile(
    r"""(?<![A-Za-z0-9._-])skills
    (?:[\\/]+[A-Za-z0-9._-]+)*
    [\\/]+(?P<skill>[A-Za-z0-9._-]+)
    [\\/]+SKILL\.md
    """,
    re.IGNORECASE | re.VERBOSE,
)

SKILL_PATH_LINE_RE = re.compile(
    r"""^skills[/\\](?P<skill>[A-Za-z0-9._-]+)[/\\]SKILL\.md\s*$""",
    re.IGNORECASE,
)

FOREACH_RE = re.compile(
    r"""\bforeach\s*\([^)]*?\$(?P<item>[A-Za-z_][A-Za-z0-9_]*)
    \s+in\s+\$(?P<collection>[A-Za-z_][A-Za-z0-9_]*)\s*\)""",
    re.IGNORECASE | re.VERBOSE,
)

POWERSHELL_COMMAND_END_RE = re.compile(r'''["']\s+in\s+''', re.IGNORECASE)


def extract_skills_from_foreach_read(command_text: str) -> list[str]:
    foreach_match = FOREACH_RE.search(command_text)
    if not foreach_match:
        return []

    item = foreach_match.group("item")
    collection = foreach_match.group("collection")
    if not re.search(
        rf"\bGet-Content\b[^;}}]*\${re.escape(item)}\b",
        command_text,
        re.IGNORECASE,
    ):
        return []

    assignment = re.search(
        rf"\${re.escape(collection)}\s*=\s*@\((?P<body>.*?)\)\s*;",
        command_text,
        re.IGNORECASE,
    )
    if not assignment:
        return []

    return [
        match.group("skill")
        for match in SKILL_PATH_RE.finditer(assignment.group("body"))
    ]


def extract_skills_from_posix_shell_read(command_text: str) -> list[str]:
    command_text = re.sub(r'''["']\s+in\s+.*$''', "", command_text)
    skills: list[str] = []

    for segment in re.split(r"\s*(?:&&|;)\s*", command_text):
        try:
            argv = shlex.split(segment)
        except ValueError:
            continue
        if not argv or pathlib.PurePosixPath(argv[0]).name not in {"cat", "sed"}:
            continue

        for argument in argv[1:]:
            match = SKILL_PATH_RE.search(argument)
            if match and match.end() == len(argument):
                skills.append(match.group("skill"))

    return skills


def extract_skills_from_powershell_command(command_text: str) -> list[str]:
    skills: list[str] = []
    for segment in command_text.split(";"):
        invocation = segment.lstrip(" \t\"'")
        if not re.match(r"Get-Content\b", invocation, re.IGNORECASE):
            continue
        direct_invocation = invocation.split("|", 1)[0]
        skills.extend(
            match.group("skill") for match in SKILL_PATH_RE.finditer(direct_invocation)
        )
    return skills or extract_skills_from_foreach_read(command_text)


def extract_skills_from_cmd_type(command_text: str) -> list[str]:
    command_text = re.sub(r'''["']\s+in\s+.*$''', "", command_text)
    skills: list[str] = []
    for segment in re.split(r"\s*(?:&&|&)\s*", command_text):
        invocation = segment.lstrip(" \t\"'")
        if not re.match(r"type\b", invocation, re.IGNORECASE):
            continue
        skills.extend(match.group("skill") for match in SKILL_PATH_RE.finditer(invocation))
    return skills


def extract_skills_from_line(line: str) -> list[str]:
    command_prefix = POWERSHELL_COMMAND_PREFIX_RE.search(line)
    if command_prefix:
        return extract_skills_from_powershell_command(line[command_prefix.end() :])

    posix_prefix = POSIX_SHELL_COMMAND_PREFIX_RE.search(line)
    if posix_prefix:
        return extract_skills_from_posix_shell_read(line[posix_prefix.end() :])

    cmd_prefix = CMD_COMMAND_PREFIX_RE.search(line)
    if cmd_prefix:
        return extract_skills_from_cmd_type(line[cmd_prefix.end() :])

    path_match = SKILL_PATH_LINE_RE.search(line)
    if path_match:
        return [path_match.group("skill")]

    return []


def extract_skill_from_line(line: str) -> str | None:
    skills = extract_skills_from_line(line)
    return skills[0] if skills else None


def iter_skill_load_events(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    powershell_continuation = False
    for line_number, line in enumerate(lines, start=1):
        command_prefix = POWERSHELL_COMMAND_PREFIX_RE.search(line)
        if command_prefix:
            command_text = line[command_prefix.end() :]
            skills = extract_skills_from_powershell_command(command_text)
            powershell_continuation = not bool(
                POWERSHELL_COMMAND_END_RE.search(command_text)
            )
        elif powershell_continuation:
            command_ended = bool(POWERSHELL_COMMAND_END_RE.search(line))
            direct_get_content = bool(
                re.match(r"^\s*Get-Content\b", line, re.IGNORECASE)
            )
            skills = (
                extract_skills_from_powershell_command(line)
                if command_ended and direct_get_content
                else []
            )
            if command_ended:
                powershell_continuation = False
        else:
            skills = extract_skills_from_line(line)

        for skill in skills:
            yield line_number, skill


def iter_loaded_skills(lines: Iterable[str]) -> Iterator[str]:
    seen: set[str] = set()
    for _, skill in iter_skill_load_events(lines):
        if skill not in seen:
            seen.add(skill)
            yield skill


def first_skill_load_line(lines: Iterable[str], skill_name: str) -> int | None:
    for line_number, skill in iter_skill_load_events(lines):
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
