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
fast_track_en="docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md"
fast_track_zh="docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md"
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
assert_contains "$current_index" "AEGIS_FAST_TRACK_PLAYBOOK.md" \
    "current docs index lists English fast-track playbook"
assert_contains "$current_index" "AEGIS_FAST_TRACK_PLAYBOOK_ZH.md" \
    "current docs index lists Chinese fast-track playbook"
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
if [[ -f "$fast_track_en" ]]; then
    pass "English fast-track playbook exists"
else
    fail "English fast-track playbook exists"
fi
if [[ -f "$fast_track_zh" ]]; then
    pass "Chinese fast-track playbook exists"
else
    fail "Chinese fast-track playbook exists"
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
assert_contains "$readme_en" "AEGIS_FAST_TRACK_PLAYBOOK.md" \
    "English README links English fast-track playbook"
assert_contains "$readme_zh" "AEGIS_FAST_TRACK_PLAYBOOK_ZH.md" \
    "Chinese README links Chinese fast-track playbook"
assert_contains "$fast_track_en" "Grill me" \
    "English fast-track playbook documents grilling trigger"
assert_contains "$fast_track_zh" "审问我" \
    "Chinese fast-track playbook documents grilling trigger"
assert_contains "$fast_track_en" "TDD defaults to" \
    "English fast-track playbook documents default TDD mode"
assert_contains "$fast_track_zh" "TDD 默认" \
    "Chinese fast-track playbook documents default TDD mode"
assert_contains "$fast_track_en" "Quick Install: Give Your Agent One Prompt" \
    "English fast-track playbook puts quick install first"
assert_contains "$fast_track_zh" "极简安装：把一段话交给 Agent" \
    "Chinese fast-track playbook puts quick install first"
assert_contains "$fast_track_en" '"workspaceSupport": "available"' \
    "English fast-track playbook defines complete-install workspace evidence"
assert_contains "$fast_track_zh" '"configStatus": "configured"' \
    "Chinese fast-track playbook defines complete-install config evidence"
assert_contains "$fast_track_en" "copy-only or skills-only install" \
    "English fast-track playbook distinguishes discovery from complete install"
assert_contains "$fast_track_zh" "只复制 skills" \
    "Chinese fast-track playbook distinguishes discovery from complete install"
assert_contains "$fast_track_en" "Lightweight By Design" \
    "English fast-track playbook leads with lightweight progressive depth"
assert_contains "$fast_track_zh" "轻量，但把力量集中在高风险处" \
    "Chinese fast-track playbook leads with lightweight progressive depth"
assert_contains "$fast_track_en" "Typical Standalone Skill Pack" \
    "English fast-track playbook explains category-level differentiation"
assert_contains "$fast_track_zh" "典型独立 Skill Pack" \
    "Chinese fast-track playbook explains category-level differentiation"
assert_contains "$fast_track_en" "Five Engineering Moats" \
    "English fast-track playbook highlights engineering moats"
assert_contains "$fast_track_zh" "五道工程护城河" \
    "Chinese fast-track playbook highlights engineering moats"
assert_contains "$fast_track_en" "L1 Symptom" \
    "English fast-track playbook documents seven-layer diagnosis"
assert_contains "$fast_track_zh" "L7 规格缺口" \
    "Chinese fast-track playbook documents seven-layer diagnosis"
assert_contains "$fast_track_en" "Change Necessity" \
    "English fast-track playbook documents pre-edit change necessity"
assert_contains "$fast_track_zh" "Complexity Delta" \
    "Chinese fast-track playbook documents post-change complexity closure"
assert_contains "$fast_track_en" "Aegis Project Workspace" \
    "English fast-track playbook explains project workspace"
assert_contains "$fast_track_zh" "Aegis 项目工作区" \
    "Chinese fast-track playbook explains project workspace"
assert_contains "$fast_track_en" "ResumeStateHint" \
    "English fast-track playbook explains resumable long-task state"
assert_contains "$fast_track_zh" "docs/aegis/" \
    "Chinese fast-track playbook names the workspace root"
