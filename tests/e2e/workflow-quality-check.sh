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
tdd_mode_doc="docs/current/AEGIS_TDD_MODE.md"
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
assert_contains "$current_index" "AEGIS_TDD_MODE.md" \
    "current docs index lists TDD mode baseline"
if [[ -f "$tdd_mode_doc" ]]; then
    pass "TDD mode baseline exists"
else
    fail "TDD mode baseline exists"
fi
assert_contains "$process_doc" "Workflow Quality" \
    "process baseline references workflow quality"
assert_contains "$process_doc" "TDD Mode" \
    "process baseline references TDD mode"
assert_contains "$process_doc" "Complexity Delta" \
    "process baseline defines completion-time complexity delta"
assert_contains "$process_doc" "Plan-Time Complexity Check" \
    "process baseline defines plan-time complexity check"
assert_contains "$process_doc" "Pre-Edit Complexity Check" \
    "process baseline defines pre-edit complexity check"
assert_contains "$process_doc" "Complexity Governance Suggestion" \
    "process baseline defines post-change complexity governance suggestion"
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
    "Three-Stage Complexity Governance" \
    "Completion-Time Complexity Delta" \
    "TDD Route Mode" \
    "Micro-Slice Artifact Budget" \
    "Strong-Opinion Review Lenses"; do
    assert_contains "$baseline" "$dimension" "baseline defines $dimension"
done

assert_contains "$tdd_mode_doc" 'tdd_mode = "auto"' \
    "TDD mode doc defines auto config"
assert_contains "$tdd_mode_doc" 'tdd_mode = "off"' \
    "TDD mode doc defines off config"
assert_contains "$tdd_mode_doc" "strict.*light.*skipped|strict.*skipped.*light|strict.*\`light\`.*skipped" \
    "TDD mode doc defines strict light skipped route"
assert_contains "$tdd_mode_doc" "verification-before-completion" \
    "TDD mode doc preserves completion verification"
assert_contains "$tdd_mode_doc" "AEGIS_TDD_MODE" \
    "TDD mode doc names environment override"
assert_contains "$tdd_mode_doc" 'aegis-doctor\.py tdd-mode off' \
    "TDD mode doc documents doctor off command"
assert_contains "$tdd_mode_doc" 'aegis-doctor\.py tdd-mode auto' \
    "TDD mode doc documents doctor auto command"

assert_contains "$baseline" "Plan-Time Complexity Check" \
    "workflow quality baseline includes plan-time complexity check"
assert_contains "$baseline" "TDD Route" \
    "workflow quality baseline includes TDD route"
assert_contains "$baseline" "auto.*strict.*light.*skipped|strict.*light.*skipped" \
    "workflow quality baseline includes auto TDD routing"
assert_contains "$baseline" "off.*verification-before-completion|verification-before-completion.*off" \
    "workflow quality baseline keeps completion verification on when TDD mode is off"
assert_contains "$baseline" "Pre-Edit Complexity Check" \
    "workflow quality baseline includes pre-edit complexity check"
assert_contains "$baseline" "Complexity Governance Suggestion" \
    "workflow quality baseline includes complexity governance suggestion"
assert_contains "$baseline" "Files newly crossing 800 lines" \
    "workflow quality baseline includes file threshold complexity signal"
assert_contains "$baseline" "Largest touched function/block" \
    "workflow quality baseline includes block-level complexity signal"
assert_contains "$baseline" "Retirement Closure" \
    "workflow quality baseline includes retirement closure"
assert_contains "$baseline" "Layer Stop Card" \
    "workflow quality baseline includes layer stop card"
assert_contains "$baseline" "User Intervention Point" \
    "workflow quality baseline exposes user intervention point"
assert_contains "$baseline" "Product Risk Lens" \
    "workflow quality baseline includes product risk lens"
assert_contains "$baseline" "Plan Pressure Test" \
    "workflow quality baseline includes plan pressure test"
assert_contains "$baseline" "Architecture Integrity Lens" \
    "workflow quality baseline includes architecture integrity lens"
