#!/usr/bin/env python3
"""Provider-network validation and confidentiality boundaries for the benchmark."""

from __future__ import annotations

import json
import hashlib
import fcntl
import ipaddress
import os
import re
import signal
import stat
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
MAX_AUTH_FILE_BYTES = 4 * 1024 * 1024
ROOT_AUTH_FIELDS = {"auth_mode", "OPENAI_API_KEY", "tokens", "last_refresh"}
TOKEN_AUTH_FIELDS = {"id_token", "access_token", "refresh_token", "account_id"}
CREDENTIAL_PATTERN_SOURCES = (
    rb"\bsk-[A-Za-z0-9_-]{16,}\b",
    rb"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b",
    rb'''(?ix)(?:["']?(?:access_token|refresh_token|id_token|api_key|apikey|access_key|secret|password)["']?\s*[:=]\s*["']?)[^"'\s,}]{8,}''',
)
CREDENTIAL_BYTE_PATTERNS = tuple(re.compile(source) for source in CREDENTIAL_PATTERN_SOURCES)
CREDENTIAL_TEXT_PATTERNS = tuple(re.compile(source.decode("ascii")) for source in CREDENTIAL_PATTERN_SOURCES)


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


class CredentialPolicy:
    """Frozen credential markers whose representation never contains a value."""

    __slots__ = ("__markers",)

    def __init__(self, markers: tuple[str, ...]) -> None:
        if any(not isinstance(marker, str) or not marker for marker in markers):
            raise SystemExit("credential markers are invalid")
        try:
            for marker in markers:
                marker.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise SystemExit("credential markers contain invalid Unicode") from exc
        object.__setattr__(self, "_CredentialPolicy__markers", tuple(sorted(set(markers), key=len, reverse=True)))

    def __setattr__(self, _name: str, _value: object) -> None:
        raise AttributeError("CredentialPolicy is immutable")

    def __repr__(self) -> str:
        return f"CredentialPolicy(marker_count={len(self.__markers)})"

    def in_memory_markers(self) -> tuple[str, ...]:
        return self.__markers


def _credential_markers_from_auth(value: Any) -> tuple[str, ...]:
    if not isinstance(value, dict):
        raise SystemExit("Codex auth must be a JSON object")
    if any(not isinstance(key, str) or key not in ROOT_AUTH_FIELDS for key in value):
        raise SystemExit("Codex auth contains an unknown root field")
    for key in ("auth_mode", "last_refresh"):
        if key in value and value[key] is not None and not isinstance(value[key], str):
            raise SystemExit(f"Codex auth {key} metadata must be a string or null")
    tokens = value.get("tokens")
    if tokens is not None and not isinstance(tokens, dict):
        raise SystemExit("Codex auth tokens must be an object or null")
    if isinstance(tokens, dict) and any(not isinstance(key, str) or key not in TOKEN_AUTH_FIELDS for key in tokens):
        raise SystemExit("Codex auth contains an unknown tokens field")
    if isinstance(tokens, dict) and "account_id" in tokens and tokens["account_id"] is not None and not isinstance(tokens["account_id"], str):
        raise SystemExit("Codex auth account_id metadata must be a string or null")
    sensitive_values = [value.get("OPENAI_API_KEY")]
    if isinstance(tokens, dict):
        sensitive_values.extend(tokens.get(key) for key in ("id_token", "access_token", "refresh_token"))
    markers: list[str] = []
    for child in sensitive_values:
        if child is None:
            continue
        if not isinstance(child, str) or not child:
            raise SystemExit("Codex auth credential values must be non-empty strings or null")
        markers.append(child)
    return tuple(markers)


def _read_auth_bytes(auth_file: Path) -> bytes:
    path = auth_file.expanduser().absolute()
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SystemExit("Codex auth file could not be opened safely") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o022:
            raise SystemExit("Codex auth file must be a private regular file")
        chunks: list[bytes] = []
        remaining = MAX_AUTH_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > MAX_AUTH_FILE_BYTES:
            raise SystemExit("Codex auth file is too large")
        return payload
    finally:
        os.close(descriptor)


def _policy_from_auth_bytes(payload: bytes) -> CredentialPolicy:
    try:
        auth_value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit("Codex auth file could not be read safely") from exc
    return CredentialPolicy(_credential_markers_from_auth(auth_value))


