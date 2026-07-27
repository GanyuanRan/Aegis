#!/usr/bin/env python3
"""Filesystem and prompt-input isolation support for the Codex benchmark."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import signal
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ARMS = ("baseline-no-aegis", "aegis-auto")
VIRTUAL_HOME = Path("/home/benchmark")
VIRTUAL_CODEX_HOME = VIRTUAL_HOME / ".codex"
VIRTUAL_WORKSPACE = Path("/workspace")
VIRTUAL_SNAPSHOT = Path("/opt/aegis")
NEUTRAL_CONFIG = "project_doc_max_bytes = 0\n\n[features]\nmulti_agent = false\n"
AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
IGNORED_TREE_PARTS = {".git", ".pytest_cache", "__pycache__"}


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
            continue
        require(candidate.is_file(), f"tree contains unsupported file type: {relative.as_posix()}")
        digest.update(relative.as_posix().encode())
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
) -> list[str]:
    command = [
        str(bwrap),
        "--die-with-parent",
        "--new-session",
        "--unshare-net",
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
    require("--unshare-net" in command, "benchmark command must disable network during prompt audit")
    require("--unshare-pid" in command, "benchmark command must isolate the host process table")
    require(str(output_root.resolve()) not in {target for _, _, target in mounts}, "benchmark output root must not be mounted as a whole")


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
) -> dict[str, Any]:
    require(bwrap.is_file(), f"bwrap is required for benchmark isolation: {bwrap}")
    require(codex.exists(), f"Codex executable is missing: {codex}")
    require(auth_file.is_file(), f"Codex auth file is required: {auth_file}")
    require(not auth_file.is_symlink(), "Codex auth file must not be a symlink")
    require(auth_file.stat().st_mode & 0o022 == 0, "Codex auth file must not be group/world writable")
    reset_directory(output_root, root)

    snapshot_root = output_root / "distribution-snapshot"
    snapshot = prepare_distribution_snapshot(root, snapshot_root)
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
