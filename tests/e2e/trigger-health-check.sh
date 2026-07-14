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

echo "=== Trigger Health Check ==="

baseline="docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md"
current_index="docs/current/README.md"
process_doc="docs/current/AEGIS_PROCESS_BASELINE.md"
readme_en="README.md"
readme_zh="README.zh-CN.md"
doctor="scripts/aegis-doctor.py"
matrix="tests/e2e/fixtures/trigger-health-matrix.json"

if [[ -f "$baseline" ]]; then
    pass "trigger health baseline exists"
else
    fail "trigger health baseline exists"
fi

assert_contains "$current_index" "AEGIS_TRIGGER_HEALTH_BASELINE.md" \
    "current docs index lists trigger health baseline"
assert_contains "$process_doc" "Trigger Health" \
    "process baseline defines trigger health"
assert_contains "$process_doc" "install and version visibility" \
    "process baseline starts trigger diagnosis at install/discovery/activation"
assert_contains "$process_doc" "host skill discovery" \
    "process baseline includes discovery in trigger diagnosis"
assert_contains "$process_doc" "activation mode and bootstrap entry" \
    "process baseline includes activation in trigger diagnosis"
assert_contains "$process_doc" "context pressure and re-entry" \
    "process baseline includes context-pressure re-entry in trigger diagnosis"
assert_contains "$process_doc" 'Keep `using-aegis` compact and route-only' \
    "process baseline keeps using-aegis compact"
assert_contains "$process_doc" "skill descriptions trigger-oriented" \
    "process baseline keeps skill descriptions trigger-oriented"
assert_contains "$process_doc" "trigger-health fixtures" \
    "process baseline requires fixtures before broadening trigger wording"

assert_contains "$baseline" "install and version visibility" \
    "baseline includes install/version layer"
assert_contains "$baseline" "host skill discovery" \
    "baseline includes discovery layer"
assert_contains "$baseline" "activation mode and bootstrap entry" \
    "baseline includes activation layer"
assert_contains "$baseline" '`using-aegis` router entry' \
    "baseline includes router-entry layer"
assert_contains "$baseline" "task-to-skill routing" \
    "baseline includes task routing layer"
assert_contains "$baseline" "skill execution depth" \
    "baseline includes execution-depth layer"
assert_contains "$baseline" "locally green checkpoint state is read" \
    "execution-depth evidence covers state readback after local success"
assert_contains "$baseline" "### L6 Context Pressure And Re-entry" \
    "baseline keeps context-pressure as L6"
assert_contains "$baseline" "context pressure and re-entry" \
    "baseline includes context-pressure layer"
assert_contains "$baseline" "compaction" \
    "baseline covers compaction as a trigger-health pressure signal"
assert_contains "$baseline" "re-entry check" \
    "baseline defines compact re-entry check"
assert_contains "$baseline" "### L7 False Positive Control" \
    "baseline keeps false-positive control as L7"
assert_contains "$baseline" "false positive over-triggering" \
    "baseline includes false-positive layer"
assert_contains "$baseline" "do not first add more keywords" \
    "baseline rejects keyword stuffing as first fix"
assert_contains "$baseline" 'Keep `using-aegis` compact and route-only' \
    "baseline preserves compact router owner"
assert_contains "$baseline" "Failure Report Shape" \
    "baseline defines failure report shape"

assert_contains "$readme_en" "trigger-chain diagnosis" \
    "English README documents trigger-chain diagnosis"
assert_contains "$readme_en" "AEGIS_TRIGGER_HEALTH_BASELINE.md" \
    "English README links trigger health baseline"
assert_contains "$readme_zh" "skill discovery" \
    "Chinese README documents trigger-chain diagnosis"
assert_contains "$readme_zh" "AEGIS_TRIGGER_HEALTH_BASELINE.md" \
    "Chinese README links trigger health baseline"

assert_contains "$doctor" "discovery-root-current" \
    "doctor can verify discovery root freshness"
