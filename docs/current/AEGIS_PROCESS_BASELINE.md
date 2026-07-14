# Aegis Process Baseline

Status: `Approved`

## 1. Document Scope

This document defines the current process baseline for the `Aegis Method Pack`.

This document answers:

- What execution framework the `Aegis` method layer adopts
- How standard tasks and fast-path tasks are handled
- How evidence, reflection, quality assurance, and output contracts converge
- Which skills these rules should project into

This document does NOT answer:

- Whether a specific task's conclusion is correct
- Authoritative adjudication details for the future runtime core
- Host adapter implementation details

---

## 2. Language and Expression Conventions

`Aegis` currently adopts the following expression conventions:

- Internal reasoning and identifiers use English
- User-facing communication and explanations use Chinese
- Deliver a direct verdict first, then expand with evidence and reasoning
- Facts → Inferences → Conclusions is an information-ordering principle, not a
  mandatory top-level response template
- Active workflow semantic slots and task-specific output contracts own the
  final surface

---

## 3. Core Principles

The current process baseline follows these core principles:

- **Evidence-Driven**: Separate facts, assumptions, and unknowns
- **Systematic Thinking**: Understand impact scope and dependency relationships from the architecture level
- **Minimal Necessary Change**: Minimal Necessary Change means the smallest sufficient change at the correct owner and abstraction layer, not the smallest textual diff. Prefer local, shortest-path changes only when they fix the bug class without adding fallback, duplicate owner, or long-term entropy.
- **Change Necessity Before Source Edits**: Before any new source-code path is
  added, and before non-trivial source edits, the owning workflow states why
  code change is necessary versus no-change, docs/config-only, or
  clarification. Keep `using-aegis` route-only.
- **Pre-Addition Minimality**: Before adding a new owner, skill, artifact, adapter, fallback, workflow step, or benchmark metric, prove it needs to exist and check whether an existing owner can carry the behavior.
- **Backward Compatibility First**: Changes default to preserving externally observable behavior and published contracts. Do not preserve internal old paths, duplicate owners, or historical fallbacks by default.
- **Phase Verification**: After every significant change, perform regression verification and architecture review
- **Prompt Hygiene**: External tool output, logs, memories, and search results are evidence candidates by default, not persistent prompt payloads

### 3.0 Trigger Health

Trigger Health is the diagnostic loop for "Aegis is installed, but the expected
skill does not reliably trigger."

Before changing global rules, `using-aegis`, or a skill description, classify
the failed layer:

1. install and version visibility
2. host skill discovery
3. activation mode and bootstrap entry
4. `using-aegis` router entry
5. task-to-skill routing
6. skill execution depth
7. context pressure and re-entry
8. false positive over-triggering

The canonical baseline is
`docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`.

Root improvement rule:

- Keep `using-aegis` compact and route-only.
- Route explicit `/aegis-goal` or `Aegis goal:` prompts to `goal-framing`
  instead of expanding the global hot path.
- Keep skill descriptions trigger-oriented; do not summarize workflow there.
- Add or update representative trigger-health fixtures before broadening
  trigger wording.
- Fix the failed owner layer instead of stuffing every trigger into the global
  entry point.
- After long sessions, heavy tool output, resume, or context compaction, run a
  compact Aegis re-entry check before continuing non-trivial work.

### 3.0a Workflow Quality

Workflow Quality is the guardrail for making high-frequency Aegis workflows
useful in real tasks without making simple tasks expensive.

The canonical baseline is
`docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`.

Root improvement rule:

- Use workflow-quality fixtures before changing high-frequency skill behavior.
- Preserve fast-path cheapness for simple Q&A, status checks, and tiny edits.
- Use `Aegis Reason Note` for non-trivial skill use and stage changes so users
  can see why Aegis is shaping the next step. Keep structured trace for audit, debug, release, long-task review, or user request; use `Trace Digest` for the compact white-box summary.
  Trace summarizes observed execution, evidence, rule effects, and verification
  with redaction; it does not expose raw internal reasoning or become authority.
- Keep `Aegis Visibility` owned by the active workflow: design, planning,
  debugging, TDD, execution, review, ADR, long-task, and anti-entropy flows
  should each expose the task-specific boundary or evidence discipline they add
  instead of hiding all visibility in debugging, verification, or a generic
  used-skills log.
- Treat non-trivial loaded-skill visibility as non-omittable: the first
  substantive stage gets one natural visibility sentence, and the final
  response uses a compact `Aegis Impact and Safety Receipt` by default.
  A single closeout sentence is only the minimum fallback for obvious low-risk
  work. Concision and natural-surface wording do not authorize dropping the
  safety fields.
- Scale output depth by task complexity and risk.
- Prefer compact output contracts over broad template expansion.
- Apply the Micro-Slice Artifact Budget when long tasks split into many tiny
  slices: reuse the parent spec/plan, use a compact Slice Card, and avoid
  per-slice plan/spec files unless a new durable boundary appears.
- Use an `Execution Readiness View` for medium/high, subagent, handoff-prone,
  or long-running execution handoffs when a compact plan-to-execution readback
  would reduce drift. Render it from existing runtime-ready drafts such as
  `TaskIntentDraft`, `BaselineUsageDraft`, `ImpactStatementDraft`,
  `GateInputPack`, `DriftCheckDraft`, and expected evidence refs; do not create
  a new authoritative artifact owner.
