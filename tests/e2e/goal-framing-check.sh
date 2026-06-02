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

echo "=== Goal Framing Check ==="

skill="skills/goal-framing/SKILL.md"
using_aegis="skills/using-aegis/SKILL.md"
subagent_skill="skills/subagent-driven-development/SKILL.md"
implementer_prompt="skills/subagent-driven-development/implementer-prompt.md"
verification_skill="skills/verification-before-completion/SKILL.md"
artifact_doc="docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md"
runtime_doc="docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md"
workflow_doc="docs/current/AEGIS_WORKFLOW_GUIDE.md"
workflow_doc_zh="docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md"
workflow_quality="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
readme_en="README.md"
readme_zh="README.zh-CN.md"
host_docs=(
    "docs/README.codex.md"
    "docs/README.opencode.md"
    "docs/README.claude-code.md"
    "docs/README.cc-gui.md"
    "docs/README.codebuddy.md"
    "docs/README.deepseek-tui.md"
    "docs/README.trae.md"
    "docs/README.copilot.md"
    "docs/README.qoder.md"
    "docs/README.pi.md"
    "docs/README.openclaw.md"
    "docs/README.hermes-agent.md"
)
task_intent_fixture="tests/e2e/fixtures/artifacts/task-intent-draft.sample.json"
subagent_packet_fixture="tests/e2e/fixtures/artifacts/subagent-context-packet.sample.json"
matrix="tests/e2e/fixtures/workflow-quality-matrix.json"

for file in \
    "$skill" \
    "$task_intent_fixture" \
    "$subagent_packet_fixture"
do
    if [[ -f "$file" ]]; then
        pass "$file exists"
    else
        fail "$file exists"
    fi
done

assert_contains "$skill" "/aegis-goal" "goal-framing supports slash shortcut"
assert_contains "$skill" "Aegis goal:" "goal-framing supports portable natural-language trigger"
assert_contains "$skill" "TaskIntentDraft" "goal-framing extends TaskIntentDraft instead of new authority"
assert_contains "$skill" "Fix the auth refresh bug without rewriting the auth system" \
    "goal-framing includes a concrete usage example"
assert_contains "$skill" "done.*blocked.*needs-verification.*scope-exceeded|done.*blocked.*scope-exceeded" \
    "goal-framing defines stop condition states"
assert_contains "$skill" "Route Matrix" \
    "goal-framing includes a route matrix"
assert_contains "$skill" "Goal framing alone does not create project files" \
    "goal-framing keeps workspace lazy"
assert_contains "$skill" "Do not stop after.*TaskIntentDraft|continue.*routed workflow" \
    "goal-framing continues into the routed workflow by default"
assert_contains "$skill" "frame-only|only define.*goal|do not execute" \
    "goal-framing stops at the frame only when explicitly requested"
assert_contains "$skill" "does not replace evidence" \
    "goal-framing prevents summary-only subagent facts"
assert_contains "$skill" "completion authority" \
    "goal-framing states authority boundary"

assert_contains "$using_aegis" "goal-framing" \
    "using-aegis routes explicit goal requests"
assert_not_contains "$using_aegis" "SubagentContextPacket" \
    "using-aegis does not absorb subagent packet template"

assert_contains "$subagent_skill" "SubagentContextPacket" \
    "subagent-driven-development requires compact context packets"
assert_contains "$implementer_prompt" "SubagentContextPacket" \
    "implementer prompt includes subagent context packet"
assert_contains "$subagent_skill" "must-read excerpts" \
    "subagent packet includes must-read excerpts"
assert_contains "$subagent_skill" "Do not paste full chat transcripts" \
    "subagent packet forbids full transcript handoff"
assert_contains "$verification_skill" "Goal Closure" \
    "verification checks goal closure when goal framing exists"
assert_contains "$verification_skill" "done.*blocked.*needs-verification.*scope-exceeded|done.*blocked.*scope-exceeded" \
    "verification uses goal stop states"

assert_contains "$artifact_doc" "successEvidence" \
    "artifact schema documents optional TaskIntentDraft goal fields"
assert_contains "$artifact_doc" "SubagentContextPacket" \
    "artifact schema documents SubagentContextPacket"
