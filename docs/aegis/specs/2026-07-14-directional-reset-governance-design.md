# Directional Reset Governance Design

Status: `Draft for user review`

Date: `2026-07-14`

## 1. Decision Summary

The Aegis workflow should make repeated same-class local repairs a mandatory
advisory stop transition before another edit when their causal paths converge
on the same owner or contract boundary.

The design will not add a new skill, artifact type, global router gate, or
authoritative runtime decision. It will reuse:

- `systematic-debugging` as the canonical repair-direction owner
- `executing-plans` as the plan-slice pause and rewind point
- `long-task-continuation` and an optional, bounded
  `DriftCheckDraft.repairDirectionSummary` as the longitudinal history carrier
- `DriftCheckDraft.newRiskSignals` as the active unresolved-risk surface
- `first-principles-review` as the compositional architecture lens
- the workspace helper as a structural consistency validator only

## 2. Problem Statement

The current method pack already says that consumer-side patches, duplicate
owners, downstream re-inference, new fallbacks, and repeated failed fixes are
hard signals to stop and investigate upward.

A real task nevertheless accumulated several Answering-side filters. Each
targeted test passed, then another evidence carrier exposed the same class of
leak. The agent treated each result as a new case instead of preserving the
cumulative direction signal.

This is not primarily a routing failure. It is an execution-depth and
longitudinal-state gap:

1. local success makes an attempted repair look complete
2. the next residual is evaluated without a compact repair-history readback
3. the failed-fix counter can reset because the previous targeted test passed
4. plan execution allows a new candidate edit to form before the cumulative
   patch shape is reconsidered

## 3. Evidence and Falsification

### 3.1 Existing Rules Are Not Missing

Current `systematic-debugging` already requires:

- patch-shape triage before consumer/caller guards and fallbacks
- canonical-owner identification
- differential diagnosis after residual symptoms
- architecture review after repeated failed fixes
- H-class findings for consumer patches, downstream re-inference, duplicate
  owners, and new fallback paths

Current static verification passes for these rules. Therefore adding another
paragraph with equivalent warnings is not sufficient evidence of improvement.

### 3.2 Current-Version Pressure Readback

A read-only pressure scenario supplied the current skills with an explicit
summary of three locally passing Answering-side repairs, a growing compiler,
and a proposed fourth guard.

The current skills produced the correct result:

- `Decision: escalate / pause-for-user`
- do not continue editing
- do not assume Answering is the canonical owner
- return to architecture and plan review

This falsifies the assumption that the debugging skill cannot reason about the
pattern. It supports the narrower diagnosis: during long execution, the
pattern is not reliably accumulated and handed back to that skill.

### 3.3 Remaining Falsifier

If a stateful replay proves that the current unmodified workflow already
records cumulative patch-shape history and consistently stops before another
same-root consumer edit, this design should be rejected or reduced to a test
fixture only.

## 4. First-Principles Invariants

1. A test failure is evidence, not authorization to create a new semantic
   owner.
2. A targeted test passing does not erase the repair shape or owner assumption
   that produced the change.
3. Repeated residuals whose causal paths converge on the same owner seam are a
   directional signal, even if each preceding local test passed.
4. Legitimate independent compound roots must remain independently repairable.
5. Method-pack enforcement may validate its own workflow-state consistency,
   but it may not decide architecture truth or grant completion authority.

## 5. Baseline Role Alignment

- Product / Requirement Baseline: Aegis must reduce repeated local patching
  without making ordinary bug fixes heavy.
- Architecture / Runtime Boundary Baseline: `systematic-debugging` remains the
  only repair-direction owner; checkpoint and plan workflows carry state but
  do not judge final architecture truth independently.
- Result: `Design Defect + Implementation Drift`
- Scope: `both`
- Next action: repair the longitudinal execution contract and verify it with a
  stateful pressure scenario.

## 6. Existence Checks

### 6.1 New Workflow Owner Or Artifact

- Proposed new surface: a separate directional-reset skill, gate, or artifact
  was considered.
- Existing owner / reuse candidate: `systematic-debugging`,
  `DriftCheckDraft.newRiskSignals`, `Execution Readiness View`, and the existing
  plan rewind path.
- Why existing surface is insufficient: the surfaces exist, but cumulative
  signal carriage and decision consistency are not explicit enough.
- Creation proof: absent for a new skill or artifact.
- Entropy / retirement impact: a new owner would duplicate debugging and drift
  responsibilities.