class FrozenAuth:
    """A sealed in-memory auth snapshot plus its source-drift detector."""

    __slots__ = ("__descriptor", "__fingerprint", "__policy", "__source")

    def __init__(self, source: Path, payload: bytes) -> None:
        if not hasattr(os, "memfd_create"):
            raise SystemExit("sealed in-memory auth requires memfd support")
        policy = _policy_from_auth_bytes(payload)
        descriptor = os.memfd_create("aegis-benchmark-auth", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
        try:
            os.fchmod(descriptor, 0o400)
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("short memfd write")
                view = view[written:]
            os.lseek(descriptor, 0, os.SEEK_SET)
            seals = fcntl.F_SEAL_SEAL | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_GROW | fcntl.F_SEAL_WRITE
            fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, seals)
        except BaseException:
            os.close(descriptor)
            raise
        object.__setattr__(self, "_FrozenAuth__descriptor", descriptor)
        object.__setattr__(self, "_FrozenAuth__fingerprint", hashlib.sha256(payload).digest())
        object.__setattr__(self, "_FrozenAuth__policy", policy)
        object.__setattr__(self, "_FrozenAuth__source", source.expanduser().absolute())

    def __repr__(self) -> str:
        return "FrozenAuth(sealed=True)"

    @property
    def credential_policy(self) -> CredentialPolicy:
        return self.__policy

    @property
    def mount_path(self) -> Path:
        return Path(f"/proc/self/fd/{self.__descriptor}")

    @property
    def descriptor(self) -> int:
        return self.__descriptor

    def assert_source_unchanged(self) -> None:
        if hashlib.sha256(_read_auth_bytes(self.__source)).digest() != self.__fingerprint:
            raise SystemExit("Codex auth changed after benchmark execution started")

    def drift_guard(self) -> dict[str, str]:
        return {"source": str(self.__source), "fingerprint": self.__fingerprint.hex()}

    def close(self) -> None:
        descriptor = self.__descriptor
        if descriptor >= 0:
            os.close(descriptor)
            object.__setattr__(self, "_FrozenAuth__descriptor", -1)


def freeze_auth_file(auth_file: Path) -> FrozenAuth:
    """Securely read auth once and seal that exact content for every mount."""

    path = auth_file.expanduser().absolute()
    return FrozenAuth(path, _read_auth_bytes(path))


def freeze_credential_policy(auth_file: Path) -> CredentialPolicy:
    """Freeze credential markers without creating a mount snapshot."""

    return _policy_from_auth_bytes(_read_auth_bytes(auth_file))


def auth_source_matches_guard(guard: Any) -> bool:
    if not isinstance(guard, dict) or set(guard) != {"source", "fingerprint"}:
        raise SystemExit("auth drift guard is invalid")
    source = guard["source"]
    fingerprint = guard["fingerprint"]
    if not isinstance(source, str) or not source or not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise SystemExit("auth drift guard is invalid")
    try:
        current = hashlib.sha256(_read_auth_bytes(Path(source))).hexdigest()
    except SystemExit:
        return False
    return current == fingerprint


def validate_auth_mount_file(auth_file: Path) -> None:
    """Accept a private regular file or the benchmark's sealed memfd path."""

    try:
        metadata = auth_file.stat()
        target = os.readlink(auth_file) if auth_file.is_symlink() else ""
    except OSError as exc:
        raise SystemExit("benchmark auth mount is unavailable") from exc
    is_frozen_memfd = bool(re.fullmatch(r"/proc/self/fd/[0-9]+", str(auth_file))) and target.startswith(
        "/memfd:aegis-benchmark-auth"
    )
    if auth_file.is_symlink() and not is_frozen_memfd:
        raise SystemExit("benchmark auth mount must not be a symlink")
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o022:
        raise SystemExit("benchmark auth mount must be a private regular file")


def command_memfd_descriptors(command: list[str]) -> tuple[int, ...]:
    descriptors = {
        int(match.group(1))
        for value in command
        if (match := re.fullmatch(r"/proc/self/fd/([0-9]+)", value)) is not None
    }
    descriptors.update(
        int(command[index + 1])
        for index, value in enumerate(command[:-1])
        if value == "--ro-bind-data" and command[index + 1].isdigit()
    )
    return tuple(sorted(descriptors))


def credential_policy_from_markers(markers: Any) -> CredentialPolicy:
    if not isinstance(markers, list) or any(not isinstance(marker, str) for marker in markers):
        raise SystemExit("credential marker transfer is invalid")
    return CredentialPolicy(tuple(markers))


def redact_credential_output(text: str, policy: CredentialPolicy) -> tuple[str, bool]:
    redacted = text
    exposed = False
    for marker in policy.in_memory_markers():
        if marker in redacted:
            redacted = redacted.replace(marker, "[REDACTED_CREDENTIAL]")
            exposed = True
    for pattern in CREDENTIAL_TEXT_PATTERNS:
        redacted, count = pattern.subn("[REDACTED_CREDENTIAL]", redacted)
        exposed = exposed or count > 0
    return redacted, exposed


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


