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
complexity_baseline="docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md"
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
assert_contains "$current_index" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md" \
    "current docs index lists complexity governance baseline"
assert_contains "$current_index" "AEGIS_TDD_MODE.md" \
    "current docs index lists TDD mode baseline"
if [[ -f "$complexity_baseline" ]]; then
    pass "complexity governance baseline exists"
else
    fail "complexity governance baseline exists"
fi
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
assert_contains "$process_doc" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE" \
    "process baseline points to complexity governance baseline"
assert_contains "$trigger_doc" "workflow-quality" \
    "trigger health references workflow-quality samples"
assert_contains "$readme_en" "Workflow Quality" \
    "English README mentions workflow quality"
assert_contains "$readme_zh" "Workflow Quality" \
    "Chinese README mentions workflow quality"
assert_contains "$readme_zh" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE" \
    "Chinese README mentions complexity governance baseline"

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
    "Strong-Opinion Review Lenses" \
    "Baseline Role Alignment" \
    "Aegis Invocation Visibility" \
    "Semantic Slots and Natural Surface"; do
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
assert_contains "$baseline" "Existence Check" \
    "workflow quality baseline includes pre-addition existence check"
assert_contains "$process_doc" "Pre-Addition Minimality" \
    "process baseline defines pre-addition minimality"
assert_contains "$process_doc" "AEGIS_MINIMALITY_REFERENCE" \
    "process baseline points to minimality reference"
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
assert_contains "$baseline" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE" \
    "workflow quality baseline points to complexity governance baseline"
assert_contains "$baseline" "Retirement Closure" \
    "workflow quality baseline includes retirement closure"
assert_contains "$baseline" "Anti-Entropy Declaration" \
    "workflow quality baseline includes anti-entropy declaration"
assert_contains "$baseline" "Data Destruction Guard" \
    "workflow quality baseline includes data destruction guard"
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
assert_contains "$baseline" "Baseline Role Alignment" \
    "workflow quality baseline includes baseline role alignment"
assert_contains "$baseline" "Baseline Alignment" \
    "workflow quality baseline includes baseline alignment compact output"
assert_contains "$baseline" "Product / Requirement Baseline" \
    "workflow quality baseline names product requirement baseline role"
assert_contains "$baseline" "Architecture / Runtime Boundary Baseline" \
    "workflow quality baseline names architecture runtime boundary baseline role"
assert_contains "$baseline" "Design Defect" \
    "workflow quality baseline includes design defect term"
assert_contains "$baseline" "Implementation Drift" \
    "workflow quality baseline includes implementation drift term"
assert_contains "$baseline" "scope: requirements | architecture | both" \
    "workflow quality baseline includes defect drift scope taxonomy"
assert_contains "$baseline" "Aegis Invocation Visibility" \
    "workflow quality baseline includes Aegis invocation visibility"
assert_contains "$baseline" "Aegis Reason Note" \
    "workflow quality baseline defines natural Aegis reason note"
assert_contains "$baseline" "Aegis Visibility" \
    "workflow quality baseline defines owner-workflow Aegis visibility slot"
assert_contains "$baseline" "why Aegis is shaping" \
    "workflow quality baseline explains why Aegis is shaping the task"
assert_contains "$baseline" "structured trace.*audit.*debug.*release.*long-task review.*user request|audit.*debug.*release.*long-task review.*user request.*structured trace" \
    "workflow quality baseline reserves structured trace for audit or requested cases"
assert_contains "$baseline" "Trace Digest" \
    "workflow quality baseline defines on-demand trace digest"
assert_contains "$baseline" "execution trace.*evidence chain.*retrieval chain|evidence chain.*retrieval chain.*rule effects" \
    "workflow quality baseline covers execution, evidence, retrieval, and rule-effect trace"
assert_contains "$baseline" "measured.*observed.*inferred.*declared.*unknown" \
    "workflow quality baseline labels trace confidence and truth source"
assert_contains "$baseline" "Trace Capability Matrix" \
    "workflow quality baseline defines host trace capability matrix"
assert_contains "$baseline" "redaction" \
    "workflow quality baseline requires trace redaction"
assert_contains "$baseline" "do not expose.*chain-of-thought|raw internal reasoning" \
    "workflow quality baseline forbids raw chain-of-thought exposure"
