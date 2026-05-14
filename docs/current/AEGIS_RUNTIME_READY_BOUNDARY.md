# Aegis Runtime-Ready Boundary

Status: `Approved`

## 1. Document Scope

This document defines the minimum boundary between the current `Aegis Method Pack` and the future `Aegis Runtime Core`.

This document is only responsible for answering the following questions:

- Which runtime-ready artifacts can this repository stably produce
- Which authoritative outputs this repository must NOT adjudicate
- How the method layer, host projection layer, and runtime core should collaborate

This document is NOT responsible for answering the following questions:

- Node-level execution implementation of the runtime core
- Transport or API details of host adapters
- Database storage structures

---

## 2. Bottom Line Up Front

The goal of this repository is not to become a runtime core, but to become:

> A `runtime-ready method pack` that can stably produce governance inputs and governance projections

Therefore:

- This repository can generate drafts, templates, checklists, and artifact conventions
- This repository can require hosts to provide necessary missing information
- This repository can output advisory, warning-style process guidance
- This repository must NOT independently produce authoritative `GateDecision`
- This repository must NOT independently grant `completion authority`

---

## 3. Runtime-Ready Artifacts This Repository Can Produce

This repository is permitted and encouraged to produce the following artifacts:

### 3.1 `TaskIntentDraft`

Minimum fields:

- `requestedOutcome`
- `scope`
- `changeKinds`
- `riskHints`

Optional goal-framing fields:

- `goal`
- `successEvidence`
- `stopCondition`
- `nonGoals`

Purpose:

- Help the host and future runtime core establish unified task framing
- Make done, blocked, needs-verification, and scope-exceeded boundaries explicit
  before execution when the user invokes `/aegis-goal` or `Aegis goal:`

### 3.2 `BaselineReadSetHint`

Minimum fields:

- `candidateDocs`
- `whyRelevant`
- `missingAuthority`

Purpose:

- Indicate which baseline documents should be read first for the current task
- Expose authority gaps

### 3.3 `ImpactStatementDraft`

Minimum fields:

- `affectedLayers`
- `owners`
- `invariants`
- `compatBoundary`
- `nonGoals`

Purpose:

- Make high-risk tasks explicitly expose impact surface and compatibility boundaries before execution
- Carry Ripple Signal Triage results when a pre-change signal indicates downstream, owner, source-of-truth, contract, fallback, or verification-scope risk

### 3.4 `EvidenceBundleDraft`

Minimum fields:

- `artifactKey`
- `type`
- `source`
- `summary`
- `verifier`

Purpose:

- Unify the naming and minimum structure of evidence collection

### 3.5 `GateInputPack`

Minimum fields:

- `baselineRefs`
- `impactStatement`
- `compatPlan`
- `retirementPlan`
- `evidenceBundle`

Purpose:

- Serve as the minimum input package for the future runtime core

### 3.6 `TodoCheckpointDraft`

Minimum fields:

- `taskId`
- `currentTodo`
- `completedTodos`
- `activeSlice`
- `evidenceRefs`
- `blockedOn`
- `nextStep`
- `updatedAt`

Purpose:

- Enable long tasks to have recoverable todo / checkpoint state before and after each execution slice

### 3.7 `ResumeStateHint`

Minimum fields:

- `taskId`
- `lastCheckpointRef`
- `resumeInstruction`
- `knownPartialWork`
- `mustReadBeforeContinuing`
- `unsafeToAssume`

Purpose:

- Provide a minimal re-entry point during session resumption, context compression, or agent handoff

### 3.8 `DriftCheckDraft`

Minimum fields:

- `taskId`
- `taskIntentRef`
- `baselineRefs`
- `scopeStatus`
- `compatStatus`
- `retirementStatus`
- `newRiskSignals`
- `decision`

Purpose:

- Explicitly check whether goals, baselines, compatibility boundaries, and retirement tracks have drifted during long task execution

### 3.9 `SubagentContextPacket`

Minimum fields:

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

Purpose:

- Provide a compact delegation packet for subagents without inheriting full
  conversation context
- Require critical facts to stay tied to bounded evidence excerpts that the
  subagent may verify directly

---

## 4. Authoritative Outputs This Repository Must NOT Adjudicate

The following outputs can only be the responsibility of the future `Aegis Runtime Core`:

- Authoritative `BaselineRef[]`
- Authoritative `PolicySnapshot`
- Authoritative `ImpactStatement`
- Authoritative `GateDecision`
- Final classification of `architecture_drift / defect / corrosion`
- Final determination of `evidence sufficiency`
- `completion authority`

No method-pack skill, host prompt, or projection template may overstep by claiming to already possess these capabilities.

---

## 5. Three-Layer Collaboration Model

The currently recommended collaboration model is:

### 5.1 Method Pack

Responsible for:

- Organizing problem definition
- Organizing artifact generation
- Outputting reminders, templates, checklists, and review structures

Not responsible for:

- Final governance adjudication

### 5.2 Host Projection / Future Adapter

Responsible for:

- Collecting raw context from the host
- Extracting raw evidence such as files, commands, tests, diffs, and logs
- Mapping method-pack artifacts and host events into unified governance inputs
- Projecting runtime core outputs into host-consumable prompts or blocks

Not responsible for:

- Independently replicating a set of authoritative gate logic

### 5.3 Runtime Core

Responsible for:

- Baseline truth
- Policy snapshot
- Authoritative impact analysis
- Gate decision
- Evidence sufficiency
- Completion authority

---

## 6. Current Operating Mode

Before the runtime core is independently landed, this repository is only permitted to adopt:

> `Advisory-first, runtime-ready`

This means:

- This repository can make hosts "work more like Aegis"
- This repository can make processes more rigorous and more evidence-driven
- This repository must NOT misrepresent process discipline as system authority

---

## 7. Drift Signals

When the following phenomena appear, it indicates that the current boundary is being eroded:

- Skill text begins directly outputting `pass / block / granted` as final adjudication
- The host side claims "governance-complete" simply because tests passed or a process ended
- This repository's docs refer to draft artifacts as authoritative records
- For convenience, runtime logic is directly stuffed back into the method pack repository

---

## 8. Current Constraints

All subsequent skill modifications related to gate, impact, verification, and review must comply with:

- May produce drafts
- May produce hints
- May produce projections
- Must NOT produce overstepping authority
