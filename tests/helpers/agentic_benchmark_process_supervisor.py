#!/usr/bin/env python3
"""Bounded process supervision for complete benchmark attempts."""

from __future__ import annotations

import json
import ctypes
import fcntl
import os
import resource
import selectors
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


MAX_REQUEST_BYTES = 1_048_576
MAX_RESULT_BYTES = 65_536
MAX_CHILD_OUTPUT_BYTES = 16 * 1024 * 1024
PROCESS_CLEANUP_SECONDS = 1.0
CONFIDENTIAL_CLEANUP_MAX_SECONDS = 2.0
ARTIFACT_POLL_SECONDS = 0.02
PROCESS_RETURN_RESERVE_SECONDS = 0.05
PR_SET_CHILD_SUBREAPER = 36


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _direct_child_pids(root_pid: int) -> set[int]:
    try:
        return {
            int(value)
            for value in Path(f"/proc/{root_pid}/task/{root_pid}/children").read_text(encoding="ascii").split()
        }
    except (OSError, ValueError):
        return set()


def _descendant_pids(root_pid: int) -> set[int]:
    descendants: set[int] = set()
    pending = [root_pid]
    while pending:
        parent = pending.pop()
        children = _direct_child_pids(parent)
        for child in children:
            if child not in descendants:
                descendants.add(child)
                pending.append(child)
    return descendants


def _enable_child_subreaper() -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) != 0:
        raise SystemExit("process containment subreaper setup failed")


def _sealed_memfd(name: str, payload: bytes) -> int:
    _require(hasattr(os, "memfd_create"), "process supervisor requires sealed memfd support")
    descriptor = os.memfd_create(name, os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            _require(written > 0, "process supervisor request write failed")
            view = view[written:]
        os.lseek(descriptor, 0, os.SEEK_SET)
        seals = fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE
        fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, seals)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _contain_process(command_fd: int) -> int:
    """Keep a stable subreaper alive until its command tree is fully reaped."""

    _enable_child_subreaper()
    os.lseek(command_fd, 0, os.SEEK_SET)
    raw = os.read(command_fd, MAX_REQUEST_BYTES + 1)
    _require(len(raw) <= MAX_REQUEST_BYTES, "process containment request is too large")
    envelope = json.loads(raw)
    _require(isinstance(envelope, dict) and set(envelope) == {"command", "passFds"}, "process containment request is invalid")
    command = envelope["command"]
    pass_fds = envelope["passFds"]
    _require(isinstance(command, list) and command and all(isinstance(item, str) and item for item in command), "contained command is invalid")
    _require(
        isinstance(pass_fds, list)
        and all(isinstance(item, int) and not isinstance(item, bool) and item >= 0 for item in pass_fds),
        "contained pass-fd list is invalid",
    )
    termination_started: list[float | None] = [None]

    def request_termination(_signal_number: int, _frame: Any) -> None:
        if termination_started[0] is None:
            termination_started[0] = time.monotonic()

    signal.signal(signal.SIGTERM, request_termination)
    child = subprocess.Popen(
        command,
        stdin=sys.stdin.fileno(),
        stdout=sys.stdout.fileno(),
        stderr=sys.stderr.fileno(),
        start_new_session=False,
        pass_fds=tuple(pass_fds),
    )
    child_return: int | None = None
    while True:
        if child_return is None:
            child_return = child.poll()
        for pid in _direct_child_pids(os.getpid()):
            if child_return is None and pid == child.pid:
                continue
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
        descendants = _descendant_pids(os.getpid())
        if termination_started[0] is not None:
            signal_number = signal.SIGKILL if time.monotonic() - termination_started[0] >= 0.01 else signal.SIGTERM
            for pid in descendants:
                try:
                    os.kill(pid, signal_number)
                except OSError:
                    pass
        if child_return is not None:
            if not _descendant_pids(os.getpid()):
                return child_return
        time.sleep(0.002)


def _observe_descendants(root_pid: int, observed: dict[int, int]) -> None:
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        return
    for pid in _descendant_pids(root_pid):
        if pid in observed:
            continue
        try:
            observed[pid] = os.pidfd_open(pid)
        except OSError:
            continue


