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

if ! grep -q "## 1. Baseline Roles" "$TARGET_ROOT/docs/aegis/BASELINE-GOVERNANCE.md"; then
    fail "init must write the dual-baseline governance template"
fi
if ! grep -q "Product / Requirement Baseline" "$TARGET_ROOT/docs/aegis/BASELINE-GOVERNANCE.md"; then
    fail "governance template must name the product requirement baseline role"
fi
if ! grep -q "Architecture / Runtime Boundary Baseline" "$TARGET_ROOT/docs/aegis/BASELINE-GOVERNANCE.md"; then
    fail "governance template must name the architecture runtime boundary baseline role"
fi
if ! grep -q "scope: requirements | architecture | both" "$TARGET_ROOT/docs/aegis/BASELINE-GOVERNANCE.md"; then
    fail "governance template must include dual-baseline scope taxonomy"
fi
pass "init writes the dual-baseline governance template"

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
  "goal": "Keep validation bounded to workspace helper artifact sidecars.",
  "successEvidence": ["validate-artifact accepts the sidecar"],
  "stopCondition": "Stop when the sidecar validates or validation fails with a real error.",
  "nonGoals": ["Do not grant completion authority"],
  "scope": "temporary target project",
  "changeKinds": ["test"],
  "riskHints": []
}'

"${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type TaskIntentDraft \
    --file "$ARTIFACT_PATH" >/dev/null
pass "validate-artifact accepts a valid TaskIntentDraft"

BASELINE_USAGE_ARTIFACT="$TARGET_ROOT/docs/aegis/work/2026-05-07-helper/baseline-usage-draft.json"
write_json "$BASELINE_USAGE_ARTIFACT" '{
  "schemaVersion": "aegis.schema.v0",
  "taskId": "task-1",
  "requiredBaselineRefs": ["docs/current/AEGIS_WORKFLOW_GUIDE.md#baseline-first"],
  "deliveredContextRefs": ["docs/current/AEGIS_WORKFLOW_GUIDE.md#baseline-first"],
  "acknowledgedBeforePlanRefs": ["docs/current/AEGIS_WORKFLOW_GUIDE.md#baseline-first"],
  "citedInPlanRefs": ["docs/current/AEGIS_WORKFLOW_GUIDE.md#baseline-first"],
  "missingRefs": [],
  "decision": "continue"
}'

"${PYTHON_CMD[@]}" "$HELPER" validate-artifact \
    --type BaselineUsageDraft \
    --file "$BASELINE_USAGE_ARTIFACT" >/dev/null
pass "validate-artifact accepts a valid BaselineUsageDraft"

"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$ARTIFACT_PATH" \
    --kind artifact \
    --title "Task intent draft sidecar" >/dev/null

"${PYTHON_CMD[@]}" "$HELPER" append-index \
    --root "$TARGET_ROOT" \
    --path "$BASELINE_USAGE_ARTIFACT" \
    --kind artifact \
    --title "Baseline usage draft sidecar" >/dev/null

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
    --goal "Verify helper-backed lifecycle records stay bounded and advisory." \
    --success-evidence "new-work creates intent, checkpoint, drift, and evidence placeholders" \
    --stop-condition "Stop when lifecycle files validate or report needs-verification." \
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

if ! grep -q "Goal: Verify helper-backed lifecycle records stay bounded and advisory." "$WORK_DIR/10-intent.md"; then
    fail "new-work intent markdown must include goal framing"
fi
if ! grep -q "Stop condition: Stop when lifecycle files validate or report needs-verification." "$WORK_DIR/10-intent.md"; then
    fail "new-work intent markdown must include stop condition"
fi
pass "new-work records optional goal framing in intent artifacts"

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

ADR_ONE_PATH="$TARGET_ROOT/docs/aegis/adr/ADR-0001-helper-owner-boundary.md"
"${PYTHON_CMD[@]}" "$HELPER" new-adr \
    --root "$TARGET_ROOT" \
    --date 2026-05-08 \
    --slug helper-owner-boundary \
    --title "Helper owner boundary" \
    --status recorded-from-work \
    --source-evidence "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" \
    --context "Completed helper work now needs a durable project-local ADR record." \
    --decision "Use docs/aegis/adr for target-project Aegis method-pack ADR memory." \
    --alternative "Keep architecture memory only in proof bundles." \
    --consequence "Completion-time ADR backfill gains a helper-backed record without creating runtime authority." \
    --compat-boundary "Writes only to target-project docs/aegis/adr and validates structure only." \
    --retirement-impact "Helper-backed ADR automation can retire the workspace ADR helper limitation once workflow wiring lands." \
    --baseline-sync needed \
    --baseline-target "docs/current/AEGIS_ADR_AUTO_BACKFILL.md" \
    --baseline-action update-baseline \
    --baseline-reason "Current ADR helper docs must reflect the new target-project command path." \
    --evidence-ref "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" >/dev/null

