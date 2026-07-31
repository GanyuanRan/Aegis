#!/usr/bin/env python3
"""Filesystem and prompt-input isolation support for the Codex benchmark."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any

from agentic_benchmark_process_supervisor import communicate_with_timeout
from agentic_benchmark_provider_preflight import CommandRunner
from agentic_benchmark_provider_preflight import popen_with_independent_memfd_offsets
from agentic_benchmark_provider_preflight import PROXY_KEYS
from agentic_benchmark_provider_preflight import ProxyPolicy
from agentic_benchmark_provider_preflight import network_policy_metadata
from agentic_benchmark_provider_preflight import popen_with_independent_auth_link
from agentic_benchmark_provider_preflight import redact_proxy_output
from agentic_benchmark_provider_preflight import resolve_proxy_policy
from agentic_benchmark_provider_preflight import run_sanitized_provider_preflight
from agentic_benchmark_provider_preflight import validate_auth_mount_file


ARMS = ("baseline-no-aegis", "aegis-auto")
VIRTUAL_HOME = Path("/home/benchmark")
VIRTUAL_CODEX_HOME = VIRTUAL_HOME / ".codex"
VIRTUAL_WORKSPACE = Path("/workspace")
VIRTUAL_SNAPSHOT = Path("/opt/aegis")
PERMISSION_PROFILE_NAME = "aegis-benchmark-workspace"
NEUTRAL_CONFIG = (
    'approval_policy = "never"\n'
    f'default_permissions = "{PERMISSION_PROFILE_NAME}"\n'
    "project_doc_max_bytes = 0\n\n"
    "[shell_environment_policy]\n"
    'inherit = "all"\n'
    "ignore_default_excludes = false\n"
    'include_only = ["PATH", "HOME", "TMPDIR", "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL"]\n\n'
    f"[permissions.{PERMISSION_PROFILE_NAME}.filesystem]\n"
    '":minimal" = "read"\n'
    '":tmpdir" = "write"\n\n'
    '"~/.agents/skills" = "read"\n\n'
    f'[permissions.{PERMISSION_PROFILE_NAME}.filesystem.":workspace_roots"]\n'
    '"." = "write"\n\n'
    f"[permissions.{PERMISSION_PROFILE_NAME}.network]\n"
    "enabled = false\n\n"
    "[features]\n"
    "multi_agent = false\n"
)
AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
IGNORED_TREE_PARTS = {".git", ".pytest_cache", "__pycache__"}
BWRAP_BASE_ENVIRONMENT = {
    "HOME": str(VIRTUAL_HOME),
    "CODEX_HOME": str(VIRTUAL_CODEX_HOME),
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "TMPDIR": "/tmp",
}
DIRECT_CODEX_PATH = "/usr/local/bin:/usr/bin:/bin"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def resolve_permission_backend_bwrap() -> Path:
    value = shutil.which("bwrap", path=DIRECT_CODEX_PATH)
    require(value is not None, "permission-profile backend bwrap is unavailable")
    resolved = Path(value).resolve()
    require(resolved.is_file(), "permission-profile backend bwrap is unavailable")
    return resolved


def resolve_codex_direct_executable(codex: Path) -> Path:
    resolved = codex.resolve()
    direct = resolved
    if resolved.name == "codex.js" and resolved.parent.name == "bin":
        target = {
            "x86_64": "x86_64-unknown-linux-musl",
            "aarch64": "aarch64-unknown-linux-musl",
        }.get(os.uname().machine)
        require(target is not None, "Codex native runtime platform is unsupported")
        package_root = resolved.parent.parent
        candidates = [
            *package_root.glob(f"node_modules/@openai/codex-*/vendor/{target}/bin/codex"),
            package_root / f"vendor/{target}/bin/codex",
        ]
        native_runtimes = sorted({path.resolve() for path in candidates if path.is_file()})
        require(len(native_runtimes) == 1, "Codex native runtime executable is ambiguous or unavailable")
        direct = native_runtimes[0]
    try:
        with direct.open("rb") as executable:
            elf_header = executable.read(4)
    except OSError as exc:
        raise SystemExit("Codex native runtime executable is unavailable") from exc
    require(elf_header == b"\x7fELF" and os.access(direct, os.X_OK), "direct Codex executable must be a native ELF runtime")
    return direct


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_hash(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def hash_tree(path: Path, *, reject_symlinks: bool = True) -> str:
    require(path.is_dir(), f"tree root must be an existing directory: {path}")
    digest = hashlib.sha256()
    file_count = 0
    for candidate in sorted(path.rglob("*")):
        relative = candidate.relative_to(path)
        if set(relative.parts) & IGNORED_TREE_PARTS:
            continue
        if candidate.is_symlink():
            require(not reject_symlinks, f"tree must not contain symlinks: {relative.as_posix()}")
            digest.update(f"symlink:{relative.as_posix()}:{os.readlink(candidate)}\n".encode())
            continue
        if candidate.is_dir():
            digest.update(f"dir:{relative.as_posix()}:mode:{stat.S_IMODE(candidate.stat().st_mode):04o}\n".encode())
            continue
        require(candidate.is_file(), f"tree contains unsupported file type: {relative.as_posix()}")
        digest.update(relative.as_posix().encode())
        digest.update(b"\0")
        digest.update(f"mode:{stat.S_IMODE(candidate.stat().st_mode):04o}".encode())
        digest.update(b"\0")
        digest.update(candidate.read_bytes())
        digest.update(b"\0")
        file_count += 1
    require(file_count > 0, f"tree must contain at least one file: {path}")
    return digest.hexdigest()


def resolve_tmp_child(root: Path, value: Path, label: str) -> Path:
    candidate = value if value.is_absolute() else root / value
    require(candidate.name not in {"", ".", ".."}, f"{label} must name a strict child")
    require(not candidate.is_symlink(), f"{label} must not be a symlink")
    tmp_root = (root / ".tmp").resolve()
    parent = candidate.parent.resolve()
    lexical = parent / candidate.name
    require(tmp_root in lexical.parents, f"{label} must be a strict child of repo .tmp: {value}")
    return lexical


def reset_directory(path: Path, root: Path) -> None:
    lexical = resolve_tmp_child(root, path, "reset directory")
    require(not lexical.is_symlink(), "reset directory leaf must not be a symlink")
    if lexical.exists():
        require(lexical.is_dir(), "reset directory leaf must be an ordinary directory")
        remove_tmp_artifact_entry(lexical, root)
    lexical.mkdir(parents=True)


def remove_tmp_artifact_entry(path: Path, root: Path) -> None:
    candidate = path if path.is_absolute() else root / path
    require(candidate.name not in {"", ".", ".."}, "artifact entry must name a strict child")
    tmp_root = (root / ".tmp").resolve()
    parent = candidate.parent.resolve()
    lexical = parent / candidate.name
    require(tmp_root in lexical.parents, "artifact entry must be a strict child of repo .tmp")
    try:
        root_metadata = lexical.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(root_metadata.st_mode):
        lexical.unlink()
        return
    try:
        mountinfo = Path("/proc/self/mountinfo").read_bytes()
        mount_points = []
        for line in mountinfo.splitlines():
            fields = line.split()
            require(len(fields) >= 10 and b"-" in fields[6:], "artifact mount boundary could not be verified")
            require(re.search(rb"\\(?![0-7]{3})", fields[4]) is None, "artifact mount boundary could not be verified")
            mount_point = re.sub(rb"\\([0-7]{3})", lambda item: bytes([int(item.group(1), 8)]), fields[4])
            require(mount_point.startswith(b"/"), "artifact mount boundary could not be verified")
            mount_points.append(mount_point)
    except OSError as exc:
        raise SystemExit("artifact mount boundary could not be verified") from exc
    root_bytes = os.fsencode(lexical)
    prefix = root_bytes + b"/"
    require(
        not any(point == root_bytes or point.startswith(prefix) for point in mount_points),
        "artifact tree must not contain mount points",
    )
    root_device = root_metadata.st_dev
    pending = [root_bytes]
    while pending:
        with os.scandir(pending.pop()) as iterator:
            entries = list(iterator)
        for entry in entries:
            metadata = entry.stat(follow_symlinks=False)
            require(metadata.st_dev == root_device, "artifact tree must stay on one filesystem")
            if stat.S_ISDIR(metadata.st_mode):
                pending.append(entry.path if isinstance(entry.path, bytes) else os.fsencode(entry.path))
    shutil.rmtree(lexical)


def prepare_distribution_snapshot(root: Path, destination: Path) -> dict[str, Any]:
    require(not destination.exists(), f"snapshot destination already exists: {destination}")
    source_skills = root / "skills"
    plugin_manifest = root / ".codex-plugin/plugin.json"
    require(source_skills.is_dir(), "Aegis skills source is missing")
    require(plugin_manifest.is_file(), "Codex plugin manifest is missing")
    hash_tree(source_skills)

    (destination / ".codex-plugin").mkdir(parents=True)
    shutil.copytree(source_skills, destination / "skills")
    shutil.copy2(plugin_manifest, destination / ".codex-plugin/plugin.json")
    return distribution_snapshot_metadata(destination)


def copy_read_only_tree(source: Path, destination: Path) -> None:
    """Copy a profile-read-only projection whose directories remain removable."""

    shutil.copytree(source, destination, symlinks=True)
    entries = [destination, *destination.rglob("*")]
    require(not any(path.is_symlink() for path in entries), "skill projection must not contain symlinks")
    for path in reversed(entries):
        mode = stat.S_IMODE(path.stat().st_mode)
        cleanup_safe_mode = (mode | 0o700) if path.is_dir() else (mode & ~0o222)
        path.chmod(cleanup_safe_mode)


def distribution_snapshot_metadata(destination: Path) -> dict[str, Any]:
    plugin_manifest = destination / ".codex-plugin/plugin.json"
    require(plugin_manifest.is_file(), "Codex plugin manifest is missing from the distribution snapshot")
    plugin = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    skill_ids = sorted(path.parent.name for path in (destination / "skills").glob("*/SKILL.md"))
    require(skill_ids, "Aegis snapshot contains no discoverable skills")
    return {
        "version": plugin.get("version"),
        "treeHash": hash_tree(destination),
        "skillIds": skill_ids,
        "skillCount": len(skill_ids),
    }


def prepare_arm_layout(
    arm_root: Path,
    seed_project: Path,
    auth_file: Path,
    snapshot: Path | None,
    *,
    virtualized_paths: bool = True,
) -> dict[str, Path]:
    home = arm_root / "home"
    workspace = arm_root / "workspace"
    home_codex = home / ".codex"
    discovery = home / ".agents/skills"
    private_tmp = arm_root / "tmp"
    home_codex.mkdir(parents=True)
    discovery.mkdir(parents=True)
    private_tmp.mkdir()
    shutil.copytree(seed_project, workspace)
    require(not any(workspace.rglob("AGENTS.md")), "benchmark seed project must not contain AGENTS.md")
    git_environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
    }
    git_commands = [
        ["git", "-c", "init.defaultBranch=main", "init", "-q"],
        ["git", "-c", "core.hooksPath=/dev/null", "add", "-A"],
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "user.name=Aegis Benchmark",
            "-c",
            "user.email=benchmark.invalid@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--no-verify",
            "-m",
            "seed benchmark workspace",
        ],
    ]
    for command in git_commands:
        completed = subprocess.run(
            command,
            cwd=workspace,
            env=git_environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )
        require(completed.returncode == 0, f"cannot initialize benchmark git workspace: {completed.stderr[:300]}")
    (home_codex / "config.toml").write_text(NEUTRAL_CONFIG, encoding="utf-8")
    (home_codex / "auth.json").touch(mode=0o600)
    if snapshot is not None:
        if virtualized_paths:
            (discovery / "aegis").symlink_to(VIRTUAL_SNAPSHOT / "skills")
        else:
            copy_read_only_tree(snapshot.resolve() / "skills", discovery / "aegis")
    return {
        "root": arm_root,
        "home": home,
        "workspace": workspace,
        "tmp": private_tmp,
        "auth": auth_file,
        "snapshot": snapshot,
    }


def prepare_provider_preflight_layout(preflight_root: Path, auth_file: Path) -> dict[str, Path | None]:
    home = preflight_root / "home"
    workspace = preflight_root / "workspace"
    home_codex = home / ".codex"
    home_codex.mkdir(parents=True)
    workspace.mkdir(parents=True)
    (home_codex / "config.toml").write_text(NEUTRAL_CONFIG, encoding="utf-8")
    (home_codex / "auth.json").touch(mode=0o600)
    return {
        "root": preflight_root,
        "home": home,
        "workspace": workspace,
        "auth": auth_file,
        "snapshot": None,
    }


def materialize_direct_skill_projection(layout: dict[str, Path]) -> None:
    snapshot = layout["snapshot"]
    if snapshot is None:
        return
    projection = layout["home"] / ".agents/skills/aegis"
    require(projection.is_symlink(), "virtual skill projection is unavailable for direct audit")
    projection.unlink()
    copy_read_only_tree(snapshot.resolve() / "skills", projection)


def system_mount_args() -> list[str]:
    arguments: list[str] = []
    for system_path in ("/usr", "/bin", "/lib", "/lib64", "/etc"):
        if Path(system_path).exists():
            arguments.extend(["--ro-bind", system_path, system_path])
    return arguments


def build_bwrap_command(
    *,
    bwrap: Path,
    codex: Path,
    layout: dict[str, Path],
    prompt: str,
    debug_prompt: bool,
    isolate_network: bool = True,
    proxy_policy: ProxyPolicy | None = None,
) -> list[str]:
    require(isolate_network or proxy_policy is not None, "network-enabled benchmark command requires a validated proxy policy")
    auth_source = str(layout["auth"])
    auth_fd = re.fullmatch(r"/proc/self/fd/([0-9]+)", auth_source)
    auth_mount = ["--ro-bind-data", auth_fd.group(1), str(VIRTUAL_CODEX_HOME / "auth.json")] if auth_fd else [
        "--ro-bind", auth_source, str(VIRTUAL_CODEX_HOME / "auth.json")
    ]
    command = [
        str(bwrap),
        "--die-with-parent",
        "--new-session",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--hostname",
        "aegis-benchmark",
        "--clearenv",
        "--setenv",
        "HOME",
        str(VIRTUAL_HOME),
        "--setenv",
        "CODEX_HOME",
        str(VIRTUAL_CODEX_HOME),
        "--setenv",
        "PATH",
        "/usr/local/bin:/usr/bin:/bin",
        "--setenv",
        "TMPDIR",
        "/tmp",
        "--tmpfs",
        "/tmp",
        "--dir",
        "/home",
        "--dir",
        str(VIRTUAL_HOME),
        "--bind",
        str(layout["home"]),
        str(VIRTUAL_HOME),
        "--dir",
        str(VIRTUAL_WORKSPACE),
        "--bind",
        str(layout["workspace"]),
        str(VIRTUAL_WORKSPACE),
        *auth_mount,
    ]
    if isolate_network:
        command.insert(3, "--unshare-net")
    else:
        for key, value in sorted(proxy_policy.child_environment().items()):  # type: ignore[union-attr]
            command.extend(["--setenv", key, value])
    command.extend(system_mount_args())
    command.extend(["--dev", "/dev", "--proc", "/proc"])
    if layout["snapshot"] is not None:
        command.extend(
            [
                "--dir",
                "/opt",
                "--dir",
                str(VIRTUAL_SNAPSHOT),
                "--ro-bind",
                str(layout["snapshot"]),
                str(VIRTUAL_SNAPSHOT),
            ]
        )
    command.extend(["--chdir", str(VIRTUAL_WORKSPACE), "--"])
    if debug_prompt:
        command.extend(
            [
                str(codex),
                "debug",
                "prompt-input",
                "-c",
                "project_doc_max_bytes=0",
                "--disable",
                "shell_snapshot",
                prompt,
            ]
        )
    else:
        command.extend([str(codex), "exec", "--help"])
    return command


def build_codex_live_command(
    *,
    codex: Path,
    layout: dict[str, Path],
    prompt: str,
    model: str,
    reasoning_effort: str,
) -> list[str]:
    return [
        str(resolve_codex_direct_executable(codex)),
        "exec",
        "--json",
        "--color",
        "never",
        "--skip-git-repo-check",
        "--ephemeral",
        "--strict-config",
        "--ignore-rules",
        "--disable",
        "shell_snapshot",
        "-c",
        f'model_reasoning_effort="{reasoning_effort}"',
        "--model",
        model,
        "-C",
        str(layout["workspace"]),
        prompt,
    ]


def direct_codex_environment(layout: dict[str, Path], proxy_policy: ProxyPolicy | None = None) -> dict[str, str]:
    environment = {
        "HOME": str(layout["home"]),
        "CODEX_HOME": str(layout["home"] / ".codex"),
        "PATH": DIRECT_CODEX_PATH,
        "TMPDIR": str(layout["tmp"]),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    if proxy_policy is not None:
        environment.update(proxy_policy.child_environment())
    return environment


def validate_codex_live_command(
    command: list[str],
    *,
    codex: Path,
    layout: dict[str, Path],
    prompt: str,
    model: str,
    reasoning_effort: str,
) -> None:
    require(
        command == build_codex_live_command(
            codex=codex,
            layout=layout,
            prompt=prompt,
            model=model,
            reasoning_effort=reasoning_effort,
        ),
        "direct Codex live command drifted",
    )
    require("--sandbox" not in command, "direct Codex live command must use the frozen permission profile")
    require("use_legacy_landlock" not in command, "direct Codex live command must not use legacy Landlock")
    require("--dangerously-bypass-approvals-and-sandbox" not in command, "direct Codex live command must not bypass sandboxing")


def validate_direct_codex_environment(
    environment: dict[str, str],
    *,
    layout: dict[str, Path],
    proxy_policy: ProxyPolicy | None,
) -> None:
    expected = direct_codex_environment(layout, proxy_policy)
    require(environment == expected, "direct Codex environment drifted")


def tool_sandbox_audit_command(
    *,
    codex: Path,
    layout: dict[str, Path],
    forbidden_files: list[Path],
    skill_file: Path | None,
) -> list[str]:
    require(forbidden_files and all(path.exists() for path in forbidden_files), "tool sandbox audit needs existing forbidden files")
    script = """
