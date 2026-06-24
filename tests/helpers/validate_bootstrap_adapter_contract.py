#!/usr/bin/env python3
"""Validate that bootstrap adapters stay thin and canonical-source based."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_adapter(repo_root: Path, adapter: dict[str, Any], canonical_text: str) -> None:
    rel_path = adapter.get("path")
    require(isinstance(rel_path, str) and rel_path, "adapter path must be non-empty")
    path = repo_root / rel_path
    require(path.exists(), f"missing bootstrap adapter: {rel_path}")
    text = path.read_text(encoding="utf-8")

    for pattern in adapter.get("requiredRegex", []):
        require(
            re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL),
            f"{rel_path} missing adapter contract pattern: {pattern}",
        )

    if adapter.get("referenceOnly"):
        require(
            len(text.splitlines()) <= 8,
            f"{rel_path} should remain a short host-native reference adapter",
        )
        return

    canonical_body_snippet = "\n".join(canonical_text.splitlines()[5:20]).strip()
    require(
        canonical_body_snippet not in text,
        f"{rel_path} appears to copy a large using-aegis body instead of sourcing it",
    )

    forbidden_positive = [
        "grants completion authority",
        "authoritative GateDecision",
        "authoritative PolicySnapshot",
    ]
    lowered = text.lower()
    for claim in forbidden_positive:
        require(claim.lower() not in lowered, f"{rel_path} contains forbidden authority claim: {claim}")


def validate_contract(repo_root: Path, fixture: Path) -> None:
    data = json.loads(fixture.read_text(encoding="utf-8"))
    require(data.get("version") == 1, "version must be 1")
    canonical_rel = data.get("canonicalHotPath")
    require(isinstance(canonical_rel, str), "canonicalHotPath must be a string")
    canonical_path = repo_root / canonical_rel
    require(canonical_path.exists(), f"missing canonical hot path: {canonical_rel}")
    canonical_text = canonical_path.read_text(encoding="utf-8")
    require("name: using-aegis" in canonical_text, "canonical hot path must be using-aegis")

    adapters = data.get("adapters", [])
    require(isinstance(adapters, list) and len(adapters) >= 3, "adapters must list host bootstrap surfaces")
    for adapter in adapters:
        validate_adapter(repo_root, adapter, canonical_text)

    allowed = set(data.get("allowedAdapterResponsibilities", []))
    forbidden = set(data.get("forbiddenAdapterResponsibilities", []))
    require("host-tool-mapping" in allowed, "adapter contract must allow host tool mapping")
    require("grant-completion-authority" in forbidden, "adapter contract must forbid completion authority")
    require("replace-task-specific-skills-with-one-large-prompt" in forbidden, "adapter contract must preserve lazy skill loading")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit("usage: validate_bootstrap_adapter_contract.py <repo-root> <fixture-json>")
    validate_contract(Path(argv[1]), Path(argv[2]))
    print("  [PASS] bootstrap adapters stay thin and source the canonical using-aegis hot path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
