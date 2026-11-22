"""``INDEX.md`` reading and appending, and the ``append-index`` command."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .errors import WorkspaceError
from .layout import WORKSPACE_REL, resolve_root, workspace
from .textio import append_text_lf


def normalize_workspace_path(root: Path, input_path: str) -> tuple[str, Path]:
    candidate = Path(input_path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()

    ws = workspace(root).resolve()
    try:
        rel_to_ws = candidate.relative_to(ws)
    except ValueError as exc:
        raise WorkspaceError(f"path must be inside {WORKSPACE_REL.as_posix()}: {candidate}") from exc

    if rel_to_ws.name == "":
        raise WorkspaceError("path must reference a file inside docs/aegis")

    return (WORKSPACE_REL / rel_to_ws).as_posix(), candidate


def read_index_paths(index_path: Path) -> set[str]:
    if not index_path.exists():
        return set()
    paths: set[str] = set()
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) < 4:
            continue
        path = columns[2]
        if path.startswith("docs/aegis/"):
            paths.add(path)
    return paths


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").strip()


def append_index_entry(
    root: Path,
    input_path: str,
    kind: str,
    title: str,
    entry_date: str | None = None,
) -> bool:
    ws = workspace(root)
    if not ws.exists():
        raise WorkspaceError(f"workspace does not exist: {ws}")
    index_path = ws / "INDEX.md"
    if not index_path.exists():
        raise WorkspaceError(f"INDEX.md does not exist: {index_path}")

    rel_path, file_path = normalize_workspace_path(root, input_path)
    if not file_path.is_file():
        raise WorkspaceError(f"path is not a file: {file_path}")

    indexed_paths = read_index_paths(index_path)
    if rel_path in indexed_paths:
        return False

    entry = (
        f"| {escape_cell(entry_date or date.today().isoformat())} | "
        f"{escape_cell(kind)} | {escape_cell(rel_path)} | {escape_cell(title)} |\n"
    )
    append_text_lf(index_path, entry)
    return True


def command_append_index(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    rel_path, file_path = normalize_workspace_path(root, args.path)
    if not append_index_entry(root, str(file_path), args.kind, args.title, args.date):
        print(f"Index already contains {rel_path}")
        return 0

    print(f"Indexed {rel_path}")
    return 0