- Keep runtime-ready artifacts as drafts, hints, projections, and evidence
  bundles only.

### 3.0b Three-Stage Complexity Governance

Aegis uses advisory three-stage complexity governance to catch entropy growth
before planning, before editing, and before completion.

`docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md` is the canonical current
owner for artifact classes, pressure signals, budget/closure shapes, and the
rule that unresolved complexity overrun blocks an Aegis completion claim.

This process baseline keeps the workflow-stage responsibilities:

1. **Plan-Time Complexity Check**: `brainstorming` and `writing-plans` inspect
   likely owner files and artifacts, estimate post-change pressure, and choose
   edit-in-place, extract helper, add owner file, split task, defer refactor,
   or revise the plan before code is written.
2. **Pre-Edit Complexity Check + Owner-Fit Decision**:
   `test-driven-development`, `systematic-debugging`, and `executing-plans`
   re-check the actual edit file or artifact, classify edit intent when the
   target owner is over-budget or mixed-purpose, and pause for a plan update if
   the safest boundary differs from the plan.
3. **Complexity Delta + Complexity Governance Suggestion +
   Complexity Closure**: `verification-before-completion` compares the final
   diff against the planned budget, reports actual entropy movement, and states
   whether the slice is `within-budget`, `exceeded-and-governed`, or
   `exceeded-unresolved`.

Complexity Delta remains the post-change guardrail for detecting entropy growth
before a task is claimed complete. It complements plan-time complexity
budgeting: plans may predict the intended file and responsibility shape, but
completion-time review must compare the actual diff against the final code or
artifact shape.

### 3.0c TDD Mode

TDD Mode controls test-first discipline, not completion evidence. The default
mode is `off`.

The two supported values are:

- `off`: Aegis does not automatically require
  `test-driven-development`, select `TDD Route: strict`, or force a failing
  test first. A plan or execution review may record `Mode: off / Decision:
  skipped`; that record is not an automatic TDD route. Explicit user/project
  strict requests still apply; diagnostic reproduction, proportional
  regression, and `verification-before-completion` remain required as fit the
  work.
- `auto`: Aegis chooses a `TDD Route` before implementation. The route is
  `strict` for risky behavior work, `light` for tiny low-risk edits, and
  `skipped` when TDD does not fit the task shape.

Only recorded `strict` makes a failing test a production-edit gate. A failing
diagnostic reproduction and a post-change regression remain evidence forms,
not implicit RED/GREEN authorization. Plan approval never supplies strict
authority.

TDD Mode is method-pack guidance only. It does not grant runtime authority,
final completion authority, or permission to skip verification.

### 3.0d Strong-Opinion Review Lenses

Strong-Opinion Review Lenses are compact task-specific checks that make Aegis
more decisive without turning the method pack into a roleplay system or runtime
approval layer.

Canonical lenses:

- `Product Risk Lens` in `brainstorming`: value, non-goals, trade-offs,
  decision-needed, and whether the idea deserves implementation
- `Plan Pressure Test` in `writing-plans`: owner / contract / retirement risk,
  verification scope, and task executability
- `Execution Readiness View` in `writing-plans` and execution workflows:
  advisory plan-to-execution handoff with intent lock, scope fence, baseline
  lock, compatibility boundary, retirement boundary, task batches, test
  obligations, review gates, drift / rewind rules, and evidence required before
  completion
- `Architecture Integrity Lens` in `first-principles-review`, composed by
  `brainstorming` and `writing-plans`: invariant, canonical owner / contract,
  responsibility overlap, higher-level simplification, retirement / falsifier,
  and verdict before a risky approach or plan decomposition is endorsed
- `Existence Check` in `brainstorming` and `writing-plans`, and in
  `systematic-debugging` when a candidate repair would add a fallback, adapter,
  branch, or new owner: proposed new surface, existing owner / reuse candidate,
  creation proof, entropy / retirement impact, and reuse-or-add decision before
  adding new owners, artifacts, adapters, fallbacks, workflow steps, or
  benchmark metrics
- `Change Necessity` in `writing-plans`, `systematic-debugging`,
  `test-driven-development`, and `executing-plans`: user-visible need,
  no-change / non-code option, why code change is necessary, minimum change
  boundary, and decision before any new source-code path or non-trivial source
  edit
- `Plan-Time Complexity Check` in `brainstorming` and `writing-plans`: target
  file pressure, owner fit, and better boundary options before implementation
- `Pre-Edit Complexity Check` in implementation workflows: actual edit-file
  pressure, edit intent, owner fit, and whether to pause for a plan update
  before source edits
- `Findings First` in `requesting-code-review`: bugs first, risk first, tests
  first, with findings before summary
- `Readiness Summary` in `verification-before-completion`: tests, docs,
  version, host compatibility, uncovered scope, and residual risk
- `Aegis Impact and Safety Receipt` in `verification-before-completion`: the
  unified user-facing completion surface for non-trivial Aegis-shaped work,
  consolidating key judgment, avoided misfix, boundary held, baseline
  alignment, complexity control, evidence strength, uncovered risk, next
  verification, and optional Aegis path
- `Complexity Governance Suggestion` in `verification-before-completion`:
  none, monitor, schedule-refactor, extract helper, split owner, or open
  follow-up based on the actual diff
