#!/usr/bin/env python3
"""Verify an installed Aegis Method Pack.

The doctor checks skill discovery surfaces and project workspace support without
writing a live docs/aegis workspace into the Aegis Method Pack repository.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


KEY_SKILLS = (
    "using-aegis",
    "goal-framing",
    "first-principles-review",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "recording-architecture-decisions",
    "verification-before-completion",
)

STALE_USING_AEGIS_PATTERNS = (
    "brainstorming item 8",
    "If `docs/aegis/` missing → create now",
)

REQUIRED_USING_AEGIS_PATTERNS = (
    "Spec Brief or Design Spec only",
    "Bug, failure, regression, or unexpected behavior routes to",
    "Workspace support is lazy",
    "configured Aegis workspace support",
)

TRIGGER_HEALTH_LAYERS = (
    "install/version",
    "host discovery",
    "activation/bootstrap",
    "using-aegis router entry",
    "task-to-skill routing",
    "skill execution depth",
    "context pressure and re-entry",
    "false-positive over-triggering",
)

KIMI_AUTO_PROFILE = "kimi-code-auto"
KIMI_EXPLICIT_PROFILE = "kimi-code-explicit"


class DoctorError(Exception):
    pass


def normalize_discovery_name_prefix(value: str | None) -> str:
    if value is None:
        return ""
    if "\0" in value or "/" in value or "\\" in value:
        raise DoctorError("discovery name prefix must not contain path separators")
    if value in {".", ".."}:
        raise DoctorError("discovery name prefix must not be a relative path segment")
    return value


def discovery_name_policy(prefix: str, *, canonical_source: bool = False) -> str:
    if canonical_source:
        return "canonical-source"
    if prefix:
        return f"prefix:{prefix}"
    return "identity"


def discovery_skill_dir_name(skill_name: str, prefix: str) -> str:
    return f"{prefix}{skill_name}"


def file_content_matches(current: Path, expected: Path) -> bool:
    try:
        return current.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")
    except OSError as exc:
        raise DoctorError(f"cannot compare discovery content: {exc}") from exc


def default_config_path() -> Path:
    return Path.home() / ".config" / "aegis" / "config.toml"


AGENTS_MD_BEGIN = "<!-- AEGIS-ROUTING-BEGIN -->"
AGENTS_MD_END = "<!-- AEGIS-ROUTING-END -->"
AGENTS_MD_ROUTING_FEATURE = "已安装 Aegis 时"
AGENTS_MD_EXPLICIT_CONTENT = (
    "已安装 Aegis 时：仅在用户显式调用 Aegis 或点名具体 Aegis skill 时"
    "加载对应 skill 或 workflow；简单任务直接 fast-path，"
    "不列清单、不写文档、不做仪式。"
)
AGENTS_MD_AUTO_CONTENT = (
    "已安装 Aegis 时：\n\n"
    "- 每轮开始先判断是否有相关 Aegis skill；匹配时加载并遵循该 skill\n"
    "- 复杂、诊断、架构、重构、contract、跨模块变更默认走 Aegis 对应 workflow\n"
    "- Aegis skill 是方法层执行纪律，不是项目事实 source of truth，也不是 runtime authority"
)


def default_agents_md_path() -> Path:
    return Path.home() / ".codex" / "AGENTS.md"


def agents_md_state_path() -> Path:
    return Path.home() / ".config" / "aegis" / "agents-md-state.json"


def read_agents_md_state(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return load_json_object(path, "agents-md state")


def write_agents_md_state(path: Path, state: dict[str, object]) -> None:
    write_text_lf(path, json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def agents_md_block_bounds(text: str) -> tuple[int, int]:
    start = text.find(AGENTS_MD_BEGIN)
    if start < 0:
        return -1, -1
    end = text.find(AGENTS_MD_END, start)
    if end < 0:
        raise DoctorError("AGENTS.md has AEGIS-ROUTING-BEGIN without AEGIS-ROUTING-END")
    return start, end + len(AGENTS_MD_END)


def agents_md_wrap(content: str) -> str:
    return f"{AGENTS_MD_BEGIN}\n{content.rstrip()}\n{AGENTS_MD_END}\n"


def agents_md_routing_bounds(text: str, feature_idx: int) -> tuple[int, int]:
    start = text.rfind("\n", 0, feature_idx) + 1
    end = start
    while end < len(text):
        nl = text.find("\n", end)
        if nl == -1:
            end = len(text)
            break
        line = text[end:nl]
        if line.startswith("#"):
            break
        end = nl + 1
    if end - start > 4000:
        raise DoctorError(
            "AGENTS.md routing paragraph is unexpectedly large; "
            "restore from backup and manage manually"
        )
    return start, end


def apply_agents_md(mode: str, path: Path, state_path: Path) -> dict[str, object]:
    """Manage the Aegis routing block in the Codex user AGENTS.md.

    Migration on first use, then block replacement only. Raises DoctorError
    before any write on failure so the caller keeps config write atomic.
    """
    if not path.is_file():
        return {"agentsMd": "skipped", "reason": "no-agents-md-file"}
    original = path.read_text(encoding="utf-8")
    state = read_agents_md_state(state_path)
    start, end = agents_md_block_bounds(original)

    if start < 0:
        feature_idx = original.find(AGENTS_MD_ROUTING_FEATURE)
        if feature_idx < 0:
            auto_content = AGENTS_MD_AUTO_CONTENT
            block_text = agents_md_wrap(auto_content)
            new_text = original.rstrip() + "\n\n" + block_text + "\n"
            state["original_routing_block"] = auto_content
        else:
            block_start, block_end = agents_md_routing_bounds(original, feature_idx)
            auto_content = original[block_start:block_end].strip("\n")
            block_text = agents_md_wrap(auto_content)
            new_text = original[:block_start] + block_text + original[block_end:]
            state["original_routing_block"] = auto_content
        backup_path = path.with_name(f"{path.name}.bak-aegis-{int(time.time())}")
        backup_path.write_text(original, encoding="utf-8")
        state["agents_md_path"] = path.as_posix()
        state["backup"] = backup_path.as_posix()
        write_agents_md_state(state_path, state)
        original = new_text
        start, end = agents_md_block_bounds(original)
        migrated = True
    else:
        migrated = False

    if mode == "explicit":
        inner = AGENTS_MD_EXPLICIT_CONTENT
    else:
        inner = state.get("original_routing_block")
        if not isinstance(inner, str) or not inner.strip():
            raise DoctorError(
                "AGENTS.md routing block exists but agents-md state has no original text; "
                "restore from backup or manage manually"
            )
    new_text = original[:start] + agents_md_wrap(inner) + original[end:]
    if "\r\n" in original:
        new_text = new_text.replace("\n", "\r\n")
    write_text_lf(path, new_text)
    return {
        "agentsMd": "updated",
        "mode": mode,
        "migrated": migrated,
        "backup": state.get("backup"),
        "reason": None,
    }


def resolve_kimi_home(value: str | None) -> Path:
    configured = value or os.environ.get("KIMI_CODE_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".kimi-code").resolve()


def load_kimi_installed_file(kimi_home: Path) -> dict[str, object]:
    installed_path = kimi_home / "plugins" / "installed.json"
    if not installed_path.is_file():
        return {"version": 1, "plugins": []}
    try:
        data = json.loads(installed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DoctorError(f"cannot parse Kimi plugin registry {installed_path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise DoctorError(f"Kimi plugin registry must use version 1: {installed_path}")
    if not isinstance(data.get("plugins"), list):
        raise DoctorError(f"Kimi plugin registry must contain a plugins list: {installed_path}")
    return data


def load_json_object(path: Path, label: str) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DoctorError(f"cannot parse {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise DoctorError(f"{label} must be a JSON object: {path}")
    return data


def validate_kimi_plugin_record(root: Path, kimi_home: Path) -> dict[str, object]:
    installed = load_kimi_installed_file(kimi_home)
    records = [
        item
        for item in installed["plugins"]  # type: ignore[index]
        if isinstance(item, dict) and item.get("id") == "aegis"
    ]
    if len(records) != 1:
        raise DoctorError(
            "Kimi auto mode requires exactly one installed Aegis plugin; "
            "run /plugins install https://github.com/GanyuanRan/Aegis and then /reload or /new"
        )
    record = records[0]
    if record.get("enabled") is not True:
        raise DoctorError("Kimi Aegis plugin is disabled; enable it with /plugins enable aegis")
    record_root_value = record.get("root")
    if not isinstance(record_root_value, str) or not record_root_value:
        raise DoctorError("Kimi Aegis plugin record is missing its managed root")
    record_root = Path(record_root_value).expanduser()
    if not record_root.is_dir():
        raise DoctorError(f"Kimi Aegis managed root is missing: {record_root}")
    try:
        if record_root.resolve() != root.resolve():
            raise DoctorError(
                "run aegis-doctor.py from Kimi's managed Aegis plugin root: "
                f"{record_root.resolve()}"
            )
    except OSError as exc:
        raise DoctorError(f"cannot resolve Kimi Aegis managed root: {exc}") from exc

    package = load_json_object(root / "package.json", "Aegis package metadata")
    manifest = load_json_object(root / "kimi.plugin.json", "Kimi plugin manifest")
    session_start = manifest.get("sessionStart")
    if not isinstance(session_start, dict):
        raise DoctorError("Kimi plugin manifest must define sessionStart")
    if manifest.get("name") != "aegis":
        raise DoctorError("Kimi plugin manifest name must be aegis")
    if manifest.get("version") != package.get("version"):
        raise DoctorError(
            "Kimi managed plugin version differs from the Aegis package version: "
            f"{manifest.get('version')!r} != {package.get('version')!r}"
        )
    if manifest.get("skills") != "./skills/":
        raise DoctorError("Kimi plugin manifest must expose the canonical ./skills/ tree")
    if session_start.get("skill") != "using-aegis":
        raise DoctorError("Kimi plugin manifest must load using-aegis at session start")

    return {
        "id": "aegis",
        "enabled": True,
        "source": record.get("source"),
        "root": record_root.resolve().as_posix(),
        "version": manifest.get("version"),
        "sessionStartSkill": "using-aegis",
    }


def skill_frontmatter_name(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0] != "---":
        return None
    for line in lines[1:]:
        if line == "---":
            return None
        if line.startswith("name:"):
            value = line.split(":", 1)[1].strip().strip('"').strip("'")
            return value or None
    return None


def find_kimi_skill_collisions(root: Path, kimi_home: Path) -> list[Path]:
    skills_root = root / "skills"
    canonical_names = {
        child.name
        for child in skills_root.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    }
    collision_roots = (kimi_home / "skills", Path.home() / ".agents" / "skills")
    collisions: list[Path] = []
    for discovery_root in collision_roots:
        for name in sorted(canonical_names):
            candidate = discovery_root / name / "SKILL.md"
            if candidate.is_file() and skill_frontmatter_name(candidate) == name:
                collisions.append(candidate.parent)
    return collisions


def enabled_kimi_aegis_plugin(kimi_home: Path) -> bool:
    installed = load_kimi_installed_file(kimi_home)
    return any(
        isinstance(item, dict) and item.get("id") == "aegis" and item.get("enabled") is True
        for item in installed["plugins"]  # type: ignore[index]
    )


def validate_kimi_explicit_mode(
    root: Path,
    kimi_home: Path,
    discovery_root: Path | None,
) -> dict[str, object]:
    if discovery_root is None:
        raise DoctorError("Kimi explicit mode requires --discovery-root")
    if enabled_kimi_aegis_plugin(kimi_home):
        raise DoctorError(
            "Kimi explicit mode conflicts with the enabled Aegis plugin; "
            "disable it with /plugins disable aegis and then /reload or /new"
        )
    selected = discovery_root.expanduser().resolve()
    alternate_collisions = [
        path
        for path in find_kimi_skill_collisions(root, kimi_home)
        if path.parent.resolve() != selected
    ]
    if alternate_collisions:
        joined = ", ".join(path.as_posix() for path in alternate_collisions)
        raise DoctorError(f"Kimi explicit mode has multiple direct-child Aegis exposures: {joined}")
    return {
        "mode": "explicit",
        "discoveryRoot": selected.as_posix(),
        "pluginEnabled": False,
    }


def method_pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def toml_string(value: str) -> str:
    return json.dumps(value)


def write_text_lf(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def read_config(path: Path) -> dict[str, str]:
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


def normalized_activation_mode(value: str | None) -> str:
    return value if value in {"auto", "explicit"} else "auto"


def normalized_tdd_mode(value: str | None) -> str:
    return value if value in {"auto", "off"} else "off"


def existing_activation_mode(path: Path) -> str:
    return normalized_activation_mode(read_config(path).get("activation_mode"))


def existing_tdd_mode(path: Path) -> str:
    return normalized_tdd_mode(read_config(path).get("tdd_mode"))


def write_config(
    path: Path,
    root: Path,
    helper: Path,
    activation_mode: str | None = None,
    tdd_mode: str | None = None,
) -> None:
    mode = normalized_activation_mode(activation_mode or existing_activation_mode(path))
    tdd = normalized_tdd_mode(tdd_mode or existing_tdd_mode(path))
    content = (
        "# Aegis user-local configuration\n"
        f"activation_mode = {toml_string(mode)}\n"
        f"tdd_mode = {toml_string(tdd)}\n"
        f"method_pack_root = {toml_string(root.as_posix())}\n"
        f"workspace_helper = {toml_string(helper.as_posix())}\n"
    )
    write_text_lf(path, content)


def config_status(path: Path, root: Path, helper: Path) -> str:
    config = read_config(path)
    if not config:
        return "missing"
    tdd_value = config.get("tdd_mode")
    if (
        config.get("activation_mode") in {"auto", "explicit"}
        and (tdd_value is None or tdd_value in {"auto", "off"})
        and Path(config.get("method_pack_root", "")).expanduser() == root
        and Path(config.get("workspace_helper", "")).expanduser() == helper
    ):
        return "configured"
    return "partial"


def resolve_workspace_helper(config_path: Path) -> tuple[Path, str]:
    env_helper = os.environ.get("AEGIS_WORKSPACE_HELPER")
    if env_helper:
        helper = Path(env_helper).expanduser()
        if helper.is_file():
            return helper, "env"

    config = read_config(config_path)
    configured_helper = config.get("workspace_helper")
    if configured_helper:
        helper = Path(configured_helper).expanduser()
        if helper.is_file():
            return helper, "config"

    installed_helper = method_pack_root() / "scripts" / "aegis-workspace.py"
    if installed_helper.is_file():
        return installed_helper, "installed-method-pack"

    cwd_helper = Path.cwd() / "scripts" / "aegis-workspace.py"
    if cwd_helper.is_file():
        return cwd_helper, "current-repo"

    raise DoctorError(
        "Aegis workspace helper unavailable. Set AEGIS_WORKSPACE_HELPER or run "
        "aegis-doctor.py --write-config from an installed Aegis Method Pack."
    )


def helper_path_result(args: argparse.Namespace) -> dict[str, object]:
    config_path = Path(args.config).expanduser() if args.config else default_config_path()
    helper, source = resolve_workspace_helper(config_path)
    helper_posix = helper.as_posix()
    return {
        "ok": True,
        "command": "helper-path",
        "workspaceHelper": helper_posix,
        "source": source,
        "configPath": config_path.as_posix(),
        "targetProjectRootArgument": "--root <target-project-root>",
        "shellHint": f"python {json.dumps(helper_posix)} check --root <target-project-root>",
        "note": (
            "The Aegis workspace helper belongs to the installed method-pack root; "
            "the target project is passed separately via --root."
        ),
    }


def activation_mode_result(args: argparse.Namespace) -> dict[str, object]:
    root = method_pack_root()
    helper = root / "scripts" / "aegis-workspace.py"
    config_path = Path(args.config).expanduser() if args.config else default_config_path()
    mode = normalized_activation_mode(args.mode)
    if args.mode != mode:
        raise DoctorError("activation-mode requires one of: auto, explicit")
    if not helper.is_file():
        raise DoctorError(f"Aegis workspace helper unavailable: {helper}")
    agents_md: dict[str, object] = {"agentsMd": "skipped", "reason": "disabled"}
    if not getattr(args, "no_agents_md", False):
        agents_md = apply_agents_md(mode, default_agents_md_path(), agents_md_state_path())
    write_config(config_path, root, helper, mode)
    return {
        "ok": True,
        "command": "activation-mode",
        "activationMode": mode,
        "configPath": config_path.as_posix(),
        "methodPackRoot": root.as_posix(),
        "workspaceHelper": helper.as_posix(),
        "agentsMd": agents_md.get("agentsMd"),
        "agentsMdReason": agents_md.get("reason"),
        "agentsMdBackup": agents_md.get("backup"),
        "restartRequired": True,
        "note": (
            "Activation mode is read by host bootstrap/profile setup. "
            "Restart or start a new host session for the change to take effect."
        ),
    }


def tdd_mode_result(args: argparse.Namespace) -> dict[str, object]:
    root = method_pack_root()
    helper = root / "scripts" / "aegis-workspace.py"
    config_path = Path(args.config).expanduser() if args.config else default_config_path()
    mode = normalized_tdd_mode(args.mode)
    if args.mode != mode:
        raise DoctorError("tdd-mode requires one of: auto, off")
    if not helper.is_file():
        raise DoctorError(f"Aegis workspace helper unavailable: {helper}")
    write_config(config_path, root, helper, tdd_mode=mode)
    return {
        "ok": True,
        "command": "tdd-mode",
        "tddMode": mode,
        "configPath": config_path.as_posix(),
        "methodPackRoot": root.as_posix(),
        "workspaceHelper": helper.as_posix(),
        "restartRequired": True,
        "note": (
            "TDD mode controls automatic test-first discipline only; "
            "verification-before-completion still applies."
        ),
    }


def run_helper(helper: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="aegis-doctor-") as tmp:
        target = Path(tmp) / "target-project"
        target.mkdir()
        init = subprocess.run(
            [sys.executable, str(helper), "init", "--root", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if init.returncode != 0:
            raise DoctorError(
                "workspace init failed: "
                + (init.stderr.strip() or init.stdout.strip() or str(init.returncode))
            )

        check = subprocess.run(
            [sys.executable, str(helper), "check", "--root", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check.returncode != 0:
            raise DoctorError(
                "workspace check failed: "
                + (check.stderr.strip() or check.stdout.strip() or str(check.returncode))
            )


def check_using_aegis_hot_path(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    folded = text.lower()
    for pattern in REQUIRED_USING_AEGIS_PATTERNS:
        if pattern.lower() not in folded:
            raise DoctorError(f"using-aegis hot path missing current pattern: {pattern}")
    for pattern in STALE_USING_AEGIS_PATTERNS:
        if pattern.lower() in folded:
            raise DoctorError(f"using-aegis hot path contains stale pattern: {pattern}")


def check_discovery_root(discovery_root: Path, skills: Path) -> None:
    if not discovery_root.is_dir():
        raise DoctorError(f"discovery root is not a directory: {discovery_root}")
    try:
        if discovery_root.resolve() != skills.resolve():
            raise DoctorError(
                "discovery root does not resolve to this method pack's skills directory: "
                f"{discovery_root} != {skills}"
            )
    except OSError as exc:
        raise DoctorError(f"cannot resolve discovery root: {exc}") from exc


def classify_discovery_root(
    discovery_root: Path,
    skills: Path,
    *,
    discovery_name_prefix: str | None = None,
) -> dict[str, str]:
    if not discovery_root.is_dir():
        raise DoctorError(f"discovery root is not a directory: {discovery_root}")
    name_prefix = normalize_discovery_name_prefix(discovery_name_prefix)

    try:
        if discovery_root.resolve() == skills.resolve():
            return {
                "expectedDiscoveryShape": "method-pack-skills-root",
                "discoveryShapeStatus": "current",
                "compatibilityExposureStatus": "canonical-source",
                "discoveryNamePolicy": discovery_name_policy(
                    name_prefix,
                    canonical_source=True,
                ),
                "discoveryNamePrefix": name_prefix,
            }
    except OSError as exc:
        raise DoctorError(f"cannot resolve discovery root: {exc}") from exc

    missing: list[str] = []
    stale: list[str] = []
    for skill_dir in sorted(skills.iterdir()):
        if not skill_dir.is_dir():
            continue
        expected_skill = skill_dir / "SKILL.md"
        if not expected_skill.is_file():
            continue
        target_name = discovery_skill_dir_name(skill_dir.name, name_prefix)
        candidate_skill = discovery_root / target_name / "SKILL.md"
        if not candidate_skill.is_file():
            missing.append(target_name)
            continue
        if not file_content_matches(candidate_skill, expected_skill):
            stale.append(target_name)

    if missing:
        joined = ", ".join(missing)
        prefix_detail = f" using name prefix {name_prefix!r}" if name_prefix else ""
        raise DoctorError(
            "discovery root does not expose the expected direct-child skill directories"
            + prefix_detail
            + ": "
            + joined
        )
    if stale:
        joined = ", ".join(stale)
        raise DoctorError(
            "stale compatibility exposure detected; direct-child skill copies differ from the canonical skills tree: "
            + joined
        )

    return {
        "expectedDiscoveryShape": (
            "prefixed-direct-child-skill-directories"
            if name_prefix
            else "direct-child-skill-directories"
        ),
        "discoveryShapeStatus": "current",
        "compatibilityExposureStatus": "generated-copy-view-current",
        "discoveryNamePolicy": discovery_name_policy(name_prefix),
        "discoveryNamePrefix": name_prefix,
    }


def perform_check(args: argparse.Namespace) -> dict[str, object]:
    root = method_pack_root()
    skills = root / "skills"
    helper = root / "scripts" / "aegis-workspace.py"
    config_path = Path(args.config).expanduser() if args.config else default_config_path()

    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            raise DoctorError(detail)

    record("method-pack-root", root.is_dir(), str(root))
    record("skills-directory", skills.is_dir(), str(skills))
    for skill in KEY_SKILLS:
        record(
            f"skill:{skill}",
            (skills / skill / "SKILL.md").is_file(),
            str(skills / skill / "SKILL.md"),
        )
    record("workspace-helper", helper.is_file(), str(helper))
    check_using_aegis_hot_path(skills / "using-aegis" / "SKILL.md")
    checks.append(
        {
            "name": "using-aegis-hot-path-current",
            "ok": True,
            "detail": "current hot path patterns present and stale patterns absent",
        }
    )
    if args.discovery_root:
        discovery_root = Path(args.discovery_root).expanduser()
        discovery_result = classify_discovery_root(
            discovery_root,
            skills,
            discovery_name_prefix=args.discovery_name_prefix,
        )
        checks.append(
            {
                "name": "discovery-root-current",
                "ok": True,
                "detail": str(discovery_root),
            }
        )
        checks.append(
            {
                "name": "discovery-shape-status",
                "ok": True,
                "detail": (
                    f"{discovery_result['expectedDiscoveryShape']} / "
                    f"{discovery_result['compatibilityExposureStatus']}"
                ),
            }
        )

    host_profile_result: dict[str, object] | None = None
    if args.host_profile:
        kimi_home = resolve_kimi_home(args.kimi_home)
        if args.host_profile == KIMI_AUTO_PROFILE:
            if args.discovery_root:
                raise DoctorError("Kimi auto mode must not use a direct-child --discovery-root")
            plugin = validate_kimi_plugin_record(root, kimi_home)
            collisions = find_kimi_skill_collisions(root, kimi_home)
            if collisions:
                joined = ", ".join(path.as_posix() for path in collisions)
                raise DoctorError(
                    "Kimi auto mode found duplicate direct-child Aegis exposure: "
                    f"{joined}. Disable/remove the plugin to keep explicit mode, or remove only "
                    "generated Aegis exposure after independently confirming ownership."
                )
            host_profile_result = {
                "hostProfile": KIMI_AUTO_PROFILE,
                "plugin": plugin,
                "duplicateExposureStatus": "none",
                "restartRequired": True,
            }
            checks.append(
                {
                    "name": "kimi-plugin-auto-route",
                    "ok": True,
                    "detail": "enabled Aegis plugin with using-aegis session start",
                }
            )
        else:
            explicit = validate_kimi_explicit_mode(
                root,
                kimi_home,
                Path(args.discovery_root) if args.discovery_root else None,
            )
            host_profile_result = {
                "hostProfile": KIMI_EXPLICIT_PROFILE,
                "plugin": {"enabled": False},
                "explicit": explicit,
                "duplicateExposureStatus": "none",
                "restartRequired": True,
            }
            checks.append(
                {
                    "name": "kimi-explicit-route",
                    "ok": True,
                    "detail": "direct-child exposure current and Aegis plugin disabled",
                }
            )
    record(
        "no-live-workspace-in-method-pack",
        not (root / "docs" / "aegis").exists(),
        "Aegis Method Pack repository must not ship docs/aegis",
    )

    run_helper(helper)
    checks.append(
        {
            "name": "workspace-helper-temp-target",
            "ok": True,
            "detail": "init/check passed in a temporary target project",
        }
    )

    if args.write_config:
        write_config(config_path, root, helper)
    status = config_status(config_path, root, helper)

    result = {
        "ok": True,
        "command": "check",
        "methodPackRoot": root.as_posix(),
        "workspaceSupport": "available",
        "configPath": config_path.as_posix(),
        "configStatus": status,
        "tddMode": existing_tdd_mode(config_path),
        "triggerHealth": {
            "baseline": (root / "docs" / "current" / "AEGIS_TRIGGER_HEALTH_BASELINE.md").as_posix(),
            "layers": list(TRIGGER_HEALTH_LAYERS),
            "note": "If expected skills do not trigger, diagnose the trigger chain before broadening skill wording.",
        },
        "checks": checks,
    }
    if args.discovery_root:
        result.update(discovery_result)
    if host_profile_result is not None:
        result.update(host_profile_result)
    return result


def print_text(result: dict[str, object]) -> None:
    if result.get("command") == "helper-path":
        print(f"Aegis workspace helper path: {result['workspaceHelper']}")
        print(f"Source: {result['source']}")
        print(f"Config path: {result['configPath']}")
        print(f"Target project argument: {result['targetProjectRootArgument']}")
        print(f"Shell hint: {result['shellHint']}")
        print(result["note"])
        return

    if result.get("command") == "activation-mode":
        print(f"Aegis activation mode set to {result['activationMode']}.")
        print(f"Config path: {result['configPath']}")
        agents_md = result.get("agentsMd")
        if agents_md == "updated":
            print("Codex AGENTS.md routing block updated.")
            backup = result.get("agentsMdBackup")
            if backup:
                print(f"Backup: {backup}")
        elif agents_md == "skipped" and result.get("agentsMdReason") != "disabled":
            print(f"AGENTS.md management skipped ({result['agentsMdReason']}).")
        print("Restart or start a new host session for the change to take effect.")
        return

    if result.get("command") == "tdd-mode":
        print(f"Aegis TDD mode set to {result['tddMode']}.")
        print(f"Config path: {result['configPath']}")
        print("Restart or start a new host session for the change to take effect.")
        print("TDD mode controls automatic test-first discipline; verification-before-completion still applies.")
        return

    print("Aegis doctor check passed.")
    print(f"Method pack root: {result['methodPackRoot']}")
    print(f"Project workspace support: {result['workspaceSupport']}")
    print(f"Config status: {result['configStatus']} ({result['configPath']})")
    print(f"TDD mode: {result['tddMode']}")
    if "expectedDiscoveryShape" in result:
        print(f"Expected discovery shape: {result['expectedDiscoveryShape']}")
        print(f"Discovery shape status: {result['discoveryShapeStatus']}")
        print(f"Compatibility exposure status: {result['compatibilityExposureStatus']}")
        print(f"Discovery name policy: {result['discoveryNamePolicy']}")
    if result.get("hostProfile"):
        print(f"Host profile: {result['hostProfile']}")
        print(f"Duplicate exposure status: {result['duplicateExposureStatus']}")
    trigger_health = result.get("triggerHealth", {})
    if isinstance(trigger_health, dict):
        print(f"Trigger health baseline: {trigger_health.get('baseline')}")
        print("Trigger health layers: " + ", ".join(trigger_health.get("layers", [])))
    for check in result["checks"]:
        item = check  # type: ignore[assignment]
        print(f"- {item['name']}: ok")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify Aegis Method Pack skill and project workspace support."
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("check", "helper-path", "activation-mode", "tdd-mode"),
        default="check",
        help="command to run; default is check",
    )
    parser.add_argument("mode", nargs="?", help="mode for activation-mode or tdd-mode commands")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--config", help="config path; defaults to ~/.config/aegis/config.toml")
    parser.add_argument(
        "--discovery-root",
        help="optional host skill discovery directory; verifies canonical or direct-child exposure",
    )
    parser.add_argument(
        "--discovery-name-prefix",
        default="",
        help="optional direct-child skill directory name prefix, such as aegis-",
    )
    parser.add_argument(
        "--write-config",
        action="store_true",
        help="write method_pack_root and workspace_helper into the config path",
    )
    parser.add_argument(
        "--host-profile",
        choices=(KIMI_AUTO_PROFILE, KIMI_EXPLICIT_PROFILE),
        help="optional host-native verification profile",
    )
    parser.add_argument(
        "--no-agents-md",
        action="store_true",
        help="skip Codex AGENTS.md routing-block management in activation-mode (config only)",
    )
    parser.add_argument(
        "--kimi-home",
        help="Kimi data root; defaults to KIMI_CODE_HOME or ~/.kimi-code",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "helper-path":
            if args.mode:
                raise DoctorError("mode is only valid with activation-mode or tdd-mode commands")
            result = helper_path_result(args)
        elif args.command == "activation-mode":
            result = activation_mode_result(args)
        elif args.command == "tdd-mode":
            result = tdd_mode_result(args)
        else:
            if args.mode:
                raise DoctorError("mode is only valid with activation-mode or tdd-mode commands")
            result = perform_check(args)
    except DoctorError as exc:
        failure = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(failure, indent=2, ensure_ascii=False))
        else:
            print(f"Aegis doctor check failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