def _signal_process_tree(
    process: subprocess.Popen[str],
    signal_number: int,
    owns_process_group: bool,
    observed_descendants: dict[int, int] | None = None,
) -> None:
    observed = observed_descendants if observed_descendants is not None else {}
    _observe_descendants(process.pid, observed)
    if owns_process_group:
        try:
            os.killpg(process.pid, signal_number)
        except OSError:
            pass
    else:
        try:
            os.kill(process.pid, signal_number)
        except OSError:
            pass
    for descriptor in observed.values():
        try:
            signal.pidfd_send_signal(descriptor, signal_number)
        except OSError:
            pass


def artifact_limit_observed(root: Path) -> bool:
    """Sample the current artifact shape without claiming transient peak coverage."""

    from agentic_benchmark_provider_preflight import MAX_ARTIFACT_ENTRIES
    from agentic_benchmark_provider_preflight import MAX_ARTIFACT_FILE_BYTES
    from agentic_benchmark_provider_preflight import MAX_ARTIFACT_TOTAL_BYTES

    if not root.exists() or root.is_symlink() or not root.is_dir():
        return False
    entries = 0
    total_bytes = 0
    pending = [os.fsencode(root)]
    while pending:
        directory = pending.pop()
        try:
            iterator = os.scandir(directory)
        except FileNotFoundError:
            continue
        except OSError:
            return True
        with iterator:
            for entry in iterator:
                entries += 1
                if entries > MAX_ARTIFACT_ENTRIES:
                    return True
                try:
                    if entry.is_dir(follow_symlinks=False):
                        pending.append(entry.path)
                        continue
                    size = entry.stat(follow_symlinks=False).st_size
                except FileNotFoundError:
                    continue
                except OSError:
                    return True
                total_bytes += size
                if size > MAX_ARTIFACT_FILE_BYTES or total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
                    return True
    return False


def sweep_process_tree(
    process: subprocess.Popen[str],
    cleanup_deadline: float,
    *,
    owns_process_group: bool,
    observed_descendants: dict[int, int],
) -> None:
    """Kill and reap a complete observed tree within one absolute cleanup deadline."""

    def alive() -> bool:
        _observe_descendants(process.pid, observed_descendants)
        for pid, descriptor in list(observed_descendants.items()):
            try:
                signal.pidfd_send_signal(descriptor, 0)
            except OSError:
                os.close(descriptor)
                del observed_descendants[pid]
        if process.poll() is None:
            return True
        if owns_process_group:
            try:
                os.killpg(process.pid, 0)
                return True
            except OSError:
                pass
        return bool(observed_descendants)

    if not alive():
        return
    _signal_process_tree(process, signal.SIGTERM, owns_process_group, observed_descendants)
    term_deadline = time.monotonic() + max(0.0, cleanup_deadline - time.monotonic()) / 4
    while time.monotonic() < term_deadline and alive():
        time.sleep(0.01)
    _signal_process_tree(process, signal.SIGKILL, owns_process_group, observed_descendants)
    while time.monotonic() < cleanup_deadline and alive():
        time.sleep(0.005)
    process.poll()
    for descriptor in observed_descendants.values():
        os.close(descriptor)
    observed_descendants.clear()


