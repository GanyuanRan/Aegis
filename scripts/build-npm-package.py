#!/usr/bin/env python3
"""Pack a scoped registry distribution from canonical, tracked Aegis sources.

Does not publish, change the source manifest, or inspect npm credentials.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parent.parent
DIRECTORIES = {
    ".claude-plugin", ".codebuddy-plugin", ".codex", ".codex-plugin",
    ".cursor", ".cursor-plugin", ".opencode", ".windsurf", "assets",
    "commands", "docs", "extensions", "hooks", "scripts", "skills",
}
ROOT_FILES = {
    "AGENTS.md", "CLAUDE.md", "CONTEXT.md", "LICENSE", "package.json",
    "README.md", "README.en.md", "README.zh-CN.md", "RELEASE-NOTES.md",
    "GLOBAL_USER_RULES_TEMPLATE.md", "GLOBAL_USER_RULES_TEMPLATE.zh-CN.md",
    "kimi.plugin.json", "SUPPORT.md", "SECURITY.md", "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
}


def build(package_name: str, output: Path, root: Path = ROOT) -> dict:
    if not re.fullmatch(r"@[a-z0-9][a-z0-9._-]*/aegis", package_name):
        raise ValueError("Use an owner-controlled scoped name: @scope/aegis")
    root = root.resolve()
    output = output.resolve()
    manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "aegis" or manifest.get("private") is not True:
        raise ValueError("Expected the private canonical aegis Git manifest")
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=root
    ).decode("utf-8").split("\0")
    selected = sorted(p for p in tracked if p and (
        p in ROOT_FILES or p.split("/")[0] in DIRECTORIES
    ))
    # These local/process surfaces never belong in a registry artifact, even
    # if someone accidentally stages them in Git.
    for relative in selected:
        parts = Path(relative).parts
        if any(p in {"node_modules", "__pycache__", ".git", "archive"} for p in parts):
            raise ValueError(f"Non-distribution path tracked: {relative}")
        source = root / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Expected a regular tracked file: {relative}")
        if not source.resolve().is_relative_to(root):
            raise ValueError(f"Source escapes repository: {relative}")
    required = {
        "LICENSE", "skills/using-aegis/SKILL.md", "scripts/aegis-doctor.py",
        "scripts/aegis-workspace.py", "extensions/dsh/index.js",
        "extensions/dsh/bootstrap.js", "extensions/dsh/cordis.patch.yml",
    }
    if not required.issubset(selected):
        raise ValueError(f"Missing distribution files: {sorted(required - set(selected))}")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise ValueError("npm is required to create the registry tarball")

    with tempfile.TemporaryDirectory(prefix="aegis-npm-") as temporary:
        stage = Path(temporary) / "package"
        stage.mkdir()
        for relative in selected:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, target)
        manifest["name"] = package_name
        manifest.pop("private")
        manifest["description"] = "Aegis Method Pack: portable agent skills and host integrations"
        manifest["publishConfig"] = {
            "access": "public", "registry": "https://registry.npmjs.org/",
        }
        manifest["files"] = selected
        (stage / "package.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        patch = stage / "extensions/dsh/cordis.patch.yml"
        original = patch.read_text(encoding="utf-8")
        old_entry = "name: 'aegis/extensions/dsh/index.js'"
        if original.count(old_entry) != 1:
            raise ValueError("Canonical DSH module entry changed; review registry projection")
        patch.write_text(original.replace(
            old_entry, f"name: '{package_name}/extensions/dsh/index.js'"
        ), encoding="utf-8")
        result = subprocess.run(
            [npm, "pack", "--json", "--ignore-scripts"], cwd=stage,
            text=True, encoding="utf-8", capture_output=True, check=True,
        )
        info = json.loads(result.stdout)[0]
        archive = stage / info["filename"]
        with tarfile.open(archive, "r:gz") as packed:
            names = {member.name.removeprefix("package/") for member in packed.getmembers() if member.isfile()}
        if names != set(selected):
            raise ValueError(f"npm payload differs from allowlist: {sorted(names ^ set(selected))}")
        output.mkdir(parents=True, exist_ok=True)
        destination = output / archive.name
        # Exclusive creation: never replace a previously reviewed release artifact.
        with destination.open("xb") as handle, archive.open("rb") as source:
            shutil.copyfileobj(source, handle)
        return {
            "name": package_name, "version": manifest["version"],
            "tarball": str(destination), "integrity": info["integrity"],
            "files": len(names), "published": False,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Confirmed owner-controlled @scope/aegis")
    parser.add_argument("--output", required=True, type=Path, help="Directory for the new tarball")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.name, args.output), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Cannot build npm distribution: {error}\n")


if __name__ == "__main__":
    main()