- Decision: `reuse-existing`.

### 6.2 Bounded Direction Summary Field

- Proposed new surface: optional `repairDirectionSummary` inside the existing
  `DriftCheckDraft`.
- Existing owner / reuse candidate: `newRiskSignals`, checkpoint prose, and
  `TodoCheckpointDraft.evidenceRefs`.
- Why existing surface is insufficient: a free-text risk label cannot preserve
  stable direction identity, completed-attempt count, locally green outcome, or
  evidence needed to recognize the same direction after compaction or resume.
- Creation proof: the real task failed during longitudinal execution while the
  current-version pressure readback stopped correctly once the same history
  was explicitly summarized.
- Entropy / retirement impact: the field is optional, triggered only after a
  relevant repair candidate or completed attempt, bounded to one current
  direction summary and three recent evidence refs, and remains inside an
  existing artifact owner.
- Decision: `add-with-proof` for the optional field; still `reuse-existing` for
  skills, artifacts, and authority owners.

## 7. Architecture Integrity Lens

- Invariant: no downstream consumer becomes a second semantic owner because a
  later test exposes another carrier.
- Canonical owner / contract: `systematic-debugging` owns the decision to
  continue repair, investigate upward, or escalate.
- Responsibility overlap: `executing-plans` and `long-task-continuation` must
  not independently reinterpret repair correctness; they only preserve the
  evidence and enforce a pause/rewind transition.
- Higher-level simplification: reuse the existing Drift Check and plan review
  loop instead of adding another workflow.
- Retirement / falsifier: no old skill retires; the ambiguous practice of
  resetting repair history after each locally green test must retire. A
  stateful replay that already stops reliably would falsify the need for skill
  changes.
- Verdict: `revise design contract`, then update the smallest owning skills.

## 8. Directional Reset Semantics

### 8.1 Completed Attempt And Candidate

A completed repair attempt is one edit-and-verification cycle. A repair
candidate is a proposed next edit considered before source mutation.

A completed attempt or new candidate belongs to the current repair direction
only when `systematic-debugging` judges that it shares the invariant, owner or
contract seam, and patch-shape family. A similar user-visible symptom alone is
insufficient. A completed attempt remains part of the history even when its
targeted test passes.

### 8.2 Repair Direction Summary

`DriftCheckDraft` may contain one optional, bounded
`repairDirectionSummary`:

```json
{
  "directionKey": "one-admission-owner@context-to-answering/consumer-filter",
  "invariant": "one admitted evidence publication owner",
  "ownerSeam": "context-admission -> answering",
  "patchShapeFamily": "consumer-semantic-filter",
  "completedAttemptCount": 1,
  "latestOutcome": "targeted-pass",
  "status": "reset-required",
  "evidenceRefs": ["first-pass-ref", "second-candidate-ref"],
  "resolutionRef": null
}
```

Semantic comparison uses the tuple:

```text
(invariant, ownerSeam, patchShapeFamily)
```

Carrier names, sample strings, test filenames, and individual payload shapes
must not change the key when they exercise the same invariant at the same
owner seam through the same patch family.

`directionKey` is the compact persisted identity for that tuple. It is created
when the first relevant direction is tracked and must be carried forward
verbatim. A later agent must either reuse it or record evidence that the new
candidate differs in invariant, owner seam, or patch-shape family. Merely
rephrasing a component or naming a different carrier does not establish a new
direction.

Field constraints:

- `directionKey`, `invariant`, `ownerSeam`, and `patchShapeFamily` are non-empty,
  compact descriptors; they must not contain raw payloads, logs, or test output
- `completedAttemptCount` is non-negative and counts completed
  edit-and-verification cycles; it does not reset after `targeted-pass`
- `latestOutcome` is `targeted-pass | residual-persists | incomplete | unknown`
- `completedAttemptCount: 0` requires `latestOutcome: unknown`
- `status` is `active | reset-required | resolved`
- `evidenceRefs` contains at most the three most recent bounded evidence refs;
  older attempts remain represented by `completedAttemptCount`
- `resolutionRef` is required when `status` is `resolved`; otherwise it is null
- ordinary tasks and legacy drafts may omit `repairDirectionSummary`

Schema-optional is not workflow-optional after a direction-tracking trigger.
Create or update the summary:

- before an H-class consumer, caller, fallback, or downstream re-inference
  candidate is allowed to proceed after patch-shape triage
- when a residual makes a repeated same-direction repair plausible
- whenever any reset condition below is active

