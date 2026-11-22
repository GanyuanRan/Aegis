"""File writes for the workspace helper.

Every write goes through this module: UTF-8 text with LF newlines, written
through ``Path.open`` because ``Path.write_text`` has no ``newline`` argument
on Python 3.9 and older.
"""

from __future__ import annotations

import json
from pathlib import Path


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    write_text_lf(path, content)
    return True


def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def append_text_lf(path: Path, content: str) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_json(path: Path, data: dict) -> None:
    write_text_lf(
        path,
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
    )
