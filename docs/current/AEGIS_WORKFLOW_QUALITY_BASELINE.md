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
6. clearer diagnostic stop points for debugging work
7. TDD strictness that scales by task risk instead of burdening every edit
8. bounded plan/spec artifacts for long tasks that execute many micro-slices

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
- direct ADR, architecture decision record, decision log, or baseline sync
  closure requests route to `recording-architecture-decisions`

### 3.2 Fast-Path Cheapness

Simple work must remain cheap.

Pass criteria:

- simple factual Q&A does not force a full workflow
- tiny wording edits do not create project workspace records
- status, version, and install-readback questions use the smallest evidence
  path
- low-complexity tasks can proceed with concise intent, baseline check, and
  verification
- TDD Route may be light or skipped for tiny low-risk work in `auto` mode

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
- commands, file paths, code identifiers, stable enum values, and exact product
  names remain unchanged
- important Aegis product terms may include the stable English identifier only
  when it prevents ambiguity, usually beside a user-language explanation on
  first use
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

### 3.9 Three-Stage Complexity Governance

Complexity governance should help agents choose safer boundaries before code is
written, then report what actually happened after the diff exists.

Pass criteria:

- plan-time checks appear in `brainstorming` and `writing-plans`
- pre-edit checks appear in implementation workflows before risky source edits
- completion keeps `Complexity Delta` and adds a useful governance suggestion
- checks stay advisory, cheap for low-risk work, and do not treat new files as
  automatically better

### 3.10 Completion-Time Complexity Delta

Non-trivial code changes should report actual complexity movement before a
completion claim.

Pass criteria:

- completion checks distinguish plan-time complexity budget from actual diff
  results
- maintained source files over 800 lines, newly crossing 800 lines, or receiving
  new logic while already oversized are reported as review signals
- touched functions, methods, components, or cohesive blocks over roughly 80
  lines, deeply nested logic, or mixed reasons to change are reported as
  block-level complexity signals
- new branches, fallbacks, adapters, guards, or compatibility paths are paired
  with retired paths or a retirement trigger
- entropy increases are either justified by owner / compatibility evidence or
  reported as residual risk
- complexity movement is paired with a governance suggestion when follow-up is
  useful

### 3.11 TDD Route Mode

TDD Mode should make test-first discipline adaptive without weakening
completion evidence.

Pass criteria:

- `auto` mode chooses a `TDD Route`: `strict`, `light`, or `skipped`
- `strict` is used for behavior, bugfix, contract, shared/core, producer /
  consumer, persistence, permission, migration, or meaningful regression risk
- `light` or `skipped` may be used for tiny low-risk edits, read-only tasks,
  docs-only changes, generated files, throwaway spikes, or environment-bound
  work where TDD does not fit
- `off` disables automatic TDD routing, but does not disable
  `verification-before-completion`
- explicit user/project TDD requests still apply in `off` mode

### 3.12 Micro-Slice Artifact Budget

Long tasks should not create a durable plan or spec for every tiny execution
slice.

Pass criteria:

- a feature or workstream defaults to one parent spec and one parent plan when
  durable artifacts are needed
- micro-slices that already fit the parent plan use the `Planless Slice Lane`
- the `Planless Slice Lane` records a compact `Slice Card` instead of adding a
  new `docs/aegis/plans/*` or `docs/aegis/specs/*` file
- `Slice Card` records the goal, parent plan/spec, touched files, boundary,
  verification, and stop condition for the current slice
- micro-slices update checkpoint, evidence, and drift state under the existing
  long-task record when persistent state is needed
- durable plan/spec creation resumes only when the slice introduces a new
  owner, contract, schema, public API, architecture boundary, persistence or
  migration surface, security/permission risk, distribution/release surface, or
  unclear verification boundary

### 3.13 Diagnostic Stop Transparency

Debugging workflows should make the diagnostic stop point visible when the
root-cause layer affects the fix boundary, contract owner, or spec/product
decision.

Pass criteria:

- `systematic-debugging` can expose a compact `Layer Stop Card`
- the card states the current stop layer, checked path, evidence for stop, and
  excluded layers
- the card includes a `Falsifier` so new evidence can correct the diagnosis
- the card includes a `User Intervention Point` so the user can challenge the
  layer, owner, or authority source early