import json
import os
import socket
from pathlib import Path

workspace_file = next(path for path in Path('.').iterdir() if path.is_file())
workspace_read = bool(workspace_file.read_bytes())
probe = Path('.aegis-sandbox-probe')
probe.write_text('ready', encoding='utf-8')
workspace_write = probe.read_text(encoding='utf-8') == 'ready'
probe.unlink()
forbidden_read_denied = True
for value in FORBIDDEN:
    try:
        Path(value).read_bytes()
    except OSError:
        continue
    forbidden_read_denied = False
network_denied = False
try:
    socket.socket()
except OSError:
    network_denied = True
proxy_environment_absent = not any(key.casefold() in {'http_proxy', 'https_proxy', 'all_proxy'} for key in os.environ)
skill_projection_ready = not Path.home().joinpath('.agents/skills/aegis').exists()
skill_projection_present = Path.home().joinpath('.agents/skills/aegis').exists()
if SKILL_FILE is not None:
    try:
        skill_projection_ready = b'name:' in Path(SKILL_FILE).read_bytes()
    except OSError:
        skill_projection_ready = False
auth_descriptor_hidden = True
for path in Path('/proc/self/fd').iterdir():
    try:
        target = path.readlink().as_posix()
    except OSError:
        continue
    if 'aegis-benchmark-auth' in target:
        auth_descriptor_hidden = False