assert_contains "$readme_en" "lightweight operating model" \
    "English README previews lightweight Aegis positioning"
assert_contains "$readme_zh" "为什么轻量" \
    "Chinese README previews lightweight Aegis positioning"

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
assert_contains "$tdd_mode_doc" "default mode is|default.*off|Default \`off\`" \
    "TDD mode doc states default off mode"
assert_contains "$tdd_mode_doc" "strict.*light.*skipped|strict.*skipped.*light|strict.*\`light\`.*skipped" \
    "TDD mode doc defines strict light skipped route"
assert_contains "$tdd_mode_doc" "TDD Route: strict|strict TDD|test-first|RED / GREEN / REFACTOR" \
    "TDD mode doc documents explicit query markers"
assert_contains "$tdd_mode_doc" "verification-before-completion" \
    "TDD mode doc preserves completion verification"
assert_contains "$tdd_mode_doc" "Decision: skipped" \
    "TDD mode doc records off mode without automatic strict routing"
assert_contains "$tdd_mode_doc" "diagnostic reproduction" \
    "TDD mode doc distinguishes diagnostic reproduction from strict RED"
assert_contains "$tdd_mode_doc" "strict RED test" \
    "TDD mode doc reserves production-edit gating for strict RED"
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
assert_contains "$baseline" "default.*off|off.*default" \
    "workflow quality baseline defines default off TDD mode"
assert_contains "$baseline" "auto.*strict.*light.*skipped|strict.*light.*skipped" \
    "workflow quality baseline includes auto TDD routing"
assert_contains "$baseline" "off.*verification-before-completion|verification-before-completion.*off" \
    "workflow quality baseline keeps completion verification on when TDD mode is off"
assert_contains "$baseline" "Pre-Edit Complexity Check" \
    "workflow quality baseline includes pre-edit complexity check"
assert_contains "$baseline" "Pre-Edit Owner-Fit Decision" \
    "workflow quality baseline includes pre-edit owner-fit decision"
assert_contains "$baseline" "Complexity Governance Suggestion" \
    "workflow quality baseline includes complexity governance suggestion"
assert_contains "$baseline" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE" \
    "workflow quality baseline points to complexity governance baseline"
assert_contains "docs/current/AEGIS_WORKFLOW_GUIDE.md" "Final Output Ordering" \
    "English workflow guide frames final output as ordering"
assert_contains "docs/current/AEGIS_WORKFLOW_GUIDE.md" "ordering principle, not a mandatory top-level template" \
    "English workflow guide does not make facts-inferences-conclusions a rigid template"
assert_contains "docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md" "最终输出排序" \
    "Chinese workflow guide frames final output as ordering"
assert_contains "docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md" "信息排序原则，不是强制顶层模板" \
    "Chinese workflow guide does not make facts-inferences-conclusions a rigid template"
assert_contains "$process_doc" "Facts.*Inferences.*Conclusions.*information-ordering principle|information-ordering principle.*Facts.*Inferences.*Conclusions" \
    "process baseline frames facts-inferences-conclusions as ordering principle"
assert_contains "$process_doc" "mandatory top-level response template" \
    "process baseline does not make facts-inferences-conclusions a rigid template"
assert_contains "$process_doc" "Final Output Semantic Slots / Attention Anchors" \
    "process baseline names final output semantic slots and attention anchors"
assert_contains "$process_doc" "findings-first" \
    "process baseline preserves workflow-owned final output structures"
assert_contains "$baseline" "attention anchor" \
    "workflow quality baseline treats required output content as attention anchors"
assert_contains "$baseline" "stealing structural ownership from the active workflow" \
    "workflow quality baseline preserves active workflow output ownership"
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
assert_contains "$baseline" "Execution Readiness View" \
    "workflow quality baseline includes execution readiness view"
assert_contains "$baseline" "gate-passed.*completion-granted.*authoritatively-safe|completion-granted.*gate-passed.*authoritatively-safe" \
    "workflow quality baseline forbids authoritative execution readiness language"
assert_contains "docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md" "Execution Readiness View" \
    "runtime-ready boundary defines execution readiness view"