if [[ ! -f "$ADR_ONE_PATH" ]]; then
    fail "new-adr must create the first workspace ADR file"
fi
if ! grep -q 'Status: `recorded-from-work`' "$ADR_ONE_PATH"; then
    fail "new-adr must record the ADR evidence-source status"
fi
if ! grep -q "## Baseline Sync" "$ADR_ONE_PATH"; then
    fail "new-adr must include a baseline sync section"
fi
if ! grep -q "advisory Aegis Method Pack record" "$ADR_ONE_PATH"; then
    fail "new-adr must preserve the advisory method-pack boundary"
fi
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "new-adr creates an indexed workspace ADR with the required structure"

if "${PYTHON_CMD[@]}" "$HELPER" new-adr \
    --root "$TARGET_ROOT" \
    --date 2026-05-08 \
    --slug helper-owner-boundary \
    --title "Duplicate helper owner boundary" \
    --status recorded-from-work \
    --source-evidence "duplicate evidence" \
    --context "Duplicate ADR slugs should be rejected." \
    --decision "Reject duplicate slugs." \
    --alternative "Allow duplicate slugs and rely on numbers only." \
    --consequence "Slug collisions stay explicit." \
    --compat-boundary "No compatibility change." \
    --retirement-impact "No retirement change." \
    --baseline-sync not-needed \
    --baseline-target "docs/current/AEGIS_ADR_AUTO_BACKFILL.md" \
    --baseline-action cite-unchanged \
    --baseline-reason "No baseline writeback is needed for a rejected duplicate." \
    --evidence-ref "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" >/tmp/aegis-workspace-adr-duplicate.out 2>&1; then
    fail "new-adr must reject a duplicate ADR slug"
fi
if ! grep -q "ADR slug already exists" /tmp/aegis-workspace-adr-duplicate.out; then
    fail "duplicate new-adr error should explain the ADR slug collision"
fi
pass "new-adr rejects duplicate ADR slugs"

"${PYTHON_CMD[@]}" "$HELPER" amend-adr \
    --root "$TARGET_ROOT" \
    --path "$ADR_ONE_PATH" \
    --date 2026-05-09 \
    --summary "Added closeout evidence" \
    --source-evidence "bash tests/e2e/aegis-workspace-check.sh" \
    --compat-boundary "The ADR helper remains target-project only and structural." \
    --retirement-impact "Fresh verification evidence can now justify retiring the helper automation limitation." \
    --baseline-sync not-needed \
    --baseline-target "docs/current/AEGIS_ADR_AUTO_BACKFILL.md" \
    --baseline-action cite-unchanged \
    --baseline-reason "The baseline target remains valid; only supporting evidence changed." \
    --evidence-ref "docs/aegis/adr/ADR-0001-helper-owner-boundary.md" >/dev/null

if ! grep -q "## Amendment - 2026-05-09 - Added closeout evidence" "$ADR_ONE_PATH"; then
    fail "amend-adr must append an amendment section"
fi
if ! grep -q -- "- Status: amended" "$ADR_ONE_PATH"; then
    fail "amend-adr must mark the appended section as amended"
fi
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "amend-adr appends amendment records without breaking workspace validation"

