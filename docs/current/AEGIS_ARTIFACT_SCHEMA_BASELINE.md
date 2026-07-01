# Aegis Artifact Schema Baseline

Status: `Approved`

## 1. Document Scope

This document defines the minimum schema baseline for the current runtime-ready artifacts of the `Aegis Method Pack`.

---

## 2. General Constraints

- Every artifact must be versionable
- Every artifact must have a stable name
- Every artifact must distinguish among:
  - method-pack produced
  - host-provided
  - future-runtime-authoritative

The current schema version is uniformly:

- `aegis.schema.v0`

When `<aegis-workspace-helper>` is available, it may validate JSON sidecar
artifacts against this minimum field baseline:

```bash
python <aegis-workspace-helper> validate-artifact --type TaskIntentDraft --file <artifact.json>
```

It may also create and assemble helper-backed task lifecycle artifacts under a
target project's `docs/aegis/work/YYYY-MM-DD-<slug>/` directory:

```bash
python <aegis-workspace-helper> new-work --root <target-project-root> ...
python <aegis-workspace-helper> add-checkpoint --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python <aegis-workspace-helper> add-evidence --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python <aegis-workspace-helper> add-drift-check --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python <aegis-workspace-helper> bundle --root <target-project-root> --work YYYY-MM-DD-<slug>
```

That validation is structural only. It does not determine evidence sufficiency,
produce authoritative `GateDecision`, or grant completion authority.

An on-demand `Trace Digest` may summarize observed execution, evidence chain,
retrieval chain, rule effects, skill-call stability, verification, and host
capability gaps. It is an advisory output shape, not a new authoritative
artifact, event log, `GateDecision`, or completion authority.

---

## 3. Artifact Definitions

### 3.1 `TaskIntentDraft`

Required fields:

- `schemaVersion`
- `requestedOutcome`
- `scope`
- `changeKinds`
- `riskHints`

Optional goal-framing fields:

- `goal`
- `successEvidence`
- `stopCondition`
- `nonGoals`

These optional fields are used by `goal-framing` and helper-generated work
records to define what the task is trying to satisfy, what evidence would count,
when to stop, and what is explicitly out of scope. They do not grant completion
authority.

Current owner:

- method pack

### 3.2 `BaselineReadSetHint`

Required fields:

- `schemaVersion`
- `candidateDocs`
- `whyRelevant`
- `missingAuthority`

Current owner:

- method pack

### 3.3 `BaselineUsageDraft`

Required fields:

- `schemaVersion`
- `taskId`
- `requiredBaselineRefs`
- `acknowledgedBeforePlanRefs`
- `citedInPlanRefs`
- `missingRefs`
- `decision`

Optional host-projected fields:

- `deliveredContextRefs`

Allowed `decision` values:

- `continue`
- `pause-for-user`
- `needs-baseline-readback`
- `needs-verification`
- `blocked`

Current owner:

- method pack / host projection

Purpose:

- Make baseline/context attention drift visible without claiming authoritative
  host observation or internal model-attention proof
- Distinguish baseline refs that were required, acknowledged before planning,
  and later cited in a plan or verification trail
- Surface missing baseline refs early enough to pause in
  `needs-baseline-readback`

### 3.4 `ImpactStatementDraft`

Required fields:

- `schemaVersion`
- `affectedLayers`
- `owners`
- `invariants`
- `compatBoundary`
- `nonGoals`

Current owner:

- method pack

### 3.5 `EvidenceBundleDraft`

Required fields:

- `schemaVersion`
- `artifactKey`
- `type`
- `source`
- `summary`
- `verifier`

Current owner:

- method pack / host projection

### 3.6 `GateInputPack`

Required fields:

- `schemaVersion`
- `baselineRefs`
- `impactStatement`
- `compatPlan`
- `retirementPlan`
- `evidenceBundle`

Current owner:

- method pack assembles
- future runtime core consumes

### 3.7 `TodoCheckpointDraft`

Required fields:

- `schemaVersion`
- `taskId`
- `currentTodo`
- `completedTodos`
- `activeSlice`
- `evidenceRefs`
- `blockedOn`
- `nextStep`
- `updatedAt`

Current owner:

- method pack

### 3.8 `ResumeStateHint`

Required fields:

- `schemaVersion`
- `taskId`
- `lastCheckpointRef`
- `resumeInstruction`
- `knownPartialWork`
- `mustReadBeforeContinuing`
- `unsafeToAssume`

Current owner:

- method pack / host projection

### 3.9 `DriftCheckDraft`

Required fields:

- `schemaVersion`
- `taskId`
- `taskIntentRef`
- `baselineRefs`
- `scopeStatus`
- `compatStatus`
- `retirementStatus`
- `newRiskSignals`
- `decision`

Allowed `decision` values:

- `continue`
- `pause-for-user`
- `needs-baseline-readback`
- `needs-verification`
- `blocked`

Current owner:

- method pack

### 3.10 `SubagentContextPacket`

Required fields:

- `schemaVersion`
- `task`
- `goal`
- `stopCondition`
- `relevantBaselineRefs`
- `relevantFiles`
- `knownFacts`
- `unknowns`
- `nonGoals`
- `expectedOutput`
- `verificationExpected`
- `mustReadExcerpts`
- `unsafeAssumptions`

Current owner:

- method pack / host projection

Purpose:

- Give subagents the smallest useful task context without inheriting the full
  conversation
- Preserve the requirement that critical facts still come from bounded raw
  evidence excerpts, not controller summaries alone

---

## 4. Authority Boundary

The following artifacts are currently only permitted to be:

- draft
- hint
- projection input

Not permitted to be directly written by the method pack as:

- authoritative `BaselineRef[]`
- authoritative `PolicySnapshot`
- authoritative `GateDecision`
- authoritative `Trace Digest`
- `completion authority`