assert_contains "$baseline" "Trace Overhead Budget" \
    "workflow quality baseline defines trace overhead budget"
assert_not_contains "$baseline" "Invocation: <skill-name> \| fast-path \| none" \
    "workflow quality baseline avoids invocation tuple as default user-facing shape"
assert_not_contains "$baseline" "Aegis Usage Trace: used skills, stage handoffs" \
    "workflow quality baseline avoids stiff default usage trace"
assert_contains "$baseline" "not runtime authority|not.*runtime gate" \
    "workflow quality baseline keeps invocation visibility advisory"
assert_contains "$process_doc" "Strong-Opinion Review Lenses" \
    "process baseline references strong-opinion review lenses"
assert_contains "$process_doc" "Architecture Integrity Lens" \
    "process baseline references architecture integrity lens"
assert_contains "$process_doc" "Micro-Slice Artifact Budget" \
    "process baseline references micro-slice artifact budget"
assert_contains "$process_doc" "Baseline Role Alignment" \
    "process baseline defines baseline role alignment"
assert_contains "$process_doc" "preserving externally observable behavior and published contracts" \
    "process baseline narrows backward compatibility to external behavior"
assert_contains "$process_doc" "persistent-state" \
    "process baseline defines persistent-state confirmation-first boundary"
if [[ -f "skills/anti-entropy-governance/SKILL.md" ]]; then
    pass "anti-entropy governance skill exists"
else
    fail "anti-entropy governance skill exists"
fi
assert_contains "$process_doc" "Product / Requirement Baseline" \
    "process baseline names product requirement baseline role"
assert_contains "$process_doc" "Architecture / Runtime Boundary Baseline" \
    "process baseline names architecture runtime boundary baseline role"
assert_contains "$process_doc" "Design Defect" \
    "process baseline defines design defect"
assert_contains "$process_doc" "Implementation Drift" \
    "process baseline defines implementation drift"
assert_contains "$process_doc" "scope: requirements | architecture | both" \
    "process baseline defines defect drift scope taxonomy"
assert_contains "$process_doc" "Architecture Defect.*architecture-scoped.*Design Defect|architecture-scoped.*Design Defect.*Architecture Defect" \
    "process baseline keeps architecture defect compatibility alias"
assert_contains "$process_doc" "Architecture Drift.*architecture-scoped.*Implementation Drift|architecture-scoped.*Implementation Drift.*Architecture Drift" \
    "process baseline keeps architecture drift compatibility alias"
assert_contains "$complexity_baseline" "Complexity Budget" \
    "complexity baseline defines complexity budget"
assert_contains "$complexity_baseline" "Complexity Closure" \
    "complexity baseline defines complexity closure"
assert_contains "$complexity_baseline" "Major Complexity Alert" \
    "complexity baseline defines major complexity alert"
assert_contains "$complexity_baseline" "Files newly crossing 800 lines" \
    "complexity baseline defines file threshold complexity signal"
assert_contains "$complexity_baseline" "Largest touched function/block" \
    "complexity baseline defines block-level complexity signal"
assert_contains "$complexity_baseline" "maintained test source file" \
    "complexity baseline governs maintained test source files"
assert_contains "$complexity_baseline" "Retired branches/fallbacks/adapters" \
    "complexity baseline ties complexity delta to retirement"
assert_contains "$process_doc" "dual-baseline.*bootstrap template|Do not regress to a flat repo-inventory checklist" \
    "process baseline distinguishes bootstrap baselines from flat repo inventory"
assert_contains "$process_doc" "Aegis Reason Note" \
    "process baseline references natural Aegis reason note"
assert_contains "$process_doc" "structured trace.*audit.*debug.*release.*long-task review.*user request|audit.*debug.*release.*long-task review.*user request.*structured trace" \
    "process baseline reserves structured trace for audit or requested cases"

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
assert_contains "skills/using-aegis/SKILL.md" "Aegis Reason Note" \
    "using-aegis exposes natural Aegis reason note"
assert_contains "skills/using-aegis/SKILL.md" "why Aegis is shaping" \
    "using-aegis explains why Aegis is shaping the next step"
assert_contains "skills/using-aegis/SKILL.md" "structured trace.*audit.*debug.*release.*long-task review.*asked|audit.*debug.*release.*long-task review.*asked.*structured trace" \
    "using-aegis reserves structured trace for audit or requested cases"