assert_contains "docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md" "not a new JSON.*artifact type|not a new.*artifact type" \
    "artifact schema baseline keeps execution readiness view out of schema artifacts"
assert_not_contains "docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md" "ExecutionContractDraft" \
    "artifact schema baseline does not add an execution contract artifact"
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
assert_contains "$baseline" "Aegis Visibility Non-Omission Rule" \
    "workflow quality baseline defines non-omittable Aegis visibility"
assert_contains "$baseline" "Aegis Reason Note" \
    "workflow quality baseline defines natural Aegis reason note"
assert_contains "$baseline" "Aegis Visibility" \
    "workflow quality baseline defines owner-workflow Aegis visibility slot"
assert_contains "$baseline" "why Aegis is shaping" \
    "workflow quality baseline explains why Aegis is shaping the task"
assert_contains "$baseline" "first substantive.*Aegis Visibility|Aegis Visibility.*first substantive" \
    "workflow quality baseline requires entry visibility at first substantive stage"
assert_contains "$baseline" "Aegis Impact and Safety Receipt" \
    "workflow quality baseline defines unified impact and safety receipt"
assert_contains "$baseline" "key judgment.*avoided misfix.*boundary held|avoided misfix.*baseline alignment.*complexity control" \
    "workflow quality baseline defines impact and safety receipt fields"
assert_contains "$baseline" "single completion closeout" \
    "workflow quality baseline keeps verification as the completion closeout aggregator"
assert_contains "$baseline" "Readiness Summary.*Trace Digest.*Goal Closure|Trace Digest.*Goal Closure.*ADR Backfill Check" \
    "workflow quality baseline names adjacent completion structures"
assert_contains "$baseline" "must not replace the unified receipt|competing final report owners" \
    "workflow quality baseline prevents adjacent structures from replacing the receipt"
assert_contains "$baseline" "not a new hot-path routing rule|must not make.*using-aegis.*heavier" \
    "workflow quality baseline keeps receipt owner contract out of the hot path"
assert_contains "$baseline" "concise.*not.*drop.*safety fields|reasons to drop the safety fields" \
    "workflow quality baseline forbids dropping receipt safety fields for concision"
assert_contains "$baseline" "user asks.*recovery path.*not a substitute|recovery path.*not a substitute" \
    "workflow quality baseline treats after-the-fact explanation as recovery only"
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
assert_contains "$complexity_baseline" "Pre-Edit Owner-Fit Decision" \
    "complexity baseline defines pre-edit owner-fit decision"
assert_contains "$complexity_baseline" "soft pressure signal" \
    "complexity baseline treats 800 line files as soft pressure"
assert_contains "$complexity_baseline" "1200\\+ line maintained artifact|largest[[:space:]]+5-10%" \
    "complexity baseline defines strong pressure signal"
assert_contains "$complexity_baseline" "new-responsibility" \
    "complexity baseline blocks default in-place new responsibility"
assert_contains "$complexity_baseline" "Completion-Time Complexity Repair Decision" \
    "complexity baseline defines completion-time repair decision"
assert_contains "$complexity_baseline" "govern-now.*follow-up-required.*not-complete|follow-up-required.*not-complete" \
    "complexity baseline defines completion-time repair outcomes"
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
assert_contains "$process_doc" "non-trivial loaded-skill visibility" \
    "process baseline protects loaded-skill visibility from compression"
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
assert_contains "skills/using-aegis/SKILL.md" "first substantive.*user-visible stage|user-visible stage.*first substantive" \
    "using-aegis requires entry visibility before substantive work"
assert_contains "skills/using-aegis/SKILL.md" "do not wait.*user.*ask|user.*ask.*where Aegis was used" \
    "using-aegis forbids delayed visibility readback"
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
assert_contains "skills/brainstorming/SKILL.md" "## Grilling Mode" \
    "brainstorming provides an explicit grilling mode"
assert_contains "skills/brainstorming/SKILL.md" "overrides the normal brainstorming execution" \
    "grilling mode overrides the normal brainstorming checklist"
