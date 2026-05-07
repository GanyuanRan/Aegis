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

When `scripts/aegis-workspace.py` is available, it may validate JSON sidecar
artifacts against this minimum field baseline:

```bash
python scripts/aegis-workspace.py validate-artifact --type TaskIntentDraft --file <artifact.json>
```

That validation is structural only. It does not determine evidence sufficiency,
produce authoritative `GateDecision`, or grant completion authority.

---

## 3. Artifact Definitions

### 3.1 `TaskIntentDraft`

Required fields:

- `schemaVersion`
- `requestedOutcome`
- `scope`
- `changeKinds`
- `riskHints`

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

### 3.3 `ImpactStatementDraft`

Required fields:

- `schemaVersion`
- `affectedLayers`
- `owners`
- `invariants`
- `compatBoundary`
- `nonGoals`

Current owner:

- method pack

### 3.4 `EvidenceBundleDraft`

Required fields:

- `schemaVersion`
- `artifactKey`
- `type`
- `source`
- `summary`
- `verifier`

Current owner:

- method pack / host projection

### 3.5 `GateInputPack`

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

### 3.6 `TodoCheckpointDraft`

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

### 3.7 `ResumeStateHint`

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

### 3.8 `DriftCheckDraft`

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
- `completion authority`