- `Retro / Memory Filter` in `recording-architecture-decisions`: executed
  durable decisions may become ADR/baseline memory; unexecuted ideas stay out of
  accepted architecture memory

These lenses are review structures, not persona commands. They do not grant
merge approval, publish authorization, authoritative `GateDecision`, or
completion authority.

### 3.0e Baseline Role Alignment

Aegis baseline checks must keep two roles separate:

- `Product / Requirement Baseline`: the confirmed requirement source of truth
  for target state, goals and scope, users and scenarios, requirement items,
  acceptance / verification criteria, non-goals, workflow constraints, open
  questions, and approved requirement or spec intent.
- `Architecture / Runtime Boundary Baseline`: canonical owners, contracts,
  source-of-truth boundaries, runtime-ready/method-pack boundary, dependency
  direction, compatibility surfaces, and retirement expectations.

When a project needs an explicit requirements model, the minimum sufficient
shape is:

```text
Requirements Baseline
- requirement sources
- goals and scope
- users and usage / system scenarios
- requirement items:
  - functional
  - quality
  - constraint
  - delivery-transition
- acceptance and verification criteria
- open questions
- change and alignment records
- requirement ready check
```

Business / mission requirements belong inside goals and scope. They are not the
name or full boundary of the baseline. A project may expose this as
`Requirements Baseline` or `Product / Requirement Baseline`; new method-layer
docs should not introduce a separate top-level `Business Requirements Baseline`
owner.

Use a lightweight `Requirement Ready Check` before design, planning, execution,
or acceptance judgment depends on a requirement being complete:

```text
Requirement Ready Check:
- Requirement source refs:
- Goals and scope refs:
- User / scenario refs:
- Requirement item refs:
- Acceptance / verification criteria refs:
- Open blocker questions:
- Decision: ready | needs-source | needs-goal-alignment | needs-scenario | needs-acceptance-criteria | needs-clarification | needs-user-decision | blocked
```

`ready` means the requirement is ready for the next method-layer step. It does
not mean the requirement is implemented, verified, accepted, or granted
completion authority.

Task-scoped input can inform a baseline check, but it is not automatically
durable authority. Snapshots are evidence of current state. ADRs record why a
durable decision changed. Current authority docs and approved baselines record
what is true now.

Use one shared defect/drift vocabulary across both roles:

```text
Baseline Role Alignment:
- Product / Requirement Baseline:
- Architecture / Runtime Boundary Baseline:
- Result: aligned | Design Defect | Implementation Drift | missing-authority | needs-clarification
- scope: requirements | architecture | both
- Evidence:
- Next action:
```

- `Design Defect`: a confirmed error, gap, contradiction, or wrong abstraction in
  the relevant requirement/design/baseline itself.
- `Implementation Drift`: implementation, plan, review, or documentation has
  deviated from a confirmed, correct, and unchanged requirement or architecture
  baseline.
- `Architecture Defect` remains a compatibility alias for an
  architecture-scoped `Design Defect`.
- `Architecture Drift` remains a compatibility alias for an
  architecture-scoped `Implementation Drift`.

This alignment is advisory method-pack discipline. It does not create a runtime
gate, authoritative `GateDecision`, authoritative `PolicySnapshot`, evidence
sufficiency decision, or completion authority.

### 3.0f Minimal Sufficient Stable Repair

Minimum is measured by long-term system entropy, not changed line count. When a
candidate repair adds a caller-side guard, fallback, adapter, compatibility
branch, special case, duplicate owner, or sample-only exception, run:

```text
Minimality Check:
- Smallest textual diff:
- Correct owner:
- Bug class fixed:
- New branch/fallback added:
- Old path retired or scheduled:
- Verdict: sufficient repair | local patch | needs first-principles review
```

Local patches are acceptable only as bounded mitigations with a retention
reason, retirement trigger, and residual risk. Do not call them sufficient
repairs.

Anti-Entropy default: for internal code retirement, prefer `delete-first`. For
`persistent-state` or irreversible source-of-truth objects, prefer
`confirmation-first`. Mentioning a destructive guard never authorizes
execution; without explicit scoped user confirmation, no destructive command or
tool call may run.

### 3.0g Pre-Addition Minimality

Pre-Addition Minimality extends anti-entropy upstream. It asks whether a new
surface should exist before the method pack creates it.

Run an `Existence Check` before design or planning endorses a new owner, skill,
artifact, host adapter, fallback, compatibility path, workflow step, or
benchmark metric. In debugging, run the same check before accepting a repair
shape that would add a fallback, adapter, branch, or new owner; a user asking
for a fallback is not proof that the fallback should exist.

```text
Existence Check:
- Proposed new surface:
- Existing owner / reuse candidate:
- Why existing surface is insufficient:
- Creation proof:
- Entropy / retirement impact:
- Decision: reuse-existing | add-with-proof | defer | reject | needs-first-principles-review
```

If the decision is `reuse-existing`, change the existing owner instead of
adding a new surface. If the decision is `add-with-proof`, carry the proof,
verification signal, and any retirement trigger into the plan, spec, or
completion evidence. If the decision remains disputed or introduces duplicate
ownership, route to `first-principles-review` or `anti-entropy-governance`
instead of adding another fallback.

The canonical reference is
`docs/current/AEGIS_MINIMALITY_REFERENCE.md`.

### 3.0h Micro-Slice Artifact Budget