def _credential_exposed(payload: bytes, policy: CredentialPolicy) -> bool:
    markers = (marker.encode("utf-8") for marker in policy.in_memory_markers())
    return any(marker in payload for marker in markers) or any(pattern.search(payload) for pattern in CREDENTIAL_BYTE_PATTERNS)


def _proxy_markers(policy: ProxyPolicy) -> tuple[bytes, ...]:
    return tuple(sorted({os.fsencode(value) for value in policy.child_environment().values()}, key=len, reverse=True))


def classify_confidential_payload(payload: bytes, proxy_policy: ProxyPolicy, credential_policy: CredentialPolicy) -> str | None:
    if _credential_exposed(payload, credential_policy):
        return "credential-exposure"
    if any(marker in payload for marker in _proxy_markers(proxy_policy)):
        return "proxy-exposure"
    return None


def scrub_confidential_artifact_tree(
    root: Path,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
) -> str | None:
    proxy_exposed = False
    entry_count = 0
    total_bytes = 0
    proxy_markers = _proxy_markers(proxy_policy)
    if not root.exists():
        return None
    if root.is_symlink() or not root.is_dir():
        raise OSError("artifact root must be an ordinary directory")
    root_device = root.stat().st_dev

    def scrub_xattrs(candidate: bytes) -> str | None:
        nonlocal entry_count, total_bytes, proxy_exposed
        for raw_name in os.listxattr(candidate, follow_symlinks=False):
            entry_count += 1
            if entry_count > MAX_ARTIFACT_ENTRIES:
                raise OSError("artifact entry-count limit exceeded")
            name = raw_name if isinstance(raw_name, bytes) else os.fsencode(raw_name)
            value = os.getxattr(candidate, raw_name, follow_symlinks=False)
            if len(value) > MAX_ARTIFACT_FILE_BYTES:
                raise OSError("artifact size limit exceeded")
            total_bytes += len(name) + len(value)
            if total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
                raise OSError("artifact size limit exceeded")
            if _credential_exposed(name, credential_policy) or _credential_exposed(value, credential_policy):
                return "credential-exposure"
            if any(marker in name or marker in value for marker in proxy_markers):
                proxy_exposed = True
            os.removexattr(candidate, raw_name, follow_symlinks=False)
        return None

    root_exposure = scrub_xattrs(os.fsencode(root))
    if root_exposure is not None:
        return root_exposure
    pending = [os.fsencode(root)]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as iterator:
            entries = sorted(iterator, key=lambda entry: entry.name)
        for entry in entries:
            entry_count += 1
            if entry_count > MAX_ARTIFACT_ENTRIES:
                raise OSError("artifact entry-count limit exceeded")
            name = entry.name if isinstance(entry.name, bytes) else os.fsencode(entry.name)
            if _credential_exposed(name, credential_policy):
                return "credential-exposure"
            candidate = entry.path if isinstance(entry.path, bytes) else os.fsencode(entry.path)
            is_symlink = entry.is_symlink()
            is_directory = entry.is_dir(follow_symlinks=False)
            is_regular = entry.is_file(follow_symlinks=False)
            if not (is_symlink or is_directory or is_regular):
                raise OSError("artifact tree contains an unsupported entry type")
            metadata = entry.stat(follow_symlinks=False)
            if metadata.st_dev != root_device:
                raise OSError("artifact entries must stay on the artifact filesystem")
            if (is_symlink or is_regular) and metadata.st_nlink != 1:
                raise OSError("artifact files and symlinks must not be hard-linked")
            xattr_exposure = scrub_xattrs(candidate)
            if xattr_exposure is not None:
                return xattr_exposure
            if is_symlink:
                payload = os.readlink(candidate)
                total_bytes += len(payload)
                if total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
                    raise OSError("artifact size limit exceeded")
                if _credential_exposed(payload, credential_policy):
                    return "credential-exposure"
                redacted = payload
                for marker in proxy_markers:
                    redacted = redacted.replace(marker, b"[REDACTED_PROXY]")
                if redacted != payload:
                    os.unlink(candidate)
                    with open(candidate, "xb") as stream:
                        stream.write(redacted)
                    proxy_exposed = True
                continue
            if is_directory:
                pending.append(candidate)
                continue
            size = metadata.st_size
            if size > MAX_ARTIFACT_FILE_BYTES or total_bytes + size > MAX_ARTIFACT_TOTAL_BYTES:
                raise OSError("artifact size limit exceeded")
            with open(candidate, "rb") as stream:
                payload = stream.read(MAX_ARTIFACT_FILE_BYTES + 1)
            if len(payload) > MAX_ARTIFACT_FILE_BYTES:
                raise OSError("artifact size limit exceeded")
            total_bytes += len(payload)
            if total_bytes > MAX_ARTIFACT_TOTAL_BYTES:
                raise OSError("artifact size limit exceeded")
            if _credential_exposed(payload, credential_policy):
                return "credential-exposure"
            redacted = payload
            for marker in proxy_markers:
                redacted = redacted.replace(marker, b"[REDACTED_PROXY]")
            if redacted != payload:
                with open(candidate, "wb") as stream:
                    stream.write(redacted)
                proxy_exposed = True
    return "proxy-exposure" if proxy_exposed else None