def communicate_with_timeout(
    process: subprocess.Popen[str],
    timeout_seconds: float,
    *,
    cleanup_timeout_seconds: float = PROCESS_CLEANUP_SECONDS,
    output_limit_bytes: int = MAX_CHILD_OUTPUT_BYTES,
    owns_process_group: bool = True,
    artifact_root: Path | None = None,
) -> tuple[str, str, bool, bool, bool]:
    """Stream bounded output and terminate on growth or deadline overrun."""

    _require(timeout_seconds > 0, "process timeout must be positive")
    _require(output_limit_bytes > 0, "process output limit must be positive")
    _require(process.stdout is not None and process.stderr is not None, "bounded capture requires output pipes")
    return_reserve = min(PROCESS_RETURN_RESERVE_SECONDS, timeout_seconds / 10)
    available_seconds = timeout_seconds - return_reserve
    cleanup_seconds = min(
        cleanup_timeout_seconds,
        available_seconds,
        max(timeout_seconds / 2, min(PROCESS_RETURN_RESERVE_SECONDS, available_seconds)),
    )
    cleanup_deadline = time.monotonic() + timeout_seconds - return_reserve
    deadline = cleanup_deadline - cleanup_seconds
    stdout_fd, stderr_fd = process.stdout.fileno(), process.stderr.fileno()
    buffers = {stdout_fd: bytearray(), stderr_fd: bytearray()}
    selector = selectors.DefaultSelector()
    stopped = False
    exceeded = False
    artifact_observed = False
    next_artifact_poll = 0.0
    observed_descendants: dict[int, int] = {}
    supervision_error: BaseException | None = None
    try:
        for descriptor in buffers:
            os.set_blocking(descriptor, False)
            selector.register(descriptor, selectors.EVENT_READ)
        while selector.get_map():
            now = time.monotonic()
            _observe_descendants(process.pid, observed_descendants)
            remaining = deadline - now
            if remaining <= 0:
                stopped = True
                break
            if artifact_root is not None and now >= next_artifact_poll:
                if artifact_limit_observed(artifact_root):
                    artifact_observed = True
                    stopped = True
                    break
                next_artifact_poll = now + ARTIFACT_POLL_SECONDS
            for key, _mask in selector.select(min(remaining, ARTIFACT_POLL_SECONDS)):
                chunk = os.read(key.fd, 65_536)
                if not chunk:
                    selector.unregister(key.fd)
                    continue
                captured = len(buffers[stdout_fd]) + len(buffers[stderr_fd])
                allowed = output_limit_bytes - captured
                buffers[key.fd].extend(chunk[: max(0, allowed)])
                if len(chunk) > allowed:
                    exceeded = True
                    stopped = True
                    break
            if stopped:
                break
        if not stopped:
            remaining = deadline - time.monotonic()
            process.wait(timeout=max(0.001, remaining))
    except subprocess.TimeoutExpired:
        stopped = True
    except BaseException as exc:
        stopped = True
        supervision_error = exc
    finally:
        selector.close()
        try:
            sweep_process_tree(
                process,
                cleanup_deadline,
                owns_process_group=owns_process_group,
                observed_descendants=observed_descendants,
            )
        finally:
            stdout = buffers[stdout_fd].decode(errors="replace")
            stderr = buffers[stderr_fd].decode(errors="replace")
            process.stdout.close()
            process.stderr.close()
    if supervision_error is not None:
        raise SystemExit("process supervision failed") from None
    return stdout, stderr, stopped and not exceeded and not artifact_observed, exceeded, artifact_observed


def _invalid(reason: str, elapsed: float, error_type: str | None = None) -> dict[str, Any]:
    result = {"status": "invalid", "invalidReason": reason, "elapsedSeconds": round(max(0.0, elapsed), 3)}
    if error_type is not None:
        result["errorType"] = error_type
    return result


def supervise_process(
    command: list[str],
    payload: str,
    timeout_seconds: float,
    *,
    pass_fds: tuple[int, ...] = (),
    artifact_root: Path | None = None,
) -> dict[str, Any]:
    """Execute one local worker tree with a deadline that includes cleanup."""

    _require(command and all(isinstance(item, str) and item for item in command), "supervisor command is invalid")
    _require(timeout_seconds > 0, "process supervisor timeout must be positive")
    _require(len(payload.encode()) <= MAX_REQUEST_BYTES, "process supervisor request is too large")
    started = time.monotonic()
    _require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"), "process supervisor requires pidfd support")
    request_fd = _sealed_memfd("aegis-benchmark-request", payload.encode())
    command_payload = json.dumps(
        {"command": command, "passFds": list(pass_fds)}, separators=(",", ":")
    ).encode()
    _require(len(command_payload) <= MAX_REQUEST_BYTES, "process containment request is too large")
    command_fd = _sealed_memfd("aegis-benchmark-command", command_payload)
    try:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--contain", str(command_fd)],
            stdin=request_fd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            pass_fds=(command_fd, *pass_fds),
        )
        stdout, _stderr, timed_out, output_exceeded, artifact_observed = communicate_with_timeout(
            process,
            timeout_seconds,
            output_limit_bytes=MAX_RESULT_BYTES,
            artifact_root=artifact_root,
        )
    finally:
        os.close(request_fd)
        os.close(command_fd)
    return {
        "returncode": process.returncode,
        "stdout": "" if output_exceeded else stdout,
        "elapsedSeconds": time.monotonic() - started,
        "timedOut": timed_out,
        "outputExceeded": output_exceeded,
        "artifactLimitObserved": artifact_observed,
    }