assert_contains "$baseline" "Planless Slice Lane" \
    "workflow quality baseline includes planless slice lane"
assert_contains "$baseline" "Slice Card" \
    "workflow quality baseline includes slice card"
assert_contains "$baseline" "one parent spec.*one parent plan|one parent plan.*one parent spec" \
    "workflow quality baseline defines artifact budget"
assert_contains "$baseline" "Findings First" \
    "workflow quality baseline includes findings-first review lens"
assert_contains "$baseline" "Readiness Summary" \
    "workflow quality baseline includes readiness summary"
assert_contains "$baseline" "Retro / Memory Filter" \
    "workflow quality baseline includes retro memory filter"
assert_contains "$baseline" "role persona.*review lens|review lens.*role persona" \
    "workflow quality baseline keeps role personas out of strong-opinion lenses"
assert_contains "$process_doc" "Strong-Opinion Review Lenses" \
    "process baseline references strong-opinion review lenses"
assert_contains "$process_doc" "Architecture Integrity Lens" \
    "process baseline references architecture integrity lens"
assert_contains "$process_doc" "Micro-Slice Artifact Budget" \
    "process baseline references micro-slice artifact budget"

for skill in \
    "using-aegis" \
    "goal-framing" \
    "brainstorming" \
    "writing-plans" \
    "systematic-debugging" \
    "requesting-code-review" \
    "verification-before-completion" \
    "recording-architecture-decisions" \
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
assert_contains "skills/brainstorming/SKILL.md" "Product Risk Lens" \
    "brainstorming includes product risk lens"
assert_contains "skills/brainstorming/SKILL.md" "Plan-Time Complexity Check" \
    "brainstorming includes plan-time complexity check"
assert_contains "skills/brainstorming/SKILL.md" "Architecture Integrity Lens" \
    "brainstorming includes architecture integrity lens"
assert_contains "skills/brainstorming/SKILL.md" "Better file boundary" \
    "brainstorming checks better file boundary"
assert_contains "skills/brainstorming/SKILL.md" "review lens, not persona|not a persona" \
    "brainstorming keeps product lens out of persona roleplay"
assert_contains "skills/brainstorming/SKILL.md" "does not override baseline evidence" \
    "brainstorming product lens cannot override baseline evidence"
assert_not_contains "skills/brainstorming/SKILL.md" "visual companion|Visual Companion|web browser|local URL" \
    "brainstorming does not offer retired browser visual companion"
assert_contains "skills/writing-plans/SKILL.md" "Compact output contract" \
    "writing-plans exposes compact output contract"
assert_contains "skills/writing-plans/SKILL.md" "Plan Pressure Test" \
    "writing-plans includes plan pressure test"
assert_contains "skills/writing-plans/SKILL.md" "Plan-Time Complexity Check" \
    "writing-plans includes plan-time complexity check"
assert_contains "skills/writing-plans/SKILL.md" "owner / contract / retirement" \
    "writing-plans pressure-tests owner contract retirement risk"
assert_contains "skills/writing-plans/SKILL.md" "Architecture Integrity Lens" \
    "writing-plans includes architecture integrity lens"
assert_contains "skills/writing-plans/SKILL.md" "Planless Slice Lane" \
    "writing-plans includes planless slice lane"
assert_contains "skills/writing-plans/SKILL.md" "Slice Card" \
    "writing-plans includes slice card"
assert_contains "skills/writing-plans/SKILL.md" "do not save a new plan|Do not save a new plan" \
    "writing-plans prevents micro-slice plan files"
assert_contains "skills/writing-plans/SKILL.md" "new owner.*contract.*schema.*public API|public API.*schema.*contract.*owner" \
    "writing-plans lists escalation triggers for durable plans"
assert_contains "skills/first-principles-review/SKILL.md" "Architecture Integrity Lens" \
    "first-principles review owns architecture integrity lens"
assert_contains "skills/first-principles-review/SKILL.md" "Higher-level simplification" \
    "first-principles review checks higher-level simplification"
