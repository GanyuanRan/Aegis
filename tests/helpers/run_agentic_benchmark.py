#!/usr/bin/env python3
"""Prepare, audit, and later execute the repeated Aegis agentic benchmark."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from agentic_benchmark_isolation import resolve_tmp_child, run_isolation_audit
from validate_agentic_benchmark_cases import load_json, validate_manifest


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_file(root: Path, value: Path, label: str) -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve()
    require(root == resolved or root in resolved.parents, f"{label} must stay inside the repo: {value}")
    require(resolved.is_file(), f"{label} must reference an existing file: {value}")
    return resolved


def find_case(manifest: dict, case_id: str) -> dict:
    matches = [case for case in manifest["cases"] if case["id"] == case_id]
    require(len(matches) == 1, f"unknown benchmark case: {case_id}")
    return matches[0]


def default_auth_file() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "auth.json"
    return Path.home() / ".codex/auth.json"


def isolation_audit(args: argparse.Namespace) -> None:
    root = repo_root()
    manifest_path = resolve_repo_file(root, args.manifest, "manifest")
    validate_manifest(manifest_path, False)
    manifest = load_json(manifest_path, "case manifest")
    case = find_case(manifest, args.case)

    output_root = resolve_tmp_child(root, args.output_root, "output-root")
    report_path = resolve_tmp_child(root, args.report_json, "report-json")
    require(output_root in report_path.parents, "isolation report must stay inside output-root")
    auth_file = args.auth_file.expanduser().resolve()
    bwrap_value = os.environ.get("AEGIS_BENCHMARK_BWRAP") or shutil.which("bwrap") or ""
    codex_value = os.environ.get("AEGIS_BENCHMARK_CODEX") or shutil.which("codex") or ""
    require(bwrap_value, "bwrap is required for benchmark isolation")
    require(codex_value, "Codex executable is required for benchmark isolation")

    report = run_isolation_audit(
        root=root,
        case=case,
        output_root=output_root,
        auth_file=auth_file,
        bwrap=Path(bwrap_value).resolve(),
        codex=Path(codex_value).resolve(),
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "caseId": report["caseId"],
                "modelCalls": report["modelCalls"],
                "baselineSkillMatches": report["arms"]["baseline-no-aegis"]["evaluatedSkillMatchCount"],
                "aegisSkillMatches": report["arms"]["aegis-auto"]["evaluatedSkillMatchCount"],
            },
            sort_keys=True,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    isolation = subparsers.add_parser("isolation-audit", help="run a no-model Codex prompt and mount audit")
    isolation.add_argument("--manifest", type=Path, default=Path("tests/e2e/fixtures/agentic-benchmark-cases.json"))
    isolation.add_argument("--case", required=True)
    isolation.add_argument("--output-root", type=Path, required=True)
    isolation.add_argument("--report-json", type=Path, required=True)
    isolation.add_argument("--auth-file", type=Path, default=default_auth_file())
    isolation.set_defaults(handler=isolation_audit)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
