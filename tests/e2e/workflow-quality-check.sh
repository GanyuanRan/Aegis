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
assert_contains "$process_doc" "Complexity Delta" \
    "process baseline defines completion-time complexity delta"
assert_contains "$process_doc" "Files newly crossing 800 lines" \
    "process baseline defines file threshold complexity signal"
assert_contains "$process_doc" "Largest touched function/block" \
    "process baseline defines block-level complexity signal"
assert_contains "$process_doc" "Retired branches/fallbacks/adapters" \
    "process baseline ties complexity delta to retirement"
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
    "User-Language Output" \
    "Evidence Freshness" \
    "Artifact Stability" \
    "Workspace Laziness" \
    "Authority Boundary" \
    "Completion-Time Complexity Delta"; do
    assert_contains "$baseline" "$dimension" "baseline defines $dimension"
done

assert_contains "$baseline" "Files newly crossing 800 lines" \
    "workflow quality baseline includes file threshold complexity signal"
assert_contains "$baseline" "Largest touched function/block" \
    "workflow quality baseline includes block-level complexity signal"
assert_contains "$baseline" "Retirement Closure" \
    "workflow quality baseline includes retirement closure"

for skill in \
    "using-aegis" \
    "goal-framing" \
    "brainstorming" \
    "writing-plans" \
    "systematic-debugging" \
    "verification-before-completion" \
    "long-task-continuation"; do
    assert_contains "$baseline" "\`$skill\`" "baseline defines compact contract for $skill"
done

assert_contains "skills/using-aegis/SKILL.md" "Route: fast-path" \
    "using-aegis exposes compact route contract"
assert_contains "skills/using-aegis/SKILL.md" "ArchitectureReviewRequired" \
    "using-aegis marks architecture review required signal"
assert_contains "skills/goal-framing/SKILL.md" "TaskIntentDraft" \
    "goal-framing exposes task intent goal frame"
assert_contains "skills/brainstorming/SKILL.md" "Compact output contract" \
    "brainstorming exposes compact output contract"
assert_not_contains "skills/brainstorming/SKILL.md" "visual companion|Visual Companion|web browser|local URL" \
    "brainstorming does not offer retired browser visual companion"
assert_contains "skills/writing-plans/SKILL.md" "Compact output contract" \
    "writing-plans exposes compact output contract"
assert_contains "skills/systematic-debugging/SKILL.md" "Quick bug lane" \
    "systematic debugging defines quick bug lane"
assert_contains "skills/verification-before-completion/SKILL.md" "Evidence Card" \
    "verification skill defines evidence card"
assert_contains "skills/verification-before-completion/SKILL.md" "User-Language Output" \
    "verification skill defines user-language output rule"
assert_contains "skills/verification-before-completion/SKILL.md" "section labels, field labels, and explanatory prose" \
    "verification skill localizes user-facing completion cards"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture Alignment" \
    "verification skill defines architecture alignment check"
assert_contains "skills/verification-before-completion/SKILL.md" "ADR Backfill Check" \
    "verification skill defines ADR backfill check"
assert_contains "skills/verification-before-completion/SKILL.md" "recording-architecture-decisions" \
    "verification skill routes ADR lifecycle closure to the dedicated skill when needed"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Delta" \
    "verification skill defines complexity delta check"
assert_contains "skills/verification-before-completion/SKILL.md" "Files newly crossing 800 lines" \
    "verification skill checks file threshold crossings"
assert_contains "skills/verification-before-completion/SKILL.md" "Largest touched function/block" \
    "verification skill checks block-level complexity"
assert_contains "skills/verification-before-completion/SKILL.md" "Retirement Closure" \
    "verification skill defines retirement closure"
assert_contains "skills/verification-before-completion/SKILL.md" "Retention reason" \
    "verification skill requires retention reason"
assert_contains "skills/verification-before-completion/SKILL.md" "Retirement trigger" \
    "verification skill requires retirement trigger"
