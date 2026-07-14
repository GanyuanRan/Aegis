# Directional Reset Governance Implementation Plan

Date: `2026-07-14`

Status: `Revised after approved falsifier`

## Goal

Preserve and reread bounded repair-direction facts across locally green
execution slices so a later convergent consumer-side patch pauses before edit,
while ordinary single-owner repairs keep the current quick-path behavior.

## Architecture

- `systematic-debugging` remains the semantic comparison owner.
- Existing checkpoint/evidence prose carries `PatchShape`, `CanonicalOwner`,
  `UpwardDrillSignal`, decision, outcome, and bounded evidence refs.
- `long-task-continuation` preserves the readback across slices and resume.
- `executing-plans` rereads it before unplanned verification-driven repair and
  routes judgment back to `systematic-debugging`.
- No schema, helper, router, description, host, or artifact-type change.

## Tech Stack

- Markdown Aegis skills and current-authority docs
- JSON workflow/trigger fixtures
- Python fixture validator
- Bash e2e and context-budget checks
- bounded Codex CLI read-only forward replay

## Baseline / Authority Refs

- `AGENTS.md`
- `docs/current/README.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
- `docs/current/AEGIS_PROCESS_BASELINE.md`
- `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`
- `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`
- `docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md`
- `docs/current/AEGIS_MINIMALITY_REFERENCE.md`
- `docs/aegis/specs/2026-07-14-directional-reset-governance-design.md`
- `docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-unmodified-stateful-falsification.json`

## Compatibility Boundary

- `skills/using-aegis/SKILL.md` and all frontmatter descriptions are unchanged.
- Artifact schema, `scripts/aegis-workspace.py`, host manifests, plugin identity,
  and installation surfaces are unchanged.
- Ordinary quick bugs do not create new artifact fields or invoke an
  architecture-review workflow.
- Directional reset remains advisory method-pack discipline.

## TDD Route

- Mode: `off`
- Decision: `skipped`
- Strict authority: `not applicable`
- Test posture: diagnostic baseline and post-change regression
- Reason: no explicit strict-TDD authority; the approved design calls for
  sample-driven workflow hardening and bounded replay.
- Verification: stateful positive fixture, independent/quick negative controls,
  context budgets, deterministic e2e checks, and post-change replay.

## Plan Basis

- Fact: the first unmodified replay checkpoint retained a completed Answering
  mitigation and returned `continue` after its targeted pass.
- Fact: two differently phrased later consumer candidates were both stopped
  before edit by current skills using that checkpoint.
- Fact: an independent provider serializer bug stayed on the quick path.
- Inference: semantic diagnosis is already sufficient; only explicit state
  carriage/readback and regression anchoring need reinforcement.
- Dropped assumption: a new `repairDirectionSummary` field/helper lifecycle is
  required for correctness.
- Unknown: live host/model variance remains advisory evidence, not a portable
  guarantee.

## BaselineUsageDraft

- Required refs: all authority and evidence refs above.
- Acknowledged before plan: all authority and evidence refs above.
- Cited in plan: all authority and evidence refs above.
- Missing refs: none.
- Decision: `continue`.

## Requirement Ready Check

- Requirement source: approved reduced Design Spec and user implementation
  authorization.
- Scenario: locally green consumer mitigation followed by differently named
  carrier; independent canonical-owner negative control.
- Acceptance: Design Spec section 11.
- Open blocker questions: none.
- Decision: `ready`.

## Change Necessity

- User-visible need: avoid repeated local consumer repairs without degrading
  ordinary Aegis invocation behavior.
- No-change option: rejected because current checkpoint wording does not
  explicitly require triggered patch-shape/owner/upward-signal state to survive
  a locally green slice.
- Minimum boundary: three existing skills, three current docs, and existing
  workflow/trigger/context/debugging tests.
- Decision: `code-change` limited to method contract text and fixtures; no
  helper/schema code change.

## Existence Check

- Proposed new surface: none.
- Existing owner/reuse: current checkpoint/evidence fields and existing tests.
- Creation proof: absent for a new schema field, helper command, or skill.
- Entropy/retirement: retire the disproven structured-field proposal before
  implementation.
- Decision: `reuse-existing`.

## Architecture Integrity Lens

- Invariant: a later carrier must not turn Answering into a second semantic
  owner.
- Canonical owner: debugging judges direction; long-task carries facts;
  executing-plans pauses/rewinds.
- Responsibility overlap: no helper semantic inference and no second classifier.
- Higher-level simplification: use current checkpoint/evidence surfaces.
- Falsifier result: structured schema/helper path rejected by live evidence.
- Verdict: `proceed` with reduced implementation.

## Anti-Entropy Declaration

- Deletion Class: `code-retirement` of an unimplemented proposal and an internal
  locally-green history-loss behavior.
- Old Path/Object: proposed `repairDirectionSummary`/helper lifecycle and
  implicit permission to forget prior patch shape after a passing test.
- New Canonical Owner: existing workflow/checkpoint owners.
- Expected Preserved Behavior: current routing, quick bugs, independent roots,
  artifacts, helper CLI, and host distribution.
- Expected Retired Behavior: history loss and the unnecessary schema path.
- External Boundary Touched: no.
- Source-of-Truth Data Risk: none.
- User Confirmation Required: no.

Retirement Decision:

- Path: `delete-first` from design/plan before source implementation.
- Non-edits: helper, schema, router, descriptions, hosts, manifests.

## Files

Modify:

- `skills/systematic-debugging/SKILL.md`
- `skills/executing-plans/SKILL.md`
- `skills/long-task-continuation/SKILL.md`
- `docs/current/AEGIS_PROCESS_BASELINE.md`
- `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`
- `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`
- `tests/e2e/fixtures/workflow-quality-matrix.json`
- `tests/e2e/fixtures/trigger-health-matrix.json`
- `tests/helpers/validate_workflow_quality_matrix.py`
- `tests/e2e/workflow-quality-check.sh`
- `tests/e2e/long-task-continuation-check.sh`
- `tests/e2e/debugging-patch-shape-gate-check.sh`
- `tests/e2e/context-budget-check.sh`

Explicit non-edits:

- `scripts/aegis-workspace.py`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `skills/using-aegis/SKILL.md`
- all skill descriptions and host/plugin surfaces
- `.codex/config.toml`

## Plan-Time Complexity Check

- Artifact class: skill, maintained test, current docs.
- Current pressure: `systematic-debugging`, process/workflow docs, matrix, and
  validator are large maintained artifacts.
- Owner fit: compact local clauses and existing fixture owners only.
- Projected pressure: at risk if full schema/state-machine prose is copied.
- Safer boundary: no new files; add concise anchors and reuse matrix validation.
- Budget result: `within-budget if caps pass`.
- Recommendation: `edit-in-place`, compress duplicates in the touched block.

## Execution Readiness View

- Intent Lock: close checkpoint state loss only.
- Scope Fence: three skills, three current docs, existing tests/fixtures.
- Baseline Lock: advisory Method Pack; no runtime authority.
- Approved Behavior: locally green patch shape survives; convergent candidate
  pauses; independent quick bug proceeds.
- Compatibility: no schema/helper/router/description/host changes.
- Retirement: structured-field proposal remains absent.
- Test Obligations: Tasks 1-4 below.
- Review Gates: stop on any new artifact field, helper logic, semantic second
  owner, raised using-aegis threshold, or quick-path regression.
- Drift/Rewind: return to this plan if a gate fires.
- Advisory Boundary: no `GateDecision`, `PolicySnapshot`, or completion grant.

## Tasks

### Task 1: Preserve The Falsification Baseline

Status: `completed before source edits`.

Evidence:

- deterministic context/trigger/workflow/artifact baselines passed
- explicit second filter paused
- disguised relation-section consumer guard paused
- independent canonical serializer mapping stayed on quick path
- raw replay logs were not retained

Commit the approved/reduced planning artifacts before workflow edits:

```bash
git commit -m "docs: reduce directional reset implementation"
```

### Task 2: Add Representative Stateful And Quick-Path Contracts

Files:

- workflow/trigger fixtures, workflow validator, and existing e2e checks listed
  above

Steps:

1. Extend `quick-single-owner-bug.mustNotDo` with
   `create-repair-direction-artifact` and `invoke-architecture-review`.
2. Add workflow sample `directional-reset-after-local-pass`:
   - primary `systematic-debugging`
   - allowed `long-task-continuation`, `executing-plans`,
     `first-principles-review`
   - forbid `erase-patch-shape-after-targeted-pass`,
     `treat-new-carrier-as-new-direction-by-name`, and
     `edit-second-consumer-guard-before-owner-review`
   - require checkpoint repair-direction readback and pre-edit pause/rewind
3. Strengthen trigger-health `repeated-fixes` so its prompt includes a locally
   green prior mitigation plus a differently named later carrier; allow
   `long-task-continuation` as state carrier.
4. Update existing validators/checks for those exact samples and anchors.
5. Add changed-skill byte-growth budgets while leaving
   `max_hot_path_chars=2500` untouched:
   - `29561 + 350` systematic debugging
   - `7823 + 450` executing plans
   - `11247 + 650` long-task continuation

Verification:

```bash
bash tests/e2e/workflow-quality-check.sh
bash tests/e2e/trigger-health-check.sh
bash tests/e2e/context-budget-check.sh
```

Expected: fixture validation passes only after Task 3 supplies required skill
anchors; no hot-path threshold changes.

### Task 3: Add The Minimal Workflow Clauses

Files:

- the three skills and three current docs listed above

Pre-Edit Owner-Fit Decisions:

- `systematic-debugging`: local-fix-without-new-responsibility; add one compact
  state-carry rule near existing residual/H-class logic.
- `executing-plans`: local-fix-without-new-responsibility; add pre-edit readback
  near verification-driven repair handling.
- `long-task-continuation`: local-fix-without-new-responsibility; add bounded
  checkpoint carry/readback in existing per-slice and resume contracts.
- current docs: edit existing process/workflow/trigger owners; no new section
  copied into every doc.

Required behavior:

- locally green verification does not erase triggered `PatchShape`,
  `CanonicalOwner`, `UpwardDrillSignal`, decision, outcome, or evidence ref
- long-task checkpoint/resume carries that bounded readback
- executing-plans rereads it before an unplanned verification fix
- semantic sameness remains in `systematic-debugging`
- carrier/sample names alone neither merge nor split directions
- independent canonical-owner bugs stay on quick path

Verification:

```bash
bash tests/e2e/debugging-patch-shape-gate-check.sh
bash tests/e2e/long-task-continuation-check.sh
bash tests/e2e/workflow-quality-check.sh
bash tests/e2e/trigger-health-check.sh
bash tests/e2e/context-budget-check.sh
```

Expected: all exit `0` within fixed budgets.

Commit Tasks 2-3 together because fixtures and contract text form one atomic
behavioral slice:

```bash
git commit -m "feat: preserve repair direction across slices"
```

### Task 4: Full Verification And Closure

1. Replay the same bounded positive/disguised/independent scenarios against the
   modified skills and record final decisions only.
2. Run:

   ```bash
   git diff --check
   python tests/helpers/test_parse_codex_skills.py
   bash tests/e2e/aegis-workspace-check.sh
   bash tests/e2e/artifact-schema-check.sh
   bash tests/e2e/long-task-continuation-check.sh
   bash tests/e2e/debugging-patch-shape-gate-check.sh
   bash tests/e2e/workflow-quality-check.sh
   bash tests/e2e/trigger-health-check.sh
   bash tests/e2e/context-budget-check.sh
   bash tests/e2e/boundary-compliance-check.sh
   bash tests/e2e/governance-completion-contract-check.sh
   bash tests/e2e/layer1-fast-check.sh --host-profile none
   bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
   ```

3. Run live skill-triggering/explicit-skill suites with Codex when the local
   account/environment is available; otherwise record the environment gap.
4. Confirm no diff in explicit non-edit files and descriptions.
5. Run complexity/architecture/retirement closure and workspace bundle/check.
6. Commit verified work records or factual fixups:

   ```bash
   git commit -m "docs: close directional reset governance"
   ```

## Risks

- An agent can still ignore advisory checkpoint discipline.
- Static anchors can pass without behavioral depth; post-change replay remains
  required.
- Overbroad wording could make independent roots heavy; negative controls and
  fixed context budgets protect this boundary.

## Retirement

- Retire locally-green patch-shape loss and unplanned repair readback bypass.
- Do not implement or retain the disproven schema/helper path.
- Preserve existing artifacts, helper CLI, routing, descriptions, and hosts.
