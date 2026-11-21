"""Workspace structure checks and process-pressure metrics: ``check``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .adr import validate_adr_file
from .artifacts import infer_artifact_type, validate_artifact_file
from .evidence import ATTEMPT_CONVERGENCE_WARNING, evidence_bundle_status
from .index import read_index_paths
from .inputs import load_json_file
from .layout import (
    CORE_FILES,
    GOVERNANCE_TEMPLATE_PROFILES,
    WORKSPACE_DIRS,
    WORKSPACE_REL,
    resolve_root,
    workspace,
)


def workspace_markdown_files(ws: Path) -> list[str]:
    paths = []
    for path in sorted(ws.rglob("*.md")):
        if path.name in CORE_FILES and path.parent == ws:
            continue
        paths.append(path.relative_to(ws.parent.parent).as_posix())
    return paths


def recognizable_artifact_json_files(ws: Path) -> list[tuple[str, Path]]:
    files = []
    for path in sorted(ws.rglob("*.json")):
        artifact_type = infer_artifact_type(path)
        if artifact_type:
            files.append((artifact_type, path))
    return files


def process_artifact_pressure(ws: Path) -> list[str]:
    output: list[str] = []
    work_root = ws / "work"
    if not work_root.is_dir():
        return output
    for work_path in sorted(path for path in work_root.iterdir() if path.is_dir()):
        evidence_paths = sorted(work_path.glob("evidence-bundle-draft*.json"))
        terminal = 0
        attempted = 0
        legacy = 0
        superseded = 0
        max_attempts = 0
        for evidence_path in evidence_paths:
            status = evidence_bundle_status(evidence_path)
            if status == "evidence-finalized":
                terminal += 1
            elif status in {"blocked", "abandoned"}:
                terminal += 1
            elif status == "attempted":
                attempted += 1
            elif status == "superseded":
                superseded += 1
            else:
                legacy += 1
            data = load_json_file(evidence_path)
            if isinstance(data, dict):
                attempt_summary = data.get("attemptSummary", {})
                if isinstance(attempt_summary, dict):
                    max_attempts = max(max_attempts, int(attempt_summary.get("total", 0) or 0))

        def line_count(name: str) -> int:
            path = work_path / name
            return len(path.read_text(encoding="utf-8").splitlines()) if path.exists() else 0

        rel = (WORKSPACE_REL / "work" / work_path.name).as_posix()
        output.append(f"process_artifact_pressure: {rel}")
        output.append(f"  evidence_sidecars: {len(evidence_paths)}")
        output.append(f"  checkpoint_lines: {line_count('20-checkpoint.md')}")
        output.append(f"  evidence_lines: {line_count('90-evidence.md')}")
        output.append(f"  terminal_evidence: {terminal}")
        output.append(f"  attempted_evidence: {attempted}")
        output.append(f"  legacy_unclassified: {legacy}")
        output.append(f"  superseded: {superseded}")
        output.append(f"  max_attempts_per_slice: {max_attempts}")
        if attempted and max_attempts >= ATTEMPT_CONVERGENCE_WARNING:
            output.append(
                "  convergence-stop: stop auto-retry and route to systematic-debugging "
                "or verification-before-completion before another attempt."
            )
    return output


def command_check(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    ws = workspace(root)
    failures: list[str] = []

    if not ws.exists():
        failures.append(f"missing workspace directory: {WORKSPACE_REL.as_posix()}")
    else:
        for directory in WORKSPACE_DIRS:
            if not (ws / directory).is_dir():
                failures.append(f"missing workspace directory: {(WORKSPACE_REL / directory).as_posix()}")
        for filename in CORE_FILES:
            if not (ws / filename).is_file():
                failures.append(f"missing workspace file: {(WORKSPACE_REL / filename).as_posix()}")

    governance_path = ws / "BASELINE-GOVERNANCE.md"
    if governance_path.exists():
        governance = governance_path.read_text(encoding="utf-8")
        governance_matches = [
            profile_name
            for profile_name, phrases in GOVERNANCE_TEMPLATE_PROFILES
            if all(phrase in governance for phrase in phrases)
        ]
        if not governance_matches:
            current_phrases = GOVERNANCE_TEMPLATE_PROFILES[0][1]
            for phrase in current_phrases:
                if phrase not in governance:
                    failures.append(f"BASELINE-GOVERNANCE.md missing phrase: {phrase}")

    index_path = ws / "INDEX.md"
    if index_path.exists() and ws.exists():
        indexed_paths = read_index_paths(index_path)
        for indexed_path in sorted(indexed_paths):
            file_path = root / Path(indexed_path)
            if not file_path.is_file():
                failures.append(f"INDEX.md points at a missing workspace file: {indexed_path}")
        for rel_path in workspace_markdown_files(ws):
            if rel_path not in indexed_paths:
                failures.append(f"workspace markdown is not indexed: {rel_path}")
        for adr_path in sorted((ws / "adr").glob("*.md")):
            failures.extend(validate_adr_file(adr_path))

    if ws.exists():
        for artifact_type, path in recognizable_artifact_json_files(ws):
            failures.extend(validate_artifact_file(artifact_type, path))

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    if getattr(args, "process_pressure", False) and ws.exists():
        for line in process_artifact_pressure(ws):
            print(line)

    print(f"Aegis workspace check passed: {ws}")
    return 0
