# Aegis Artifact Schema Baseline

状态：`Approved`

## 1. 文档定位

本文档定义 `Aegis Method Pack` 当前 runtime-ready artifacts 的最小 schema baseline。

---

## 2. 通用约束

- 每个 artifact 必须可版本化
- 每个 artifact 必须有稳定名称
- 每个 artifact 必须区分：
  - method-pack produced
  - host-provided
  - future-runtime-authoritative

当前 schema version 统一为：

- `aegis.schema.v0`

---

## 3. Artifact Definitions

### 3.1 `TaskIntentDraft`

必填字段：

- `schemaVersion`
- `requestedOutcome`
- `scope`
- `changeKinds`
- `riskHints`

当前 owner：

- method pack

### 3.2 `BaselineReadSetHint`

必填字段：

- `schemaVersion`
- `candidateDocs`
- `whyRelevant`
- `missingAuthority`

当前 owner：

- method pack

### 3.3 `ImpactStatementDraft`

必填字段：

- `schemaVersion`
- `affectedLayers`
- `owners`
- `invariants`
- `compatBoundary`
- `nonGoals`

当前 owner：

- method pack

### 3.4 `EvidenceBundleDraft`

必填字段：

- `schemaVersion`
- `artifactKey`
- `type`
- `source`
- `summary`
- `verifier`

当前 owner：

- method pack / host projection

### 3.5 `GateInputPack`

必填字段：

- `schemaVersion`
- `baselineRefs`
- `impactStatement`
- `compatPlan`
- `retirementPlan`
- `evidenceBundle`

当前 owner：

- method pack assembles
- future runtime core consumes

### 3.6 `TodoCheckpointDraft`

必填字段：

- `schemaVersion`
- `taskId`
- `currentTodo`
- `completedTodos`
- `activeSlice`
- `evidenceRefs`
- `blockedOn`
- `nextStep`
- `updatedAt`

当前 owner：

- method pack

### 3.7 `ResumeStateHint`

必填字段：

- `schemaVersion`
- `taskId`
- `lastCheckpointRef`
- `resumeInstruction`
- `knownPartialWork`
- `mustReadBeforeContinuing`
- `unsafeToAssume`

当前 owner：

- method pack / host projection

### 3.8 `DriftCheckDraft`

必填字段：

- `schemaVersion`
- `taskId`
- `taskIntentRef`
- `baselineRefs`
- `scopeStatus`
- `compatStatus`
- `retirementStatus`
- `newRiskSignals`
- `decision`

允许的 `decision`：

- `continue`
- `pause-for-user`
- `needs-baseline-readback`
- `needs-verification`
- `blocked`

当前 owner：

- method pack

---

## 4. Authority Boundary

以下 artifacts 当前只允许是：

- draft
- hint
- projection input

不允许被 method pack 直接写成：

- authoritative `BaselineRef[]`
- authoritative `PolicySnapshot`
- authoritative `GateDecision`
- `completion authority`
