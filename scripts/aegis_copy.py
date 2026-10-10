"""File ownership and preflight for the updater's copy-skills exposure."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any


class CopySyncError(Exception):
    pass


def copy_scope(source_root: Path, target_root: Path, prefix: str) -> dict[str, str]:
    return {
        "methodPackRoot": source_root.resolve().as_posix(),
        "discoveryRoot": target_root.resolve().as_posix(),
        "discoveryNamePrefix": prefix,
    }


def _conflict(path: Path, reason: str) -> None:
    raise CopySyncError(
        f"copy-skills conflict at {path}: {reason}. "
        "Reconcile or move this path, or use a separate discovery root, then retry."
    )


def _check_path(path: Path) -> None:
    """Do not traverse links, junctions, or non-directory parents, even if broken."""
    for candidate in reversed((path, *path.parents)):
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            _conflict(candidate, "symbolic links and junctions are not copied ownership")
        if candidate != path and not stat.S_ISDIR(info.st_mode):
            _conflict(candidate, "a parent is not a directory")


def _relative_path(value: str) -> Path:
    relative = PurePosixPath(value)
    if (
        not value
        or relative.is_absolute()
        or any(part in {".", ".."} for part in value.split("/"))
        or "\\" in value
        or ":" in value
        or "\0" in value
        or relative.as_posix() != value
    ):
        raise CopySyncError(f"Invalid copyInventory relative path: {value!r}")
    return Path(*relative.parts)


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_key(value: str) -> str:
    return unicodedata.normalize("NFC", value.casefold())


def sync_copy(
    source_root: Path,
    target: Path,
    prefix: str,
    inventory: Any,
    required_skills: tuple[str, ...],
) -> dict[str, Any]:
    """Preflight the whole view, then replace/retire only proven unchanged files."""
    source = source_root / "skills"
    _check_path(source)
    _check_path(target)
    if not source.is_dir():
        raise CopySyncError(f"Source skills directory is missing: {source}")
    if target.exists() and not target.is_dir():
        _conflict(target, "the discovery root is not a directory")
    source = source.resolve()
    target = target.resolve()
    if source.is_relative_to(target) or target.is_relative_to(source):
        _conflict(target, "source skills and discovery root overlap")

    scope = copy_scope(source_root, target, prefix)
    previous: dict[str, str] = {}
    if inventory is not None:
        if not isinstance(inventory, dict):
            raise CopySyncError("Invalid copyInventory: expected an object")
        if inventory.get("scope") == scope:
            previous = inventory.get("files")
            if not isinstance(previous, dict):
                raise CopySyncError("Invalid copyInventory: expected file digests")
            for relative, digest in previous.items():
                _relative_path(relative)
                if not isinstance(digest, str) or len(digest) != 64 or any(
                    char not in "0123456789abcdef" for char in digest
                ):
                    raise CopySyncError(f"Invalid copyInventory digest: {relative}")
    previous_by_path = {os.path.normcase(relative): digest for relative, digest in previous.items()}

    files: dict[str, tuple[Path, str]] = {}
    directories: dict[str, Path] = {}
    destinations: dict[str, Path] = {}

    def collect(path: Path, relative: Path) -> None:
        _check_path(path)
        key = relative.as_posix()
        _relative_path(key)
        # Require portable source names even on case-sensitive hosts. This key
        # rejects ambiguous output layouts; it never grants file ownership.
        destination_key = _portable_key(key)
        if destination_key in destinations:
            raise CopySyncError(
                f"Source entries {destinations[destination_key]} and {path} map to "
                "the same destination under portable Unicode/case normalization. "
                "Rename the conflicting source entries before retrying."
            )
        destinations[destination_key] = path
        if path.is_dir():
            directories[key] = path
            for child in sorted(path.iterdir()):
                collect(child, relative / child.name)
        elif path.is_file():
            files[key] = (path, _digest(path))
        else:
            _conflict(path, "source is not a regular file or directory")

    for child in sorted(source.iterdir()):
        name = prefix + child.name if child.is_dir() and (child / "SKILL.md").is_file() else child.name
        collect(child, Path(name))
    for skill in required_skills:
        if f"{prefix}{skill}/SKILL.md" not in files:
            raise CopySyncError(f"Source skills directory is missing {skill}/SKILL.md: {source}")

    # All conflicts, including stale-path containment, are checked before mkdir,
    # copy, or unlink. A name or prefix never grants ownership of a directory.
    for relative in directories:
        destination = target / relative
        _check_path(destination)
        if destination.exists() and not destination.is_dir():
            _conflict(destination, "a source directory collides with a file")

    writes = []
    current_file_aliases = set()
    for relative, (path, digest) in files.items():
        destination = target / relative
        _check_path(destination)
        if destination.exists():
            if not destination.is_file():
                _conflict(destination, "a source file collides with a directory")
            info = destination.stat()
            current_file_aliases.add((_portable_key(relative), info.st_dev, info.st_ino))
            current = _digest(destination)
            if current == digest:
                continue  # Safe adoption also makes a partially copied retry harmless.
            if current != previous_by_path.get(os.path.normcase(relative)):
                _conflict(destination, "the file is untracked or locally modified")
        writes.append((path, destination))

    retire = []
    current_paths = {os.path.normcase(relative) for relative in files}
    for relative, digest in previous.items():
        if os.path.normcase(relative) in current_paths:
            continue
        destination = target / _relative_path(relative)
        _check_path(destination)
        if destination.is_file():
            info = destination.stat()
            # Preserve aliases through case/Unicode spelling changes without
            # retaining unrelated stale hardlink names. This grants no ownership.
            alias = (_portable_key(relative), info.st_dev, info.st_ino)
            if alias not in current_file_aliases and _digest(destination) == digest:
                retire.append(destination)

    target.mkdir(parents=True, exist_ok=True)
    for relative in sorted(directories, key=lambda name: len(Path(name).parts)):
        (target / relative).mkdir(parents=True, exist_ok=True)
    for path, destination in writes:
        # Stage each file beside its destination. A failed copy leaves existing
        # bytes intact; replacement also avoids writing through hard links.
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".aegis-copy-", delete=False) as staged:
            staged_path = Path(staged.name)
        try:
            shutil.copy2(path, staged_path)
            staged_path.replace(destination)
        finally:
            staged_path.unlink(missing_ok=True)
    for destination in retire:
        destination.unlink()
        parent = destination.parent
        while parent != target:
            # Keep user additions and directories still present in the source.
            if parent.relative_to(target).as_posix() in directories or any(parent.iterdir()):
                break
            parent.rmdir()
            parent = parent.parent

    return {"scope": scope, "files": {relative: digest for relative, (_, digest) in files.items()}}
