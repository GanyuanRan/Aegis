#!/usr/bin/env python3
"""Tests for scripts/aegis-deferred-ledger.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "aegis-deferred-ledger.py"
spec = importlib.util.spec_from_file_location("aegis_deferred_ledger", SCRIPT)
assert spec and spec.loader
ledger = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ledger
spec.loader.exec_module(ledger)

FOLLOWUP = "aegis-" + "followup:"
RETIRE = "aegis-" + "retire:"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_collects_valid_markers_and_skips_archive() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(
            root / "docs" / "note.md",
            f'# {FOLLOWUP} owner="docs" reason="baseline update" trigger="next host change" verification="run check"\n',
        )
        write(
            root / "src" / "adapter.py",
            f'# {RETIRE} owner="adapter" reason="legacy host" trigger="major review" verification="smoke test"\n',
        )
        write(root / "docs" / "archive" / "old.md", f"# {FOLLOWUP} owner=archive\n")

        entries, issues = ledger.collect(root)

    assert not issues
    assert [entry.kind for entry in entries] == ["followup", "retire"]
    assert {entry.owner for entry in entries} == {"docs", "adapter"}


def test_reports_missing_required_fields() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(root / "note.md", f"# {FOLLOWUP} owner=docs reason=needs-check\n")

        entries, issues = ledger.collect(root)

    assert not entries
    assert len(issues) == 1
    assert "trigger" in issues[0].message
    assert "verification" in issues[0].message


def test_ignores_markdown_fenced_examples() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write(
            root / "README.md",
            "```text\n"
            f'# {FOLLOWUP} owner="docs" reason="example" trigger="never" verification="none"\n'
            "```\n",
        )

        entries, issues = ledger.collect(root)

    assert not entries
    assert not issues
