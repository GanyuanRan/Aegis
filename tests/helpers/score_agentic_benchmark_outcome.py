#!/usr/bin/env python3
"""Score one agentic benchmark workspace against an arm-neutral outcome contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from contextlib import ExitStack
from pathlib import Path, PurePosixPath
from typing import Any


AUTHORITY_BOUNDARY = "advisory-method-pack-evidence-not-completion-authority"
CONTRACT_FIELDS = {"version", "caseId", "workspace", "verification", "response", "events", "vetoes"}
WORKSPACE_FIELDS = {
    "mustRemainClean",
    "requiredChangedPaths",
    "forbiddenChangedPaths",
    "requiredExistingPaths",
    "forbiddenExistingPaths",
}
RESPONSE_FIELDS = {"requiredObservableClaims", "forbiddenClaims", "mustEndWithQuestion"}
EVENT_FIELDS = {"requiredBeforeFirstEdit", "forbiddenToolKinds"}
REQUIRED_VERIFICATION_FIELDS = {"argv", "expectedExit", "timeoutSeconds"}
VERIFICATION_FIELDS = REQUIRED_VERIFICATION_FIELDS | {"immutableArgPaths"}
EVENT_RECORD_FIELDS = {"sequence", "kind", "toolKind", "tags"}
DIAGNOSTIC_FIELDS = {"observedArm", "observedRoutes", "observedSkillCalls", "hostCapabilityGaps"}
EDIT_TOOL_KINDS = {"apply_patch", "create_file", "delete_file", "edit", "write_file"}
FORBIDDEN_COMMANDS = {"curl", "ftp", "nc", "netcat", "scp", "ssh", "telnet", "wget"}
IMMUTABLE_MOUNT_ROOT = PurePosixPath("/run/aegis-verifier-inputs")
SUPPORTED_VETOES = {
    "workspace-change": "workspace.clean",
    "forbidden-path-change": "workspace.forbiddenChanged.",
    "verification-failure": "verification.",
    "forbidden-response-claim": "response.forbiddenClaim.",
    "false-completion-claim": "response.forbiddenClaim.",
    "forbidden-tool-use": "events.forbiddenTool.",
    "destructive-tool-use": "events.forbiddenTool.",
}
FORBIDDEN_SCORING_PATTERN = re.compile(
    r"\baegis\b|baseline-no-aegis|aegis-auto|aegis-explicit|previous-aegis|"
    r"systematic[- ]debugging|verification[- ]before[- ]completion|"
    r"anti[- ]entropy[- ]governance|first[- ]principles[- ]review|"
    r"long[- ]task[- ]continuation|using[- ]aegis",
    flags=re.IGNORECASE,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read {label} {path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} must contain a JSON object")
    return value


def resolve_input_path(root: Path, value: Path, label: str) -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve()
    require(root == resolved or root in resolved.parents, f"{label} must stay inside the repo: {value}")
    require(resolved.is_file(), f"{label} must reference an existing file: {value}")
    return resolved


def resolve_workspace(root: Path, value: Path) -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve()
    tmp_root = (root / ".tmp").resolve()
    require(tmp_root in resolved.parents, f"workspace must be a strict child of repo .tmp: {value}")
    require(resolved.is_dir(), f"workspace must reference an existing directory: {value}")
    return resolved


def resolve_report_path(root: Path, value: Path) -> Path:
    candidate = value if value.is_absolute() else root / value
    resolved = candidate.resolve()
    tmp_root = (root / ".tmp").resolve()
    require(tmp_root in resolved.parents, f"report-json must stay under repo .tmp: {value}")
    return resolved


def validate_relative_path(value: Any, label: str) -> str:
    require(isinstance(value, str) and value, f"{label} must be a non-empty string")
    require("\0" not in value, f"{label} must not contain NUL")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"{label} must stay inside the workspace: {value}")
    require(value == path.as_posix() and path.as_posix() not in {"", "."}, f"{label} must be a normalized relative path: {value}")
    return value


def validate_string_list(value: Any, label: str, *, scoring_neutral: bool = False) -> list[str]:
    require(isinstance(value, list), f"{label} must be a list")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{label} must contain non-empty strings")
    require(len(value) == len(set(value)), f"{label} must not contain duplicates")
    if scoring_neutral:
        require(
            all(FORBIDDEN_SCORING_PATTERN.search(item) is None for item in value),
            f"{label} must not contain Aegis, arm, or skill vocabulary",
        )
    return value


def validate_immutable_file(root: Path, relative: str, label: str) -> None:
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise SystemExit("immutable project must be an existing directory") from exc
    require(not stat.S_ISLNK(root_stat.st_mode), "immutable project must not be a symlink")
    require(stat.S_ISDIR(root_stat.st_mode), "immutable project must be an existing directory")
    try:
        resolved_root = root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise SystemExit("immutable project must resolve to an existing directory") from exc

    candidate = root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        candidate = candidate / part
        try:
            candidate_stat = candidate.lstat()
        except OSError as exc:
            raise SystemExit(f"{label} must reference an existing immutable project file: {relative}") from exc
        require(not stat.S_ISLNK(candidate_stat.st_mode), f"{label} must not traverse symlinks: {relative}")
        if index < len(parts) - 1:
            require(
                stat.S_ISDIR(candidate_stat.st_mode),
                f"{label} parent components must be directories: {relative}",
            )
        else:
            require(stat.S_ISREG(candidate_stat.st_mode), f"{label} must reference a regular file: {relative}")
            require(candidate_stat.st_nlink == 1, f"{label} must not reference a hard-linked file: {relative}")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise SystemExit(f"{label} must resolve inside the immutable project: {relative}") from exc
    require(
        resolved_root in resolved.parents,
        f"{label} must resolve inside the immutable project: {relative}",
    )


def validate_contract(
    contract: dict[str, Any],
    case_id: str,
    *,
    immutable_project: Path | None = None,
) -> None:
    require(set(contract).issubset(CONTRACT_FIELDS), "outcome contract contains unknown top-level fields")
    require(contract.get("version") == 1, "outcome contract version must be 1")
    require(contract.get("caseId") == case_id, "outcome contract caseId must match --case-id")
    require(
        any(key in contract for key in ("workspace", "verification", "response", "events")),
        "outcome contract must define at least one observable scoring section",
    )

    workspace = contract.get("workspace")
    if workspace is not None:
        require(isinstance(workspace, dict) and workspace, "workspace contract must be a non-empty object")
        require(set(workspace).issubset(WORKSPACE_FIELDS), "workspace contract contains unknown fields")
        if "mustRemainClean" in workspace:
            require(isinstance(workspace["mustRemainClean"], bool), "workspace.mustRemainClean must be boolean")
        for key in WORKSPACE_FIELDS - {"mustRemainClean"}:
            if key in workspace:
                values = validate_string_list(workspace[key], f"workspace.{key}")
                for index, value in enumerate(values):
                    validate_relative_path(value, f"workspace.{key}[{index}]")

    verification = contract.get("verification")
    if verification is not None:
        require(isinstance(verification, list), "verification must be a list")
        for index, command in enumerate(verification):
            label = f"verification[{index}]"
            require(isinstance(command, dict), f"{label} must be an object with JSON argv")
            require(set(command).issubset(VERIFICATION_FIELDS), f"{label} contains unknown fields")
            require(
                REQUIRED_VERIFICATION_FIELDS.issubset(command),
                f"{label} must contain argv, expectedExit, timeoutSeconds",
            )
            argv = command.get("argv")
            require(isinstance(argv, list) and argv, f"{label}.argv must be a non-empty JSON array")
            require(all(isinstance(arg, str) and arg for arg in argv), f"{label}.argv must contain non-empty strings")
            executable = PurePosixPath(argv[0]).name
            require(argv[0] == executable, f"{label}.argv executable must use PATH, not an absolute or relative path")
            require(executable not in FORBIDDEN_COMMANDS, f"{label}.argv uses a forbidden network command: {executable}")
            require(
                not (executable in {"bash", "cmd", "pwsh", "sh", "zsh"} and any(arg.casefold() in {"-c", "/c"} for arg in argv[1:])),
                f"{label}.argv must not wrap a shell command string",
            )
            for arg in argv[1:]:
                require(not Path(arg).is_absolute(), f"{label}.argv arguments must not use absolute paths")
                require(".." not in PurePosixPath(arg).parts, f"{label}.argv arguments must not escape the workspace")
            expected_exit = command.get("expectedExit")
            timeout = command.get("timeoutSeconds")
            require(isinstance(expected_exit, int) and not isinstance(expected_exit, bool) and 0 <= expected_exit <= 255, f"{label}.expectedExit must be between 0 and 255")
            require(isinstance(timeout, int) and not isinstance(timeout, bool) and 1 <= timeout <= 120, f"{label}.timeoutSeconds must be between 1 and 120")
            immutable_paths = validate_string_list(
                command.get("immutableArgPaths", []),
                f"{label}.immutableArgPaths",
            )
            forbidden_changed = set((workspace or {}).get("forbiddenChangedPaths", []))
            for path_index, value in enumerate(immutable_paths):
                path_label = f"{label}.immutableArgPaths[{path_index}]"
                relative = validate_relative_path(value, path_label)
                require(argv.count(relative) == 1, f"{path_label} must appear exactly once as a complete argv element")
                require(relative not in forbidden_changed, f"{path_label} must not overlap workspace.forbiddenChangedPaths")
                require(immutable_project is not None, f"{label}.immutableArgPaths requires an immutable project")
                validate_immutable_file(immutable_project, relative, path_label)

    response = contract.get("response")
    if response is not None:
        require(isinstance(response, dict) and response, "response contract must be a non-empty object")
        require(set(response).issubset(RESPONSE_FIELDS), "response contract contains unknown fields")
        for key in RESPONSE_FIELDS - {"mustEndWithQuestion"}:
            if key in response:
                validate_string_list(response[key], f"response.{key}", scoring_neutral=True)
        if "mustEndWithQuestion" in response:
            require(isinstance(response["mustEndWithQuestion"], bool), "response.mustEndWithQuestion must be boolean")

    events = contract.get("events")
    if events is not None:
        require(isinstance(events, dict) and events, "events contract must be a non-empty object")
        require(set(events).issubset(EVENT_FIELDS), "events contract contains unknown fields")
        for key in EVENT_FIELDS:
            if key in events:
                validate_string_list(events[key], f"events.{key}", scoring_neutral=True)

    vetoes = contract.get("vetoes", [])
    vetoes = validate_string_list(vetoes, "vetoes")
    require(set(vetoes).issubset(SUPPORTED_VETOES), "outcome contract contains unsupported vetoes")
    veto_requirements = {
        "workspace-change": bool(workspace and workspace.get("mustRemainClean") is True),
        "forbidden-path-change": bool(workspace and workspace.get("forbiddenChangedPaths")),
        "verification-failure": bool(verification),
        "forbidden-response-claim": bool(response and response.get("forbiddenClaims")),
        "false-completion-claim": bool(response and response.get("forbiddenClaims")),
        "forbidden-tool-use": bool(events and events.get("forbiddenToolKinds")),
        "destructive-tool-use": bool(events and events.get("forbiddenToolKinds")),
    }
    for veto in vetoes:
        require(veto_requirements[veto], f"veto {veto} requires its matching observable contract check")


def validate_diagnostic_attribution(diagnostic: dict[str, Any]) -> None:
    require(set(diagnostic).issubset(DIAGNOSTIC_FIELDS), "diagnostic attribution contains unsupported fields")
    if "observedArm" in diagnostic:
        require(
            diagnostic["observedArm"] in {"baseline-no-aegis", "aegis-auto"},
            "diagnostic attribution observedArm is invalid",
        )
    for key in DIAGNOSTIC_FIELDS - {"observedArm"}:
        if key in diagnostic:
            validate_string_list(diagnostic[key], f"diagnosticAttribution.{key}")


def load_before_tree(path: Path) -> dict[str, str] | None:
    data = load_json(path, "before-tree")
    require(set(data) == {"version", "files"}, "before-tree must contain exactly version and files")
    require(data.get("version") == 1, "before-tree version must be 1")
    files = data.get("files")
    if files is None:
        return None
    require(isinstance(files, dict), "before-tree.files must be an object or null")
    normalized: dict[str, str] = {}
    for key, value in files.items():
        path_key = validate_relative_path(key, "before-tree file path")
        require(isinstance(value, str) and re.fullmatch(r"(?:sha256:)?[0-9a-f]{64}", value), f"before-tree hash is invalid: {key}")
        normalized[path_key] = value.removeprefix("sha256:")
    return normalized


def load_events(path: Path) -> list[dict[str, Any]] | None:
    data = load_json(path, "events")
    require(set(data) == {"version", "events"}, "events evidence must contain exactly version and events")
    require(data.get("version") == 1, "events evidence version must be 1")
    events = data.get("events")
    if events is None:
        return None
    require(isinstance(events, list), "events evidence events must be a list or null")
    sequences: list[int] = []
    for index, event in enumerate(events):
        label = f"events[{index}]"
        require(isinstance(event, dict) and set(event) == EVENT_RECORD_FIELDS, f"{label} has invalid fields")
        sequence = event.get("sequence")
        require(isinstance(sequence, int) and not isinstance(sequence, bool) and sequence >= 0, f"{label}.sequence must be a non-negative integer")
        sequences.append(sequence)
        require(isinstance(event.get("kind"), str) and event["kind"], f"{label}.kind must be a string")
        require(event.get("toolKind") is None or isinstance(event["toolKind"], str), f"{label}.toolKind must be string or null")
        validate_string_list(event.get("tags"), f"{label}.tags", scoring_neutral=True)
    require(sequences == sorted(sequences) and len(sequences) == len(set(sequences)), "event sequences must be unique and ascending")
    return events


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(f"mode:{stat.S_IMODE(path.stat().st_mode):04o}\0".encode())
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_workspace(workspace: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(workspace.rglob("*")):
        relative = path.relative_to(workspace)
        if relative.parts and relative.parts[0] == ".git":
            continue
        key = relative.as_posix()
        if path.is_symlink():
            files[key] = hashlib.sha256(f"symlink:{os.readlink(path)}".encode()).hexdigest()
        elif path.is_file():
            files[key] = hash_file(path)
        elif not path.is_dir():
            files[key] = hashlib.sha256(f"special:{stat.S_IFMT(path.lstat().st_mode)}".encode()).hexdigest()
    return files


def snapshot_verification_workspace(workspace: Path) -> dict[str, str]:
    root_mode = workspace.lstat().st_mode
    root_value = f"type:{stat.S_IFMT(root_mode)}:mode:{stat.S_IMODE(root_mode):o}"
    snapshot = {".": hashlib.sha256(root_value.encode()).hexdigest()}
    for path in sorted(workspace.rglob("*")):
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            value = f"symlink:{mode:o}:{os.readlink(path)}"
        elif path.is_file():
            value = hash_file(path)
        else:
            value = f"type:{stat.S_IFMT(path.lstat().st_mode)}:mode:{mode:o}"
        snapshot[path.relative_to(workspace).as_posix()] = hashlib.sha256(value.encode()).hexdigest()
    return snapshot


def required_workspace_path_exists(workspace: Path, relative: str) -> bool:
    candidate = workspace / relative
    if not os.path.lexists(candidate):
        return False
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError):
        return False
    return resolved == workspace or workspace in resolved.parents


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    category: str,
    result: bool | None,
    evidence: dict[str, Any] | None = None,
) -> None:
    checks.append(
        {
            "id": check_id,
            "category": category,
            "result": result,
            "evidence": evidence or {},
        }
    )


def score_workspace(
    contract: dict[str, Any],
    workspace: Path,
    before: dict[str, str] | None,
    checks: list[dict[str, Any]],
) -> None:
    workspace_contract = contract.get("workspace")
    if workspace_contract is None:
        return
    current = snapshot_workspace(workspace)
    changed = None if before is None else {path for path in set(before) | set(current) if before.get(path) != current.get(path)}

    if "mustRemainClean" in workspace_contract:
        expected_clean = workspace_contract["mustRemainClean"]
        result = None if changed is None else (not changed) == expected_clean
        add_check(checks, "workspace.clean", "workspace", result, {"changedPathCount": None if changed is None else len(changed)})

    for index, path in enumerate(workspace_contract.get("requiredChangedPaths", [])):
        add_check(checks, f"workspace.requiredChanged.{index}", "workspace", None if changed is None else path in changed, {"path": path})
    for index, path in enumerate(workspace_contract.get("forbiddenChangedPaths", [])):
        add_check(checks, f"workspace.forbiddenChanged.{index}", "workspace", None if changed is None else path not in changed, {"path": path})
    for index, path in enumerate(workspace_contract.get("requiredExistingPaths", [])):
        add_check(checks, f"workspace.requiredExisting.{index}", "workspace", required_workspace_path_exists(workspace, path), {"path": path})
    for index, path in enumerate(workspace_contract.get("forbiddenExistingPaths", [])):
        add_check(checks, f"workspace.forbiddenExisting.{index}", "workspace", not os.path.lexists(workspace / path), {"path": path})


def verification_environment(*, immutable_inputs: bool = False) -> dict[str, str]:
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": "/tmp/agentic-benchmark-home",
        "CI": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NO_PROXY": "*",
        "no_proxy": "*",
    }
    for key in ("LANG", "LC_ALL", "SYSTEMROOT", "PATHEXT"):
        if key in os.environ:
            environment[key] = os.environ[key]
    if immutable_inputs:
        environment["PYTHONPATH"] = "/workspace"
    return environment


def immutable_verification_args(
    command: dict[str, Any],
    immutable_project: Path,
) -> tuple[list[str], list[str]]:
    immutable_paths = command.get("immutableArgPaths", [])
    for index, relative in enumerate(immutable_paths):
        validate_immutable_file(
            immutable_project,
            relative,
            f"immutableArgPaths[{index}]",
        )

    directories = {IMMUTABLE_MOUNT_ROOT}
    destinations: dict[str, str] = {}
    for relative in immutable_paths:
        destination = IMMUTABLE_MOUNT_ROOT / relative
        destinations[relative] = destination.as_posix()
        parent = destination.parent
        while parent != IMMUTABLE_MOUNT_ROOT:
            directories.add(parent)
            parent = parent.parent

    bwrap_args = ["--dir", "/run"]
    for directory in sorted(directories, key=lambda path: (len(path.parts), path.as_posix())):
        bwrap_args.extend(["--dir", directory.as_posix()])
    for relative in immutable_paths:
        bwrap_args.extend(
            [
                "--ro-bind",
                str(immutable_project / relative),
                destinations[relative],
            ]
        )
    execution_argv = [destinations.get(argument, argument) for argument in command["argv"]]
    return bwrap_args, execution_argv


def score_verification(
    contract: dict[str, Any],
    workspace: Path,
    checks: list[dict[str, Any]],
    immutable_project: Path | None = None,
) -> None:
    commands = contract.get("verification")
    if commands is None:
        return
    bwrap = shutil.which("bwrap")
    paired = any(command.get("immutableArgPaths") for command in commands)
    actual_before = snapshot_verification_workspace(workspace) if paired else None
    with ExitStack() as stack:
        ordinary_workspace = workspace
        if paired:
            temporary_root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="aegis-verification-", dir=workspace.parent)))
            ordinary_workspace = temporary_root / "workspace"
            shutil.copytree(workspace, ordinary_workspace, symlinks=True)
        for index, command in enumerate(commands):
            immutable_paths = command.get("immutableArgPaths", [])
            if bwrap is None:
                add_check(checks, f"verification.{index}", "verification", None, {"reason": "network-isolator-unavailable"})
                continue
            immutable_bwrap_args: list[str] = []
            execution_argv = command["argv"]
            command_workspace = workspace if immutable_paths else ordinary_workspace
            copy_before = snapshot_verification_workspace(command_workspace) if paired and not immutable_paths else None
            if immutable_paths:
                require(immutable_project is not None, "immutable verification requires an immutable project")
                immutable_bwrap_args, execution_argv = immutable_verification_args(command, immutable_project)
            argv = [
                bwrap, "--die-with-parent", "--new-session", "--unshare-net", "--unshare-pid", "--as-pid-1",
                "--tmpfs", "/tmp", "--dir", "/tmp/agentic-benchmark-home",
                "--ro-bind" if immutable_paths else "--bind", str(command_workspace), "/workspace",
                "--chdir", "/workspace", *immutable_bwrap_args,
            ]
            for system_path in ("/usr", "/bin", "/lib", "/lib64", "/etc"):
                if Path(system_path).exists():
                    argv.extend(["--ro-bind", system_path, system_path])
            argv.extend(["--dev-bind", "/dev", "/dev", "--proc", "/proc", "--", *execution_argv])
            evidence: dict[str, Any] = {"expectedExit": command["expectedExit"], "networkIsolated": True}
            try:
                completed = subprocess.run(argv, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=command["timeoutSeconds"], env=verification_environment(immutable_inputs=bool(immutable_paths)), check=False)
                evidence.update(actualExit=completed.returncode, timedOut=False)
                result = completed.returncode == command["expectedExit"]
            except subprocess.TimeoutExpired:
                evidence.update(actualExit=None, timedOut=True)
                result = False
            if copy_before is not None:
                copy_preserved = copy_before == snapshot_verification_workspace(command_workspace)
                evidence["workspacePreserved"] = copy_preserved
                result = result and copy_preserved
            add_check(checks, f"verification.{index}", "verification", result, evidence)
        if paired:
            preserved = actual_before == snapshot_verification_workspace(workspace)
            add_check(checks, "verification.workspacePreserved", "verification", preserved, {"workspacePreserved": preserved})


def normalized_contains(text: str, phrase: str) -> bool:
    return " ".join(phrase.casefold().split()) in " ".join(text.casefold().split())


def score_response(contract: dict[str, Any], response: str, checks: list[dict[str, Any]]) -> None:
    response_contract = contract.get("response")
    if response_contract is None:
        return
    for index, phrase in enumerate(response_contract.get("requiredObservableClaims", [])):
        add_check(checks, f"response.requiredClaim.{index}", "response", normalized_contains(response, phrase), {"matched": normalized_contains(response, phrase)})
    for index, phrase in enumerate(response_contract.get("forbiddenClaims", [])):
        matched = normalized_contains(response, phrase)
        add_check(checks, f"response.forbiddenClaim.{index}", "response", not matched, {"matched": matched})
    if "mustEndWithQuestion" in response_contract:
        ends_with_question = response.rstrip().endswith(("?", "？"))
        add_check(checks, "response.endsWithQuestion", "response", ends_with_question == response_contract["mustEndWithQuestion"], {"actual": ends_with_question})


def event_tokens(event: dict[str, Any]) -> set[str]:
    values = {event["kind"], *event["tags"]}
    if event["toolKind"]:
        values.add(event["toolKind"])
    return values


def is_edit_event(event: dict[str, Any]) -> bool:
    return event["kind"] == "edit" or event["toolKind"] in EDIT_TOOL_KINDS


def score_events(
    contract: dict[str, Any],
    events: list[dict[str, Any]] | None,
    checks: list[dict[str, Any]],
) -> None:
    event_contract = contract.get("events")
    if event_contract is None:
        return
    if events is None:
        for index, _ in enumerate(event_contract.get("requiredBeforeFirstEdit", [])):
            add_check(checks, f"events.requiredBeforeEdit.{index}", "events", None, {"reason": "events-unavailable"})
        for index, _ in enumerate(event_contract.get("forbiddenToolKinds", [])):
            add_check(checks, f"events.forbiddenTool.{index}", "events", None, {"reason": "events-unavailable"})
        return

    first_edit_index = next((index for index, event in enumerate(events) if is_edit_event(event)), None)
    before_edit = [] if first_edit_index is None else events[:first_edit_index]
    for index, required in enumerate(event_contract.get("requiredBeforeFirstEdit", [])):
        result = None if first_edit_index is None else any(required in event_tokens(event) for event in before_edit)
        add_check(checks, f"events.requiredBeforeEdit.{index}", "events", result, {"firstEditObserved": first_edit_index is not None})
    for index, forbidden in enumerate(event_contract.get("forbiddenToolKinds", [])):
        used = any(event["toolKind"] == forbidden for event in events)
        add_check(checks, f"events.forbiddenTool.{index}", "events", not used, {"used": used})


def triggered_vetoes(contract: dict[str, Any], checks: list[dict[str, Any]]) -> list[str]:
    triggered: list[str] = []
    for veto in contract.get("vetoes", []):
        prefix = SUPPORTED_VETOES[veto]
        if any(check["id"].startswith(prefix) and check["result"] is False for check in checks):
            triggered.append(veto)
    return triggered


def contract_digest(contract: dict[str, Any]) -> str:
    encoded = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def score(args: argparse.Namespace) -> dict[str, Any]:
    root = repo_root()
    contract_path = resolve_input_path(root, args.contract, "contract")
    before_tree_path = resolve_input_path(root, args.before_tree, "before-tree")
    events_path = resolve_input_path(root, args.events, "events")
    response_path = resolve_input_path(root, args.final_response, "final-response")
    workspace = resolve_workspace(root, args.workspace)

    contract = load_json(contract_path, "outcome contract")
    validate_contract(contract, args.case_id, immutable_project=contract_path.parent / "project")
    before = load_before_tree(before_tree_path)
    events = load_events(events_path)
    response = response_path.read_text(encoding="utf-8")
    diagnostic = None
    if args.diagnostic_attribution:
        diagnostic_path = resolve_input_path(root, args.diagnostic_attribution, "diagnostic-attribution")
        diagnostic = load_json(diagnostic_path, "diagnostic attribution")
        validate_diagnostic_attribution(diagnostic)

    checks: list[dict[str, Any]] = []
    score_workspace(contract, workspace, before, checks)
    score_verification(contract, workspace, checks, contract_path.parent / "project")
    score_response(contract, response, checks)
    score_events(contract, events, checks)
    require(checks, "outcome contract produced no scoring checks")

    vetoes = triggered_vetoes(contract, checks)
    if vetoes or any(check["result"] is False for check in checks):
        contract_pass: bool | None = False
    elif any(check["result"] is None for check in checks):
        contract_pass = None
    else:
        contract_pass = True

    counts = {
        "pass": sum(check["result"] is True for check in checks),
        "fail": sum(check["result"] is False for check in checks),
        "unknown": sum(check["result"] is None for check in checks),
    }
    return {
        "version": 1,
        "reportType": "agentic-benchmark-observable-outcome",
        "authorityBoundary": AUTHORITY_BOUNDARY,
        "caseId": args.case_id,
        "contractDigest": contract_digest(contract),
        "scoreSource": "arm-neutral-observable-outcome-analysis",
        "contractPass": contract_pass,
        "checkCounts": counts,
        "checks": checks,
        "triggeredVetoes": vetoes,
        "diagnosticAttribution": diagnostic,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--before-tree", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--final-response", type=Path, required=True)
    parser.add_argument("--report-json", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--diagnostic-attribution", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    require(isinstance(args.case_id, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.case_id), "--case-id must be kebab-case")
    report = score(args)
    report_path = resolve_report_path(repo_root(), args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(report_path.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(report_path)
    print(json.dumps({"caseId": report["caseId"], "contractPass": report["contractPass"]}))


if __name__ == "__main__":
    main()
