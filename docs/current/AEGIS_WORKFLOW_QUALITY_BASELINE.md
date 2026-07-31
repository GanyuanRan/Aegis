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
9. pre-addition minimality so new owners, artifacts, adapters, fallbacks, and
   metrics are justified before they exist
10. visible change necessity before any new source-code path and before
    non-trivial source edits without making `using-aegis` heavier

The stable path is sample-driven hardening:

- define representative task samples first
- lock expected routing, output shape, workspace policy, and artifact policy
- only then change skill wording or workflow depth
- use the agentic benchmark baseline when a claim depends on with/without Aegis
  behavior across representative tasks

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
- medium tasks may use `Spec Brief`, compact plans, or evidence semantic slots
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
- locally green patch-shape state remains bounded in existing checkpoint prose
  and evidence refs rather than creating another artifact or schema field

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

`docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md` is the canonical current
owner for artifact classes, pressure signals, budget/closure shapes, and major
complexity follow-up semantics.

Pass criteria:

- plan-time checks appear in `brainstorming` and `writing-plans`
- pre-edit checks appear in implementation workflows before risky source edits
- completion keeps `Complexity Delta`, `Complexity Closure`, and adds a useful `Complexity Governance Suggestion`
- 800+ line files are soft pressure signals, not automatic edit bans
- 1200+ line files or touched artifacts in the largest 5-10% of the project are
  strong pressure signals
- checks stay advisory, cheap for low-risk work, and do not treat new files as
  automatically better
- implementation workflows classify edit intent before adding non-trivial logic
  to an over-budget or mixed-purpose owner
- `new-responsibility` does not go in place by default on an over-budget or
  mixed-purpose owner; use an existing owner, extract a clearer owner, split the
  task, or pause for plan review
- maintained test source files are governed like maintained source code, not as
  blanket low-risk exceptions
- plan/spec/baseline/ADR/work-record artifacts use artifact-aware complexity
  checks instead of source-code-only heuristics

### 3.10 Completion-Time Complexity Delta

Non-trivial code changes should report actual complexity movement before a
completion claim.

Pass criteria:

- completion checks distinguish plan-time complexity budget from actual diff
  results
- maintained source files over 800 lines, newly crossing 800 lines, or receiving
  new logic while already oversized are reported as review signals
- maintained test source files over 800 lines, newly crossing 800 lines, or
  receiving new logic while already oversized are reported as the same review
  signal class
- touched functions, methods, components, or cohesive blocks over roughly 80
  lines, deeply nested logic, or mixed reasons to change are reported as
  block-level complexity signals
- new branches, fallbacks, adapters, guards, or compatibility paths are paired
  with retired paths or a retirement trigger
- entropy increases are either justified by owner / compatibility evidence or
  reported as residual risk
- complexity movement is paired with a governance suggestion when follow-up is
  useful
- completion distinguishes `within-budget`, `exceeded-and-governed`, and
  `exceeded-unresolved`
- completion-time overrun is classified as `govern-now`,
  `follow-up-required`, or `not-complete` before any additional owner extraction
  or scope expansion
- `govern-now` stays inside the current authorized slice and has a clear
  verification boundary
- if the result is `exceeded-unresolved`, Aegis does not claim the task is
  complete

### 3.11 TDD Route Mode

TDD Mode should keep test-first discipline opt-in by default without weakening
completion evidence.

Pass criteria:

- default `off` mode disables automatic TDD routing, TDD-skill loading, and
  forced RED / GREEN while preserving proportional regression and
  `verification-before-completion`
- users may enable `auto` mode through config, environment override, or a host
  command, or request TDD directly with explicit query markers
- `auto` mode chooses a `TDD Route`: `strict`, `light`, or `skipped`
- `strict` is used for behavior, bugfix, contract, shared/core, producer /
  consumer, persistence, permission, migration, or meaningful regression risk
- `light` or `skipped` may be used for tiny low-risk edits, read-only tasks,
  docs-only changes, generated files, throwaway spikes, or environment-bound
  work where TDD does not fit
- a passing GREEN cycle proves local behavior only and does not by itself prove
  parent-task acceptance or final completion
- when business behavior, success evidence, or acceptance is unclear, the
  workflow routes to `brainstorming` or `writing-plans` before strict TDD
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
- `Slice Card` anchors slice-level completeness only; whole-task completion
  still requires `verification-before-completion` to reconcile slice progress
  with parent acceptance and goal closure
- micro-slices update checkpoint, evidence, and drift state under the existing
  long-task record when persistent state is needed
- durable plan/spec creation resumes only when the slice introduces a new
  owner, contract, schema, public API, architecture boundary, persistence or
  migration surface, security/permission risk, distribution/release surface, or
  unclear verification boundary
