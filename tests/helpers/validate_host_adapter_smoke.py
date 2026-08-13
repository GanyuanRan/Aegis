#!/usr/bin/env python3
"""Parse host adapter manifests and hook files for lightweight smoke coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def load_json(path: Path) -> Any:
    require(path.exists(), f"missing JSON file: {path.as_posix()}")
    return json.loads(path.read_text(encoding="utf-8"))


def field(data: Any, dotted: str) -> Any:
    value = data
    for part in dotted.split("."):
        value = value[int(part)] if part.isdigit() else value[part]
    return value


def validate_versions(root: Path) -> None:
    package = load_json(root / "package.json")
    expected = package["version"]
    config = load_json(root / ".version-bump.json")
    for item in config["files"]:
        path = root / item["path"]
        actual = field(load_json(path), item["field"])
        require(actual == expected, f"{item['path']} {item['field']} version drift: {actual} != {expected}")


def validate_codex_manifest(root: Path) -> None:
    manifest = load_json(root / ".codex-plugin" / "plugin.json")
    require(manifest.get("name") == "aegis", "Codex manifest name must be aegis")
    require(manifest.get("skills") == "./skills/", "Codex manifest must expose ./skills/")
    interface = manifest.get("interface", {})
    require(interface.get("composerIcon") == "./assets/aegis-small.svg", "Codex manifest must reference composer icon")
    require(interface.get("logo") == "./assets/app-icon.png", "Codex manifest must reference logo")
    require((root / "assets" / "aegis-small.svg").exists(), "composer icon asset must exist")
    require((root / "assets" / "app-icon.png").exists(), "logo asset must exist")


def validate_kimi_manifest(root: Path) -> None:
    manifest = load_json(root / "kimi.plugin.json")
    require(manifest.get("name") == "aegis", "Kimi manifest name must be aegis")
    require(manifest.get("skills") == "./skills/", "Kimi manifest must expose ./skills/")
    require(
        manifest.get("sessionStart", {}).get("skill") == "using-aegis",
        "Kimi manifest must load using-aegis at session start",
    )
    require(
        (root / "skills" / "using-aegis" / "SKILL.md").is_file(),
        "Kimi session-start skill must exist",
    )
    unsupported = {
        "tools",
        "apps",
        "inject",
        "configFile",
        "bootstrap",
        "mcpServers",
        "hooks",
    }.intersection(manifest)
    require(not unsupported, f"Kimi manifest contains unneeded runtime fields: {sorted(unsupported)}")


def validate_cursor_manifest(root: Path) -> None:
    manifest = load_json(root / ".cursor-plugin" / "plugin.json")
    require(manifest.get("skills") == "./skills/", "Cursor manifest must expose skills")
    require("agents" not in manifest, "Cursor manifest must not expose retired root agents")
    require(manifest.get("commands") == "./commands/", "Cursor manifest must expose commands")
    require(manifest.get("hooks") == "./hooks/hooks-cursor.json", "Cursor manifest must point at hooks-cursor.json")
    require((root / "hooks" / "hooks-cursor.json").exists(), "Cursor hook file must exist")


def validate_hook_files(root: Path) -> None:
    claude_hooks = load_json(root / "hooks" / "hooks.json")
    cursor_hooks = load_json(root / "hooks" / "hooks-cursor.json")
    github_hook = load_json(root / ".github" / "hooks" / "session-start.json")
    require("SessionStart" in claude_hooks.get("hooks", {}), "Claude hook config must define SessionStart")
    require("sessionStart" in cursor_hooks.get("hooks", {}), "Cursor hook config must define sessionStart")
    session = github_hook.get("hooks", {}).get("sessionStart", [])
    require(session, "GitHub/Copilot hook config must define sessionStart")
    hook = session[0]
    require("hooks/session-start" in hook.get("bash", ""), "Copilot hook bash command must call session-start")
    require("hooks/copilot-session-start.ps1" in hook.get("powershell", ""), "Copilot hook powershell command must call fallback script")
    require((root / "hooks" / "session-start").exists(), "session-start hook must exist")
    require((root / "hooks" / "copilot-session-start.ps1").exists(), "Copilot PowerShell fallback must exist")


def validate_marketplace(root: Path) -> None:
    for rel in (".claude-plugin/marketplace.json", ".codebuddy-plugin/marketplace.json"):
        marketplace = load_json(root / rel)
        plugin = marketplace["plugins"][0]
        require(plugin.get("name") == "aegis", f"{rel} must publish aegis plugin")
        require(plugin.get("source") == "./", f"{rel} source must stay local plugin root")


def validate(root: Path) -> None:
    validate_versions(root)
    validate_codex_manifest(root)
    validate_kimi_manifest(root)
    validate_cursor_manifest(root)
    validate_hook_files(root)
    validate_marketplace(root)
    require(not (root / "docs" / "aegis").exists(), "method-pack repo must not ship docs/aegis workspace")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: validate_host_adapter_smoke.py <repo-root>")
    validate(Path(argv[1]))
    print("  [PASS] host adapter manifests, hook configs, versions, assets, and workspace boundary parse cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
