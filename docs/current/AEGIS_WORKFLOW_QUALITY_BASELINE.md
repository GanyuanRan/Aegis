# Aegis Workflow Quality Baseline

Status: `Reviewed`

## 1. Document Scope

This document defines the quality baseline for high-frequency `Aegis Method
Pack` workflows.

It answers:

- how to keep common workflows useful in real tasks
- how to keep simple tasks cheap
- how to scale output depth by task risk
- how to make reusable evidence and runtime-ready artifacts appear only when
  the workflow needs them

It does not answer:

- authoritative runtime routing decisions
- host adapter implementation details
- final evidence sufficiency
- authoritative `GateDecision` or `completion authority`

---

## 2. Bottom Line

Workflow hardening must optimize for:

1. fewer false positives
2. fewer false negatives
3. less output noise
4. fresher verification evidence
5. more stable draft / hint / projection artifacts

The stable path is sample-driven hardening:

- define representative task samples first
- lock expected routing, output shape, workspace policy, and artifact policy
- only then change skill wording or workflow depth

Do not make `using-aegis` heavier in order to compensate for weak task-specific
workflow boundaries.

---

## 3. Quality Dimensions

### 3.1 Trigger Accuracy

The expected skill should trigger for representative tasks that need it.

Pass criteria:

- explicit skill requests route to the requested skill when available
- ambiguous features route to `brainstorming`
- approved requirements / specs route to `writing-plans`
- bugs, failures, and unexpected behavior route to `systematic-debugging`
- completion claims route to `verification-before-completion`
- long, resumable, or handoff-prone work routes to `long-task-continuation`

### 3.2 Fast-Path Cheapness

Simple work must remain cheap.

Pass criteria:

- simple factual Q&A does not force a full workflow
- tiny wording edits do not create project workspace records
- status, version, and install-readback questions use the smallest evidence
  path
- low-complexity tasks can proceed with concise intent, baseline check, and
  verification

### 3.3 Output Compactness

Output depth must scale with task complexity.

Pass criteria:

- low-complexity tasks use concise output
- medium tasks may use `Spec Brief`, compact plans, or evidence cards
- high-complexity architecture / contract / cross-module work uses fuller
  design, planning, and verification structures
- no workflow emits a full ceremony merely because Aegis is installed

### 3.4 User-Language Output

User-facing output should match the user's current language.

Pass criteria:

- section labels, field labels, and explanatory prose use the user's language
- commands, file paths, code identifiers, stable enum values, and product terms
  remain in English when precision requires it
- important Aegis product terms may use first-use bilingual labels, then the
  user's language in later references
- compact contracts remain machine-readable without forcing English labels into
  every user-facing response

### 3.5 Evidence Freshness

Completion claims require fresh evidence.

Pass criteria:

- completion output names the exact command or manual check
- exit status and scope are clear
- uncovered scope and residual risk are stated
- method-pack verification is not described as final authority

### 3.6 Artifact Stability

Medium/high-risk tasks should produce stable draft / hint / projection
artifacts when a process trail is needed.

Pass criteria:

- artifact names match `AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- JSON sidecars, when present, validate structurally
- work records use `docs/aegis/work/YYYY-MM-DD-<slug>/`
- proof bundles remain advisory method-pack handoff packages

### 3.7 Workspace Laziness

Project workspace records are lazy, not universal.

Pass criteria:

- global install/update/status tasks do not write target-project files
- fast-path Q&A and tiny edits do not create `docs/aegis/`
- spec, plan, medium/high debugging, long-task continuation, and reusable
  evidence trails use configured workspace support when available
- every new `docs/aegis/` file is indexed

### 3.8 Authority Boundary

Workflow quality checks stay inside the method-pack boundary.

Pass criteria:

- skills may output drafts, hints, projections, evidence, and recommendations
- skills do not grant authoritative `GateDecision`
- skills do not grant `completion authority`
- tests check wording for authority drift

---

## 4. Compact Output Contracts

### 4.1 `using-aegis`

Purpose:

- route the turn, then get out of the way

Compact contract:

```text
Route: fast-path | <skill-name> | needs-baseline-readback
ArchitectureReviewRequired: yes | no
Why: <one short reason>
Next: <smallest safe action>
```

For obvious fast-path work, the route can stay implicit in the normal answer.
Set `ArchitectureReviewRequired: yes` when a medium/high task or project rule
touches architecture, contract, cross-module data flow, canonical owner,
source-of-truth owner, context/answering/runtime flow, public user-visible
identity, evidence model, fallback, adapter, or compatibility path. Carry the
signal to `verification-before-completion`; it is a completion-time reporting
signal, not a runtime gate.

### 4.2 `brainstorming`

Purpose:

- stabilize ambiguous feature, product, UI, architecture, contract, or
  medium/high-complexity work before implementation

Compact contract:

```text
TaskIntentDraft: outcome, scope, risk hints
BaselineReadSetHint: candidate docs, missing authority
ImpactStatementDraft: affected layers, owners, invariants, non-goals
Options: 2-3 choices with trade-offs and recommendation
Decision Needed: approve brief/design, revise, or defer
```

Use a `Spec Brief` for medium tasks. Use a `Design Spec` only when ambiguity,
architecture, contract, migration, or cross-module risk requires it.

### 4.2a `goal-framing`

Purpose:

- set an explicit goal, evidence target, stop condition, and non-goals before
  routing onward

Compact contract:

```text
TaskIntentDraft: requested outcome, goal, success evidence, stop condition, non-goals
Route: fast-path | <skill-name> | needs-baseline-readback
Next: next smallest safe action
```

Goal framing is opt-in. It does not create project workspace records unless the
routed workflow needs persistent evidence, and it does not grant completion
authority.

Route matrix:

| Goal signal | Route |
| --- | --- |
| single-owner, low-risk, clear verification | fast path or `test-driven-development` |
| bug, failure, regression, unexpected behavior | `systematic-debugging` |
| ambiguous product, architecture, contract, cross-module behavior | `brainstorming` |
| approved spec, stable requirements, implementation slicing | `writing-plans` |
| multi-step, handoff, compaction-prone work | `long-task-continuation` |
| completion, release, handoff, "is this done?" | `verification-before-completion` |

### 4.3 `writing-plans`

Purpose:

- turn approved requirements, a Spec Brief, or a Design Spec into executable
  implementation slices

Compact contract:

```text
Plan Basis: approved requirement/spec refs
Files: owners and edit boundaries
Compatibility: invariants and non-goals
Tasks: bite-sized steps with verification
Risks: residual unknowns and rollback surface
Retirement: old owner/fallback handling when applicable
```

Do not redesign without cause.

### 4.4 `systematic-debugging`

Purpose:

- locate root cause before repair

Compact contract:

```text
Symptom: observed failure
Reproduction: command/input and result
Root Cause: evidence-backed owner and cause
Fix Boundary: canonical owner, compatibility, non-edits
Verification: failing test or reproduction now passing
Repair Track / Retirement Track: when fallback, owner, or contract risk exists
```

Quick bug lane is allowed for low-risk bugs, but root-cause evidence is still
required.

### 4.5 `verification-before-completion`

Purpose:

- prevent unsupported completion claims

Compact contract:

```text
Evidence Card:
- Command / Check:
- Exit Status:
- Covered:
- Not Covered:
- Residual Risk:
- Confidence: A | B | C
```

Localize completion card labels and explanatory prose to the user's language.
Keep commands, paths, code identifiers, stable enum values, and product terms in
English when needed for precision. For important product terms, first-use
bilingual labels such as `架构对齐（Architecture Alignment）` are preferred.

When project instructions require architecture reporting or completed
medium/high work touched durable architecture surfaces, include an advisory
`Architecture Alignment` result before the final completion claim:

```text
Architecture Alignment:
- Trigger: yes | no
- Scope:
- Baseline checked:
- Result: aligned | architecture drift | architecture defect
- Evidence:
- Residual architecture risk:
```

Architecture Alignment states whether the completed work matches the current
baseline or should be reported as drift/defect. It is separate from ADR
Backfill and does not grant completion authority.

For completed medium/high work that touched durable architecture surfaces,
include an advisory `ADR Backfill Check` before the final completion claim:

```text
ADR Backfill Check:
- Trigger: yes | no
- Suggested action: create | amend | supersede | skip
- Evidence source:
- Baseline sync: needed | not-needed | unknown
- Skip reason:
- Boundary: advisory method-pack signal only
```

Do not force ADR ceremony onto simple wording edits, ordinary README cleanup,
routine release-note edits, low-risk single-file changes, tests-only coverage
improvements, or bug fixes that only restore the existing baseline.

If evidence is incomplete, the claim must be downgraded.

Goal Closure:

When a task used `goal-framing`, `verification-before-completion` must compare
the final claim against the latest goal frame:

```text
Goal status: satisfied | blocked | needs-verification | scope-exceeded
Success evidence: fresh commands, files, logs, or manual verification
Stop state: done | blocked | needs-verification | scope-exceeded
Non-goals respected: yes | no | unknown
```

Goal Closure is advisory and evidence-focused. It does not grant completion
authority or decide final evidence sufficiency.

### 4.6 `long-task-continuation`

Purpose:

- preserve state across long, multi-phase, subagent, handoff, resume, or
  compaction-prone work

Compact contract:

```text
TodoCheckpointDraft: current todo, completed todos, active slice, next step
Evidence: command/file/log refs
DriftCheckDraft: scope, compatibility, retirement, decision
Risk / Unknown: blockers or missing evidence
Next: next smallest safe action
```

Low-complexity tasks skip `work/`.

---

## 5. Representative Workflow Quality Matrix

The canonical matrix lives at:

`tests/e2e/fixtures/workflow-quality-matrix.json`

Each sample records:

- `expectedPrimarySkill`
- `allowedSecondarySkills`
- `mustNotDo`
- `expectedOutputShape`
- `workspacePolicy`
- `expectedArtifacts`
- `verificationSignal`

The matrix must cover both false negatives and false positives.

---

## 6. Improvement Rule

Before broadening skill descriptions or adding new workflow steps:

1. add or update a representative sample
2. classify whether the issue is routing, execution depth, output shape,
   workspace policy, artifact stability, evidence freshness, or authority
   boundary
3. change the smallest owning surface
4. run workflow quality, trigger health, context budget, and boundary checks

If a proposed change makes simple tasks heavier without improving a
representative medium/high-risk sample, reject or revise it.

---

## 7. Boundary

Workflow quality is advisory method-pack verification.

It can show whether Aegis workflows are likely to be useful, compact, and
evidence-aware in representative tasks.

It does not grant authoritative runtime decisions, final gate decisions,
evidence sufficiency, or completion authority.