assert_contains "skills/brainstorming/SKILL.md" 'Suspend `Checklist`, `The Process`, the `Compact output contract`' \
    "grilling mode suspends conflicting normal-flow artifacts"
assert_contains "skills/brainstorming/SKILL.md" "exactly one decision question" \
    "grilling mode asks one decision question per turn"
assert_contains "skills/brainstorming/SKILL.md" "### Grilling Entry Signals" \
    "grilling mode distinguishes direct and soft entry signals"
assert_contains "skills/brainstorming/SKILL.md" "Grill or normal brainstorming" \
    "soft grilling intent asks the user to confirm the mode"
assert_contains "skills/brainstorming/SKILL.md" "at most three independent decision questions" \
    "fast grilling mode batches only independent questions"
assert_contains "skills/brainstorming/SKILL.md" "◆ Grilling Session" \
    "grilling mode has a one-time opening card"
assert_contains "skills/brainstorming/SKILL.md" "PR, diff, or current-code review" \
    "grilling mode routes implementation review to code review"
assert_contains "skills/brainstorming/SKILL.md" "does not grant completion authority" \
    "grilling mode preserves the completion authority boundary"
assert_contains "skills/using-aegis/SKILL.md" "grill me.*brainstorming|brainstorming.*grill me" \
    "using-aegis routes explicit grilling requests without a new skill"
assert_contains "skills/using-aegis/SKILL.md" "grill this plan.*审问我.*盘问我.*拷问我" \
    "using-aegis retains direct grilling aliases"
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
assert_contains "skills/writing-plans/SKILL.md" "Execution Readiness View" \
    "writing-plans renders execution readiness view for handoff"
assert_contains "skills/writing-plans/SKILL.md" "Intent Lock.*Scope Fence.*Baseline Lock|Baseline Lock.*Scope Fence.*Intent Lock" \
    "writing-plans execution readiness view locks intent scope and baseline"
assert_contains "skills/writing-plans/SKILL.md" "not.*GateDecision.*PolicySnapshot.*completion authority|GateDecision.*PolicySnapshot.*completion authority" \
    "writing-plans keeps execution readiness advisory"
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
assert_contains "skills/test-driven-development/SKILL.md" "Pre-Edit Owner-Fit Decision" \
    "test-driven-development includes pre-edit owner-fit decision"
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
assert_contains "skills/using-aegis/SKILL.md" "off=no auto route/load" \
    "using-aegis keeps off mode out of automatic TDD routing and loading"
assert_contains "skills/systematic-debugging/SKILL.md" "TDD Mode: off" \
    "systematic debugging names the off-mode boundary"
assert_contains "skills/systematic-debugging/SKILL.md" "do not require a failing test" \
    "systematic debugging does not force a test-first cycle when off"
assert_contains "skills/writing-plans/SKILL.md" "Strict RED / GREEN steps belong only" \
    "writing plans makes strict TDD steps explicit-route only"
assert_contains "skills/writing-plans/SKILL.md" "TDD Route Guard" \
    "writing plans record route authority before task decomposition"
assert_contains "skills/executing-plans/SKILL.md" "TDD Route Guard" \
    "executing plans verify route authority before task execution"
assert_contains "skills/subagent-driven-development/SKILL.md" "Inherit the parent TDD decision" \
    "subagents inherit rather than force TDD"
assert_contains "skills/writing-skills/SKILL.md" "loading.*test-driven-development" \
    "writing skills does not force-load the TDD skill"
assert_contains "skills/systematic-debugging/SKILL.md" "Quick bug lane" \
    "systematic debugging defines quick bug lane"
assert_contains "skills/systematic-debugging/SKILL.md" "Pre-Edit Complexity Check" \
    "systematic debugging includes pre-edit complexity check"
assert_contains "skills/systematic-debugging/SKILL.md" "Pre-Edit Owner-Fit Decision" \
    "systematic debugging includes pre-edit owner-fit decision"
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
    "systematic debugging main names the layer-stop escalation trigger"
assert_contains "skills/systematic-debugging/SKILL.md" "advanced-debugging-governance.md.*before another fix|before another fix.*advanced-debugging-governance.md" \
    "systematic debugging main directly triggers advanced escalation guidance"