- fast-path Q&A about debugging concepts does not emit a full layer card
- the card remains advisory method-pack output, not a `GateDecision`,
  `PolicySnapshot`, or completion authority

### 3.14 Strong-Opinion Review Lenses

High-value workflows should be opinionated enough to catch bad direction early
without turning Aegis into a roleplay system, approval board, or runtime gate.

Pass criteria:

- `brainstorming` can use a compact `Product Risk Lens` for product value,
  non-goals, trade-offs, and decision-needed clarity
- `writing-plans` can use a compact `Plan Pressure Test` for owner / contract /
  retirement risk, verification scope, and task executability
- `brainstorming` and `writing-plans` can use a compact `Architecture Integrity
  Lens` when an executable direction may still encode responsibility overlap,
  a wrong canonical owner, caller-side fallback, stale path, or missed
  higher-level owner / contract / source-of-truth simplification
- `brainstorming` and `writing-plans` can use a compact
  `Plan-Time Complexity Check` to identify target file pressure, add-in-place
  risk, and safer file boundaries before implementation
- `test-driven-development`, `systematic-debugging`, and `executing-plans` can
  use a compact `Pre-Edit Complexity Check` to avoid stuffing new logic into an
  overloaded or wrong owner
- `requesting-code-review` uses `Findings First` and prioritizes bugs first,
  risk first, tests first
- `verification-before-completion` can emit a `Readiness Summary` for tests,
  docs, version, host compatibility, uncovered scope, and residual risk
- `verification-before-completion` can emit a `Complexity Governance
  Suggestion` after `Complexity Delta`
- `recording-architecture-decisions` can use a `Retro / Memory Filter` to
  distinguish executed durable decisions from unexecuted ideas
- a role persona is not a review lens; Aegis borrows sharp evaluation angles,
  not CEO/CSO/QA persona commands
- readiness, review, retro, and plan pressure outputs remain advisory
  method-pack guidance, not merge approval, publish authorization,
  authoritative `GateDecision`, or completion authority

### 3.15 Baseline Role Alignment

Baseline checks should separate requirement truth from architecture truth without
creating heavy ceremony.

Pass criteria:

- `Product / Requirement Baseline` is the place to check the problem, accepted
  behavior, success evidence, non-goals, and user/workflow constraints
- `Architecture / Runtime Boundary Baseline` is the place to check canonical
  owner, contract, source-of-truth, dependency direction, compatibility,
  runtime-ready/method-pack boundary, and retirement state
- task-scoped input can inform a check, but durable current truth still comes
  from current authority docs, approved baseline snapshots, and ADR-backed
  state
- disagreements are reported as `Design Defect` or `Implementation Drift`
  instead of product-vs-architecture ambiguity
- every defect/drift report includes `scope: requirements | architecture | both`
- `Architecture Defect` and `Architecture Drift` remain compatibility aliases
  for architecture-scoped `Design Defect` and architecture-scoped
  `Implementation Drift`
- `Baseline Alignment` remains advisory method-pack output, not a runtime gate,
  authoritative `GateDecision`, `PolicySnapshot`, evidence sufficiency decision,
  or completion authority

### 3.16 Aegis Invocation Visibility

Aegis should be visible when it materially shapes task quality, but it must not
turn routine work into ceremony.

Pass criteria:

- non-trivial skill use starts with an `Aegis Reason Note` that explains why
  Aegis is shaping the task and what quality risk it reduces
- stage changes use a natural transition sentence when the task moves from
  diagnosis to repair, planning to implementation, implementation to
  verification, review to follow-up, or resume to drift check
- obvious tiny fast-path work can keep the trace implicit unless the user asks
  why Aegis did or did not trigger
- completion output uses a natural Aegis closeout sentence to name the boundary
  or quality risk Aegis held steady, without turning it into a self-credit
  heading
- structured trace is reserved for audit, debug, release, long-task review, or user request
- the trace stays advisory method-pack transparency, not runtime authority, not
  a runtime gate, and not completion authority

Default shape:

```text
Aegis Reason Note: <why Aegis is shaping the next step and what quality risk it reduces>
```

Completion shape:

```text
This judgment used Aegis to hold one boundary steady: <boundary / quality risk>.
```

Structured trace, only when audit/debug/release/long-task review or user request needs it:

```text
Aegis Invocation Trace:
- Trigger:
- Reason:
- Stage transition:
- Next quality gate:
- Boundary: advisory method-pack trace only
```

