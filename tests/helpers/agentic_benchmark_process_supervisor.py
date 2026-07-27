#!/usr/bin/env python3
"""Bounded process supervision for complete benchmark attempts."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


MAX_REQUEST_BYTES = 1_048_576
MAX_RESULT_BYTES = 65_536
PROCESS_CLEANUP_SECONDS = 1.0
CONFIDENTIAL_CLEANUP_MAX_SECONDS = 2.0


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def terminate_process(process: subprocess.Popen[str], cleanup_seconds: float = PROCESS_CLEANUP_SECONDS) -> tuple[str, str]:
    """Terminate a complete process group and reap its leader within a bound."""

    _require(cleanup_seconds > 0, "process cleanup timeout must be positive")
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        return process.communicate(timeout=cleanup_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        return process.communicate(timeout=cleanup_seconds)
    except subprocess.TimeoutExpired as exc:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
        try:
            process.wait(timeout=cleanup_seconds)
        except subprocess.TimeoutExpired:
            pass
        return _text(exc.output), _text(exc.stderr)


def communicate_with_timeout(
    process: subprocess.Popen[str],
    timeout_seconds: float,
    *,
    cleanup_timeout_seconds: float = PROCESS_CLEANUP_SECONDS,
) -> tuple[str, str, bool]:
    """Bound a subprocess and its process group; callers may discard output."""

    _require(timeout_seconds > 0, "process timeout must be positive")
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return stdout, stderr, False
    except subprocess.TimeoutExpired:
        stdout, stderr = terminate_process(process, cleanup_timeout_seconds)
        return stdout, stderr, True


def _invalid(reason: str, elapsed: float) -> dict[str, Any]:
    return {"status": "invalid", "invalidReason": reason, "elapsedSeconds": round(max(0.0, elapsed), 3)}


def supervise_process(
    command: list[str],
    payload: str,
    timeout_seconds: float,
    *,
    pass_fds: tuple[int, ...] = (),
) -> dict[str, Any]:
    """Execute one local worker tree with a deadline that includes cleanup."""

    _require(command and all(isinstance(item, str) and item for item in command), "supervisor command is invalid")
    _require(timeout_seconds > 0, "process supervisor timeout must be positive")
    cleanup_seconds = min(PROCESS_CLEANUP_SECONDS, timeout_seconds / 2)
    execution_seconds = timeout_seconds - cleanup_seconds
    _require(len(payload.encode()) <= MAX_REQUEST_BYTES, "process supervisor request is too large")
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        pass_fds=pass_fds,
    )
    try:
        stdout, _stderr = process.communicate(input=payload, timeout=execution_seconds)
    except subprocess.TimeoutExpired:
        terminate_process(process, cleanup_seconds)
        return {
            "returncode": process.returncode,
            "stdout": "",
            "elapsedSeconds": min(time.monotonic() - started, timeout_seconds),
            "timedOut": True,
            "outputExceeded": False,
        }
    encoded = stdout.encode()
    return {
        "returncode": process.returncode,
        "stdout": stdout if len(encoded) <= MAX_RESULT_BYTES else "",
        "elapsedSeconds": min(time.monotonic() - started, timeout_seconds),
        "timedOut": False,
        "outputExceeded": len(encoded) > MAX_RESULT_BYTES,
    }


def supervise_operation(
    operation: str,
    request: dict[str, Any],
    timeout_seconds: float,
) -> Any:
    """Run a complete active-run stage in one killable process."""

    _require(operation in {"attempt", "confidential-cleanup", "isolation-setup", "provider-preflight"}, "unknown supervised operation")
    worker_request = dict(request)
    worker_request["timeoutSeconds"] = timeout_seconds
    payload = json.dumps({"operation": operation, "request": worker_request}, separators=(",", ":"))
    auth_fd = request.get("authFd")
    if auth_fd is None:
        pass_fds: tuple[int, ...] = ()
    else:
        _require(isinstance(auth_fd, int) and not isinstance(auth_fd, bool) and auth_fd >= 0, "auth fd is invalid")
        _require(request.get("authFile") == f"/proc/self/fd/{auth_fd}", "auth fd path is invalid")
        try:
            os.fstat(auth_fd)
        except OSError as exc:
            raise SystemExit("auth fd is unavailable") from exc
        pass_fds = (auth_fd,)
    command = [sys.executable, str(Path(__file__).resolve()), "--worker"]
    outcome = supervise_process(command, payload, timeout_seconds, pass_fds=pass_fds) if pass_fds else supervise_process(command, payload, timeout_seconds)
    elapsed = outcome["elapsedSeconds"]

    if outcome["timedOut"]:
        if operation == "attempt":
            return _invalid("timeout", elapsed)
        raise SystemExit(f"benchmark {operation} exceeded the remaining wall-clock budget")
    if outcome["returncode"] != 0:
        if operation == "attempt":
            return _invalid("infrastructure", elapsed)
        raise SystemExit(f"benchmark {operation} failed")
    if outcome["outputExceeded"]:
        if operation == "attempt":
            return _invalid("infrastructure", elapsed)
        raise SystemExit(f"benchmark {operation} result is too large")
    try:
        result = json.loads(outcome["stdout"])
    except (TypeError, json.JSONDecodeError):
        if operation == "attempt":
            return _invalid("infrastructure", elapsed)
        raise SystemExit(f"benchmark {operation} returned an invalid result")
    if not isinstance(result, dict):
        if operation == "attempt":
            return _invalid("infrastructure", elapsed)
        raise SystemExit(f"benchmark {operation} returned an invalid result")
    if operation == "attempt":
        result["elapsedSeconds"] = round(elapsed, 3)
    return result


def _operation_budgets(timeout_seconds: float) -> tuple[float, float]:
    _require(timeout_seconds > 0, "bounded operation timeout must be positive")
    cleanup = min(CONFIDENTIAL_CLEANUP_MAX_SECONDS, timeout_seconds / 3)
    return timeout_seconds - cleanup, cleanup


def supervise_attempt(
    request: dict[str, Any],
    timeout_seconds: float,
    final_cleanup: Callable[[float, bool], str | None],
) -> dict[str, Any]:
    """Run setup, Codex, parsing, scoring and cleanup in one killable process."""

    execution_seconds, cleanup_seconds = _operation_budgets(timeout_seconds)
    result: dict[str, Any] | None = None
    pending: BaseException | None = None
    try:
        result = supervise_operation("attempt", request, execution_seconds)
    except BaseException as exc:
        pending = exc
    uncertain = pending is not None or result is None or result.get("invalidReason") in {"infrastructure", "timeout"}
    try:
        exposure = final_cleanup(cleanup_seconds, uncertain)
    except BaseException as cleanup_error:
        raise cleanup_error from None
    if exposure == "auth-drift":
        raise SystemExit("Codex auth changed during benchmark execution")
    if exposure in {"credential-exposure", "proxy-exposure"}:
        return _invalid(exposure, result.get("elapsedSeconds", 0.0) if result is not None else 0.0)
    if pending is not None:
        raise pending
    _require(result is not None, "attempt supervisor returned no result")
    return result


def supervise_stage(
    operation: str,
    request: dict[str, Any],
    timeout_seconds: float,
    final_cleanup: Callable[[float], str | None],
) -> Any:
    """Run a stage and its parent-owned confidentiality cleanup within one budget."""

    _require(operation in {"isolation-setup", "provider-preflight"}, "unknown supervised stage")
    execution_seconds, cleanup_seconds = _operation_budgets(timeout_seconds)
    result: Any = None
    pending: BaseException | None = None
    try:
        result = supervise_operation(operation, request, execution_seconds)
    except BaseException as exc:
        pending = exc
    exposure = final_cleanup(cleanup_seconds)
    if exposure == "auth-drift":
        raise SystemExit("Codex auth changed during benchmark execution")
    if exposure in {"credential-exposure", "proxy-exposure"}:
        raise SystemExit(f"benchmark {operation} confidentiality exposure detected")
    if pending is not None:
        raise pending
    return result


def supervise_confidential_cleanup(request: dict[str, Any], timeout_seconds: float) -> str | None:
    result = supervise_operation("confidential-cleanup", request, timeout_seconds)
    _require(isinstance(result, dict) and set(result) == {"exposure"}, "confidential cleanup result is invalid")
    exposure = result["exposure"]
    _require(exposure in {None, "auth-drift", "credential-exposure", "proxy-exposure"}, "confidential cleanup exposure is invalid")
    return exposure


def _path(value: Any, label: str) -> Path:
    _require(isinstance(value, str) and value, f"attempt worker {label} must be a path")
    return Path(value)


def _execute_isolation_setup(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "supervised setup root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch = request.get("batch")
    proxy_policy = runner.verify_batch(batch, root, output_root)
    auth_file = _path(request.get("authFile"), "authFile")
    runner.validate_auth_mount_file(auth_file)
    credential_policy = runner.credential_policy_from_markers(request.get("credentialMarkers"))
    attempts_root = runner.resolve_tmp_child(root, output_root / "attempts", "attempts artifact root")
    try:
        loaded_batch, ledger = runner.load_batch_and_ledger(output_root)
        _require(loaded_batch == batch, "supervised setup batch drifted")
        runner.agentic_benchmark_scheduler.validate_ledger(batch, ledger)
        completed_attempt_roots: set[str] = set()
        for attempt in ledger["attempts"]:
            if attempt.get("status") not in {"valid", "invalid"} or "recovery" in attempt:
                continue
            leaf = f"{attempt['attemptNumber']:03d}-{attempt['targetId']}"
            _require(Path(leaf).name == leaf, "ledger attempt artifact name is invalid")
            completed_attempt_roots.add(leaf)
    except BaseException:
        try:
            runner.remove_tmp_artifact_entry(attempts_root, root)
        except BaseException:
            raise SystemExit("untrusted attempt artifact cleanup failed") from None
        raise
    runner.scrub_stale_confidential_artifacts(
        attempts_root,
        completed_attempt_roots,
        proxy_policy,
        credential_policy,
        lambda path: runner.remove_tmp_artifact_entry(path, root),
    )
    bwrap = runner.resolve_tool("bwrap", "AEGIS_BENCHMARK_BWRAP")
    codex = runner.resolve_tool("codex", "AEGIS_BENCHMARK_CODEX")
    frozen_case = runner.find_case(batch["frozenCases"], "caseId", batch["caseIds"][0], "frozen benchmark")
    isolation_case = {
        "id": frozen_case["caseId"],
        "promptPath": runner.relative_repo_path(root, output_root / frozen_case["frozenPromptPath"]),
        "seedProjectPath": runner.relative_repo_path(root, output_root / frozen_case["frozenSeedProjectPath"]),
    }
    report = runner.run_isolation_audit(
        root=root,
        case=isolation_case,
        output_root=output_root / "isolation-audit",
        auth_file=auth_file,
        bwrap=bwrap,
        codex=codex,
        prepared_snapshot=output_root / "distribution-snapshot",
        timeout_seconds=request["timeoutSeconds"] + PROCESS_CLEANUP_SECONDS,
    )
    runner.validate_live_isolation_report(report, batch)
    runner.atomic_json(output_root / "isolation-report.json", report)
    return {"authFile": str(auth_file), "bwrap": str(bwrap), "codex": str(codex)}


def _execute_provider_preflight(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "supervised preflight root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch = request.get("batch")
    proxy_policy = runner.verify_batch(batch, root, output_root)
    return runner.run_provider_preflight(
        root=root,
        batch_root=output_root,
        auth_file=_path(request.get("authFile"), "authFile"),
        bwrap=_path(request.get("bwrap"), "bwrap"),
        codex=_path(request.get("codex"), "codex"),
        requested_model=batch["modelPolicy"]["requestedModel"],
        timeout_seconds=request["timeoutSeconds"] + PROCESS_CLEANUP_SECONDS,
        proxy_policy=proxy_policy,
    )


def _execute_confidential_cleanup(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "confidential cleanup root drifted")
    tree_root = runner.resolve_tmp_child(root, _path(request.get("treeRoot"), "treeRoot"), "confidential tree root")
    mode = request.get("mode")
    if mode == "purge-untrusted":
        _require(set(request) == {"root", "treeRoot", "mode", "timeoutSeconds"}, "untrusted cleanup request is invalid")
        runner.remove_tmp_artifact_entry(tree_root, root)
        return {"exposure": None}
    credential_policy = runner.credential_policy_from_markers(request.get("credentialMarkers"))
    proxy_policy = runner.resolve_proxy_policy(os.environ)
    auth_unchanged = runner.auth_source_matches_guard(request.get("authGuard"))
    if mode == "attempt":
        exposure = runner.finalize_confidential_artifacts(
            tree_root,
            tree_root / "isolated/home",
            proxy_policy,
            credential_policy,
            lambda path: runner.remove_tmp_directory(path, root),
        )
    elif mode == "stage":
        exposure = runner.finalize_confidential_stage(
            tree_root,
            proxy_policy,
            credential_policy,
            lambda path: runner.remove_tmp_directory(path, root),
        )
    elif mode == "auth-check":
        exposure = None
    else:
        raise SystemExit("confidential cleanup mode is invalid")
    if not auth_unchanged:
        if mode == "auth-check":
            runner.finalize_confidential_stage(
                tree_root,
                proxy_policy,
                credential_policy,
                lambda path: runner.remove_tmp_directory(path, root),
            )
        exposure = "auth-drift"
    return {"exposure": exposure}


def _worker() -> int:
    raw = sys.stdin.read(MAX_REQUEST_BYTES + 1)
    _require(len(raw.encode()) <= MAX_REQUEST_BYTES, "attempt worker request is too large")
    envelope = json.loads(raw)
    _require(isinstance(envelope, dict) and set(envelope) == {"operation", "request"}, "worker request is invalid")
    operation = envelope["operation"]
    request = envelope["request"]
    _require(isinstance(request, dict), "worker request must be an object")
    result_stream = os.fdopen(os.dup(sys.stdout.fileno()), "w", encoding="utf-8")
    with open(os.devnull, "w", encoding="utf-8") as sink:
        os.dup2(sink.fileno(), sys.stdout.fileno())

    import run_agentic_benchmark as runner

    if operation == "attempt":
        policy = runner.resolve_proxy_policy(os.environ)
        credential_policy = runner.credential_policy_from_markers(request.get("credentialMarkers"))
        result = runner.execute_target(
            root=_path(request.get("root"), "root"),
            output_root=_path(request.get("outputRoot"), "outputRoot"),
            batch=request.get("batch"),
            target=request.get("target"),
            attempt_number=request.get("attemptNumber"),
            auth_file=_path(request.get("authFile"), "authFile"),
            bwrap=_path(request.get("bwrap"), "bwrap"),
            codex=_path(request.get("codex"), "codex"),
            timeout_seconds=request.get("timeoutSeconds") + PROCESS_CLEANUP_SECONDS,
            proxy_policy=policy,
            credential_policy=credential_policy,
            process_group_supervised=True,
        )
    elif operation == "isolation-setup":
        result = _execute_isolation_setup(runner, request)
    elif operation == "provider-preflight":
        result = _execute_provider_preflight(runner, request)
    elif operation == "confidential-cleanup":
        result = _execute_confidential_cleanup(runner, request)
    else:
        raise SystemExit("worker operation is invalid")
    rendered = json.dumps(result, separators=(",", ":"))
    _require(len(rendered.encode()) <= MAX_RESULT_BYTES, "worker result is too large")
    result_stream.write(rendered)
    result_stream.flush()
    result_stream.close()
    return 0


if __name__ == "__main__":
    if sys.argv[1:] != ["--worker"]:
        raise SystemExit("process supervisor is an internal benchmark helper")
    try:
        raise SystemExit(_worker())
    except SystemExit:
        raise
    except BaseException:
        raise SystemExit(70) from None