def supervise_inherited_process(
    command: list[str],
    payload: str,
    timeout_seconds: float,
    *,
    pass_fds: tuple[int, ...] = (),
) -> dict[str, Any]:
    """Execute a contained command with inherited output under one deadline."""

    _require(command and all(isinstance(item, str) and item for item in command), "supervisor command is invalid")
    _require(timeout_seconds > 0, "process supervisor timeout must be positive")
    _require(len(payload.encode()) <= MAX_REQUEST_BYTES, "process supervisor request is too large")
    _require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"), "process supervisor requires pidfd support")
    started = time.monotonic()
    return_reserve = min(PROCESS_RETURN_RESERVE_SECONDS, timeout_seconds / 10)
    cleanup_seconds = min(PROCESS_CLEANUP_SECONDS, max(0.0, timeout_seconds - return_reserve) / 2)
    cleanup_deadline = started + timeout_seconds - return_reserve
    execution_deadline = cleanup_deadline - cleanup_seconds
    request_fd = _sealed_memfd("aegis-benchmark-request", payload.encode())
    command_payload = json.dumps(
        {"command": command, "passFds": list(pass_fds)}, separators=(",", ":")
    ).encode()
    _require(len(command_payload) <= MAX_REQUEST_BYTES, "process containment request is too large")
    command_fd = _sealed_memfd("aegis-benchmark-command", command_payload)
    observed_descendants: dict[int, int] = {}
    supervision_error: BaseException | None = None
    timed_out = False
    try:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--contain", str(command_fd)],
            stdin=request_fd,
            start_new_session=True,
            pass_fds=(command_fd, *pass_fds),
        )
        try:
            while process.poll() is None:
                _observe_descendants(process.pid, observed_descendants)
                remaining = execution_deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                time.sleep(min(0.005, remaining))
        except BaseException as exc:
            supervision_error = exc
        finally:
            sweep_process_tree(
                process,
                cleanup_deadline,
                owns_process_group=True,
                observed_descendants=observed_descendants,
            )
    finally:
        os.close(request_fd)
        os.close(command_fd)
    if supervision_error is not None:
        raise SystemExit("process supervision failed") from None
    return {
        "returncode": process.returncode,
        "elapsedSeconds": time.monotonic() - started,
        "timedOut": timed_out,
    }


def supervise_operation(
    operation: str,
    request: dict[str, Any],
    timeout_seconds: float,
) -> Any:
    """Run a complete active-run stage in one killable process."""

    _require(
        operation in {
            "attempt",
            "confidential-cleanup",
            "finalize",
            "isolation-setup",
            "provider-preflight",
            "reserve-invocation",
            "settle-invocation",
        },
        "unknown supervised operation",
    )
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
    output_root = Path(request["outputRoot"]) if isinstance(request.get("outputRoot"), str) else None
    artifact_root: Path | None = None
    if operation == "attempt" and output_root is not None:
        target = request.get("target")
        number = request.get("attemptNumber")
        if isinstance(target, dict) and isinstance(target.get("targetId"), str) and isinstance(number, int):
            leaf = f"{number:03d}-{target['targetId']}"
            if Path(leaf).name == leaf:
                artifact_root = output_root / "attempts" / leaf
    elif operation == "isolation-setup" and output_root is not None:
        artifact_root = output_root / "isolation-audit"
    elif operation == "provider-preflight" and output_root is not None:
        artifact_root = output_root / "provider-preflight-isolated"
    kwargs = {"pass_fds": pass_fds, "artifact_root": artifact_root}
    outcome = supervise_process(command, payload, timeout_seconds, **kwargs)
    elapsed = outcome["elapsedSeconds"]

    if outcome["timedOut"]:
        if operation == "attempt":
            return _invalid("timeout", elapsed)
        raise SystemExit(f"benchmark {operation} exceeded the remaining wall-clock budget")
    if outcome["outputExceeded"]:
        if operation == "attempt":
            return _invalid("infrastructure", elapsed, "supervisor-output-limit")
        raise SystemExit(f"benchmark {operation} result is too large")
    if outcome.get("artifactLimitObserved"):
        if operation == "attempt":
            return _invalid("infrastructure", elapsed, "supervisor-artifact-limit")
        raise SystemExit(f"benchmark {operation} artifact limits were observed during sampled monitoring")
    if outcome["returncode"] != 0:
        if operation == "attempt":
            return _invalid("infrastructure", elapsed, "supervisor-worker-exit")
        raise SystemExit(f"benchmark {operation} failed")
    try:
        result = json.loads(outcome["stdout"])
    except (TypeError, json.JSONDecodeError):
        if operation == "attempt":
            return _invalid("infrastructure", elapsed, "supervisor-result-invalid-json")
        raise SystemExit(f"benchmark {operation} returned an invalid result") from None
    if not isinstance(result, dict):
        if operation == "attempt":
            return _invalid("infrastructure", elapsed, "supervisor-result-invalid-shape")
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
    final_cleanup: Callable[[float, bool], str | None],
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
    exposure = final_cleanup(cleanup_seconds, pending is not None)
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
        proxy_policy=proxy_policy,
        prepared_snapshot=output_root / "distribution-snapshot",
        timeout_seconds=request["timeoutSeconds"] + PROCESS_CLEANUP_SECONDS,
        process_group_supervised=True,
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
        requested_reasoning_effort=batch["modelPolicy"]["reasoningEffort"],
        timeout_seconds=request["timeoutSeconds"] + PROCESS_CLEANUP_SECONDS,
        proxy_policy=proxy_policy,
        process_group_supervised=True,
    )


