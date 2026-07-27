#!/usr/bin/env python3
"""Provider-network validation and confidentiality boundaries for the benchmark."""

from __future__ import annotations

import json
import hashlib
import ipaddress
import os
import signal
import subprocess
import time
from collections.abc import Callable
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import urlsplit


CommandRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]
AttemptCallback = Callable[..., dict[str, Any]]
DirectoryRemover = Callable[[Path], None]
PREFLIGHT_CLEANUP_TIMEOUT_SECONDS = 5.0
MAX_ARTIFACT_ENTRIES = 4_096
MAX_ARTIFACT_FILE_BYTES = 64 * 1024 * 1024
MAX_ARTIFACT_TOTAL_BYTES = 256 * 1024 * 1024
PROXY_KEYS = ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY")
PROXY_SCHEMES = {"http", "https", "socks5", "socks5h"}


class ProxyPolicy:
    """Validated proxy values with a deliberately secret-free representation."""

    __slots__ = ("__mapping",)

    def __init__(self, mapping: dict[str, str]) -> None:
        object.__setattr__(self, "_ProxyPolicy__mapping", MappingProxyType(dict(mapping)))

    def __setattr__(self, _name: str, _value: object) -> None:
        raise AttributeError("ProxyPolicy is immutable")

    def __repr__(self) -> str:
        return f"ProxyPolicy(mode={'proxy' if self.__mapping else 'direct'}, keys={sorted(self.__mapping)})"

    def child_environment(self) -> dict[str, str]:
        return dict(self.__mapping)


def _proxy_error(key: str, reason: str) -> None:
    raise SystemExit(f"invalid proxy environment key {key}: {reason}")


def _validate_proxy_url(key: str, value: str) -> str:
    if any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value):
        _proxy_error(key, "whitespace or control characters are forbidden")
    if "?" in value or "#" in value:
        _proxy_error(key, "query or fragment components are forbidden")
    if "\\" in value:
        _proxy_error(key, "backslashes are forbidden")
    for index, character in enumerate(value):
        if character == "%" and (index + 2 >= len(value) or any(item not in "0123456789abcdefABCDEF" for item in value[index + 1 : index + 3])):
            _proxy_error(key, "percent escape is malformed")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        _proxy_error(key, "URL or port is invalid")
    scheme = parsed.scheme.lower()
    if scheme not in PROXY_SCHEMES:
        _proxy_error(key, "scheme is not allowed")
    if not parsed.netloc or not parsed.hostname:
        _proxy_error(key, "hostname is required")
    if parsed.username is not None or parsed.password is not None:
        _proxy_error(key, "username or password is forbidden")
    if parsed.path not in {"", "/"}:
        _proxy_error(key, "proxy must contain only an authority")
    if parsed.netloc.endswith(":") or port == 0:
        _proxy_error(key, "port is invalid")
    hostname = parsed.hostname
    if ":" in hostname:
        try:
            ipaddress.IPv6Address(hostname)
        except ValueError:
            _proxy_error(key, "hostname is invalid")
    elif hostname.count(".") == 3 and all(character.isdigit() or character == "." for character in hostname):
        try:
            ipaddress.IPv4Address(hostname)
        except ValueError:
            _proxy_error(key, "hostname is invalid")
    else:
        labels = hostname.split(".")
        if any(not label or len(label) > 63 or label[0] == "-" or label[-1] == "-" or not all(character.isascii() and (character.isalnum() or character == "-") for character in label) for label in labels):
            _proxy_error(key, "hostname is invalid")
    return scheme


def resolve_proxy_policy(environment: Mapping[str, str]) -> ProxyPolicy:
    mapping: dict[str, str] = {}
    for key in PROXY_KEYS:
        lowercase = key.lower()
        upper_present = key in environment
        lower_present = lowercase in environment
        if upper_present and lower_present and environment[key] != environment[lowercase]:
            _proxy_error(key, "uppercase and lowercase values conflict")
        if not upper_present and not lower_present:
            continue
        value = environment[key] if upper_present else environment[lowercase]
        _validate_proxy_url(key, value)
        mapping[key] = value
    return ProxyPolicy(mapping)