assert_contains "skills/test-driven-development/SKILL.md" "Pre-Edit Complexity Check" \
    "test-driven-development includes pre-edit complexity check"
assert_contains "skills/test-driven-development/SKILL.md" "TDD Mode" \
    "test-driven-development includes TDD mode"
assert_contains "skills/test-driven-development/SKILL.md" "TDD Route" \
    "test-driven-development includes TDD route"
assert_contains "skills/test-driven-development/SKILL.md" "strict.*light.*skipped|strict.*skipped.*light" \
    "test-driven-development defines strict light skipped route"
assert_contains "skills/test-driven-development/SKILL.md" "verification-before-completion" \
    "test-driven-development keeps completion verification independent of TDD mode"
assert_contains "skills/test-driven-development/SKILL.md" "pause for plan update" \
    "test-driven-development can pause for plan update when complexity risk appears"
assert_contains "skills/systematic-debugging/SKILL.md" "Quick bug lane" \
    "systematic debugging defines quick bug lane"
assert_contains "skills/systematic-debugging/SKILL.md" "Pre-Edit Complexity Check" \
    "systematic debugging includes pre-edit complexity check"
assert_contains "skills/systematic-debugging/SKILL.md" "Layer Stop Card" \
    "systematic debugging defines layer stop card"
assert_contains "skills/systematic-debugging/SKILL.md" "User Intervention Point" \
    "systematic debugging exposes user intervention point"
assert_contains "skills/systematic-debugging/SKILL.md" "Falsifier" \
    "systematic debugging exposes falsifier for layer stop"
assert_contains "skills/long-task-continuation/SKILL.md" "Planless Slice Lane" \
    "long-task continuation includes planless slice lane"
assert_contains "skills/long-task-continuation/SKILL.md" "Slice Card" \
    "long-task continuation includes slice card"
assert_contains "skills/long-task-continuation/SKILL.md" "parent plan" \
    "long-task continuation reuses parent plan for micro-slices"
assert_contains "skills/long-task-continuation/SKILL.md" "do not create.*plan.*spec|Do not create.*plan.*spec" \
    "long-task continuation prevents per-slice plan/spec files"
assert_contains "skills/verification-before-completion/SKILL.md" "Evidence Card" \
    "verification skill defines evidence card"
assert_contains "skills/verification-before-completion/SKILL.md" "Readiness Summary" \
    "verification skill defines readiness summary"
assert_contains "skills/verification-before-completion/SKILL.md" "commit, tag, publish, merge, or release" \
    "verification readiness does not authorize publishing actions"
assert_contains "skills/verification-before-completion/SKILL.md" "User-Language Output" \
    "verification skill defines user-language output rule"
assert_contains "skills/verification-before-completion/SKILL.md" "section labels, field labels, and explanatory prose" \
    "verification skill localizes user-facing completion cards"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture Alignment" \
    "verification skill defines architecture alignment check"
assert_contains "skills/verification-before-completion/SKILL.md" "Integrity Residual Risk" \
    "verification skill reports architecture integrity residual risk when triggered"
assert_contains "skills/verification-before-completion/SKILL.md" "ADR Backfill Check" \
    "verification skill defines ADR backfill check"
assert_contains "skills/verification-before-completion/SKILL.md" "recording-architecture-decisions" \
    "verification skill routes ADR lifecycle closure to the dedicated skill when needed"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Delta" \
    "verification skill defines complexity delta check"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Governance Suggestion" \
    "verification skill defines complexity governance suggestion"
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
assert_contains "skills/executing-plans/SKILL.md" "Pre-Edit Complexity Check" \
    "executing-plans re-checks complexity before source edits"
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
assert_contains "skills/requesting-code-review/SKILL.md" "Findings First|Findings-first" \
    "requesting code review uses findings-first lens"
assert_contains "skills/requesting-code-review/SKILL.md" "bugs first, risk first, tests first" \
    "requesting code review prioritizes bugs risks and tests"
