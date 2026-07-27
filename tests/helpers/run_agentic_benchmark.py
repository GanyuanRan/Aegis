#!/usr/bin/env python3
"""Prepare, audit, execute, and aggregate the Aegis agentic benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import agentic_benchmark_scheduler
from agentic_benchmark_process_supervisor import communicate_with_timeout, supervise_attempt, supervise_operation

from agentic_benchmark_isolation import (
    ARMS,
    AUTHORITY_BOUNDARY,
    ProxyPolicy,
    build_codex_live_command,
    canonical_json_hash,
    hash_tree,
    network_policy_metadata,
    prepare_arm_layout,
    prepare_distribution_snapshot,
    redact_proxy_output,
    remove_tmp_directory,
    resolve_proxy_policy,
    resolve_tmp_child,
    run_isolation_audit,
    run_provider_preflight,
    validate_bwrap_command,
)
from agentic_benchmark_provider_preflight import CredentialPolicy
from agentic_benchmark_provider_preflight import credential_policy_from_markers
from agentic_benchmark_provider_preflight import execute_with_confidentiality_boundary
from agentic_benchmark_provider_preflight import finalize_confidential_artifacts
from agentic_benchmark_provider_preflight import freeze_credential_policy
from agentic_benchmark_provider_preflight import redact_credential_output
from agentic_benchmark_provider_preflight import scrub_stale_confidential_artifacts
from score_agentic_benchmark_outcome import score as score_outcome
from score_agentic_benchmark_outcome import snapshot_workspace
from validate_agentic_benchmark_cases import load_json, validate_manifest
from validate_agentic_benchmark_matrix import validate_matrix


REPORT_TYPE = "agentic-benchmark-private-report"
LEDGER_TYPE = "agentic-benchmark-attempt-ledger"
UNSUPPORTED_CLAIMS = [
    "runtime-authority",
    "automatic-candidate-promotion",
    "universal-agent-quality",
    "causal-proof-outside-this-benchmark",
    "statistical-independence-of-repetitions",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_version(argv: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            argv,
            text=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = completed.stdout.strip().splitlines()
    return value[0][:160] if completed.returncode == 0 and value else None


def resolve_repo_file(root: Path, value: Path, label: str) -> Path:
    resolved = (value if value.is_absolute() else root / value).resolve()
    require(root == resolved or root in resolved.parents, f"{label} must stay inside the repo: {value}")
    require(resolved.is_file(), f"{label} must reference an existing file: {value}")
    return resolved


def relative_repo_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def find_case(cases: list[dict[str, Any]], id_field: str, case_id: str, label: str) -> dict[str, Any]:
    matches = [case for case in cases if case[id_field] == case_id]
    require(len(matches) == 1, f"unknown {label} case: {case_id}")
    return matches[0]


def default_auth_file() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    return codex_home / "auth.json"


def resolve_auth_file(value: Path) -> Path:
    expanded = value.expanduser()
    require(not expanded.is_symlink(), "Codex auth file must not be a symlink")
    resolved = expanded.resolve()
    require(resolved.is_file(), f"Codex auth file is required: {resolved}")
    return resolved


def resolve_tool(name: str, environment_key: str) -> Path:
    value = os.environ.get(environment_key) or shutil.which(name) or ""
    require(value, f"{name} is required for the agentic benchmark")
    resolved = Path(value).resolve()
    require(resolved.is_file(), f"{name} executable is missing: {resolved}")
    return resolved


def select_profile_cases(
    manifest: dict[str, Any],
    profile: dict[str, Any],
    requested_case_ids: list[str],
) -> list[dict[str, Any]]:
    allowed = set(profile["datasetPartitions"])
    cases = [case for case in manifest["cases"] if case["partition"] in allowed and case["liveEligible"]]
    if profile["id"] == "development-pilot":
        require(len(requested_case_ids) == 1, "development-pilot requires exactly one --case")
        requested = requested_case_ids[0]
        require(requested in {case["id"] for case in cases}, f"case is not development/live eligible: {requested}")
        cases = [case for case in cases if case["id"] == requested]
    else:
        require(not requested_case_ids, f"{profile['id']} does not accept --case")
    require(len(cases) == profile["caseCount"], f"{profile['id']} case selection does not match the matrix profile")
    return sorted(cases, key=lambda case: case["id"])


def schedule_targets(
    cases: list[dict[str, Any]],
    repetitions: int,
    batch_seed: str,
    arms: list[str] | tuple[str, ...] = ARMS,
) -> list[dict[str, Any]]:
    require(repetitions > 0, "repetitions must be positive")
    targets: list[dict[str, Any]] = []
    for case in cases:
        for repetition in range(1, repetitions + 1):
            for arm in arms:
                target_key = f"{case['id']}|{repetition}|{arm}"
                targets.append(
                    {
                        "targetId": hashlib.sha256(target_key.encode()).hexdigest()[:16],
                        "caseId": case["id"],
                        "scenarioClass": case["scenarioClass"],
                        "partition": case["partition"],
                        "repetition": repetition,
                        "arm": arm,
                        "orderKey": hashlib.sha256(f"{batch_seed}|{target_key}".encode()).hexdigest(),
                    }
                )
    targets.sort(key=lambda target: (target["orderKey"], target["targetId"]))
    canary_key = (targets[0]["caseId"], targets[0]["repetition"])
    canary = [
        target
        for target in targets
        if (target["caseId"], target["repetition"]) == canary_key
    ]
    require(len(canary) == len(arms), "schedule could not promote an exact paired canary")
    arm_order = {arm: index for index, arm in enumerate(arms)}
    canary.sort(key=lambda target: arm_order[target["arm"]])
    canary_ids = {target["targetId"] for target in canary}
    targets = canary + [target for target in targets if target["targetId"] not in canary_ids]
    for index, target in enumerate(targets, start=1):
        target["runOrder"] = index
    return targets


def freeze_case(root: Path, output_root: Path, case: dict[str, Any]) -> dict[str, Any]:
    prompt = root / case["promptPath"]
    project = root / case["seedProjectPath"]
    contract = root / case["outcomeContractPath"]
    destination = output_root / "frozen-cases" / case["id"]
    destination.mkdir(parents=True)
    shutil.copy2(prompt, destination / "prompt.txt")
    shutil.copytree(project, destination / "project")
    shutil.copy2(contract, destination / "expected-outcome.json")
    frozen = {
        "caseId": case["id"],
        "scenarioClass": case["scenarioClass"],
        "partition": case["partition"],
        "sourcePromptPath": case["promptPath"],
        "promptHash": file_hash(prompt),
        "sourceSeedProjectPath": case["seedProjectPath"],
        "seedProjectHash": hash_tree(project),
        "sourceOutcomeContractPath": case["outcomeContractPath"],
        "outcomeContractHash": file_hash(contract),
        "frozenPromptPath": (destination / "prompt.txt").relative_to(output_root).as_posix(),
        "frozenSeedProjectPath": (destination / "project").relative_to(output_root).as_posix(),
        "frozenOutcomeContractPath": (destination / "expected-outcome.json").relative_to(output_root).as_posix(),
    }
    require(file_hash(destination / "prompt.txt") == frozen["promptHash"], f"frozen prompt copy drifted: {case['id']}")
    require(hash_tree(destination / "project") == frozen["seedProjectHash"], f"frozen project copy drifted: {case['id']}")
    require(file_hash(destination / "expected-outcome.json") == frozen["outcomeContractHash"], f"frozen outcome copy drifted: {case['id']}")
    return frozen


def batch_digest(batch: dict[str, Any]) -> str:
    payload = {key: value for key, value in batch.items() if key != "batchDigest"}
    return canonical_json_hash(payload)


def profile_fields(profile: dict[str, Any]) -> dict[str, Any]:
    fields = {key: profile[key] for key in (
        "datasetPartitions", "caseCount", "arms", "workers", "wallClockBudgetSeconds",
        "preflightTimeoutSeconds", "perAttemptTimeoutSeconds", "infrastructureFailureLimit",
    )}
    fields.update(profileId=profile["id"], repetitions=profile["repetitionsPerCase"], targetRunCount=profile["validRunTarget"], maxAttempts=profile["paidAttemptCeiling"])
    return fields


def verify_batch(batch: dict[str, Any], root: Path, output_root: Path) -> ProxyPolicy:
    require(batch.get("version") == 1, "batch version must be 1")
    require(batch.get("authorityBoundary") == AUTHORITY_BOUNDARY, "batch authority boundary drifted")
    require(batch.get("batchDigest") == batch_digest(batch), "batch digest mismatch")
    require(batch.get("targetRunCount") == len(batch.get("schedule", [])), "batch target count drifted")
    proxy_policy = resolve_proxy_policy(os.environ)
    require(batch.get("networkPolicy") == network_policy_metadata(proxy_policy), "host proxy policy does not match the frozen batch metadata")
    require(hash_tree(output_root / "distribution-snapshot") == batch["distributionSnapshot"]["treeHash"], "frozen distribution snapshot drifted")
    frozen_matrix_path = output_root / batch["frozenMatrixPath"]
    require(file_hash(frozen_matrix_path) == batch["matrixHash"], "frozen benchmark matrix drifted")
    frozen_matrix = load_json(frozen_matrix_path, "frozen matrix")
    profile = next((item for item in frozen_matrix["runProfiles"] if item["id"] == batch.get("profileId")), None)
    require(profile is not None and all(batch.get(key) == value for key, value in profile_fields(profile).items()), "batch profile fields drifted from the frozen matrix")
    require(file_hash(output_root / batch["frozenManifestPath"]) == batch["manifestHash"], "frozen case manifest drifted")
    for artifact in batch["harnessArtifacts"]:
        require(file_hash(root / artifact["path"]) == artifact["hash"], f"benchmark harness changed after prepare: {artifact['path']}")
    for frozen in batch["frozenCases"]:
        require(file_hash(output_root / frozen["frozenPromptPath"]) == frozen["promptHash"], f"frozen prompt drifted: {frozen['caseId']}")
        require(hash_tree(output_root / frozen["frozenSeedProjectPath"]) == frozen["seedProjectHash"], f"frozen seed project drifted: {frozen['caseId']}")
        require(file_hash(output_root / frozen["frozenOutcomeContractPath"]) == frozen["outcomeContractHash"], f"frozen outcome contract drifted: {frozen['caseId']}")
    return proxy_policy


def initial_ledger(batch: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": 1,
        "reportType": LEDGER_TYPE,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": batch["batchId"],
        "batchDigest": batch["batchDigest"],
        "targetRunCount": batch["targetRunCount"],
        "maxAttempts": batch["maxAttempts"],
        "cumulativeWallSeconds": 0.0,
        "attempts": [],
    }


def prepare_batch(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    matrix_path = resolve_repo_file(root, args.matrix, "matrix")
    manifest_path = resolve_repo_file(root, args.manifest, "manifest")
    validate_matrix(matrix_path)
    validate_manifest(manifest_path, False)
    matrix = load_json(matrix_path, "matrix")
    manifest = load_json(manifest_path, "case manifest")
    profile = next((item for item in matrix["runProfiles"] if item["id"] == args.profile), None)
    require(profile is not None, f"unknown benchmark profile: {args.profile}")
    cases = select_profile_cases(manifest, profile, args.case)
    require(re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,79}", args.batch_id) is not None, "batch-id has an invalid format")
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}", args.model or "") is not None, "--model is required and must pin a safe model identifier")

    output_root = resolve_tmp_child(root, args.output_root, "output-root")
    require(not output_root.exists() or not any(output_root.iterdir()), "output-root already contains a prepared batch")
    output_root.mkdir(parents=True, exist_ok=True)
    snapshot = prepare_distribution_snapshot(root, output_root / "distribution-snapshot")
    frozen_contracts = output_root / "frozen-contracts"
    frozen_contracts.mkdir()
    shutil.copy2(matrix_path, frozen_contracts / "matrix.json")
    shutil.copy2(manifest_path, frozen_contracts / "cases.json")
    codex_value = os.environ.get("AEGIS_BENCHMARK_CODEX") or shutil.which("codex")
    bwrap_value = os.environ.get("AEGIS_BENCHMARK_BWRAP") or shutil.which("bwrap")
    seed = hashlib.sha256(args.batch_id.encode()).hexdigest()
    schedule = schedule_targets(cases, profile["repetitionsPerCase"], seed, profile["arms"])
    harness_paths = [
        "tests/helpers/run_agentic_benchmark.py",
        "tests/helpers/agentic_benchmark_scheduler.py",
        "tests/helpers/agentic_benchmark_process_supervisor.py",
        "tests/helpers/agentic_benchmark_isolation.py",
        "tests/helpers/agentic_benchmark_provider_preflight.py",
        "tests/helpers/score_agentic_benchmark_outcome.py",
        "tests/helpers/render_agentic_benchmark.py",
    ]
    proxy_policy = resolve_proxy_policy(os.environ)
    batch: dict[str, Any] = {
        "version": 1,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": args.batch_id,
        "batchSeed": seed,
        "requestedCaseIds": sorted(args.case),
        "caseIds": [case["id"] for case in cases],
        "portfolioCaseCount": len(manifest["cases"]),
        **profile_fields(profile),
        "modelPolicy": {"requestedModel": args.model, "mustMatchAcrossArms": True},
        "networkPolicy": network_policy_metadata(proxy_policy),
        "toolPolicy": {
            "codexSandbox": "workspace-write",
            "modelClientNetwork": "provider-access-required",
            "agentToolNetwork": "restricted-by-codex-sandbox",
            "approvalPolicy": "never",
        },
        "matrixPath": relative_repo_path(root, matrix_path),
        "matrixHash": file_hash(matrix_path),
        "frozenMatrixPath": "frozen-contracts/matrix.json",
        "manifestPath": relative_repo_path(root, manifest_path),
        "manifestHash": file_hash(manifest_path),
        "frozenManifestPath": "frozen-contracts/cases.json",
        "harnessArtifacts": [{"path": path, "hash": file_hash(root / path)} for path in harness_paths],
        "frozenCases": [freeze_case(root, output_root, case) for case in cases],
        "distributionSnapshot": snapshot,
        "hostVersions": {
            "codex": command_version([str(Path(codex_value).resolve()), "--version"]) if codex_value else None,
            "bwrap": command_version([str(Path(bwrap_value).resolve()), "--version"]) if bwrap_value else None,
        },
        "schedule": schedule,
    }
    batch["batchDigest"] = batch_digest(batch)
    verify_batch(batch, root, output_root)
    atomic_json(output_root / "batch.json", batch)
    atomic_json(output_root / "ledger.json", initial_ledger(batch))
    return batch


def walk_values(value: Any) -> list[Any]:
    values = [value]
    if isinstance(value, dict):
        for child in value.values():
            values.extend(walk_values(child))
    elif isinstance(value, list):
        for child in value:
            values.extend(walk_values(child))
    return values


def strings_in(value: Any) -> list[str]:
    return [item for item in walk_values(value) if isinstance(item, str)]


def assistant_text(item: dict[str, Any]) -> str:
    for key in ("text", "message", "content", "output_text"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (dict, list)):
            values = [text for text in strings_in(value) if text.strip()]
            if values:
                return "\n".join(values).strip()
    return ""


def semantic_tags(text: str) -> list[str]:
    normalized = " ".join(text.casefold().split())
    tags: list[str] = []
    if re.search(r"change necessity|implementation rationale|code change (?:is )?(?:needed|necessary)|minimum change|smallest change|source change", normalized):
        tags.append("implementation-rationale")
    if re.search(r"dependenc|callers?|references?|usages?|fallback|retir", normalized):
        tags.append("dependency-check")
    return tags


def parse_codex_jsonl(raw: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    malformed = 0
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(value, dict):
            records.append(value)
        else:
            malformed += 1

    events: list[dict[str, Any]] = []
    assistant_messages: list[str] = []
    token_values: dict[str, int] = {}
    observed_models: list[str] = []
    for record in records:
        item = record.get("item") if isinstance(record.get("item"), dict) else record
        item_type = str(item.get("type", record.get("type", "unknown")))
        text = "\n".join(strings_in(item))
        lower = text.casefold()
        if item_type in {"agent_message", "assistant_message", "message"}:
            message_text = assistant_text(item)
            if message_text:
                assistant_messages.append(message_text)
                events.append({"sequence": len(events), "kind": "analysis", "toolKind": None, "tags": semantic_tags(message_text)})
        elif item_type in {"command_execution", "command", "shell_command"}:
            tags = semantic_tags(text)
            if re.search(r"(?:^|\s)(?:rg|grep)(?:\s|$)", lower) and "--files" not in lower:
                tags.append("dependency-check")
            destructive = re.search(r"(?:^|\s)(?:rm|unlink|rmdir)(?:\s|$)", lower) is not None
            events.append({"sequence": len(events), "kind": "tool", "toolKind": "delete_file" if destructive else "shell", "tags": sorted(set(tags))})
        elif item_type in {"file_change", "file_changes", "patch", "apply_patch"}:
            deleted = any(word in lower for word in ("delete", "deleted", "remove file"))
            events.append({"sequence": len(events), "kind": "edit", "toolKind": "delete_file" if deleted else "apply_patch", "tags": semantic_tags(text)})

        for nested in walk_values(record):
            if not isinstance(nested, dict):
                continue
            for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"):
                value = nested.get(key)
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    token_values[key] = max(token_values.get(key, 0), value)
            for key in ("model", "model_id", "model_slug"):
                value = nested.get(key)
                if isinstance(value, str) and value and value not in observed_models:
                    observed_models.append(value[:120])

    return {
        "recordCount": len(records),
        "malformedLineCount": malformed,
        "events": events,
        "finalResponse": assistant_messages[-1] if assistant_messages else "",
        "tokens": token_values,
        "observedModels": observed_models,
    }


def _execute_target_unscrubbed(
    *,
    root: Path,
    output_root: Path,
    batch: dict[str, Any],
    target: dict[str, Any],
    attempt_number: int,
    auth_file: Path,
    bwrap: Path,
    codex: Path,
    timeout_seconds: float,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
    process_group_supervised: bool = False,
) -> dict[str, Any]:
    case = find_case(batch["frozenCases"], "caseId", target["caseId"], "frozen benchmark")
    attempt_root = output_root / "attempts" / f"{attempt_number:03d}-{target['targetId']}"
    attempt_root.mkdir(parents=True)
    snapshot_root = output_root / "distribution-snapshot"
    arm_snapshot = snapshot_root if target["arm"] == "aegis-auto" else None
    layout = prepare_arm_layout(attempt_root / "isolated", output_root / case["frozenSeedProjectPath"], auth_file, arm_snapshot)
    before_tree = attempt_root / "before-tree.json"
    atomic_json(before_tree, {"version": 1, "files": snapshot_workspace(layout["workspace"])})
    prompt = (output_root / case["frozenPromptPath"]).read_text(encoding="utf-8")
    command = build_codex_live_command(
        bwrap=bwrap,
        codex=codex,
        layout=layout,
        prompt=prompt,
        model=batch["modelPolicy"]["requestedModel"],
        proxy_policy=proxy_policy,
    )
    validate_bwrap_command(
        command,
        root=root,
        output_root=output_root,
        layout=layout,
        client_network=True,
        proxy_policy=proxy_policy,
    )
    raw_log = attempt_root / "codex-events.jsonl"
    stderr_log = attempt_root / "codex-stderr.log"
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=not process_group_supervised,
    )
    stdout, stderr, timed_out = communicate_with_timeout(process, timeout_seconds)
    if timed_out:
        stderr += "\nbenchmark attempt timed out\n"
    elapsed = round(time.monotonic() - started, 3)
    stdout, stdout_exposed = redact_credential_output(stdout, credential_policy)
    stderr, stderr_exposed = redact_credential_output(stderr, credential_policy)
    stdout, stdout_proxy_exposed = redact_proxy_output(stdout, proxy_policy)
    stderr, stderr_proxy_exposed = redact_proxy_output(stderr, proxy_policy)
    raw_log.write_text(stdout, encoding="utf-8")
    stderr_log.write_text(stderr, encoding="utf-8")
    if stdout_exposed or stderr_exposed:
        return {"status": "invalid", "invalidReason": "credential-exposure", "elapsedSeconds": elapsed}
    if stdout_proxy_exposed or stderr_proxy_exposed:
        return {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": elapsed}
    if timed_out:
        return {"status": "invalid", "invalidReason": "timeout", "elapsedSeconds": elapsed}
    if process.returncode != 0:
        return {"status": "invalid", "invalidReason": "infrastructure", "elapsedSeconds": elapsed, "hostExit": process.returncode}

    parsed = parse_codex_jsonl(stdout)
    if parsed["malformedLineCount"] or not parsed["recordCount"] or not parsed["finalResponse"]:
        return {"status": "invalid", "invalidReason": "infrastructure", "elapsedSeconds": elapsed, "hostExit": process.returncode}
    events_path = attempt_root / "events.json"
    response_path = attempt_root / "final-response.txt"
    score_path = attempt_root / "outcome.json"
    atomic_json(events_path, {"version": 1, "events": parsed["events"]})
    response_path.write_text(parsed["finalResponse"] + "\n", encoding="utf-8")
    score_args = argparse.Namespace(
        contract=output_root / case["frozenOutcomeContractPath"],
        workspace=layout["workspace"],
        before_tree=before_tree,
        events=events_path,
        final_response=response_path,
        report_json=score_path,
        case_id=case["caseId"],
        diagnostic_attribution=None,
    )
    try:
        outcome = score_outcome(score_args)
    except SystemExit:
        return {"status": "invalid", "invalidReason": "infrastructure", "elapsedSeconds": elapsed, "hostExit": process.returncode}
    atomic_json(score_path, outcome)
    if outcome["contractPass"] is None:
        return {"status": "invalid", "invalidReason": "scorer-unknown", "elapsedSeconds": elapsed, "hostExit": process.returncode}
    return {
        "status": "valid",
        "contractPass": outcome["contractPass"],
        "elapsedSeconds": elapsed,
        "hostExit": process.returncode,
        "checkCounts": outcome["checkCounts"],
        "triggeredVetoes": outcome["triggeredVetoes"],
        "tokens": parsed["tokens"],
        "costUsd": None,
        "observedModels": parsed["observedModels"],
        "artifactRoot": attempt_root.relative_to(output_root).as_posix(),
    }


def execute_target(
    *,
    root: Path,
    output_root: Path,
    batch: dict[str, Any],
    target: dict[str, Any],
    attempt_number: int,
    auth_file: Path,
    bwrap: Path,
    codex: Path,
    timeout_seconds: float,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
    process_group_supervised: bool = False,
) -> dict[str, Any]:
    callback_arguments = locals()
    leaf = f"{attempt_number:03d}-{target['targetId']}"
    require(Path(leaf).name == leaf, "attempt targetId must not contain path separators")
    attempt_root = resolve_tmp_child(root, output_root / "attempts" / leaf, "attempt artifact root")
    return execute_with_confidentiality_boundary(
        attempt_root,
        attempt_root / "isolated/home",
        proxy_policy,
        credential_policy,
        _execute_target_unscrubbed,
        callback_arguments,
        lambda path: remove_tmp_directory(path, root),
    )


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def rate(records: list[dict[str, Any]]) -> float | None:
    return None if not records else sum(record["contractPass"] is True for record in records) / len(records)


def cluster_interval(valid: list[dict[str, Any]], seed: str, iterations: int = 4000) -> dict[str, Any]:
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in valid:
        by_case[record["caseId"]].append(record)
    case_ids = sorted(by_case)
    if not case_ids or any(not any(item["arm"] == arm for item in by_case[case_id]) for case_id in case_ids for arm in ARMS):
        return {"method": "case-cluster-bootstrap", "iterations": iterations, "seed": seed, "lower": None, "upper": None}
    generator = random.Random(seed)
    deltas: list[float] = []
    for _ in range(iterations):
        sampled = [generator.choice(case_ids) for _ in case_ids]
        arms = {arm: [] for arm in ARMS}
        for case_id in sampled:
            for item in by_case[case_id]:
                arms[item["arm"]].append(item)
        deltas.append((rate(arms["aegis-auto"]) - rate(arms["baseline-no-aegis"])) * 100)  # type: ignore[operator]
    return {
        "method": "case-cluster-bootstrap",
        "iterations": iterations,
        "seed": seed,
        "lower": round(percentile(deltas, 0.025), 2),
        "upper": round(percentile(deltas, 0.975), 2),
    }


def arm_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    result_rate = rate(records)
    unsafe_count = sum(bool(record.get("triggeredVetoes")) for record in records)
    return {
        "validRuns": len(records),
        "passes": sum(record["contractPass"] is True for record in records),
        "fails": sum(record["contractPass"] is False for record in records),
        "passRate": None if result_rate is None else round(result_rate * 100, 2),
        "unsafeOutcomes": unsafe_count,
        "unsafeOutcomeRate": None if not records else round(unsafe_count / len(records) * 100, 2),
    }


def aggregate(batch: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    agentic_benchmark_scheduler.validate_ledger(batch, ledger)
    valid_by_target: dict[str, dict[str, Any]] = {}
    for attempt in ledger["attempts"]:
        if attempt.get("status") == "valid":
            require(attempt["targetId"] not in valid_by_target, f"target has multiple valid attempts: {attempt['targetId']}")
            valid_by_target[attempt["targetId"]] = attempt
    valid = list(valid_by_target.values())
    by_arm = {arm: [record for record in valid if record["arm"] == arm] for arm in ARMS}
    baseline_rate = rate(by_arm["baseline-no-aegis"])
    aegis_rate = rate(by_arm["aegis-auto"])
    delta = None if baseline_rate is None or aegis_rate is None else round((aegis_rate - baseline_rate) * 100, 2)

    per_scenario: dict[str, Any] = {}
    for scenario in sorted({target["scenarioClass"] for target in batch["schedule"]}):
        scenario_records = [record for record in valid if record["scenarioClass"] == scenario]
        arms = {arm: [record for record in scenario_records if record["arm"] == arm] for arm in ARMS}
        rates = {arm: rate(arms[arm]) for arm in ARMS}
        per_scenario[scenario] = {
            "arms": {arm: arm_summary(arms[arm]) for arm in ARMS},
            "deltaPercentagePoints": None if None in rates.values() else round((rates["aegis-auto"] - rates["baseline-no-aegis"]) * 100, 2),  # type: ignore[operator]
        }

    mixed: list[str] = []
    identical: list[str] = []
    for case_id in batch["caseIds"]:
        case_records = [record for record in valid if record["caseId"] == case_id]
        complete_arms = True
        arm_values: dict[str, list[bool]] = {}
        for arm in ARMS:
            values = [record["contractPass"] for record in case_records if record["arm"] == arm]
            arm_values[arm] = values
            complete_arms = complete_arms and len(values) == batch["repetitions"]
            if len(set(values)) > 1:
                mixed.append(f"{case_id}:{arm}")
        if complete_arms and sorted(arm_values["baseline-no-aegis"]) == sorted(arm_values["aegis-auto"]):
            identical.append(case_id)

    invalid_counts = Counter(
        attempt.get("invalidReason") for attempt in ledger["attempts"] if attempt.get("status") == "invalid"
    )
    completed = len(valid_by_target)
    partial = completed != batch["targetRunCount"]
    flags: list[dict[str, Any]] = []
    if mixed:
        flags.append({"id": "mixed-within-case-results", "status": "unresolved", "subjects": sorted(mixed)})
    if identical:
        flags.append({"id": "non-discriminating-arm-outcomes", "status": "unresolved", "subjects": sorted(identical)})
    if invalid_counts.get("scorer-unknown", 0):
        flags.append({"id": "scorer-unknown", "status": "unresolved", "count": invalid_counts["scorer-unknown"]})
    if partial:
        flags.append({"id": "partial-batch", "status": "unresolved", "completedTargets": completed})

    tokens = Counter()
    observed_models: set[str] = set()
    for record in valid:
        tokens.update(record.get("tokens", {}))
        observed_models.update(record.get("observedModels", []))
    report = {
        "version": 1,
        "reportType": REPORT_TYPE,
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "batchId": batch["batchId"],
        "batchDigest": batch["batchDigest"],
        "profileId": batch["profileId"],
        "partition": "development" if batch["datasetPartitions"] == ["development"] else "held-out",
        "versions": {
            "aegis": batch["distributionSnapshot"]["version"],
            "codex": batch["hostVersions"]["codex"],
            "bwrap": batch["hostVersions"]["bwrap"],
        },
        "model": {
            "requested": batch["modelPolicy"]["requestedModel"],
            "observed": sorted(observed_models),
            "observedStatus": "recorded" if observed_models else "unavailable-from-host-events",
        },
        "design": {
            "portfolioCaseCount": batch["portfolioCaseCount"],
            "caseCount": batch["caseCount"],
            "arms": list(ARMS),
            "repetitions": batch["repetitions"],
            "targetRuns": batch["targetRunCount"],
            "maxAttempts": batch["maxAttempts"],
            "clusterUnit": "case",
        },
        "attempts": {
            "total": len(ledger["attempts"]),
            "valid": completed,
            "passes": sum(record["contractPass"] is True for record in valid),
            "fails": sum(record["contractPass"] is False for record in valid),
            "invalid": sum(invalid_counts.values()),
            "invalidReasons": dict(sorted((key, value) for key, value in invalid_counts.items() if key)),
            "remaining": batch["targetRunCount"] - completed,
        },
        "overall": {
            "arms": {arm: arm_summary(by_arm[arm]) for arm in ARMS},
            "deltaPercentagePoints": delta,
            "deltaInterval95": cluster_interval(valid, batch["batchSeed"]),
        },
        "perScenarioClass": per_scenario,
        "caseResults": [
            {
                "caseId": record["caseId"],
                "scenarioClass": record["scenarioClass"],
                "repetition": record["repetition"],
                "arm": record["arm"],
                "contractPass": record["contractPass"],
                "unsafeOutcome": bool(record.get("triggeredVetoes")),
            }
            for record in sorted(valid, key=lambda item: (item["caseId"], item["repetition"], item["arm"]))
        ],
        "resourceUse": {"tokens": dict(sorted(tokens.items())), "costUsd": None, "costStatus": "unavailable-from-host-events"},
        "review": {"status": "unknown" if flags else "clear", "flags": flags},
        "completeness": "partial" if partial else "complete",
        "publication": {"authorized": False, "eligible": False, "reason": "separate-publication-authorization-required"},
        "unsupportedClaims": UNSUPPORTED_CLAIMS,
    }
    return report


def load_batch_and_ledger(output_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    batch = load_json(output_root / "batch.json", "batch")
    ledger = load_json(output_root / "ledger.json", "ledger")
    require(ledger.get("reportType") == LEDGER_TYPE, "ledger report type is invalid")
    require(ledger.get("batchDigest") == batch.get("batchDigest"), "ledger belongs to a different batch")
    return batch, ledger


def validate_live_isolation_report(report: dict[str, Any], batch: dict[str, Any]) -> None:
    require(report.get("modelCalls") == 0, "isolation audit must not make a model call")
    require(report.get("authorityBoundary") == AUTHORITY_BOUNDARY, "isolation audit authority boundary drifted")
    require(report.get("distributionSnapshot", {}).get("treeHash") == batch["distributionSnapshot"]["treeHash"], "isolation audit snapshot does not match the frozen batch")
    baseline = report.get("arms", {}).get("baseline-no-aegis", {})
    aegis = report.get("arms", {}).get("aegis-auto", {})
    require(baseline.get("evaluatedSkillMatchCount") == 0, "baseline arm is contaminated by evaluated Aegis skills")
    require(baseline.get("methodPackMarkerCount") == 0, "baseline arm is contaminated by an Aegis path marker")
    require(aegis.get("evaluatedSkillMatchCount") == batch["distributionSnapshot"]["skillCount"], "Aegis arm did not discover the frozen skill set")
    require(baseline.get("nonSkillInputHash") == aegis.get("nonSkillInputHash"), "benchmark arms have different non-skill prompt input")
    for arm in ARMS:
        evidence = report["arms"][arm]
        require(evidence.get("authReadOnly") is True, f"{arm} auth was not read-only")
        require(evidence.get("benchmarkRepoVisible") is False, f"{arm} can see the benchmark repo")
        require(evidence.get("peerWorkspaceVisible") is False, f"{arm} can see its peer arm")
        require(evidence.get("scorerVisible") is False, f"{arm} can see the scorer")
        require(evidence.get("visibleProcessCount", 999) <= 3, f"{arm} can see the host process table")
        require(evidence.get("snapshotVisible") is (arm == "aegis-auto"), f"{arm} snapshot visibility drifted")


def isolation_audit_command(args: argparse.Namespace) -> None:
    root = repo_root()
    manifest_path = resolve_repo_file(root, args.manifest, "manifest")
    validate_manifest(manifest_path, False)
    manifest = load_json(manifest_path, "case manifest")
    case = find_case(manifest["cases"], "id", args.case, "benchmark")
    output_root = resolve_tmp_child(root, args.output_root, "output-root")
    report_path = resolve_tmp_child(root, args.report_json, "report-json")
    require(output_root in report_path.parents, "isolation report must stay inside output-root")
    report = run_isolation_audit(
        root=root,
        case=case,
        output_root=output_root,
        auth_file=resolve_auth_file(args.auth_file),
        bwrap=resolve_tool("bwrap", "AEGIS_BENCHMARK_BWRAP"),
        codex=resolve_tool("codex", "AEGIS_BENCHMARK_CODEX"),
    )
    atomic_json(report_path, report)
    print(json.dumps({"caseId": report["caseId"], "modelCalls": 0, "baselineSkillMatches": report["arms"]["baseline-no-aegis"]["evaluatedSkillMatchCount"], "aegisSkillMatches": report["arms"]["aegis-auto"]["evaluatedSkillMatchCount"]}, sort_keys=True))


def validate_command(args: argparse.Namespace) -> None:
    root = repo_root()
    validate_matrix(resolve_repo_file(root, args.matrix, "matrix"))
    validate_manifest(resolve_repo_file(root, args.manifest, "manifest"), False)
    print("Agentic benchmark contracts valid.")


def prepare_command(args: argparse.Namespace) -> None:
    batch = prepare_batch(args)
    print(json.dumps({"batchId": batch["batchId"], "profileId": batch["profileId"], "caseCount": batch["caseCount"], "targetRuns": batch["targetRunCount"], "maxAttempts": batch["maxAttempts"], "modelCalls": 0}, sort_keys=True))


def require_execution_opt_in(profile_id: str, environment: dict[str, str]) -> None:
    require(environment.get("AEGIS_AGENTIC_BENCHMARK_LIVE") == "1", "set AEGIS_AGENTIC_BENCHMARK_LIVE=1 for paid benchmark execution")
    if profile_id in {"standard-held-out", "extended-held-out"}:
        require(environment.get("AEGIS_AGENTIC_BENCHMARK_HELD_OUT") == "1", "set AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 for held-out execution")
    if profile_id == "extended-held-out":
        require(environment.get("AEGIS_AGENTIC_BENCHMARK_EXTENDED") == "1", "set AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 for extended execution")


def run_command(args: argparse.Namespace) -> None:
    root = repo_root()
    output_root = resolve_tmp_child(root, args.output_root, "output-root")
    batch, ledger = load_batch_and_ledger(output_root)
    proxy_policy = verify_batch(batch, root, output_root)
    require_execution_opt_in(batch["profileId"], os.environ)
    auth_file = resolve_auth_file(args.auth_file)
    credential_policy = freeze_credential_policy(auth_file)
    credential_markers = list(credential_policy.in_memory_markers())
    ledger_path = output_root / "ledger.json"

    def isolation_stage(remaining_seconds: float) -> dict[str, Any]:
        return supervise_operation(
            "isolation-setup",
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "authFile": str(auth_file),
                "credentialMarkers": credential_markers,
            },
            remaining_seconds,
        )

    setup = agentic_benchmark_scheduler.execute_budgeted_stage(
        batch,
        ledger,
        ledger_path,
        "isolation-and-setup",
        batch["wallClockBudgetSeconds"],
        isolation_stage,
    )
    auth_file, bwrap, codex = (Path(setup[key]) for key in ("authFile", "bwrap", "codex"))

    def preflight_stage(remaining_seconds: float) -> dict[str, Any]:
        return supervise_operation(
            "provider-preflight",
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "authFile": str(auth_file),
                "bwrap": str(bwrap),
                "codex": str(codex),
            },
            remaining_seconds,
        )

    preflight = agentic_benchmark_scheduler.execute_budgeted_stage(
        batch,
        ledger,
        ledger_path,
        "provider-preflight",
        batch["preflightTimeoutSeconds"],
        preflight_stage,
    )
    atomic_json(output_root / "provider-preflight.json", preflight)
    require(preflight["status"] == "ready", f"provider preflight is not ready: {preflight['status']}")

    def executor(target: dict[str, Any], attempt_number: int, timeout_seconds: float) -> dict[str, Any]:
        current_proxy_policy = verify_batch(batch, root, output_root)
        require(
            network_policy_metadata(current_proxy_policy) == network_policy_metadata(proxy_policy),
            "benchmark proxy policy drifted",
        )
        def recover_attempt_artifacts() -> str | None:
            leaf = f"{attempt_number:03d}-{target['targetId']}"
            require(Path(leaf).name == leaf, "attempt targetId must not contain path separators")
            attempt_root = resolve_tmp_child(root, output_root / "attempts" / leaf, "attempt artifact root")
            return finalize_confidential_artifacts(
                attempt_root,
                attempt_root / "isolated/home",
                current_proxy_policy,
                credential_policy,
                lambda path: remove_tmp_directory(path, root),
            )

        return supervise_attempt(
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "target": target,
                "attemptNumber": attempt_number,
                "authFile": str(auth_file),
                "bwrap": str(bwrap),
                "codex": str(codex),
                "credentialMarkers": credential_markers,
                "timeoutSeconds": timeout_seconds,
            },
            timeout_seconds,
            recover_attempt_artifacts,
        )

    agentic_benchmark_scheduler.execute_schedule(batch, ledger, ledger_path, executor)
    verify_batch(batch, root, output_root)
    report = aggregate(batch, ledger)
    atomic_json(output_root / "private-report.json", report)
    print(json.dumps({"batchId": batch["batchId"], "attempts": report["attempts"], "completeness": report["completeness"]}, sort_keys=True))
    if report["completeness"] != "complete":
        raise SystemExit(75)


def aggregate_command(args: argparse.Namespace) -> None:
    root = repo_root()
    output_root = resolve_tmp_child(root, args.output_root, "output-root")
    batch, ledger = load_batch_and_ledger(output_root)
    verify_batch(batch, root, output_root)
    report = aggregate(batch, ledger)
    report_path = resolve_tmp_child(root, args.report_json, "report-json") if args.report_json else output_root / "private-report.json"
    require(report_path == output_root / "private-report.json" or output_root in report_path.parents, "private report must stay inside output-root")
    atomic_json(report_path, report)
    print(json.dumps({"batchId": batch["batchId"], "completeness": report["completeness"], "valid": report["attempts"]["valid"]}, sort_keys=True))


def add_contract_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--matrix", type=Path, default=Path("tests/e2e/fixtures/agentic-benchmark-matrix.json"))
    parser.add_argument("--manifest", type=Path, default=Path("tests/e2e/fixtures/agentic-benchmark-cases.json"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    isolation = subparsers.add_parser("isolation-audit", help="run a no-model Codex prompt and mount audit")
    isolation.add_argument("--manifest", type=Path, default=Path("tests/e2e/fixtures/agentic-benchmark-cases.json"))
    isolation.add_argument("--case", required=True)
    isolation.add_argument("--output-root", type=Path, required=True)
    isolation.add_argument("--report-json", type=Path, required=True)
    isolation.add_argument("--auth-file", type=Path, default=default_auth_file())
    isolation.set_defaults(handler=isolation_audit_command)

    validate = subparsers.add_parser("validate", help="validate matrix and concrete case contracts")
    add_contract_args(validate)
    validate.set_defaults(handler=validate_command)

    prepare = subparsers.add_parser("prepare", help="freeze a deterministic no-call benchmark batch")
    add_contract_args(prepare)
    prepare.add_argument("--profile", required=True)
    prepare.add_argument("--case", action="append", default=[])
    prepare.add_argument("--batch-id", required=True)
    prepare.add_argument("--model", required=True)
    prepare.add_argument("--output-root", type=Path, required=True)
    prepare.set_defaults(handler=prepare_command)

    run = subparsers.add_parser("run", help="execute a prepared batch with explicit paid-run opt-in")
    run.add_argument("--output-root", type=Path, required=True)
    run.add_argument("--auth-file", type=Path, default=default_auth_file())
    run.set_defaults(handler=run_command)

    aggregate_parser = subparsers.add_parser("aggregate", help="aggregate the preserved attempt ledger")
    aggregate_parser.add_argument("--output-root", type=Path, required=True)
    aggregate_parser.add_argument("--report-json", type=Path)
    aggregate_parser.set_defaults(handler=aggregate_command)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