assert_contains "skills/systematic-debugging/advanced-debugging-governance.md" "Current Stop Layer" \
    "advanced debugging reference owns the detailed layer stop card"
assert_contains "skills/systematic-debugging/advanced-debugging-governance.md" "User Intervention Point" \
    "advanced debugging reference owns the intervention field"
assert_contains "skills/systematic-debugging/advanced-debugging-governance.md" "Falsifier:" \
    "advanced debugging reference owns the layer-stop falsifier field"
assert_not_contains "skills/systematic-debugging/SKILL.md" "Current Stop Layer:" \
    "systematic debugging main does not duplicate the detailed layer stop card"
assert_contains "skills/systematic-debugging/SKILL.md" "root-cause-claim-contract.md.*before claiming a root cause|before claiming a root cause.*root-cause-claim-contract.md" \
    "systematic debugging main directly triggers the causal proof contract"
assert_contains "skills/systematic-debugging/root-cause-claim-contract.md" "Falsifier Checked" \
    "root-cause contract owns falsifier proof"
assert_contains "skills/systematic-debugging/root-cause-claim-contract.md" "Pre-Claim Gate Pass" \
    "root-cause contract owns the pre-claim output"
assert_contains "skills/systematic-debugging/root-cause-claim-contract.md" "Causal Topology Gate" \
    "root-cause contract owns causal topology proof"
assert_not_contains "skills/systematic-debugging/advanced-debugging-governance.md" "Pre-Claim Gate Pass:" \
    "advanced debugging reference does not duplicate the causal proof output"
assert_contains "skills/systematic-debugging/advanced-debugging-governance.md" "H1:.*conditional" \
    "advanced debugging reference owns expanded hard-signal governance"
assert_contains "skills/long-task-continuation/SKILL.md" "Planless Slice Lane" \
    "long-task continuation includes planless slice lane"
assert_contains "skills/long-task-continuation/SKILL.md" "Slice Card" \
    "long-task continuation includes slice card"
assert_contains "skills/long-task-continuation/SKILL.md" "parent plan" \
    "long-task continuation reuses parent plan for micro-slices"
assert_contains "skills/long-task-continuation/SKILL.md" "do not create.*plan.*spec|Do not create.*plan.*spec" \
    "long-task continuation prevents per-slice plan/spec files"
assert_contains "skills/long-task-continuation/SKILL.md" "Execution Readiness View" \
    "long-task continuation reads execution readiness view when present"
assert_contains "skills/long-task-continuation/SKILL.md" "intent lock.*scope fence.*baseline lock|baseline lock.*scope fence.*intent lock" \
    "long-task continuation compares resume state against readiness locks"
assert_contains "skills/verification-before-completion/SKILL.md" "Required evidence slots" \
    "verification skill defines required evidence semantic slots"
assert_not_contains "skills/verification-before-completion/SKILL.md" "Command / Check|Exit Status" \
    "verification skill does not require legacy fixed English evidence fields"
assert_contains "skills/verification-before-completion/SKILL.md" "L0 fast-path" \
    "verification skill defines tiny fast-path closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "L1 default|L1 Default" \
    "verification skill defines default non-trivial receipt closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "L2 expanded|L2 Expanded" \
    "verification skill defines triggered expanded closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "Do not output parallel final reports|one completion surface" \
    "verification skill prevents parallel closeout contracts"
assert_contains "skills/verification-before-completion/SKILL.md" "Readiness Summary" \
    "verification skill preserves readiness summary as triggered detail"
assert_contains "skills/verification-before-completion/SKILL.md" "Execution Readiness View" \
    "verification skill accounts for execution readiness view"
assert_contains "skills/verification-before-completion/SKILL.md" "Do not treat the view itself as verification evidence" \
    "verification skill does not treat execution readiness as evidence"
assert_contains "skills/verification-before-completion/SKILL.md" "Natural Aegis closeout" \
    "verification skill summarizes natural Aegis closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "Semantic Slots" \
    "verification skill preserves required semantic slots"