assert_contains "skills/requesting-code-review/SKILL.md" "[Rr]eview readiness is not merge approval" \
    "requesting code review preserves merge authority boundary"
assert_contains "skills/requesting-code-review/SKILL.md" "baseline / current authority" \
    "requesting code review checks baseline and current authority refs"
assert_contains "skills/requesting-code-review/SKILL.md" "baseline defect vs architecture drift" \
    "requesting code review distinguishes baseline defect from architecture drift"
assert_contains "skills/requesting-code-review/code-reviewer.md" "Baseline / Current Authority" \
    "code reviewer template includes baseline/current authority section"
assert_contains "skills/requesting-code-review/code-reviewer.md" "Findings First|Findings-first" \
    "code reviewer template leads with findings"
assert_contains "skills/requesting-code-review/code-reviewer.md" "bugs first, risk first, tests first" \
    "code reviewer template prioritizes bugs risks and tests"
assert_contains "skills/requesting-code-review/code-reviewer.md" "ownership map, contract inventory, and dependency direction" \
    "code reviewer template checks baseline ownership contracts and dependencies"
assert_contains "skills/requesting-code-review/code-reviewer.md" "highest appropriate owner/contract layer" \
    "code reviewer checks highest appropriate owner or contract layer"
assert_contains "skills/requesting-code-review/code-reviewer.md" "caller-side fallback" \
    "code reviewer flags caller-side fallback masking contract fixes"
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
assert_contains "skills/recording-architecture-decisions/SKILL.md" "Retro / Memory Filter" \
    "recording architecture decisions skill defines retro memory filter"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "executed durable decisions" \
    "recording architecture decisions records executed durable decisions only"
assert_contains "skills/recording-architecture-decisions/SKILL.md" "unexecuted ideas" \
    "recording architecture decisions rejects unexecuted ideas as accepted memory"
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
    "plan-time-complexity-check-before-design",
    "plan-time-complexity-check-before-plan",
    "pre-edit-complexity-check-before-code",
    "pre-edit-complexity-check-debugging-fix",
    "tdd-auto-small-task-light-verification",
    "tdd-auto-risky-code-strict",
    "tdd-off-no-automatic-tdd",
    "minimal-sufficient-repair-not-local-patch",
    "core-file-complexity-delta-before-completion",
    "high-risk-merge-independent-review",
    "simple-completion-no-adr-ceremony",
    "architecture-area-bugfix-restores-baseline-no-adr",
    "layer-stop-local-root-cause",
    "layer-stop-cross-system-contract",
    "layer-stop-spec-gap",
    "fast-path-no-layer-stop-card",
    "layer-stop-user-falsifier-correction",
    "strong-opinion-product-risk-lens",
    "strong-opinion-plan-pressure-test",
    "architecture-integrity-higher-level-path",
    "strong-opinion-review-findings-first",
    "strong-opinion-release-readiness-summary",
    "strong-opinion-retro-memory-filter",
    "strong-opinion-fast-path-no-persona",
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
    "test-driven-development",
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
    "test-driven-development",
    "executing-plans",
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
if "Complexity Governance Suggestion" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Complexity Governance Suggestion")
if "Architecture Alignment" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Architecture Alignment")
if "ADR Backfill Check" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include ADR Backfill Check")
if "Retirement Closure" not in contracts["verification-before-completion"]:
    raise SystemExit("verification compact contract must include Retirement Closure")
if "recording-architecture-decisions" not in contracts:
    raise SystemExit("compact output contracts must include recording-architecture-decisions")
if "Layer Stop Card" not in contracts["systematic-debugging"]:
    raise SystemExit("systematic-debugging compact contract must include Layer Stop Card")
if "Pre-Edit Complexity Check" not in contracts["systematic-debugging"]:
    raise SystemExit("systematic-debugging compact contract must include Pre-Edit Complexity Check")
if "Pre-Edit Complexity Check" not in contracts["test-driven-development"]:
    raise SystemExit("test-driven-development compact contract must include Pre-Edit Complexity Check")