def network_policy_metadata(policy: ProxyPolicy) -> dict[str, Any]:
    mapping = policy.child_environment()
    payload = json.dumps(mapping, sort_keys=True, separators=(",", ":")).encode()
    return {
        "mode": "proxy" if mapping else "direct",
        "keys": sorted(mapping),
        "schemes": sorted({_validate_proxy_url(key, value) for key, value in mapping.items()}),
        "fingerprint": hashlib.sha256(payload).hexdigest(),
    }


def redact_proxy_output(text: str, policy: ProxyPolicy) -> tuple[str, bool]:
    redacted = text
    exposed = False
    for value in sorted(set(policy.child_environment().values()), key=len, reverse=True):
        if value in redacted:
            redacted = redacted.replace(value, "[REDACTED_PROXY]")
            exposed = True
    return redacted, exposed


def scrub_proxy_artifact_tree(root: Path, policy: ProxyPolicy) -> bool:
    exposed = False
    entry_count = 0
    total_bytes = 0
    markers = sorted({os.fsencode(value) for value in policy.child_environment().values()}, key=len, reverse=True)
    if not root.exists():
        return False
    if root.is_symlink() or not root.is_dir():
        raise OSError("artifact root must be an ordinary directory")
    for candidate in root.rglob("*"):
        entry_count += 1
        if entry_count > MAX_ARTIFACT_ENTRIES:
            raise OSError("artifact entry-count limit exceeded")
        if candidate.is_symlink():
            payload = os.readlink(os.fsencode(candidate))
            total_bytes += len(payload)
            redacted = payload
            for marker in markers:
                redacted = redacted.replace(marker, b"[REDACTED_PROXY]")
            if redacted != payload:
                candidate.unlink()
                candidate.write_bytes(redacted)
                exposed = True
            continue
        if not candidate.is_file():
            continue
        size = candidate.stat().st_size
        total_bytes += size
        if size > MAX_ARTIFACT_FILE_BYTES or total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
            raise OSError("artifact size limit exceeded")
        payload = candidate.read_bytes()
        redacted = payload
        for marker in markers:
            if marker in redacted:
                redacted = redacted.replace(marker, b"[REDACTED_PROXY]")
                exposed = True
        if redacted != payload:
            candidate.write_bytes(redacted)
    return exposed


def finalize_proxy_artifacts(
    attempt_root: Path,
    isolated_home: Path,
    policy: ProxyPolicy,
    remove_directory: DirectoryRemover,
) -> bool:
    try:
        remove_directory(isolated_home)
        return scrub_proxy_artifact_tree(attempt_root, policy)
    except (OSError, SystemExit) as exc:
        try:
            remove_directory(attempt_root)
        except (OSError, SystemExit):
            pass
        raise SystemExit("benchmark attempt artifact cleanup failed") from exc


def execute_with_proxy_artifact_boundary(
    attempt_root: Path,
    isolated_home: Path,
    policy: ProxyPolicy,
    callback: AttemptCallback,
    callback_arguments: dict[str, Any],
    remove_directory: DirectoryRemover,
) -> dict[str, Any]:
    result: dict[str, Any] | None = None
    pending_error: BaseException | None = None
    try:
        result = callback(**callback_arguments)
    except BaseException as exc:
        pending_error = exc
    exposed = finalize_proxy_artifacts(attempt_root, isolated_home, policy, remove_directory)
    if exposed:
        elapsed = result.get("elapsedSeconds", 0.0) if result is not None else 0.0
        return {"status": "invalid", "invalidReason": "proxy-exposure", "elapsedSeconds": elapsed}
    if pending_error is not None:
        raise pending_error
    if result is None:
        raise SystemExit("benchmark attempt did not produce a result")
    return result


def scrub_stale_proxy_artifacts(
    attempts_root: Path,
    policy: ProxyPolicy,
    remove_directory: DirectoryRemover,
) -> None:
    if not attempts_root.exists():
        return
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise SystemExit("attempts artifact root must be an ordinary directory")
    for attempt_root in sorted(attempts_root.iterdir()):
        if attempt_root.is_symlink() or not attempt_root.is_dir():
            raise SystemExit("stale attempt artifact must be an ordinary directory")
        finalize_proxy_artifacts(attempt_root, attempt_root / "isolated/home", policy, remove_directory)


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