assert_contains "$runtime_doc" "successEvidence" \
    "runtime-ready boundary documents goal framing fields"
assert_contains "$workflow_doc" "Aegis goal:" \
    "English workflow guide documents portable goal entry"
assert_contains "$workflow_doc_zh" "Aegis goal:" \
    "Chinese workflow guide documents portable goal entry"
assert_contains "$workflow_quality" "goal-framing" \
    "workflow quality baseline includes goal-framing compact contract"
assert_contains "$workflow_quality" "Goal Closure" \
    "workflow quality baseline covers goal closure"
assert_contains "$readme_en" "Aegis goal: Fix the auth refresh bug without rewriting the auth system" \
    "English README includes goal framing example"
assert_contains "$readme_zh" "Aegis goal:" \
    "Chinese README includes goal framing example"

for host_doc in "${host_docs[@]}"; do
    assert_contains "$host_doc" "Aegis goal:" \
        "$host_doc documents portable goal entry"
done

"${PYTHON_CMD[@]}" - "$task_intent_fixture" "$subagent_packet_fixture" "$matrix" <<'PY'
import json
import sys
from pathlib import Path

task_intent = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
subagent_packet = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
matrix = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))

for field in ("goal", "successEvidence", "stopCondition", "nonGoals"):
    if field not in task_intent:
        raise SystemExit(f"task intent sample missing optional goal field: {field}")

required_packet_fields = {
    "schemaVersion",
    "task",
    "goal",
    "stopCondition",
    "relevantBaselineRefs",
    "relevantFiles",
    "knownFacts",
    "unknowns",
    "nonGoals",
    "expectedOutput",
    "verificationExpected",
    "mustReadExcerpts",
    "unsafeAssumptions",
}
missing = sorted(required_packet_fields - subagent_packet.keys())
if missing:
    raise SystemExit(f"subagent context packet missing fields: {', '.join(missing)}")

joined_non_goals = " ".join(subagent_packet.get("nonGoals", [])).lower()
if "conversation" not in joined_non_goals and "transcript" not in joined_non_goals:
    raise SystemExit("subagent context packet should avoid full conversation inheritance")
if not subagent_packet.get("mustReadExcerpts"):
    raise SystemExit("subagent context packet must include mustReadExcerpts")
if not subagent_packet.get("verificationExpected"):
    raise SystemExit("subagent context packet must include verificationExpected")

samples = matrix.get("samples", [])
sample = next((item for item in samples if item.get("id") == "explicit-aegis-goal"), None)
if not sample:
    raise SystemExit("workflow quality matrix missing explicit-aegis-goal sample")
if sample.get("expectedPrimarySkill") != "goal-framing":
    raise SystemExit("explicit-aegis-goal sample must route to goal-framing")
if "create-project-workspace-records" not in sample.get("mustNotDo", []):
    raise SystemExit("goal-framing sample must forbid workspace creation by default")
if "TaskIntentDraft" not in sample.get("expectedArtifacts", []):
    raise SystemExit("goal-framing sample must expect TaskIntentDraft")
if "stop-after-task-intent-draft" not in sample.get("mustNotDo", []):
    raise SystemExit("goal-framing sample must forbid stopping after TaskIntentDraft")
if "continue" not in sample.get("expectedOutputShape", ""):
    raise SystemExit("goal-framing sample must expect continuation into the routed workflow")
if "continue" not in sample.get("verificationSignal", ""):
    raise SystemExit("goal-framing sample must verify continuation beyond the frame")

contracts = matrix.get("compactOutputContracts", {})
if "goal-framing" not in contracts:
    raise SystemExit("workflow quality contracts missing goal-framing")
for field in ("Goal", "Success evidence", "Stop condition", "Non-goals", "Route", "Next", "Continuation"):
    if field not in contracts["goal-framing"]:
        raise SystemExit(f"goal-framing compact contract missing {field}")
for field in ("Goal status", "Success evidence", "Stop state", "Non-goals respected"):
    if field not in contracts["verification-before-completion"]:
        raise SystemExit(f"verification compact contract missing goal closure field: {field}")

print("  [PASS] goal-framing fixtures and workflow matrix are shaped correctly")
PY

if (( failures > 0 )); then
    echo ""
    echo "Goal framing check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Goal framing check passed."