assert_contains "skills/long-task-continuation/SKILL.md" "Minimal Reporting Shape" \
    "long-task continuation keeps minimal reporting shape"
assert_contains "skills/brainstorming/SKILL.md" "ADR signals" \
    "brainstorming marks ADR signals without creating accepted memory"
assert_contains "skills/brainstorming/SKILL.md" "unexecuted ideas" \
    "brainstorming does not create accepted architecture memory from unexecuted ideas"
assert_contains "skills/writing-plans/SKILL.md" "ADR signal preservation" \
    "writing-plans preserves ADR signals for completion"
assert_contains "skills/writing-plans/SKILL.md" "baseline-sync questions for completion" \
    "writing-plans preserves baseline-sync questions"
assert_contains "skills/long-task-continuation/SKILL.md" "preferred ADR Auto Backfill source" \
    "long-task continuation records are preferred ADR source"
assert_contains "skills/long-task-continuation/SKILL.md" "proof bundle.*ADR signals" \
    "long-task completion passes proof bundle and ADR signals forward"
assert_contains "skills/requesting-code-review/SKILL.md" "missing ADR Auto Backfill or baseline sync" \
    "requesting code review checks missing ADR or baseline sync"
assert_contains "skills/requesting-code-review/SKILL.md" "recording-architecture-decisions" \
    "requesting code review references dedicated ADR lifecycle skill"
assert_contains "skills/requesting-code-review/SKILL.md" "independent code review" \
    "requesting code review is framed as independent review"
assert_contains "skills/requesting-code-review/SKILL.md" "baseline / current authority" \
    "requesting code review checks baseline and current authority refs"
assert_contains "skills/requesting-code-review/SKILL.md" "baseline defect vs architecture drift" \
    "requesting code review distinguishes baseline defect from architecture drift"
assert_contains "skills/requesting-code-review/code-reviewer.md" "Baseline / Current Authority" \
    "code reviewer template includes baseline/current authority section"
assert_contains "skills/requesting-code-review/code-reviewer.md" "ownership map, contract inventory, and dependency direction" \
    "code reviewer template checks baseline ownership contracts and dependencies"
assert_contains "skills/requesting-code-review/code-reviewer.md" "baseline defect, architecture drift, or intentional architecture change" \
    "code reviewer template distinguishes baseline defect and drift"
assert_contains "agents/code-reviewer.md" "skills/requesting-code-review/code-reviewer.md" \
    "named code reviewer points to canonical skill template path"
assert_contains "agents/code-reviewer.md" "canonical Aegis code" \
    "named code reviewer identifies canonical Aegis review checklist"
assert_contains "agents/code-reviewer.md" "host compatibility projection" \
    "named code reviewer is marked as compatibility projection"
assert_contains "agents/code-reviewer.md" "baseline defect, architecture drift, and intentional architecture change" \
    "named code reviewer mirrors baseline defect and drift distinction"
assert_contains "agents/code-reviewer.md" "ADR Auto Backfill or baseline sync" \
    "named code reviewer mirrors ADR and baseline sync checks"

