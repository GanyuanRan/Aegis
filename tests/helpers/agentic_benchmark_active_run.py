#!/usr/bin/env python3
"""Absolute-deadline orchestration for one paid benchmark invocation."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from agentic_benchmark_process_supervisor import CONFIDENTIAL_CLEANUP_MAX_SECONDS
from agentic_benchmark_process_supervisor import supervise_attempt
from agentic_benchmark_process_supervisor import supervise_confidential_cleanup
from agentic_benchmark_process_supervisor import supervise_operation
from agentic_benchmark_process_supervisor import supervise_stage


MAX_PARENT_RETURN_RESERVE_SECONDS = 1.0


def run_active(runner: Any, args: Any) -> None:
    started = time.monotonic()
    root = runner.repo_root()
    output_root = runner.resolve_tmp_child(root, args.output_root, "output-root")
    attempts_root = output_root / "attempts"

    def purge_untrusted(timeout_seconds: float = CONFIDENTIAL_CLEANUP_MAX_SECONDS) -> None:
        try:
            exposure = supervise_confidential_cleanup(
                {"root": str(root), "treeRoot": str(attempts_root), "mode": "purge-untrusted"},
                timeout_seconds,
            )
            runner.require(exposure is None, "untrusted benchmark artifact purge reported an exposure")
        except BaseException:
            raise SystemExit("untrusted benchmark artifact purge failed") from None

    try:
        batch, ledger = runner.load_batch_and_ledger(output_root)
        runner.agentic_benchmark_scheduler.validate_ledger(batch, ledger)
        initial_cumulative = float(ledger["cumulativeWallSeconds"])
    except BaseException:
        purge_untrusted()
        raise

    runner.require_execution_opt_in(batch["profileId"], os.environ)
    try:
        frozen_auth = runner.freeze_auth_file(args.auth_file)
    except BaseException:
        purge_untrusted()
        raise

    auth_file = frozen_auth.mount_path
    credential_markers = list(frozen_auth.credential_policy.in_memory_markers())
    ledger_path = output_root / "ledger.json"
    invocation_budget = float(batch["wallClockBudgetSeconds"]) - initial_cumulative
    return_reserve_seconds = min(MAX_PARENT_RETURN_RESERVE_SECONDS, max(0.01, invocation_budget / 4))

    def remaining(*, return_reserve: bool = False) -> float:
        reserve = return_reserve_seconds if return_reserve else 0.0
        value = float(batch["wallClockBudgetSeconds"]) - initial_cumulative - (time.monotonic() - started) - reserve
        runner.require(value > 0, "benchmark absolute wall-clock deadline is exhausted")
        return value

    def confidential_cleanup(tree_root: Path, mode: str, seconds: float, *, purge_after: bool = False) -> str | None:
        request = {
            "root": str(root),
            "treeRoot": str(tree_root),
            "mode": mode,
            "authGuard": frozen_auth.drift_guard(),
            "credentialMarkers": credential_markers,
        }
        if purge_after:
            request["purgeAfter"] = True
        return supervise_confidential_cleanup(request, min(seconds, remaining(return_reserve=True)))

    def isolation_stage(stage_seconds: float) -> dict[str, Any]:
        return supervise_stage(
            "isolation-setup",
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "authFile": str(auth_file),
                "authFd": frozen_auth.descriptor,
                "credentialMarkers": credential_markers,
            },
            min(stage_seconds, remaining(return_reserve=True)),
            isolation_cleanup,
        )

    def isolation_cleanup(seconds: float, uncertain: bool) -> str | None:
        if not uncertain:
            return confidential_cleanup(output_root / "isolation-audit", "stage", seconds)
        purge_seconds = seconds / 2
        failures: list[BaseException] = []
        exposure: str | None = None
        try:
            purge_untrusted(purge_seconds)
        except BaseException as exc:
            failures.append(exc)
        try:
            exposure = confidential_cleanup(output_root / "isolation-audit", "stage", seconds - purge_seconds)
        except BaseException as exc:
            failures.append(exc)
        if failures:
            raise SystemExit("benchmark isolation setup cleanup failed") from None
        return exposure

    def preflight_stage(stage_seconds: float) -> dict[str, Any]:
        return supervise_stage(
            "provider-preflight",
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "authFile": str(auth_file),
                "authFd": frozen_auth.descriptor,
                "bwrap": str(bwrap),
                "codex": str(codex),
            },
            min(stage_seconds, remaining(return_reserve=True)),
            lambda seconds, _uncertain: confidential_cleanup(
                output_root / "provider-preflight-isolated", "stage", seconds
            ),
        )

    def executor(target: dict[str, Any], attempt_number: int, attempt_seconds: float) -> dict[str, Any]:
        def cleanup(seconds: float, uncertain: bool) -> str | None:
            leaf = f"{attempt_number:03d}-{target['targetId']}"
            runner.require(Path(leaf).name == leaf, "attempt targetId must not contain path separators")
            mode = "attempt" if uncertain else "auth-check"
            return confidential_cleanup(output_root / "attempts" / leaf, mode, seconds, purge_after=uncertain)

        return supervise_attempt(
            {
                "root": str(root),
                "outputRoot": str(output_root),
                "batch": batch,
                "target": target,
                "attemptNumber": attempt_number,
                "authFile": str(auth_file),
                "authFd": frozen_auth.descriptor,
                "authGuard": frozen_auth.drift_guard(),
                "bwrap": str(bwrap),
                "codex": str(codex),
                "credentialMarkers": credential_markers,
            },
            min(attempt_seconds, remaining(return_reserve=True)),
            cleanup,
        )

    try:
        setup = runner.agentic_benchmark_scheduler.execute_budgeted_stage(
            batch, ledger, ledger_path, "isolation-and-setup", remaining(return_reserve=True), isolation_stage,
        )
        auth_file, bwrap, codex = (Path(setup[key]) for key in ("authFile", "bwrap", "codex"))
        preflight = runner.agentic_benchmark_scheduler.execute_budgeted_stage(
            batch,
            ledger,
            ledger_path,
            "provider-preflight",
            min(batch["preflightTimeoutSeconds"], remaining(return_reserve=True)),
            preflight_stage,
        )
        runner.atomic_json(output_root / "provider-preflight.json", preflight)
        runner.require(preflight["status"] == "ready", f"provider preflight is not ready: {preflight['status']}")
        runner.agentic_benchmark_scheduler.execute_schedule(batch, ledger, ledger_path, executor)

        def finalize_stage(stage_seconds: float) -> dict[str, Any]:
            return supervise_operation(
                "finalize",
                {
                    "root": str(root),
                    "outputRoot": str(output_root),
                    "batch": batch,
                    "authGuard": frozen_auth.drift_guard(),
                },
                min(stage_seconds, remaining(return_reserve=True)),
            )

        summary = runner.agentic_benchmark_scheduler.execute_budgeted_stage(
            batch, ledger, ledger_path, "finalize", remaining(return_reserve=True), finalize_stage,
        )
        print(json.dumps(summary, sort_keys=True))
        if summary["completeness"] != "complete":
            raise SystemExit(75)
    finally:
        frozen_auth.close()
