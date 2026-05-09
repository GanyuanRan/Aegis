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
    write_text_lf(path, content)
    return True


def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


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
    with index_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(entry)
    return True


def command_append_index(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    rel_path, file_path = normalize_workspace_path(root, args.path)
    if not append_index_entry(root, str(file_path), args.kind, args.title, args.date):
        print(f"Index already contains {rel_path}")
        return 0

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


def write_json(path: Path, data: dict) -> None:
    write_text_lf(
        path,
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
    )


def read_json_dict(path: Path) -> dict:
    data = load_json_file(path)
    if not isinstance(data, dict):
        raise WorkspaceError(f"{path}: expected JSON object")
    return data


def list_arg(values: list[str] | None) -> list[str]:
    return list(values or [])


def optional_none(value: str | None) -> str | None:
    if value in (None, "", "none", "None"):
        return None
    return value


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


def append_work_file(root: Path, path: Path, kind: str, title: str, entry_date: str | None = None) -> None:
    append_index_entry(root, str(path), kind, title, entry_date)


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- none\n"
    return "".join(f"- {item}\n" for item in items)


def command_new_work(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    initialize_workspace(root)

    work_name = f"{args.date}-{args.slug}"
    target = work_dir(root, work_name)
    if target.exists():
        raise WorkspaceError(f"work lifecycle already exists: {target}")
    target.mkdir(parents=True, exist_ok=True)

    task_id = args.task_id or work_name
    risk_hints = list_arg(args.risk_hint)
    change_kinds = list_arg(args.change_kind)
    candidate_docs = list_arg(args.baseline_ref)
    affected_layers = list_arg(args.affected_layer)
    owners = list_arg(args.owner)
    invariants = list_arg(args.invariant)
    compat_boundary = args.compat_boundary or "Compatibility boundary not yet refined."
    non_goals = list_arg(args.non_goal)

    task_intent = {
        "schemaVersion": SCHEMA_VERSION,
        "requestedOutcome": args.requested_outcome,
        "scope": args.scope,
        "changeKinds": change_kinds,
        "riskHints": risk_hints,
    }
    baseline_hint = {
        "schemaVersion": SCHEMA_VERSION,
        "candidateDocs": candidate_docs,
        "whyRelevant": args.why_relevant or "Baseline read-set requires agent review.",
        "missingAuthority": list_arg(args.missing_authority),
    }
    impact = {
        "schemaVersion": SCHEMA_VERSION,
        "affectedLayers": affected_layers,
        "owners": owners,
        "invariants": invariants,
        "compatBoundary": compat_boundary,
        "nonGoals": non_goals,
    }
    checkpoint = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": task_id,
        "currentTodo": args.current_todo or "Define first execution slice.",
        "completedTodos": [],
        "activeSlice": args.active_slice or "initial",
        "evidenceRefs": [],
        "blockedOn": optional_none(args.blocked_on),
        "nextStep": args.next_step or "Read baseline refs and start the next safe slice.",
        "updatedAt": args.date,
    }
    drift = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": task_id,
        "taskIntentRef": f"{work_rel(target)}/task-intent-draft.json",
        "baselineRefs": candidate_docs,
        "scopeStatus": "not-yet-verified",
        "compatStatus": "not-yet-verified",
        "retirementStatus": "not-yet-verified",
        "newRiskSignals": risk_hints,
        "decision": "needs-baseline-readback" if candidate_docs else "needs-verification",
    }

    write_json(target / "task-intent-draft.json", task_intent)
    write_json(target / "baseline-read-set-hint.json", baseline_hint)
    write_json(target / "impact-statement-draft.json", impact)
    write_json(target / "todo-checkpoint-draft.json", checkpoint)
    write_json(target / "drift-check-draft.json", drift)

    write_text_lf(
        target / "10-intent.md",
        f"# {args.title} - Intent\n\n"
        "## TaskIntentDraft\n\n"
        f"- Requested outcome: {args.requested_outcome}\n"
        f"- Scope: {args.scope}\n"
        f"- Change kinds:\n{markdown_list(change_kinds)}"
        f"- Risk hints:\n{markdown_list(risk_hints)}"
        "\n## BaselineReadSetHint\n\n"
        f"{markdown_list(candidate_docs)}"
        "\n## ImpactStatementDraft\n\n"
        f"- Compatibility boundary: {compat_boundary}\n"
        f"- Affected layers:\n{markdown_list(affected_layers)}"
        f"- Owners:\n{markdown_list(owners)}"
        f"- Invariants:\n{markdown_list(invariants)}"
        f"- Non-goals:\n{markdown_list(non_goals)}"
        "\nThese records are Method Pack drafts / hints, not authoritative runtime decisions.\n",
    )
    write_text_lf(
        target / "20-checkpoint.md",
        f"# {args.title} - Checkpoint\n\n"
        f"- Task ID: {task_id}\n"
        f"- Current todo: {checkpoint['currentTodo']}\n"
        f"- Active slice: {checkpoint['activeSlice']}\n"
        f"- Blocked on: {checkpoint['blockedOn'] or 'none'}\n"
        f"- Next step: {checkpoint['nextStep']}\n",
    )
    write_text_lf(
        target / "90-evidence.md",
        f"# {args.title} - Evidence\n\n"
        "No evidence has been recorded yet.\n",
    )
    write_text_lf(
        target / "99-reflection.md",
        f"# {args.title} - Reflection\n\n"
        "Completion reflection has not been recorded yet.\n\n"
        "Method Pack output does not grant completion authority.\n",
    )

    for filename, kind, title in (
        ("10-intent.md", "work", f"{args.title} intent"),
        ("20-checkpoint.md", "work", f"{args.title} checkpoint"),
        ("90-evidence.md", "work", f"{args.title} evidence"),
        ("99-reflection.md", "work", f"{args.title} reflection"),
        ("task-intent-draft.json", "artifact", f"{args.title} task intent draft"),
        ("baseline-read-set-hint.json", "artifact", f"{args.title} baseline read-set hint"),
        ("impact-statement-draft.json", "artifact", f"{args.title} impact statement draft"),
        ("todo-checkpoint-draft.json", "artifact", f"{args.title} todo checkpoint draft"),
        ("drift-check-draft.json", "artifact", f"{args.title} drift check draft"),
    ):
        append_work_file(root, target / filename, kind, title, args.date)

    print(f"Created work lifecycle: {target}")
    return 0