Micro-Slice Artifact Budget keeps long-task continuity from becoming artifact
noise. A feature or workstream should normally have one parent spec and one
parent plan when durable planning artifacts are needed. Tiny execution slices
that do not change the durable boundary should use the Planless Slice Lane:
record a Slice Card, update checkpoint/evidence/drift state, and continue from
the parent plan.

This is also artifact complexity governance: excessive plan, spec, or work-log
fan-out is itself a complexity regression even when no source file grew.

Escalate back to a durable spec or plan only when the slice introduces a new
owner, contract, schema, public API, architecture boundary, migration,
persistence, security/permission concern, distribution/release surface, or an
unclear verification boundary.

### 3.0i Change Necessity Before Source Edits

Change Necessity makes the "should we edit code at all?" judgment visible
before a workflow adds a new source-code path or makes a non-trivial source
edit. It is a semantic slot for the owning workflow, not a new artifact, not a
new skill, and not a heavier `using-aegis` hot path.

The trigger is behavioral, not prompt-word based: if the workflow is about to
endorse any new source-code path or a non-trivial source edit, the owning
workflow must expose the code-change necessity even when the user did not ask
for a "Change Necessity" section. A new helper, small guard, new branch,
fallback, adapter, or owner is not exempt just because it looks tiny. A natural
sentence is enough for a tiny new path when it remains auditable, for example:

```text
Code necessity check: a non-code path is insufficient because <reason>; the
minimum change boundary is <owner/files>, so the decision is code-change.
```

Use this compact shape when a plan, bug repair, strict TDD slice, or plan
execution is about to endorse any new source-code path or non-trivial source
edit:

```text
Change Necessity:
- User-visible need:
- No-change / non-code option:
- Why code change is necessary:
- Minimum change boundary:
- Decision: no-change | docs/config-only | code-change | needs-clarification
```

If the decision is `no-change`, do not write source code. If the decision is
`docs/config-only`, route the work to that narrower change and verify it. If
the decision is `needs-clarification`, pause before implementation. If the
decision is `code-change`, carry the minimum boundary into `Files`,
`Fix Boundary`, `TDD Route`, or the relevant implementation task.

Tiny fast-path edits may satisfy this in natural prose. Medium/high work should
make the slot explicit before task decomposition, repair, or strict RED/GREEN.
The slot stays advisory method-pack discipline; it does not grant runtime
authority, authoritative `GateDecision`, or completion authority.

### 3.1 Ripple Signal Triage

Ripple Signal Triage is the pre-change entry point for dependency-aware work.

Before implementation, check whether the requested change touches any ripple
signal:

- shared module, core logic, or cross-module behavior
- public API, schema, data contract, or compatibility boundary
- persistence, cache, export/copy/readback path, or source-of-truth candidate
- fallback, adapter, duplicate owner, legacy path, or retirement boundary
- producer and consumer both implicated by the same change
- bug fix proposed at a consumer/caller instead of the canonical owner
- candidate fix adds keyword, phrase, regex, negation-word list,
  sample-text exception, local guard, one-off branch, fallback, adapter,
  compatibility branch, prompt branch, or legacy path expansion
- downstream logic re-parses raw text or re-infers action/state while typed
  intent, normalized state, contract, or another source-of-truth already exists
- artifact, download, export, readback, or cache behavior is patched without
  first locating the producer and source-of-truth owner

If no signal is hit, continue through the normal workflow without extra output.

If any signal is hit, perform the smallest sufficient triage before code
changes:

1. Identify the canonical owner and affected downstream consumers
2. State whether any source-of-truth, contract, fallback, or retirement risk exists
3. Expand verification scope when producer/consumer, contract, shared module, or
   real user paths are affected
4. If the candidate fix shape itself is the signal, record
   `PatchShape`, `CanonicalOwner`, `UpwardDrillSignal`, and `Decision`
   before editing
5. Record the result as a short note or in `ImpactStatementDraft` when the task is
   medium/high complexity

A locally green verification does not erase triage state. When a checkpoint
already exists, retain `PatchShape`, `CanonicalOwner`, `UpwardDrillSignal`, the
decision, latest outcome, and a bounded evidence ref. Before an unplanned
repair, read that state and compare invariant, owner/contract seam, patch shape,
and causal topology; a new carrier name alone does not prove a new direction.
This reuses existing checkpoint/evidence surfaces and adds no schema owner.

If the triage requires changing the canonical owner, changing a public contract,
making a cache/export/copy into a source of truth, retaining two owners, or
adding a fallback/adapter/compatibility branch, pause for design or explicit
alignment before implementation.

`Cascade proliferation` in the Architecture Review remains the post-change
review of whether the implemented change introduced unexpected ripple scope.

---

## 4. Prompt Hygiene and Evidence Injection Boundary

The current process baseline uses `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md` as the canonical owner for prompt hygiene.

Minimum rules:

- External tool output, logs, memories, and search results default to summary-first, with raw excerpts cited on demand.
- Large raw output is isolated at its source by default; only source, scope, summary, refs, and unknowns enter the prompt.
- When a summary is insufficient, read back the smallest raw excerpt or run fresh verification — do not lower the judgment standard.
- When information is still insufficient, the conclusion MUST be downgraded to `unknown`, `partial`, or `needs-verification`.
- Reducing persistent context must not weaken baseline-first, evidence-before-claims, impact review, root-cause-first debugging, or verification-before-completion.

