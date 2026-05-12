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

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== Workflow Quality Check ==="

baseline="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
current_index="docs/current/README.md"
process_doc="docs/current/AEGIS_PROCESS_BASELINE.md"
trigger_doc="docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md"
readme_en="README.md"
readme_zh="README.zh-CN.md"
matrix="tests/e2e/fixtures/workflow-quality-matrix.json"

if [[ -f "$baseline" ]]; then
    pass "workflow quality baseline exists"
else
    fail "workflow quality baseline exists"
fi

if [[ -f "$matrix" ]]; then
    pass "workflow quality matrix exists"
else
    fail "workflow quality matrix exists"
fi

assert_contains "$current_index" "AEGIS_WORKFLOW_QUALITY_BASELINE.md" \
    "current docs index lists workflow quality baseline"
assert_contains "$process_doc" "Workflow Quality" \
    "process baseline references workflow quality"
assert_contains "$trigger_doc" "workflow-quality" \
    "trigger health references workflow-quality samples"
assert_contains "$readme_en" "Workflow Quality" \
    "English README mentions workflow quality"
assert_contains "$readme_zh" "工作流质量" \
    "Chinese README mentions workflow quality"

for dimension in \
    "Trigger Accuracy" \
    "Fast-Path Cheapness" \
    "Output Compactness" \
    "Evidence Freshness" \
    "Artifact Stability" \
    "Workspace Laziness" \
    "Authority Boundary"; do
    assert_contains "$baseline" "$dimension" "baseline defines $dimension"
done

for skill in \
    "using-aegis" \
    "brainstorming" \
    "writing-plans" \
    "systematic-debugging" \
    "verification-before-completion" \
    "long-task-continuation"; do
    assert_contains "$baseline" "\`$skill\`" "baseline defines compact contract for $skill"
done

assert_contains "skills/using-aegis/SKILL.md" "Route: fast-path" \
    "using-aegis exposes compact route contract"
assert_contains "skills/brainstorming/SKILL.md" "Compact output contract" \
    "brainstorming exposes compact output contract"
assert_contains "skills/writing-plans/SKILL.md" "Compact output contract" \
    "writing-plans exposes compact output contract"
assert_contains "skills/systematic-debugging/SKILL.md" "Quick bug lane" \
    "systematic debugging defines quick bug lane"
assert_contains "skills/verification-before-completion/SKILL.md" "Evidence Card" \
    "verification skill defines evidence card"
assert_contains "skills/long-task-continuation/SKILL.md" "Minimal Reporting Shape" \
    "long-task continuation keeps minimal reporting shape"

assert_not_contains "skills/using-aegis/SKILL.md" "Evidence Card" \
    "using-aegis does not absorb verification output contract"
assert_not_contains "skills/using-aegis/SKILL.md" "Design Spec.*Design Spec.*Design Spec" \
    "using-aegis hot path avoids repeated design-spec ceremony"

"${PYTHON_CMD[@]}" - "$matrix" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
samples = data.get("samples", [])

expected_ids = {
    "simple-factual-qa",
    "tiny-wording-edit",
    "git-status-version-question",
    "quick-single-owner-bug",
    "failing-test-diagnosis",
    "ambiguous-feature",
    "approved-spec-to-plan",
    "completion-claim",
    "interrupted-long-task-resume",
    "governance-compat-cleanup",
}
ids = {item.get("id") for item in samples}
missing = sorted(expected_ids - ids)
if missing:
    raise SystemExit(f"missing workflow-quality samples: {', '.join(missing)}")

if len(samples) < 10:
    raise SystemExit("workflow quality matrix must contain at least 10 samples")

required_fields = {
    "id",
    "prompt",
    "expectedPrimarySkill",
    "allowedSecondarySkills",
    "mustNotDo",
    "expectedOutputShape",
    "workspacePolicy",
    "expectedArtifacts",
    "verificationSignal",
}

for item in samples:
    missing_fields = sorted(required_fields - item.keys())
    if missing_fields:
        raise SystemExit(f"{item.get('id', '<unknown>')} missing fields: {', '.join(missing_fields)}")
    if not item["mustNotDo"]:
        raise SystemExit(f"{item['id']} must define mustNotDo")
    if not item["workspacePolicy"]:
        raise SystemExit(f"{item['id']} must define workspacePolicy")
    if not item["expectedOutputShape"]:
        raise SystemExit(f"{item['id']} must define expectedOutputShape")
    if not item["verificationSignal"]:
        raise SystemExit(f"{item['id']} must define verificationSignal")

negative = [s for s in samples if s.get("expectedPrimarySkill") is None]
positive = [s for s in samples if s.get("expectedPrimarySkill")]
if len(negative) < 3:
    raise SystemExit("workflow quality matrix must include at least 3 fast-path / negative samples")
if len(positive) < 6:
    raise SystemExit("workflow quality matrix must include at least 6 positive samples")

skills = {s.get("expectedPrimarySkill") for s in positive}
required_skills = {
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "verification-before-completion",
    "long-task-continuation",
}
missing_skills = sorted(required_skills - skills)
if missing_skills:
    raise SystemExit(f"missing expected primary skills: {', '.join(missing_skills)}")

for item in negative:
    if item.get("expectedArtifacts"):
        raise SystemExit(f"{item['id']} is fast-path but expects artifacts")
    if "no-workspace" not in item.get("workspacePolicy", ""):
        raise SystemExit(f"{item['id']} fast-path sample must use no-workspace policy")

contracts = data.get("compactOutputContracts", {})
required_contracts = {
    "using-aegis",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "verification-before-completion",
    "long-task-continuation",
}
missing_contracts = sorted(required_contracts - contracts.keys())
if missing_contracts:
    raise SystemExit(f"missing compact output contracts: {', '.join(missing_contracts)}")

if "Confidence" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Confidence")
if "DriftCheckDraft" not in contracts["long-task-continuation"]:
    raise SystemExit("long-task compact contract must include DriftCheckDraft")

print("  [PASS] workflow quality matrix has representative samples and compact contracts")
PY

if (( failures > 0 )); then
    echo ""
    echo "Workflow quality check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workflow quality check passed."