Ordinary single-owner fixes that do not meet these triggers do not create the
field.

The next proposed matching edit has candidate ordinal
`completedAttemptCount + 1`. It is not counted as completed before source
editing. Therefore a second candidate can set `status: reset-required` while
`completedAttemptCount` remains `1`; the candidate itself is referenced in
`evidenceRefs`.

State lifecycle:

- `active`: one relevant direction is being tracked and no reset condition is
  yet proven
- `reset-required`: a reset condition is proven; source edits stop
- `resolved`: architecture/plan review supplied resolution evidence; history
  remains visible in the resolution checkpoint, but active reserved risks are
  removed

Only one direction summary is active for an implementation slice. It cannot be
overwritten by a second key while `active` or `reset-required`. A proven
independent candidate does not increment or re-key the current summary. A later
direction may replace a `resolved` summary only after the final resolved
summary has been bundled in the task-local artifact named by `resolutionRef`.

### 8.3 Directional Risk Signals

Use these reserved advisory labels inside
`DriftCheckDraft.newRiskSignals` when evidence supports them:

- `duplicate-owner`
- `unplanned-consumer-semantics`
- `plan-owner-contradiction`
- `repeated-same-class-patch-shape`

These labels report observed method-workflow risk. They do not prove an
authoritative architecture decision.

`newRiskSignals` contains active unresolved risks, not append-only history.
Resolved history stays in `repairDirectionSummary` with a non-null
`resolutionRef`.

### 8.4 Reset Conditions

Pause source edits and return to diagnostic/plan review when any of these is
true:

1. a proposed edit would keep two semantic owners active
2. a plan that forbids new semantic branches now requires a consumer-side
   semantic branch
3. a proposed candidate would be the second matching repair attempt and the
   causal paths converge on the same upstream owner or contract seam
4. an earlier local repair reduced one symptom but residual behavior still
   requires another consumer-side interpretation of the same semantic input

The second-attempt rule is a backstop, not permission for the first local
consumer patch. The existing H-class patch-shape triage still applies before
the first edit. A first consumer-side semantic patch may proceed only when it
is proven to be at the canonical owner or is an explicitly bounded
compatibility mitigation with retention reason and retirement trigger.

Do not trigger solely because two fixes exist. Independent compound roots may
need two independent repairs. Use the existing causal topology and
anti-disguise checks to distinguish them.

### 8.5 Required Transition

When a reset condition is active:

1. stop new source edits
2. set `repairDirectionSummary.status` to `reset-required`
3. record the reserved active risk label and bounded evidence refs
4. set the Drift Check decision to `pause-for-user`; do not use `continue`
5. re-enter `systematic-debugging` for differential diagnosis
6. compose the `Architecture Integrity Lens`
7. classify `Design Defect` or `Implementation Drift`
8. return to design/plan review before implementation resumes

`pause-for-user` is reused because an owner/contract correction changes the
approved implementation direction. No new decision enum is required.

After user/plan review, continuing requires a new checkpoint that:

- sets the summary to `resolved`
- supplies `resolutionRef`
- removes all reserved directional labels for the resolved direction from
  active `newRiskSignals`
- records the new or reaffirmed owner/contract boundary

`resolutionRef` must resolve to an existing task-local evidence bundle that
contains the final direction key, completed-attempt count, disposition, and the
approved design/plan reference. A non-empty but unresolvable label is not
resolution evidence.

The summary must not be silently omitted or replaced while its status is
`active` or `reset-required`.

## 9. Workflow Changes

### 9.1 `systematic-debugging`

Keep its canonical-owner and differential-diagnosis logic. Make only the
smallest clarification needed:

- a locally passing test does not remove an attempt from repeated-repair
  analysis
- create or update the direction summary at the defined trigger; do not treat
  its schema optionality as permission to omit triggered state
- derive the repair-direction comparison key from the invariant, owner/contract
  seam, and patch-shape family; do not use carrier or sample identity as the
  key
- a second same-class, convergent consumer patch is an earlier architecture
  reset signal; it does not need to wait for a fourth failed fix

Do not duplicate the full checkpoint or plan workflow here.

### 9.2 `executing-plans`

Before an unplanned repair caused by verification output:

- compare the candidate edit with the plan's owner, contract, branch,
  compatibility, and retirement boundaries
- reuse `PatchShape`, `CanonicalOwner`, and `UpwardDrillSignal` to compare the
  candidate with any active `repairDirectionSummary`; do not add another
  repair-check artifact
