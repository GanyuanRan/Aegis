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

RESULT_STATUS_RE = re.compile(
    r"^\s*(?P<status>succeeded|exited\s+\d+)\s+in\b.*:\s*$",
    re.IGNORECASE,
)

FRONTMATTER_NAME_RE = re.compile(
    r'''^\s*name\s*:\s*["']?(?P<skill>[A-Za-z0-9._-]+)["']?\s*$''',
    re.IGNORECASE,
)

FRONTMATTER_DESCRIPTION_RE = re.compile(r"^\s*description\s*:", re.IGNORECASE)

RESULT_BOUNDARY_MARKERS = {"exec", "codex", "tokens used"}

SKILL_PATH_RE = re.compile(
    r"""(?<![A-Za-z0-9._-])skills
    (?:[\\/]+[A-Za-z0-9._-]+)*
    [\\/]+(?P<skill>[A-Za-z0-9._-]+)
    [\\/]+SKILL\.md
    """,
    re.IGNORECASE | re.VERBOSE,
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

    return []


def extract_skill_from_line(line: str) -> str | None:
    skills = extract_skills_from_line(line)
    return skills[0] if skills else None


def iter_skill_read_attempts(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
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


def extract_skill_names_from_result(lines: list[str]) -> list[str]:
    """Return skill names proven by frontmatter in one successful exec result."""

    skills: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].strip() != "---":
            index += 1
            continue

        closing = index + 1
        while closing < len(lines) and lines[closing].strip() != "---":
            closing += 1
        if closing >= len(lines):
            break

        header = lines[index + 1 : closing]
        name: str | None = None
        has_description = False
        for line in header:
            match = FRONTMATTER_NAME_RE.match(line)
            if match:
                name = match.group("skill")
            if FRONTMATTER_DESCRIPTION_RE.match(line):
                has_description = True
        if name and has_description:
            skills.append(name)
        index = closing + 1

    return skills


def iter_successful_skill_results(lines: list[str]) -> Iterator[tuple[int, str]]:
    for index, line in enumerate(lines):
        status = RESULT_STATUS_RE.match(line)
        if not status or status.group("status").lower() != "succeeded":
            continue

        result_lines: list[str] = []
        for candidate in lines[index + 1 :]:
            if RESULT_STATUS_RE.match(candidate):
                break
            if candidate.strip() in RESULT_BOUNDARY_MARKERS:
                break
            result_lines.append(candidate)

        for skill in extract_skill_names_from_result(result_lines):
            yield index + 1, skill


def iter_skill_load_events(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    """Yield reads whose successful result proves the requested skill was loaded."""

    materialized = list(lines)
    attempts = [
        (ordinal, line_number, skill)
        for ordinal, (line_number, skill) in enumerate(
            iter_skill_read_attempts(materialized)
        )
    ]
    confirmed_attempts: set[int] = set()

    for result_line, skill in iter_successful_skill_results(materialized):
        candidates = [
            attempt
            for attempt in attempts
            if attempt[0] not in confirmed_attempts
            and attempt[1] < result_line
            and attempt[2] == skill
        ]
        if candidates:
            confirmed_attempts.add(candidates[-1][0])

    for ordinal, line_number, skill in attempts:
        if ordinal in confirmed_attempts:
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
