"""Workspace layout and templates, root resolution, and the ``init`` command."""

from __future__ import annotations

import argparse
from pathlib import Path

from .errors import WorkspaceError
from .textio import write_if_missing


WORKSPACE_REL = Path("docs") / "aegis"
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

## 1. Baseline Roles
- Product / Requirement Baseline: problem, accepted behavior, success evidence,
  non-goals, workflow constraints, and approved requirement/spec intent.
- Architecture / Runtime Boundary Baseline: canonical owner, contract,
  source-of-truth boundary, dependency direction, compatibility, runtime-ready
  boundary, and retirement state.

## 2. Design Defect
A confirmed error, gap, contradiction, or wrong abstraction IN the relevant
requirement, design, or baseline.
- Fix the defective requirement/design/baseline first.
- Then align implementation to the corrected baseline.
- Do NOT patch implementation around a defective baseline.

## 3. Implementation Drift
Implementation, plan, review, or documentation has deviated from a confirmed,
correct, unchanged requirement or architecture baseline.
- Return to baseline via the simplest stable path.
- Do NOT "update baseline to match drift" without explicit review.

## 4. Compatibility Aliases
- Architecture Defect = architecture-scoped Design Defect.
- Architecture Drift = architecture-scoped Implementation Drift.
- New findings should report Design Defect / Implementation Drift plus
  `scope: requirements | architecture | both`.

## 5. Baseline Check Protocol
Before non-trivial changes:
1. Read the latest Product / Requirement Baseline candidate.
2. Read the latest Architecture / Runtime Boundary Baseline candidate.
3. Compare current work against requirement acceptance and architecture owner /
   contract boundaries.
4. Check for new anti-patterns not recorded in known list.
5. Report: aligned / Design Defect / Implementation Drift /
   missing-authority / needs-clarification, with
   `scope: requirements | architecture | both`.

## 6. Architecture Review - 7 Dimensions
After each non-trivial change:
1. **Ownership integrity** - every component has exactly one canonical owner
2. **Module boundaries** - no unauthorized cross-module coupling
3. **Contract changes** - all API/signature/behavior contract changes documented
4. **Cascade proliferation** - no new cascading dependency chains
5. **Dependency direction** - dependencies flow toward stability
6. **Retirement completeness** - old owners/fallbacks/paths removed or scheduled
7. **Entropy flow** - net complexity decreased or stayed; no unjustified new entities

## 7. Hard Boundaries
- BASELINE-GOVERNANCE.md is the constitution for THIS project's Aegis workspace
- Baseline snapshots in `baseline/` are evidence, not authority
- ADRs in `adr/` record decisions; they do not replace baseline governance
- This file is NEVER auto-updated - changes require explicit user review
"""

WORKSPACE_DIRS = ("adr", "baseline", "specs", "plans", "work")
CORE_FILES = ("README.md", "INDEX.md", "BASELINE-GOVERNANCE.md")
GOVERNANCE_TEMPLATE_PROFILES = (
    (
        "current-dual-baseline",
        (
            "## 1. Baseline Roles",
            "Product / Requirement Baseline",
            "Architecture / Runtime Boundary Baseline",
            "## 2. Design Defect",
            "## 3. Implementation Drift",
            "## 4. Compatibility Aliases",
            "scope: requirements | architecture | both",
            "## 5. Baseline Check Protocol",
            "## 6. Architecture Review",
            "## 7. Hard Boundaries",
            "evidence, not authority",
            "NEVER auto-updated",
        ),
    ),
    (
        "legacy-architecture-only",
        (
            "## 1. Architecture Defect",
            "## 2. Architecture Drift",
            "## 3. Baseline Check Protocol",
            "## 4. Architecture Review",
            "## 5. Hard Boundaries",
            "evidence, not authority",
            "NEVER auto-updated",
        ),
    ),
)


def resolve_root(root_arg: str) -> Path:
    root = Path(root_arg).expanduser().resolve()
    if not root.exists():
        raise WorkspaceError(f"root does not exist: {root}")
    if not root.is_dir():
        raise WorkspaceError(f"root is not a directory: {root}")
    return root


def workspace(root: Path) -> Path:
    return root / WORKSPACE_REL


def initialize_workspace(root: Path) -> list[str]:
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
    return created


def command_init(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    created = initialize_workspace(root)

    if created:
        print(f"Initialized {WORKSPACE_REL.as_posix()} in {root}")
        print("Created: " + ", ".join(created))
    else:
        print(f"{WORKSPACE_REL.as_posix()} already initialized in {root}")
    return 0


def work_dir(root: Path, work: str) -> Path:
    work_name = Path(work).name
    if work != work_name or work_name in ("", ".", ".."):
        raise WorkspaceError(f"work slug must be a single directory name: {work}")
    ws = workspace(root).resolve()
    candidate = ws / "work" / work
    candidate = candidate.resolve()
    try:
        candidate.relative_to(ws / "work")
    except ValueError as exc:
        raise WorkspaceError(f"work slug must stay inside docs/aegis/work: {work}") from exc
    return candidate


def work_rel(work_path: Path) -> str:
    return (WORKSPACE_REL / "work" / work_path.name).as_posix()


def ensure_work_exists(root: Path, work: str) -> Path:
    path = work_dir(root, work)
    if not path.is_dir():
        raise WorkspaceError(f"work directory does not exist: {path}")
    return path