if "TDD Route" not in contracts["test-driven-development"]:
    raise SystemExit("test-driven-development compact contract must include TDD Route")
if "Pre-Edit Complexity Check" not in contracts["executing-plans"]:
    raise SystemExit("executing-plans compact contract must include Pre-Edit Complexity Check")
for contract in ("brainstorming", "writing-plans"):
    if "Plan-Time Complexity Check" not in contracts[contract]:
        raise SystemExit(f"{contract} compact contract must include Plan-Time Complexity Check")
for required in ("Decision Candidate", "ADR Gate", "ADR Action", "Owner Surface", "Baseline Sync", "Boundary"):
    if required not in contracts["recording-architecture-decisions"]:
        raise SystemExit(f"recording-architecture-decisions compact contract must include {required}")
if "ArchitectureReviewRequired" not in contracts["using-aegis"]:
    raise SystemExit("using-aegis compact contract must include ArchitectureReviewRequired")
if "Stop condition" not in contracts["goal-framing"]:
    raise SystemExit("goal-framing compact contract must include Stop condition")
if "DriftCheckDraft" not in contracts["long-task-continuation"]:
    raise SystemExit("long-task compact contract must include DriftCheckDraft")

strong_lens_contracts = {
    "brainstorming": "Product Risk Lens",
    "writing-plans": "Plan Pressure Test",
    "requesting-code-review": "Findings First",
    "verification-before-completion": "Readiness Summary",
    "recording-architecture-decisions": "Retro / Memory Filter",
}
for contract, required in strong_lens_contracts.items():
    if contract not in contracts:
        raise SystemExit(f"compact output contracts must include {contract}")
    if required not in contracts[contract]:
        raise SystemExit(f"{contract} compact contract must include {required}")

for contract in ("brainstorming", "writing-plans"):
    if "Architecture Integrity Lens" not in contracts[contract]:
        raise SystemExit(f"{contract} compact contract must include Architecture Integrity Lens")

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
    "skip-complexity-governance-suggestion",
    "ignore-file-crossing-800-lines",
    "retain-old-logic-without-retirement-trigger",
    "claim-completion-with-entropy-increase-hidden",
):
    if required not in complexity_sample.get("mustNotDo", []):
        raise SystemExit(f"core file complexity sample must forbid {required}")
for required_signal in (
    "complexity-delta",
    "complexity-governance-suggestion",
    "file-thresholds",
    "net-entropy",
    "retirement-closure",
):
    if required_signal not in complexity_sample.get("verificationSignal", ""):
        raise SystemExit(f"core file complexity sample must require {required_signal}")
for required_shape in ("complexity-delta", "governance-suggestion"):
    if required_shape not in complexity_sample.get("expectedOutputShape", ""):
        raise SystemExit(f"core file complexity sample must include {required_shape} in output shape")

complexity_stage_samples = {
    "plan-time-complexity-check-before-design": ("brainstorming", "plan-time-complexity-check"),
    "plan-time-complexity-check-before-plan": ("writing-plans", "plan-time-complexity-check"),
    "pre-edit-complexity-check-before-code": ("test-driven-development", "pre-edit-complexity-check"),
    "pre-edit-complexity-check-debugging-fix": ("systematic-debugging", "pre-edit-complexity-check"),
}
for sample_id, (skill, signal) in complexity_stage_samples.items():
    sample = by_id[sample_id]
    if sample.get("expectedPrimarySkill") != skill:
        raise SystemExit(f"{sample_id} must use {skill}")
    if signal not in sample.get("expectedOutputShape", ""):
        raise SystemExit(f"{sample_id} output shape must include {signal}")
    if signal not in sample.get("verificationSignal", ""):
        raise SystemExit(f"{sample_id} verification signal must include {signal}")
    if "complexity-check" not in " ".join(sample.get("mustNotDo", [])):
        raise SystemExit(f"{sample_id} must forbid skipping {signal}")

tdd_auto_small = by_id["tdd-auto-small-task-light-verification"]
if tdd_auto_small.get("expectedPrimarySkill") is not None:
    raise SystemExit("AUTO small-task TDD sample must stay fast path")
