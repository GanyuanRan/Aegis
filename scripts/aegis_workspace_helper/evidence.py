"""Evidence sidecars and proof bundles: ``add-evidence``, ``add-attempt``, ``bundle``."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .artifacts import (
    ATTEMPT_STATUSES,
    EVIDENCE_STATUSES,
    SCHEMA_VERSION,
    TERMINAL_EVIDENCE_STATUSES,
    require_valid_artifact,
)
from .errors import WorkspaceError
from .index import append_index_entry
from .inputs import list_arg, load_json_file, read_json_dict, require_text
from .layout import ensure_work_exists, resolve_root, work_rel
from .markdown import markdown_list, upsert_markdown_section
from .textio import write_json, write_text_lf


ATTEMPT_CONVERGENCE_WARNING = 3
MAX_RECENT_ATTEMPTS = 5


def safe_key(value: str) -> str:
    key = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in value).strip("-")
    if not key:
        raise WorkspaceError("value must contain at least one safe character")
    return key


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


def classify_evidence_status(data: object) -> str:
    """Classify a loaded evidence sidecar for ``bundle`` and ``check --process-pressure``."""
    if not isinstance(data, dict):
        return "invalid"
    status = data.get("evidenceStatus", "legacy-unclassified")
    return status if status in EVIDENCE_STATUSES else "invalid"


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
    require_valid_artifact("EvidenceBundleDraft", evidence, path)
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
    append_index_entry(root, str(path), "artifact", f"{args.work} evidence {slice_id}")
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
    require_valid_artifact("EvidenceBundleDraft", evidence, path)
    write_json(path, evidence)
    append_index_entry(root, str(path), "artifact", f"{args.work} evidence {slice_id}")
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
        status = classify_evidence_status(load_json_file(path))
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
    append_index_entry(
        root, str(target / "gate-input-pack.json"), "artifact", f"{args.work} gate input pack"
    )

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
    append_index_entry(root, str(target / "proof-bundle.md"), "work", f"{args.work} proof bundle")
    print(f"Assembled proof bundle: {target / 'proof-bundle.md'}")
    return 0