def _remove_attempt_or_fail(attempt_root: Path, remove_directory: DirectoryRemover) -> None:
    try:
        remove_directory(attempt_root)
    except (OSError, SystemExit) as exc:
        try:
            remove_directory(attempt_root)
        except (OSError, SystemExit):
            pass
        raise SystemExit("benchmark attempt artifact cleanup failed") from exc


def finalize_confidential_artifacts(
    attempt_root: Path,
    isolated_home: Path,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
    remove_directory: DirectoryRemover,
    *,
    force_credential_removal: bool = False,
) -> str | None:
    try:
        remove_directory(isolated_home)
        exposure = scrub_confidential_artifact_tree(attempt_root, proxy_policy, credential_policy)
    except (OSError, SystemExit) as exc:
        try:
            remove_directory(attempt_root)
        except (OSError, SystemExit):
            pass
        raise SystemExit("benchmark attempt artifact cleanup failed") from exc
    if exposure == "credential-exposure" or force_credential_removal:
        _remove_attempt_or_fail(attempt_root, remove_directory)
        return "credential-exposure"
    return exposure


def finalize_confidential_stage(
    stage_root: Path,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
    remove_directory: DirectoryRemover,
) -> str | None:
    """Scan a disposable writable stage tree, then remove it on every path."""

    try:
        exposure = scrub_confidential_artifact_tree(stage_root, proxy_policy, credential_policy)
    except (OSError, SystemExit) as exc:
        try:
            remove_directory(stage_root)
        except (OSError, SystemExit):
            pass
        raise SystemExit("benchmark stage confidentiality cleanup failed") from exc
    try:
        remove_directory(stage_root)
    except (OSError, SystemExit) as exc:
        try:
            remove_directory(stage_root)
        except (OSError, SystemExit):
            pass
        raise SystemExit("benchmark stage confidentiality cleanup failed") from exc
    return exposure


def execute_with_confidentiality_boundary(
    attempt_root: Path,
    isolated_home: Path,
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
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
    result_reason = result.get("invalidReason") if result is not None else None
    error_reason = (
        classify_confidential_payload(str(pending_error).encode("utf-8", errors="surrogatepass"), proxy_policy, credential_policy)
        if pending_error is not None
        else None
    )
    exposed = finalize_confidential_artifacts(
        attempt_root,
        isolated_home,
        proxy_policy,
        credential_policy,
        remove_directory,
        force_credential_removal=result_reason == "credential-exposure" or error_reason == "credential-exposure",
    )
    reason = "credential-exposure" if "credential-exposure" in {exposed, result_reason, error_reason} else None
    if reason is None and "proxy-exposure" in {exposed, result_reason, error_reason}:
        reason = "proxy-exposure"
    if reason is not None:
        elapsed = result.get("elapsedSeconds", 0.0) if result is not None else 0.0
        return {"status": "invalid", "invalidReason": reason, "elapsedSeconds": elapsed}
    if pending_error is not None:
        raise pending_error
    if result is None:
        raise SystemExit("benchmark attempt did not produce a result")
    return result


def scrub_stale_confidential_artifacts(
    attempts_root: Path,
    completed_attempt_roots: set[str],
    proxy_policy: ProxyPolicy,
    credential_policy: CredentialPolicy,
    remove_entry: DirectoryRemover,
) -> None:
    if not attempts_root.exists():
        return
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise SystemExit("attempts artifact root must be an ordinary directory")
    unsafe_completed = False
    for attempt_root in sorted(attempts_root.iterdir()):
        if attempt_root.name not in completed_attempt_roots:
            try:
                remove_entry(attempt_root)
            except (OSError, SystemExit):
                unsafe_completed = True
            continue
        if attempt_root.is_symlink() or not attempt_root.is_dir():
            try:
                remove_entry(attempt_root)
            except (OSError, SystemExit):
                pass
            unsafe_completed = True
            continue
        try:
            exposure = finalize_confidential_artifacts(
                attempt_root,
                attempt_root / "isolated/home",
                proxy_policy,
                credential_policy,
                remove_entry,
            )
            unsafe_completed = unsafe_completed or exposure == "credential-exposure"
        except SystemExit:
            unsafe_completed = True
    if unsafe_completed:
        raise SystemExit("stale benchmark attempt artifacts were unsafe")


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
        pass_fds=command_memfd_descriptors(command),
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