assert_contains "skills/verification-before-completion/SKILL.md" "Natural Surface" \
    "verification skill allows natural user-facing expression"
assert_contains "skills/verification-before-completion/SKILL.md" "Governance Receipt" \
    "verification skill defines governance receipt closeout"
assert_contains "skills/verification-before-completion/SKILL.md" "Aegis Impact and Safety Receipt" \
    "verification skill defines unified impact and safety receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "single completion closeout" \
    "verification skill owns the single completion closeout aggregator"
assert_contains "skills/verification-before-completion/SKILL.md" "must not replace the receipt|competing final report owner" \
    "verification skill prevents adjacent structures from replacing the receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Expanded structures.*inputs.*optional detail cards|optional detail cards.*not competing final report owners" \
    "verification skill treats expanded cards as conditional inputs"
assert_contains "skills/verification-before-completion/SKILL.md" "Key judgment" \
    "verification skill reports key judgment in the unified receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Avoided misfix" \
    "verification skill reports avoided misfix in the unified receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Baseline alignment" \
    "verification skill reports baseline safety in the unified receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity control" \
    "verification skill reports complexity safety in the unified receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Next most valuable verification" \
    "verification skill reports next highest-value verification in the unified receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "Evidence slots fold into.*Evidence strength.*Uncovered risk|Evidence strength.*Uncovered risk" \
    "verification skill folds evidence slots into the compact receipt"
assert_contains "skills/verification-before-completion/SKILL.md" "natural.*semantic slots|semantic slots.*natural" \
    "verification skill treats natural expression as valid when semantic slots are present"
assert_contains "skills/verification-before-completion/SKILL.md" "One natural sentence is enough|one evidence sentence" \
    "verification skill still allows tiny low-risk one-sentence fallback"
assert_contains "skills/verification-before-completion/SKILL.md" "used-skills list" \
    "verification skill rejects used-skills list as visibility substitute"
assert_contains "skills/verification-before-completion/SKILL.md" "held one narrow boundary steady|Boundary held" \
    "verification skill frames Aegis visibility as boundary discipline"
assert_contains "skills/verification-before-completion/SKILL.md" "Aegis Contribution Note" \
    "verification skill avoids self-credit heading by default"
assert_contains "skills/verification-before-completion/SKILL.md" "structured trace.*audit.*debug.*release.*long-task review.*user request|audit.*debug.*release.*long-task review.*user request.*structured trace" \
    "verification skill reserves structured trace for audit or requested cases"
assert_contains "skills/verification-before-completion/SKILL.md" "Trace Digest" \
    "verification skill preserves trace digest as triggered detail"
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
assert_contains "skills/verification-before-completion/SKILL.md" "Do not.*bilingual labels|mixed-language explanations" \
    "verification skill avoids bilingual/mixed-language receipt labels by default"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture Alignment" \
    "verification skill preserves architecture alignment as a compatibility alias"
assert_contains "skills/verification-before-completion/SKILL.md" "Architecture Alignment.*compatibility alias|architecture-scoped compatibility alias" \
    "verification skill does not make architecture alignment a second default card"
assert_contains "skills/verification-before-completion/SKILL.md" "Baseline Alignment" \
    "verification skill preserves baseline alignment trigger"
assert_contains "skills/verification-before-completion/SKILL.md" "Requirement accepted" \
    "verification skill distinguishes task or slice completion from requirement acceptance"
assert_contains "skills/verification-before-completion/SKILL.md" "task or slice completion.*accepted requirement satisfaction|accepted requirement satisfaction.*task or slice completion" \
    "verification skill prevents overstating task or slice completion as requirement acceptance"
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
assert_contains "skills/verification-before-completion/SKILL.md" "ADR Backfill Check" \
    "verification skill preserves ADR backfill as triggered detail"
assert_contains "skills/verification-before-completion/SKILL.md" "recording-architecture-decisions" \
    "verification skill routes ADR lifecycle closure to the dedicated skill when needed"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Delta" \
    "verification skill preserves complexity delta trigger"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Closure" \
    "verification skill preserves complexity closure trigger"
