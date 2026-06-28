# Aegis Workflow Guide

Status: `Approved`

## 1. Document Position

This guide helps users and contributors understand how `Aegis Method Pack`
triggers, routes, executes, verifies, and closes engineering tasks.

This is an explanatory guide. The authority sources remain:

1. `AGENTS.md`
2. `docs/current/README.md`
3. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
4. Task-relevant `docs/current/*.md`
5. Host install and usage docs

This guide does not add runtime authority. It does not grant `GateDecision` or
`completion authority`.

---

## 2. Aegis In One Sentence

Aegis is currently:

> `Aegis Method Pack (runtime-ready)`

Its job is to make AI coding agent work more stable, evidence-driven, and
recoverable:

- classify task type and risk before editing
- make code-change necessity visible before non-trivial source edits
- read project baselines and authority sources before acting from session memory
- split complex work into verifiable slices
- keep repair, compatibility, retirement, and verification evidence visible
- produce runtime-ready drafts, hints, and projections for a future runtime core

It does not currently own:

- final governance adjudication
- authoritative `PolicySnapshot`
- authoritative `GateDecision`
- final `completion authority`

---

## 3. Overall Flow

A standard Aegis workflow can be summarized as:

```text
startup routing
  -> task classification
  -> baseline readback
  -> problem definition
  -> investigation and approach decision
  -> plan and minimal slices
  -> TDD Route / implementation
  -> verification and regression
  -> reflection and QA closure
  -> output facts, evidence, impact scope, and residual risk
```

Not every task uses the full workflow. Simple tasks stay on the fast path;
complex tasks use the standard path.

---

## 4. Startup Routing

At the start of a task, Aegis checks whether a relevant skill should be loaded.

The typical entry point is `using-aegis`:

- it is a compact router
- it does not contain the full workflow
- it does not replace task-specific skills
- it does not absorb every trigger rule into one entry file

If the user explicitly invokes a skill, such as `aegis:systematic-debugging` or
`aegis:writing-plans`, the matching skill takes priority.

If the user starts with `/aegis-goal <task>` or `Aegis goal: <task>`, load
`goal-framing` first. It creates a thin `TaskIntentDraft` frame with goal,
success evidence, stop condition, and non-goals, then continues into the routed
workflow by default. Goal framing does not create project files by default and
does not grant completion authority. Stop at the frame only when the user
explicitly asks to only define the goal / stop condition, not execute, not
implement, not write a plan, or wait for confirmation.

Example:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Route from the goal frame by signal:

| Goal signal | Route |
| --- | --- |
| single-owner, low-risk, clear verification | fast path or TDD Route `light` / `skipped` |
| bug, failure, regression, unexpected behavior | `systematic-debugging` |
| ambiguous product, architecture, contract, cross-module behavior | `brainstorming` |
| approved spec, stable requirements, implementation slicing | `writing-plans` |
| multi-step, handoff, compaction-prone work | `long-task-continuation` |
| completion, release, handoff, "is this done?" | `verification-before-completion` |

If the task is small, such as a factual question, version check, or tiny wording
edit, the agent may continue after a compact routing check without creating
project workspace records.

---

## 5. Task Classification

Aegis chooses the execution path by complexity.

### 5.1 Fast Path

Use for:

- simple Q&A
- clear small configuration changes
- low-risk single-file edits
- tasks that do not touch contracts, architecture, cross-module behavior, or
  shared logic

Requirements:

- confirm the intent briefly
- read only the evidence needed
- act directly
- run risk-matched verification
- report the result, evidence, and remaining unknowns

### 5.2 Standard Path

Use for:

- bug diagnosis
- feature work
- refactoring
- architecture work
- performance work
- contract, schema, shared-module, or cross-module behavior changes

Requirements:

- define the problem and acceptance method first
- read relevant baseline and authority docs
- identify owner, impact scope, compatibility boundary, and non-goals
- plan minimal slices
- verify, regress, and close quality after implementation

### 5.3 High-Complexity Path

Use for:

- unclear goals or wide solution space
- possible architecture boundary changes
- multiple producers or consumers
- public API, schema, persistence, cache, export, or source-of-truth impact
- work that needs user confirmation before implementation

Requirements:

- write a Spec Brief or Design Spec first
- plan before execution
- create `docs/aegis/work/` records when needed
- do not package inferences as conclusions before user confirmation or clear
  authority sources

