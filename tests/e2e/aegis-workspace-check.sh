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

fail() {
    echo "  [FAIL] $1"
    exit 1
}

pass() {
    echo "  [PASS] $1"
}

write_json() {
    local path="$1"
    shift
    mkdir -p "$(dirname "$path")"
    printf '%s\n' "$*" > "$path"
}

mkdir -p "$REPO_ROOT/.tmp"
TMP_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/aegis-workspace.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

TARGET_ROOT="$TMP_ROOT/target-project"
mkdir -p "$TARGET_ROOT"

HELPER="$REPO_ROOT/scripts/aegis-workspace.py"

echo "=== Aegis Workspace Helper Check ==="

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "Aegis method-pack repository must not ship a live docs/aegis workspace"
fi
pass "repository has no precreated docs/aegis workspace"

"${PYTHON_CMD[@]}" "$HELPER" init --root "$TARGET_ROOT" >/dev/null
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "init creates a valid target-project workspace"

SPEC_PATH="$TARGET_ROOT/docs/aegis/specs/2026-05-07-helper-design.md"
mkdir -p "$(dirname "$SPEC_PATH")"
printf '# Helper Design\n' > "$SPEC_PATH"

if "${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/tmp/aegis-workspace-unindexed.out 2>&1; then
    fail "check must fail when a workspace markdown file is not indexed"
fi
pass "check detects unindexed workspace markdown"

"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$SPEC_PATH" \
    --kind spec \
    --title "Workspace helper design" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$SPEC_PATH" \
    --kind spec \
    --title "Workspace helper design" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "append-index records workspace markdown and remains idempotent"

ARTIFACT_PATH="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/task-intent-draft.json"
write_json "$ARTIFACT_PATH" '{
  "schemaVersion": "aegis.schema.v0",
  "requestedOutcome": "Validate workspace helper artifact sidecars.",
  "scope": "temporary target project",
  "changeKinds": ["test"],
  "riskHints": []
}'

"${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type TaskIntentDraft \
    --file "$ARTIFACT_PATH" >/dev/null
pass "validate-artifact accepts a valid TaskIntentDraft"

"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$ARTIFACT_PATH" \
    --kind artifact \
    --title "Task intent draft sidecar" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "check validates indexed recognizable artifact JSON sidecars"

BROKEN_ARTIFACT="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/impact-statement-draft.json"
write_json "$BROKEN_ARTIFACT" '{
  "schemaVersion": "aegis.schema.v0",
  "affectedLayers": []
}'

if "${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type ImpactStatementDraft \
    --file "$BROKEN_ARTIFACT" >/tmp/aegis-workspace-missing-field.out 2>&1; then
    fail "validate-artifact must reject missing required fields"
fi
pass "validate-artifact rejects missing required fields"

BAD_SCHEMA="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/evidence-bundle-draft.json"
write_json "$BAD_SCHEMA" '{
  "schemaVersion": "aegis.schema.v1",
  "artifactKey": "evidence-1",
  "type": "test",
  "source": "temporary target project",
  "summary": "bad schema",
  "verifier": "aegis-workspace-check"
}'

if "${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type EvidenceBundleDraft \
    --file "$BAD_SCHEMA" >/tmp/aegis-workspace-bad-schema.out 2>&1; then
    fail "validate-artifact must reject invalid schemaVersion"
fi
pass "validate-artifact rejects invalid schemaVersion"

BAD_DECISION="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/drift-check-draft.json"
write_json "$BAD_DECISION" '{
  "schemaVersion": "aegis.schema.v0",
  "taskId": "task-1",
  "taskIntentRef": "task-intent-draft.json",
  "baselineRefs": [],
  "scopeStatus": "aligned",
  "compatStatus": "unchanged",
  "retirementStatus": "none",
  "newRiskSignals": [],
  "decision": "completion-granted"
}'

if "${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type DriftCheckDraft \
    --file "$BAD_DECISION" >/tmp/aegis-workspace-bad-decision.out 2>&1; then
    fail "validate-artifact must reject authoritative DriftCheckDraft decisions"
fi
pass "validate-artifact rejects authoritative DriftCheckDraft decisions"

UNKNOWN_JSON="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/project-local-data.json"
write_json "$UNKNOWN_JSON" '{"project": "local"}'
"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$UNKNOWN_JSON" \
    --kind data \
    --title "Project local JSON" >/dev/null

rm "$BROKEN_ARTIFACT" "$BAD_SCHEMA" "$BAD_DECISION"
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "check ignores unrecognized project-local JSON files"

WORK_DIR="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper-lifecycle"
"${PYTHON_CMD[@]}" "$HELPER" new-work \
    --root "$TARGET_ROOT" \
    --date 2026-05-07 \
    --slug helper-lifecycle \
    --title "Helper lifecycle" \
    --requested-outcome "Exercise helper-backed task lifecycle records." \
    --scope "temporary target project" \
    --change-kind test \
    --risk-hint advisory-only >/dev/null

if "${PYTHON_CMD[@]}" "$HELPER" new-work \
    --root "$TARGET_ROOT" \
    --date 2026-05-07 \
    --slug helper-lifecycle \
    --title "Helper lifecycle duplicate" \
    --requested-outcome "Duplicate work record should not overwrite." \
    --scope "temporary target project" \
    --change-kind test >/tmp/aegis-workspace-duplicate.out 2>&1; then
    fail "new-work must reject an existing work lifecycle directory"