assert_contains "skills/using-aegis/SKILL.md" "Trace Digest" \
    "using-aegis knows the on-demand trace digest surface"
assert_contains "skills/using-aegis/SKILL.md" "trace.*does not.*route|route.*not.*trace" \
    "using-aegis keeps trace from participating in routing"
assert_not_contains "skills/using-aegis/SKILL.md" "Invocation: <skill-name> \| fast-path \| none" \
    "using-aegis avoids invocation tuple as default user-facing shape"
assert_not_contains "skills/using-aegis/SKILL.md" "Stage handoff" \
    "using-aegis avoids stiff stage handoff wording"
assert_contains "skills/using-aegis/SKILL.md" "ArchitectureReviewRequired" \
    "using-aegis marks architecture review required signal"

for skill_file in \
    "skills/goal-framing/SKILL.md" \
    "skills/brainstorming/SKILL.md" \
    "skills/writing-plans/SKILL.md" \
    "skills/systematic-debugging/SKILL.md" \
    "skills/test-driven-development/SKILL.md" \
    "skills/first-principles-review/SKILL.md" \
    "skills/executing-plans/SKILL.md" \
    "skills/long-task-continuation/SKILL.md" \
    "skills/requesting-code-review/SKILL.md" \
    "skills/recording-architecture-decisions/SKILL.md" \
    "skills/anti-entropy-governance/SKILL.md" \
    "skills/verification-before-completion/SKILL.md"; do
    assert_contains "$skill_file" "Aegis Visibility" \
        "$skill_file exposes owner-workflow Aegis visibility"
done

assert_contains "skills/goal-framing/SKILL.md" "TaskIntentDraft" \
    "goal-framing exposes task intent goal frame"
assert_contains "skills/brainstorming/SKILL.md" "Compact output contract" \
    "brainstorming exposes compact output contract"
assert_contains "skills/brainstorming/SKILL.md" "Product Risk Lens" \
    "brainstorming includes product risk lens"
assert_contains "skills/brainstorming/SKILL.md" "Plan-Time Complexity Check" \
    "brainstorming includes plan-time complexity check"
assert_contains "skills/brainstorming/SKILL.md" "Existence Check" \
    "brainstorming includes pre-addition existence check"
assert_contains "skills/brainstorming/SKILL.md" "AEGIS_MINIMALITY_REFERENCE" \
    "brainstorming points to minimality reference"
assert_contains "skills/brainstorming/SKILL.md" "Complexity Budget" \
    "brainstorming includes complexity budget"
assert_contains "skills/brainstorming/SKILL.md" "Architecture Integrity Lens" \
    "brainstorming includes architecture integrity lens"
assert_contains "skills/brainstorming/SKILL.md" "Baseline Role Alignment" \
    "brainstorming includes baseline role alignment"
assert_contains "skills/brainstorming/SKILL.md" "Requirement Ready Check" \
    "brainstorming includes requirement ready check"
assert_contains "skills/brainstorming/SKILL.md" "needs-acceptance-criteria" \
    "brainstorming surfaces missing acceptance criteria"
assert_contains "skills/brainstorming/SKILL.md" "Product / Requirement Baseline" \
    "brainstorming template names product requirement baseline role"
assert_contains "skills/brainstorming/SKILL.md" "Architecture / Runtime Boundary Baseline" \
    "brainstorming template names architecture runtime boundary baseline role"
assert_contains "skills/brainstorming/SKILL.md" "initial dual-baseline snapshot|dual baselines" \
    "brainstorming template frames the first baseline as dual-baseline bootstrap"
assert_contains "skills/brainstorming/SKILL.md" "Non-negotiables" \
    "brainstorming template requires non-negotiables in the initial baseline"
assert_contains "skills/brainstorming/SKILL.md" "Product Non-goals" \
    "brainstorming template requires product non-goals in the initial baseline"
assert_contains "skills/brainstorming/SKILL.md" "Architecture Non-negotiables" \
    "brainstorming template requires architecture non-negotiables in the initial baseline"
assert_contains "skills/brainstorming/SKILL.md" "Design Defect" \
    "brainstorming template includes design defect"
assert_contains "skills/brainstorming/SKILL.md" "Implementation Drift" \
    "brainstorming template includes implementation drift"
