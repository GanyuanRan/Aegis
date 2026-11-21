"""Work lifecycle records.

Commands: ``new-work``, ``add-checkpoint``, ``add-baseline-usage``, and
``add-drift-check``.
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .artifacts import SCHEMA_VERSION, validate_artifact_data
from .errors import WorkspaceError
from .index import append_work_file
from .inputs import arg_value, list_arg, optional_none, read_json_dict
from .layout import (
    ensure_work_exists,
    initialize_workspace,
    resolve_root,
    work_dir,
    work_rel,
)
from .markdown import markdown_list, upsert_markdown_section
from .textio import write_json, write_text_lf


MAX_CHECKPOINT_HISTORY = 5


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
    # history is newest-first (previous Current, then prior updates in file
    # order), so keep the head to retain the most recent entries.
    recent = history[:MAX_CHECKPOINT_HISTORY]

    drift_match = re.search(r"(?ms)^## DriftCheckDraft\n\n(.*?)(?=\n## |\Z)", existing)

    content = f"{title}\n\n## Current Checkpoint\n\n{current_block.rstrip()}\n"
    if recent:
        content += "\n## Recent Checkpoint History\n\n"
        for entry in recent:
            content += "## Checkpoint Update\n\n" + entry + "\n"
    if drift_match and drift_match.group(1).strip():
        content += "\n## DriftCheckDraft\n\n" + drift_match.group(1).strip() + "\n"
    write_text_lf(path, content)


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
