#!/usr/bin/env python3
"""Scan Aegis deferred-work markers."""

from __future__ import annotations

import argparse
import json
import os
import shlex
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


FOLLOWUP_PREFIX = "aegis-" + "followup:"
RETIRE_PREFIX = "aegis-" + "retire:"
REQUIRED_FIELDS = ("owner", "reason", "trigger", "verification")
SKIP_PARTS = {".git", ".tmp", ".worktrees", "node_modules", "__pycache__", ".serena"}
SKIP_RELATIVE_PREFIXES = {
    Path("docs/archive"),
    Path("tests/local"),
    Path(".opencode/node_modules"),
}


@dataclass(frozen=True)
class LedgerEntry:
    kind: str
    path: str
    line: int
    owner: str
    reason: str
    trigger: str
    verification: str
    raw: str


@dataclass(frozen=True)
class LedgerIssue:
    path: str
    line: int
    message: str
    raw: str


def is_skipped_relative(rel: Path) -> bool:
    if any(part in SKIP_PARTS for part in rel.parts):
        return True
    return any(rel == prefix or prefix in rel.parents for prefix in SKIP_RELATIVE_PREFIXES)


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        current_rel = current_path.relative_to(root)
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if not is_skipped_relative(current_rel / dirname)
        ]
        for filename in filenames:
            path = current_path / filename
            rel = path.relative_to(root)
            if not is_skipped_relative(rel):
                yield path


def parse_fields(payload: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for token in shlex.split(payload, posix=True):
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        fields[key.strip()] = value.strip()
    return fields


def parse_line(path: Path, root: Path, line_number: int, line: str) -> tuple[LedgerEntry | None, LedgerIssue | None]:
    prefixes = ((FOLLOWUP_PREFIX, "followup"), (RETIRE_PREFIX, "retire"))
    for prefix, kind in prefixes:
        marker_index = line.find(prefix)
        if marker_index < 0:
            continue
        payload = line[marker_index + len(prefix) :].strip()
        try:
            fields = parse_fields(payload)
        except ValueError as exc:
            return None, LedgerIssue(path.as_posix(), line_number, f"cannot parse marker fields: {exc}", line.strip())
        missing = [field for field in REQUIRED_FIELDS if not fields.get(field)]
        if missing:
            return None, LedgerIssue(
                path.relative_to(root).as_posix(),
                line_number,
                f"missing fields: {', '.join(missing)}",
                line.strip(),
            )
        return (
            LedgerEntry(
                kind=kind,
                path=path.relative_to(root).as_posix(),
                line=line_number,
                owner=fields["owner"],
                reason=fields["reason"],
                trigger=fields["trigger"],
                verification=fields["verification"],
                raw=line.strip(),
            ),
            None,
        )
    return None, None


def collect(root: Path) -> tuple[list[LedgerEntry], list[LedgerIssue]]:
    entries: list[LedgerEntry] = []
    issues: list[LedgerIssue] = []
    for path in iter_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        in_fenced_block = False
        for index, line in enumerate(lines, start=1):
            if path.suffix.lower() == ".md" and line.lstrip().startswith("```"):
                in_fenced_block = not in_fenced_block
                continue
            if in_fenced_block:
                continue
            entry, issue = parse_line(path, root, index, line)
            if entry:
                entries.append(entry)
            if issue:
                issues.append(issue)
    return entries, issues


def render_text(entries: list[LedgerEntry], issues: list[LedgerIssue]) -> str:
    lines: list[str] = []
    if not entries:
        lines.append("No Aegis deferred ledger markers found.")
    else:
        lines.append("Aegis deferred ledger:")
        for entry in entries:
            lines.append(
                f"- {entry.kind} {entry.path}:{entry.line} owner={entry.owner} "
                f"trigger={entry.trigger} verification={entry.verification}"
            )
    if issues:
        lines.append("")
        lines.append("Malformed markers:")
        for issue in issues:
            lines.append(f"- {issue.path}:{issue.line} {issue.message}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Aegis deferred-work markers.")
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--fail-on-vague", action="store_true", help="exit nonzero when malformed markers are found")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    entries, issues = collect(root)
    if args.json:
        print(
            json.dumps(
                {
                    "entries": [asdict(entry) for entry in entries],
                    "issues": [asdict(issue) for issue in issues],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(render_text(entries, issues))
    return 1 if args.fail_on_vague and issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