assert_contains "skills/brainstorming/SKILL.md" "scope: requirements | architecture | both" \
    "brainstorming template includes defect drift scope taxonomy"
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
assert_contains "skills/writing-plans/SKILL.md" "Existence Check" \
    "writing-plans includes pre-addition existence check"
assert_contains "skills/writing-plans/SKILL.md" "AEGIS_MINIMALITY_REFERENCE" \
    "writing-plans points to minimality reference"
assert_contains "skills/writing-plans/SKILL.md" "Plan-Time Complexity Check" \
    "writing-plans includes plan-time complexity check"
assert_contains "skills/writing-plans/SKILL.md" "Complexity Budget" \
    "writing-plans includes complexity budget"
assert_contains "skills/writing-plans/SKILL.md" "owner / contract / retirement" \
    "writing-plans pressure-tests owner contract retirement risk"
assert_contains "skills/writing-plans/SKILL.md" "Architecture Integrity Lens" \
    "writing-plans includes architecture integrity lens"
assert_contains "skills/writing-plans/SKILL.md" "Requirement Ready Check" \
    "writing-plans includes requirement ready check before task decomposition"
assert_contains "skills/writing-plans/SKILL.md" "do not create implementation tasks" \
    "writing-plans blocks implementation tasks when requirements are not ready"
assert_contains "skills/writing-plans/SKILL.md" "Change Necessity" \
    "writing-plans surfaces change necessity before code-edit tasks"
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
assert_contains "skills/test-driven-development/SKILL.md" "Complexity Budget" \
    "test-driven-development includes complexity budget"
assert_contains "skills/test-driven-development/SKILL.md" "TDD Mode" \
    "test-driven-development includes TDD mode"
assert_contains "skills/test-driven-development/SKILL.md" "TDD Route" \
    "test-driven-development includes TDD route"
assert_contains "skills/test-driven-development/SKILL.md" "Change Necessity" \
    "test-driven-development checks change necessity before strict code edits"
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
assert_contains "skills/systematic-debugging/SKILL.md" "Minimality Check" \
    "systematic debugging includes minimality check"
assert_contains "skills/systematic-debugging/SKILL.md" "Change Necessity" \
    "systematic debugging checks change necessity before repair code"
assert_contains "skills/systematic-debugging/SKILL.md" "Quick bug lane.*Change Necessity.*before source edits" \
    "systematic debugging quick bug lane requires change necessity before source edits"
assert_contains "skills/systematic-debugging/SKILL.md" "explicit decision token" \
    "systematic debugging quick bug lane requires explicit code-change decision"
assert_contains "skills/systematic-debugging/SKILL.md" "Decision: code-change" \
    "systematic debugging quick bug lane names code-change decision token"
assert_contains "$baseline" "explicit decision token.*Decision: code-change" \
    "workflow quality baseline requires explicit quick bug decision token"
assert_contains "skills/systematic-debugging/SKILL.md" "AEGIS_MINIMALITY_REFERENCE" \
    "systematic debugging points to minimality reference"
assert_contains "skills/systematic-debugging/SKILL.md" "Layer Stop Card" \
    "systematic debugging defines layer stop card"
assert_contains "skills/systematic-debugging/SKILL.md" "User Intervention Point" \
    "systematic debugging exposes user intervention point"
assert_contains "skills/systematic-debugging/SKILL.md" "Falsifier" \
    "systematic debugging exposes falsifier for layer stop"
assert_contains "skills/systematic-debugging/SKILL.md" "Pre-Claim Gate" \
    "systematic debugging defines pre-claim gate before claiming root cause"
assert_contains "skills/systematic-debugging/SKILL.md" "Causal Topology Gate" \
    "systematic debugging defines causal topology gate for multi-root classification"
assert_contains "skills/long-task-continuation/SKILL.md" "Planless Slice Lane" \
    "long-task continuation includes planless slice lane"
assert_contains "skills/long-task-continuation/SKILL.md" "Slice Card" \
    "long-task continuation includes slice card"
assert_contains "skills/long-task-continuation/SKILL.md" "parent plan" \
    "long-task continuation reuses parent plan for micro-slices"
assert_contains "skills/long-task-continuation/SKILL.md" "do not create.*plan.*spec|Do not create.*plan.*spec" \
    "long-task continuation prevents per-slice plan/spec files"