assert_contains "$doctor" "using-aegis-hot-path-current" \
    "doctor can verify using-aegis hot path freshness"
assert_contains "$doctor" "context pressure and re-entry" \
    "doctor reports context-pressure trigger-health layer"

assert_contains "$baseline" "does not grant authoritative" \
    "baseline explicitly avoids authority escalation in trigger health"
assert_contains "skills/using-aegis/SKILL.md" "off=no auto route/load" \
    "router prevents automatic TDD routing and loading when off"
assert_contains "skills/systematic-debugging/SKILL.md" "TDD Mode: off" \
    "debugging names the off-mode boundary"
assert_contains "skills/systematic-debugging/SKILL.md" "do not require a failing test" \
    "debugging keeps off mode out of a forced test-first cycle"
assert_contains "skills/using-aegis/SKILL.md" "grill me.*brainstorming|brainstorming.*grill me" \
    "router sends explicit grilling requests to brainstorming"
assert_contains "skills/using-aegis/SKILL.md" "grill this plan.*审问我.*盘问我.*拷问我" \
    "router retains the direct grilling aliases"
assert_contains "skills/brainstorming/SKILL.md" "## Grilling Mode" \
    "brainstorming defines the explicit grilling mode"
assert_contains "skills/brainstorming/SKILL.md" "overrides the normal brainstorming execution" \
    "grilling mode overrides the normal brainstorming checklist"
assert_contains "skills/brainstorming/SKILL.md" 'Suspend `Checklist`, `The Process`, the `Compact output contract`' \
    "grilling mode suspends conflicting normal-flow artifacts"
assert_contains "skills/brainstorming/SKILL.md" "exactly one decision question" \
    "grilling mode limits each turn to one decision question"
assert_contains "skills/brainstorming/SKILL.md" "### Grilling Entry Signals" \
    "grilling mode distinguishes direct and soft entry signals"
assert_contains "skills/brainstorming/SKILL.md" "at most three independent decision questions" \
    "fast grilling mode limits batched questions to independent decisions"
assert_contains "skills/brainstorming/SKILL.md" "PR, diff, or current-code review" \
    "grilling mode keeps implementation review out of the interview"

"${PYTHON_CMD[@]}" - <<'PY'
from pathlib import Path

failures = []
for path in sorted(Path("skills").glob("*/SKILL.md")):
    lines = path.read_text(encoding="utf-8").splitlines()
    desc = next((line for line in lines if line.startswith("description:")), "")
    if not desc:
        failures.append(f"{path}: missing description")
        continue
    value = desc.split(":", 1)[1].strip().strip('"')
    if not value.startswith("Use when"):
        failures.append(f"{path}: description must start with Use when")
    lowered = value.lower()
    if " - " in value and any(
        marker in lowered
        for marker in (
            " - guides",
            " - creates",
            " - keeps",
            " - routes",
            " - requires",
            " - drops",
            " - maintains",
        )
    ):
        failures.append(f"{path}: description appears to summarize workflow")

if failures:
    raise SystemExit("\n".join(failures))

print("  [PASS] active skill descriptions stay trigger-oriented and avoid workflow summaries")
PY

"${PYTHON_CMD[@]}" - "$matrix" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
samples = data.get("samples", [])
expected_ids = {
    "quick-shared-module-bug",
    "failing-test-diagnosis",
    "tdd-off-risky-debugging",
    "ambiguous-feature",
    "explicit-grilling-mode",
    "grill-this-plan",
    "interrogate-me-chinese",
    "cross-examine-me-chinese",
    "soft-grilling-intent",
    "fast-grilling-mode",
    "existing-pr-red-team",
    "grilling-phrase-explanation",
    "explicit-aegis-goal",
    "approved-plan",
    "completion-claim",
    "high-risk-merge-independent-review",
    "repeated-fixes",
    "context-compaction-reentry",
    "simple-factual-qa",
    "tiny-wording-edit",
}
ids = {item.get("id") for item in samples}
missing = sorted(expected_ids - ids)
if missing:
    raise SystemExit(f"missing trigger-health samples: {', '.join(missing)}")