print(json.dumps({
    'authDescriptorHidden': auth_descriptor_hidden,
    'forbiddenReadDenied': forbidden_read_denied,
    'networkDenied': network_denied,
    'proxyEnvironmentAbsent': proxy_environment_absent,
    'skillProjectionReady': skill_projection_ready,
    'skillProjectionPresent': skill_projection_present,
    'status': 'ready',
    'visibleProcessCount': len(list(Path('/proc').glob('[0-9]*'))),
    'workspaceRead': workspace_read,
    'workspaceWrite': workspace_write,
}, sort_keys=True))
""".replace("FORBIDDEN", repr([str(path) for path in forbidden_files])).replace(
        "SKILL_FILE", repr(str(skill_file) if skill_file is not None else None)
    ).strip()
    return [
        str(resolve_codex_direct_executable(codex)),
        "sandbox",
        "--permission-profile",
        PERMISSION_PROFILE_NAME,
        "--cd",
        str(layout["workspace"]),
        "--",
        "python3",
        "-c",
        script,
    ]


def build_provider_preflight_command(
    *,
    bwrap: Path,
    codex: Path,
    layout: dict[str, Path | None],
    proxy_policy: ProxyPolicy,
) -> list[str]:
    command = build_bwrap_command(
        bwrap=bwrap,
        codex=codex,
        layout=layout,  # type: ignore[arg-type]
        prompt="unused",
        debug_prompt=False,
        isolate_network=False,
        proxy_policy=proxy_policy,
    )
    separator = command.index("--")
    return [*command[: separator + 1], str(codex), "debug", "models"]


def command_mounts(command: list[str]) -> list[tuple[str, str, str]]:
    mounts: list[tuple[str, str, str]] = []
    prefix = command[: command.index("--")]
    for index, value in enumerate(prefix):
        if value in {"--bind", "--ro-bind", "--ro-bind-data"} and index + 2 < len(prefix):
            mounts.append((value, prefix[index + 1], prefix[index + 2]))
    return mounts


def validate_bwrap_command(
    command: list[str],
    *,
    root: Path,
    output_root: Path,
    layout: dict[str, Path],
    client_network: bool = False,
    proxy_policy: ProxyPolicy | None = None,
) -> None:
    mounts = command_mounts(command)
    auth_target = str(VIRTUAL_CODEX_HOME / "auth.json")
    auth_mounts = [mount for mount in mounts if mount[2] == auth_target]
    auth_match = re.fullmatch(r"/proc/self/fd/([0-9]+)", str(layout["auth"]))
    expected_auth = ("--ro-bind-data", auth_match.group(1), auth_target) if auth_match else ("--ro-bind", str(layout["auth"]), auth_target)
    require(auth_mounts == [expected_auth], "benchmark auth must be mounted exactly once and read-only")
    require(
        [(kind, target) for kind, source, target in mounts if target == str(VIRTUAL_WORKSPACE)]
        == [("--bind", str(VIRTUAL_WORKSPACE))],
        "benchmark workspace must be the only writable case mount",
    )
    require(
        any(source == str(layout["workspace"]) and target == str(VIRTUAL_WORKSPACE) for _, source, target in mounts),
        "benchmark workspace mount source drifted",
    )
    forbidden_targets = {str(root.resolve()), "/benchmark-repo", "/peer-workspace"}
    require(not any(target in forbidden_targets for _, _, target in mounts), "benchmark repo or peer workspace must not be mounted")
    allowed_sources = {str(layout["home"]), str(layout["workspace"]), expected_auth[1]}
    if layout["snapshot"] is not None:
        allowed_sources.add(str(layout["snapshot"]))
    for kind, source, target in mounts:
        if source.startswith("/usr") or source in {"/bin", "/lib", "/lib64", "/etc", "/dev"}:
            continue
        require(source in allowed_sources, f"unexpected benchmark mount source: {source}")
        if kind == "--bind":
            require(target in {str(VIRTUAL_HOME), str(VIRTUAL_WORKSPACE)}, f"unexpected writable benchmark mount: {target}")
    if client_network:
        require(proxy_policy is not None, "network-enabled benchmark command requires a validated proxy policy")
        require("--unshare-net" not in command, "network-enabled benchmark command must use the validated transport policy")
    else:
        require(proxy_policy is None, "network-disabled benchmark command must not receive a proxy policy")
        require("--unshare-net" in command, "network-disabled benchmark command must unshare the network namespace")
    separator = command.index("--")
    prefix = command[:separator]
    command_environment: dict[str, str] = {}
    for index, value in enumerate(prefix):
        if value != "--setenv":
            continue
        require(index + 2 < len(prefix), "benchmark command contains an incomplete environment entry")
        key = prefix[index + 1]
        require(key not in command_environment, f"benchmark command repeats environment key {key}")
        command_environment[key] = prefix[index + 2]
    expected_environment = dict(BWRAP_BASE_ENVIRONMENT)
    if proxy_policy is not None:
        expected_environment.update(proxy_policy.child_environment())
    unexpected_keys = sorted(set(command_environment) - set(expected_environment))
    require(not unexpected_keys, f"benchmark command contains unexpected environment key {unexpected_keys[0]}" if unexpected_keys else "")
    missing_keys = sorted(set(expected_environment) - set(command_environment))
    require(not missing_keys, f"benchmark command environment key {missing_keys[0]} is missing" if missing_keys else "")
    for key in sorted(expected_environment):
        require(command_environment[key] == expected_environment[key], f"benchmark command environment key {key} value drifted")
    require(command.count("--clearenv") == 1, "benchmark command must clear the inherited environment exactly once")
    require("--unshare-pid" in command, "benchmark command must isolate the host process table")
    require(str(output_root.resolve()) not in {target for _, _, target in mounts}, "benchmark output root must not be mounted as a whole")


def run_provider_preflight(
    *,
    root: Path,
    batch_root: Path,
    auth_file: Path,
    bwrap: Path,
    codex: Path,
    requested_model: str,
    requested_reasoning_effort: str,
    timeout_seconds: float,
    proxy_policy: ProxyPolicy,
    command_runner: CommandRunner | None = None,
    process_group_supervised: bool = False,
) -> dict[str, Any]:
    require(bwrap.is_file(), "bwrap is required for provider preflight")
    require(codex.is_file(), "Codex executable is required for provider preflight")
    validate_auth_mount_file(auth_file)
    batch_root = resolve_tmp_child(root, batch_root, "provider preflight batch root")
    require(batch_root.is_dir(), "provider preflight batch root must be an ordinary directory")
    output_root = batch_root / "provider-preflight-isolated"
    reset_directory(output_root, root)
    try:
        layout = prepare_provider_preflight_layout(output_root, auth_file)
        command = build_provider_preflight_command(
            bwrap=bwrap,
            codex=codex,
            layout=layout,
            proxy_policy=proxy_policy,
        )
        validate_bwrap_command(
            command,
            root=root,
            output_root=output_root,
            layout=layout,  # type: ignore[arg-type]
            client_network=True,
            proxy_policy=proxy_policy,
        )
        require(command[command.index("--") + 1 :] == [str(codex), "debug", "models"], "provider preflight command drifted")
        return run_sanitized_provider_preflight(
            command,
            requested_model,
            requested_reasoning_effort,
            timeout_seconds,
            command_runner=command_runner,
            process_group_supervised=process_group_supervised,
        )
    finally:
        try:
            remove_tmp_artifact_entry(output_root, root)
        except (OSError, SystemExit) as exc:
            raise SystemExit("provider preflight isolated root cleanup failed") from exc
        require(not output_root.exists(), "provider preflight isolated root cleanup failed")


def run_command(
    command: list[str],
    label: str,
    timeout: float = 60.0,
    *,
    process_group_supervised: bool = False,
    proxy_policy: ProxyPolicy | None = None,
    environment: dict[str, str] | None = None,
    auth_file: Path | None = None,
    auth_link: Path | None = None,
) -> str:
    spawn = popen_with_independent_memfd_offsets
    spawn_arguments: dict[str, Any] = {}
    if auth_file is not None or auth_link is not None:
        require(auth_file is not None and auth_link is not None, "direct auth spawn requires both source and link")
        spawn = popen_with_independent_auth_link
        spawn_arguments = {"auth_file": auth_file, "auth_link": auth_link}
    process = spawn(
        command,
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=not process_group_supervised,
        env=environment,
        **spawn_arguments,
    )
    stdout, stderr, timed_out, output_exceeded, _artifact_limit_observed = communicate_with_timeout(
        process,
        timeout,
        owns_process_group=not process_group_supervised,
    )
    if timed_out:
        raise SystemExit(f"{label} timed out")
    if output_exceeded:
        raise SystemExit(f"{label} output exceeded the capture limit")
    safe_stderr = redact_proxy_output(stderr, proxy_policy)[0] if proxy_policy is not None else stderr
    require(process.returncode == 0, f"{label} failed with exit {process.returncode}: {safe_stderr[:500]}")
    return stdout


def prompt_text(data: list[dict[str, Any]]) -> str:
    values: list[str] = []
    for item in data:
        for content in item.get("content", []):
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                values.append(content["text"])
    return "\n".join(values)


def without_skill_instructions(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped = copy.deepcopy(data)
    for item in stripped:
        item.pop("id", None)
        content = item.get("content")
        if not isinstance(content, list):
            continue
        item["content"] = [
            block
            for block in content
            if not (
                isinstance(block, dict)
                and isinstance(block.get("text"), str)
                and block["text"].startswith("<skills_instructions>")
            )
        ]
        for block in item["content"]:
            if not isinstance(block, dict) or not isinstance(block.get("text"), str):
                continue
            block["text"] = re.sub(
                r"(?<=<path>)/home/benchmark/\.codex/tmp/arg0/codex-arg0[A-Za-z0-9]+(?=</path>)",
                "/home/benchmark/.codex/tmp/arg0/codex-arg0<VOLATILE>",
                block["text"],
            )
    return stripped


def prompt_input_summary(data: Any, prompt: str, expected_skill_ids: list[str]) -> dict[str, Any]:
    require(isinstance(data, list) and all(isinstance(item, dict) for item in data), "Codex prompt-input must be a JSON list")
    text = prompt_text(data)
    matched_skills = [skill_id for skill_id in expected_skill_ids if f"aegis:{skill_id}" in text]
    roles = Counter(item.get("role", "unknown") for item in data)
    return {
        "inputHash": canonical_json_hash(data),
        "nonSkillInputHash": canonical_json_hash(without_skill_instructions(data)),
        "itemCount": len(data),
        "roleCounts": dict(sorted(roles.items())),
        "textBytes": len(text.encode()),
        "promptOccurrences": text.count(prompt),
        "methodPackMarkerCount": text.count(f"{VIRTUAL_SNAPSHOT}/skills"),
        "evaluatedSkillMatchCount": len(matched_skills),
        "evaluatedSkillMatches": matched_skills,
    }


def mount_audit_command(
    *,
    bwrap: Path,
    codex: Path,
    layout: dict[str, Path],
) -> list[str]:
    command = build_bwrap_command(
        bwrap=bwrap,
        codex=codex,
        layout=layout,
        prompt="unused",
        debug_prompt=False,
    )
    separator = command.index("--")
    audit_script = """