assert_contains "skills/recording-architecture-decisions/SKILL.md" "name: recording-architecture-decisions" \
    "recording architecture decisions skill exists"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "architecture decision record|durable architecture decision|decision log" \
    "recording architecture decisions skill has ADR discovery terms"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "ADR-CREATION-GATE.md" \
    "recording architecture decisions skill reads ADR creation gate"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "AEGIS_ADR_AUTO_BACKFILL.md" \
    "recording architecture decisions skill reads ADR auto backfill baseline"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "Baseline Sync" \
    "recording architecture decisions skill defines baseline sync closure"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "create.*amend.*supersede.*skip" \
    "recording architecture decisions skill covers ADR lifecycle actions"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "existing baseline remains valid|baseline remains valid" \
    "recording architecture decisions skill requires unchanged-baseline reason"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "not completion authority" \
    "recording architecture decisions skill preserves authority boundary"

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
    "explicit-aegis-goal",
    "approved-spec-to-plan",
    "completion-claim",
    "architecture-completion-adr-backfill-check",
    "core-file-complexity-delta-before-completion",
    "high-risk-merge-independent-review",
    "simple-completion-no-adr-ceremony",
    "architecture-area-bugfix-restores-baseline-no-adr",
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
    "goal-framing",
    "brainstorming",
    "writing-plans",
    "systematic-debugging",
    "verification-before-completion",
    "long-task-continuation",
    "requesting-code-review",
    "recording-architecture-decisions",
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
    "goal-framing",
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
if "Complexity Delta" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Complexity Delta")
if "Architecture Alignment" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Architecture Alignment")
if "ADR Backfill Check" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include ADR Backfill Check")
if "Retirement Closure" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Retirement Closure")
if "recording-architecture-decisions" not in contracts:
    raise SystemExit("compact output contracts must include recording-architecture-decisions")
for required in ("Decision Candidate", "ADR Gate", "ADR Action", "Owner Surface", "Baseline Sync", "Boundary"):
    if required not in contracts["recording-architecture-decisions"]:
        raise SystemExit(f"recording-architecture-decisions compact contract must include {required}")
if "ArchitectureReviewRequired" not in contracts["using-aegis"]:
    raise SystemExit("using-aegis compact contract must include ArchitectureReviewRequired")
if "Stop condition" not in contracts["goal-framing"]:
    raise SystemExit("goal-framing compact contract must include Stop condition")
if "DriftCheckDraft" not in contracts["long-task-continuation"]:
    raise SystemExit("long-task compact contract must include DriftCheckDraft")

by_id = {item["id"]: item for item in samples}
adr_sample = by_id["architecture-completion-adr-backfill-check"]
if adr_sample.get("expectedPrimarySkill") != "verification-before-completion":
    raise SystemExit("ADR backfill completion sample must use verification-before-completion")
if "skip-architecture-alignment" not in adr_sample.get("mustNotDo", []):
    raise SystemExit("ADR backfill completion sample must forbid skipping architecture alignment")
if "skip-adr-backfill-check" not in adr_sample.get("mustNotDo", []):
    raise SystemExit("ADR backfill completion sample must forbid skipping the check")
if "architecture-alignment" not in adr_sample.get("verificationSignal", ""):
    raise SystemExit("ADR backfill completion sample must require architecture alignment judgment")
if "baseline-sync" not in adr_sample.get("verificationSignal", ""):
    raise SystemExit("ADR backfill completion sample must require baseline-sync judgment")
if "authoritative" not in " ".join(adr_sample.get("mustNotDo", [])):
    raise SystemExit("ADR backfill completion sample must protect the authority boundary")
if "recording-architecture-decisions" not in adr_sample.get("allowedSecondarySkills", []):
    raise SystemExit("ADR backfill completion sample must allow recording-architecture-decisions for lifecycle closure")

direct_adr_sample = by_id["direct-adr-lifecycle-request"]
if direct_adr_sample.get("expectedPrimarySkill") != "recording-architecture-decisions":
    raise SystemExit("direct ADR lifecycle request must use recording-architecture-decisions")
for required in (
    "treat-adr-as-completion-authority",
    "write-adr-without-gate-check",
    "skip-baseline-sync-closure",
):
    if required not in direct_adr_sample.get("mustNotDo", []):
        raise SystemExit(f"direct ADR lifecycle request must forbid {required}")
for required_signal in (
    "adr-gate",
    "owner-surface",
    "baseline-sync",
    "unchanged-reason",
):
    if required_signal not in direct_adr_sample.get("verificationSignal", ""):
        raise SystemExit(f"direct ADR lifecycle request must require {required_signal}")

direct_adr_skip_sample = by_id["direct-adr-skip-request"]
if direct_adr_skip_sample.get("expectedPrimarySkill") != "recording-architecture-decisions":
    raise SystemExit("direct ADR skip request must use recording-architecture-decisions")
