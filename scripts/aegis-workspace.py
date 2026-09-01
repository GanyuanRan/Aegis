#!/usr/bin/env python3
"""Manage a target project's docs/aegis workspace.

This helper belongs to the Aegis Method Pack, but it writes only to the project
root explicitly passed by the caller. It validates workspace structure and
index coverage; it does not make authoritative governance decisions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


WORKSPACE_REL = Path("docs") / "aegis"
SCHEMA_VERSION = "aegis.schema.v0"
EVIDENCE_STATUSES = {
    "attempted",
    "evidence-finalized",
    "blocked",
    "abandoned",
    "superseded",
}
TERMINAL_EVIDENCE_STATUSES = {
    "evidence-finalized",
    "blocked",
    "abandoned",
}
ATTEMPT_STATUSES = {
    "attempted",
    "failed",
    "blocked",
}
ATTEMPT_CONVERGENCE_WARNING = 3
MAX_RECENT_ATTEMPTS = 5
MAX_CHECKPOINT_HISTORY = 5
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
ARTIFACT_SCHEMAS = {
    "TaskIntentDraft": (
        "schemaVersion",
        "requestedOutcome",
        "scope",
        "changeKinds",
        "riskHints",
    ),
    "BaselineUsageDraft": (
        "schemaVersion",
        "taskId",
        "requiredBaselineRefs",
        "acknowledgedBeforePlanRefs",
        "citedInPlanRefs",
        "missingRefs",
        "decision",
    ),
    "SubagentContextPacket": (
        "schemaVersion",
        "task",
        "goal",
        "stopCondition",
        "relevantBaselineRefs",
        "relevantFiles",
        "knownFacts",
        "unknowns",
        "nonGoals",
        "expectedOutput",
        "verificationExpected",
        "mustReadExcerpts",
        "unsafeAssumptions",
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
    "baseline-usage-draft": "BaselineUsageDraft",
    "subagent-context-packet": "SubagentContextPacket",
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
BASELINE_USAGE_DECISIONS = DRIFT_DECISIONS
ADR_SOURCE_STATUSES = (
    "recorded-from-work",
    "recorded-from-plan",
    "recorded-from-spec",
)
ADR_MUTATION_STATUSES = ("amended", "superseded")
ADR_BASELINE_SYNC_STATES = ("needed", "not-needed", "unknown")
ADR_BASELINE_SYNC_ACTIONS = {
    "create-snapshot": "create snapshot",
    "update-baseline": "update baseline",
    "cite-unchanged": "cite unchanged",
    "blocked": "blocked",
}
ADR_FILENAME_RE = re.compile(r"^ADR-(\d{4})-([a-z0-9][a-z0-9-]*)\.md$")
ADR_REQUIRED_PHRASES = (
    "# ADR-",
    "Status: `",
    "## Source Evidence",
    "## Context",
    "## Decision",
    "## Alternatives Considered",
    "## Consequences",
    "## Compatibility Boundary",
    "## Retirement Impact",
    "## Baseline Sync",
    "## Evidence References",
    "advisory Aegis Method Pack record",
    "does not grant completion authority",
)


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
    if artifact_type == "BaselineUsageDraft":
        decision = data.get("decision")
        if decision not in BASELINE_USAGE_DECISIONS:
            failures.append(
                f"{source}: BaselineUsageDraft decision must be advisory, got {decision}"
            )
    if artifact_type == "EvidenceBundleDraft":
        evidence_status = data.get("evidenceStatus")
        if evidence_status is not None and evidence_status not in EVIDENCE_STATUSES:
            failures.append(
                f"{source}: EvidenceBundleDraft evidenceStatus must be advisory, got {evidence_status}"
            )
        slice_id = data.get("sliceId")
        if slice_id is not None and (not isinstance(slice_id, str) or not slice_id.strip()):
            failures.append(f"{source}: EvidenceBundleDraft sliceId must be a non-empty string")
        attempts = data.get("attempts")
        if attempts is not None:
            if not isinstance(attempts, list):
                failures.append(f"{source}: EvidenceBundleDraft attempts must be a list")
            else:
                for index, attempt in enumerate(attempts):
                    if not isinstance(attempt, dict):
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} must be an object"
                        )
                        continue
                    attempt_id = attempt.get("attemptId")
                    if not isinstance(attempt_id, str) or not attempt_id.strip():
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} missing attemptId"
                        )
                    attempt_status = attempt.get("attemptStatus")
                    if attempt_status not in ATTEMPT_STATUSES:
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} attemptStatus must be advisory, got {attempt_status}"
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


def adr_directory(root: Path) -> Path:
    return workspace(root) / "adr"


def normalize_slug(value: str, label: str) -> str:
    slug = Path(value).name.lower()
    if value != Path(value).name or slug in ("", ".", ".."):
        raise WorkspaceError(f"{label} must be a single slug: {value}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise WorkspaceError(f"{label} must match [a-z0-9][a-z0-9-]*: {value}")
    return slug


def adr_id_from_path(path: Path) -> str:
    match = ADR_FILENAME_RE.match(path.name)
    if not match:
        raise WorkspaceError(f"ADR filename must match ADR-####-slug.md: {path}")
    return f"ADR-{match.group(1)}"


def adr_title_from_path(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def existing_adr_records(root: Path) -> list[tuple[int, str, Path]]:
    records = []
    for path in sorted(adr_directory(root).glob("ADR-*.md")):
        match = ADR_FILENAME_RE.match(path.name)
        if match:
            records.append((int(match.group(1)), match.group(2), path))
    return records


def next_adr_path(root: Path, slug: str) -> Path:
    records = existing_adr_records(root)
    for _, existing_slug, path in records:
        if existing_slug == slug:
            raise WorkspaceError(f"ADR slug already exists: {path}")
    next_number = max((number for number, _, _ in records), default=0) + 1
    return adr_directory(root) / f"ADR-{next_number:04d}-{slug}.md"


def normalize_adr_path(root: Path, input_path: str) -> tuple[str, Path]:
    rel_path, file_path = normalize_workspace_path(root, input_path)
    adr_prefix = (WORKSPACE_REL / "adr").as_posix() + "/"
    if not rel_path.startswith(adr_prefix):
        raise WorkspaceError(
            f"path must be inside {(WORKSPACE_REL / 'adr').as_posix()}: {file_path}"
        )
    if file_path.suffix.lower() != ".md":
        raise WorkspaceError(f"ADR path must be a markdown file: {file_path}")
    if not file_path.is_file():
        raise WorkspaceError(f"ADR file does not exist: {file_path}")
    return rel_path, file_path


def render_baseline_sync(
    needed: str,
    target: str,
    action: str,
    reason: str,
    heading_level: str = "##",
) -> str:
    return (
        f"{heading_level} Baseline Sync\n\n"
        f"- Needed: {needed}\n"
        f"- Target: {target}\n"
        f"- Action: {ADR_BASELINE_SYNC_ACTIONS[action]}\n"
        f"- Reason: {reason}\n"
    )


def render_adr_markdown(
    adr_id: str,
    title: str,
    entry_date: str,
    status: str,
    source_evidence: list[str],
    context: str,
    decision: str,
    alternatives: list[str],
    consequences: list[str],
    compat_boundary: str,
    retirement_impact: str,
    baseline_sync_needed: str,
    baseline_target: str,
    baseline_action: str,
    baseline_reason: str,
    evidence_refs: list[str],
    extra_sections: list[str] | None = None,
) -> str:
    extras = ""
    if extra_sections:
        extras = "".join(
            section if section.endswith("\n") else section + "\n" for section in extra_sections
        )

    return (
        f"# {adr_id} - {title}\n\n"
        f"Status: `{status}`\n"
        f"Date: `{entry_date}`\n\n"
        "## Source Evidence\n\n"
        f"{markdown_list(source_evidence)}"
        "## Context\n\n"
        f"{context}\n\n"
        "## Decision\n\n"
        f"{decision}\n\n"
        "## Alternatives Considered\n\n"
        f"{markdown_list(alternatives)}"
        "## Consequences\n\n"
        f"{markdown_list(consequences)}"
        "## Compatibility Boundary\n\n"
        f"{compat_boundary}\n\n"
        "## Retirement Impact\n\n"
        f"{retirement_impact}\n\n"
        f"{render_baseline_sync(baseline_sync_needed, baseline_target, baseline_action, baseline_reason)}\n"
        "## Evidence References\n\n"
        f"{markdown_list(evidence_refs)}"
        f"{extras}"
        "## Boundary\n\n"
        "This ADR is an advisory Aegis Method Pack record. It does not grant "
        "completion authority or replace project-authoritative architecture "
        "sources.\n"
    )


def ensure_adr_indexed(root: Path, path: Path, entry_date: str | None = None) -> None:
    append_index_entry(root, str(path), "adr", adr_title_from_path(path), entry_date)


def validate_adr_file(path: Path) -> list[str]:
    failures = []
    match = ADR_FILENAME_RE.match(path.name)
    if not match:
        failures.append(f"{path}: ADR filename must match ADR-####-slug.md")

    text = path.read_text(encoding="utf-8")
    for phrase in ADR_REQUIRED_PHRASES:
        if phrase not in text:
            failures.append(f"{path}: ADR missing phrase: {phrase}")

    if "- Status: superseded" in text and "## Superseded By" not in text:
        failures.append(f"{path}: superseded ADR marker requires a Superseded By section")

    return failures


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


def safe_key(value: str) -> str:
    key = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value).strip("-")
    if not key:
        raise WorkspaceError("value must contain at least one safe character")
    return key


def upsert_markdown_section(path: Path, heading: str, body: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = f"{heading}\n\n"
    pattern = re.compile(
        r"(?m)^" + re.escape(heading) + r"\n\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    replacement = marker + body.rstrip("\n") + "\n"
    if pattern.search(text):
        text = pattern.sub(replacement, text, count=1)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "\n" + replacement
    write_text_lf(path, text)


def evidence_bundle_path(target: Path, slice_id: str) -> Path:
    return target / f"evidence-bundle-draft-{safe_key(slice_id)}.json"


def load_or_create_evidence_bundle(
    target: Path,
    slice_id: str,
    artifact_key: str,
    evidence_type: str,
    source: str,
    summary: str,
    verifier: str,
) -> tuple[Path, dict]:
    path = evidence_bundle_path(target, slice_id)
    if path.exists():
        data = read_json_dict(path)
        if not isinstance(data, dict):
            raise WorkspaceError(f"evidence bundle must be a JSON object: {path}")
    else:
        data = {
            "schemaVersion": SCHEMA_VERSION,
            "artifactKey": artifact_key,
            "type": evidence_type,
            "source": source,
            "summary": summary,
            "verifier": verifier,
        }
    data.setdefault("sliceId", slice_id)
    data.setdefault("evidenceStatus", "attempted")
    return path, data


def merge_attempt(data: dict, attempt: dict) -> None:
    attempts = data.get("attempts", [])
    if not isinstance(attempts, list):
        attempts = []
    summary = data.get("attemptSummary", {})
    if not isinstance(summary, dict):
        summary = {}

    previous = next(
        (item for item in attempts if isinstance(item, dict) and item.get("attemptId") == attempt["attemptId"]),
        None,
    )
    previous_status = previous.get("attemptStatus") if previous else None
    attempts = [
        item
        for item in attempts
        if not isinstance(item, dict) or item.get("attemptId") != attempt["attemptId"]
    ]
    attempts.append(attempt)
    data["attempts"] = attempts[-MAX_RECENT_ATTEMPTS:]

    total = int(summary.get("total", 0) or 0)
    if previous is None:
        total += 1
    for status in ATTEMPT_STATUSES:
        count = int(summary.get(status, 0) or 0)
        if previous_status == status:
            count -= 1
        if attempt["attemptStatus"] == status:
            count += 1
        summary[status] = max(count, 0)
    summary["total"] = total
    summary["lastAttemptId"] = attempt["attemptId"]
    data["attemptSummary"] = summary


def bounded_checkpoint_markdown(path: Path, current_block: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    title = "# Checkpoint"
    for line in existing.splitlines():
        if line.startswith("# "):
            title = line.strip()
            break

    history: list[str] = []
    current_match = re.search(r"(?ms)^## Current Checkpoint\n\n(.*?)(?=\n## |\Z)", existing)
    if current_match and current_match.group(1).strip():
        history.append(current_match.group(1).strip())
    for block in re.findall(r"(?ms)^## Checkpoint Update\n\n(.*?)(?=\n## Checkpoint Update|\Z)", existing):
        cleaned = block.strip()
        if cleaned:
            history.append(cleaned)
    recent = history[-MAX_CHECKPOINT_HISTORY:]

    drift_match = re.search(r"(?ms)^## DriftCheckDraft\n\n(.*?)(?=\n## |\Z)", existing)

    content = f"{title}\n\n## Current Checkpoint\n\n{current_block.rstrip()}\n"
    if recent:
        content += "\n## Recent Checkpoint History\n\n"
        for entry in recent:
            content += "## Checkpoint Update\n\n" + entry + "\n"
    if drift_match and drift_match.group(1).strip():
        content += "\n## DriftCheckDraft\n\n" + drift_match.group(1).strip() + "\n"
    write_text_lf(path, content)


def evidence_bundle_status(path: Path) -> str:
    data = load_json_file(path)
    if not isinstance(data, dict):
        return "invalid"
    status = data.get("evidenceStatus", "legacy-unclassified")
    return status if status in EVIDENCE_STATUSES else "invalid"


def command_new_adr(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    initialize_workspace(root)

    slug = normalize_slug(args.slug, "ADR slug")
    target = next_adr_path(root, slug)
    adr_id = adr_id_from_path(target)
    source_evidence = require_list(args.source_evidence, "--source-evidence")
    alternatives = require_list(args.alternative, "--alternative")
    consequences = require_list(args.consequence, "--consequence")
    evidence_refs = require_list(args.evidence_ref, "--evidence-ref")
    title = require_text(args.title, "ADR title")
    content = render_adr_markdown(
        adr_id=adr_id,
        title=title,
        entry_date=args.date,
        status=args.status,
        source_evidence=source_evidence,
        context=require_text(args.context, "ADR context"),
        decision=require_text(args.decision, "ADR decision"),
        alternatives=alternatives,
        consequences=consequences,
        compat_boundary=require_text(args.compat_boundary, "compatibility boundary"),
        retirement_impact=require_text(args.retirement_impact, "retirement impact"),
        baseline_sync_needed=args.baseline_sync,
        baseline_target=require_text(args.baseline_target, "baseline sync target"),
        baseline_action=args.baseline_action,
        baseline_reason=require_text(args.baseline_reason, "baseline sync reason"),
        evidence_refs=evidence_refs,
    )
    write_text_lf(target, content)
    ensure_adr_indexed(root, target, args.date)
    print(f"Created ADR: {(WORKSPACE_REL / 'adr' / target.name).as_posix()}")
    return 0


def command_amend_adr(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    initialize_workspace(root)

    rel_path, target = normalize_adr_path(root, args.path)
    source_evidence = require_list(args.source_evidence, "--source-evidence")
    evidence_refs = require_list(args.evidence_ref, "--evidence-ref")
    summary = require_text(args.summary, "amendment summary")

    with target.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n"
            f"## Amendment - {args.date} - {summary}\n\n"
            "- Status: amended\n\n"
            "### Source Evidence\n\n"
            f"{markdown_list(source_evidence)}"
            "### Change Summary\n\n"
            f"{summary}\n\n"
            "### Compatibility Boundary\n\n"
            f"{require_text(args.compat_boundary, 'compatibility boundary')}\n\n"
            "### Retirement Impact\n\n"
            f"{require_text(args.retirement_impact, 'retirement impact')}\n\n"
            f"{render_baseline_sync(args.baseline_sync, require_text(args.baseline_target, 'baseline sync target'), args.baseline_action, require_text(args.baseline_reason, 'baseline sync reason'), heading_level='###')}\n"
            "### Evidence References\n\n"
            f"{markdown_list(evidence_refs)}"
            "### Boundary\n\n"
            "This amendment is an advisory Aegis Method Pack record. It does not grant "
            "completion authority or replace project-authoritative architecture "
            "sources.\n"
        )

    ensure_adr_indexed(root, target, args.date)
    print(f"Amended ADR: {rel_path}")
    return 0


def command_supersede_adr(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    initialize_workspace(root)

    prior_rel, prior_path = normalize_adr_path(root, args.path)
    prior_text = prior_path.read_text(encoding="utf-8")
    if "## Superseded By" in prior_text:
        raise WorkspaceError(f"ADR is already marked as superseded: {prior_path}")

    slug = normalize_slug(args.slug, "ADR slug")
    target = next_adr_path(root, slug)
    adr_id = adr_id_from_path(target)
    target_rel = (WORKSPACE_REL / "adr" / target.name).as_posix()
    source_evidence = require_list(args.source_evidence, "--source-evidence")
    alternatives = require_list(args.alternative, "--alternative")
    consequences = require_list(args.consequence, "--consequence")
    evidence_refs = require_list(args.evidence_ref, "--evidence-ref")
    supersession_reason = require_text(args.supersession_reason, "supersession reason")
    content = render_adr_markdown(
        adr_id=adr_id,
        title=require_text(args.title, "ADR title"),
        entry_date=args.date,
        status=args.status,
        source_evidence=source_evidence,
        context=require_text(args.context, "ADR context"),
        decision=require_text(args.decision, "ADR decision"),
        alternatives=alternatives,
        consequences=consequences,
        compat_boundary=require_text(args.compat_boundary, "compatibility boundary"),
        retirement_impact=require_text(args.retirement_impact, "retirement impact"),
        baseline_sync_needed=args.baseline_sync,
        baseline_target=require_text(args.baseline_target, "baseline sync target"),
        baseline_action=args.baseline_action,
        baseline_reason=require_text(args.baseline_reason, "baseline sync reason"),
        evidence_refs=evidence_refs,
        extra_sections=[
            "## Supersedes\n\n"
            f"- ADR: {prior_rel}\n"
            f"- Reason: {supersession_reason}\n"
        ],
    )
    write_text_lf(target, content)

    with prior_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "\n"
            "## Superseded By\n\n"
            "- Status: superseded\n"
            f"- Date: {args.date}\n"
            f"- ADR: {target_rel}\n"
            f"- Reason: {supersession_reason}\n"
        )

    ensure_adr_indexed(root, target, args.date)
    ensure_adr_indexed(root, prior_path, args.date)
    print(f"Created superseding ADR: {target_rel}")
    return 0


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
        "goal": arg_value(args, "goal") or args.requested_outcome,
        "successEvidence": list_arg(arg_value(args, "success_evidence", [])),
        "stopCondition": arg_value(args, "stop_condition") or "Stop when success evidence is satisfied or a blocker/risk requires pause.",
        "nonGoals": non_goals,
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
    baseline_usage = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": task_id,
        "requiredBaselineRefs": candidate_docs,
        "deliveredContextRefs": [],
        "acknowledgedBeforePlanRefs": [],
        "citedInPlanRefs": [],
        "missingRefs": candidate_docs,
        "decision": "needs-baseline-readback" if candidate_docs else "continue",
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
    write_json(target / "baseline-usage-draft.json", baseline_usage)
    write_json(target / "impact-statement-draft.json", impact)
    write_json(target / "todo-checkpoint-draft.json", checkpoint)
    write_json(target / "drift-check-draft.json", drift)

    write_text_lf(
        target / "10-intent.md",
        f"# {args.title} - Intent\n\n"
        "## TaskIntentDraft\n\n"
        f"- Requested outcome: {args.requested_outcome}\n"
        f"- Goal: {task_intent['goal']}\n"
        f"- Success evidence:\n{markdown_list(task_intent['successEvidence'])}"
        f"- Stop condition: {task_intent['stopCondition']}\n"
        f"- Non-goals:\n{markdown_list(non_goals)}"
        f"- Scope: {args.scope}\n"
        f"- Change kinds:\n{markdown_list(change_kinds)}"
        f"- Risk hints:\n{markdown_list(risk_hints)}"
        "\n## BaselineReadSetHint\n\n"
        f"{markdown_list(candidate_docs)}"
        "\n## BaselineUsageDraft\n\n"
        f"- Required baseline refs:\n{markdown_list(candidate_docs)}"
        f"- Acknowledged before plan:\n{markdown_list(baseline_usage['acknowledgedBeforePlanRefs'])}"
        f"- Cited in plan:\n{markdown_list(baseline_usage['citedInPlanRefs'])}"
        f"- Missing refs:\n{markdown_list(baseline_usage['missingRefs'])}"
        f"- Advisory decision: {baseline_usage['decision']}\n"
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
        ("baseline-usage-draft.json", "artifact", f"{args.title} baseline usage draft"),
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

    current_block = (
        f"- Current todo: {args.current_todo}\n"
        f"- Active slice: {args.active_slice}\n"
        f"- Completed todos:\n{markdown_list(completed)}"
        f"- Evidence refs:\n{markdown_list(evidence_refs)}"
        f"- Blocked on: {optional_none(args.blocked_on) or 'none'}\n"
        f"- Next step: {args.next_step}\n"
    )
    bounded_checkpoint_markdown(target / "20-checkpoint.md", current_block)

    append_work_file(root, target / "resume-state-hint.json", "artifact", f"{args.work} resume state hint")
    print(f"Updated checkpoint: {checkpoint_path}")
    return 0


def command_add_baseline_usage(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    checkpoint = read_json_dict(target / "todo-checkpoint-draft.json")
    baseline_usage = {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": str(checkpoint.get("taskId", args.work)),
        "requiredBaselineRefs": list_arg(args.required_baseline_ref),
        "deliveredContextRefs": list_arg(args.delivered_context_ref),
        "acknowledgedBeforePlanRefs": list_arg(args.acknowledged_baseline_ref),
        "citedInPlanRefs": list_arg(args.cited_baseline_ref),
        "missingRefs": list_arg(args.missing_ref),
        "decision": args.decision,
    }
    failures = validate_artifact_data(
        "BaselineUsageDraft", baseline_usage, target / "baseline-usage-draft.json"
    )
    if failures:
        raise WorkspaceError("; ".join(failures))
    write_json(target / "baseline-usage-draft.json", baseline_usage)
    body = (
        f"- Required baseline refs:\n{markdown_list(list_arg(args.required_baseline_ref))}"
        f"- Delivered context refs:\n{markdown_list(list_arg(args.delivered_context_ref))}"
        f"- Acknowledged before plan:\n{markdown_list(list_arg(args.acknowledged_baseline_ref))}"
        f"- Cited in plan:\n{markdown_list(list_arg(args.cited_baseline_ref))}"
        f"- Missing refs:\n{markdown_list(list_arg(args.missing_ref))}"
        f"- Advisory decision: {args.decision}\n"
    )
    upsert_markdown_section(target / "10-intent.md", "## BaselineUsageDraft", body)
    append_work_file(root, target / "baseline-usage-draft.json", "artifact", f"{args.work} baseline usage draft")
    print(f"Updated baseline usage: {target / 'baseline-usage-draft.json'}")
    return 0


def command_add_evidence(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    artifact_key = require_text(args.artifact_key, "artifact key")
    slice_id = args.slice_id
    if slice_id is None:
        slice_id = artifact_key
        print(
            "legacy add-evidence invocation: prefer --slice-id to keep retry evidence slice-scoped",
            file=sys.stderr,
        )
    evidence_status = args.evidence_status or "evidence-finalized"
    path, evidence = load_or_create_evidence_bundle(
        target,
        slice_id,
        artifact_key,
        args.type,
        args.source,
        args.summary,
        args.verifier,
    )
    evidence.update(
        {
            "schemaVersion": SCHEMA_VERSION,
            "artifactKey": artifact_key,
            "type": args.type,
            "source": args.source,
            "summary": args.summary,
            "verifier": args.verifier,
            "sliceId": slice_id,
            "evidenceStatus": evidence_status,
            "updatedAt": getattr(args, "date", None) or date.today().isoformat(),
        }
    )
    failures = validate_artifact_data("EvidenceBundleDraft", evidence, path)
    if failures:
        raise WorkspaceError("; ".join(failures))
    write_json(path, evidence)

    body = (
        f"- Artifact key: {artifact_key}\n"
        f"- Slice ID: {slice_id}\n"
        f"- Type: {args.type}\n"
        f"- Source: {args.source}\n"
        f"- Summary: {args.summary}\n"
        f"- Verifier: {args.verifier}\n"
        f"- Evidence status: {evidence_status}\n"
    )
    evidence_markdown = target / "90-evidence.md"
    if evidence_markdown.exists():
        evidence_text = evidence_markdown.read_text(encoding="utf-8")
        evidence_text = evidence_text.replace("No evidence has been recorded yet.\n", "")
        write_text_lf(evidence_markdown, evidence_text)
    upsert_markdown_section(evidence_markdown, f"## EvidenceBundleDraft: {slice_id}", body)
    append_work_file(root, path, "artifact", f"{args.work} evidence {slice_id}")
    print(f"Added evidence bundle: {path}")
    return 0


def command_add_attempt(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    slice_id = require_text(args.slice_id, "slice id")
    attempt_id = require_text(args.attempt_id, "attempt id")
    summary_text = require_text(args.summary, "attempt summary")
    path, evidence = load_or_create_evidence_bundle(
        target,
        slice_id,
        slice_id,
        args.type or "attempt",
        args.source or "attempt telemetry",
        summary_text,
        args.verifier or "not-yet-verified",
    )
    if evidence.get("evidenceStatus") in TERMINAL_EVIDENCE_STATUSES or evidence.get("evidenceStatus") == "superseded":
        raise WorkspaceError("slice evidence is already terminal; do not add attempts to a closed slice")

    attempt = {
        "attemptId": attempt_id,
        "attemptStatus": args.attempt_status,
        "summary": summary_text,
        "evidenceRefs": list_arg(args.evidence_ref),
        "updatedAt": args.date or date.today().isoformat(),
    }
    merge_attempt(evidence, attempt)
    evidence.update(
        {
            "evidenceStatus": "attempted",
            "sliceId": slice_id,
            "summary": f"Latest attempt {attempt_id}: {summary_text}",
            "updatedAt": attempt["updatedAt"],
        }
    )
    failures = validate_artifact_data("EvidenceBundleDraft", evidence, path)
    if failures:
        raise WorkspaceError("; ".join(failures))
    write_json(path, evidence)
    append_work_file(root, path, "artifact", f"{args.work} evidence {slice_id}")
    print(f"Recorded attempt: {path} (attempt {attempt_id})")

    attempt_summary = evidence.get("attemptSummary", {})
    total = int(attempt_summary.get("total", 0) or 0)
    failed = int(attempt_summary.get("failed", 0) or 0)
    blocked = int(attempt_summary.get("blocked", 0) or 0)
    if total >= ATTEMPT_CONVERGENCE_WARNING:
        print(
            f"process-artifact-pressure: {slice_id} has {total} attempt(s), "
            f"{failed} failed, {blocked} blocked, and no terminal evidence. "
            "Stop auto-retry and route to systematic-debugging or "
            "verification-before-completion before another attempt."
        )
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
    body = (
        f"- Scope status: {args.scope_status}\n"
        f"- Compatibility status: {args.compat_status}\n"
        f"- Retirement status: {args.retirement_status}\n"
        f"- New risk signals:\n{markdown_list(list_arg(args.new_risk_signal))}"
        f"- Advisory decision: {args.decision}\n"
    )
    upsert_markdown_section(target / "20-checkpoint.md", "## DriftCheckDraft", body)
    print(f"Updated drift check: {target / 'drift-check-draft.json'}")
    return 0


def command_bundle(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    target = ensure_work_exists(root, args.work)
    task_intent = read_json_dict(target / "task-intent-draft.json")
    impact = read_json_dict(target / "impact-statement-draft.json")
    drift = read_json_dict(target / "drift-check-draft.json")
    evidence_paths = sorted(target.glob("evidence-bundle-draft*.json"))

    formal_refs: list[str] = []
    non_passed_refs: list[str] = []
    legacy_refs: list[str] = []
    superseded_count = 0
    for path in evidence_paths:
        rel = f"{work_rel(target)}/{path.name}"
        status = evidence_bundle_status(path)
        if status == "evidence-finalized":
            formal_refs.append(rel)
        elif status in {"blocked", "abandoned"}:
            non_passed_refs.append(rel)
        elif status == "superseded":
            superseded_count += 1
        elif status == "legacy-unclassified":
            legacy_refs.append(rel)

    terminal_refs = formal_refs + non_passed_refs
    gate_input = {
        "schemaVersion": SCHEMA_VERSION,
        "baselineRefs": drift.get("baselineRefs", []),
        "impactStatement": f"{work_rel(target)}/impact-statement-draft.json",
        "compatPlan": impact.get("compatBoundary", ""),
        "retirementPlan": drift.get("retirementStatus", ""),
        "evidenceBundle": terminal_refs,
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
        "\n## Terminal Evidence Refs\n\n"
        f"{markdown_list(terminal_refs)}"
        "\n## Formal Evidence\n\n"
        f"{markdown_list(formal_refs)}"
        "\n## Terminal Non-Passed Evidence\n\n"
        f"{markdown_list(non_passed_refs)}"
        "\n## Legacy Unclassified Evidence\n\n"
        f"{markdown_list(legacy_refs)}"
        f"\n## Superseded Evidence Count\n\n- {superseded_count}\n"
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
    check_parser.add_argument(
        "--process-pressure",
        action="store_true",
        help="print advisory process-artifact pressure metrics after structural checks",
    )
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

    new_adr_parser = subparsers.add_parser(
        "new-adr", help="create a helper-backed ADR in a target project workspace"
    )
    new_adr_parser.add_argument("--root", required=True, help="target project root")
    new_adr_parser.add_argument("--date", default=date.today().isoformat(), help="ADR date")
    new_adr_parser.add_argument("--slug", required=True, help="ADR slug without numeric prefix")
    new_adr_parser.add_argument("--title", required=True, help="human-readable ADR title")
    new_adr_parser.add_argument(
        "--status", required=True, choices=ADR_SOURCE_STATUSES, help="ADR evidence source status"
    )
    new_adr_parser.add_argument(
        "--source-evidence", action="append", default=[], help="source evidence summary"
    )
    new_adr_parser.add_argument("--context", required=True, help="ADR context")
    new_adr_parser.add_argument("--decision", required=True, help="ADR decision")
    new_adr_parser.add_argument(
        "--alternative", action="append", default=[], help="alternative considered"
    )
    new_adr_parser.add_argument(
        "--consequence", action="append", default=[], help="decision consequence"
    )
    new_adr_parser.add_argument(
        "--compat-boundary", required=True, help="compatibility boundary"
    )
    new_adr_parser.add_argument(
        "--retirement-impact", required=True, help="retirement impact"
    )
    new_adr_parser.add_argument(
        "--baseline-sync",
        required=True,
        choices=ADR_BASELINE_SYNC_STATES,
        help="baseline sync requirement",
    )
    new_adr_parser.add_argument(
        "--baseline-target", required=True, help="baseline sync target"
    )
    new_adr_parser.add_argument(
        "--baseline-action",
        required=True,
        choices=sorted(ADR_BASELINE_SYNC_ACTIONS),
        help="baseline sync action",
    )
    new_adr_parser.add_argument(
        "--baseline-reason", required=True, help="baseline sync reason"
    )
    new_adr_parser.add_argument(
        "--evidence-ref", action="append", default=[], help="evidence reference"
    )
    new_adr_parser.set_defaults(func=command_new_adr)

    amend_adr_parser = subparsers.add_parser(
        "amend-adr", help="append an amendment record to an existing workspace ADR"
    )
    amend_adr_parser.add_argument("--root", required=True, help="target project root")
    amend_adr_parser.add_argument("--path", required=True, help="existing ADR path inside docs/aegis/adr")
    amend_adr_parser.add_argument("--date", default=date.today().isoformat(), help="amendment date")
    amend_adr_parser.add_argument("--summary", required=True, help="amendment summary")
    amend_adr_parser.add_argument(
        "--source-evidence", action="append", default=[], help="source evidence summary"
    )
    amend_adr_parser.add_argument(
        "--compat-boundary", required=True, help="compatibility boundary"
    )
    amend_adr_parser.add_argument(
        "--retirement-impact", required=True, help="retirement impact"
    )
    amend_adr_parser.add_argument(
        "--baseline-sync",
        required=True,
        choices=ADR_BASELINE_SYNC_STATES,
        help="baseline sync requirement",
    )
    amend_adr_parser.add_argument(
        "--baseline-target", required=True, help="baseline sync target"
    )
    amend_adr_parser.add_argument(
        "--baseline-action",
        required=True,
        choices=sorted(ADR_BASELINE_SYNC_ACTIONS),
        help="baseline sync action",
    )
    amend_adr_parser.add_argument(
        "--baseline-reason", required=True, help="baseline sync reason"
    )
    amend_adr_parser.add_argument(
        "--evidence-ref", action="append", default=[], help="evidence reference"
    )
    amend_adr_parser.set_defaults(func=command_amend_adr)

    supersede_adr_parser = subparsers.add_parser(
        "supersede-adr", help="create a superseding ADR and mark the prior ADR"
    )
    supersede_adr_parser.add_argument("--root", required=True, help="target project root")
    supersede_adr_parser.add_argument("--path", required=True, help="prior ADR path inside docs/aegis/adr")
    supersede_adr_parser.add_argument("--date", default=date.today().isoformat(), help="ADR date")
    supersede_adr_parser.add_argument("--slug", required=True, help="new ADR slug without numeric prefix")
    supersede_adr_parser.add_argument("--title", required=True, help="human-readable ADR title")
    supersede_adr_parser.add_argument(
        "--status", required=True, choices=ADR_SOURCE_STATUSES, help="ADR evidence source status"
    )
    supersede_adr_parser.add_argument(
        "--source-evidence", action="append", default=[], help="source evidence summary"
    )
    supersede_adr_parser.add_argument("--context", required=True, help="ADR context")
    supersede_adr_parser.add_argument("--decision", required=True, help="ADR decision")
    supersede_adr_parser.add_argument(
        "--alternative", action="append", default=[], help="alternative considered"
    )
    supersede_adr_parser.add_argument(
        "--consequence", action="append", default=[], help="decision consequence"
    )
    supersede_adr_parser.add_argument(
        "--compat-boundary", required=True, help="compatibility boundary"
    )
    supersede_adr_parser.add_argument(
        "--retirement-impact", required=True, help="retirement impact"
    )
    supersede_adr_parser.add_argument(
        "--baseline-sync",
        required=True,
        choices=ADR_BASELINE_SYNC_STATES,
        help="baseline sync requirement",
    )
    supersede_adr_parser.add_argument(
        "--baseline-target", required=True, help="baseline sync target"
    )
    supersede_adr_parser.add_argument(
        "--baseline-action",
        required=True,
        choices=sorted(ADR_BASELINE_SYNC_ACTIONS),
        help="baseline sync action",
    )
    supersede_adr_parser.add_argument(
        "--baseline-reason", required=True, help="baseline sync reason"
    )
    supersede_adr_parser.add_argument(
        "--evidence-ref", action="append", default=[], help="evidence reference"
    )
    supersede_adr_parser.add_argument(
        "--supersession-reason", required=True, help="why the prior ADR is superseded"
    )
    supersede_adr_parser.set_defaults(func=command_supersede_adr)

    new_work_parser = subparsers.add_parser(
        "new-work", help="create helper-backed work lifecycle records"
    )
    new_work_parser.add_argument("--root", required=True, help="target project root")
    new_work_parser.add_argument("--date", default=date.today().isoformat(), help="work date")
    new_work_parser.add_argument("--slug", required=True, help="work slug without date prefix")
    new_work_parser.add_argument("--title", required=True, help="human-readable work title")
    new_work_parser.add_argument("--task-id", help="stable task id; defaults to date-slug")
    new_work_parser.add_argument("--requested-outcome", required=True, help="requested outcome")
    new_work_parser.add_argument("--goal", help="goal framing; defaults to requested outcome")
    new_work_parser.add_argument(
        "--success-evidence", action="append", default=[], help="evidence that would satisfy the goal"
    )
    new_work_parser.add_argument("--stop-condition", help="condition for done, blocked, needs verification, or scope exceeded")
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

    baseline_usage_parser = subparsers.add_parser(
        "add-baseline-usage", help="update a BaselineUsageDraft sidecar"
    )
    baseline_usage_parser.add_argument("--root", required=True, help="target project root")
    baseline_usage_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    baseline_usage_parser.add_argument(
        "--decision", required=True, choices=sorted(BASELINE_USAGE_DECISIONS)
    )
    baseline_usage_parser.add_argument(
        "--required-baseline-ref", action="append", default=[], help="required baseline ref"
    )
    baseline_usage_parser.add_argument(
        "--delivered-context-ref", action="append", default=[], help="host-projected delivered context ref"
    )
    baseline_usage_parser.add_argument(
        "--acknowledged-baseline-ref", action="append", default=[], help="acknowledged baseline ref before planning"
    )
    baseline_usage_parser.add_argument(
        "--cited-baseline-ref", action="append", default=[], help="baseline ref cited in plan or verification"
    )
    baseline_usage_parser.add_argument(
        "--missing-ref", action="append", default=[], help="missing baseline ref"
    )
    baseline_usage_parser.set_defaults(func=command_add_baseline_usage)

    attempt_parser = subparsers.add_parser(
        "add-attempt", help="record a bounded retry attempt for an active evidence slice"
    )
    attempt_parser.add_argument("--root", required=True, help="target project root")
    attempt_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    attempt_parser.add_argument("--slice-id", required=True, help="stable active slice identifier")
    attempt_parser.add_argument("--attempt-id", required=True, help="attempt identifier")
    attempt_parser.add_argument(
        "--attempt-status", required=True, choices=sorted(ATTEMPT_STATUSES), help="attempt status"
    )
    attempt_parser.add_argument("--summary", required=True, help="attempt summary")
    attempt_parser.add_argument("--type", help="evidence type for a first-attempt sidecar")
    attempt_parser.add_argument("--source", help="attempt source")
    attempt_parser.add_argument("--verifier", help="attempt verifier")
    attempt_parser.add_argument("--evidence-ref", action="append", default=[], help="attempt evidence ref")
    attempt_parser.add_argument("--date", help="attempt date, defaults to today")
    attempt_parser.set_defaults(func=command_add_attempt)

    evidence_parser = subparsers.add_parser(
        "add-evidence", help="add or finalize an EvidenceBundleDraft sidecar"
    )
    evidence_parser.add_argument("--root", required=True, help="target project root")
    evidence_parser.add_argument("--work", required=True, help="work directory name under docs/aegis/work")
    evidence_parser.add_argument("--artifact-key", required=True, help="evidence key")
    evidence_parser.add_argument("--slice-id", help="stable slice identifier; defaults to artifact-key for legacy calls")
    evidence_parser.add_argument(
        "--evidence-status",
        choices=sorted(TERMINAL_EVIDENCE_STATUSES | {"superseded"}),
        default="evidence-finalized",
        help="terminal evidence status",
    )
    evidence_parser.add_argument("--type", required=True, help="evidence type")
    evidence_parser.add_argument("--source", required=True, help="evidence source")
    evidence_parser.add_argument("--summary", required=True, help="evidence summary")
    evidence_parser.add_argument("--verifier", required=True, help="evidence verifier")
    evidence_parser.add_argument("--date", help="evidence date, defaults to today")
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