def command_add_checkpoint(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    checkpoint_path = target / "todo-checkpoint-draft.json"
    checkpoint = read_json_dict(checkpoint_path)
    task_id = str(checkpoint.get("taskId", args.work))
    evidence_refs = list_arg(args.evidence_ref)
    completed = list_arg(args.completed_todo)

    checkpoint.update(
        {
            "schemaVersion": SCHEMA_VERSION,
            "taskId": task_id,
            "currentTodo": args.current_todo,
            "completedTodos": completed,
            "activeSlice": args.active_slice,
            "evidenceRefs": evidence_refs,
            "blockedOn": optional_none(args.blocked_on),
            "nextStep": args.next_step,
            "updatedAt": args.date or date.today().isoformat(),
        }
    )
    write_json(checkpoint_path, checkpoint)

    resume = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": task_id,
        "lastCheckpointRef": f"{work_rel(target)}/todo-checkpoint-draft.json",
        "resumeInstruction": args.resume_instruction,
        "knownPartialWork": completed,
        "mustReadBeforeContinuing": [
            f"{work_rel(target)}/10-intent.md",
            f"{work_rel(target)}/20-checkpoint.md",
            f"{work_rel(target)}/todo-checkpoint-draft.json",
        ],
        "unsafeToAssume": list_arg(args.unsafe_to_assume),
    }
    write_json(target / "resume-state-hint.json", resume)

    with (target / "20-checkpoint.md").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n## Checkpoint Update\n\n"
            f"- Current todo: {args.current_todo}\n"
            f"- Active slice: {args.active_slice}\n"
            f"- Completed todos:\n{markdown_list(completed)}"
            f"- Evidence refs:\n{markdown_list(evidence_refs)}"
            f"- Blocked on: {optional_none(args.blocked_on) or 'none'}\n"
            f"- Next step: {args.next_step}\n"
        )

    append_work_file(root, target / "resume-state-hint.json", "artifact", f"{args.work} resume state hint")
    print(f"Updated checkpoint: {checkpoint_path}")
    return 0