fi
if ! grep -q "work lifecycle already exists" /tmp/aegis-workspace-duplicate.out; then
    fail "duplicate new-work error should explain the existing lifecycle directory"
fi

if "${PYTHON_CMD[@]}" "$HELPER" new-work \
    --root "$TARGET_ROOT" \
    --date 2026-05-07 \
    --slug "nested/path" \
    --title "Nested work" \
    --requested-outcome "Nested work record should be rejected." \
    --scope "temporary target project" \
    --change-kind test >/tmp/aegis-workspace-nested.out 2>&1; then
    fail "new-work must reject nested work slugs"
fi
if ! grep -q "work slug must be a single directory name" /tmp/aegis-workspace-nested.out; then
    fail "nested new-work error should explain the single-directory slug rule"
fi

for path in \
    "$WORK_DIR/10-intent.md" \
    "$WORK_DIR/20-checkpoint.md" \
    "$WORK_DIR/90-evidence.md" \
    "$WORK_DIR/99-reflection.md" \
    "$WORK_DIR/task-intent-draft.json" \
    "$WORK_DIR/baseline-read-set-hint.json" \
    "$WORK_DIR/impact-statement-draft.json" \
    "$WORK_DIR/todo-checkpoint-draft.json" \
    "$WORK_DIR/drift-check-draft.json"
do
    if [[ ! -f "$path" ]]; then
        fail "new-work must create lifecycle file: $path"
    fi
done
pass "new-work creates helper-backed lifecycle records"

"${PYTHON_CMD[@]}" "$HELPER" add-checkpoint \
    --root "$TARGET_ROOT" \
    --work 2026-05-07-helper-lifecycle \
    --current-todo "Implement helper lifecycle commands" \
    --completed-todo "Created work record" \
    --active-slice "P0 lifecycle" \
    --evidence-ref "docs/aegis/work/2026-05-07-helper-lifecycle/10-intent.md" \
    --blocked-on "none" \
    --next-step "Assemble proof bundle" \
    --resume-instruction "Read checkpoint and proof bundle before continuing" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" add-evidence \
    --root "$TARGET_ROOT" \
    --work 2026-05-07-helper-lifecycle \
    --artifact-key workspace-check \
    --type test \
    --source "bash tests/e2e/aegis-workspace-check.sh" \
    --summary "Lifecycle commands were exercised in a temporary target project." \
    --verifier "aegis-workspace-check" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" add-drift-check \
    --root "$TARGET_ROOT" \
    --work 2026-05-07-helper-lifecycle \
    --decision needs-verification \
    --scope-status aligned \
    --compat-status unchanged \
    --retirement-status none \
    --baseline-ref docs/current/AEGIS_PROCESS_BASELINE.md \
    --new-risk-signal "proof bundle still needs assembly" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" bundle \
    --root "$TARGET_ROOT" \
    --work 2026-05-07-helper-lifecycle >/dev/null

for path in \
    "$WORK_DIR/evidence-bundle-draft-workspace-check.json" \
    "$WORK_DIR/resume-state-hint.json" \
    "$WORK_DIR/gate-input-pack.json" \
    "$WORK_DIR/proof-bundle.md"
do
    if [[ ! -f "$path" ]]; then
        fail "lifecycle commands must create proof-bundle file: $path"
    fi
done

if ! grep -q "Method Pack Boundary" "$WORK_DIR/proof-bundle.md"; then
    fail "proof bundle must state the Method Pack boundary"
fi

"${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type GateInputPack \
    --file "$WORK_DIR/gate-input-pack.json" >/dev/null
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "lifecycle commands assemble a structural proof bundle"

COUNT="$(grep -c 'docs/aegis/specs/2026-05-07-helper-design.md' "$TARGET_ROOT/docs/aegis/INDEX.md")"
if [[ "$COUNT" != "1" ]]; then
    fail "append-index must not duplicate an existing path"
fi
pass "append-index avoids duplicate entries"

if "${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$TARGET_ROOT/docs/aegis/specs/missing.md" \
    --kind spec \
    --title "Missing spec" >/tmp/aegis-workspace-missing.out 2>&1; then
    fail "append-index must reject missing files"
fi
pass "append-index rejects missing files"

if "${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$TARGET_ROOT/README.md" \
    --kind note \
    --title "Outside workspace" >/tmp/aegis-workspace-outside.out 2>&1; then
    fail "append-index must reject paths outside docs/aegis"
fi
pass "append-index rejects paths outside docs/aegis"

printf '| 2026-05-07 | spec | docs/aegis/specs/stale.md | Stale spec |\n' >> "$TARGET_ROOT/docs/aegis/INDEX.md"
if "${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/tmp/aegis-workspace-stale.out 2>&1; then
    fail "check must fail when INDEX.md points at a missing workspace file"
fi
pass "check detects stale INDEX.md entries"

if [[ -e "$REPO_ROOT/docs/aegis" ]]; then
    fail "helper must not create docs/aegis in the Aegis repository during target-root tests"
fi
pass "helper only wrote to the explicit target root"

echo ""
echo "Aegis workspace helper check passed."
