"""Argument parsing and dispatch for ``scripts/aegis-workspace.py``."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from .adr import (
    ADR_BASELINE_SYNC_ACTIONS,
    ADR_BASELINE_SYNC_STATES,
    ADR_SOURCE_STATUSES,
    command_amend_adr,
    command_new_adr,
    command_supersede_adr,
)
from .artifacts import (
    ARTIFACT_SCHEMAS,
    ATTEMPT_STATUSES,
    BASELINE_USAGE_DECISIONS,
    DRIFT_DECISIONS,
    TERMINAL_EVIDENCE_STATUSES,
    command_validate_artifact,
)
from .checks import command_check
from .errors import WorkspaceError
from .evidence import command_add_attempt, command_add_evidence, command_bundle
from .index import command_append_index
from .layout import command_init
from .work import (
    command_add_baseline_usage,
    command_add_checkpoint,
    command_add_drift_check,
    command_new_work,
)


def add_adr_target_arguments(
    parser: argparse.ArgumentParser,
    date_help: str,
    path_help: str | None = None,
    slug_help: str | None = None,
) -> None:
    """Add --root, then --path if given, --date, then --slug if given.

    The order is part of the help output; the three ADR commands differ only
    in which of these flags they take and in their help strings.
    """
    parser.add_argument("--root", required=True, help="target project root")
    if path_help is not None:
        parser.add_argument("--path", required=True, help=path_help)
    parser.add_argument("--date", default=date.today().isoformat(), help=date_help)
    if slug_help is not None:
        parser.add_argument("--slug", required=True, help=slug_help)


def add_adr_source_evidence_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source-evidence", action="append", default=[], help="source evidence summary"
    )


def add_adr_decision_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--title", required=True, help="human-readable ADR title")
    parser.add_argument(
        "--status", required=True, choices=ADR_SOURCE_STATUSES, help="ADR evidence source status"
    )
    add_adr_source_evidence_argument(parser)
    parser.add_argument("--context", required=True, help="ADR context")
    parser.add_argument("--decision", required=True, help="ADR decision")
    parser.add_argument(
        "--alternative", action="append", default=[], help="alternative considered"
    )
    parser.add_argument(
        "--consequence", action="append", default=[], help="decision consequence"
    )


def add_adr_boundary_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--compat-boundary", required=True, help="compatibility boundary")
    parser.add_argument("--retirement-impact", required=True, help="retirement impact")
    parser.add_argument(
        "--baseline-sync",
        required=True,
        choices=ADR_BASELINE_SYNC_STATES,
        help="baseline sync requirement",
    )
    parser.add_argument("--baseline-target", required=True, help="baseline sync target")
    parser.add_argument(
        "--baseline-action",
        required=True,
        choices=sorted(ADR_BASELINE_SYNC_ACTIONS),
        help="baseline sync action",
    )
    parser.add_argument("--baseline-reason", required=True, help="baseline sync reason")
    parser.add_argument(
        "--evidence-ref", action="append", default=[], help="evidence reference"
    )


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
    add_adr_target_arguments(
        new_adr_parser, date_help="ADR date", slug_help="ADR slug without numeric prefix"
    )
    add_adr_decision_arguments(new_adr_parser)
    add_adr_boundary_arguments(new_adr_parser)
    new_adr_parser.set_defaults(func=command_new_adr)

    amend_adr_parser = subparsers.add_parser(
        "amend-adr", help="append an amendment record to an existing workspace ADR"
    )
    add_adr_target_arguments(
        amend_adr_parser,
        date_help="amendment date",
        path_help="existing ADR path inside docs/aegis/adr",
    )
    amend_adr_parser.add_argument("--summary", required=True, help="amendment summary")
    add_adr_source_evidence_argument(amend_adr_parser)
    add_adr_boundary_arguments(amend_adr_parser)
    amend_adr_parser.set_defaults(func=command_amend_adr)

    supersede_adr_parser = subparsers.add_parser(
        "supersede-adr", help="create a superseding ADR and mark the prior ADR"
    )
    add_adr_target_arguments(
        supersede_adr_parser,
        date_help="ADR date",
        path_help="prior ADR path inside docs/aegis/adr",
        slug_help="new ADR slug without numeric prefix",
    )
    add_adr_decision_arguments(supersede_adr_parser)
    add_adr_boundary_arguments(supersede_adr_parser)
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