if direct_adr_skip_sample.get("expectedArtifacts"):
    raise SystemExit("direct ADR skip request must not expect artifacts")
for required in (
    "force-adr-creation",
    "force-baseline-writeback",
    "treat-implementation-detail-as-durable-decision",
):
    if required not in direct_adr_skip_sample.get("mustNotDo", []):
        raise SystemExit(f"direct ADR skip request must forbid {required}")

completion_sample = by_id["completion-claim"]
if "requesting-code-review" in completion_sample.get("allowedSecondarySkills", []):
    raise SystemExit("generic completion sample must not route to requesting-code-review by default")

complexity_sample = by_id["core-file-complexity-delta-before-completion"]
if complexity_sample.get("expectedPrimarySkill") != "verification-before-completion":
    raise SystemExit("core file complexity sample must use verification-before-completion")
for required in (
    "skip-complexity-delta",
    "ignore-file-crossing-800-lines",
    "retain-old-logic-without-retirement-trigger",
    "claim-completion-with-entropy-increase-hidden",
):
    if required not in complexity_sample.get("mustNotDo", []):
        raise SystemExit(f"core file complexity sample must forbid {required}")
for required_signal in (
    "complexity-delta",
    "file-thresholds",
    "net-entropy",
    "retirement-closure",
):
    if required_signal not in complexity_sample.get("verificationSignal", ""):
        raise SystemExit(f"core file complexity sample must require {required_signal}")
if "complexity-delta" not in complexity_sample.get("expectedOutputShape", ""):
    raise SystemExit("core file complexity sample must include complexity delta in output shape")

review_sample = by_id["high-risk-merge-independent-review"]
if review_sample.get("expectedPrimarySkill") != "requesting-code-review":
    raise SystemExit("high-risk merge review sample must use requesting-code-review")
for required in (
    "replace-verification-before-completion",
    "skip-baseline-alignment",
    "treat-review-as-completion-authority",
):
    if required not in review_sample.get("mustNotDo", []):
        raise SystemExit(f"high-risk review sample must forbid {required}")
for required_signal in (
    "baseline-alignment",
    "architecture-drift",
    "retirement",
    "adr-baseline-sync",
):
    if required_signal not in review_sample.get("verificationSignal", ""):
        raise SystemExit(f"high-risk review sample must require {required_signal}")

no_adr_sample = by_id["simple-completion-no-adr-ceremony"]
if no_adr_sample.get("expectedArtifacts"):
    raise SystemExit("simple completion no-ADR sample must not expect artifacts")
if no_adr_sample.get("workspacePolicy") != "no-workspace":
    raise SystemExit("simple completion no-ADR sample must keep no-workspace policy")
if "force-adr-backfill-ceremony" not in no_adr_sample.get("mustNotDo", []):
    raise SystemExit("simple completion no-ADR sample must forbid ADR ceremony")

baseline_restore_sample = by_id["architecture-area-bugfix-restores-baseline-no-adr"]
if baseline_restore_sample.get("expectedPrimarySkill") != "verification-before-completion":
    raise SystemExit("baseline restoration sample must use verification-before-completion")
if "force-adr-creation-for-baseline-restoration" not in baseline_restore_sample.get("mustNotDo", []):
    raise SystemExit("baseline restoration sample must forbid forced ADR creation")
if "skip-reason" not in baseline_restore_sample.get("verificationSignal", ""):
    raise SystemExit("baseline restoration sample must require a skip reason")
if "existing-baseline-was-restored" not in baseline_restore_sample.get("verificationSignal", ""):
    raise SystemExit("baseline restoration sample must cite existing baseline restoration")

print("  [PASS] workflow quality matrix has representative samples and compact contracts")
PY

if (( failures > 0 )); then
    echo ""
    echo "Workflow quality check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workflow quality check passed."