---

## 5. Todo Recitation Loop

For standard-path tasks, the todo recitation loop MUST be explicitly executed:

1. Create or update the todo list when the task begins
2. List complete steps
3. Re-read the todo list before every phase transition
4. Write back current state and next step

The goal of the todo recitation loop is not formal checkmarking — it is to prevent scope drift during analysis, execution, or verification phases.

---

## 6. TLREF: Path Selection

`Aegis` currently adopts the path-selection layer of the three-layer reflective execution framework:

### 6.1 Fast Path

Applicable tasks:

- Knowledge Q&A
- Configuration adjustments
- Dependency upgrades
- Other low-risk, clearly bounded problems not requiring deep governance

Execution requirements:

- Execute directly
- Verify results
- Must retain factual evidence

### 6.2 Standard Path

Applicable tasks:

- Diagnosis
- Feature work
- Architecture work
- Refactoring
- Performance work

Execution requirements:

- Problem definition
- Analysis and decision-making
- Execution and verification
- Quality assurance

The todo recitation loop must run throughout the standard path.

---

## 7. DIVE: Standard Path Minimum Cycle

For standard-path tasks, the current minimum execution cycle is:

- `Define`
- `Investigate`
- `Validate`
- `Evolve`

### 7.1 Define

Must cover at minimum:

- `What / Who / When / Where / Why / How / How much`
- Current environment and reproducible baseline
- Success criteria and acceptance method

### 7.2 Investigate

Must cover at minimum:

- Data flow and owner
- Compatibility boundary
- Whether special cases are business-required or historical patches
- Whether the local issue has escalated to the architecture level

### 7.3 Validate

Must cover at minimum:

- Whether evidence supports the current judgment
- Whether acceptance criteria are met after implementation
- Whether new risks, drift, or hidden gaps have been introduced

### 7.4 Evolve

Must cover at minimum:

- Whether the current conclusion should exit, continue iterating, or escalate the problem definition
- Whether baseline, ADR, review, or verification strategy needs revision
- Whether completed work should backfill, amend, supersede, or skip an ADR
  based on `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`

---

## 8. Reflection Checklist

For standard-path tasks, every round MUST complete the minimum reflection:

- `Goal`
- `DeeperCause`
- `Evidence`
- `Risk/Unknown`
- `Decision`

Where:

- If `DeeperCause` cannot be clearly answered as "no", do not exit directly
- If `Evidence` cannot support the current judgment, do not package inferences as conclusions
- If there remain issues not yet drilled upward to indivisible root causes, do not treat the diagnostic task as complete
- Diagnosis must drill upward layer by layer from symptoms (L1 Symptom → L2 Logic → L3 System → L4 Architecture → L5 Cross-system Contract → L6 Platform/Framework Constraint → L7 Spec Gap); the chain's endpoint is "the root cause that cannot be further decomposed", not a fixed layer
- Candidate fixes that add keyword, phrase, regex, negation-word lists, local
  guards, one-off branches, fallbacks, adapters, compatibility branches,
  prompt branches, legacy path expansion, consumer-side patches, or downstream
  re-parsing while a typed contract/source-of-truth exists are hard signals to
  continue upward drilling before implementation
- A minimal fix must be a minimal sufficient stable repair: correct owner,
  bug class fixed, and no unbounded fallback/branch growth. If only a local
  patch is possible, record retention reason and retirement trigger.
- Watch for compound root causes: when symptoms persist after a fix, perform differential diagnosis to distinguish "incomplete fix", "compound root cause", and "chain-causal failure" before deciding the next action
- Watch for terminal unactionable root causes: when the required change exceeds system boundaries (T-class hard signals), record the root cause and boundary, then choose a mitigation/fallback/escalation strategy — do not package a local patch as root-cause repair

---

## 9. Quality Assurance

For standard-path tasks, after exiting the reflection loop, enter quality assurance:

- `Remove/Restore`
- Complexity Delta
- Rollback preparation
- Confidence assessment
- Asset capture

Minimum principle:

- Do not end at "the feature seems to work"
- Must state side effects, residual risks, and rollback boundaries
- For non-trivial code changes, must state whether the actual diff decreased,
  preserved, or increased complexity before claiming completion

---

## 10. Test Failure Iron Law

The current process baseline explicitly rejects the following behaviors:

- Modifying tests to cover up business code defects
- Modifying business code to accommodate incorrect tests
- Bidirectional accommodation without first locating the error source

The enforced principle is:

- Code is wrong → fix the code
- Test is wrong → fix the test
- Final guarantee: business behavior is genuinely correct AND test expectations are accurately aligned

---

## 11. Final Output Semantic Slots / Attention Anchors

`Aegis` final output uses semantic slots and attention anchors, not fixed global
headings. These anchors keep evidence, impact, and recommendation visible while
preserving active workflow-owned output contracts.

Default anchors, satisfied by natural prose or by the active workflow's own
fields, are:

- `Facts` / evidence-backed observations
- `Evidence`
- `Recommendation/Approach`
- `Impact Scope`

Extended by task type:

- Diagnosis: reproduction steps, root cause, blocking points
- Feature work: acceptance criteria, interface or data contract changes
- Architecture work: option comparison, trade-offs, ADR references
- Refactoring: hotspots, test safety net, complexity changes
- Performance: baseline, bottleneck, gains
- Risk and rollback: trigger conditions, rollback steps, feature flags