assert_contains "skills/verification-before-completion/SKILL.md" "Required evidence slots" \
    "verification skill defines required evidence semantic slots"
assert_not_contains "skills/verification-before-completion/SKILL.md" "Command / Check|Exit Status" \
    "verification skill does not require legacy fixed English evidence fields"
assert_contains "skills/verification-before-completion/SKILL.md" "Readiness Summary" \
    "verification skill defines readiness summary"
assert_contains "skills/verification-before-completion/SKILL.md" "Natural Aegis closeout" \
    "verification skill summarizes natural Aegis closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "Semantic Slots" \
    "verification skill preserves required semantic slots"
assert_contains "skills/verification-before-completion/SKILL.md" "Natural Surface" \
    "verification skill allows natural user-facing expression"
assert_contains "skills/verification-before-completion/SKILL.md" "Governance Receipt" \
    "verification skill defines governance receipt closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "natural.*semantic slots|semantic slots.*natural" \
    "verification skill treats natural expression as valid when semantic slots are present"
assert_contains "skills/verification-before-completion/SKILL.md" "one sentence" \
    "verification skill keeps Aegis closeout concise by default"
assert_contains "skills/verification-before-completion/SKILL.md" "hold one boundary steady" \
    "verification skill frames Aegis visibility as boundary discipline"
assert_contains "skills/verification-before-completion/SKILL.md" "Do not default to a visible.*Aegis Contribution Note" \
    "verification skill avoids self-credit heading by default"
assert_contains "skills/verification-before-completion/SKILL.md" "structured trace.*audit.*debug.*release.*long-task review.*user request|audit.*debug.*release.*long-task review.*user request.*structured trace" \
    "verification skill reserves structured trace for audit or requested cases"
assert_contains "skills/verification-before-completion/SKILL.md" "Trace Digest" \
    "verification skill defines on-demand trace digest closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "measured.*observed.*inferred.*declared.*unknown" \
    "verification skill labels trace confidence source"
assert_contains "skills/verification-before-completion/SKILL.md" "redaction" \
    "verification skill requires trace redaction"
assert_not_contains "skills/verification-before-completion/SKILL.md" "Used skills" \
    "verification skill avoids stiff used-skills card by default"
assert_not_contains "skills/verification-before-completion/SKILL.md" "Stage handoffs" \
    "verification skill avoids stiff stage-handoffs card by default"
assert_contains "skills/verification-before-completion/SKILL.md" "not completion authority" \
    "verification skill keeps Aegis contribution advisory"
assert_contains "skills/verification-before-completion/SKILL.md" "commit, tag, publish, merge, or release" \
    "verification readiness does not authorize publishing actions"
assert_contains "skills/verification-before-completion/SKILL.md" "User-Language Output" \
    "verification skill defines user-language output rule"
assert_contains "skills/verification-before-completion/SKILL.md" "section labels, field labels, and explanatory prose" \
    "verification skill localizes user-facing completion cards"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture Alignment" \
    "verification skill defines architecture alignment check"
assert_contains "skills/verification-before-completion/SKILL.md" "Baseline Alignment" \
    "verification skill defines baseline alignment check"
assert_contains "skills/verification-before-completion/SKILL.md" "Requirement / acceptance alignment" \
    "verification skill checks requirement acceptance alignment"
assert_contains "skills/verification-before-completion/SKILL.md" "Requirement Ready Check" \
    "verification skill reports requirement ready check"
assert_contains "skills/verification-before-completion/SKILL.md" "Requirement acceptance boundary" \
    "verification skill distinguishes task or slice completion from requirement acceptance"
assert_contains "skills/verification-before-completion/SKILL.md" "task or slice completion.*accepted requirement satisfaction|accepted requirement satisfaction.*task or slice completion" \
    "verification skill prevents overstating task or slice completion as requirement acceptance"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture / owner / contract alignment" \
    "verification skill checks architecture owner contract alignment"
assert_contains "skills/verification-before-completion/SKILL.md" "Product / Requirement Baseline" \
    "verification skill names product requirement baseline role"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture / Runtime Boundary Baseline" \
    "verification skill names architecture runtime boundary baseline role"
assert_contains "skills/verification-before-completion/SKILL.md" "Design Defect" \
    "verification skill includes design defect result"