- route patch-shape candidates through `systematic-debugging`
- if a reset condition is active, freeze the task and return to plan review
  instead of treating the repair as an implementation detail

### 9.3 `long-task-continuation`

Extend the existing Drift Check contract to:

- preserve the optional bounded `repairDirectionSummary` across slices,
  compaction, handoff, and resume
- keep `newRiskSignals` limited to active unresolved risks
- use the reserved risk labels when supported by evidence
- forbid `continue` while a reserved directional risk remains unresolved
- carry the reset and rewind state into the next checkpoint

### 9.4 Workspace Helper

Add structural validation only:

- a `DriftCheckDraft` containing a reserved directional risk label cannot use
  `decision: continue`
- `repairDirectionSummary.status: reset-required` requires
  `decision: pause-for-user` and at least one reserved directional risk label
- `repairDirectionSummary.status: resolved` requires a non-empty
  `resolutionRef`, a resolvable referenced artifact, and no reserved
  directional label in active `newRiskSignals`
- the same `directionKey` cannot lower `completedAttemptCount`
- an existing `active` or `reset-required` summary is preserved when an
  `add-drift-check` update does not explicitly replace or resolve it
- an `active` or `reset-required` summary cannot be replaced by a different
  `directionKey`
- legacy drafts without the optional summary remain valid

The helper validates internal consistency of an agent-authored draft. It does
not detect the risk itself and does not decide whether the architecture is
correct. In particular, it cannot prove that two differently named keys are
semantically independent; that judgment remains in `systematic-debugging` and
is exercised by the behavioral pressure scenario.

## 10. Verification Design

### 10.1 Baseline Pressure Evidence

Preserve both pieces of evidence:

- the real task where longitudinal execution continued patching
- the current-version read-only scenario where an explicit cumulative summary
  caused the agent to stop

The difference is the behavior the change must close.

### 10.2 Stateful Positive Scenario

Model at least three slices:

1. a pre-existing or explicitly bounded first consumer filter is recorded with
   `completedAttemptCount: 1`; targeted verification passes
2. second carrier exposes the same semantic leak; candidate second filter
3. checkpoint/plan execution must stop before the second same-root consumer
   interpretation is implemented

Expected behavior:

- repair history survives the locally green result
- carrier identity does not change the repair-direction comparison key
- the persisted `directionKey` is reused; the second candidate has derived
  ordinal `2`
- the bounded summary keeps `completedAttemptCount: 1` and reaches
  `status: reset-required` before the candidate is implemented
- causal convergence is checked
- a reserved risk label is recorded
- decision is not `continue`
- source edits pause and the workflow returns to diagnostic/plan review

### 10.3 Negative Controls

- an ordinary single-owner bug stays on the quick path
- two genuinely independent compound roots may receive two repairs after
  topology proof
- two similar symptoms with different invariants or owner seams do not share a
  direction key merely because their presentation looks alike
- rephrasing a matching invariant or naming a different carrier does not create
  a fresh direction key or reset the completed-attempt count
- a legacy `DriftCheckDraft` without `repairDirectionSummary` remains valid
- an informational risk that is not a reserved directional signal may still
  use `continue`

### 10.4 Deterministic Checks

Add or update:

- workspace helper tests for optional-summary compatibility, bounded fields,
  preserved active state, stable direction identity, non-decreasing completed
  count, resolvable resolution evidence, and reserved risk/decision consistency
- trigger-health or workflow-quality fixtures for the stateful sequence and
  negative controls
- the existing artifact-schema fixture with both legacy and optional-summary
  coverage
- static contract checks only for indispensable owner/transition anchors; do
  not treat additional string assertions as behavioral proof
- these repository checks, adjusted only if the final touched surface proves a
  smaller set is sufficient:

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

- run `tests/skill-triggering/run-all.sh` and
  `tests/explicit-skill-requests/run-all.sh` when their required local host and
  account environment is available; otherwise report them as environment-bound

### 10.5 Forward Validation

Before changing skills, run a multi-turn baseline pressure scenario in which
the first targeted verification passes and the next carrier appears only in a
later turn. Do not provide the final cumulative summary in the initial prompt.

After changing each skill, replay the same turn sequence with minimal context
and without leaking the intended answer. Compare whether checkpoint state and
the stop transition survive between turns; keyword presence is not behavioral
proof.

Bound all forward-test context to the direction summary and evidence refs. Do
not replay raw logs, full diffs, or unbounded repair history.