def _execute_confidential_cleanup(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "confidential cleanup root drifted")
    tree_value = _path(request.get("treeRoot"), "treeRoot")
    mode = request.get("mode")
    if mode == "purge-untrusted":
        _require(set(request) == {"root", "treeRoot", "mode", "timeoutSeconds"}, "untrusted cleanup request is invalid")
        runner.remove_tmp_artifact_entry(tree_value, root)
        return {"exposure": None}
    _require(mode in {"attempt", "stage", "auth-check"}, "confidential cleanup mode is invalid")
    try:
        tree_root = runner.resolve_tmp_child(root, tree_value, "confidential tree root")
    except BaseException:
        try:
            runner.remove_tmp_artifact_entry(tree_value, root)
        except BaseException:
            raise SystemExit("confidential cleanup path removal failed") from None
        raise
    credential_policy = runner.credential_policy_from_markers(request.get("credentialMarkers"))
    proxy_policy = runner.resolve_proxy_policy(os.environ)
    auth_unchanged = runner.auth_source_matches_guard(request.get("authGuard"))
    if mode == "attempt":
        exposure = runner.finalize_confidential_artifacts(
            tree_root,
            tree_root / "isolated/home",
            proxy_policy,
            credential_policy,
            lambda path: runner.remove_tmp_artifact_entry(path, root),
        )
        if request.get("purgeAfter") is True and tree_root.exists():
            runner.remove_tmp_artifact_entry(tree_root, root)
    elif mode == "stage":
        exposure = runner.finalize_confidential_stage(
            tree_root,
            proxy_policy,
            credential_policy,
            lambda path: runner.remove_tmp_artifact_entry(path, root),
        )
    elif mode == "auth-check":
        exposure = None
    if not auth_unchanged:
        if mode == "auth-check":
            runner.finalize_confidential_stage(
                tree_root,
                proxy_policy,
                credential_policy,
                lambda path: runner.remove_tmp_artifact_entry(path, root),
            )
        exposure = "auth-drift"
    return {"exposure": exposure}