- artifact fan-out itself is treated as a complexity signal for plan and process
  artifacts, not just a documentation style preference

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
- non-trivial root claims include a `Deeper Cause Challenge` that identifies the
  upstream generator, recurrence path, bug-class counterfactual, plausible
  deeper candidate and rejection evidence, causal status, and topology /
  anti-disguise proof
- a green local intervention cannot close an open recurrence path or promote a
  `proximate` / `deepest-confirmed-root-unknown` mechanism to `root`
- the quick lane skips the full challenge only through a `Quick Exit Proof`
  covering local origin/termination, negative upstream/history/same-pattern
  evidence, and a bug-class variant counterfactual
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
- `writing-plans` can render an `Execution Readiness View` from existing
  runtime-ready drafts and the task plan for medium/high, subagent,
  handoff-prone, or long-running execution handoffs. This is a human-readable
  view, not a new artifact owner or approval gate.
- `brainstorming` and `writing-plans` can use a compact `Architecture Integrity
  Lens` when an executable direction may still encode responsibility overlap,
  a wrong canonical owner, caller-side fallback, stale path, or missed
  higher-level owner / contract / source-of-truth simplification
- `brainstorming` and `writing-plans` can use a compact `Existence Check` when
  an approach or plan would add a new owner, skill, artifact, adapter,
  fallback, workflow step, or benchmark metric; `systematic-debugging` uses the
  same check when a candidate repair would add a fallback, adapter, branch, or
  new owner. The trigger is the proposed addition behavior, not whether the
  prompt names `Existence Check`.
- `brainstorming` and `writing-plans` can use a compact
  `Plan-Time Complexity Check` to identify target file pressure, add-in-place
  risk, and safer file boundaries before implementation
- `writing-plans`, `systematic-debugging`, `test-driven-development`, and
  `executing-plans` can use a compact `Change Necessity` slot before any new
  source-code path or non-trivial source edit so no-change, docs/config-only,
  code-change, and needs-clarification decisions are visible before
  implementation
- `test-driven-development`, `systematic-debugging`, and `executing-plans` can
  use a compact `Pre-Edit Complexity Check` plus `Pre-Edit Owner-Fit Decision`
  to avoid stuffing new logic into an overloaded or wrong owner
- `requesting-code-review` uses `Findings First` and prioritizes bugs first,
  risk first, tests first
- `verification-before-completion` can emit a `Readiness Summary` for tests,
  docs, version, host compatibility, uncovered scope, and residual risk
- `verification-before-completion` can emit a `Complexity Governance Suggestion` after `Complexity Delta`
- `recording-architecture-decisions` can use a `Retro / Memory Filter` to
  distinguish executed durable decisions from unexecuted ideas
- a role persona is not a review lens; Aegis borrows sharp evaluation angles,
  not CEO/CSO/QA persona commands
- readiness, review, retro, and plan pressure outputs remain advisory
  method-pack guidance, not merge approval, publish authorization,
  authoritative `GateDecision`, or completion authority
- `Execution Readiness View` follows the same boundary: it may make
  implementation start conditions visible, but it must not claim
  `gate-passed`, `completion-granted`, or `authoritatively-safe`

### 3.15 Baseline Role Alignment

Baseline checks should separate requirement truth from architecture truth without
creating heavy ceremony.

Pass criteria:

- `Product / Requirement Baseline` is the place to check confirmed requirement
  sources, goals and scope, users / scenarios, functional / quality /
  constraint / delivery-transition requirement items, acceptance /
  verification criteria, non-goals, open questions, and user/workflow
  constraints
- `Requirement Ready Check` reports whether a requirement has enough confirmed
  source, goal, scenario, requirement-item, acceptance, and open-question
  context to proceed to design, planning, execution, or acceptance judgment
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
- Aegis Visibility Non-Omission Rule: when an Aegis skill is loaded and the task is not an obvious tiny fast-path, the first substantive user-visible stage must include one natural Aegis Visibility sentence naming why Aegis is shaping the task and what quality risk it reduces
- final closeouts for non-trivial Aegis-shaped work default to a compact
  `Aegis Impact and Safety Receipt`; a single natural Aegis sentence is only a
  minimum fallback for obvious low-risk work, and concise final answers are not
  reasons to drop the safety fields
- if the user asks after the fact why Aegis was not visible, the answer is a recovery path and not a substitute for the required entry visibility and final closeout
- task-owning workflows expose an `Aegis Visibility` semantic slot when Aegis
  materially changes the work: design-first restraint in `brainstorming`,
  owner / contract / verification pressure in `writing-plans`, root-cause and
  canonical-owner discipline in `systematic-debugging`, TDD route and
  regression boundary in `test-driven-development`, plan checkpoint and drift
  control in `executing-plans`, directional principle / falsifier clarity in
  `first-principles-review`, stop-condition and route clarity in
  `goal-framing`, resume / drift visibility in `long-task-continuation`,
  findings-first review focus in `requesting-code-review`, executed-decision
  filtering in `recording-architecture-decisions`, and retirement / deletion
  safety in `anti-entropy-governance`