---

## 6. Baseline First

Before non-trivial execution, read the smallest relevant baseline.

Inside the Aegis repository, common starting points are:

- `docs/current/README.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
- task-relevant `docs/current/*.md`

In a target project, candidate baselines include:

- project `AGENTS.md`
- README
- ADRs
- `docs/current/`
- `docs/aegis/baseline/`
- architecture, contract, test, or run docs

If no usable baseline exists, Aegis performs a bounded index-first scan: file
index, README, manifests, entry points, key modules, and tests. It initializes a
project baseline only when evidence is sufficient.

---

## 7. Standard Execution Loop: DIVE

The minimum standard-path cycle is `DIVE`.

### 7.1 Define

Make the task concrete:

- what needs to be solved
- who is affected
- what the current environment is
- where the issue reproduces
- why it matters now
- how it should be approached
- how success will be accepted

### 7.2 Investigate

Find the real owner and cause:

- where the data comes from and where it goes
- who the canonical owner is
- whether compatibility boundaries are involved
- whether fallbacks, adapters, duplicate owners, or historical patches exist
- whether a local bug has escalated into architecture or contract territory

### 7.3 Validate

Confirm the judgment and implementation with evidence:

- whether evidence supports the current conclusion
- whether the change meets acceptance criteria
- whether new risk, drift, or hidden dependencies were introduced
- whether tests cover real user paths and critical boundaries

### 7.4 Evolve

Decide whether to close or continue:

- can the current task end
- should the work keep iterating
- should the problem definition escalate
- should baseline, ADR, plan, or verification strategy change

---

## 8. Reflection And QA Gate

Every standard task round uses the minimum reflection shape:

```text
Goal:
DeeperCause:
Evidence:
Risk/Unknown:
Decision:
```

QA closure is not "it seems to work." Before closing, state:

- what was verified
- which behavior the evidence covers
- which risks remain
- where the rollback boundary is
- whether old owners, fallbacks, adapters, or compatibility paths were removed
  or explicitly retained

---

## 9. Dual-Track Governance

For bug fixes, architecture refactors, contract adjustments, and governance
cleanup, Aegis uses dual-track governance by default.

### 9.1 Repair Track

Answer:

- what the true root cause is
- who the unique canonical owner is
- what the minimum necessary change is
- where the compatibility boundary is
- how verification will be performed

### 9.2 Retirement Track

Answer:

- where old logic, duplicate owners, fallbacks, or historical patches are
- whether they are still active on the main path
- whether they can be deleted in the current slice
- if not deleted, why they are retained, how they will be observed, and when
  they should retire
- how deletion or retention is verified without lingering references or damage

Default rule: when adding the repair, account for the old logic in the same
slice. Do not add new branches without explaining the old branches.

Anti-Entropy default:

- internal code retirement should prefer `delete-first`
- external compatibility retention requires active dependency evidence
- `persistent-state` or irreversible source-of-truth deletion requires
  `confirmation-first`

Mentioning destructive guardrails does not authorize destructive execution.
Without explicit scoped user confirmation, do not execute irreversible
deletion, do not emit a runnable destructive command as the next action, and do
not treat generic assent as confirmation.

---

## 10. TDD And Test Iron Law

TDD is the implementation discipline. It is not the first entry point for every
complex task.

TDD Mode has two values:

- `auto`: choose TDD Route `strict`, `light`, or `skipped` by task risk
- `off`: do not automatically require TDD; explicit TDD requests still apply

TDD Mode controls test-first discipline, not completion evidence.
`verification-before-completion` still applies in both modes.

Before implementation, confirm:

- the requirement or issue is defined
- owner and impact scope are identified
- required baselines have been read
- code change is necessary versus no-change, docs/config-only, or clarification
- the task can be split into verifiable slices

Test iron law:

- if code is wrong, fix the code
- if the test is wrong, fix the test
- do not change tests to hide business defects
- do not change business code to satisfy incorrect tests
- the final target is correct business behavior and accurate test expectations

---

## 11. Trigger Health Diagnosis

If Aegis is installed but the expected skill does not reliably trigger, do not
first stuff more keywords into a skill description.

Diagnose the trigger chain:

1. install and version visibility
2. host skill discovery
3. activation mode and bootstrap entry
4. `using-aegis` router entry
5. task-to-skill routing
6. skill execution depth
7. context pressure and re-entry
8. false positive over-triggering

Common checks:

- verify the install root and version
- verify the host can discover the current `skills/`
- verify whether the host needs restart or reload
- verify whether activation mode is `auto` or `explicit`
- explicitly invoke `aegis:using-aegis` or the target skill for comparison

See `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md` for the diagnostic layers.

---

## 12. Long Tasks And Workspace Records

Aegis supports a lazy project workspace.

Do not create `docs/aegis/` by default for:

- global install or version queries
- simple Q&A
- tiny wording edits
- low-risk fast-path tasks

Create or use `docs/aegis/` when the workflow needs:

- baseline bootstrap
- Spec Brief / Design Spec
- medium or high complexity planning
- ripple triage
- long-task continuation
- a recoverable evidence trail
- completion-time ADR backfill from durable architecture decisions

Typical structure:

```text
docs/aegis/
├── README.md
├── INDEX.md
├── BASELINE-GOVERNANCE.md
├── adr/
├── baseline/
├── specs/
├── plans/
└── work/
```

These records are method-layer evidence and handoff material, not final runtime
adjudication.

### 12.1 ADR Auto Backfill

ADR Auto Backfill runs near completion, not before execution.

When completed work changes a durable architecture surface, Aegis should check
whether to create, amend, supersede, or skip an ADR. It reads the strongest
available source:

```text
work -> plan -> spec -> git / verification evidence
```

Examples of durable architecture surfaces include owners, public contracts,
dependency direction, source-of-truth ownership, host compatibility strategy,
runtime-ready artifact boundaries, and retained or retired fallback paths.

ADR and baseline records are linked:

```text
ADR records why.
Baseline records current state.
```

When an ADR changes or confirms current architecture state, Aegis must run a
baseline sync check. If the baseline is not updated, the ADR or reflection
should state why the existing baseline still holds.

See `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`.

---

## 13. Common Skill Responsibilities

`using-aegis`
: Decide whether to enter an Aegis workflow and select the right skill.

`brainstorming`
: Clarify new features, product behavior, UI, architecture, contract, or
medium/high-complexity direction.

`writing-plans`
: Convert an existing spec or requirement into verifiable executable tasks.

`executing-plans`
: Execute a written plan and keep review checkpoints between phases.

`systematic-debugging`
: Trace bugs, test failures, or unexpected behavior from symptom to root cause.

`test-driven-development`
: Use tests to drive minimal implementation and regression coverage before
feature or bugfix code.

`first-principles-review`
: Use when direction is complex, repeated fixes are accumulating, fallbacks are
growing, owners are duplicated, or the user explicitly asks for first
principles. Before risky approach selection or task decomposition, it can
escalate to a decision hygiene review covering first-principles invariants,
owner / retirement, and falsification checks.

`requesting-code-review`
: Check behavioral risks, regressions, and missing tests after important work.

`verification-before-completion`
: Require fresh verification evidence before claiming done, fixed, passing,
release-ready, or handoff-ready. For medium/high work that touched durable
architecture surfaces, also run the ADR Auto Backfill check. When goal framing
exists, include Goal Closure: goal status, success evidence, stop state, and
whether non-goals were respected.

`long-task-continuation`
: Maintain checkpoints, resume hints, and drift checks for long, cross-session,
or handoff-prone work.

---

## 14. Final Output Shape

Aegis user-facing output should prioritize:

```text
Facts -> Inferences -> Conclusions
```

The minimum output includes:

- Facts
- Evidence
- Recommendation / Approach
- Impact Scope

Extend by task type:

- Diagnosis: reproduction, root cause, blockers
- Feature work: acceptance criteria, interface or data contract changes
- Architecture work: option comparison, trade-offs, ADR references
- Refactoring: hotspots, test safety net, complexity changes
- Performance: baseline, bottleneck, gains
- Risk and rollback: trigger conditions, rollback steps, feature flags

---

## 15. Boundary Reminder

Aegis can make a host work more like a rigorous engineering agent, but this
repository is still a `Method Pack`.

Aegis can currently produce:

- `TaskIntentDraft`
- `BaselineReadSetHint`
- `BaselineUsageDraft`
- `ImpactStatementDraft`
- `EvidenceBundleDraft`
- `GateInputPack`
- `SubagentContextPacket`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

These are drafts, hints, or projection inputs. They can help a future runtime
core make decisions, but they must not be written as final authority already
owned by this repository.
