#!/usr/bin/env python3
"""Update registered Aegis Method Pack installations.

The updater is host-scoped by design. A plain update targets the current or
explicit host installation; updating every registered host requires --all.
"""

from __future__ import annotations

import argparse
import json
import locale
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
VALID_SYNC_MODES = {"junction", "symlink", "copy-skills", "plugin-managed", "repo-only"}
VALID_UPDATE_MODES = {"manual", "auto", "disabled"}
VALID_DISCOVERY_SHAPES = {"umbrella-root", "direct-child", "host-managed", "none"}
COPY_DISCOVERY_KEY_SKILLS = ("using-aegis", "update-aegis", "verification-before-completion")
KIMI_HOST_ALIASES = {"kimi", "kimi-code", "kimi-code-cli"}
GROK_HOST_ALIASES = {"grok", "grok-build"}
DEEPSEEK_HARNESS_HOST_ALIASES = {"deepseek-harness", "dsh"}
REGISTER_TIME_SYNC_MODES = {"junction", "symlink", "copy-skills"}
DEEPSEEK_HARNESS_PLUGIN_INSTALL = (
    'dsh plugin --profile <profile> add "git+https://github.com/GanyuanRan/Aegis.git"'
)


class UpdateError(Exception):
    pass


def method_pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_config_path() -> Path:
    return Path.home() / ".config" / "aegis" / "config.toml"


def default_registry_path() -> Path:
    return Path.home() / ".config" / "aegis" / "installations.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_local_config(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}

    config: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            try:
                config[key] = json.loads(value)
            except json.JSONDecodeError:
                config[key] = value.strip('"')
        else:
            config[key] = value
    return config


def configured_method_pack_root(config_path: Path | None = None) -> Path | None:
    configured_env = os.environ.get("AEGIS_METHOD_PACK_ROOT")
    if configured_env:
        candidate = Path(configured_env).expanduser().resolve()
        if candidate.is_dir():
            return candidate

    config = read_local_config(config_path or default_config_path())
    configured = config.get("method_pack_root")
    if not configured:
        return None

    candidate = Path(configured).expanduser().resolve()
    if candidate.is_dir():
        return candidate
    return None


def default_method_pack_root() -> Path:
    configured = configured_method_pack_root()
    if configured:
        return configured
    return method_pack_root()


