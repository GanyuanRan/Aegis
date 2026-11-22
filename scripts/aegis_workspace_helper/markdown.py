"""Markdown list rendering and section replacement for workspace records."""

from __future__ import annotations

import re
from pathlib import Path

from .textio import write_text_lf


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- none\n"
    return "".join(f"- {item}\n" for item in items)


def upsert_markdown_section(path: Path, heading: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = f"{heading}\n\n"
    pattern = re.compile(
        r"(?m)^" + re.escape(heading) + r"\n\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    replacement = marker + body.rstrip("\n") + "\n"
    if pattern.search(text):
        # A callable keeps the replacement literal; a template string would
        # treat backslashes in the body (for example Windows paths) as escapes.
        text = pattern.sub(lambda _match: replacement, text, count=1)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n" + replacement
    write_text_lf(path, text)