These anchors must not override task-specific structures such as findings-first
code review, verification evidence slots, the unified Aegis Impact and Safety
Receipt, repair/retirement closure, complexity closure, Aegis Visibility,
Execution Readiness View, or requested Trace Digest. When final-output anchors
and completion governance both apply, render the user-facing completion through
the unified receipt and expand individual cards only when risk, release, audit,
or user request requires it.

---

## 12. Project Workspace, Baseline Bootstrap, and Complexity Routing

### 12.1 Project Baseline Bootstrap

Project Baseline Bootstrap is the first active-project guardrail.

When the user is inside a codebase and asks a project-related question or asks
what to do next, Aegis should check whether a project baseline already exists
before giving code-changing advice. Existing project authority docs, ADRs,
README, local agent rules, and `docs/aegis/baseline/` all count as candidate
baseline sources.

If no usable baseline is found, do a bounded repo scan using an index-first
flow:

1. identify project root and git state
2. list files with `rg --files` or equivalent
3. ignore generated, dependency, build, vendor, and output directories
4. read README, manifests, config, entry points, key `src` files, and tests
5. infer stack, module owners, contracts, dependency direction, run/test commands,
   and compatibility boundaries

If there is sufficient project content, create the first baseline snapshot
under `docs/aegis/baseline/` and continue answering the user's original
question. If content is too sparse, do not generate an empty baseline; tell the
user that the baseline was skipped because sufficient project content is not
available, then still answer the original question from the evidence that
exists.

### 12.2 Lazy Workspace Support

Aegis Project Workspace hard binary rule:

- **Global install** (plugin registration, version query, skill listing,
  updating Aegis itself): NEVER write target-project files.
- **Fast path** (normal Q&A, simple explanation, version status, git status,
  tiny wording/format edits, and low-risk single-file changes): do not create
  `docs/aegis/` unless a workflow explicitly needs a reusable project record.
- **Active project record needed**: initialize or use `docs/aegis/` only when
  baseline bootstrap, spec writing, plan writing, medium/high debugging, ripple
  triage, long-task continuation, or work evidence requires persistent files.

Use configured Aegis workspace support when it is available. The current
repository ships zero-dependency scripts for workspace initialization,
lifecycle records, proof-bundle assembly, and structural checks, but these are
method-pack support tools. They validate structure and index coverage only;
they do not decide evidence sufficiency and do not grant completion authority.
Resolve the helper from the installed method-pack support path, then pass the
target project separately, for example
`python <aegis-workspace-helper> check --root <target-project-root>`.

The Aegis method-pack repository itself must not ship a precreated live
`docs/aegis/` workspace. That directory belongs to the concrete target project
where Aegis records are being written.

### 12.3 Workspace Shell and Task Work Record

Workspace Shell is the lightweight project-local container:

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

Task Work Record is created only for medium/high or long-running work:

```text
docs/aegis/work/YYYY-MM-DD-<slug>/
├── 10-intent.md
├── 20-checkpoint.md
├── 90-evidence.md
├── 99-reflection.md
├── *-draft.json / *-hint.json / gate-input-pack.json
└── proof-bundle.md
```

Every new file under `docs/aegis/` must be indexed in `INDEX.md`.

### 12.4 Spec Brief and Design Spec

Use the smallest spec artifact that stabilizes the task:

- **Spec Brief** (`docs/aegis/specs/YYYY-MM-DD-<topic>-brief.md`): medium tasks
  where what/why/acceptance needs to be pinned before planning, but no formal
  architecture design is needed.
- **Design Spec** (`docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`): high
  complexity, architecture, contract, migration, cross-module, or ambiguous
  product behavior that needs user review before planning.

Both are advisory method-pack artifacts. Existing project docs and ADRs remain
the preferred authority when they already own the truth.

### 12.5 Complexity Routing

- **Low complexity**: concise intent + baseline check → TDD Route +
  verification, no `work/` created
- **Medium complexity**: baseline read-set + Spec Brief or requirements + plan
  + atomic tasks → TDD Route + verification; create `work/` only when a process
  trail is needed
- **High complexity**: Design Spec + plan + user confirmation → TDD Route +
  verification, `work/` created

Mid-stream complexity escalation: pause implementation, initialize workspace if
missing, backfill required artifacts, then continue.

TDD is the implementation discipline, not the first entry point for medium- or
high-complexity tasks. The default `off` mode disables automatic TDD while
keeping completion verification mandatory. In `auto` mode, TDD Route decides
strict, light, or skipped by task risk.

### 12.6 Workspace Integrity Checks

When configured Aegis workspace support is available, workflows that write
`docs/aegis/` should use the shared support path for:

- appending `INDEX.md`
- creating task work records
- adding checkpoints, evidence, and drift checks
- assembling proof bundles
- checking workspace structure before pause, handoff, or completion candidate

The generated proof bundle is a structural review/handoff package. It is not a
final evidence-sufficiency decision, not an authoritative `GateDecision`, and
not completion authority.

### 12.7 ADR Auto Backfill

ADR Auto Backfill is the completion-time workflow for turning completed
engineering work into architecture memory.

It uses the strongest available source in this order:

1. `docs/aegis/work/YYYY-MM-DD-<slug>/`
2. `docs/aegis/plans/YYYY-MM-DD-<topic>.md`
3. `docs/aegis/specs/YYYY-MM-DD-<topic>-brief.md` or
   `docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`
4. git diff, commits, verification output, release notes, and current docs

The workflow may create, amend, supersede, or skip an ADR. It must not promote
speculative, unexecuted plans into durable architecture memory.

If an ADR action changes or confirms ownership, contract inventory, dependency
direction, source-of-truth ownership, compatibility boundary, host support
status, runtime-ready artifact boundary, or retirement schedule, a baseline sync
check is mandatory.

Canonical rule:

```text
ADR records why.
Baseline records current state.
```

Detailed trigger and sync rules live in
`docs/current/AEGIS_ADR_AUTO_BACKFILL.md`.

---

## 13. Projection Targets for Existing Skills

This process baseline should be projected into the following skills as a priority:

- `brainstorming`
  - Own design/spec clarification for new, ambiguous, architecture, contract,
    cross-module, or medium/high-complexity work; do not force low-complexity
    fast-path work through full design ceremony
- `first-principles-review`
  - Provide a lightweight compositional review for first-principles, Occam,
    ambiguous direction, repeated fixes, fallback growth, duplicate owners, or
    architecture/product direction risk; own the decision hygiene escalation for
    invariants, owner / retirement, and falsification checks before risky specs
    or plans are endorsed; own the narrower `Architecture Integrity Lens` for
    responsibility overlap, higher-level owner / contract simplification,
    caller-side fallback, stale path, and retirement / falsifier checks; do not
    add it to the always-loaded hot path
- `using-aegis`
  - Add complexity routing, project workspace creation boundary, prompt hygiene
    hot path, and light delegation to owner workflows for Change Necessity
- `systematic-debugging`
  - Explicitly cover the "Symptom → Logic → System → Architecture" diagnostic
    layers and surface Change Necessity before repair code
- `writing-plans`
  - Introduce impact, compat, retirement, Change Necessity, and verification
    perspectives
- `test-driven-development`
  - Position TDD as the implementation discipline for approved atomic tasks,
    preventing medium/high-complexity tasks from bypassing planning, and confirm
    code-change necessity before strict RED/GREEN enters production edits
- `requesting-code-review`
  - Add evidence sufficiency, requirements/product alignment, Design Defect /
    Implementation Drift checks, and missing ADR / baseline sync findings for
    durable architecture decisions
- `verification-before-completion`
  - Align with reflection, QA, final output semantic slots, and ADR Auto Backfill for
    completed medium/high work that touched architecture surfaces

---

## 14. Current Constraints

All subsequent skill modifications must satisfy:

- Rules must be triggerable and executable, not philosophical prose
- Process constraints should fall into specific workflows, not remain as abstract slogans
- The method pack can organize reasoning and artifacts, but must not overstep into claiming authoritative completion

---

## 15. Architecture Review — 7-Dimension Operational Definition

After every non-trivial change, perform the following 7-dimension check. The
`Cascade proliferation` dimension is a post-change review companion to the
pre-change Ripple Signal Triage in §3.1.

| # | Dimension | Check Question | Pass Criterion |
|---|-----------|---------------|----------------|
| 1 | Ownership integrity | Does every component have exactly one canonical owner? Any new duplicate owners? | No new duplicate owners |
| 2 | Module boundaries | Any unauthorized cross-module coupling? Does new code respect existing module boundaries? | Boundaries not eroded |
| 3 | Contract changes | Any API/signature/behavior contract changes? Are they documented? Backward compatible? | Changes documented, compatible or explicitly broken |
| 4 | Cascade proliferation | Any new cascading dependency chains? Does a single change ripple beyond expected scope? | Ripple scope ≤ expected |
| 5 | Dependency direction | Do dependencies flow toward stability? Any circular or reverse dependencies? | No cycles, direction correct |
| 6 | Retirement completeness | Old owners/fallbacks/paths deleted or scheduled? Any "add only, never remove" patterns? | Retirement track explicit |
| 7 | Entropy flow | Net complexity decreased or increased? Any unjustified new entities, branches, or adapters? | Entropy decreased or stable |

If any dimension fails → record as an architecture finding → decide: fix now / schedule fix / record as known limitation.

The 7-dimension check results MUST be entered into the Reflection Risk/Unknown field (mapping rules in §17). For non-trivial code changes, the Entropy flow finding should be backed by the completion-time Complexity Delta when available.

### 15.1 Baseline Snapshot Update Trigger

A new `baseline/YYYY-MM-DD-<scope>-baseline.md` MUST be created when any of the following conditions are met:

1. **Architecture review found material Implementation Drift and it has been resolved** — implementation has returned to baseline or baseline has been updated via ADR; a new snapshot is needed to record the corrected state.
2. **Architecture review found an architecture-scoped Design Defect and it has been corrected** — baseline document has been fixed; a new snapshot is needed to solidify the correction.
3. **Reflection Evolve decision is "revise baseline"** — regardless of trigger source, if Reflection determines the baseline needs revision, a new snapshot must be written.
4. **Ownership map, contract inventory, or dependency direction convention has changed** — even if all 7 dimensions pass, if any of these three items changes, a new snapshot is required.
5. **ADR Auto Backfill created, amended, or superseded a decision that changes current architecture state** — the baseline must either be updated or explicitly state why the existing baseline remains valid.