---

## 4. Compact Output Contracts

### 4.1 `using-aegis`

Purpose:

- route the turn, then get out of the way

Compact contract:

```text
Route: fast-path | <skill-name> | needs-baseline-readback
Aegis Reason Note: why Aegis is shaping the next step; structured trace only for audit/debug/release/long-task review or user request
ArchitectureReviewRequired: yes | no
Why: <one short reason>
Next: <smallest safe action>
```

For obvious fast-path work, the route and reason note can stay implicit in the
normal answer unless the user asks about Aegis routing or traceability.
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
Product Risk Lens: value, non-goals, trade-offs, decision-needed
Architecture Integrity Lens: invariant, owner/contract, overlap, higher-level path, retirement/falsifier, verdict
Baseline Role Alignment: Product / Requirement Baseline, Architecture / Runtime Boundary Baseline, Design Defect / Implementation Drift, scope
Plan-Time Complexity Check: target files, shape signals, owner fit, recommendation
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
Planless Slice Lane: use Slice Card when an existing parent plan/spec already owns the tiny slice
Files: owners and edit boundaries
Compatibility: invariants and non-goals
Architecture Integrity Lens: invariant, owner/contract, overlap, higher-level path, retirement/falsifier, verdict
Plan Pressure Test: owner / contract / retirement risk and verification scope
Plan-Time Complexity Check: target files, add-in-place risk, better boundary, recommendation
Tasks: bite-sized steps with verification
Risks: residual unknowns and rollback surface
Retirement: old owner/fallback handling when applicable
```

Do not redesign without cause. Do not create a new durable plan when a compact
Slice Card inside the parent workstream is enough.

### 4.4 `systematic-debugging`

Purpose:

- locate root cause before repair

Compact contract:

```text
Symptom: observed failure
Reproduction: command/input and result
Root Cause: evidence-backed owner and cause
Layer Stop Card: stop layer, checked path, evidence, excluded layers, falsifier, user intervention point, next action
Fix Boundary: canonical owner, compatibility, non-edits
Pre-Edit Complexity Check: target edit file, pressure signal, safer boundary, decision
Verification: failing test or reproduction now passing
Repair Track / Retirement Track: when fallback, owner, or contract risk exists
```

Quick bug lane is allowed for low-risk bugs, but root-cause evidence is still
required. Use `Layer Stop Card` when the diagnostic stop point is ambiguous,
crosses a boundary, reaches L5/L6/L7, or is corrected by a user-provided
falsifier. Do not use it for simple factual Q&A or tiny fast-path responses.

### 4.4a `test-driven-development`

Purpose:

- apply strict TDD only when the TDD Route calls for it

Compact contract:

```text
TDD Route: mode, decision, reason, verification
Preflight Gate: low | route-to-plan | route-to-spec
Pre-Edit Complexity Check: target edit file, pressure signal, safer boundary, decision
RED: failing test or reason strict TDD does not fit
GREEN: minimal code and passing target test
REFACTOR: cleanup with tests still green
Regression Scope: target, related, producer/consumer, manual fallback
```

In `auto` mode, strict/light/skipped route decisions scale with risk. In `off`
mode, do not automatically require TDD, but `verification-before-completion`
still requires fresh completion evidence.

### 4.5 `requesting-code-review`

Purpose:

- request advisory independent review with sharp findings and bounded authority

Compact contract:

```text
Findings First: Critical, Important, Minor findings before summary
Evidence Review: supplied evidence, unsupported claims, missing proof
Baseline / Current Authority: refs checked, drift or defect distinction
Baseline Role Alignment: requirements/product alignment, architecture/current-authority alignment, Design Defect / Implementation Drift, scope
Compatibility / Retirement: preserved behavior, old path disposition
Review Readiness: ready | with fixes | not ready, advisory only
```

Review readiness is not merge approval and does not replace
`verification-before-completion`.

### 4.6 `verification-before-completion`

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
Readiness Summary: tests, docs, version, host compatibility, residual risk
Natural Aegis closeout: one sentence naming the boundary or quality risk Aegis held steady; structured trace only for audit/debug/release/long-task review or user request
```

Localize completion card labels and explanatory prose to the user's language.
Keep commands, paths, code identifiers, stable enum values, and exact product
names unchanged. For important Aegis product terms, include the stable English
identifier only when it prevents ambiguity, usually beside a user-language
explanation on first use.

