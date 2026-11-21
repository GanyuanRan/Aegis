"""Readers and validators for JSON files and command-line values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .errors import WorkspaceError


def load_json_file(path: Path) -> object:
    if not path.is_file():
        raise WorkspaceError(f"artifact file does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkspaceError(f"{path}: invalid JSON ({exc})") from exc


def read_json_dict(path: Path) -> dict:
    data = load_json_file(path)
    if not isinstance(data, dict):
        raise WorkspaceError(f"{path}: expected JSON object")
    return data


def list_arg(values: list[str] | None) -> list[str]:
    return list(values or [])


def arg_value(args: argparse.Namespace, name: str, default: object = None) -> object:
    return getattr(args, name, default)


def optional_none(value: str | None) -> str | None:
    if value in (None, "", "none", "None"):
        return None
    return value


def require_text(value: str | None, label: str) -> str:
    text = (value or "").strip()
    if not text:
        raise WorkspaceError(f"{label} must not be empty")
    return text


def require_list(values: list[str] | None, label: str) -> list[str]:
    items = [item.strip() for item in list_arg(values) if item and item.strip()]
    if not items:
        raise WorkspaceError(f"{label} requires at least one value")
    return items
