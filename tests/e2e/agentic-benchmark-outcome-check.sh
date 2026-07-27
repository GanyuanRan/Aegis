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
import shutil
import stat
import subprocess
import sys
from pathlib import Path


root = Path(sys.argv[1]).resolve()
scorer = root / "tests/helpers/score_agentic_benchmark_outcome.py"
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
):
    case_root = test_root / folder
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

    completed = subprocess.run(command, cwd=root, text=True, capture_output=True)
    report = json.loads(report_path.read_text(encoding="utf-8")) if completed.returncode == 0 else None
    return completed, report


def expect_result(label, expected, *args, **kwargs):
    completed, report = invoke_case(*args, **kwargs)
    assert completed.returncode == 0, f"{label}: {completed.stderr}"
    assert report["contractPass"] is expected, (label, report)
    assert report["scoreSource"] == "arm-neutral-observable-outcome-analysis"
    assert report["authorityBoundary"] == "advisory-method-pack-evidence-not-completion-authority"
    print(f"  [PASS] {label}")
    return report


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
print("  [PASS] arm-favoring scoring contract vocabulary is rejected")


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
print("  [PASS] both arms receive the identical scoring contract")


bad_command, _ = invoke_case(
    "shell-string",
    "shell-string",
    {"verification": ["python3 -c 'pass'"]},
    {"README.md": "seed\n"},
    events=[],
)
assert bad_command.returncode != 0
assert "JSON argv" in bad_command.stderr
print("  [PASS] shell-string verification command is rejected")


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
print("  [PASS] shell-wrapper argv is rejected")


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
print("  [PASS] explicit network verification command is rejected")


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
print("  [PASS] report path outside repo .tmp is rejected")

print("Agentic benchmark observable outcome checks passed: 17")
PY

echo ""
echo "Agentic benchmark observable outcome check passed."