## 11. Compatibility and Retirement

### Repair Track

- Repair the missing cross-slice signal carriage.
- Keep `systematic-debugging` as canonical owner.
- Add only an optional bounded field to the existing Drift Check artifact.
- Preserve ordinary debugging and plan execution behavior.

### Retirement Track

- Retire the interpretation that a locally green test resets repair history.
- Retire ad hoc plan-execution fixes that bypass patch-shape triage.
- Do not retain a second directional-reset owner.

### Compatibility Boundary

- no host installation or manifest changes
- no new public plugin identity
- no authoritative runtime claims
- no strict TDD route implied by this design
- no automatic stop for independent compound roots solely because two edits
  exist
- existing `aegis.schema.v0` Drift Check artifacts without the optional field
  continue to validate
- the current schema contract is a minimum-field baseline and the validator
  already tolerates additive optional fields, so this addition does not require
  a schema-version cutover; that decision must be revisited if unknown fields
  later become invalid
- active state is compacted to one comparison key, a count, and at most three
  evidence refs; raw logs and full patch history do not enter checkpoints

## 12. Plan-Time Complexity Check

- Artifact class: method workflow skills, one backward-compatible optional
  Drift Check field, current docs, helper validation, and regression fixtures
- Likely target files: existing skill bodies and existing verification owners
- Current pressure: `systematic-debugging` is already large; adding another
  full workflow section would increase context and duplication
- Projected pressure: at risk if the reset contract is copied into every skill
  or if repair history becomes an unbounded ledger; free-text key aliases would
  recreate the original escape hatch
- Planned governance: keep judgment in `systematic-debugging`; use compact
  transition clauses elsewhere; bound the summary; prefer shared baseline
  wording over duplicated prose
- Recommendation: edit existing owners with compact clauses; do not add a new
  skill or artifact file type

### 12.1 Residual Risks And Limits

- Structural validation cannot prove that two free-text semantic descriptions
  are actually independent. Exact `directionKey` carry and behavioral pressure
  tests reduce aliasing, while `systematic-debugging` retains semantic judgment.
- Backward compatibility means the helper must accept a legacy draft with no
  summary. It therefore cannot infer that a first required summary was omitted;
  workflow trigger tests must cover creation, not only update validation.
- An agent or host that ignores the loaded workflow can still bypass an
  advisory stop. This design improves method discipline and draft consistency;
  it does not create a runtime enforcement gate.
- Over-triggering remains possible for superficially similar compound roots.
  Causal topology and the independent-root negative controls are required to
  keep ordinary debugging usable.
- The one-summary bound intentionally sacrifices an in-place historical ledger.
  Resolved summaries must be bundled before replacement so compaction does not
  become silent deletion.

## 13. ADR and Baseline Sync Signals

This design changes a durable workflow contract but does not change the
Method Pack / Runtime Core boundary.

At completion:

- run the ADR gate to decide whether the existing ADR remains sufficient
- update the smallest current process, workflow-quality, trigger-health, and
  artifact-schema docs needed to describe the implemented state
- do not record this draft as an accepted architecture decision until the user
  approves it and the implementation is executed

## 14. Acceptance Criteria

1. No new skill, artifact type, runtime gate, or completion owner is created.
2. Legacy Drift Check artifacts remain valid; the optional summary is used only
   when repair-direction history matters.
3. Once a direction-tracking trigger is met, the summary is created or updated
   before the candidate source edit; schema optionality cannot bypass this.
4. A locally green test does not erase relevant same-root repair history or
   reduce its completed-attempt count.
5. Different carriers exercising the same invariant, owner seam, and patch
   family retain the same persisted direction key; rewording alone cannot
   create a new key.
6. A second same-class convergent consumer repair pauses before source editing;
   this backstop does not weaken first-edit H-class triage.
7. Duplicate-owner and plan-owner contradictions cannot coexist with
   `DriftCheckDraft.decision: continue` when recorded using reserved labels.
8. Active or reset-required direction state cannot disappear during checkpoint
   update, compaction, handoff, or resume without resolution evidence.
9. Independent compound roots and ordinary single-owner bugs remain supported.
10. Stateful multi-turn behavioral validation supplements, rather than merely
   expands, static string assertions.
11. Direction history remains bounded and does not inject raw logs or full
    diffs into prompts or checkpoints.
12. Existing host distribution and method-pack authority boundaries remain
    unchanged.

## 15. User Decision

Approve, revise, or reject this Design Spec before implementation planning.