assert_contains "skills/verification-before-completion/SKILL.md" "Completion-Time Complexity Repair Decision" \
    "verification skill references completion-time complexity repair decision"
assert_contains "skills/verification-before-completion/SKILL.md" "Complexity Governance Suggestion" \
    "verification skill references complexity governance suggestion"
assert_contains "skills/verification-before-completion/SKILL.md" "Major Complexity Alert" \
    "verification skill references major complexity alert"
assert_contains "skills/verification-before-completion/SKILL.md" "using-aegis/references/complexity-governance.md" \
    "verification skill points to shared complexity reference"
assert_contains "skills/verification-before-completion/SKILL.md" "AEGIS_COMPLEXITY_GOVERNANCE_BASELINE" \
    "verification skill points to complexity baseline owner"
assert_not_contains "skills/verification-before-completion/SKILL.md" "Files newly crossing 800 lines|Largest touched function/block" \
    "verification skill does not inline the full complexity expanded card"
assert_contains "skills/verification-before-completion/SKILL.md" "Retirement Closure" \
    "verification skill preserves retirement closure as triggered detail"
assert_contains "skills/verification-before-completion/SKILL.md" "Anti-Entropy Declaration" \
    "verification skill preserves anti-entropy declaration as triggered detail"
assert_contains "skills/verification-before-completion/SKILL.md" "Data Destruction Guard" \
    "verification skill preserves data destruction guard as triggered detail"
assert_contains "skills/verification-before-completion/SKILL.md" "anti-entropy-governance" \
    "verification skill delegates anti-entropy decision surface"
assert_contains "skills/verification-before-completion/SKILL.md" "assent such as" \
    "verification skill rejects broad assent as destructive confirmation"
assert_contains "skills/verification-before-completion/SKILL.md" "report the task as not" \
    "verification skill blocks completion after unconfirmed persistent-state deletion"
assert_contains "skills/verification-before-completion/SKILL.md" "retention reason" \
    "verification skill requires retention reason"
assert_contains "skills/verification-before-completion/SKILL.md" "retirement trigger" \
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
assert_contains "skills/executing-plans/SKILL.md" "Pre-Edit Owner-Fit Decision" \
    "executing-plans re-checks owner fit before source edits"
assert_contains "skills/executing-plans/SKILL.md" "Complexity Budget" \
    "executing-plans re-checks complexity budget before source edits"
assert_contains "skills/executing-plans/SKILL.md" "Execution Readiness View" \
    "executing-plans reads execution readiness view before implementation"
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
if [[ -e "agents/code-reviewer.md" ]]; then
    fail "retired root code reviewer agent stays deleted"
else
    pass "retired root code reviewer agent stays deleted"
fi
assert_not_contains "skills/requesting-code-review/SKILL.md" "aegis:code-reviewer" \
    "requesting code review no longer depends on retired named agent type"
assert_contains "skills/requesting-code-review/SKILL.md" "requesting-code-review/code-reviewer.md" \
    "requesting code review uses canonical reviewer template"
assert_contains "skills/subagent-driven-development/code-quality-reviewer-prompt.md" "general-purpose reviewer" \
    "subagent-driven code quality review uses generic reviewer subagent"

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
assert_contains "skills/executing-plans/SKILL.md" "verification-driven unplanned edit" \
    "executing plans reads retained direction before unplanned edits"
assert_contains "skills/executing-plans/SKILL.md" "systematic-debugging.*before editing" \
    "executing plans keeps direction judgment in systematic debugging"
assert_contains "skills/executing-plans/SKILL.md" "root stays on the normal plan path" \
    "executing plans preserves the independent-root quick path"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "locally green patch-shape state remains bounded" \
    "workflow quality reuses existing checkpoint artifacts"
assert_contains "docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md" "carrier naming alone cannot reset the direction" \
    "workflow quality compares repair direction semantically"

"${PYTHON_CMD[@]}" tests/helpers/validate_workflow_quality_matrix.py "$matrix"
if (( failures > 0 )); then
    echo ""
    echo "Workflow quality check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Workflow quality check passed."
