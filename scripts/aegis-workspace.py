#!/usr/bin/env python3
"""Manage a target project's docs/aegis workspace.

This helper belongs to the Aegis Method Pack, but it writes only to the project
root explicitly passed by the caller. It validates workspace structure and
index coverage; it does not make authoritative governance decisions.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


WORKSPACE_REL = Path("docs") / "aegis"
SCHEMA_VERSION = "aegis.schema.v0"
INDEX_HEADER = """# Aegis Workspace Index

This index tracks files created under this project's `docs/aegis/` workspace.
Entries are workspace records, not authoritative runtime decisions.

| Date | Kind | Path | Title |
| --- | --- | --- | --- |
"""

README_TEXT = """# Aegis Project Workspace

This directory stores project-local Aegis method-pack records.

It may contain task intent, baseline snapshots, specs, plans, work checkpoints,
evidence notes, and reflection records for this project.

These files are advisory method-pack artifacts. They do not grant completion
authority, produce authoritative `GateDecision`, or replace this project's
existing authority docs.
"""

BASELINE_GOVERNANCE_TEXT = """# Baseline Governance

## 1. Architecture Defect
A confirmed error, gap, or contradiction IN the baseline itself.
- Fix baseline first, then align implementation to corrected baseline.
- Do NOT patch implementation around a defective baseline.

## 2. Architecture Drift
Implementation has deviated from a confirmed, correct baseline.
- Return to baseline via the simplest path.
- Do NOT "update baseline to match drift" without explicit review.

## 3. Baseline Check Protocol
Before non-trivial changes:
1. Read the latest baseline snapshot in `baseline/`
2. Compare current code structure against ownership map
3. Compare current contracts against contract inventory
4. Check for new anti-patterns not recorded in known list
5. Report: aligned / minor drift (self-correctable) / material drift (needs review)

## 4. Architecture Review - 7 Dimensions
After each non-trivial change:
1. **Ownership integrity** - every component has exactly one canonical owner
2. **Module boundaries** - no unauthorized cross-module coupling
3. **Contract changes** - all API/signature/behavior contract changes documented
4. **Cascade proliferation** - no new cascading dependency chains
5. **Dependency direction** - dependencies flow toward stability
6. **Retirement completeness** - old owners/fallbacks/paths removed or scheduled
7. **Entropy flow** - net complexity decreased or stayed; no unjustified new entities