For the first baseline in an uninitialized project, use the dual-baseline
bootstrap template from `brainstorming/SKILL.md` so the project starts with an
explicit `Product / Requirement Baseline` and an explicit `Architecture /
Runtime Boundary Baseline`, each with its own non-negotiables and non-goals.
For later change-date snapshots, preserve that role separation and record the
owner / contract / dependency truths that changed. Do not regress to a flat repo-inventory checklist. Snapshots are evidence, not authority -
`BASELINE-GOVERNANCE.md` remains the constitution.

Low-complexity tasks (no `work/`, no 7-dimension review) do not trigger snapshot updates.

---

## 16. Design Defect and Implementation Drift

### 16.1 Baseline Roles

Before classifying a baseline disagreement, identify which baseline role owns the
truth:

- `Product / Requirement Baseline`: confirmed requirement sources, target state,
  goals and scope, users and usage / system scenarios, functional requirements,
  quality requirements, constraint requirements, delivery / transition
  requirements, acceptance / verification criteria, non-goals, workflow
  constraints, open questions, change records, and approved requirement/spec
  intent.
- `Architecture / Runtime Boundary Baseline`: canonical owner, contract
  inventory, dependency direction, source-of-truth owner, compatibility boundary,
  runtime-ready/method-pack boundary, and retirement state.

Then classify the finding with:

```text
scope: requirements | architecture | both
```

### 16.2 Design Defect

Definition: a confirmed error, gap, contradiction, or wrong abstraction IN the
relevant requirement/design/baseline itself.

Criteria:
- The `Product / Requirement Baseline` contradicts the user's accepted problem,
  target state, requirement source, goal, scenario, requirement item, acceptance
  / verification criterion, non-goal, or workflow constraint.
- The `Architecture / Runtime Boundary Baseline` records an owner, contract,
  dependency direction, or source-of-truth boundary that contradicts the actual
  correct system shape.
- Two baseline/current-authority documents contradict each other.
- The baseline forces implementation to solve the right problem in the wrong
  owner, contract layer, or abstraction.

Process:
1. Confirm the baseline/design is the wrong party (not Implementation Drift).
2. Fix the relevant requirement, design, baseline, or ADR-backed current
   authority first.
3. If implementation deviated because the baseline/design was defective, align
   implementation to the corrected baseline.
4. NEVER patch implementation around a defective baseline/design.

### 16.3 Implementation Drift

Definition: implementation, plan, review output, or documentation has deviated
from a confirmed, correct, and unchanged product/requirement or architecture
baseline.

Criteria:
- Work implements behavior outside the accepted requirement, success evidence,
  or non-goals.
- New code introduced a new owner not recorded in the architecture baseline.
- New code modified a contract recorded in the baseline without updating the
  contract document.
- New code violated the dependency direction convention recorded in the baseline.
- New code duplicated the responsibility of an existing canonical owner.

Process:
1. Confirm the baseline is correct (not a Design Defect).
2. Return the implementation, plan, review, or documentation to the baseline via
   the simplest stable path.
3. If the drift is intentional, update the baseline first through the relevant
   requirement/spec/ADR process, then align the implementation.
4. NEVER "update the baseline to match the drift" without explicit review.

### 16.4 Compatibility Aliases

Older Aegis wording remains valid as an architecture-scoped subset:

- `Architecture Defect` = architecture-scoped `Design Defect`
- `Architecture Drift` = architecture-scoped `Implementation Drift`

Reviewers may use the old terms when reading historical docs, but new baseline
work should report `Design Defect` / `Implementation Drift` plus
`scope: requirements | architecture | both`.

### 16.5 Baseline Check Protocol

Before every non-trivial change:
1. Read the latest Product / Requirement Baseline candidate: requirement
   sources, goals and scope, users / scenarios, requirement items, acceptance /
   verification criteria, open questions, accepted requirements/spec,
   product/current docs, or task intent. If only a task intent or conversation
   exists, treat it as a candidate requirement source, not durable baseline
   authority.
2. Read the latest Architecture / Runtime Boundary Baseline candidate:
   baseline snapshot, ADR, current authority doc, owner map, contract inventory,
   or runtime boundary doc.
3. Compare current implementation and plan against requirement acceptance and
   architecture owner/contract boundaries.
4. Check whether known anti-patterns have new instances.
5. Report: aligned / Design Defect / Implementation Drift /
   missing-authority / needs-clarification, with
   `scope: requirements | architecture | both`.

---

## 17. Architecture Review → Reflection Risk/Unknown Mapping

Explicit mapping from 7-dimension check results to Reflection checklist:

| Architecture Dimension | Reflection Field | Mapping Rule |
|------------------------|-----------------|--------------|
| Ownership integrity | Risk/Unknown | New duplicate owner → record as Risk |
| Module boundaries | Risk/Unknown | Boundary erosion → record as Risk |
| Contract changes | Evidence | Contract change → cite as Evidence |
| Cascade proliferation | Risk/Unknown | Ripple beyond expected → record as Unknown |
| Dependency direction | Risk/Unknown | Cycle/reversal → record as Risk |
| Retirement completeness | Risk/Unknown | Not retired → record as Risk, note schedule |
| Entropy flow | DeeperCause | Entropy increase → check for unanalyzed deeper cause |

This mapping ensures architecture review findings are not lost during the Reflection phase.
