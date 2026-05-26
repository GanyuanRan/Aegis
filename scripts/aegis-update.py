#!/usr/bin/env python3
"""Update registered Aegis Method Pack installations.

The updater is host-scoped by design. A plain update targets the current or
explicit host installation; updating every registered host requires --all.
"""

from __future__ import annotations

import argparse
import json
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
COPY_DISCOVERY_KEY_SKILLS = ("using-aegis", "update-aegis", "verification-before-completion")


class UpdateError(Exception):
    pass


def method_pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_registry_path() -> Path:
    return Path.home() / ".config" / "aegis" / "installations.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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


def register_installation(
    registry_path: Path,
    *,
    host: str,
    method_pack_root: Path,
    discovery_root: Path | None = None,
    sync_mode: str = "repo-only",
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
        "trackedRef": tracked_ref,
        "updateMode": update_mode,
        "reloadHint": reload_hint or default_reload_hint(normalized_host),
        "lastRegisteredAt": utc_now(),
    }
    if discovery_root:
        entry["discoveryRoot"] = Path(discovery_root).expanduser().resolve().as_posix()

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
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
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


def sync_skills(entry: dict[str, Any]) -> str:
    sync_mode = entry.get("syncMode", "repo-only")
    if sync_mode in {"junction", "symlink", "repo-only"}:
        return f"{sync_mode}: no copy step required"
    if sync_mode == "plugin-managed":
        return "plugin-managed: update is owned by the host plugin manager"
    if sync_mode != "copy-skills":
        raise UpdateError(f"Unsupported syncMode: {sync_mode}")

    discovery_root = entry.get("discoveryRoot")
    if not discovery_root:
        raise UpdateError("copy-skills sync requires discoveryRoot")

    source = Path(entry["methodPackRoot"]) / "skills"
    target = Path(discovery_root)
    if not source.is_dir():
        raise UpdateError(f"Source skills directory is missing: {source}")
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        destination = target / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        elif child.is_file():
            shutil.copy2(child, destination)
    verify_copy_discovery_root(entry)
    return f"copied skills into {target.as_posix()}"


def doctor_discovery_root(entry: dict[str, Any]) -> str | None:
    discovery_root = entry.get("discoveryRoot")
    if not discovery_root:
        return None
    if entry.get("syncMode", "repo-only") in {"junction", "symlink", "repo-only"}:
        return discovery_root
    return None


def verify_copy_discovery_root(entry: dict[str, Any]) -> None:
    if entry.get("syncMode") != "copy-skills":
        return
    discovery_root = entry.get("discoveryRoot")
    if not discovery_root:
        raise UpdateError("copy-skills sync requires discoveryRoot")
    root = Path(discovery_root)
    for skill in COPY_DISCOVERY_KEY_SKILLS:
        skill_md = root / skill / "SKILL.md"
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


def update_installation(
    entry: dict[str, Any],
    *,
    config_path: Path | None = None,
    dry_run: bool = False,
    stash: bool = False,
    force: bool = False,
    verify: bool = True,
) -> dict[str, Any]:
    if entry.get("updateMode") == "disabled" and not force:
        return {
            "id": entry.get("id"),
            "host": entry.get("host"),
            "status": "skipped",
            "reason": "updateMode is disabled",
        }

    if entry.get("syncMode") == "plugin-managed":
        return {
            "id": entry.get("id"),
            "host": entry.get("host"),
            "status": "skipped",
            "reason": "host plugin manager owns this update path",
            "reloadHint": entry.get("reloadHint"),
        }

    root = Path(entry["methodPackRoot"])
    tracked_ref, remote_ref = branch_remote_ref(entry.get("trackedRef", "main"))
    if dry_run:
        return {
            "id": entry.get("id"),
            "host": entry.get("host"),
            "status": "dry-run",
            "methodPackRoot": root.as_posix(),
            "wouldFetch": f"origin {tracked_ref}",
            "wouldMerge": remote_ref,
            "wouldVerify": verify,
            "reloadHint": entry.get("reloadHint"),
        }

    ensure_git_checkout(root)
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
    sync_result = sync_skills(entry)
    doctor_result = run_doctor(entry, config_path=config_path) if verify else None
    after = current_commit(root)

    return {
        "id": entry.get("id"),
        "host": entry.get("host"),
        "status": "updated" if before != after else "already-current",
        "beforeCommit": before,
        "afterCommit": after,
        "sync": sync_result,
        "verified": doctor_result is not None,
        "reloadHint": entry.get("reloadHint"),
    }


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
    for entry in selected:
        result = update_installation(
            entry,
            config_path=config_path,
            dry_run=dry_run,
            stash=stash,
            force=force,
            verify=verify,
        )
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
    register.add_argument("--method-pack-root", default=method_pack_root().as_posix())
    register.add_argument("--discovery-root")
    register.add_argument("--workspace-helper")
    register.add_argument("--sync-mode", choices=sorted(VALID_SYNC_MODES), default="repo-only")
    register.add_argument("--tracked-ref", default="main")
    register.add_argument("--update-mode", choices=sorted(VALID_UPDATE_MODES), default="manual")
    register.add_argument("--reload-hint")

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
    return register_installation(
        Path(args.registry).expanduser(),
        host=args.host,
        install_id=args.install_id,
        method_pack_root=Path(args.method_pack_root),
        discovery_root=Path(args.discovery_root) if args.discovery_root else None,
        workspace_helper=Path(args.workspace_helper) if args.workspace_helper else None,
        sync_mode=args.sync_mode,
        tracked_ref=args.tracked_ref,
        update_mode=args.update_mode,
        reload_hint=args.reload_hint,
    )


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