def command_add_evidence(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    safe_key = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in args.artifact_key).strip("-")
    if not safe_key:
        raise WorkspaceError("artifact-key must contain at least one safe character")
    path = target / f"evidence-bundle-draft-{safe_key}.json"
    evidence = {
        "schemaVersion": SCHEMA_VERSION,
        "artifactKey": args.artifact_key,
        "type": args.type,
        "source": args.source,
        "summary": args.summary,
        "verifier": args.verifier,
    }
    write_json(path, evidence)
    with (target / "90-evidence.md").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n## EvidenceBundleDraft\n\n"
            f"- Artifact key: {args.artifact_key}\n"
            f"- Type: {args.type}\n"
            f"- Source: {args.source}\n"
            f"- Summary: {args.summary}\n"
            f"- Verifier: {args.verifier}\n"
        )
    append_work_file(root, path, "artifact", f"{args.work} evidence {args.artifact_key}")
    print(f"Added evidence bundle: {path}")
    return 0


def command_add_drift_check(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    checkpoint = read_json_dict(target / "todo-checkpoint-draft.json")
    drift = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": str(checkpoint.get("taskId", args.work)),
        "taskIntentRef": f"{work_rel(target)}/task-intent-draft.json",
        "baselineRefs": list_arg(args.baseline_ref),
        "scopeStatus": args.scope_status,
        "compatStatus": args.compat_status,
        "retirementStatus": args.retirement_status,
        "newRiskSignals": list_arg(args.new_risk_signal),
        "decision": args.decision,
    }
    failures = validate_artifact_data("DriftCheckDraft", drift, target / "drift-check-draft.json")
    if failures:
        raise WorkspaceError("; ".join(failures))
    write_json(target / "drift-check-draft.json", drift)
    with (target / "20-checkpoint.md").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n## DriftCheckDraft\n\n"
            f"- Scope status: {args.scope_status}\n"
            f"- Compatibility status: {args.compat_status}\n"
            f"- Retirement status: {args.retirement_status}\n"
            f"- New risk signals:\n{markdown_list(list_arg(args.new_risk_signal))}"
            f"- Advisory decision: {args.decision}\n"
        )
    print(f"Updated drift check: {target / 'drift-check-draft.json'}")
    return 0


