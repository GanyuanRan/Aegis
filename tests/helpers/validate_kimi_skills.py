#!/usr/bin/env python3
"""Validate the portable skill metadata contract consumed by Kimi Code."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


FIELD_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]*(.*))$")
WHEN_TO_USE_KEYS = {"whenToUse", "when-to-use", "when_to_use"}
DISABLE_MODEL_KEYS = {
    "disableModelInvocation",
    "disable-model-invocation",
    "disable_model_invocation",
}


def quoted_string(raw: str, *, path: Path, field: str, errors: list[str]) -> str | None:
    if not raw.startswith('"') or not raw.endswith('"'):
        errors.append(f"{path.as_posix()}: {field} must be a JSON-compatible double-quoted string")
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.as_posix()}: invalid {field} string: {exc.msg}")
        return None
    if not isinstance(value, str):
        errors.append(f"{path.as_posix()}: {field} must decode to a string")
        return None
    return value


def frontmatter_fields(path: Path, errors: list[str]) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{path.as_posix()}: missing opening frontmatter fence")
        return {}
    try:
        closing = lines.index("---", 1)
    except ValueError:
        errors.append(f"{path.as_posix()}: missing closing frontmatter fence")
        return {}

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line or line[0].isspace():
            continue
        match = FIELD_RE.fullmatch(line)
        if match is None:
            errors.append(f"{path.as_posix()}:{line_number}: invalid top-level frontmatter field")
            continue
        key, raw = match.groups()
        if key in fields:
            errors.append(f"{path.as_posix()}:{line_number}: duplicate frontmatter field {key}")
            continue
        fields[key] = raw
    return fields


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    fields = frontmatter_fields(path, errors)

    name = fields.get("name", "").strip()
    if not name:
        errors.append(f"{path.as_posix()}: name is required")
    elif name != path.parent.name:
        errors.append(
            f"{path.as_posix()}: name {name!r} must match directory {path.parent.name!r}"
        )

    raw_description = fields.get("description")
    if raw_description is None:
        errors.append(f"{path.as_posix()}: description is required")
    else:
        description = quoted_string(
            raw_description,
            path=path,
            field="description",
            errors=errors,
        )
        if description is not None:
            if "\n" in description or "\r" in description:
                errors.append(f"{path.as_posix()}: description must stay on one line")
            if not 1 <= len(description) <= 240:
                errors.append(
                    f"{path.as_posix()}: description length must be 1..240, got {len(description)}"
                )
            if not description.startswith("Use when"):
                errors.append(f"{path.as_posix()}: description must start with Use when")

    skill_type = fields.get("type", "prompt").strip().lower()
    if skill_type not in {"prompt", "inline"}:
        errors.append(f"{path.as_posix()}: type must remain model-invocable, got {skill_type!r}")

    for key in sorted(DISABLE_MODEL_KEYS.intersection(fields)):
        if fields[key].strip().lower() in {"true", "yes", "on", "1"}:
            errors.append(f"{path.as_posix()}: {key} must not disable model invocation")

    for key in sorted(WHEN_TO_USE_KEYS.intersection(fields)):
        value = quoted_string(fields[key], path=path, field=key, errors=errors)
        if value is not None and not value.strip():
            errors.append(f"{path.as_posix()}: {key} must not be empty")

    return errors


def validate(root: Path) -> list[str]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return [f"missing skills directory: {skills_root.as_posix()}"]
    paths = sorted(skills_root.glob("*/SKILL.md"))
    if not paths:
        return [f"no directory-form skills found under {skills_root.as_posix()}"]
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_skill(path))
    if not errors:
        print(f"  [PASS] {len(paths)} Kimi-visible skill metadata files are valid")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit("usage: validate_kimi_skills.py <repo-root>")
    errors = validate(Path(argv[1]).resolve())
    if errors:
        for error in errors:
            print(f"  [FAIL] {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