ADR_TWO_PATH="$TARGET_ROOT/docs/aegis/adr/ADR-0002-helper-owner-boundary-v2.md"
"${PYTHON_CMD[@]}" "$HELPER" supersede-adr \
    --root "$TARGET_ROOT" \
    --path "$ADR_ONE_PATH" \
    --date 2026-05-10 \
    --slug helper-owner-boundary-v2 \
    --title "Helper owner boundary v2" \
    --status recorded-from-work \
    --source-evidence "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" \
    --context "The helper contract now includes explicit create, amend, and supersede commands." \
    --decision "Supersede the earlier ADR with the command-backed helper contract." \
    --alternative "Amend the prior ADR and keep the same decision scope." \
    --consequence "Future contributors see the helper-backed contract as the current durable record." \
    --compat-boundary "The helper still writes only to target-project docs/aegis/adr." \
    --retirement-impact "The baseline-defined-only limitation can now shrink to workflow/documentation follow-up." \
    --baseline-sync needed \
    --baseline-target "docs/current/AEGIS_ADR_AUTO_BACKFILL.md" \
    --baseline-action update-baseline \
    --baseline-reason "Current ADR helper docs must describe the superseding command path." \
    --evidence-ref "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" \
    --supersession-reason "Helper automation moved from placeholder policy to command-backed workspace support." >/dev/null

if [[ ! -f "$ADR_TWO_PATH" ]]; then
    fail "supersede-adr must create a new superseding ADR file"
fi
if ! grep -q "## Supersedes" "$ADR_TWO_PATH"; then
    fail "supersede-adr must record which ADR is being superseded"
fi
if ! grep -q "docs/aegis/adr/ADR-0001-helper-owner-boundary.md" "$ADR_TWO_PATH"; then
    fail "supersede-adr must link the superseding ADR back to the prior ADR"
fi
if ! grep -q "## Superseded By" "$ADR_ONE_PATH"; then
    fail "supersede-adr must mark the prior ADR as superseded"
fi
if ! grep -q -- "- Status: superseded" "$ADR_ONE_PATH"; then
    fail "supersede-adr must append a superseded status marker to the prior ADR"
fi
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "supersede-adr creates a superseding ADR and marks the prior ADR"

if "${PYTHON_CMD[@]}" "$HELPER" supersede-adr \
    --root "$TARGET_ROOT" \
    --path "$ADR_ONE_PATH" \
    --date 2026-05-11 \
    --slug helper-owner-boundary-v3 \
    --title "Helper owner boundary v3" \
    --status recorded-from-work \
    --source-evidence "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" \
    --context "Already-superseded ADRs should not be superseded again." \
    --decision "Reject the second supersession attempt." \
    --alternative "Allow multiple superseded-by tails." \
    --consequence "ADR lineage stays single-valued." \
    --compat-boundary "No compatibility change." \
    --retirement-impact "No retirement change." \
    --baseline-sync not-needed \
    --baseline-target "docs/current/AEGIS_ADR_AUTO_BACKFILL.md" \
    --baseline-action cite-unchanged \
    --baseline-reason "No writeback is needed for a rejected supersession." \
    --evidence-ref "docs/aegis/work/2026-05-07-helper-lifecycle/proof-bundle.md" \
    --supersession-reason "This should be rejected." >/tmp/aegis-workspace-adr-superseded.out 2>&1; then
    fail "supersede-adr must reject an ADR that is already marked as superseded"
fi
if ! grep -q "already marked as superseded" /tmp/aegis-workspace-adr-superseded.out; then
    fail "supersede-adr rejection should explain the existing superseded marker"
fi
pass "supersede-adr rejects already-superseded ADRs"

cp "$ADR_TWO_PATH" "$ADR_TWO_PATH.bak"
printf '# Broken ADR\n' > "$ADR_TWO_PATH"
if "${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/tmp/aegis-workspace-broken-adr.out 2>&1; then
    fail "check must fail when a workspace ADR loses required structure"
fi
mv "$ADR_TWO_PATH.bak" "$ADR_TWO_PATH"
"${PYTHON_CMD[@]}" "$HELPER" check --root "$TARGET_ROOT" >/dev/null
pass "check validates helper-backed ADR structure as well as index coverage"

COUNT="$(grep -c 'docs/aegis/specs/2026-05-07-helper-design.md' "$TARGET_ROOT/docs/aegis/INDEX.md")"
if [[ "$COUNT" != "1" ]]; then
    fail "append-index must not duplicate an existing path"
fi
pass "append-index avoids duplicate entries"

ADR_COUNT="$(grep -c 'docs/aegis/adr/ADR-0001-helper-owner-boundary.md' "$TARGET_ROOT/docs/aegis/INDEX.md")"
if [[ "$ADR_COUNT" != "1" ]]; then
    fail "ADR helper mutations must not duplicate an existing ADR index path"
fi
pass "ADR helper mutations keep INDEX.md path entries idempotent"

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