if len(samples) < 9:
    raise SystemExit("trigger-health matrix must contain at least 9 samples")

positives = [s for s in samples if s.get("expectedPrimarySkill")]
negatives = [s for s in samples if s.get("expectedPrimarySkill") is None]
if len(positives) < 6 or len(negatives) < 2:
    raise SystemExit("trigger-health matrix must include both positive and negative samples")

required_skills = {
    "using-aegis",
    "goal-framing",
    "systematic-debugging",
    "brainstorming",
    "writing-plans",
    "verification-before-completion",
    "requesting-code-review",
}
skills = {s.get("expectedPrimarySkill") for s in positives}
missing_skills = sorted(required_skills - skills)
if missing_skills:
    raise SystemExit(f"missing expected primary skills: {', '.join(missing_skills)}")

for item in samples:
    for field in ("id", "prompt", "allowedSecondarySkills", "mustNotDo", "failureLayer"):
        if field not in item:
            raise SystemExit(f"{item.get('id', '<unknown>')} missing field: {field}")
    if not item["mustNotDo"]:
        raise SystemExit(f"{item['id']} must define mustNotDo")

required_report_fields = {
    "TriggerHealthLayer",
    "ObservedPrompt",
    "ExpectedSkill",
    "ActualSkill",
    "FailureType",
    "CanonicalOwner",
    "SmallestFix",
    "Verification",
}
report_fields = set(data.get("failureReportFields", []))
missing_fields = sorted(required_report_fields - report_fields)
if missing_fields:
    raise SystemExit(f"missing failure report fields: {', '.join(missing_fields)}")

context_sample = next((s for s in samples if s.get("id") == "context-compaction-reentry"), None)
if not context_sample:
    raise SystemExit("missing context-compaction-reentry sample")
if context_sample.get("failureLayer") != "context-pressure":
    raise SystemExit("context-compaction-reentry must use context-pressure failure layer")
if "continue-without-reentry" not in context_sample.get("mustNotDo", []):
    raise SystemExit("context-compaction-reentry must forbid continuing without re-entry")

repeated_sample = next((s for s in samples if s.get("id") == "repeated-fixes"), None)
if not repeated_sample:
    raise SystemExit("missing repeated-fixes sample")
for required in ("add-another-local-patch", "erase-prior-patch-shape", "treat-new-carrier-name-as-new-direction"):
    if required not in repeated_sample.get("mustNotDo", []):
        raise SystemExit(f"repeated-fixes must forbid {required}")
if "long-task-continuation" not in repeated_sample.get("allowedSecondarySkills", []):
    raise SystemExit("repeated-fixes must allow checkpoint state readback")

completion_sample = next((s for s in samples if s.get("id") == "completion-claim"), None)
if not completion_sample:
    raise SystemExit("missing completion-claim sample")
if "requesting-code-review" in completion_sample.get("allowedSecondarySkills", []):
    raise SystemExit("generic completion sample must not route to requesting-code-review by default")

review_sample = next((s for s in samples if s.get("id") == "high-risk-merge-independent-review"), None)
if not review_sample:
    raise SystemExit("missing high-risk-merge-independent-review sample")
if review_sample.get("expectedPrimarySkill") != "requesting-code-review":
    raise SystemExit("high-risk merge review sample must use requesting-code-review")
if "skip-baseline-alignment" not in review_sample.get("mustNotDo", []):
    raise SystemExit("high-risk merge review sample must forbid skipping baseline alignment")
if "treat-review-as-completion-authority" not in review_sample.get("mustNotDo", []):
    raise SystemExit("high-risk merge review sample must protect authority boundary")

print("  [PASS] trigger-health matrix has representative positive and negative samples")
PY

if (( failures > 0 )); then
    echo ""
    echo "Trigger health check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Trigger health check passed."
