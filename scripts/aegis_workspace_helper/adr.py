"""Workspace ADR records: ``new-adr``, ``amend-adr``, and ``supersede-adr``."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from .errors import WorkspaceError
from .index import append_index_entry, normalize_workspace_path
from .inputs import require_list, require_text
from .layout import WORKSPACE_REL, initialize_workspace, resolve_root, workspace
from .markdown import markdown_list
from .textio import append_text_lf, write_text_lf


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

    append_text_lf(
        target,
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
        "sources.\n",
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

    append_text_lf(
        prior_path,
        "\n"
        "## Superseded By\n\n"
        "- Status: superseded\n"
        f"- Date: {args.date}\n"
        f"- ADR: {target_rel}\n"
        f"- Reason: {supersession_reason}\n",
    )

    ensure_adr_indexed(root, target, args.date)
    ensure_adr_indexed(root, prior_path, args.date)
    print(f"Created superseding ADR: {target_rel}")
    return 0