for required in (
    "force-red-green-refactor",
    "load-test-driven-development-for-tiny-edit",
    "skip-verification-before-completion",
):
    if required not in tdd_auto_small.get("mustNotDo", []):
        raise SystemExit(f"AUTO small-task TDD sample must forbid {required}")
if "tdd-route-auto-light-or-skipped" not in tdd_auto_small.get("verificationSignal", ""):
    raise SystemExit("AUTO small-task TDD sample must require light or skipped route signal")

tdd_auto_risky = by_id["tdd-auto-risky-code-strict"]
if tdd_auto_risky.get("expectedPrimarySkill") != "test-driven-development":
    raise SystemExit("AUTO risky-code TDD sample must use test-driven-development")
for required in (
    "skip-strict-tdd-route",
    "write-production-code-before-failing-test",
    "skip-producer-consumer-regression",
):
    if required not in tdd_auto_risky.get("mustNotDo", []):
        raise SystemExit(f"AUTO risky-code TDD sample must forbid {required}")
if "tdd-route-auto-strict" not in tdd_auto_risky.get("verificationSignal", ""):
    raise SystemExit("AUTO risky-code TDD sample must require strict route signal")

tdd_off = by_id["tdd-off-no-automatic-tdd"]
if tdd_off.get("expectedPrimarySkill") is not None:
    raise SystemExit("OFF TDD sample must not auto-trigger a primary TDD skill")
for required in (
    "auto-trigger-tdd",
    "treat-off-as-skip-verification",
    "skip-verification-before-completion",
):
    if required not in tdd_off.get("mustNotDo", []):
        raise SystemExit(f"OFF TDD sample must forbid {required}")
if "fresh-completion-evidence" not in tdd_off.get("verificationSignal", ""):
    raise SystemExit("OFF TDD sample must still require completion evidence")

minimal_repair_sample = by_id["minimal-sufficient-repair-not-local-patch"]
if minimal_repair_sample.get("expectedPrimarySkill") != "systematic-debugging":
    raise SystemExit("minimal sufficient repair sample must use systematic-debugging")
for required in (
    "equate-minimal-change-with-smallest-diff",
    "add-fallback-without-owner-check",
    "skip-minimality-check",
    "skip-retirement-trigger",
):
    if required not in minimal_repair_sample.get("mustNotDo", []):
        raise SystemExit(f"minimal sufficient repair sample must forbid {required}")
for required_signal in (
    "minimality-check",
    "correct-owner",
    "bug-class-fixed",
    "retirement",
    "verdict",
):
    if required_signal not in minimal_repair_sample.get("verificationSignal", ""):
        raise SystemExit(f"minimal sufficient repair sample must require {required_signal}")

product_lens_sample = by_id["strong-opinion-product-risk-lens"]
if product_lens_sample.get("expectedPrimarySkill") != "brainstorming":
    raise SystemExit("product risk lens sample must use brainstorming")
for required in (
    "role-persona-theater",
    "override-baseline-evidence",
    "start-implementation-immediately",
):
    if required not in product_lens_sample.get("mustNotDo", []):
        raise SystemExit(f"product risk lens sample must forbid {required}")
for required_signal in ("product-risk-lens", "non-goals", "tradeoff", "decision-needed"):
    if required_signal not in product_lens_sample.get("verificationSignal", ""):
        raise SystemExit(f"product risk lens sample must require {required_signal}")

plan_pressure_sample = by_id["strong-opinion-plan-pressure-test"]
if plan_pressure_sample.get("expectedPrimarySkill") != "writing-plans":
    raise SystemExit("plan pressure test sample must use writing-plans")
for required in (
    "write-tasks-without-owner-contract-retirement-check",
    "turn-pressure-test-into-approval-gate",
    "redesign-approved-spec-without-cause",
):
    if required not in plan_pressure_sample.get("mustNotDo", []):
        raise SystemExit(f"plan pressure test sample must forbid {required}")