- stage changes use a natural transition sentence when the task moves from
  diagnosis to repair, planning to implementation, implementation to
  verification, review to follow-up, or resume to drift check
- obvious tiny fast-path work can keep the trace implicit unless the user asks
  why Aegis did or did not trigger
- completion output keeps Aegis user-visible for non-trivial Aegis-shaped work
  and shows how Aegis changed the decision path, avoided likely misfixes, held
  boundaries, checked baseline/complexity safety, required evidence, and kept
  residual risk visible
- Aegis may appear more than once in the closeout when it materially shaped
  multiple parts of the judgment, but each mention should carry task-specific
  information rather than repeated slogan wording
- no single Aegis closeout phrase is canonical; repeated identical Aegis
  closeout wording across tasks is a quality miss
- structured trace is reserved for audit, debug, release, long-task review, or user request
- structured trace uses a `Trace Digest` when the user asks for white-box
  auditability: execution trace, evidence chain, retrieval chain, rule effects,
  skill-call stability, tool / command trace, verification trace, and value
  signals
- `Trace Digest` entries label their source confidence as `measured`, `observed`, `inferred`, `declared`, or `unknown`;
  unavailable host fields stay explicitly unavailable instead of being guessed
- a `Trace Capability Matrix` names which fields the current host can expose
  directly, which are transcript-observed, and which are unavailable
- trace output applies redaction and summary-first hygiene for logs, paths,
  external content, private text, and secret-like values
- trace may summarize decision rationale, but it must not expose raw chain-of-thought or raw internal reasoning
- `Trace Overhead Budget`: tiny fast-path work stays implicit; non-trivial
  entry visibility stays to a natural sentence by default; completion output
  uses the compact impact/safety receipt by default; full `Trace Digest` is
  on-demand or audit/release/debug scoped
- the trace stays advisory method-pack transparency, not runtime authority, not
  a runtime gate, and not completion authority

Default shape:

```text
Aegis Reason Note: <why Aegis is shaping the next step and what quality risk it reduces>
```

Completion shape:

```text
Aegis Impact and Safety Receipt:
- Key judgment:
- Avoided misfix:
- Boundary held:
- Baseline alignment:
- Complexity control:
- Evidence strength:
- Uncovered risk:
- Next most valuable verification:
- Aegis path:
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

On-demand white-box shape:

```text
Aegis Trace Digest:
- traceLevel: inline | receipt | structured
- hostCapabilities:
- taskStage:
- triggeredSkills:
- skippedRelevantSkills:
- evidenceChain:
- retrievalChain:
- staticRulesEvaluated:
- ruleEffects:
- toolCommandTrace:
- verificationTrace:
- stabilitySignals:
- valueSignals:
- confidenceLabels: measured | observed | inferred | declared | unknown
- unavailableFields:
- redactionApplied:
- boundary: advisory trace, not runtime authority or completion authority
```

### 3.17 Semantic Slots and Natural Surface

Aegis output must preserve governance forcing functions without making every
answer look like an internal process log.

Pass criteria:

- `Facts -> Inferences -> Conclusions` is an ordering principle, not a
  mandatory top-level response template
- required output content acts as an attention anchor for the code, contract,
  evidence, or governance logic it names; preserve that attention without
  stealing structural ownership from the active workflow
- required governance checks are treated as `Semantic Slots`, not rigid English
  headings
- `Aegis Visibility` is a semantic slot owned by the active workflow, not a
  mandatory fixed heading, a global skill log, or a replacement for evidence
- a `Natural Surface` is valid when the user-facing prose still makes the
  required slots auditable
- natural transition sentences may satisfy Aegis visibility when they name the
  owner / baseline read, failing example, minimum repair, and verification path
- natural expression may be concise, but it must not erase non-omittable
  semantic slots; for non-trivial loaded-skill work, entry visibility and final
  closeout are required even when no fixed heading is used
- completion output for non-trivial Aegis-shaped work uses a compact
  `Aegis Impact and Safety Receipt` by default. It groups value and safety:
  key judgment, avoided misfix, boundary held, baseline alignment, complexity
  control, evidence strength, uncovered risk, next most valuable verification,
  and optional Aegis path
- `verification-before-completion` is the single completion closeout
  aggregator for non-trivial Aegis-shaped work. Completion-adjacent structures
  such as `Readiness Summary`, `Trace Digest`, `Goal Closure`,
  `ADR Backfill Check`, `Retirement Closure`, `Baseline Alignment`, and
  `Complexity Delta` can feed the receipt or appear as optional expanded
  detail, but they must not replace the unified receipt or become competing
  final report owners
- `Governance Receipt`, `Baseline Alignment`, `Complexity Delta`,
  `Complexity Closure`, `Readiness Summary`, `Goal Closure`,
  `Retirement Closure`, and `ADR Backfill Check` remain semantic slots or
  expanded detail cards, but they should flow through the unified receipt by
  default instead of becoming separate user-visible report formats
- This owner contract is output conformance, not a new hot-path routing rule,
  runtime gate, or completion authority. It must not make `using-aegis`
  heavier or force Trace Digest ceremony when the task did not ask for audit
- fixed skill traces, used-skill lists, and stage handoff logs stay reserved for
  audit, debug, release, long-task review, or explicit user request
- natural expression does not relax evidence freshness, dual-track governance,
  baseline / architecture alignment, complexity delta, retirement closure, or
  authority-boundary requirements

Example natural transition:

```text
I will follow the Aegis order here: read the owner / baseline and current
implementation first, add a failing example for the generator main path, then
make the minimal repair and verify it.
```

The example is valid because it exposes the semantic slots that matter for the
task. It is not a replacement for completion evidence after the work is done.

### 3.18 Pre-Addition Minimality

Aegis should check whether a new surface needs to exist before it is designed
or planned.

Pass criteria:

- `brainstorming` and `writing-plans` use `Existence Check` when an approach or
  plan would add a new owner, skill, artifact, host adapter, fallback,
  compatibility path, workflow step, or benchmark metric
- `systematic-debugging` uses `Existence Check` before accepting a repair shape
  that would add a fallback, adapter, branch, or new owner; a user-requested
  fallback does not count as creation proof
- the check names the proposed new surface and an existing owner / reuse
  candidate
- creation is justified with proof, not preference for new structure
- entropy and retirement impact are visible before the approach or task list is
  endorsed
- `reuse-existing` routes work to the existing owner instead of creating a new
  surface
- `add-with-proof` carries verification signal and any retirement trigger into
  the design or plan
- the check remains advisory method-pack discipline, not a runtime gate,
  authoritative `GateDecision`, or completion authority

### 3.19 Change Necessity Before Source Edits

Aegis should make the reason for code change visible before any new source-code
path and before non-trivial source edits, while keeping `using-aegis` compact
and route-only.

Pass criteria:

- `using-aegis` delegates Change Necessity to the owning workflow instead of
  expanding the hot path
- the trigger is behavioral: any new source-code path and non-trivial source
  edits surface a natural code-necessity readback even when the user did not
  name `Change Necessity`
- a tiny helper, small guard, new branch, fallback, adapter, or owner is not
  exempt from Change Necessity merely because the addition looks small
- bug, failure, regression, or unexpected behavior does not stop at a
  `using-aegis`-only fast path; it routes to `systematic-debugging`
- `writing-plans` records `Change Necessity` before task decomposition when the
  plan will endorse a new source-code path or source edits
- `systematic-debugging` records `Change Necessity` after root cause and before
  repair code for any new source-code path and non-trivial fixes; quick bug lane may use one compact
  sentence, but it still appears before source edits
- `test-driven-development` records `Change Necessity` before strict RED/GREEN
  enters production code edits, including tiny guards or helpers
- `executing-plans` honors the plan's `Change Necessity` and creates a compact
  one before editing when the approved plan task would add a new source-code
  path but did not carry the slot forward
- the slot distinguishes `no-change`, `docs/config-only`, `code-change`, and
  `needs-clarification`
- the decision carries a minimum change boundary into files, fix boundary, or
  TDD route
- a valid natural surface may say: "Code necessity check: a non-code path is
  insufficient because <reason>; the minimum change boundary is <owner/files>,
  so the decision is code-change."
- tiny fast-path edits that add no new source-code path may satisfy the slot in
  natural prose or stay implicit when they are purely mechanical; tiny new
  source-code paths still need at least a natural Change Necessity readback
- the slot remains advisory method-pack discipline, not a runtime gate,
  authoritative `GateDecision`, or completion authority

### 3.20 Semantic Context Reliability

Project terminology should shape non-trivial work without making simple work
expensive or creating a second authority system.

Pass criteria:

- `establishing-project-context` is the only active-modeling and write-policy
  owner; consumers carry only bounded lookup or composition cues
- ordinary non-trivial work passively consumes relevant active terms without
  loading active modeling
- evidence grade (`A/B/C`) and semantic authority (`fact/decision`) remain
  separate; A/B facts may update directly, while unresolved decisions ask one
  bounded user question and do not become active truth
- the first resolved term may create the glossary lazily; there is no fixed
  initial term quota or preliminary consent requirement for decided facts
- no semantic delta leaves bytes unchanged, and pre-write readback preserves
  unrelated concurrent changes
- root plus mapped bounded-context selection is relevant and bounded rather
  than reading every glossary
- legacy table glossaries remain readable while new writes use compact natural
  Markdown without volatile timestamps or task/session metadata
- context content is treated as semantic data, not executable policy; mapped
  paths and symlinks cannot escape the project root
- later planning, debugging, review, and continuation reuse updated canonical
  terms
- tiny tasks do not read, create, write, or report context ceremony
- context output remains terminology-only and does not become architecture,
  requirement, task-state, evidence, or completion authority
- cache friendliness is an optimization property, not a provider cache-hit,
  latency, context-capacity, or billing guarantee

### 3.21 Capability-Preserving Progressive Disclosure

High-frequency workflow skills may use progressive disclosure to reduce their
default loaded payload, but capability remains the acceptance boundary.

Pass criteria:

- each main body retains an executable quick/default path and explicit,
  evidence-based triggers for every direct reference it may require
- moving deep detail into a direct reference does not weaken required semantic
  slots, owner and root-cause rules, escalation behavior, or verification
  evidence
- direct references load only when task evidence activates their documented
  triggers; untriggered references do not become default prompt payload
- capability gates pass before size gates: `systematic-debugging/SKILL.md` is
  at most 10,000 bytes, `verification-before-completion/SKILL.md` is at most
  7,000 bytes, their combined main bodies are at most 17,000 bytes, and
  `using-aegis/SKILL.md` remains within its existing 2,500-byte hot-path ceiling
- if a required behavior cannot fit these ceilings, return to design review
  instead of deleting capability or hiding it behind an undiscoverable trigger

These ceilings are maintenance constraints for capability-preserving skill
payloads. They are not benchmark performance results and do not claim lower
latency, token usage, cost, or model-context occupancy.

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
Bug, failure, regression, or unexpected behavior is not `using-aegis`-only
fast-path work; route it to `systematic-debugging`, which may then use the
quick bug lane.
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
Aegis Visibility: why design/spec comes before implementation and what drift or overbuild risk this prevents
TaskIntentDraft: outcome, scope, risk hints
BaselineReadSetHint: candidate docs, missing authority
BaselineUsageDraft: required refs, acknowledged refs, cited refs, missing refs, decision
ImpactStatementDraft: affected layers, owners, invariants, non-goals
Product Risk Lens: value, non-goals, trade-offs, decision-needed
Existence Check: proposed new surface, existing owner / reuse candidate, creation proof, entropy / retirement impact, decision
Architecture Integrity Lens: invariant, owner/contract, overlap, higher-level path, retirement/falsifier, verdict
Baseline Role Alignment: Product / Requirement Baseline, Architecture / Runtime Boundary Baseline, Requirement Ready Check, Design Defect / Implementation Drift, scope
Complexity Budget: artifact class, current pressure, projected post-change pressure, planned governance
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
Aegis Visibility: why the goal frame constrains route, stop condition, and non-goals without becoming trace ceremony
Route: fast-path | <skill-name> | needs-baseline-readback
Next: next smallest safe action
Continuation: continue into the routed workflow by default
```