## 5. Hard Boundaries
- BASELINE-GOVERNANCE.md is the constitution for THIS project's Aegis workspace
- Baseline snapshots in `baseline/` are evidence, not authority
- ADRs in `adr/` record decisions; they do not replace baseline governance
- This file is NEVER auto-updated - changes require explicit user review
"""

WORKSPACE_DIRS = ("adr", "baseline", "specs", "plans", "work")
CORE_FILES = ("README.md", "INDEX.md", "BASELINE-GOVERNANCE.md")
GOVERNANCE_REQUIRED_PHRASES = (
    "## 1. Architecture Defect",
    "## 2. Architecture Drift",
    "## 3. Baseline Check Protocol",
    "## 4. Architecture Review",
    "## 5. Hard Boundaries",
    "evidence, not authority",
    "NEVER auto-updated",
)
ARTIFACT_SCHEMAS = {
    "TaskIntentDraft": (
        "schemaVersion",
        "requestedOutcome",
        "scope",
        "changeKinds",
        "riskHints",
    ),
    "BaselineReadSetHint": (
        "schemaVersion",
        "candidateDocs",
        "whyRelevant",
        "missingAuthority",
    ),
    "ImpactStatementDraft": (
        "schemaVersion",
        "affectedLayers",
        "owners",
        "invariants",
        "compatBoundary",
        "nonGoals",
    ),
    "EvidenceBundleDraft": (
        "schemaVersion",
        "artifactKey",
        "type",
        "source",
        "summary",
        "verifier",
    ),
    "GateInputPack": (
        "schemaVersion",
        "baselineRefs",
        "impactStatement",
        "compatPlan",
        "retirementPlan",
        "evidenceBundle",
    ),
    "TodoCheckpointDraft": (
        "schemaVersion",
        "taskId",
        "currentTodo",
        "completedTodos",
        "activeSlice",
        "evidenceRefs",
        "blockedOn",
        "nextStep",
        "updatedAt",
    ),
    "ResumeStateHint": (
        "schemaVersion",
        "taskId",
        "lastCheckpointRef",
        "resumeInstruction",
        "knownPartialWork",
        "mustReadBeforeContinuing",
        "unsafeToAssume",
    ),
    "DriftCheckDraft": (
        "schemaVersion",
        "taskId",
        "taskIntentRef",
        "baselineRefs",
        "scopeStatus",
        "compatStatus",
        "retirementStatus",
        "newRiskSignals",
        "decision",
    ),
}
ARTIFACT_FILENAME_TYPES = {
    "task-intent-draft": "TaskIntentDraft",
    "baseline-read-set-hint": "BaselineReadSetHint",
    "impact-statement-draft": "ImpactStatementDraft",
    "evidence-bundle-draft": "EvidenceBundleDraft",
    "gate-input-pack": "GateInputPack",
    "todo-checkpoint-draft": "TodoCheckpointDraft",
    "resume-state-hint": "ResumeStateHint",
    "drift-check-draft": "DriftCheckDraft",
}
DRIFT_DECISIONS = {
    "continue",
    "pause-for-user",
    "needs-baseline-readback",
    "needs-verification",
    "blocked",
}


class WorkspaceError(Exception):
    pass


def resolve_root(root_arg: str) -> Path:
    root = Path(root_arg).expanduser().resolve()
    if not root.exists():
        raise WorkspaceError(f"root does not exist: {root}")
    if not root.is_dir():
        raise WorkspaceError(f"root is not a directory: {root}")
    return root


def workspace(root: Path) -> Path:
    return root / WORKSPACE_REL


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def command_init(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    ws = workspace(root)
    ws.mkdir(parents=True, exist_ok=True)

    for directory in WORKSPACE_DIRS:
        (ws / directory).mkdir(parents=True, exist_ok=True)

    created = []
    if write_if_missing(ws / "README.md", README_TEXT):
        created.append("README.md")
    if write_if_missing(ws / "INDEX.md", INDEX_HEADER):
        created.append("INDEX.md")
    if write_if_missing(ws / "BASELINE-GOVERNANCE.md", BASELINE_GOVERNANCE_TEXT):
        created.append("BASELINE-GOVERNANCE.md")

    if created:
        print(f"Initialized {WORKSPACE_REL.as_posix()} in {root}")
        print("Created: " + ", ".join(created))
    else:
        print(f"{WORKSPACE_REL.as_posix()} already initialized in {root}")
    return 0


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


def command_append_index(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    ws = workspace(root)
    if not ws.exists():
        raise WorkspaceError(f"workspace does not exist: {ws}")
    index_path = ws / "INDEX.md"
    if not index_path.exists():
        raise WorkspaceError(f"INDEX.md does not exist: {index_path}")

    rel_path, file_path = normalize_workspace_path(root, args.path)
    if not file_path.is_file():
        raise WorkspaceError(f"path is not a file: {file_path}")

    indexed_paths = read_index_paths(index_path)
    if rel_path in indexed_paths:
        print(f"Index already contains {rel_path}")
        return 0

    entry_date = args.date or date.today().isoformat()
    entry = (
        f"| {escape_cell(entry_date)} | {escape_cell(args.kind)} | "
        f"{escape_cell(rel_path)} | {escape_cell(args.title)} |\n"
    )
    with index_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(entry)
    print(f"Indexed {rel_path}")
    return 0


def infer_artifact_type(path: Path) -> str | None:
    filename = path.name.lower()
    if not filename.endswith(".json"):
        return None
    stem = filename[:-5]
    for prefix, artifact_type in ARTIFACT_FILENAME_TYPES.items():
        if stem == prefix or stem.startswith(f"{prefix}-"):
            return artifact_type
    return None


def load_json_file(path: Path) -> object:
    if not path.is_file():
        raise WorkspaceError(f"artifact file does not exist: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkspaceError(f"{path}: invalid JSON ({exc})") from exc


def validate_artifact_data(artifact_type: str, data: object, source: Path) -> list[str]:
    fields = ARTIFACT_SCHEMAS.get(artifact_type)
    if fields is None:
        return [f"{source}: unknown artifact type: {artifact_type}"]
    if not isinstance(data, dict):
        return [f"{source}: artifact must be a JSON object"]

    failures = []
    for field in fields:
        if field not in data:
            failures.append(f"{source}: {artifact_type} missing field: {field}")

    schema_version = data.get("schemaVersion")
    if schema_version != SCHEMA_VERSION:
        failures.append(
            f"{source}: schemaVersion must be {SCHEMA_VERSION}, got {schema_version}"
        )

    if artifact_type == "DriftCheckDraft":
        decision = data.get("decision")
        if decision not in DRIFT_DECISIONS:
            failures.append(
                f"{source}: DriftCheckDraft decision must be advisory, got {decision}"
            )

    return failures


def validate_artifact_file(artifact_type: str, path: Path) -> list[str]:
    data = load_json_file(path)
    return validate_artifact_data(artifact_type, data, path)


def command_validate_artifact(args: argparse.Namespace) -> int:
    path = Path(args.file).expanduser().resolve()
    artifact_type = args.type or infer_artifact_type(path)
    if not artifact_type:
        raise WorkspaceError(f"could not infer artifact type from filename: {path.name}")

    failures = validate_artifact_file(artifact_type, path)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"{artifact_type} structure check passed: {path}")
    return 0


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
        for phrase in GOVERNANCE_REQUIRED_PHRASES:
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

    if ws.exists():
        for artifact_type, path in recognizable_artifact_json_files(ws):
            failures.extend(validate_artifact_file(artifact_type, path))

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"Aegis workspace check passed: {ws}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize and validate a target project's docs/aegis workspace."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create docs/aegis in a target project")
    init_parser.add_argument("--root", required=True, help="target project root")
    init_parser.set_defaults(func=command_init)

    check_parser = subparsers.add_parser("check", help="validate a target project workspace")
    check_parser.add_argument("--root", required=True, help="target project root")
    check_parser.set_defaults(func=command_check)

    append_parser = subparsers.add_parser("append-index", help="append an INDEX.md entry")
    append_parser.add_argument("--root", required=True, help="target project root")
    append_parser.add_argument("--path", required=True, help="file path inside docs/aegis")
    append_parser.add_argument("--kind", required=True, help="entry kind, such as spec or plan")
    append_parser.add_argument("--title", required=True, help="human-readable title")
    append_parser.add_argument("--date", help="entry date, defaults to today")
    append_parser.set_defaults(func=command_append_index)

    validate_parser = subparsers.add_parser(
        "validate-artifact", help="validate a runtime-ready artifact JSON file"
    )
    validate_parser.add_argument(
        "--type",
        choices=sorted(ARTIFACT_SCHEMAS),
        help="artifact type; inferred from filename when omitted",
    )
    validate_parser.add_argument("--file", required=True, help="artifact JSON file")
    validate_parser.set_defaults(func=command_validate_artifact)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except WorkspaceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