for required_signal in ("plan-pressure-test", "owner-contract-retirement", "verification-scope"):
    if required_signal not in plan_pressure_sample.get("verificationSignal", ""):
        raise SystemExit(f"plan pressure test sample must require {required_signal}")

architecture_integrity_sample = by_id["architecture-integrity-higher-level-path"]
if architecture_integrity_sample.get("expectedPrimarySkill") != "writing-plans":
    raise SystemExit("architecture integrity sample must use writing-plans")
if "first-principles-review" not in architecture_integrity_sample.get("allowedSecondarySkills", []):
    raise SystemExit("architecture integrity sample must allow first-principles-review")
for required in (
    "write-tasks-before-architecture-integrity-lens",
    "add-caller-side-fallback-without-higher-owner-check",
    "skip-retirement-or-falsifier",
    "turn-integrity-lens-into-runtime-gate",
):
    if required not in architecture_integrity_sample.get("mustNotDo", []):
        raise SystemExit(f"architecture integrity sample must forbid {required}")
for required_signal in (
    "architecture-integrity-lens",
    "invariant",
    "canonical-owner-contract",
    "responsibility-overlap",
    "higher-level-path",
    "retirement",
    "falsifier",
    "verdict",
):
    if required_signal not in architecture_integrity_sample.get("verificationSignal", ""):
        raise SystemExit(f"architecture integrity sample must require {required_signal}")

review_lens_sample = by_id["strong-opinion-review-findings-first"]
if review_lens_sample.get("expectedPrimarySkill") != "requesting-code-review":
    raise SystemExit("findings-first review sample must use requesting-code-review")
for required in (
    "lead-with-summary-before-findings",
    "treat-review-as-merge-approval",
    "skip-tests-risk-check",
):
    if required not in review_lens_sample.get("mustNotDo", []):
        raise SystemExit(f"findings-first review sample must forbid {required}")
for required_signal in ("findings-first", "bugs-risk-tests", "advisory-review"):
    if required_signal not in review_lens_sample.get("verificationSignal", ""):
        raise SystemExit(f"findings-first review sample must require {required_signal}")

readiness_sample = by_id["strong-opinion-release-readiness-summary"]
if readiness_sample.get("expectedPrimarySkill") != "verification-before-completion":
    raise SystemExit("release readiness sample must use verification-before-completion")
for required in (
    "auto-commit",
    "auto-tag",
    "auto-publish",
    "treat-readiness-as-completion-authority",
):
    if required not in readiness_sample.get("mustNotDo", []):
        raise SystemExit(f"release readiness sample must forbid {required}")
for required_signal in ("readiness-summary", "tests-docs-version-hosts", "residual-risk"):
    if required_signal not in readiness_sample.get("verificationSignal", ""):
        raise SystemExit(f"release readiness sample must require {required_signal}")

retro_sample = by_id["strong-opinion-retro-memory-filter"]
if retro_sample.get("expectedPrimarySkill") != "recording-architecture-decisions":
    raise SystemExit("retro memory filter sample must use recording-architecture-decisions")
for required in (
    "record-unexecuted-ideas-as-accepted-memory",
    "force-adr-for-every-retro",
    "skip-baseline-sync-question",
):
    if required not in retro_sample.get("mustNotDo", []):
        raise SystemExit(f"retro memory filter sample must forbid {required}")
for required_signal in ("retro-memory-filter", "executed-durable-decision", "skip-or-record"):
    if required_signal not in retro_sample.get("verificationSignal", ""):
        raise SystemExit(f"retro memory filter sample must require {required_signal}")

fast_path_persona_sample = by_id["strong-opinion-fast-path-no-persona"]
if fast_path_persona_sample.get("expectedPrimarySkill") is not None:
    raise SystemExit("fast-path strong-opinion no-persona sample must stay fast path")
if fast_path_persona_sample.get("expectedArtifacts"):
    raise SystemExit("fast-path strong-opinion no-persona sample must not expect artifacts")
