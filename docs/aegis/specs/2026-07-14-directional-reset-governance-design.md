# Directional Reset Governance Design

Status: `Approved for implementation — reduced after falsification`

Date: `2026-07-14`

## 1. Decision Summary

Aegis will close the repeated-local-repair gap by making existing checkpoint
state preserve and replay the repair direction after a locally green test.

The implementation will not add `repairDirectionSummary`, change
`DriftCheckDraft`, modify the workspace helper, or create a new workflow owner.
It will reuse:

- `systematic-debugging` for semantic owner and causal-topology judgment
- `TodoCheckpointDraft.completedTodos` / `activeSlice` and bounded evidence
  refs for repair-direction carriage
- `executing-plans` for pre-edit readback and plan rewind
- `long-task-continuation` for checkpoint, compaction, handoff, and resume
- existing workflow-quality, trigger-health, and context-budget checks

## 2. Problem Statement

A real task accumulated multiple Answering-side semantic filters. Each targeted
test passed, then another carrier exposed the same class of leak. The failure
was not missing diagnostic knowledge: current `systematic-debugging` already
recognizes consumer patches, duplicate owners, fallback growth, downstream
re-inference, and repeated fixes.

The narrower gap is longitudinal execution discipline:

1. a locally passing test can make a repair slice look complete
2. the checkpoint may preserve the completed edit without clearly retaining
   its patch shape, owner assumption, and unresolved upward signal
3. the next verification-driven candidate can form before that state is read
   back and compared

## 3. Falsification Result

The original design proposed an optional structured Drift Check field and
helper lifecycle. Before implementation, the approved falsifier was run against
the unmodified skills.

Observed bounded results:

| Scenario | Current behavior |
| --- | --- |
| First bounded Answering mitigation, targeted test passes | ordinary checkpoint, `continue` |
| Next carrier explicitly proposed as another Answering filter | paused before editing |
| Relation-bundle guard disguised as `_build_relation_section` pruning | still classified as consumer guard and paused |
| Independent provider serializer mapping at its canonical owner | remained on the quick path |

This proves the current semantic owner can distinguish convergent consumer
patches from independent single-owner repairs when the prior slice survives in
checkpoint readback. The structured field/helper proposal is therefore
unnecessary and is retired before implementation.

## 4. First-Principles Invariants

1. A targeted test passing does not erase the patch shape or owner assumption
   that produced the edit.
2. A test failure is evidence, not authorization to create another semantic
   owner.
3. Same-direction judgment remains semantic: invariant, owner/contract seam,
   patch shape, and causal topology matter; carrier names do not decide it.
4. Independent compound roots and ordinary canonical-owner bugs remain
   independently repairable.
5. Method-pack checkpoints are advisory state, not runtime authority or
   completion authority.
6. A new schema field must not exist when current artifacts can carry enough
   state to make the correct next decision.

## 5. Owner Boundary

- `systematic-debugging`: decides whether a candidate shares the prior repair
  direction, requires more diagnosis, or may proceed at the canonical owner.
- `long-task-continuation`: preserves bounded prior-direction facts and evidence
  across slices; it does not decide semantic sameness.
- `executing-plans`: reads the checkpoint before an unplanned repair and routes
  semantic judgment back to `systematic-debugging`; it does not create a second
  classifier.
- Existing checkpoint/evidence artifacts: carry facts only.
- Workspace helper: unchanged structural lifecycle support.

## 6. Existing-State Contract

### 6.1 When State Must Be Carried

After a slice in which Patch-Shape Triage, Ripple Signal Triage, an H-class
finding, or a bounded compatibility mitigation was relevant, the next
checkpoint must retain a compact repair-direction readback even when targeted
verification passes.

The readback reuses existing checkpoint prose and evidence refs and includes:

- `PatchShape`
- `CanonicalOwner`
- `UpwardDrillSignal`
- the implemented or rejected decision
- latest verification outcome
- bounded evidence ref

It must not include raw logs, full diffs, payload dumps, or an append-only
repair ledger.

### 6.2 Before The Next Unplanned Repair

When verification reveals another candidate edit:

1. read the latest checkpoint and referenced evidence
2. compare the candidate with the prior invariant, owner/contract seam, patch
   shape, and causal topology
3. route consumer/caller/fallback/downstream-reinference candidates through
   `systematic-debugging`
4. pause before editing when the paths converge or would keep duplicate owners
   active
5. allow an independent canonical-owner fix to remain on the ordinary quick
   path after topology evidence

The second-candidate rule is a backstop, not permission for the first consumer
patch. Existing H-class pre-edit triage still applies to the first candidate.