import json
from pathlib import Path

mount_line = None
for line in Path('/proc/self/mountinfo').read_text().splitlines():
    fields = line.split()
    if len(fields) > 5 and fields[4] == '/home/benchmark/.codex/auth.json':
        mount_line = fields
        break
visible_process_count = len(list(Path('/proc').glob('[0-9]*')))
print(json.dumps({
    'authMountFound': mount_line is not None,
    'authReadOnly': bool(mount_line and 'ro' in mount_line[5].split(',')),
    'repoVisible': Path('/benchmark-repo').exists(),
    'peerWorkspaceVisible': Path('/peer-workspace').exists(),
    'scorerVisible': Path('/workspace/tests/helpers/score_agentic_benchmark_outcome.py').exists(),
    'snapshotVisible': Path('/opt/aegis/skills').is_dir(),
    'visibleProcessCount': visible_process_count,
}))
""".strip()
    return [*command[: separator + 1], "python3", "-c", audit_script]


def validate_arm_pair(layouts: dict[str, dict[str, Path]], prompt: str) -> dict[str, str]:
    config_hashes = {
        arm: sha256_bytes((layout["home"] / ".codex/config.toml").read_bytes())
        for arm, layout in layouts.items()
    }
    workspace_hashes = {arm: hash_tree(layout["workspace"]) for arm, layout in layouts.items()}
    require(len(set(config_hashes.values())) == 1, "benchmark arm config drift detected")
    require(len(set(workspace_hashes.values())) == 1, "benchmark arm workspace drift detected")
    return {
        "configHash": next(iter(config_hashes.values())),
        "workspaceHash": next(iter(workspace_hashes.values())),
        "promptHash": sha256_bytes(prompt.encode()),
    }


def run_isolation_audit(
    *,
    root: Path,
    case: dict[str, Any],
    output_root: Path,
    auth_file: Path,
    bwrap: Path,
    codex: Path,
    proxy_policy: ProxyPolicy,
    prepared_snapshot: Path | None = None,
    timeout_seconds: float = 60.0,
    process_group_supervised: bool = False,
) -> dict[str, Any]:
    require(timeout_seconds > 0, "isolation audit timeout must be positive")
    deadline = time.monotonic() + timeout_seconds

    def remaining_timeout() -> float:
        remaining = deadline - time.monotonic()
        require(remaining > 0, "isolation audit exceeded the remaining wall-clock budget")
        return remaining

    require(bwrap.is_file(), f"bwrap is required for benchmark isolation: {bwrap}")
    require(codex.exists(), f"Codex executable is missing: {codex}")
    validate_auth_mount_file(auth_file)
    reset_directory(output_root, root)

    snapshot_root = output_root / "distribution-snapshot"
    if prepared_snapshot is None:
        snapshot = prepare_distribution_snapshot(root, snapshot_root)
    else:
        require(prepared_snapshot.is_dir(), "prepared Aegis snapshot is missing")
        hash_tree(prepared_snapshot)
        shutil.copytree(prepared_snapshot, snapshot_root)
        snapshot = distribution_snapshot_metadata(snapshot_root)
    seed_project = (root / case["seedProjectPath"]).resolve()
    prompt = (root / case["promptPath"]).read_text(encoding="utf-8")
    layouts = {
        "baseline-no-aegis": prepare_arm_layout(output_root / "baseline-no-aegis", seed_project, auth_file, None),
        "aegis-auto": prepare_arm_layout(output_root / "aegis-auto", seed_project, auth_file, snapshot_root),
    }
    pair = validate_arm_pair(layouts, prompt)

    summaries: dict[str, Any] = {}
    mount_audits: dict[str, Any] = {}
    tool_sandbox_audits: dict[str, Any] = {}
    for arm in ARMS:
        command = build_bwrap_command(
            bwrap=bwrap,
            codex=codex,
            layout=layouts[arm],
            prompt=prompt,
            debug_prompt=True,
            isolate_network=False,
            proxy_policy=proxy_policy,
        )
        validate_bwrap_command(
            command,
            root=root,
            output_root=output_root,
            layout=layouts[arm],
            client_network=True,
            proxy_policy=proxy_policy,
        )
        require(
            command[command.index("--") + 1 : command.index("--") + 4]
            == [str(codex), "debug", "prompt-input"],
            "network-enabled isolation audit must remain the fixed Codex prompt-input command",
        )
        raw = run_command(
            command,
            f"{arm} Codex prompt-input audit",
            remaining_timeout(),
            process_group_supervised=process_group_supervised,
            proxy_policy=proxy_policy,
        )
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{arm} Codex prompt-input was not valid JSON") from exc
        summaries[arm] = prompt_input_summary(data, prompt, snapshot["skillIds"])

        audit_command = mount_audit_command(bwrap=bwrap, codex=codex, layout=layouts[arm])
        validate_bwrap_command(audit_command, root=root, output_root=output_root, layout=layouts[arm])
        mount_audits[arm] = json.loads(
            run_command(
                audit_command,
                f"{arm} mount audit",
                remaining_timeout(),
                process_group_supervised=process_group_supervised,
            )
        )
        materialize_direct_skill_projection(layouts[arm])
        peer = next(value for key, value in layouts.items() if key != arm)
        peer_file = next(path for path in peer["workspace"].iterdir() if path.is_file())
        forbidden_files = [
            root / "tests/helpers/score_agentic_benchmark_outcome.py",
            layouts[arm]["home"] / ".codex/auth.json",
            peer_file,
        ]
        if layouts[arm]["snapshot"] is not None:
            forbidden_files.append(next((layouts[arm]["snapshot"] / "skills").glob("*/SKILL.md")))
        projected_skill = next((layouts[arm]["home"] / ".agents/skills/aegis").glob("*/SKILL.md"), None)
        sandbox_command = tool_sandbox_audit_command(
            codex=codex,
            layout=layouts[arm],
            forbidden_files=forbidden_files,
            skill_file=projected_skill,
        )
        direct_environment = direct_codex_environment(layouts[arm], proxy_policy)
        validate_direct_codex_environment(direct_environment, layout=layouts[arm], proxy_policy=proxy_policy)
        tool_sandbox_audits[arm] = json.loads(run_command(
            sandbox_command,
            f"{arm} tool sandbox audit",
            remaining_timeout(),
            process_group_supervised=process_group_supervised,
            environment=direct_environment,
            auth_file=auth_file,
            auth_link=layouts[arm]["home"] / ".codex/auth.json",
        ))
        tool_sandbox_audits[arm]["backend"] = "permission-profile-bwrap"

    baseline = summaries["baseline-no-aegis"]
    aegis = summaries["aegis-auto"]
    require(baseline["evaluatedSkillMatchCount"] == 0, "baseline prompt input contains evaluated Aegis skills")
    require(baseline["methodPackMarkerCount"] == 0, "baseline prompt input contains an Aegis method-pack path marker")
    require(
        aegis["evaluatedSkillMatchCount"] == snapshot["skillCount"],
        "Aegis prompt input does not contain every evaluated skill",
    )
    require(aegis["methodPackMarkerCount"] > 0, "Aegis prompt input contains no distribution snapshot marker")
    require(baseline["promptOccurrences"] == 1 and aegis["promptOccurrences"] == 1, "both arms must receive the prompt exactly once")
    require(baseline["nonSkillInputHash"] == aegis["nonSkillInputHash"], "non-skill prompt input drift detected between arms")
    for arm, audit in mount_audits.items():
        require(audit.get("authMountFound") is True and audit.get("authReadOnly") is True, f"{arm} auth mount is not read-only")
        require(audit.get("repoVisible") is False, f"{arm} can see the benchmark repository")
        require(audit.get("peerWorkspaceVisible") is False, f"{arm} can see a peer workspace")
        require(audit.get("scorerVisible") is False, f"{arm} can see the outcome scorer")
        require(audit.get("visibleProcessCount", 999) <= 3, f"{arm} can see the host process table")
        require(audit.get("snapshotVisible") is (arm == "aegis-auto"), f"{arm} snapshot visibility drifted")
    for arm, audit in tool_sandbox_audits.items():
        require(audit.get("status") == "ready", f"{arm} tool sandbox did not start")
        require(audit.get("workspaceRead") is True and audit.get("workspaceWrite") is True, f"{arm} tool sandbox cannot use its workspace")
        require(audit.get("forbiddenReadDenied") is True, f"{arm} tool sandbox can read benchmark-private files")
        require(audit.get("networkDenied") is True, f"{arm} tool sandbox network is not denied")
        require(audit.get("proxyEnvironmentAbsent") is True, f"{arm} tool sandbox inherited provider proxy state")
        require(audit.get("skillProjectionReady") is True, f"{arm} skill projection visibility drifted")
        require(audit.get("skillProjectionPresent") is (arm == "aegis-auto"), f"{arm} skill projection presence drifted")
        require(audit.get("authDescriptorHidden") is True, f"{arm} tool sandbox inherited the sealed auth descriptor")
        require(audit.get("visibleProcessCount", 999) <= 3, f"{arm} tool sandbox can see the host process table")

    return {
        "version": 1,
        "reportType": "agentic-benchmark-isolation-audit",
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "caseId": case["id"],
        "modelCalls": 0,
        "auditNetworkPolicy": {
            "promptInput": network_policy_metadata(proxy_policy),
            "mountAudit": {"mode": "network-disabled"},
        },
        "distributionSnapshot": snapshot,
        "sharedInputs": pair,
        "arms": {
            arm: {
                **summaries[arm],
                "authReadOnly": mount_audits[arm]["authReadOnly"],
                "benchmarkRepoVisible": mount_audits[arm]["repoVisible"],
                "peerWorkspaceVisible": mount_audits[arm]["peerWorkspaceVisible"],
                "scorerVisible": mount_audits[arm]["scorerVisible"],
                "visibleProcessCount": tool_sandbox_audits[arm]["visibleProcessCount"],
                "snapshotVisible": mount_audits[arm]["snapshotVisible"],
                "toolSandbox": tool_sandbox_audits[arm],
            }
            for arm in ARMS
        },
    }
