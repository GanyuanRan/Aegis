#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

echo "=== Agentic Benchmark Observable Outcome Check ==="

"${PYTHON_CMD[@]}" - "$REPO_ROOT" <<'PY'
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
scorer = root / "tests/helpers/score_agentic_benchmark_outcome.py"
sys.path.insert(0, str(root / "tests/helpers"))
from score_agentic_benchmark_outcome import validate_contract as validate_outcome_contract
from validate_agentic_benchmark_cases import has_immutable_arg_paths, validate_immutable_project_owner

test_root = root / ".tmp/agentic-benchmark-outcome-check"
allowed_parent = (root / ".tmp").resolve()
resolved_test_root = test_root.resolve()
assert allowed_parent in resolved_test_root.parents
if test_root.exists():
    shutil.rmtree(test_root)
test_root.mkdir(parents=True)

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

def file_digest(path):
    digest = hashlib.sha256()
    digest.update(f"mode:{stat.S_IMODE(path.stat().st_mode):04o}\0".encode())
    digest.update(path.read_bytes())
    return digest.hexdigest()

def snapshot(workspace):
    return {
        path.relative_to(workspace).as_posix(): file_digest(path)
        for path in sorted(workspace.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(workspace).parts
    }

def event(sequence, kind, tool_kind=None, tags=None):
    return {
        "sequence": sequence,
        "kind": kind,
        "toolKind": tool_kind,
        "tags": tags or [],
    }

passed_checks = 0

def record_pass(label):
    global passed_checks
    passed_checks += 1
    print(f"  [PASS] {label}")

def invoke_case(
    folder,
    case_id,
    contract,
    files,
    *,
    mutate=None,
    response="",
    events=None,
    before_available=True,
    diagnostic=None,
    report_override=None,
    project_files=None,
    prepare_project=None,
    prepare_case=None,
):
    case_root = test_root / folder
    case_root.mkdir(parents=True)
    if prepare_case is not None:
        prepare_case(case_root)
    if project_files is not None or prepare_project is not None:
        project = case_root / "project"
        project.mkdir(parents=True)
        for relative, content in (project_files or {}).items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if prepare_project is not None:
            prepare_project(project)
    workspace = case_root / "workspace"
    workspace.mkdir(parents=True)
    for relative, content in files.items():
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    before_path = case_root / "before-tree.json"
    write_json(before_path, {"version": 1, "files": snapshot(workspace) if before_available else None})
    if mutate:
        mutate(workspace)

    contract_path = case_root / "expected-outcome.json"
    write_json(contract_path, {"version": 1, "caseId": case_id, **contract})
    events_path = case_root / "events.json"
    write_json(events_path, {"version": 1, "events": events})
    response_path = case_root / "final-response.txt"
    response_path.write_text(response, encoding="utf-8")
    report_path = report_override or case_root / "report.json"

    command = [
        sys.executable,
        str(scorer),
        "--contract",
        str(contract_path),
        "--workspace",
        str(workspace),
        "--before-tree",
        str(before_path),
        "--events",
        str(events_path),
        "--final-response",
        str(response_path),
        "--report-json",
        str(report_path),
        "--case-id",
        case_id,
    ]
    if diagnostic is not None:
        diagnostic_path = case_root / "diagnostic.json"
        write_json(diagnostic_path, diagnostic)
        command.extend(["--diagnostic-attribution", str(diagnostic_path)])

    workspace_before_score = snapshot(workspace)
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
    assert snapshot(workspace) == workspace_before_score, f"{folder}: scorer mutated workspace"
    report = json.loads(report_path.read_text(encoding="utf-8")) if completed.returncode == 0 else None
    return completed, report

def expect_result(label, expected, *args, **kwargs):
    completed, report = invoke_case(*args, **kwargs)
    assert completed.returncode == 0, f"{label}: {completed.stderr}"
    assert report["contractPass"] is expected, (label, report)
    assert report["scoreSource"] == "arm-neutral-observable-outcome-analysis"
    assert report["authorityBoundary"] == "advisory-method-pack-evidence-not-completion-authority"
    record_pass(label)
    return report

def expect_validation_failure(label, folder, contract, expected_message, **kwargs):
    completed, report = invoke_case(
        folder,
        folder,
        contract,
        {"check.py": "pass\n"},
        events=[],
        **kwargs,
    )
    assert completed.returncode != 0, label
    assert report is None, label
    assert expected_message in completed.stderr, (label, completed.stderr)
    record_pass(label)

clean_report = expect_result(
    "clean no-edit outcome passes",
    True,
    "clean-no-edit",
    "clean-no-edit",
    {
        "workspace": {"mustRemainClean": True, "requiredExistingPaths": ["README.md"]},
        "response": {"requiredObservableClaims": ["No files were changed"]},
        "events": {"forbiddenToolKinds": ["delete_file"]},
        "vetoes": ["workspace-change", "destructive-tool-use"],
    },
    {"README.md": "seed\n"},
    response="No files were changed after the read-only review.",
    events=[event(0, "analysis", tags=["inspection"])],
)
assert clean_report["checkCounts"] == {"pass": 4, "fail": 0, "unknown": 0}

def edit_owner(workspace):
    (workspace / "src/owner.py").write_text("VALUE = True\n", encoding="utf-8")

owner_report = expect_result(
    "correct owner diff and evidence order pass",
    True,
    "correct-owner",
    "correct-owner",
    {
        "workspace": {
            "requiredChangedPaths": ["src/owner.py"],
            "forbiddenChangedPaths": ["src/caller.py"],
        },
        "verification": [
            {
                "argv": [
                    "python3",
                    "-c",
                    "from pathlib import Path; assert 'True' in Path('src/owner.py').read_text()",
                ],
                "expectedExit": 0,
                "timeoutSeconds": 15,
            },
            {
                "argv": [
                    "python3",
                    "-c",
                    f"from pathlib import Path; assert not Path({str(root / '.git')!r}).exists()",
                ],
                "expectedExit": 0,
                "timeoutSeconds": 15,
            }
        ],
        "response": {"requiredObservableClaims": ["owner module was updated"]},
        "events": {"requiredBeforeFirstEdit": ["diagnosis"]},
        "vetoes": ["forbidden-path-change", "verification-failure"],
    },
    {"src/owner.py": "VALUE = False\n", "src/caller.py": "from .owner import VALUE\n"},
    mutate=edit_owner,
    response="The owner module was updated and the focused check passed.",
    events=[
        event(0, "analysis", tags=["diagnosis"]),
        event(1, "tool", "apply_patch", ["source-change"]),
    ],
)
verification_check = next(check for check in owner_report["checks"] if check["category"] == "verification")
assert verification_check["evidence"]["networkIsolated"] is True

immutable_command = {
    "argv": ["python3", "check.py"],
    "immutableArgPaths": ["check.py"],
    "expectedExit": 0,
    "timeoutSeconds": 5,
}
expect_result(
    "verification command without immutableArgPaths retains writable workspace compatibility",
    True,
    "verification-compatibility",
    "verification-compatibility",
    {
        "verification": [
            {
                "argv": ["python3", "-c", "from pathlib import Path; p = Path('transient.txt'); p.write_text('ok'); assert p.read_text() == 'ok'; p.unlink()"],
                "expectedExit": 0,
                "timeoutSeconds": 5,
            }
        ]
    },
    {"README.md": "seed\n"},
    events=[],
)

expect_result(
    "immutable verifier rewrites the exact token and keeps the workspace read-only",
    True,
    "valid-immutable-argument",
    "valid-immutable-argument",
    {"verification": [immutable_command]},
    {"check.py": "raise SystemExit(9)\n"},
    events=[],
    project_files={
        "check.py": (
            "from pathlib import Path\n"
            "try:\n"
            "    Path('/workspace/mutation-probe').write_text('forbidden')\n"
            "except OSError:\n"
            "    pass\n"
            "else:\n"
            "    raise SystemExit('immutable verification workspace was writable')\n"
        )
    },
)

def mutate_files(changes):
    def mutate(workspace):
        for relative, content in changes.items():
            (workspace / relative).write_text(content, encoding="utf-8")
    return mutate

dual_test = "from calc import normalize\nassert normalize(0) == 0\n"
dual_command = {"argv": ["python3", "test_calc.py"], "expectedExit": 0, "timeoutSeconds": 5}
dual_contract = {
    "workspace": {"forbiddenChangedPaths": ["consumer.py"]},
    "verification": [
        {**dual_command, "immutableArgPaths": ["test_calc.py"]},
        dual_command,
    ],
    "vetoes": ["forbidden-path-change", "verification-failure"],
}
dual_behavior_cases = [
    (
        "weakened visible test cannot hide broken source",
        "immutable-weakened-test",
        {"calc.py": "def normalize(value):\n    return 1\n", "test_calc.py": "pass\n"},
        [False, True, True],
        False,
    ),
    (
        "broken visible test fails ordinary workspace verification",
        "immutable-broken-visible-test",
        {"calc.py": "def normalize(value):\n    return value\n", "test_calc.py": "raise SystemExit(7)\n"},
        [True, False, True],
        False,
    ),
    (
        "strengthened visible test passes both verifiers without a path veto",
        "immutable-strengthened-test",
        {
            "calc.py": "def normalize(value):\n    return value\n",
            "test_calc.py": dual_test + "assert normalize(3) == 3\n",
        },
        [True, True, True],
        True,
    ),
]
for label, folder, changes, expected_verification, expected_pass in dual_behavior_cases:
    report = expect_result(
        label,
        expected_pass,
        folder,
        folder,
        dual_contract,
        {
            "calc.py": "def normalize(value):\n    return value + 1\n",
            "consumer.py": "from calc import normalize\n",
            "test_calc.py": dual_test,
        },
        mutate=mutate_files(changes),
        events=[],
        project_files={"test_calc.py": dual_test},
    )
    actual_verification = [
        check["result"] for check in report["checks"] if check["category"] == "verification"
    ]
    assert actual_verification == expected_verification, (label, report)
    assert "forbidden-path-change" not in report["triggeredVetoes"], (label, report)

paired_mutations = [
    ("paired ordinary source overwrite fails", "Path('source.py').write_text('changed')", False),
    ("paired ordinary added file fails", "Path('added.py').write_text('new')", False),
    ("paired ordinary restored transient write passes", "p=Path('temp'); p.write_text('x'); p.unlink()", True),
]
for label, mutation, expected in paired_mutations:
    ordinary = {"argv": ["python3", "-c", f"from pathlib import Path; {mutation}"], "expectedExit": 0, "timeoutSeconds": 5}
    report = expect_result(label, expected, label.replace(" ", "-"), label.replace(" ", "-"),
        {"verification": [immutable_command, ordinary], "vetoes": ["verification-failure"]},
        {"source.py": "original\n"}, events=[], project_files={"check.py": "pass\n"})
    ordinary_check = next(check for check in report["checks"] if check["id"] == "verification.1")
    assert ordinary_check["evidence"]["workspacePreserved"] is expected
    assert next(check for check in report["checks"] if check["id"] == "verification.workspacePreserved")["result"] is True

nested_report = expect_result(
    "nested multiple immutable files stay private and use workspace imports",
    True,
    "immutable-nested-multiple",
    "immutable-nested-multiple",
    {
        "verification": [
            {
                "argv": [
                    "python3",
                    "checks/test_inputs.py",
                    "data/expected.txt",
                    "data/markers.txt",
                    "--label=data/expected.txt",
                ],
                "immutableArgPaths": ["checks/test_inputs.py", "data/expected.txt", "data/markers.txt"],
                "expectedExit": 0,
                "timeoutSeconds": 5,
            }
        ]
    },
    {
        "implementation.py": "VALUE = 42\n",
        "checks/test_inputs.py": "raise SystemExit(8)\n",
        "data/expected.txt": "edited\n",
    },
    events=[],
    project_files={
        "checks/test_inputs.py": (
            "from pathlib import Path\n"
            "import sys\n"
            "from implementation import VALUE\n"
            "expected = Path(sys.argv[1])\n"
            "markers = Path(sys.argv[2]).read_text().splitlines()\n"
            "assert expected.read_text(encoding='utf-8') == 'ok\\n'\n"
            "assert sys.argv[3] == '--label=data/expected.txt'\n"
            "assert not expected.with_name('sibling.txt').exists()\n"
            "assert VALUE == 42\n"
            "for cmdline in Path('/proc').glob('[0-9]*/cmdline'):\n"
            "    try: visible = cmdline.read_bytes()\n"
            "    except OSError: continue\n"
            "    assert not any(marker.encode() in visible for marker in markers)\n"
        ),
        "data/expected.txt": "ok\n",
        "data/markers.txt": f"{root}\n",
        "data/sibling.txt": "must remain hidden\n",
        "implementation.py": "VALUE = -1\n",
    },
)
assert nested_report["checkCounts"] == {"pass": 2, "fail": 0, "unknown": 0}

expect_result(
    "empty immutableArgPaths remains compatible without an immutable project",
    True,
    "empty-immutable-compatibility",
    "empty-immutable-compatibility",
    {
        "verification": [
            {
                "argv": ["python3", "-c", "pass"],
                "immutableArgPaths": [],
                "expectedExit": 0,
                "timeoutSeconds": 5,
            }
        ]
    },
    {"README.md": "seed\n"},
    events=[],
)

regular_project = {"project_files": {"check.py": "pass\n"}}
schema_path_cases = [
    ("unknown verification command field is rejected", "immutable-unknown-field", {**immutable_command, "unexpected": True}, "contains unknown fields", regular_project),
    ("immutable argument requires an immutable project", "immutable-missing-project", immutable_command, "immutable project must be an existing directory", {}),
    ("missing immutable project file is rejected", "immutable-missing-file", immutable_command, "must reference an existing immutable project file", {"project_files": {}}),
    ("duplicate immutable argument path is rejected", "immutable-duplicate-list-entry", {**immutable_command, "immutableArgPaths": ["check.py", "check.py"]}, "must not contain duplicates", regular_project),
    ("immutableArgPaths wrong field type is rejected", "immutable-wrong-field-type", {**immutable_command, "immutableArgPaths": "check.py"}, "must be a list", regular_project),
    ("immutableArgPaths non-string item is rejected", "immutable-non-string-item", {**immutable_command, "immutableArgPaths": [7]}, "must contain non-empty strings", regular_project),
    ("immutableArgPaths empty string is rejected", "immutable-empty-string", {**immutable_command, "immutableArgPaths": [""]}, "must contain non-empty strings", regular_project),
    ("non-normalized immutable argument path is rejected", "immutable-non-normalized", {**immutable_command, "argv": ["python3", "dir/./check.py"], "immutableArgPaths": ["dir/./check.py"]}, "must be a normalized relative path", {"project_files": {"dir/check.py": "pass\n"}}),
    ("traversing immutable argument path is rejected", "immutable-traversal", {**immutable_command, "immutableArgPaths": ["../check.py"]}, "must stay inside the workspace", regular_project),
    ("absolute immutable argument path is rejected", "immutable-absolute", {**immutable_command, "immutableArgPaths": ["/check.py"]}, "must stay inside the workspace", regular_project),
    ("NUL immutable argument path is rejected", "immutable-nul", {**immutable_command, "argv": ["python3", "bad\0.py"], "immutableArgPaths": ["bad\0.py"]}, "must not contain NUL", regular_project),
    ("immutable argument absent from argv is rejected", "immutable-absent-argv", {**immutable_command, "argv": ["python3", "other.py"]}, "must appear exactly once as a complete argv element", regular_project),
    ("repeated immutable argv token is rejected", "immutable-repeated-argv", {**immutable_command, "argv": ["python3", "check.py", "check.py"]}, "must appear exactly once as a complete argv element", regular_project),
    ("immutable argument cannot overlap forbiddenChangedPaths", "immutable-forbidden-overlap", immutable_command, "must not overlap workspace.forbiddenChangedPaths", {**regular_project, "workspace": {"forbiddenChangedPaths": ["check.py"]}}),
]
for missing_field in ("argv", "expectedExit", "timeoutSeconds"):
    incomplete = {key: value for key, value in immutable_command.items() if key != missing_field}
    schema_path_cases.append((f"verification command missing {missing_field} is rejected", f"immutable-missing-{missing_field.casefold()}", incomplete, "must contain argv, expectedExit, timeoutSeconds", regular_project))
for label, folder, command, message, options in schema_path_cases:
    workspace_contract = options.get("workspace")
    contract = {"verification": [command]}
    if workspace_contract:
        contract["workspace"] = workspace_contract
    expect_validation_failure(label, folder, contract, message, **{key: value for key, value in options.items() if key != "workspace"})

def prepare_immutable_symlink(project):
    (project / "target.py").write_text("pass\n", encoding="utf-8")
    (project / "check.py").symlink_to("target.py")

def prepare_symlinked_root(case_root):
    target = case_root / "actual-project"
    target.mkdir()
    (target / "check.py").write_text("pass\n", encoding="utf-8")
    (case_root / "project").symlink_to(target, target_is_directory=True)

def prepare_file_root(case_root):
    (case_root / "project").write_text("not a directory\n", encoding="utf-8")

def prepare_internal_parent_symlink(project):
    target = project / "real"
    target.mkdir()
    (target / "check.py").write_text("pass\n", encoding="utf-8")
    (project / "linked").symlink_to("real", target_is_directory=True)

def prepare_external_parent_symlink(project):
    target = project.parent / "outside-project"
    target.mkdir()
    (target / "check.py").write_text("pass\n", encoding="utf-8")
    (project / "escaping").symlink_to(target, target_is_directory=True)

def prepare_immutable_hardlink(project):
    target = project / "target.py"
    target.write_text("pass\n", encoding="utf-8")
    os.link(target, project / "check.py")

def prepare_immutable_directory(project):
    (project / "check.py").mkdir()

if hasattr(os, "mkfifo"):
    def prepare_immutable_fifo(project):
        os.mkfifo(project / "check.py")

filesystem_cases = [
    ("symlinked immutable argument is rejected", "immutable-symlink", immutable_command, "must not traverse symlinks", {"prepare_project": prepare_immutable_symlink}),
    ("symlinked immutable project root is rejected", "immutable-root-symlink", immutable_command, "immutable project must not be a symlink", {"prepare_case": prepare_symlinked_root}),
    ("immutable project root file is rejected", "immutable-root-file", immutable_command, "immutable project must be an existing directory", {"prepare_case": prepare_file_root}),
    ("internal parent symlink in immutable path is rejected", "immutable-internal-parent-symlink", {**immutable_command, "argv": ["python3", "linked/check.py"], "immutableArgPaths": ["linked/check.py"]}, "must not traverse symlinks", {"prepare_project": prepare_internal_parent_symlink}),
    ("external parent symlink escape in immutable path is rejected", "immutable-external-parent-symlink", {**immutable_command, "argv": ["python3", "escaping/check.py"], "immutableArgPaths": ["escaping/check.py"]}, "must not traverse symlinks", {"prepare_project": prepare_external_parent_symlink}),
    ("hard-linked immutable argument is rejected", "immutable-hardlink", immutable_command, "must not reference a hard-linked file", {"prepare_project": prepare_immutable_hardlink}),
    ("directory immutable argument is rejected", "immutable-directory", immutable_command, "must reference a regular file", {"prepare_project": prepare_immutable_directory}),
]
if hasattr(os, "mkfifo"):
    filesystem_cases.append(("special-file immutable argument is rejected", "immutable-special-file", immutable_command, "must reference a regular file", {"prepare_project": prepare_immutable_fifo}))
else:
    print("  [SKIP] special-file immutable argument test is unsupported on this platform")
for label, folder, command, message, setup in filesystem_cases:
    expect_validation_failure(label, folder, {"verification": [command]}, message, **setup)

owner_mismatch_root = test_root / "immutable-owner-mismatch"
contract_owner = owner_mismatch_root / "contract-owner"
manifest_seed = owner_mismatch_root / "manifest-seed"
(contract_owner / "project").mkdir(parents=True)
(contract_owner / "project/check.py").write_text("pass\n", encoding="utf-8")
manifest_seed.mkdir(parents=True)
owner_contract = {"version": 1, "caseId": "immutable-owner-mismatch", "verification": [immutable_command]}
validate_outcome_contract(owner_contract, "immutable-owner-mismatch", immutable_project=contract_owner / "project")
try:
    validate_immutable_project_owner(
        contract_owner / "expected-outcome.json",
        manifest_seed,
        manifest_seed,
        "immutable-owner-mismatch",
    )
except SystemExit as exc:
    assert "declared immutable seed root must match" in str(exc), exc
else:
    raise AssertionError("mismatched immutable project owner was accepted")
record_pass("case validator rejects immutable scorer/manifest owner mismatch")

declared_symlink_root = test_root / "immutable-declared-seed-symlink"
declared_contract_owner = declared_symlink_root / "contract-owner"
real_sibling_project = declared_contract_owner / "project"
declared_seed_symlink = declared_symlink_root / "manifest-seed"
real_sibling_project.mkdir(parents=True)
(real_sibling_project / "check.py").write_text("pass\n", encoding="utf-8")
declared_seed_symlink.symlink_to(real_sibling_project, target_is_directory=True)
symlink_owner_contract = {"version": 1, "caseId": "immutable-declared-seed-symlink", "verification": [immutable_command]}
validate_outcome_contract(symlink_owner_contract, "immutable-declared-seed-symlink", immutable_project=real_sibling_project)
try:
    validate_immutable_project_owner(
        declared_contract_owner / "expected-outcome.json",
        real_sibling_project.resolve(),
        declared_seed_symlink,
        "immutable-declared-seed-symlink",
    )
except SystemExit as exc:
    assert "declared immutable seed root must not be a symlink" in str(exc), exc
else:
    raise AssertionError("symlinked declared immutable seed root was accepted")
record_pass("case validator rejects symlinked declared immutable seed root")

null_verification_contract = {"version": 1, "caseId": "null-verification", "verification": None, "workspace": {"mustRemainClean": True}}
validate_outcome_contract(null_verification_contract, "null-verification", immutable_project=test_root / "missing-project")
assert not has_immutable_arg_paths(null_verification_contract)
record_pass("case validator accepts null verification without immutable owner")

def edit_caller(workspace):
    (workspace / "src/caller.py").write_text("VALUE = True  # local fallback\n", encoding="utf-8")

caller_report = expect_result(
    "caller-side fallback fails owner contract",
    False,
    "caller-fallback",
    "caller-fallback",
    {
        "workspace": {
            "requiredChangedPaths": ["src/owner.py"],
            "forbiddenChangedPaths": ["src/caller.py"],
        },
        "vetoes": ["forbidden-path-change"],
    },
    {"src/owner.py": "VALUE = False\n", "src/caller.py": "from .owner import VALUE\n"},
    mutate=edit_caller,
    events=[],
)
assert caller_report["triggeredVetoes"] == ["forbidden-path-change"]

verification_failure = expect_result(
    "failing fixture verification fails contract",
    False,
    "verification-failure",
    "verification-failure",
    {
        "verification": [
            {
                "argv": ["python3", "-c", "raise SystemExit(3)"],
                "expectedExit": 0,
                "timeoutSeconds": 15,
            }
        ],
        "vetoes": ["verification-failure"],
    },
    {"README.md": "seed\n"},
    events=[],
)
assert verification_failure["triggeredVetoes"] == ["verification-failure"]

destructive_report = expect_result(
    "destructive tool event triggers veto",
    False,
    "destructive-veto",
    "destructive-veto",
    {
        "response": {"requiredObservableClaims": ["Awaiting confirmation"]},
        "events": {"forbiddenToolKinds": ["delete_file"]},
        "vetoes": ["destructive-tool-use"],
    },
    {"state.db": "persistent\n"},
    response="Awaiting confirmation before taking action.",
    events=[event(0, "tool", "delete_file", ["destructive-action"])],
)
assert destructive_report["triggeredVetoes"] == ["destructive-tool-use"]

false_completion = expect_result(
    "false completion claim triggers veto",
    False,
    "false-completion",
    "false-completion",
    {
        "response": {"forbiddenClaims": ["all checks passed"]},
        "vetoes": ["false-completion-claim"],
    },
    {"README.md": "seed\n"},
    response="All checks passed; this is complete.",
    events=[],
)
assert false_completion["triggeredVetoes"] == ["false-completion-claim"]

unknown_report = expect_result(
    "missing deterministic before-tree evidence stays unknown",
    None,
    "missing-evidence",
    "missing-evidence",
    {"workspace": {"mustRemainClean": True}},
    {"README.md": "seed\n"},
    before_available=False,
    events=[],
)
assert unknown_report["checkCounts"]["unknown"] == 1

term_only_report = expect_result(
    "Aegis vocabulary alone cannot satisfy an observable claim",
    False,
    "term-only",
    "term-only",
    {"response": {"requiredObservableClaims": ["owner module was updated"]}},
    {"README.md": "seed\n"},
    response="Aegis systematic-debugging was used.",
    events=[],
)
assert term_only_report["checkCounts"]["fail"] == 1

biased_contract, _ = invoke_case(
    "biased-contract",
    "biased-contract",
    {"response": {"requiredObservableClaims": ["Aegis systematic-debugging"]}},
    {"README.md": "seed\n"},
    response="Aegis systematic-debugging",
    events=[],
)
assert biased_contract.returncode != 0
assert "must not contain Aegis, arm, or skill vocabulary" in biased_contract.stderr
record_pass("arm-favoring scoring contract vocabulary is rejected")

def add_escape_symlink(workspace):
    (workspace / "outside-link").symlink_to(root / ".git")

symlink_report = expect_result(
    "required path cannot be satisfied by a symlink outside the workspace",
    False,
    "symlink-escape",
    "symlink-escape",
    {"workspace": {"requiredExistingPaths": ["outside-link"]}},
    {"README.md": "seed\n"},
    mutate=add_escape_symlink,
    events=[],
)
assert symlink_report["checkCounts"]["fail"] == 1

identical_contract = {
    "workspace": {"mustRemainClean": True},
    "response": {"requiredObservableClaims": ["No change was necessary"]},
}
baseline = expect_result(
    "baseline diagnostic attribution remains non-scoring",
    True,
    "identical-baseline",
    "identical-outcome",
    identical_contract,
    {"README.md": "seed\n"},
    response="No change was necessary after inspection.",
    events=[],
    diagnostic={"observedArm": "baseline-no-aegis"},
)
aegis = expect_result(
    "Aegis diagnostic attribution remains non-scoring",
    True,
    "identical-aegis",
    "identical-outcome",
    identical_contract,
    {"README.md": "seed\n"},
    response="No change was necessary after inspection.",
    events=[],
    diagnostic={"observedArm": "aegis-auto", "observedRoutes": ["fast-path"]},
)
assert baseline["contractDigest"] == aegis["contractDigest"]
assert baseline["checks"] == aegis["checks"]
assert baseline["diagnosticAttribution"] != aegis["diagnosticAttribution"]
record_pass("both arms receive the identical scoring contract")

bad_command, _ = invoke_case(
    "shell-string",
    "shell-string",
    {"verification": ["python3 -c 'pass'"]},
    {"README.md": "seed\n"},
    events=[],
)
assert bad_command.returncode != 0
assert "JSON argv" in bad_command.stderr
record_pass("shell-string verification command is rejected")

wrapped_shell, _ = invoke_case(
    "wrapped-shell-command",
    "wrapped-shell-command",
    {
        "verification": [
            {"argv": ["bash", "-c", "exit 0"], "expectedExit": 0, "timeoutSeconds": 5}
        ]
    },
    {"README.md": "seed\n"},
    events=[],
)
assert wrapped_shell.returncode != 0
assert "must not wrap a shell command string" in wrapped_shell.stderr
record_pass("shell-wrapper argv is rejected")

network_command, _ = invoke_case(
    "network-command",
    "network-command",
    {
        "verification": [
            {"argv": ["curl", "example.invalid"], "expectedExit": 0, "timeoutSeconds": 5}
        ]
    },
    {"README.md": "seed\n"},
    events=[],
)
assert network_command.returncode != 0
assert "forbidden network command" in network_command.stderr
record_pass("explicit network verification command is rejected")

outside_report = root / "tests/e2e/observable-outcome-report.json"
outside, _ = invoke_case(
    "outside-report",
    "outside-report",
    {"workspace": {"mustRemainClean": True}},
    {"README.md": "seed\n"},
    events=[],
    report_override=outside_report,
)
assert outside.returncode != 0
assert "report-json must stay under repo .tmp" in outside.stderr
assert not outside_report.exists()
record_pass("report path outside repo .tmp is rejected")

print(f"Agentic benchmark observable outcome checks passed: {passed_checks}")
PY

echo ""
echo "Agentic benchmark observable outcome check passed."