def _execute_finalize(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "supervised finalize root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch = request.get("batch")
    runner.verify_batch(batch, root, output_root)
    loaded_batch, ledger = runner.load_batch_and_ledger(output_root)
    _require(loaded_batch == batch, "supervised finalize batch drifted")
    _require(runner.auth_source_matches_guard(request.get("authGuard")), "Codex auth changed during benchmark execution")
    report = runner.aggregate(batch, ledger)
    runner.atomic_json(output_root / "private-report.json", report)
    runner.verify_batch(batch, root, output_root)
    _require(runner.auth_source_matches_guard(request.get("authGuard")), "Codex auth changed during benchmark execution")
    return {
        "batchId": batch["batchId"],
        "attempts": report["attempts"],
        "completeness": report["completeness"],
    }


def _execute_reserve_invocation(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "invocation reservation root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch, ledger = runner.load_batch_and_ledger(output_root)
    runner.agentic_benchmark_scheduler.validate_ledger(batch, ledger)
    had_interrupted_invocation = "activeInvocation" in ledger
    try:
        active = runner.agentic_benchmark_scheduler.reserve_invocation(
            batch,
            ledger,
            output_root / "ledger.json",
            request.get("invocationId"),
        )
    except BaseException:
        if had_interrupted_invocation:
            try:
                runner.remove_tmp_artifact_entry(output_root / "attempts", root)
            except BaseException:
                raise SystemExit("interrupted invocation artifact cleanup failed") from None
        raise
    try:
        runner.verify_batch(batch, root, output_root)
        runner.require_execution_opt_in(batch["profileId"], os.environ)
    except BaseException:
        try:
            runner.remove_tmp_artifact_entry(output_root / "attempts", root)
        except BaseException:
            raise SystemExit("untrusted attempt artifact cleanup failed") from None
        raise
    return {
        "invocationId": active["invocationId"],
        "profileId": batch["profileId"],
        "batchDigest": batch["batchDigest"],
        "reservedWallSeconds": active["reservedWallSeconds"],
    }


def _execute_settle_invocation(runner: Any, request: dict[str, Any]) -> dict[str, Any]:
    root = _path(request.get("root"), "root")
    _require(root.resolve() == runner.repo_root(), "invocation settlement root drifted")
    output_root = runner.resolve_tmp_child(root, _path(request.get("outputRoot"), "outputRoot"), "output-root")
    batch, ledger = runner.load_batch_and_ledger(output_root)
    runner.verify_batch(batch, root, output_root)
    started = request.get("startedMonotonicSeconds")
    _require(
        isinstance(started, (int, float))
        and not isinstance(started, bool)
        and 0 < float(started) <= time.monotonic(),
        "invocation settlement monotonic start is invalid",
    )
    runner.agentic_benchmark_scheduler.settle_invocation(
        batch,
        ledger,
        output_root / "ledger.json",
        request.get("invocationId"),
        time.monotonic() - float(started),
    )
    return {"invocationId": request.get("invocationId"), "status": "settled"}


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
    from agentic_benchmark_provider_preflight import MAX_ARTIFACT_FILE_BYTES

    _current_soft, current_hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    file_limit = min(MAX_ARTIFACT_FILE_BYTES, current_hard) if current_hard != resource.RLIM_INFINITY else MAX_ARTIFACT_FILE_BYTES
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_limit, file_limit))

    if operation == "attempt":
        root = _path(request.get("root"), "root")
        output_root = _path(request.get("outputRoot"), "outputRoot")
        batch = request.get("batch")
        policy = runner.verify_batch(batch, root, output_root)
        runner.validate_auth_mount_file(_path(request.get("authFile"), "authFile"))
        _require(runner.auth_source_matches_guard(request.get("authGuard")), "Codex auth changed during benchmark execution")
        credential_policy = runner.credential_policy_from_markers(request.get("credentialMarkers"))
        result = runner.execute_target(
            root=root,
            output_root=output_root,
            batch=batch,
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
        runner.verify_batch(batch, root, output_root)
        _require(runner.auth_source_matches_guard(request.get("authGuard")), "Codex auth changed during benchmark execution")
    elif operation == "isolation-setup":
        result = _execute_isolation_setup(runner, request)
    elif operation == "provider-preflight":
        result = _execute_provider_preflight(runner, request)
    elif operation == "confidential-cleanup":
        result = _execute_confidential_cleanup(runner, request)
    elif operation == "finalize":
        result = _execute_finalize(runner, request)
    elif operation == "reserve-invocation":
        result = _execute_reserve_invocation(runner, request)
    elif operation == "settle-invocation":
        result = _execute_settle_invocation(runner, request)
    else:
        raise SystemExit("worker operation is invalid")
    rendered = json.dumps(result, separators=(",", ":"))
    _require(len(rendered.encode()) <= MAX_RESULT_BYTES, "worker result is too large")
    result_stream.write(rendered)
    result_stream.flush()
    result_stream.close()
    return 0


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--worker"]:
            raise SystemExit(_worker())
        if len(sys.argv) == 3 and sys.argv[1] == "--contain":
            raise SystemExit(_contain_process(int(sys.argv[2])))
        raise SystemExit("process supervisor is an internal benchmark helper")
    except SystemExit:
        raise
    except BaseException:
        raise SystemExit(70) from None
