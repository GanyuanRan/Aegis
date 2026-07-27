#!/usr/bin/env python3
"""Absolute-deadline orchestration for one paid benchmark invocation."""

from __future__ import annotations

import json
import os
import secrets
import math
import stat
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agentic_benchmark_process_supervisor import CONFIDENTIAL_CLEANUP_MAX_SECONDS
from agentic_benchmark_process_supervisor import supervise_attempt
from agentic_benchmark_process_supervisor import supervise_confidential_cleanup
from agentic_benchmark_process_supervisor import supervise_inherited_process
from agentic_benchmark_process_supervisor import supervise_operation
from agentic_benchmark_process_supervisor import supervise_stage


MAX_PARENT_RETURN_RESERVE_SECONDS = 1.0
MAX_ACTIVE_BUDGET_BYTES = 4096
MAX_PROFILE_WALL_SECONDS = 2700.0
ACTIVE_BUDGET_FIELDS = {"version", "profileId", "batchDigest", "wallClockBudgetSeconds"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _direct_output_root(value: Path) -> tuple[Path, Path]:
    root = _repo_root()
    tmp_root = (root / ".tmp").resolve()
    output_root = (value if value.is_absolute() else root / value).resolve()
    _require(tmp_root in output_root.parents, "output-root must stay below the repo .tmp directory")
    return root, output_root


def _load_active_budget(output_root: Path) -> dict[str, Any]:
    path = output_root / "active-budget.json"
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit("benchmark active budget is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        _require(stat.S_ISREG(metadata.st_mode), "benchmark active budget must be a regular file")
        _require(metadata.st_size <= MAX_ACTIVE_BUDGET_BYTES, "benchmark active budget is too large")
        payload = os.read(descriptor, MAX_ACTIVE_BUDGET_BYTES + 1)
        _require(len(payload) <= MAX_ACTIVE_BUDGET_BYTES, "benchmark active budget is too large")
        envelope = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("benchmark active budget is invalid") from exc
    finally:
        os.close(descriptor)
    _require(isinstance(envelope, dict) and set(envelope) == ACTIVE_BUDGET_FIELDS, "benchmark active budget fields are invalid")
    _require(envelope["version"] == 1, "benchmark active budget version is invalid")
    _require(isinstance(envelope["profileId"], str) and envelope["profileId"], "benchmark active budget profile is invalid")
    digest = envelope["batchDigest"]
    _require(isinstance(digest, str) and len(digest) == 64 and all(character in "0123456789abcdef" for character in digest), "benchmark active budget digest is invalid")
    wall = envelope["wallClockBudgetSeconds"]
    _require(isinstance(wall, (int, float)) and not isinstance(wall, bool), "benchmark active wall budget is invalid")
    _require(0 < float(wall) <= MAX_PROFILE_WALL_SECONDS, "benchmark active wall budget is outside the supported range")
    return envelope


def _load_bootstrap_cumulative(output_root: Path, envelope: dict[str, Any]) -> float:
    """Read a bounded conservative projection; the reservation worker remains authoritative."""

    path = output_root / "ledger.json"
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit("benchmark ledger bootstrap is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        _require(stat.S_ISREG(metadata.st_mode), "benchmark ledger bootstrap must be a regular file")
        _require(metadata.st_size <= 4 * 1024 * 1024, "benchmark ledger bootstrap is too large")
        payload = os.read(descriptor, 4 * 1024 * 1024 + 1)
        _require(len(payload) <= 4 * 1024 * 1024, "benchmark ledger bootstrap is too large")
        ledger = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("benchmark ledger bootstrap is invalid") from exc
    finally:
        os.close(descriptor)
    _require(isinstance(ledger, dict), "benchmark ledger bootstrap must be an object")
    _require(ledger.get("batchDigest") == envelope["batchDigest"], "benchmark ledger bootstrap belongs to a different batch")
    cumulative = ledger.get("cumulativeWallSeconds")
    _require(
        isinstance(cumulative, (int, float))
        and not isinstance(cumulative, bool)
        and math.isfinite(cumulative)
        and 0 <= float(cumulative) <= float(envelope["wallClockBudgetSeconds"]),
        "benchmark ledger bootstrap cumulative wall time is invalid",
    )
    return float(cumulative)


def _require_execution_opt_in(profile_id: str) -> None:
    _require(os.environ.get("AEGIS_AGENTIC_BENCHMARK_LIVE") == "1", "set AEGIS_AGENTIC_BENCHMARK_LIVE=1 for paid benchmark execution")
    if profile_id in {"standard-held-out", "extended-held-out"}:
        _require(os.environ.get("AEGIS_AGENTIC_BENCHMARK_HELD_OUT") == "1", "set AEGIS_AGENTIC_BENCHMARK_HELD_OUT=1 for held-out execution")
    if profile_id == "extended-held-out":
        _require(os.environ.get("AEGIS_AGENTIC_BENCHMARK_EXTENDED") == "1", "set AEGIS_AGENTIC_BENCHMARK_EXTENDED=1 for extended execution")


def _active_worker_command() -> list[str]:
    return [sys.executable, str(Path(__file__).resolve()), "--worker"]


def run_supervised(args: Any) -> None:
    """Own the complete paid invocation from bounded bootstrap to child reap."""

    started = time.monotonic()
    root, output_root = _direct_output_root(args.output_root)
    envelope = _load_active_budget(output_root)
    _require_execution_opt_in(envelope["profileId"])
    wall = float(envelope["wallClockBudgetSeconds"])
    bootstrap_cumulative = _load_bootstrap_cumulative(output_root, envelope)
    invocation_budget = wall - bootstrap_cumulative
    _require(invocation_budget > 0, "benchmark cumulative wall-clock budget is exhausted")
    return_reserve = min(MAX_PARENT_RETURN_RESERVE_SECONDS, max(0.01, invocation_budget / 4))

    def remaining() -> float:
        value = invocation_budget - (time.monotonic() - started) - return_reserve
        _require(value > 0, "benchmark absolute wall-clock deadline is exhausted")
        return value

    invocation_id = secrets.token_hex(16)
    reservation = supervise_operation(
        "reserve-invocation",
        {"root": str(root), "outputRoot": str(output_root), "invocationId": invocation_id},
        remaining(),
    )
    _require(
        isinstance(reservation, dict)
        and reservation.get("invocationId") == invocation_id
        and reservation.get("profileId") == envelope["profileId"]
        and reservation.get("batchDigest") == envelope["batchDigest"],
        "benchmark invocation reservation result drifted",
    )
    reserved = reservation.get("reservedWallSeconds")
    _require(isinstance(reserved, (int, float)) and not isinstance(reserved, bool) and 0 < float(reserved) <= invocation_budget, "benchmark invocation reservation is invalid")
    child_remaining = float(reserved) - (time.monotonic() - started) - return_reserve
    _require(child_remaining > 0, "benchmark absolute wall-clock deadline is exhausted")
    payload = json.dumps(
        {
            "outputRoot": str(output_root),
            "authFile": str(args.auth_file),
            "invocationId": invocation_id,
            "startedMonotonicSeconds": started,
            "reservedWallSeconds": float(reserved),
        },
        separators=(",", ":"),
    )
    outcome = supervise_inherited_process(
        _active_worker_command(),
        payload,
        child_remaining,
    )
    if outcome["timedOut"]:
        raise SystemExit("benchmark active invocation exceeded the remaining wall-clock budget")
    returncode = outcome["returncode"]
    if returncode == 75:
        raise SystemExit(75)
    _require(returncode == 0, "benchmark active invocation failed")


def run_active(
    runner: Any,
    args: Any,
    *,
    invocation_id: str | None = None,
    started_monotonic_seconds: float | None = None,
    reserved_wall_seconds: float | None = None,
) -> None:
    started = time.monotonic() if started_monotonic_seconds is None else started_monotonic_seconds
    runner.require(started <= time.monotonic(), "benchmark invocation monotonic start is invalid")
    root = runner.repo_root()
    output_root = runner.resolve_tmp_child(root, args.output_root, "output-root")
    attempts_root = output_root / "attempts"

    def purge_untrusted(timeout_seconds: float | None = None) -> None:
        if timeout_seconds is None:
            if reserved_wall_seconds is None:
                timeout_seconds = CONFIDENTIAL_CLEANUP_MAX_SECONDS
            else:
                timeout_seconds = min(
                    CONFIDENTIAL_CLEANUP_MAX_SECONDS,
                    reserved_wall_seconds - (time.monotonic() - started) - 0.01,
                )
                runner.require(timeout_seconds > 0, "benchmark absolute wall-clock deadline is exhausted")
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
        if invocation_id is None:
            initial_cumulative = float(ledger["cumulativeWallSeconds"])
            invocation_budget = float(batch["wallClockBudgetSeconds"]) - initial_cumulative
        else:
            active = ledger.get("activeInvocation")
            runner.require(isinstance(active, dict), "active invocation reservation is missing")
            runner.require(active.get("invocationId") == invocation_id, "active invocation id drifted")
            initial_cumulative = float(active["preInvocationCumulativeWallSeconds"])
            invocation_budget = float(active["reservedWallSeconds"])
            runner.require(reserved_wall_seconds == invocation_budget, "active invocation reservation drifted")
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
    return_reserve_seconds = min(MAX_PARENT_RETURN_RESERVE_SECONDS, max(0.01, invocation_budget / 4))

    def remaining(*, return_reserve: bool = False) -> float:
        reserve = return_reserve_seconds if return_reserve else 0.0
        value = invocation_budget - (time.monotonic() - started) - reserve
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

    summary: dict[str, Any] | None = None
    pending: BaseException | None = None
    try:
        if invocation_id is not None:
            runner.agentic_benchmark_scheduler.checkpoint_invocation(
                batch,
                ledger,
                ledger_path,
                invocation_id,
                time.monotonic() - started,
            )
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
    except BaseException as exc:
        pending = exc
    try:
        frozen_auth.close()
    except BaseException as exc:
        if pending is None:
            pending = exc
    if summary is not None:
        try:
            print(json.dumps(summary, sort_keys=True))
            if summary["completeness"] != "complete" and pending is None:
                pending = SystemExit(75)
        except BaseException as exc:
            if pending is None:
                pending = exc
    if invocation_id is not None:
        try:
            runner.agentic_benchmark_scheduler.settle_invocation(
                batch,
                ledger,
                ledger_path,
                invocation_id,
                time.monotonic() - started,
            )
        except BaseException as exc:
            pending = exc
    if pending is not None:
        raise pending


def _worker() -> int:
    raw = sys.stdin.read(MAX_ACTIVE_BUDGET_BYTES + 1)
    _require(len(raw.encode()) <= MAX_ACTIVE_BUDGET_BYTES, "active invocation request is too large")
    envelope = json.loads(raw)
    _require(
        isinstance(envelope, dict)
        and set(envelope)
        == {"outputRoot", "authFile", "invocationId", "startedMonotonicSeconds", "reservedWallSeconds"},
        "active invocation request is invalid",
    )
    import run_agentic_benchmark as runner

    run_active(
        runner,
        SimpleNamespace(output_root=Path(envelope["outputRoot"]), auth_file=Path(envelope["authFile"])),
        invocation_id=envelope["invocationId"],
        started_monotonic_seconds=envelope["startedMonotonicSeconds"],
        reserved_wall_seconds=envelope["reservedWallSeconds"],
    )
    return 0


if __name__ == "__main__":
    try:
        if sys.argv[1:] != ["--worker"]:
            raise SystemExit("active invocation runner is an internal benchmark helper")
        raise SystemExit(_worker())
    except SystemExit as exc:
        if isinstance(exc.code, int):
            raise
        raise SystemExit(70) from None
    except BaseException:
        raise SystemExit(70) from None
