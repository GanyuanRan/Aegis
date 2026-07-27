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
from typing import Any


MAX_REQUEST_BYTES = 1_048_576
MAX_RESULT_BYTES = 65_536
PROCESS_CLEANUP_SECONDS = 1.0


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


def supervise_process(command: list[str], payload: str, timeout_seconds: float) -> dict[str, Any]:
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


def supervise_operation(operation: str, request: dict[str, Any], timeout_seconds: float) -> Any:
    """Run a complete active-run stage in one killable process."""

    _require(operation in {"attempt", "isolation-setup", "provider-preflight"}, "unknown supervised operation")
    worker_request = dict(request)
    worker_request["timeoutSeconds"] = timeout_seconds
    payload = json.dumps({"operation": operation, "request": worker_request}, separators=(",", ":"))
    outcome = supervise_process(
        [sys.executable, str(Path(__file__).resolve()), "--worker"],
        payload,
        timeout_seconds,
    )
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


def supervise_attempt(request: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    """Run setup, Codex, parsing, scoring and cleanup in one killable process."""

    return supervise_operation("attempt", request, timeout_seconds)


def _path(value: Any, label: str) -> Path:
    _require(isinstance(value, str) and value, f"attempt worker {label} must be a path")
    return Path(value)


def _execute_isolation_setup(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "supervised setup root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch = request.get("batch")
    proxy_policy = runner.verify_batch(batch, root, output_root)
    auth_file = runner.resolve_auth_file(_path(request.get("authFile"), "authFile"))
    attempts_root = runner.resolve_tmp_child(root, output_root / "attempts", "attempts artifact root")
    runner.scrub_stale_proxy_artifacts(
        attempts_root,
        proxy_policy,
        lambda path: runner.remove_tmp_directory(path, root),
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
        auth_file=runner.resolve_auth_file(_path(request.get("authFile"), "authFile")),
        bwrap=_path(request.get("bwrap"), "bwrap"),
        codex=_path(request.get("codex"), "codex"),
        requested_model=batch["modelPolicy"]["requestedModel"],
        timeout_seconds=request["timeoutSeconds"] + PROCESS_CLEANUP_SECONDS,
        proxy_policy=proxy_policy,
    )


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
            process_group_supervised=True,
        )
    elif operation == "isolation-setup":
        result = _execute_isolation_setup(runner, request)
    elif operation == "provider-preflight":
        result = _execute_provider_preflight(runner, request)
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
