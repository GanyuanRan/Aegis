#!/usr/bin/env python3
"""Validate host and global instruction invariant coverage."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing instruction surface: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def validate_surface(repo_root: Path, surface: dict[str, Any]) -> None:
    rel_path = surface.get("path")
    require(isinstance(rel_path, str) and rel_path, "surface path must be non-empty")
    path = repo_root / rel_path
    text = read_text(path)
    for pattern in surface.get("requiredRegex", []):
        require(
            re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE),
            f"{rel_path} missing invariant pattern: {pattern}",
        )
    for pattern in surface.get("forbiddenRegex", []):
        require(
            not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE),
            f"{rel_path} contains forbidden role-overlap pattern: {pattern}",
        )
    max_chars = surface.get("maxChars")
    if max_chars is not None:
        require(len(text) <= int(max_chars), f"{rel_path} exceeds maxChars={max_chars}")
    max_lines = surface.get("maxLines")
    if max_lines is not None:
        require(len(text.splitlines()) <= int(max_lines), f"{rel_path} exceeds maxLines={max_lines}")


def validate_forbidden_claims(repo_root: Path, surfaces: list[dict[str, Any]], claims: list[str]) -> None:
    for surface in surfaces:
        rel_path = surface["path"]
        text = read_text(repo_root / rel_path)
        lower = text.lower()
        for claim in claims:
            require(
                claim.lower() not in lower,
                f"{rel_path} contains forbidden positive claim: {claim}",
            )


def validate_matrix(repo_root: Path, fixture: Path) -> None:
    data = json.loads(fixture.read_text(encoding="utf-8"))
    require(data.get("version") == 1, "version must be 1")
    required = set(data.get("requiredSurfaces", []))
    surfaces = data.get("surfaces", [])
    require(isinstance(surfaces, list) and surfaces, "surfaces must be a non-empty list")
    surface_paths = {surface.get("path") for surface in surfaces}
    missing = sorted(required - surface_paths)
    require(not missing, f"missing required surfaces: {', '.join(missing)}")
    for surface in surfaces:
        validate_surface(repo_root, surface)
    claims = data.get("forbiddenPositiveClaims", [])
    require(isinstance(claims, list), "forbiddenPositiveClaims must be a list")
    validate_forbidden_claims(repo_root, surfaces, claims)
    require(not (repo_root / "docs" / "aegis").exists(), "Aegis method-pack repo must not ship docs/aegis workspace records")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: validate_host_instruction_invariants.py <repo-root> <fixture-json>")
    validate_matrix(Path(argv[1]), Path(argv[2]))
    print("  [PASS] host instruction invariants preserve projection roles, semantics, and budgets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