def command_bundle(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    task_intent = read_json_dict(target / "task-intent-draft.json")
    impact = read_json_dict(target / "impact-statement-draft.json")
    drift = read_json_dict(target / "drift-check-draft.json")
    evidence_paths = sorted(target.glob("evidence-bundle-draft*.json"))
    evidence_refs = [f"{work_rel(target)}/{path.name}" for path in evidence_paths]
    gate_input = {
        "schemaVersion": SCHEMA_VERSION,
        "baselineRefs": drift.get("baselineRefs", []),
        "impactStatement": f"{work_rel(target)}/impact-statement-draft.json",
        "compatPlan": impact.get("compatBoundary", ""),
        "retirementPlan": drift.get("retirementStatus", ""),
        "evidenceBundle": evidence_refs,
    }
    write_json(target / "gate-input-pack.json", gate_input)
    append_work_file(root, target / "gate-input-pack.json", "artifact", f"{args.work} gate input pack")

    proof = (
        f"# Proof Bundle - {args.work}\n\n"
        "## Method Pack Boundary\n\n"
        "This proof bundle is an advisory Aegis Method Pack record. It does not "
        "determine evidence sufficiency, produce authoritative `GateDecision`, "
        "or grant `completion authority`.\n\n"
        "## Task Intent\n\n"
        f"- Requested outcome: {task_intent.get('requestedOutcome', '')}\n"
        f"- Scope: {task_intent.get('scope', '')}\n"
        "\n## Impact\n\n"
        f"- Compatibility boundary: {impact.get('compatBoundary', '')}\n"
        f"- Non-goals:\n{markdown_list(list(impact.get('nonGoals', [])))}"
        "\n## Evidence Bundle Refs\n\n"
        f"{markdown_list(evidence_refs)}"
        "\n## Drift Check\n\n"
        f"- Scope status: {drift.get('scopeStatus', '')}\n"
        f"- Compatibility status: {drift.get('compatStatus', '')}\n"
        f"- Retirement status: {drift.get('retirementStatus', '')}\n"
        f"- Advisory decision: {drift.get('decision', '')}\n"
    )
    write_text_lf(target / "proof-bundle.md", proof)
    append_work_file(root, target / "proof-bundle.md", "work", f"{args.work} proof bundle")
    print(f"Assembled proof bundle: {target / 'proof-bundle.md'}")
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

    new_work_parser = subparsers.add_parser(
        "new-work", help="create helper-backed work lifecycle records"
    )
    new_work_parser.add_argument("--root", required=True, help="target project root")
    new_work_parser.add_argument("--date", default=date.today().isoformat(), help="work date")
    new_work_parser.add_argument("--slug", required=True, help="work slug without date prefix")
    new_work_parser.add_argument("--title", required=True, help="human-readable work title")
    new_work_parser.add_argument("--task-id", help="stable task id; defaults to date-slug")
    new_work_parser.add_argument("--requested-outcome", required=True, help="requested outcome")
    new_work_parser.add_argument("--scope", required=True, help="task scope")
    new_work_parser.add_argument("--change-kind", action="append", default=[], help="change kind")
    new_work_parser.add_argument("--risk-hint", action="append", default=[], help="risk hint")
    new_work_parser.add_argument("--baseline-ref", action="append", default=[], help="baseline ref")
    new_work_parser.add_argument("--why-relevant", help="why baseline refs are relevant")
    new_work_parser.add_argument("--missing-authority", action="append", default=[], help="authority gap")
    new_work_parser.add_argument("--affected-layer", action="append", default=[], help="affected layer")
    new_work_parser.add_argument("--owner", action="append", default=[], help="owner")
    new_work_parser.add_argument("--invariant", action="append", default=[], help="invariant")
    new_work_parser.add_argument("--compat-boundary", help="compatibility boundary")
    new_work_parser.add_argument("--non-goal", action="append", default=[], help="non-goal")
    new_work_parser.add_argument("--current-todo", help="initial current todo")
    new_work_parser.add_argument("--active-slice", help="initial active slice")
    new_work_parser.add_argument("--blocked-on", help="initial blocker")
    new_work_parser.add_argument("--next-step", help="initial next step")
    new_work_parser.set_defaults(func=command_new_work)

    checkpoint_parser = subparsers.add_parser(
        "add-checkpoint", help="update checkpoint and resume hint for a work record"
    )
    checkpoint_parser.add_argument("--root", required=True, help="target project root")
    checkpoint_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    checkpoint_parser.add_argument("--date", help="checkpoint date")
    checkpoint_parser.add_argument("--current-todo", required=True, help="current todo")
    checkpoint_parser.add_argument("--completed-todo", action="append", default=[], help="completed todo")
    checkpoint_parser.add_argument("--active-slice", required=True, help="active slice")
    checkpoint_parser.add_argument("--evidence-ref", action="append", default=[], help="evidence ref")
    checkpoint_parser.add_argument("--blocked-on", help="blocker")
    checkpoint_parser.add_argument("--next-step", required=True, help="next step")
    checkpoint_parser.add_argument(
        "--resume-instruction", required=True, help="resume instruction"
    )
    checkpoint_parser.add_argument(
        "--unsafe-to-assume", action="append", default=[], help="unsafe assumption"
    )
    checkpoint_parser.set_defaults(func=command_add_checkpoint)

    evidence_parser = subparsers.add_parser(
        "add-evidence", help="add an EvidenceBundleDraft sidecar"
    )
    evidence_parser.add_argument("--root", required=True, help="target project root")
    evidence_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    evidence_parser.add_argument("--artifact-key", required=True, help="evidence key")
    evidence_parser.add_argument("--type", required=True, help="evidence type")
    evidence_parser.add_argument("--source", required=True, help="evidence source")
    evidence_parser.add_argument("--summary", required=True, help="evidence summary")
    evidence_parser.add_argument("--verifier", required=True, help="evidence verifier")
    evidence_parser.set_defaults(func=command_add_evidence)

    drift_parser = subparsers.add_parser(
        "add-drift-check", help="update a DriftCheckDraft sidecar"
    )
    drift_parser.add_argument("--root", required=True, help="target project root")
    drift_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    drift_parser.add_argument("--decision", required=True, choices=sorted(DRIFT_DECISIONS))
    drift_parser.add_argument("--scope-status", required=True, help="scope status")
    drift_parser.add_argument("--compat-status", required=True, help="compatibility status")
    drift_parser.add_argument("--retirement-status", required=True, help="retirement status")
    drift_parser.add_argument("--baseline-ref", action="append", default=[], help="baseline ref")
    drift_parser.add_argument("--new-risk-signal", action="append", default=[], help="new risk signal")
    drift_parser.set_defaults(func=command_add_drift_check)

    bundle_parser = subparsers.add_parser(
        "bundle", help="assemble a structural proof bundle for a work record"
    )
    bundle_parser.add_argument("--root", required=True, help="target project root")
    bundle_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    bundle_parser.set_defaults(func=command_bundle)

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