assert_contains "skills/verification-before-completion/SKILL.md" "Implementation Drift" \
    "verification skill includes implementation drift result"
assert_contains "skills/verification-before-completion/SKILL.md" "scope: requirements | architecture | both" \
    "verification skill includes defect drift scope taxonomy"
assert_contains "skills/verification-before-completion/SKILL.md" "Integrity Residual Risk" \
    "verification skill reports architecture integrity residual risk when triggered"
assert_contains "skills/verification-before-completion/SKILL.md" "ADR Backfill Check" \
    "verification skill defines ADR backfill check"
assert_contains "skills/verification-before-completion/SKILL.md" "recording-architecture-decisions" \
    "verification skill routes ADR lifecycle closure to the dedicated skill when needed"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Delta" \
    "verification skill defines complexity delta check"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Closure" \
    "verification skill defines complexity closure"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Governance Suggestion" \
    "verification skill defines complexity governance suggestion"
assert_contains "skills/verification-before-completion/SKILL.md" "Major Complexity Alert" \
    "verification skill defines major complexity alert"
assert_contains "skills/verification-before-completion/SKILL.md" "Files newly crossing 800 lines" \
    "verification skill checks file threshold crossings"
assert_contains "skills/verification-before-completion/SKILL.md" "Largest touched function/block" \
    "verification skill checks block-level complexity"
assert_contains "skills/verification-before-completion/SKILL.md" "Retirement Closure" \
    "verification skill defines retirement closure"
assert_contains "skills/verification-before-completion/SKILL.md" "Anti-Entropy Declaration" \
    "verification skill defines anti-entropy declaration"
assert_contains "skills/verification-before-completion/SKILL.md" "Data Destruction Guard" \
    "verification skill defines data destruction guard"
assert_contains "skills/verification-before-completion/SKILL.md" "assent such as" \
    "verification skill rejects broad assent as destructive confirmation"
assert_contains "skills/verification-before-completion/SKILL.md" "report the task as not" \
    "verification skill blocks completion after unconfirmed persistent-state deletion"
assert_contains "skills/verification-before-completion/SKILL.md" "Retention reason" \
    "verification skill requires retention reason"
assert_contains "skills/verification-before-completion/SKILL.md" "Retirement trigger" \
    "verification skill requires retirement trigger"
assert_contains "docs/current/AEGIS_PROCESS_BASELINE.md" "Requirement Ready Check" \
    "process baseline defines requirement ready check"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "Requirement acceptance boundary" \
    "workflow quality baseline distinguishes requirement acceptance boundary"
assert_contains "skills/anti-entropy-governance/SKILL.md" "confirmation-first" \
    "anti-entropy skill defines confirmation-first path"
assert_contains "skills/anti-entropy-governance/SKILL.md" "Data Destruction Guard" \
    "anti-entropy skill defines data destruction guard"
assert_contains "skills/anti-entropy-governance/SKILL.md" "generic agreement" \
    "anti-entropy skill rejects generic agreement as confirmation"
assert_contains "skills/anti-entropy-governance/SKILL.md" "Do not load this directly from .*using-aegis.*unless explicitly requested" \
    "anti-entropy skill stays out of the global hot path"
assert_contains "skills/long-task-continuation/SKILL.md" "Minimal Reporting Shape" \
    "long-task continuation keeps minimal reporting shape"
assert_contains "skills/executing-plans/SKILL.md" "Pre-Edit Complexity Check" \
    "executing-plans re-checks complexity before source edits"
assert_contains "skills/executing-plans/SKILL.md" "Complexity Budget" \
    "executing-plans re-checks complexity budget before source edits"
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
assert_contains "skills/requesting-code-review/SKILL.md" "legacy phrase mapping" \
    "requesting code review maps legacy defect drift phrases to shared vocabulary"
assert_contains "skills/requesting-code-review/SKILL.md" "requirements/product alignment" \
    "requesting code review checks requirements product alignment"
assert_contains "skills/requesting-code-review/SKILL.md" "Design Defect / Implementation Drift" \
    "requesting code review uses aligned defect drift terminology"
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
assert_contains "skills/requesting-code-review/code-reviewer.md" "legacy phrasing appears" \
    "code reviewer template maps legacy defect drift phrasing"
assert_contains "skills/requesting-code-review/code-reviewer.md" "requirements/product alignment" \
    "code reviewer template checks requirements product alignment"
