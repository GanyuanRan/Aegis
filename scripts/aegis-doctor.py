#!/usr/bin/env python3
"""Verify an installed Aegis Method Pack.

The doctor checks skill discovery surfaces and project workspace support without
writing a live docs/aegis workspace into the Aegis Method Pack repository.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


KEY_SKILLS = (
    "using-aegis",
    "first-principles-review",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "verification-before-completion",
)

STALE_USING_AEGIS_PATTERNS = (
    "brainstorming item 8",
    "If `docs/aegis/` missing → create now",
)

REQUIRED_USING_AEGIS_PATTERNS = (
    "Spec Brief or Design Spec only",
    "Workspace support is lazy",
    "configured Aegis workspace support",
)


class DoctorError(Exception):
    pass


def default_config_path() -> Path:
    return Path.home() / ".config" / "aegis" / "config.toml"


def method_pack_root() -> Path:
    return Path(__file__).resolve().parent.parent


def toml_string(value: str) -> str:
    return json.dumps(value)


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


def write_config(path: Path, root: Path, helper: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "# Aegis user-local configuration\n"
        'activation_mode = "auto"\n'
        f"method_pack_root = {toml_string(root.as_posix())}\n"
        f"workspace_helper = {toml_string(helper.as_posix())}\n"
    )
    path.write_text(content, encoding="utf-8", newline="\n")


def config_status(path: Path, root: Path, helper: Path) -> str:
    config = read_config(path)
    if not config:
        return "missing"
    if (
        config.get("activation_mode") in {"auto", "explicit"}
        and Path(config.get("method_pack_root", "")).expanduser() == root
        and Path(config.get("workspace_helper", "")).expanduser() == helper
    ):
        return "configured"
    return "partial"


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
        check_discovery_root(discovery_root, skills)
        checks.append(
            {
                "name": "discovery-root-current",
                "ok": True,
                "detail": str(discovery_root),
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

    return {
        "ok": True,
        "methodPackRoot": root.as_posix(),
        "workspaceSupport": "available",
        "configPath": config_path.as_posix(),
        "configStatus": status,
        "checks": checks,
    }


def print_text(result: dict[str, object]) -> None:
    print("Aegis doctor check passed.")
    print(f"Method pack root: {result['methodPackRoot']}")
    print(f"Project workspace support: {result['workspaceSupport']}")
    print(f"Config status: {result['configStatus']} ({result['configPath']})")
    for check in result["checks"]:
        item = check  # type: ignore[assignment]
        print(f"- {item['name']}: ok")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify Aegis Method Pack skill and project workspace support."
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--config", help="config path; defaults to ~/.config/aegis/config.toml")
    parser.add_argument(
        "--discovery-root",
        help="optional host skill discovery directory; must resolve to this method pack's skills directory",
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
