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
pass() { echo "  [PASS] $1"; }
fail() { echo "  [FAIL] $1"; failures=$((failures + 1)); }

assert_contains() {
    local file="$1" pattern="$2" label="$3"
    if grep -qE "$pattern" "$file"; then pass "$label"; else fail "$label"; fi
}

assert_not_contains() {
    local file="$1" pattern="$2" label="$3"
    if grep -qE "$pattern" "$file"; then fail "$label"; else pass "$label"; fi
}

echo "=== Context Semantic Infrastructure Check ==="

owner="skills/establishing-project-context/SKILL.md"
format="skills/establishing-project-context/CONTEXT-FORMAT.md"
matrix="tests/e2e/fixtures/context-semantic-infrastructure-matrix.json"
consumers=(
    skills/using-aegis/SKILL.md
    skills/brainstorming/SKILL.md
    skills/writing-plans/SKILL.md
    skills/systematic-debugging/SKILL.md
    skills/requesting-code-review/SKILL.md
    skills/long-task-continuation/SKILL.md
    skills/verification-before-completion/SKILL.md
)

for file in "$owner" "$format" "$matrix" CONTEXT.md; do
    if [[ -f "$file" ]]; then pass "$file exists"; else fail "$file exists"; fi
done

assert_contains "$owner" 'single active-modeling' \
    "active modeling has one canonical owner"
assert_contains "$owner" 'A/B \+ fact' "owner separates evidence and factual authority"
assert_contains "$owner" 'A/B/C \+ decision' "owner keeps unresolved decisions user-owned"
assert_contains "$owner" 'Domain Scenario Check' "owner defines scenario pressure testing"
assert_contains "$owner" 'byte-for-byte unchanged' "owner requires no-delta byte stability"
assert_contains "$owner" 'Re-read immediately before writing' "owner protects concurrent edits"
assert_contains "$owner" 'outside the project root' "owner rejects path and symlink escapes"
assert_contains "$owner" 'semantic data' "owner separates context data from instructions"
assert_not_contains "$owner" 'Want me to set up|start with 3-5|without user consent' \
    "retired consent and fixed-count rules are absent"

assert_contains "$format" 'Canonical Write Shape' "format defines compact canonical writes"
assert_contains "$format" 'Legacy Read Compatibility' "format preserves legacy reads"
assert_contains "$format" 'no timestamps' "format forbids volatile timestamps"

for consumer in "${consumers[@]}"; do
    assert_contains "$consumer" 'CONTEXT|establishing-project-context|Context Impact' \
        "$consumer contains a context consumer cue"
    assert_not_contains "$consumer" 'A/B \+ fact|A/B/C \+ decision|Evidence grade:' \
        "$consumer does not duplicate active write policy"
done

assert_contains docs/current/AEGIS_PROCESS_BASELINE.md 'Semantic Context Infrastructure' \
    "process baseline owns the shared semantic contract"
assert_contains docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md \
    'Stable Semantic Context Prefix' "prompt hygiene defines stable bounded context"
assert_contains docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md \
    'does not guarantee provider cache hits' "cache savings remain non-guaranteed"
assert_contains docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md \
    'Semantic Context Reliability' "workflow quality defines context reliability"
assert_contains docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md \
    'filesystem-state samples' "trigger health requires execution-depth evidence"

assert_contains CONTEXT.md 'docs/current/AEGIS_TARGET_STATE.md' \
    "root glossary links target-state authority"
assert_contains CONTEXT.md 'ADR-0001-aegis-method-pack-is-not-runtime-core.md' \
    "root glossary links runtime-boundary ADR"

if "${PYTHON_CMD[@]}" - "$matrix" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
samples = data.get("samples", [])
required_ids = {
    "existing-context-passive-consumption",
    "missing-context-no-resolved-term",
    "first-resolved-fact-lazy-create",
    "existing-context-ab-fact-minimal-update",
    "unresolved-decision-asks-no-active-write",
    "code-context-conflict-no-silent-winner",
    "relational-term-scenario-pressure-test",
    "no-semantic-delta-byte-stable",
    "tiny-task-no-context-ceremony",
    "multi-context-selects-relevant-files",
    "downstream-plan-reuses-canonical-term",
    "legacy-table-remains-readable",
    "instruction-like-content-is-not-executed",
    "context-map-path-escape-is-refused",
    "concurrent-same-term-change-is-not-overwritten",
}
required_fields = {
    "id", "initialFiles", "initialHashes", "prompt", "taskClass",
    "expectedMode", "expectedPrimarySkill", "mustLoadSkills",
    "mustNotLoadSkills", "evidenceGrade", "semanticAuthority",
    "expectedContextFiles", "expectedFileAction", "expectedCanonicalTerms",
    "mustAskUser", "mustNotDo", "liveEligibleHosts",
}
ids = {sample.get("id") for sample in samples}
if ids != required_ids:
    raise SystemExit(f"matrix IDs differ: missing={sorted(required_ids - ids)}, extra={sorted(ids - required_ids)}")

write_actions = {"create", "update", "deprecate"}
no_write_actions = {"none", "read-only", "ask-no-write", "preserve", "refuse-no-write", "concurrent-conflict"}
for sample in samples:
    missing = required_fields - sample.keys()
    if missing:
        raise SystemExit(f"{sample['id']} missing fields: {sorted(missing)}")
    action = sample["expectedFileAction"]
    if action in write_actions:
        if sample["evidenceGrade"] not in {"A", "B"} or sample["semanticAuthority"] != "fact":
            raise SystemExit(f"{sample['id']} write lacks A/B fact authority")
    elif action not in no_write_actions:
        raise SystemExit(f"{sample['id']} has unknown action {action}")
    if action in no_write_actions:
        guards = " ".join(sample["mustNotDo"])
        if not any(token in guards for token in ("write", "create", "overwrite", "execute", "context")):
            raise SystemExit(f"{sample['id']} no-write case lacks a write prohibition")
    for rel in sample["initialFiles"]:
        path = Path(rel)
        if path.is_absolute() or ".." in path.parts:
            raise SystemExit(f"{sample['id']} initial fixture path escapes project: {rel}")

if not all(any(s["expectedMode"] == mode for s in samples) for mode in ("passive", "active", "fast-path")):
    raise SystemExit("matrix must cover passive, active, and fast-path behavior")

security = {
    "instruction-like-content-is-not-executed",
    "context-map-path-escape-is-refused",
    "concurrent-same-term-change-is-not-overwritten",
}
if not security <= ids:
    raise SystemExit("matrix missing semantic context security cases")

allowed_terms = {"Aegis Method Pack", "Host Adapter", "Runtime Core", "runtime-ready artifact"}
text = Path("CONTEXT.md").read_text(encoding="utf-8")
terms = {line[2:-3] for line in text.splitlines() if line.startswith("**") and line.endswith("**:")}
if terms != allowed_terms:
    raise SystemExit(f"root CONTEXT.md terms differ: {sorted(terms)}")

print("  [PASS] context matrix covers lifecycle, negative, security, and compatibility cases")
PY
then
    pass "context semantic matrix is valid"
else
    fail "context semantic matrix is valid"
fi

if (( failures > 0 )); then
    echo ""
    echo "Context semantic infrastructure check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Context semantic infrastructure check passed."