### 6.3 Quick-Path Boundary

An ordinary single-owner bug with no consumer patch, fallback, duplicate owner,
contract ambiguity, or residual cross-slice direction:

- stays in the existing quick bug lane
- does not create new workspace artifact fields
- does not invoke the Architecture Integrity Lens
- does not acquire an extra skill route

## 7. Workflow Changes

### 7.1 `systematic-debugging`

Add only a compact state-carry obligation:

- locally green verification does not erase a triggered patch shape
- when a long-task checkpoint exists, carry the bounded repair-direction
  readback forward
- a later carrier/sample name does not establish a new direction

Do not add another diagnostic section or duplicate checkpoint semantics.

### 7.2 `executing-plans`

Before an unplanned repair caused by verification output:

- read prior checkpoint/evidence patch-shape state
- compare the candidate with plan owner, contract, compatibility, and
  retirement boundaries
- route semantic comparison to `systematic-debugging`
- rewind to diagnostic/plan review instead of forming another local branch when
  the directions converge

### 7.3 `long-task-continuation`

Extend existing per-slice/checkpoint wording so triggered patch-shape state and
its locally green outcome remain in bounded checkpoint/evidence readback across
compaction, handoff, and resume.

No JSON schema change is required.

## 8. Verification Design

### 8.1 Positive Stateful Sample

Model two slices:

1. an approved bounded consumer mitigation passes targeted verification and the
   checkpoint retains its patch shape, owner assumption, upward signal, outcome,
   and evidence ref
2. a differently named carrier suggests a convergent consumer-side guard

Expected: the second candidate pauses before editing and returns to diagnostic
or plan review.

### 8.2 Negative Controls

- an independent canonical-owner serializer bug remains on the quick path
- similar presentation with a different invariant/owner seam is not grouped
  solely by wording
- a simple single-owner bug does not create new artifacts or architecture
  ceremony
- a locally green result remains evidence but not whole-task completion

### 8.3 Call And Context Stability

- `using-aegis` and every skill description remain unchanged
- the existing `using-aegis` threshold stays `2500`; it is not raised
- changed-skill growth is capped against the pre-change byte counts:
  - `systematic-debugging`: `29561 + 350`
  - `executing-plans`: `7823 + 450`
  - `long-task-continuation`: `11247 + 650`
- ordinary quick-path fixtures forbid a repair-direction artifact and an extra
  architecture-review invocation

### 8.4 Deterministic Checks

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

Run live skill-triggering/explicit-skill suites when the local host/account is
available; otherwise report the environment-bound gap.

## 9. Compatibility And Retirement

Repair track:

- preserve and reread existing checkpoint/evidence state after local success
- add representative stateful and quick-path fixtures
- keep semantic judgment in the current debugging owner

Retirement track:

- retire locally-green history loss
- retire unplanned verification fixes that bypass prior-state readback
- retire the proposed `repairDirectionSummary` field, helper flags, validation
  lifecycle, and directional risk enum before they enter implementation

Compatibility boundary:

- no artifact schema/helper/CLI changes
- no host, manifest, installation, router, or description changes
- no new workflow owner or runtime authority
- no automatic stop for proven independent roots

## 10. Complexity And Residual Risk

- The implementation touches three existing skills with compact clauses and
  reuses current test owners.
- The largest residual risk is behavioral omission: an agent may ignore the
  checkpoint contract. Stateful fixtures and live replay reduce this but cannot
  turn a method pack into a runtime gate.
- Static strings are anchors only; the pre/post bounded replay is the behavioral
  evidence.
- If implementation needs schema/helper changes, a new semantic classifier, or
  broader router wording, stop and return to design review.

## 11. Acceptance Criteria

1. No new skill, artifact field/type, helper lifecycle, runtime gate, router
   branch, or completion owner is created.
2. A locally green H-class or compatibility-mitigation slice retains bounded
   patch-shape/owner/upward-signal/outcome evidence in the existing checkpoint.
3. A later convergent consumer candidate pauses before editing.
4. Carrier or sample renaming alone cannot disguise the prior direction.
5. Independent canonical-owner and ordinary single-owner fixes remain on the
   quick path.
6. `using-aegis`, skill descriptions, host distribution, and artifact schemas
   remain unchanged.
7. Changed-skill context budgets pass without raising thresholds.
8. Deterministic checks and bounded forward replay support the completion
   claim; uncovered live-host checks are reported explicitly.

## 12. User Decision

The user approved implementation on `2026-07-14`. This reduced design follows
the original approved falsifier and narrows implementation risk without
changing the requested outcome.
