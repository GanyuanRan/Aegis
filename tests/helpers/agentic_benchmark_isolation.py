#!/usr/bin/env python3
"""Filesystem and prompt-input isolation support for the Codex benchmark."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import signal
import stat
import subprocess
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import urlsplit

from agentic_benchmark_provider_preflight import CommandRunner
from agentic_benchmark_provider_preflight import run_sanitized_provider_preflight


ARMS = ("baseline-no-aegis", "aegis-auto")
VIRTUAL_HOME = Path("/home/benchmark")
VIRTUAL_CODEX_HOME = VIRTUAL_HOME / ".codex"
VIRTUAL_WORKSPACE = Path("/workspace")
VIRTUAL_SNAPSHOT = Path("/opt/aegis")
NEUTRAL_CONFIG = (
    'approval_policy = "never"\n'
    'sandbox_mode = "workspace-write"\n'
    "project_doc_max_bytes = 0\n\n"
    "[features]\n"
    "multi_agent = false\n"
)
AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
IGNORED_TREE_PARTS = {".git", ".pytest_cache", "__pycache__"}
PROXY_KEYS = ("ALL_PROXY", "HTTPS_PROXY", "HTTP_PROXY")
PROXY_SCHEMES = {"http", "https", "socks5", "socks5h"}


class ProxyPolicy:
    """Validated proxy values with a deliberately secret-free representation."""

    __slots__ = ("__mapping", "__sealed")

    def __init__(self, mapping: dict[str, str]) -> None:
        object.__setattr__(self, "_ProxyPolicy__mapping", MappingProxyType(dict(mapping)))
        object.__setattr__(self, "_ProxyPolicy__sealed", True)

    def __setattr__(self, _name: str, _value: object) -> None:
        raise AttributeError("ProxyPolicy is immutable")

    def __repr__(self) -> str:
        return f"ProxyPolicy(mode={'proxy' if self.__mapping else 'direct'}, keys={sorted(self.__mapping)})"

    def _child_environment(self) -> dict[str, str]:
        return dict(self.__mapping)


def _proxy_error(key: str, reason: str) -> None:
    raise SystemExit(f"invalid proxy environment key {key}: {reason}")


def _validate_proxy_url(key: str, value: str) -> str:
    if any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value):
        _proxy_error(key, "whitespace or control characters are forbidden")
    if "?" in value:
        _proxy_error(key, "query components are forbidden")
    if "#" in value:
        _proxy_error(key, "fragment components are forbidden")
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
    mapping = policy._child_environment()
    return {
        "mode": "proxy" if mapping else "direct",
        "keys": sorted(mapping),
        "schemes": sorted({_validate_proxy_url(key, value) for key, value in mapping.items()}),
        "fingerprint": canonical_json_hash(mapping),
    }


def redact_proxy_output(text: str, policy: ProxyPolicy) -> tuple[str, bool]:
    redacted = text
    exposed = False
    values = set(policy._child_environment().values())
    for value in sorted(values, key=len, reverse=True):
        if value in redacted:
            redacted = redacted.replace(value, "[REDACTED_PROXY]")
            exposed = True
    return redacted, exposed


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


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
    resolved = candidate.resolve()
    tmp_root = (root / ".tmp").resolve()
    require(tmp_root in resolved.parents, f"{label} must be a strict child of repo .tmp: {value}")
    return resolved


def reset_directory(path: Path, root: Path) -> None:
    tmp_root = (root / ".tmp").resolve()
    resolved = path.resolve()
    require(tmp_root in resolved.parents, f"refusing to reset directory outside repo .tmp: {path}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


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
) -> dict[str, Path]:
    home = arm_root / "home"
    workspace = arm_root / "workspace"
    home_codex = home / ".codex"
    discovery = home / ".agents/skills"
    home_codex.mkdir(parents=True)
    discovery.mkdir(parents=True)
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
        (discovery / "aegis").symlink_to(VIRTUAL_SNAPSHOT / "skills")
    return {
        "root": arm_root,
        "home": home,
        "workspace": workspace,
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
        "--ro-bind",
        str(layout["auth"]),
        str(VIRTUAL_CODEX_HOME / "auth.json"),
    ]
    if isolate_network:
        command.insert(3, "--unshare-net")
    else:
        for key, value in sorted(proxy_policy._child_environment().items()):  # type: ignore[union-attr]
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
    bwrap: Path,
    codex: Path,
    layout: dict[str, Path],
    prompt: str,
    model: str,
    proxy_policy: ProxyPolicy,
) -> list[str]:
    command = build_bwrap_command(
        bwrap=bwrap,
        codex=codex,
        layout=layout,
        prompt=prompt,
        debug_prompt=False,
        isolate_network=False,
        proxy_policy=proxy_policy,
    )
    separator = command.index("--")
    return [
        *command[: separator + 1],
        str(codex),
        "exec",
        "--json",
        "--color",
        "never",
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--ephemeral",
        "--strict-config",
        "--ignore-rules",
        "--disable",
        "shell_snapshot",
        "--model",
        model,
        "-C",
        str(VIRTUAL_WORKSPACE),
        prompt,
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
    for index, value in enumerate(command):
        if value in {"--bind", "--ro-bind"} and index + 2 < len(command):
            mounts.append((value, command[index + 1], command[index + 2]))
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
    require(auth_mounts == [("--ro-bind", str(layout["auth"]), auth_target)], "benchmark auth must be mounted exactly once and read-only")
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
    allowed_sources = {str(layout["home"]), str(layout["workspace"]), str(layout["auth"])}
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
        require("--unshare-net" not in command, "live Codex client must be able to reach the configured model provider")
    else:
        require(proxy_policy is None, "network-disabled benchmark command must not receive a proxy policy")
        require("--unshare-net" in command, "benchmark command must disable network during prompt audit")
    command_environment: dict[str, str] = {}
    for index, value in enumerate(command):
        if value != "--setenv":
            continue
        require(index + 2 < len(command), "benchmark command contains an incomplete environment entry")
        key = command[index + 1]
        require(key not in command_environment, f"benchmark command repeats environment key {key}")
        command_environment[key] = command[index + 2]
    proxy_environment = {
        key: value for key, value in command_environment.items() if key.lower().endswith("_proxy")
    }
    forbidden_no_proxy = next((key for key in command_environment if key.lower() == "no_proxy"), None)
    require(forbidden_no_proxy is None, f"benchmark command must not forward proxy key {forbidden_no_proxy}")
    unexpected_proxy_keys = sorted(set(proxy_environment) - set(PROXY_KEYS))
    require(not unexpected_proxy_keys, f"benchmark command contains unexpected proxy key {unexpected_proxy_keys[0]}" if unexpected_proxy_keys else "")
    expected_proxy_environment = proxy_policy._child_environment() if proxy_policy is not None else {}
    for key in PROXY_KEYS:
        require(
            (key in proxy_environment) == (key in expected_proxy_environment),
            f"benchmark command proxy key {key} presence does not match validated policy",
        )
        if key in expected_proxy_environment:
            require(proxy_environment[key] == expected_proxy_environment[key], f"benchmark command proxy key {key} value does not match validated policy")
    require(command.count("--clearenv") == 1, "benchmark command must clear the inherited environment exactly once")
    require("--unshare-pid" in command, "benchmark command must isolate the host process table")
    require(str(output_root.resolve()) not in {target for _, _, target in mounts}, "benchmark output root must not be mounted as a whole")


def run_provider_preflight(
    *,
    root: Path,
    output_root: Path,
    auth_file: Path,
    bwrap: Path,
    codex: Path,
    requested_model: str,
    timeout_seconds: float,
    proxy_policy: ProxyPolicy,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    require(bwrap.is_file(), "bwrap is required for provider preflight")
    require(codex.is_file(), "Codex executable is required for provider preflight")
    require(auth_file.is_file(), "Codex auth file is required for provider preflight")
    require(not auth_file.is_symlink(), "Codex auth file must not be a symlink")
    require(auth_file.stat().st_mode & 0o022 == 0, "Codex auth file must not be group/world writable")
    reset_directory(output_root, root)
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
        timeout_seconds,
        command_runner=command_runner,
    )


def run_command(command: list[str], label: str, timeout: int = 60) -> str:
    process = subprocess.Popen(
        command,
        text=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        raise SystemExit(f"{label} timed out") from exc
    require(process.returncode == 0, f"{label} failed with exit {process.returncode}: {stderr[:500]}")
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
    prepared_snapshot: Path | None = None,
) -> dict[str, Any]:
    require(bwrap.is_file(), f"bwrap is required for benchmark isolation: {bwrap}")
    require(codex.exists(), f"Codex executable is missing: {codex}")
    require(auth_file.is_file(), f"Codex auth file is required: {auth_file}")
    require(not auth_file.is_symlink(), "Codex auth file must not be a symlink")
    require(auth_file.stat().st_mode & 0o022 == 0, "Codex auth file must not be group/world writable")
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
    for arm in ARMS:
        command = build_bwrap_command(
            bwrap=bwrap,
            codex=codex,
            layout=layouts[arm],
            prompt=prompt,
            debug_prompt=True,
        )
        validate_bwrap_command(command, root=root, output_root=output_root, layout=layouts[arm])
        raw = run_command(command, f"{arm} Codex prompt-input audit")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{arm} Codex prompt-input was not valid JSON") from exc
        summaries[arm] = prompt_input_summary(data, prompt, snapshot["skillIds"])

        audit_command = mount_audit_command(bwrap=bwrap, codex=codex, layout=layouts[arm])
        validate_bwrap_command(audit_command, root=root, output_root=output_root, layout=layouts[arm])
        mount_audits[arm] = json.loads(run_command(audit_command, f"{arm} mount audit"))

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

    return {
        "version": 1,
        "reportType": "agentic-benchmark-isolation-audit",
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "caseId": case["id"],
        "modelCalls": 0,
        "distributionSnapshot": snapshot,
        "sharedInputs": pair,
        "arms": {
            arm: {
                **summaries[arm],
                "authReadOnly": mount_audits[arm]["authReadOnly"],
                "benchmarkRepoVisible": mount_audits[arm]["repoVisible"],
                "peerWorkspaceVisible": mount_audits[arm]["peerWorkspaceVisible"],
                "scorerVisible": mount_audits[arm]["scorerVisible"],
                "visibleProcessCount": mount_audits[arm]["visibleProcessCount"],
                "snapshotVisible": mount_audits[arm]["snapshotVisible"],
            }
            for arm in ARMS
        },
    }
