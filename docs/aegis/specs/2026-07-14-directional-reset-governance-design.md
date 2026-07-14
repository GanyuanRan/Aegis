# Directional Reset Governance Design

Status: `Draft for user review`

Date: `2026-07-14`

## 1. Decision Summary

Aegis should prevent repeated same-class local repairs from being treated as
unrelated new bugs when their causal paths converge on the same owner or
contract boundary.

The design will not add a new skill, artifact type, global router gate, or
authoritative runtime decision. It will reuse:

- `systematic-debugging` as the canonical repair-direction owner
- `executing-plans` as the plan-slice pause and rewind point
- `long-task-continuation` and `DriftCheckDraft.newRiskSignals` as the
  longitudinal state carrier
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

## 6. Existence Check

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

### 8.1 Repair Attempt

A repair attempt is one edit-and-verification cycle associated with the same
user-visible failure, owner seam, source-of-truth boundary, or contract family.

It remains part of the history even when its targeted test passes.

### 8.2 Directional Risk Signals

Use these reserved advisory labels inside
`DriftCheckDraft.newRiskSignals` when evidence supports them:

- `duplicate-owner`
- `unplanned-consumer-semantics`
- `plan-owner-contradiction`
- `repeated-same-class-patch-shape`

These labels report observed method-workflow risk. They do not prove an
authoritative architecture decision.

### 8.3 Reset Conditions

Pause source edits and return to diagnostic/plan review when any of these is
true:

1. a proposed edit would keep two semantic owners active
2. a plan that forbids new semantic branches now requires a consumer-side
   semantic branch
3. a second repair attempt hits the same patch-shape family and the causal
   paths converge on the same upstream owner or contract seam
4. an earlier local repair reduced one symptom but residual behavior still
   requires another consumer-side interpretation of the same semantic input

Do not trigger solely because two fixes exist. Independent compound roots may
need two independent repairs. Use the existing causal topology and
anti-disguise checks to distinguish them.

### 8.4 Required Transition

When a reset condition is active:

1. stop new source edits
2. record the repair attempts and reserved risk label in the active checkpoint
3. set the Drift Check decision to `pause-for-user`; do not use `continue`
4. re-enter `systematic-debugging` for differential diagnosis
5. compose the `Architecture Integrity Lens`
6. classify `Design Defect` or `Implementation Drift`
7. return to design/plan review before implementation resumes

`pause-for-user` is reused because an owner/contract correction changes the
approved implementation direction. No new decision enum is required.

## 9. Workflow Changes

### 9.1 `systematic-debugging`

Keep its canonical-owner and differential-diagnosis logic. Make only the
smallest clarification needed:

- a locally passing test does not remove an attempt from repeated-repair
  analysis
- a second same-class, convergent consumer patch is an earlier architecture
  reset signal; it does not need to wait for a fourth failed fix

Do not duplicate the full checkpoint or plan workflow here.

### 9.2 `executing-plans`

Before an unplanned repair caused by verification output:

- compare the candidate edit with the plan's owner, contract, branch,
  compatibility, and retirement boundaries
- route patch-shape candidates through `systematic-debugging`
- if a reset condition is active, freeze the task and return to plan review
  instead of treating the repair as an implementation detail

### 9.3 `long-task-continuation`

Extend the existing Drift Check contract to:

- preserve repair-attempt summaries across slices and resumes
- use the reserved risk labels when supported by evidence
- forbid `continue` while a reserved directional risk remains unresolved
- carry the reset and rewind state into the next checkpoint

### 9.4 Workspace Helper

Add structural validation only:

- a `DriftCheckDraft` containing a reserved directional risk label cannot use
  `decision: continue`
- the same draft may use `pause-for-user`, `needs-baseline-readback`,
  `needs-verification`, or `blocked` as appropriate

The helper validates internal consistency of an agent-authored draft. It does
not detect the risk itself and does not decide whether the architecture is
correct.

## 10. Verification Design

### 10.1 Baseline Pressure Evidence

Preserve both pieces of evidence:

- the real task where longitudinal execution continued patching
- the current-version read-only scenario where an explicit cumulative summary
  caused the agent to stop

The difference is the behavior the change must close.

### 10.2 Stateful Positive Scenario

Model at least three slices:

1. first consumer filter; targeted verification passes
2. second carrier exposes the same semantic leak; candidate second filter
3. checkpoint/plan execution must stop before the second same-root consumer
   interpretation is implemented

Expected behavior:

- repair history survives the locally green result
- causal convergence is checked
- a reserved risk label is recorded
- decision is not `continue`
- source edits pause and the workflow returns to diagnostic/plan review

### 10.3 Negative Controls

- an ordinary single-owner bug stays on the quick path
- two genuinely independent compound roots may receive two repairs after
  topology proof
- an informational risk that is not a reserved directional signal may still
  use `continue`

### 10.4 Deterministic Checks

Add or update:

- workspace helper tests for reserved risk/decision consistency
- trigger-health or workflow-quality fixtures for the stateful sequence and
  negative controls
- static contract checks for the owning workflow language
- existing workflow quality, trigger health, context budget, boundary, parser,
  and layer-one fast checks as required by the final touched surface

### 10.5 Forward Validation

Before changing skills, capture the current response to the pressure scenario.
After changing each skill, re-run a minimal-context forward test without
leaking the intended answer. Compare behavior, not keyword presence.

## 11. Compatibility and Retirement

### Repair Track

- Repair the missing cross-slice signal carriage.
- Keep `systematic-debugging` as canonical owner.
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

## 12. Plan-Time Complexity Check

- Artifact class: method workflow skills, current docs, helper validation, and
  regression fixtures
- Likely target files: existing skill bodies and existing verification owners
- Current pressure: `systematic-debugging` is already large; adding another
  full workflow section would increase context and duplication
- Projected pressure: at risk if the reset contract is copied into every skill
- Planned governance: keep judgment in `systematic-debugging`; use compact
  transition clauses elsewhere; prefer shared baseline wording over duplicated
  prose
- Recommendation: edit existing owners with compact clauses; do not add a new
  skill or artifact file type

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
2. A locally green test does not erase relevant same-root repair history.
3. A second same-class convergent consumer repair pauses before source editing.
4. Duplicate-owner and plan-owner contradictions cannot coexist with
   `DriftCheckDraft.decision: continue` when recorded using reserved labels.
5. Independent compound roots and ordinary single-owner bugs remain supported.
6. Stateful behavioral validation supplements, rather than merely expands,
   static string assertions.
7. Existing host distribution and method-pack authority boundaries remain
   unchanged.

## 15. User Decision

Approve, revise, or reject this Design Spec before implementation planning.
