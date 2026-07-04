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
    write_config(config_path, root, helper, mode)
    return {
        "ok": True,
        "command": "activation-mode",
        "activationMode": mode,
        "configPath": config_path.as_posix(),
        "methodPackRoot": root.as_posix(),
        "workspaceHelper": helper.as_posix(),
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