def load_registry(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schemaVersion": SCHEMA_VERSION, "installations": []}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UpdateError(f"Invalid Aegis installation registry JSON: {path}: {exc}") from exc

    if data.get("schemaVersion") != SCHEMA_VERSION:
        raise UpdateError(
            f"Unsupported Aegis installation registry schemaVersion: "
            f"{data.get('schemaVersion')!r}"
        )
    installations = data.get("installations")
    if not isinstance(installations, list):
        raise UpdateError("Aegis installation registry must contain an installations list")
    return data


def save_registry(path: Path, data: dict[str, Any]) -> None:
    data["schemaVersion"] = SCHEMA_VERSION
    data["updatedAt"] = utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def default_reload_hint(host: str) -> str:
    return f"restart or reload {host}"


def default_discovery_shape(sync_mode: str) -> str:
    if sync_mode == "copy-skills":
        return "direct-child"
    if sync_mode in {"plugin-managed", "repo-only"}:
        return "host-managed"
    return "umbrella-root"


def is_kimi_host(host: str | None) -> bool:
    return (host or "").strip().lower() in KIMI_HOST_ALIASES


def is_grok_host(host: str | None) -> bool:
    return (host or "").strip().lower() in GROK_HOST_ALIASES


def is_deepseek_harness_host(host: str | None) -> bool:
    return (host or "").strip().lower() in DEEPSEEK_HARNESS_HOST_ALIASES


def default_kimi_discovery_root() -> Path:
    kimi_home = os.environ.get("KIMI_CODE_HOME")
    if kimi_home:
        return Path(kimi_home).expanduser() / "skills"
    return Path.home() / ".kimi-code" / "skills"


def default_grok_discovery_root() -> Path:
    grok_home = os.environ.get("GROK_HOME")
    if grok_home:
        return Path(grok_home).expanduser() / "skills"
    return Path.home() / ".grok" / "skills"


def default_deepseek_harness_discovery_root() -> Path:
    dsh_home = os.environ.get("DSH_HOME")
    if dsh_home:
        return Path(dsh_home).expanduser() / "skills"
    return Path.home() / ".dsh" / "skills"


def default_discovery_root_for_host(host: str | None) -> Path | None:
    if is_kimi_host(host):
        return default_kimi_discovery_root()
    if is_grok_host(host):
        return default_grok_discovery_root()
    if is_deepseek_harness_host(host):
        return default_deepseek_harness_discovery_root()
    return None


def default_discovery_shape_for_host(host: str | None, sync_mode: str) -> str:
    normalized_host = host.strip().lower() if host else ""
    if (
        normalized_host == "zcode"
        or is_kimi_host(normalized_host)
        or is_grok_host(normalized_host)
        or is_deepseek_harness_host(normalized_host)
    ):
        return "direct-child"
    return default_discovery_shape(sync_mode)


def normalized_discovery_shape(
    value: str | None,
    sync_mode: str,
    host: str | None = None,
) -> str:
    shape = value or default_discovery_shape_for_host(host, sync_mode)
    if shape not in VALID_DISCOVERY_SHAPES:
        raise UpdateError(
            f"discovery_shape must be one of: {', '.join(sorted(VALID_DISCOVERY_SHAPES))}"
        )
    return shape


def normalize_discovery_name_prefix(value: str | None) -> str:
    if value is None:
        return ""
    if "\0" in value or "/" in value or "\\" in value:
        raise UpdateError("discovery_name_prefix must not contain path separators")
    if value in {".", ".."}:
        raise UpdateError("discovery_name_prefix must not be a relative path segment")
    return value


def discovery_skill_dir_name(skill_name: str, prefix: str) -> str:
    return f"{prefix}{skill_name}"


def entry_discovery_name_prefix(entry: dict[str, Any], shape: str | None = None) -> str:
    sync_mode = entry.get("syncMode", "repo-only")
    discovery_shape = shape or normalized_discovery_shape(
        entry.get("discoveryShape"),
        sync_mode,
        entry.get("host"),
    )
    prefix = normalize_discovery_name_prefix(entry.get("discoveryNamePrefix"))
    if prefix and discovery_shape != "direct-child":
        raise UpdateError("discoveryNamePrefix requires direct-child discoveryShape")
    return prefix


def entry_discovery_root(entry: dict[str, Any]) -> str | None:
    discovery_root = entry.get("discoveryRoot")
    if discovery_root:
        return discovery_root
    default_root = default_discovery_root_for_host(entry.get("host"))
    if default_root:
        return default_root.expanduser().resolve().as_posix()
    return None


def should_sync_and_verify_at_register(entry: dict[str, Any]) -> bool:
    sync_mode = entry.get("syncMode", "repo-only")
    shape = normalized_discovery_shape(
        entry.get("discoveryShape"),
        sync_mode,
        entry.get("host"),
    )
    return shape == "direct-child" and sync_mode in REGISTER_TIME_SYNC_MODES


def register_installation(
    registry_path: Path,
    *,
    host: str,
    method_pack_root: Path,
    discovery_root: Path | None = None,
    sync_mode: str = "repo-only",
    discovery_shape: str | None = None,
    discovery_name_prefix: str | None = None,
    tracked_ref: str = "main",
    update_mode: str = "manual",
    reload_hint: str | None = None,
    install_id: str | None = None,
    workspace_helper: Path | None = None,
) -> dict[str, Any]:
    if sync_mode not in VALID_SYNC_MODES:
        raise UpdateError(f"sync_mode must be one of: {', '.join(sorted(VALID_SYNC_MODES))}")
    if update_mode not in VALID_UPDATE_MODES:
        raise UpdateError(f"update_mode must be one of: {', '.join(sorted(VALID_UPDATE_MODES))}")

    normalized_host = host.strip().lower()
    if not normalized_host:
        raise UpdateError("host is required")
    shape = normalized_discovery_shape(discovery_shape, sync_mode, normalized_host)
    name_prefix = normalize_discovery_name_prefix(discovery_name_prefix)
    if name_prefix and shape != "direct-child":
        raise UpdateError("discovery_name_prefix requires direct-child discovery_shape")
    effective_discovery_root = discovery_root or default_discovery_root_for_host(
        normalized_host
    )

    root = Path(method_pack_root).expanduser().resolve()
    helper = (
        Path(workspace_helper).expanduser().resolve()
        if workspace_helper
        else root / "scripts" / "aegis-workspace.py"
    )
    item_id = install_id or f"{normalized_host}:default"
    entry: dict[str, Any] = {
        "id": item_id,
        "host": normalized_host,
        "methodPackRoot": root.as_posix(),
        "workspaceHelper": helper.as_posix(),
        "syncMode": sync_mode,
        "discoveryShape": shape,
        "trackedRef": tracked_ref,
        "updateMode": update_mode,
        "reloadHint": reload_hint or default_reload_hint(normalized_host),
        "lastRegisteredAt": utc_now(),
    }
    if effective_discovery_root:
        entry["discoveryRoot"] = (
            Path(effective_discovery_root).expanduser().resolve().as_posix()
        )
    if name_prefix:
        entry["discoveryNamePrefix"] = name_prefix

    data = load_registry(registry_path)
    installations = data["installations"]
    for index, existing in enumerate(installations):
        if existing.get("id") == item_id:
            installations[index] = entry
            break
    else:
        installations.append(entry)

    save_registry(registry_path, data)
    return entry


def select_installations(
    registry: dict[str, Any],
    *,
    host: str | None,
    all_hosts: bool,
) -> list[dict[str, Any]]:
    installations = registry.get("installations", [])
    if not installations:
        raise UpdateError("No Aegis installations are registered. Run register first.")

    if all_hosts:
        return installations

    normalized_host = host.strip().lower() if host else None
    if normalized_host:
        matches = [
            item
            for item in installations
            if item.get("host") == normalized_host or item.get("id") == normalized_host
        ]
        if not matches:
            candidates = ", ".join(item.get("id", "<unknown>") for item in installations)
            raise UpdateError(f"No registered Aegis installation matches {host!r}. Candidates: {candidates}")
        return matches

    if len(installations) == 1:
        return [installations[0]]

    candidates = ", ".join(item.get("id", "<unknown>") for item in installations)
    raise UpdateError(
        "Multiple Aegis installations are registered. Pass --host <host-or-id> "
        f"for the current host, or --all to update every host. Candidates: {candidates}"
    )


def run_command(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding=locale.getencoding(),
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise UpdateError(f"{' '.join(command)} failed: {detail}")
    return result


def git_output(root: Path, *args: str) -> str:
    return run_command(["git", "-C", root.as_posix(), *args]).stdout.strip()


def ensure_git_checkout(root: Path) -> None:
    if not root.is_dir():
        raise UpdateError(f"Method-pack root does not exist: {root}")
    inside = git_output(root, "rev-parse", "--is-inside-work-tree")
    if inside != "true":
        raise UpdateError(f"Method-pack root is not a git checkout: {root}")


def current_commit(root: Path) -> str:
    return git_output(root, "rev-parse", "HEAD")


def has_dirty_worktree(root: Path) -> bool:
    return bool(git_output(root, "status", "--porcelain"))


def branch_remote_ref(tracked_ref: str) -> tuple[str, str]:
    ref = tracked_ref.strip()
    if not ref:
        raise UpdateError("trackedRef is empty")
    if ref.startswith("-") or ":" in ref:
        raise UpdateError("trackedRef must be a branch-like ref without ':' or leading '-'")
    if ref.startswith("origin/"):
        return ref.removeprefix("origin/"), ref
    return ref, f"origin/{ref}"


def is_junction(path: Path) -> bool:
    checker = getattr(path, "is_junction", None)
    return bool(checker and checker())


def link_points_to(path: Path, target: Path) -> bool:
    try:
        return path.resolve(strict=False) == target.resolve(strict=True)
    except OSError:
        return False


def is_aegis_owned_skill_link(path: Path, source_skills: Path) -> bool:
    if not (path.is_symlink() or is_junction(path)):
        return False
    try:
        link_target = path.resolve(strict=False)
        source_root = source_skills.resolve(strict=True)
    except OSError:
        return False
    return link_target == source_root or source_root in link_target.parents


def remove_link_like_directory(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    elif is_junction(path):
        path.rmdir()
    else:
        raise UpdateError(f"Refusing to remove non-link skill directory: {path}")


def create_direct_child_link(source: Path, destination: Path) -> bool:
    if destination.exists() or destination.is_symlink():
        if link_points_to(destination, source):
            return False
        raise UpdateError(
            "direct-child sync will not overwrite an existing skill directory: "
            f"{destination}"
        )

    try:
        if os.name == "nt":
            run_command(["cmd", "/c", "mklink", "/J", str(destination), str(source)])
        else:
            os.symlink(source, destination, target_is_directory=True)
    except FileExistsError:
        if link_points_to(destination, source):
            return False
        raise
    except OSError as exc:
        raise UpdateError(f"failed to create direct-child skill link {destination}: {exc}") from exc
    return True


def ensure_direct_child_links(entry: dict[str, Any]) -> str:
    sync_mode = entry.get("syncMode", "repo-only")
    shape = normalized_discovery_shape(entry.get("discoveryShape"), sync_mode, entry.get("host"))
    name_prefix = entry_discovery_name_prefix(entry, shape)
    if shape != "direct-child" or sync_mode not in {"junction", "symlink"}:
        return f"{sync_mode}: no direct-child link step required"

    discovery_root = entry_discovery_root(entry)
    if not discovery_root:
        raise UpdateError("direct-child junction/symlink sync requires discoveryRoot")

    source_skills = Path(entry["methodPackRoot"]) / "skills"
    target_root = Path(discovery_root)
    if not source_skills.is_dir():
        raise UpdateError(f"Source skills directory is missing: {source_skills}")
    target_root.mkdir(parents=True, exist_ok=True)

    expected_skills = {
        discovery_skill_dir_name(child.name, name_prefix): child
        for child in source_skills.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }

    pruned = 0
    for child in target_root.iterdir():
        if child.name not in expected_skills and is_aegis_owned_skill_link(child, source_skills):
            remove_link_like_directory(child)
            pruned += 1

    created = 0
    current = 0
    for target_name, source in sorted(expected_skills.items()):
        destination = target_root / target_name
        if create_direct_child_link(source, destination):
            created += 1
        else:
            current += 1

    missing = [
        target_name
        for target_name in sorted(expected_skills)
        if not (target_root / target_name / "SKILL.md").is_file()
        or not link_points_to(target_root / target_name, expected_skills[target_name])
    ]
    if missing:
        raise UpdateError(
            "direct-child discovery root is missing current skill links: "
            + ", ".join(missing)
        )

    return (
        f"{sync_mode}: direct-child links current in {target_root.as_posix()} "
        f"({created} created, {current} already current, {pruned} stale pruned)"
    )


def sync_skills(entry: dict[str, Any]) -> str:
    sync_mode = entry.get("syncMode", "repo-only")
    shape = normalized_discovery_shape(
        entry.get("discoveryShape"),
        sync_mode,
        entry.get("host"),
    )
    name_prefix = entry_discovery_name_prefix(entry, shape)
    if sync_mode in {"junction", "symlink"} and shape == "direct-child":
        return ensure_direct_child_links(entry)
    if sync_mode in {"junction", "symlink", "repo-only"}:
        return f"{sync_mode}: no copy step required"
    if sync_mode == "plugin-managed":
        return "plugin-managed: host adapter refresh remains owned by the host plugin manager"
    if sync_mode != "copy-skills":
        raise UpdateError(f"Unsupported syncMode: {sync_mode}")

    discovery_root = entry_discovery_root(entry)
    if not discovery_root:
        raise UpdateError("copy-skills sync requires discoveryRoot")

    source = Path(entry["methodPackRoot"]) / "skills"
    target = Path(discovery_root)
    if not source.is_dir():
        raise UpdateError(f"Source skills directory is missing: {source}")
    target.mkdir(parents=True, exist_ok=True)
    expected_skill_names = {
        discovery_skill_dir_name(child.name, name_prefix)
        for child in source.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }
    for child in target.iterdir():
        should_prune = child.name not in expected_skill_names
        if name_prefix and not child.name.startswith(name_prefix):
            should_prune = False
        if child.is_dir() and should_prune and (child / "SKILL.md").is_file():
            shutil.rmtree(child)
    for child in source.iterdir():
        if child.is_dir() and (child / "SKILL.md").is_file():
            destination = target / discovery_skill_dir_name(child.name, name_prefix)
        else:
            destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        elif child.is_file():
            shutil.copy2(child, destination)
    verify_copy_discovery_root(entry)
    return f"copied skills into {target.as_posix()}"


def doctor_discovery_root(entry: dict[str, Any]) -> str | None:
    discovery_root = entry_discovery_root(entry)
    if not discovery_root:
        return None
    shape = normalized_discovery_shape(
        entry.get("discoveryShape"),
        entry.get("syncMode", "repo-only"),
        entry.get("host"),
    )
    if shape in {"umbrella-root", "direct-child"}:
        return discovery_root
    return None


def doctor_discovery_name_prefix(entry: dict[str, Any]) -> str | None:
    sync_mode = entry.get("syncMode", "repo-only")
    shape = normalized_discovery_shape(
        entry.get("discoveryShape"),
        sync_mode,
        entry.get("host"),
    )
    if shape != "direct-child":
        return None
    prefix = entry_discovery_name_prefix(entry, shape)
    return prefix or None


def verify_copy_discovery_root(entry: dict[str, Any]) -> None:
    if entry.get("syncMode") != "copy-skills":
        return
    discovery_root = entry_discovery_root(entry)
    if not discovery_root:
        raise UpdateError("copy-skills sync requires discoveryRoot")
    root = Path(discovery_root)
    prefix = entry_discovery_name_prefix(entry)
    for skill in COPY_DISCOVERY_KEY_SKILLS:
        skill_md = root / discovery_skill_dir_name(skill, prefix) / "SKILL.md"
        if not skill_md.is_file():
            raise UpdateError(f"copied discovery root is missing {skill}/SKILL.md: {root}")


def run_doctor(entry: dict[str, Any], *, config_path: Path | None) -> dict[str, Any]:
    root = Path(entry["methodPackRoot"])
    doctor = root / "scripts" / "aegis-doctor.py"
    if not doctor.is_file():
        raise UpdateError(f"aegis-doctor.py not found under method-pack root: {doctor}")

    command = [sys.executable, doctor.as_posix(), "--write-config", "--json"]
    if config_path:
        command.extend(["--config", config_path.as_posix()])
    discovery_root = doctor_discovery_root(entry)
    if discovery_root:
        command.extend(["--discovery-root", discovery_root])
        discovery_name_prefix = doctor_discovery_name_prefix(entry)
        if discovery_name_prefix:
            command.extend(["--discovery-name-prefix", discovery_name_prefix])

    result = run_command(command)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise UpdateError(f"aegis-doctor.py did not emit JSON: {exc}") from exc

    if data.get("ok") is not True:
        raise UpdateError("aegis-doctor.py did not report ok: true")
    if data.get("workspaceSupport") != "available":
        raise UpdateError("aegis-doctor.py did not report workspaceSupport: available")
    if data.get("configStatus") != "configured":
        raise UpdateError("aegis-doctor.py did not report configStatus: configured")
    return data


def update_method_pack_checkout(
    entry: dict[str, Any],
    *,
    dry_run: bool = False,
    stash: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    if entry.get("updateMode") == "disabled" and not force:
        return {
            "status": "skipped",
            "reason": "updateMode is disabled",
        }

    root = Path(entry["methodPackRoot"])
    tracked_ref, remote_ref = branch_remote_ref(entry.get("trackedRef", "main"))
    if dry_run:
        return {
            "status": "dry-run",
            "methodPackRoot": root.as_posix(),
            "wouldFetch": f"origin {tracked_ref}",
            "wouldMerge": remote_ref,
        }

    try:
        ensure_git_checkout(root)
    except UpdateError:
        if entry.get("syncMode") == "plugin-managed":
            return {
                "status": "skipped",
                "reason": "host plugin manager owns this update path and the registered method-pack root is not a direct git checkout",
                "methodPackRoot": root.as_posix(),
            }
        raise

    before = current_commit(root)
    if has_dirty_worktree(root):
        if not stash:
            raise UpdateError(
                f"Method-pack checkout has local changes: {root}. "
                "Commit, stash, or rerun with --stash."
            )
        run_command(
            [
                "git",
                "-C",
                root.as_posix(),
                "stash",
                "push",
                "-u",
                "-m",
                f"aegis-update {utc_now()}",
            ]
        )

    run_command(
        [
            "git",
            "-C",
            root.as_posix(),
            "fetch",
            "origin",
            f"{tracked_ref}:refs/remotes/origin/{tracked_ref}",
        ]
    )
    run_command(["git", "-C", root.as_posix(), "merge", "--ff-only", remote_ref])
    after = current_commit(root)

    return {
        "status": "updated" if before != after else "already-current",
        "beforeCommit": before,
        "afterCommit": after,
        "methodPackRoot": root.as_posix(),
    }


def finalize_host_update(
    entry: dict[str, Any],
    *,
    root_result: dict[str, Any],
    config_path: Path | None,
    dry_run: bool,
    verify: bool,
    shared_root_reused: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": entry.get("id"),
        "host": entry.get("host"),
        "status": root_result.get("status", "updated"),
        "methodPackRoot": entry.get("methodPackRoot"),
        "reloadHint": entry.get("reloadHint"),
        "sharedMethodPackRootReused": shared_root_reused,
    }

    if root_result.get("reason"):
        result["reason"] = root_result["reason"]
    if root_result.get("beforeCommit"):
        result["beforeCommit"] = root_result["beforeCommit"]
    if root_result.get("afterCommit"):
        result["afterCommit"] = root_result["afterCommit"]
    if root_result.get("wouldFetch"):
        result["wouldFetch"] = root_result["wouldFetch"]
    if root_result.get("wouldMerge"):
        result["wouldMerge"] = root_result["wouldMerge"]
    if dry_run:
        result["wouldVerify"] = verify
        return result

    if root_result.get("status") == "skipped":
        return result

    sync_result = sync_skills(entry)
    doctor_result = run_doctor(entry, config_path=config_path) if verify else None
    result["sync"] = sync_result
    result["verified"] = doctor_result is not None
    if entry.get("syncMode") == "plugin-managed":
        result["adapterManagedByHost"] = True
    return result


def update_installation(
    entry: dict[str, Any],
    *,
    config_path: Path | None = None,
    dry_run: bool = False,
    stash: bool = False,
    force: bool = False,
    verify: bool = True,
) -> dict[str, Any]:
    root_result = update_method_pack_checkout(
        entry,
        dry_run=dry_run,
        stash=stash,
        force=force,
    )
    return finalize_host_update(
        entry,
        root_result=root_result,
        config_path=config_path,
        dry_run=dry_run,
        verify=verify,
    )


def update_registered_installations(
    registry_path: Path,
    selected: list[dict[str, Any]],
    *,
    config_path: Path | None,
    dry_run: bool,
    stash: bool,
    force: bool,
    verify: bool,
) -> list[dict[str, Any]]:
    data = load_registry(registry_path)
    results = []
    by_id = {item.get("id"): item for item in data["installations"]}
    shared_root_updates: dict[str, dict[str, Any]] = {}
    shared_root_refs: dict[str, str] = {}
    for entry in selected:
        root_key = entry.get("methodPackRoot")
        tracked_ref = entry.get("trackedRef", "main")
        reuse_shared_root = (
            not dry_run
            and root_key is not None
            and entry.get("syncMode") != "plugin-managed"
        )
        if reuse_shared_root and root_key in shared_root_updates:
            if shared_root_refs[root_key] != tracked_ref:
                raise UpdateError(
                    "Multiple registered hosts share the same method-pack root but "
                    "declare different trackedRef values. Align the trackedRef before "
                    "running a shared update."
                )
            result = finalize_host_update(
                entry,
                root_result=shared_root_updates[root_key],
                config_path=config_path,
                dry_run=dry_run,
                verify=verify,
                shared_root_reused=True,
            )
        else:
            result = update_installation(
                entry,
                config_path=config_path,
                dry_run=dry_run,
                stash=stash,
                force=force,
                verify=verify,
            )
            if reuse_shared_root and root_key is not None and result.get("status") != "skipped":
                shared_root_updates[root_key] = {
                    "status": result.get("status"),
                    "beforeCommit": result.get("beforeCommit"),
                    "afterCommit": result.get("afterCommit"),
                    "methodPackRoot": result.get("methodPackRoot"),
                }
                shared_root_refs[root_key] = tracked_ref
        results.append(result)
        if not dry_run and result.get("afterCommit") and entry.get("id") in by_id:
            by_id[entry["id"]]["lastVerifiedCommit"] = result["afterCommit"]
            by_id[entry["id"]]["lastVerifiedAt"] = utc_now()
    if not dry_run:
        save_registry(registry_path, data)
    return results


def emit(data: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if isinstance(data, list):
        for item in data:
            status = item.get("status", "registered")
            print(f"{item.get('id')}: {status}")
            if item.get("reason"):
                print(f"  reason: {item['reason']}")
            if item.get("methodPackRoot"):
                print(f"  root: {item['methodPackRoot']}")
            if item.get("afterCommit"):
                print(f"  commit: {item['afterCommit']}")
            if item.get("reloadHint"):
                print(f"  reload: {item['reloadHint']}")
        return

    print(json.dumps(data, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update registered Aegis Method Pack installations."
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--registry", default=default_registry_path().as_posix())
    common.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    subparsers = parser.add_subparsers(dest="command")

    register = subparsers.add_parser(
        "register", parents=[common], help="register or update a host installation"
    )
    register.add_argument("--host", required=True)
    register.add_argument("--id", dest="install_id")
    register.add_argument("--method-pack-root", default=default_method_pack_root().as_posix())
    register.add_argument("--discovery-root")
    register.add_argument("--workspace-helper")
    register.add_argument("--sync-mode", choices=sorted(VALID_SYNC_MODES), default="repo-only")
    register.add_argument("--discovery-shape", choices=sorted(VALID_DISCOVERY_SHAPES))
    register.add_argument("--discovery-name-prefix")
    register.add_argument("--tracked-ref", default="main")
    register.add_argument("--update-mode", choices=sorted(VALID_UPDATE_MODES), default="manual")
    register.add_argument("--reload-hint")
    register.add_argument("--config", help="config path passed through to aegis-doctor.py")
    register.add_argument(
        "--compatibility-mode",
        action="store_true",
        help="explicitly allow a compatibility-only host exposure when the native plugin path is unavailable",
    )

    status = subparsers.add_parser("status", parents=[common], help="show registered installations")
    status.add_argument("--host")

    update = subparsers.add_parser("update", parents=[common], help="update one host installation")
    update.add_argument("--host")
    update.add_argument("--all", action="store_true", help="update every registered host")
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--stash", action="store_true", help="stash local changes before updating")
    update.add_argument("--force", action="store_true", help="override updateMode disabled")
    update.add_argument("--no-verify", action="store_true", help="skip aegis-doctor verification")
    update.add_argument("--config", help="config path passed through to aegis-doctor.py")

    return parser


def command_register(args: argparse.Namespace) -> Any:
    normalized_host = args.host.strip().lower()
    compatibility_mode = getattr(args, "compatibility_mode", False)
    requested_shape = normalized_discovery_shape(
        args.discovery_shape,
        args.sync_mode,
        normalized_host,
    )
    if is_deepseek_harness_host(normalized_host):
        if not compatibility_mode:
            raise UpdateError(
                "DeepSeek Harness defaults to the native profile plugin. Run "
                f"`{DEEPSEEK_HARNESS_PLUGIN_INSTALL}`; use --compatibility-mode "
                "only when the DSH bundle API or pnpm-backed plugin manager is unavailable."
            )
        if (
            requested_shape != "direct-child"
            or args.sync_mode not in REGISTER_TIME_SYNC_MODES
        ):
            raise UpdateError(
                "DeepSeek Harness compatibility mode requires direct-child discovery "
                "with --sync-mode junction, symlink, or copy-skills."
            )
    elif compatibility_mode:
        raise UpdateError("--compatibility-mode is currently reserved for DeepSeek Harness")

    effective_discovery_root = args.discovery_root
    if not effective_discovery_root:
        default_discovery_root = default_discovery_root_for_host(normalized_host)
        if default_discovery_root:
            effective_discovery_root = default_discovery_root.as_posix()
    discovery_name_prefix = normalize_discovery_name_prefix(args.discovery_name_prefix)
    if discovery_name_prefix and requested_shape != "direct-child":
        raise UpdateError("--discovery-name-prefix requires --discovery-shape direct-child")
    if (
        requested_shape == "direct-child"
        and args.sync_mode in {"junction", "symlink", "copy-skills"}
        and not effective_discovery_root
    ):
        raise UpdateError("direct-child sync registration requires --discovery-root")

    entry = register_installation(
        Path(args.registry).expanduser(),
        host=args.host,
        install_id=args.install_id,
        method_pack_root=Path(args.method_pack_root),
        discovery_root=(
            Path(effective_discovery_root) if effective_discovery_root else None
        ),
        workspace_helper=Path(args.workspace_helper) if args.workspace_helper else None,
        sync_mode=args.sync_mode,
        discovery_shape=args.discovery_shape,
        discovery_name_prefix=args.discovery_name_prefix,
        tracked_ref=args.tracked_ref,
        update_mode=args.update_mode,
        reload_hint=args.reload_hint,
    )
    if not should_sync_and_verify_at_register(entry):
        return entry

    sync_result = sync_skills(entry)
    doctor_result = run_doctor(
        entry,
        config_path=Path(args.config).expanduser() if args.config else None,
    )
    result = dict(entry)
    result["status"] = "registered"
    result["sync"] = sync_result
    result["verified"] = True
    result["doctor"] = {
        "ok": doctor_result.get("ok"),
        "workspaceSupport": doctor_result.get("workspaceSupport"),
        "configStatus": doctor_result.get("configStatus"),
        "expectedDiscoveryShape": doctor_result.get("expectedDiscoveryShape"),
        "discoveryShapeStatus": doctor_result.get("discoveryShapeStatus"),
        "compatibilityExposureStatus": doctor_result.get("compatibilityExposureStatus"),
    }
    return result


def command_status(args: argparse.Namespace) -> Any:
    data = load_registry(Path(args.registry).expanduser())
    if args.host:
        return select_installations(data, host=args.host, all_hosts=False)
    return data["installations"]


def command_update(args: argparse.Namespace) -> Any:
    if args.host and args.all:
        raise UpdateError("Use either --host or --all, not both")
    registry_path = Path(args.registry).expanduser()
    data = load_registry(registry_path)
    host = args.host or os.environ.get("AEGIS_HOST")
    selected = select_installations(data, host=host, all_hosts=args.all)
    return update_registered_installations(
        registry_path,
        selected,
        config_path=Path(args.config).expanduser() if args.config else None,
        dry_run=args.dry_run,
        stash=args.stash,
        force=args.force,
        verify=not args.no_verify,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.error("command is required: register, status, or update")

    try:
        if args.command == "register":
            result = command_register(args)
        elif args.command == "status":
            result = command_status(args)
        elif args.command == "update":
            result = command_update(args)
        else:
            raise UpdateError(f"Unknown command: {args.command}")
    except UpdateError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2, ensure_ascii=False))
        else:
            print(f"Aegis update failed: {exc}", file=sys.stderr)
        return 1

    emit(result, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
