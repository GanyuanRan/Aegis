#!/usr/bin/env python3
"""Raw Codex catalog reduction for the isolated benchmark preflight."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from collections.abc import Callable
from typing import Any


CommandRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]
PREFLIGHT_CLEANUP_TIMEOUT_SECONDS = 5.0


def _terminate_process(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.communicate(timeout=PREFLIGHT_CLEANUP_TIMEOUT_SECONDS)
        return
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.communicate(timeout=PREFLIGHT_CLEANUP_TIMEOUT_SECONDS)
        return
    except subprocess.TimeoutExpired:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
    try:
        process.wait(timeout=PREFLIGHT_CLEANUP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        pass


def _default_command_runner(command: list[str], timeout_seconds: float) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _terminate_process(process)
        raise subprocess.TimeoutExpired(command[0], timeout_seconds) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _result(status: str, elapsed_seconds: float, available: bool, count: int) -> dict[str, Any]:
    return {
        "status": status,
        "elapsedSeconds": round(max(0.0, elapsed_seconds), 3),
        "requestedModelAvailable": available,
        "catalogCount": count,
    }


def run_sanitized_provider_preflight(
    command: list[str],
    requested_model: str,
    timeout_seconds: float,
    *,
    command_runner: CommandRunner | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Execute a no-inference catalog command and discard all raw output."""

    if timeout_seconds <= 0:
        raise SystemExit("provider preflight timeout must be positive")
    if not requested_model:
        raise SystemExit("provider preflight requested model must be non-empty")
    started = clock()
    try:
        completed = (command_runner or _default_command_runner)(command, timeout_seconds)
    except subprocess.TimeoutExpired:
        return _result("timeout", clock() - started, False, 0)
    except OSError:
        return _result("command-failed", clock() - started, False, 0)
    elapsed = clock() - started
    if completed.returncode != 0:
        return _result("command-failed", elapsed, False, 0)
    # Codex can retain a cached catalog and exit zero after a refresh error. Treat
    # every stderr signal as failure instead of parsing unstable log wording.
    if completed.stderr:
        return _result("command-failed", elapsed, False, 0)
    try:
        catalog = json.loads(completed.stdout)
    except (TypeError, json.JSONDecodeError):
        return _result("malformed-catalog", elapsed, False, 0)
    if not isinstance(catalog, dict) or set(catalog) != {"models"}:
        return _result("malformed-catalog", elapsed, False, 0)
    models = catalog["models"]
    if not isinstance(models, list):
        return _result("malformed-catalog", elapsed, False, 0)
    slugs: list[str] = []
    for model in models:
        if not isinstance(model, dict) or not isinstance(model.get("slug"), str) or not model["slug"]:
            return _result("malformed-catalog", elapsed, False, 0)
        slugs.append(model["slug"])
    if len(set(slugs)) != len(slugs):
        return _result("malformed-catalog", elapsed, False, 0)
    if not slugs:
        return _result("empty-catalog", elapsed, False, 0)
    available = requested_model in slugs
    return _result("ready" if available else "requested-model-missing", elapsed, available, len(slugs))