When project instructions require baseline reporting, or completed medium/high
work touched requirement, product, or architecture surfaces, include an advisory
`Baseline Alignment` result before the final completion claim:

```text
Baseline Alignment:
- Trigger: yes | no
- Product / Requirement Baseline:
- Architecture / Runtime Boundary Baseline:
- Requirement / acceptance alignment:
- Architecture / owner / contract alignment:
- Result: aligned | Design Defect | Implementation Drift | missing-authority | needs-clarification
- scope: requirements | architecture | both
- Evidence:
- Residual risk:
```

`Baseline Alignment` states whether the completed work matches the current
requirement and architecture baselines, or should be reported as Design Defect /
Implementation Drift. It is separate from ADR Backfill and does not grant
completion authority.

When project instructions specifically require architecture reporting or
completed medium/high work touched durable architecture surfaces, the
architecture-scoped subset may also be reported as `Architecture Alignment`:

```text
Architecture Alignment:
- Trigger: yes | no
- Scope:
- Baseline checked:
- Result: aligned | Design Defect | Implementation Drift | missing-authority | needs-clarification
- Evidence:
- Residual architecture risk:
```

Architecture Alignment states whether the completed work matches the current
baseline or should be reported as architecture-scoped Design Defect /
Implementation Drift. It is a compatibility alias for architecture-scoped
Baseline Alignment; older phrases such as architecture defect/drift map back to
the shared vocabulary. It remains separate from ADR Backfill and does not grant
completion authority.

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

When the suggested ADR action is create, amend, or supersede, or when baseline
sync is needed or unknown, use `recording-architecture-decisions` for the ADR
lifecycle and Baseline Sync Closure before the final completion claim.

If evidence is incomplete, the claim must be downgraded.

A `Readiness Summary` can organize release or handoff evidence, but it is not
authorization to commit, tag, publish, merge, or release.

TDD Mode `off` does not reduce this contract. Completion claims still require
fresh verification evidence.

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

For non-trivial code changes, include a compact `Complexity Delta` before the
final completion claim:

```text
Complexity Delta:
- Files over 800 lines:
- Files newly crossing 800 lines:
- Largest touched file delta:
- Largest touched function/block:
- New branches/fallbacks/adapters:
- Retired branches/fallbacks/adapters:
- Net entropy: decreased | stable | increased-with-justification
- Required follow-up:
```

When useful, add `Complexity Governance Suggestion`:

```text
Complexity Governance Suggestion:
- Recommendation: none | monitor | schedule-refactor | extract helper | split owner | open follow-up
- Why:
- Suggested scope:
- Timing:
```

For governance, compatibility, cleanup, or retirement work that adds, replaces,
or retains old logic, include `Retirement Closure`:

```text
Retirement Closure:
- Old logic located:
- Deleted:
- Retained:
- Retention reason:
- Retirement trigger:
- Lingering references checked:
```

### 4.7 `long-task-continuation`

Purpose:

- preserve state across long, multi-phase, subagent, handoff, resume, or
  compaction-prone work

Compact contract:

```text
TodoCheckpointDraft: current todo, completed todos, active slice, next step
Slice Card: goal, parent plan/spec, files, boundary, verification, stop
Evidence: command/file/log refs
DriftCheckDraft: scope, compatibility, retirement, decision
Risk / Unknown: blockers or missing evidence
Next: next smallest safe action
```

Low-complexity tasks skip `work/`. Micro-slices reuse the parent plan/spec and
update the existing long-task checkpoint/evidence trail instead of creating
per-slice plan or spec files.

### 4.8 `recording-architecture-decisions`

Purpose:

- record durable architecture decisions and close baseline sync without
  becoming a completion owner

Compact contract:

```text
Decision Candidate: summary and evidence source
ADR Gate: hard to reverse / surprising without context / real trade-off
Retro / Memory Filter: executed durable decision | unexecuted idea | process note
ADR Action: create | amend | supersede | skip
Owner Surface: project docs/adr | docs/aegis/adr | existing ADR | lighter record
Baseline Sync: required, target, action, reason
Boundary: advisory method-pack signal only; not completion authority
```

If ADR Action is create, amend, or supersede, Baseline Sync must be checked. If
the baseline is not changed, the output must state why the existing baseline
remains valid.

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