assert_contains "skills/requesting-code-review/code-reviewer.md" "Design Defect / Implementation Drift" \
    "code reviewer template uses aligned defect drift terminology"
assert_contains "agents/code-reviewer.md" "skills/requesting-code-review/code-reviewer.md" \
    "named code reviewer points to canonical skill template path"
assert_contains "agents/code-reviewer.md" "canonical Aegis code" \
    "named code reviewer identifies canonical Aegis review checklist"
assert_contains "agents/code-reviewer.md" "host compatibility projection" \
    "named code reviewer is marked as compatibility projection"
assert_contains "agents/code-reviewer.md" "Map legacy phrasing" \
    "named code reviewer mirrors legacy defect drift alias handling"
assert_contains "agents/code-reviewer.md" "requirements/product alignment" \
    "named code reviewer mirrors requirements product alignment"
assert_contains "agents/code-reviewer.md" "Design Defect / Implementation Drift" \
    "named code reviewer mirrors aligned defect drift terminology"
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

assert_not_contains "skills/using-aegis/SKILL.md" "Required evidence slots|Governance Receipt" \
    "using-aegis does not absorb verification output contract"
assert_not_contains "skills/using-aegis/SKILL.md" "Design Spec.*Design Spec.*Design Spec" \
    "using-aegis hot path avoids repeated design-spec ceremony"
assert_contains "skills/using-aegis/SKILL.md" "owner workflow.*Change Necessity" \
    "using-aegis delegates change necessity to owner workflows"
assert_contains "skills/using-aegis/SKILL.md" "Bug, failure, regression, or unexpected behavior routes to.*systematic-debugging" \
    "using-aegis routes bug fast path to systematic-debugging"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "does not stop at a.*using-aegis.*fast path.*systematic-debugging|using-aegis.*fast path.*systematic-debugging" \
    "workflow quality baseline keeps bug repairs out of using-aegis-only fast path"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "Change Necessity Before Source Edits" \
    "workflow quality baseline defines change necessity before source edits"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "behavioral.*not.*prompt|prompt.*names.*Existence Check" \
    "workflow quality baseline treats addition checks as behavior-triggered"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "natural code-necessity|Code necessity check" \
    "workflow quality baseline requires natural code necessity readback"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "any new source-code path" \
    "workflow quality baseline applies change necessity to any new source-code path"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "tiny helper|small guard" \
    "workflow quality baseline rejects tiny-helper or small-guard exemptions"
assert_contains "docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md" "Trace Digest" \
    "agentic benchmark baseline covers trace digest quality"
assert_contains "docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md" "skill-call-stability|trace-digest-coverage|rule-effect-attribution" \
    "agentic benchmark baseline includes trace and rule-effect metrics"
assert_contains "skills/systematic-debugging/SKILL.md" "behavior-triggered.*not prompt-triggered" \
    "systematic debugging makes change necessity behavior-triggered"
assert_contains "skills/systematic-debugging/SKILL.md" "any new source-code path" \
    "systematic debugging applies change necessity to any new source-code path"
assert_contains "skills/systematic-debugging/SKILL.md" "Existence Check" \
    "systematic debugging checks requested fallback additions before editing"
assert_contains "skills/writing-plans/SKILL.md" "behavior-triggered.*not prompt-triggered" \
    "writing plans makes change necessity behavior-triggered"
assert_contains "skills/writing-plans/SKILL.md" "any new source-code path" \
    "writing plans applies change necessity to any new source-code path"
assert_contains "skills/test-driven-development/SKILL.md" "behavior-triggered.*not prompt-triggered" \
    "TDD makes change necessity behavior-triggered"
assert_contains "skills/test-driven-development/SKILL.md" "any new source-code path" \
    "TDD applies change necessity to any new source-code path"
assert_contains "skills/executing-plans/SKILL.md" "Change Necessity" \
    "executing plans carries change necessity during plan execution"
assert_contains "skills/executing-plans/SKILL.md" "any new source-code path" \
    "executing plans applies change necessity to any new source-code path"

"${PYTHON_CMD[@]}" tests/helpers/validate_workflow_quality_matrix.py "$matrix"
if (( failures > 0 )); then
    echo ""
    echo "Workflow quality check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workflow quality check passed."