Goal framing is opt-in. It does not create project workspace records unless the
routed workflow needs persistent evidence, and it does not grant completion
authority. It is a start protocol, not a stop point: do not stop after
`TaskIntentDraft` unless the user explicitly asks for frame-only behavior such
as only defining the goal / stop condition, not executing, not implementing, not
writing a plan, or waiting for confirmation.

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
Aegis Visibility: which owner, contract, retirement, or verification pressure makes planning useful before execution
BaselineUsageDraft: required baseline refs, acknowledged refs, cited refs, missing refs, decision
Planless Slice Lane: use Slice Card when an existing parent plan/spec already owns the tiny slice
Files: owners and edit boundaries
Compatibility: invariants and non-goals
Change Necessity: user-visible need, no-change / non-code option, why code change, minimum boundary, decision
Existence Check: proposed new surface, existing owner / reuse candidate, creation proof, entropy / retirement impact, decision
Architecture Integrity Lens: invariant, owner/contract, overlap, higher-level path, retirement/falsifier, verdict
Plan Pressure Test: owner / contract / retirement risk and verification scope
Complexity Budget: artifact class, current pressure, projected post-change pressure, planned governance
Plan-Time Complexity Check: target files, add-in-place risk, better boundary, recommendation
Tasks: bite-sized steps with verification
Risks: residual unknowns and rollback surface
Retirement: old owner/fallback handling when applicable
Execution Readiness View: optional human-readable rendering of intent lock, scope fence, baseline lock, owner / contract constraints, compatibility boundary, retirement boundary, task batches, test obligations, review gates, drift / rewind rules, and evidence required before completion
```

Use `Execution Readiness View` when a plan is about to cross into subagent,
handoff-prone, long-running, medium/high, architecture, contract, compatibility,
or retirement-sensitive execution. Skip it for tiny fast-path tasks unless the
user asks for an execution handoff readback.

Do not redesign without cause. Do not create a new durable plan when a compact
Slice Card inside the parent workstream is enough.

### 4.4 `systematic-debugging`

Purpose:

- locate root cause before repair

Compact contract:

```text
Aegis Visibility: how root-cause, canonical-owner, patch-shape, and verification discipline changed the repair path
Symptom: observed failure
Reproduction: command/input and result
Root Cause: evidence-backed owner and cause
Layer Stop Card: stop layer, topology, checked path, evidence, excluded layers, falsifier, user intervention point, next action
Pre-Claim Gate: causal closure, falsifier checked, adversarial self-refutation, topology classified, layer ceiling proof — required before claiming root cause when a patch-shape signal fires
Topology Card: explicit causal topology (single-root / single-root-multi-symptom / chain / independent-compound / conjunctive-cluster / disjunctive-or) with topology-specific member proof and anti-disguise check
Deeper Cause Challenge: claimed cause, causal status, upstream generator, recurrence path, counterfactual, deeper candidate, rejection evidence, recurrence status, topology / anti-disguise proof
Quick Exit Proof: canonical local owner, origin/termination, negative upstream/history/same-pattern evidence, variant counterfactual, root status
Change Necessity: user-visible need, no-change / non-code option, why code change, minimum boundary, decision
Fix Boundary: canonical owner, compatibility, non-edits
Minimality Check: smallest textual diff, existing owner / reuse path, correct owner, bug class fixed, new branch/fallback, old path retirement, verdict
Existence Check: proposed fallback/adapter/branch/new owner, existing owner / reuse candidate, creation proof, entropy / retirement impact, decision
Pre-Edit Complexity Check: target edit file, pressure signal, safer boundary, decision
Pre-Edit Owner-Fit Decision: edit intent, owner fit, safer boundary, decision
Verification: failing test or reproduction now passing
Repair Track / Retirement Track: when fallback, owner, or contract risk exists
```

Quick bug lane is allowed for low-risk bugs, but root-cause evidence is still
required, and `Change Necessity` still appears before source edits. Use
an explicit decision token such as `Decision: code-change`; minimum-boundary
wording is not a substitute for the decision. Use
`Layer Stop Card` when the diagnostic stop point is ambiguous, crosses a
boundary, reaches L5/L6/L7, or is corrected by a user-provided falsifier. Do
not use it for simple factual Q&A or tiny fast-path responses.

Use `Pre-Claim Gate` and `Topology Card` when a patch-shape signal fires
(guard, fallback, consumer/caller patch, artifact/cache patch, or sample-only
naming) or the diagnosis crosses a component boundary. The gate turns a
self-judged stop into a checkable, falsifiable claim; it is advisory
method-pack discipline, not a `GateDecision`, `PolicySnapshot`, or completion
authority.

Use the `Deeper Cause Challenge` before every non-trivial root claim and when an
upstream producer/config/default/contract/policy/spec dependency remains
unexcluded. If the recurrence generator stays open, preserve `proximate`,
`contributing`, or `deepest-confirmed-root-unknown` status. Keep true local bugs
cheap only when the `Quick Exit Proof` is complete.

When a patch-shape/ripple/H-class or bounded compatibility slice passes local
verification, its checkpoint state still carries `PatchShape`,
`CanonicalOwner`, `UpwardDrillSignal`, decision, outcome, and a bounded evidence
ref. A later unplanned candidate is compared by invariant, owner seam, patch
shape, and causal topology; carrier naming alone cannot reset the direction.

### 4.4a `test-driven-development`

Purpose:

- apply strict TDD only when the TDD Route calls for it

Compact contract:

```text
Aegis Visibility: why the route is strict, light, or skipped and what RED/GREEN does and does not prove
TDD Route: mode, decision, strict authority when decision is strict, test posture, reason, verification
Test Posture: diagnostic reproduction | post-change regression | strict RED test
Preflight Gate: low | route-to-plan | route-to-spec
Change Necessity: user-visible need, no-change / non-code option, why code change, minimum boundary, decision
Complexity Budget: artifact class, current pressure, projected post-change pressure, planned governance
Pre-Edit Complexity Check: target edit file, pressure signal, safer boundary, decision
Pre-Edit Owner-Fit Decision: edit intent, owner fit, safer boundary, decision
RED: failing test only when decision is strict; otherwise state why strict TDD is skipped
GREEN: minimal code and passing target test only for strict TDD
REFACTOR: cleanup with tests still green only for strict TDD
Regression Scope: target, related, producer/consumer, manual fallback
```

In `auto` mode, strict/light/skipped route decisions scale with risk. In `off`
mode, record `Decision: skipped` for plan/execution review unless an explicit
user/project strict request overrides it; do not automatically require TDD.
Diagnostic reproduction and post-change regression remain available evidence,
while only a recorded strict route makes a failing test a RED gate.
`verification-before-completion` still requires fresh completion evidence.

### 4.5 `requesting-code-review`

Purpose:

- request advisory independent review with sharp findings and bounded authority

Compact contract:

```text
Aegis Visibility: why findings-first review, evidence sufficiency, baseline alignment, or retirement risk matters for this review
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
Required evidence semantic slots:
- evidence action / check performed
- result / exit status
- covered scope
- uncovered scope
- residual risk
- confidence grade: A | B | C
Aegis Visibility: decision boundary, evidence discipline, baseline/complexity safety, and residual risk kept visible
Semantic Slots: required governance fields may appear as localized headings,
natural prose, or compact cards when they remain explicit and auditable
Natural Surface: natural user-facing wording is valid when it preserves the
semantic slots
Aegis Impact and Safety Receipt: default compact closeout for Aegis-shaped
non-trivial work, naming key judgment, avoided misfix, boundary held, baseline
alignment, complexity control, evidence strength, uncovered risk, next most
valuable verification, and optional Aegis path
Governance Receipt: compatibility name for the completion closeout slot; its
user-facing rendering should flow through the impact/safety receipt by default
Readiness Summary: tests, docs, version, host compatibility, residual risk
Natural Aegis closeout: the receipt stays localized and natural; a single
sentence is only the minimum fallback for low-risk work, not the default
non-trivial closeout
Trace Digest: on-demand white-box summary for execution trace, evidence chain,
retrieval chain, static rules evaluated, rule effects, triggered and skipped
skills, tool/command trace, verification trace, stability signals, value
signals, confidence labels, host capabilities, unavailable fields, redaction,
and advisory boundary
Complexity Closure: planned budget vs actual result, governed now, deferred follow-up, completion impact
Major Complexity Alert: materially oversized maintained artifact that needs explicit user-visible follow-up
```

Localize completion card labels and explanatory prose to the user's language.
Do not default to bilingual labels or mixed-language explanations. Keep
commands, paths, code identifiers, test names, error codes, config keys, stable
enum values, raw evidence strings, and exact product names unchanged. For
important Aegis product terms, include the stable English identifier only when
auditability or exact doc cross-reference requires it.

When project instructions require baseline reporting, or completed medium/high
work touched requirement, product, or architecture surfaces, include an advisory
`Baseline Alignment` result before the final completion claim. By default,
render its user-facing conclusion in the receipt's baseline alignment field and
use the expanded card only for audit, release, architecture, or user-requested
detail:

```text
Baseline Alignment:
- Trigger: yes | no
- Product / Requirement Baseline:
- Architecture / Runtime Boundary Baseline:
- Requirement Ready Check:
- Requirement / acceptance alignment:
- Architecture / owner / contract alignment:
- Requirement acceptance boundary: task-or-slice-done | requirement-verified | requirement-accepted | risk-accepted | not-accepted | unknown
- Result: aligned | Design Defect | Implementation Drift | missing-authority | needs-clarification
- scope: requirements | architecture | both
- Evidence:
- Residual risk:
```

`Baseline Alignment` states whether the completed work matches the current
requirement and architecture baselines, or should be reported as Design Defect /
Implementation Drift. It is separate from ADR Backfill and does not grant
completion authority. A completed task, completed slice, or passing test can
support `requirement-verified`, but only confirmed acceptance criteria or
authorized risk acceptance can support `requirement-accepted` or
`risk-accepted`.

Use `docs/current/AEGIS_PROCESS_BASELINE.md` §3.0e and §16 for the canonical
meaning of `Product / Requirement Baseline`, `Architecture / Runtime Boundary
Baseline`, `Design Defect`, `Implementation Drift`, and their compatibility
aliases.

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

Use `docs/current/AEGIS_ADR_AUTO_BACKFILL.md` for canonical trigger criteria,
durable-surface interpretation, create/amend/supersede/skip selection, and
baseline-sync rules.

When the suggested ADR action is create, amend, or supersede, or when baseline
sync is needed or unknown, use `recording-architecture-decisions` for the ADR
lifecycle and Baseline Sync Closure before the final completion claim.

If evidence is incomplete, the claim must be downgraded.

A `Readiness Summary` can organize release or handoff evidence, but it is not
authorization to commit, tag, publish, merge, or release.

TDD Mode `off` does not reduce this contract. Completion claims still require
fresh verification evidence.

Goal Closure:

When a task used `goal-framing`, `verification-before-completion` must match
the completion claim to the highest available explicit boundary and keep any
higher open boundary visible:

```text
Goal status: satisfied | blocked | needs-verification | scope-exceeded
Success evidence: fresh commands, files, logs, or manual verification
Stop state: done | blocked | needs-verification | scope-exceeded
Non-goals respected: yes | no | unknown
```

Goal Closure is advisory and evidence-focused. It does not grant completion
authority or decide final evidence sufficiency.

For the shared `Complexity Delta`, `Complexity Closure`,
`Completion-Time Complexity Repair Decision`, and `Major Complexity Alert`
shapes, see
`docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md`. By default, render the
user-facing conclusion in the receipt's complexity control field; expand the
cards when meaningful pressure exists or the task is audit/release/high-risk.

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

If the work retires old logic, chooses between delete-first and compat
retention, or touches source-of-truth deletion boundaries, include
`Anti-Entropy Declaration`:

```text
Anti-Entropy Declaration:
- Deletion Class:
- Source-of-Truth Data Risk:
- User Confirmation Required:
```

If `User Confirmation Required: yes`, the workflow must stop at a
`Data Destruction Guard`. Mentioning a destructive rule or warning never
authorizes execution:

```text
Data Destruction Guard:
- Exact Target(s):
- Blocked Destructive Steps:
- Confirmation Required: yes
- Status: awaiting scoped confirmation
```

### 4.6a `anti-entropy-governance` (composed)

Purpose:

- classify retirement and deletion targets without granting destructive
  authority

Compact contract:

```text
Aegis Visibility: why retirement, compatibility retention, or confirmation-first safety shaped the work
Anti-Entropy Declaration: deletion class, preserved vs retired behavior, source-of-truth risk, confirmation need
Retirement Decision: delete-first | compat-exception | confirmation-first, why, non-edits
Verification Plan: main-path, lingering-reference, negative, boundary checks
Gap Closure: gap type, repair action, compat reintroduction, retirement trigger
Data Destruction Guard: exact targets, blocked destructive steps, confirmation status when persistent-state is touched
```

This skill is composed by owning workflows such as `brainstorming`,
`writing-plans`, `systematic-debugging`, and
`verification-before-completion`. It should not become a new global hot-path
entry, and it never grants destructive execution authority.

### 4.7 `long-task-continuation`

Purpose:

- preserve state across long, multi-phase, subagent, handoff, resume, or
  compaction-prone work

Compact contract:

```text
Aegis Visibility: why checkpoint, resume, drift, or handoff discipline is shaping this long task
TodoCheckpointDraft: current todo, completed todos, active slice, next step
BaselineUsageDraft: required refs, acknowledged refs, cited refs, missing refs, decision
Slice Card: goal, parent plan/spec, files, boundary, verification, stop
Execution Readiness View: re-read or refresh when resuming a medium/high parent plan or handoff-prone workstream
Evidence: command/file/log refs
DriftCheckDraft: scope, compatibility, retirement, decision
Risk / Unknown: blockers or missing evidence
Next: next smallest safe action
```

Low-complexity tasks skip `work/`. Micro-slices reuse the parent plan/spec and
update the existing long-task checkpoint/evidence trail instead of creating
per-slice plan or spec files.
When an `Execution Readiness View` exists, resume and checkpoint updates compare
the active slice against its intent lock, scope fence, baseline lock,
compatibility boundary, retirement boundary, test obligations, and review gates.
Drift routes back to planning or a refreshed advisory handoff instead of
continuing from chat memory alone.
Triggered patch-shape state survives a locally green slice in the existing
checkpoint/evidence trail; resume reads it before proposing an unplanned edit.

### 4.7a `executing-plans`

Purpose:

- execute an approved plan while preserving checkpoint, drift, pre-edit, and
  verification discipline

Compact contract:

```text
Aegis Visibility: why the active slice is constrained by the approved plan, checkpoint, drift check, pre-edit governance, or verification boundary
Plan Review: concerns, blockers, or proceed decision
Todo: active task, completed tasks, next task
Change Necessity: inherited from plan or compactly recreated before new source-code paths
Complexity Budget: planned pressure and governance for the active edit
Pre-Edit Complexity Check: safer edit boundary and pause condition
Pre-Edit Owner-Fit Decision: edit intent, owner fit, safer boundary, decision
Execution Readiness View: read before implementation when provided by the plan or long-task checkpoint
Verification: commands, scope, and result for the slice
Checkpoint: TodoCheckpointDraft, DriftCheckDraft, evidence refs
```

This workflow executes a plan; it does not redesign without cause and does not
grant completion authority. If the active slice contradicts the plan's owner,
complexity, or verification boundary, return to plan review instead of pushing
through. If an `Execution Readiness View` contradicts the current plan, baseline,
or worktree evidence, refresh the advisory handoff or return to planning before
editing.
Verification-driven unplanned edits first read retained patch-shape/owner state.
`systematic-debugging` judges whether consumer, caller, fallback, or
downstream-reinference candidates converge and require rewind; proven
independent canonical-owner roots remain on the normal plan path.

### 4.8 `recording-architecture-decisions`

Purpose:

- record durable architecture decisions and close baseline sync without
  becoming a completion owner

Compact contract:

```text
Aegis Visibility: why executed-decision filtering, ADR gate, owner surface, or baseline sync matters now
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

The agentic benchmark fixture is the public design contract for measuring
with/without Aegis behavior. It measures route, evidence, authority, owner,
retirement, and workspace discipline; it does not turn benchmark output into
completion authority.

It does not grant authoritative runtime decisions, final gate decisions,
evidence sufficiency, or completion authority.