if fast_path_persona_sample.get("workspacePolicy") != "no-workspace":
    raise SystemExit("fast-path strong-opinion no-persona sample must use no-workspace policy")
for required in (
    "emit-ceo-persona",
    "force-strong-opinion-lens",
    "create-project-workspace-records",
):
    if required not in fast_path_persona_sample.get("mustNotDo", []):
        raise SystemExit(f"fast-path strong-opinion no-persona sample must forbid {required}")

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

layer_required = {
    "layer-stop-local-root-cause": "L3 System",
    "layer-stop-cross-system-contract": "L5 Cross-system Contract",
    "layer-stop-spec-gap": "L7 Spec Gap",
    "layer-stop-user-falsifier-correction": "L5 Cross-system Contract",
}
required_layer_fields = {
    "required",
    "stopLayer",
    "checkedPath",
    "evidenceForStop",
    "excludedLayers",
    "falsifier",
    "userInterventionPoint",
    "nextAction",
}
for sample_id, stop_layer in layer_required.items():
    sample = by_id[sample_id]
    if sample.get("expectedPrimarySkill") != "systematic-debugging":
        raise SystemExit(f"{sample_id} must route to systematic-debugging")
    card = sample.get("layerStopCard")
    if not isinstance(card, dict):
        raise SystemExit(f"{sample_id} must define layerStopCard")
    missing_card_fields = sorted(required_layer_fields - card.keys())
    if missing_card_fields:
        raise SystemExit(f"{sample_id} layerStopCard missing fields: {', '.join(missing_card_fields)}")
    if card.get("required") is not True:
        raise SystemExit(f"{sample_id} layerStopCard must be required")
    if card.get("stopLayer") != stop_layer:
        raise SystemExit(f"{sample_id} must stop at {stop_layer}")
    for field in ("checkedPath", "evidenceForStop", "excludedLayers", "falsifier", "userInterventionPoint", "nextAction"):
        if not card.get(field):
            raise SystemExit(f"{sample_id} layerStopCard {field} must not be empty")
    if "layer-stop-card" not in sample.get("expectedOutputShape", ""):
        raise SystemExit(f"{sample_id} output shape must require layer-stop-card")
    if "layer-stop-card" not in sample.get("verificationSignal", ""):
        raise SystemExit(f"{sample_id} verification signal must require layer-stop-card")
    if "skip-layer-stop-card" not in sample.get("mustNotDo", []):
        raise SystemExit(f"{sample_id} must forbid skipping layer stop card")

correction_sample = by_id["layer-stop-user-falsifier-correction"]
for required in (
    "ignore-user-falsifier",
    "cling-to-initial-l7-diagnosis",
    "skip-correction-readback",
):
    if required not in correction_sample.get("mustNotDo", []):
        raise SystemExit(f"user falsifier correction sample must forbid {required}")
for required_signal in ("user-falsifier", "correction-to-l5", "user-intervention-point"):
    if required_signal not in correction_sample.get("verificationSignal", ""):
        raise SystemExit(f"user falsifier correction sample must require {required_signal}")

no_card_sample = by_id["fast-path-no-layer-stop-card"]
if no_card_sample.get("expectedPrimarySkill") is not None:
    raise SystemExit("fast-path no-card sample must stay on fast path")
if no_card_sample.get("layerStopCard", {}).get("required") is not False:
    raise SystemExit("fast-path no-card sample must mark layerStopCard required false")
if "emit-layer-stop-card" not in no_card_sample.get("mustNotDo", []):
    raise SystemExit("fast-path no-card sample must forbid emitting layer stop card")
if no_card_sample.get("expectedArtifacts"):
    raise SystemExit("fast-path no-card sample must not expect artifacts")
if no_card_sample.get("workspacePolicy") != "no-workspace":
    raise SystemExit("fast-path no-card sample must use no-workspace policy")

print("  [PASS] workflow quality matrix has representative samples and compact contracts")
PY

if (( failures > 0 )); then
    echo ""
    echo "Workflow quality check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workflow quality check passed."
