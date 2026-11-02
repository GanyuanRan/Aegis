# Aegis Complexity Governance Baseline

Status: `Reviewed`

## 1. Document Scope

This document is the canonical current baseline for complexity governance in the
`Aegis Method Pack`.

It defines:

- which maintained artifact classes complexity governance applies to
- the shared pressure-signal interpretation used across planning,
  implementation, and completion
- the shared budget, closure, and major-follow-up shapes
- the rule that unresolved complexity overrun blocks an Aegis completion claim

It does not define:

- runtime authority
- merge or release authorization
- host adapter implementation details

## 2. Artifact Classes

Complexity governance applies to maintained artifacts, not only production code.
At minimum:

- `Source Complexity`: production and library source owners
- `Test Complexity`: maintained test source owners, helpers, harnesses, routers,
  and assertion/build orchestration
- `Decision / Plan Complexity`: spec, brief, plan, baseline, and ADR artifacts
  whose structure affects implementation quality
- `Process Artifact Complexity`: checkpoints, evidence, reflections, and other
  durable work records whose sprawl affects continuity, reviewability, or
  handoff quality

Do not treat a maintained test source file as a cheap `tests-only` exception.

## 3. Shared Budget Shape

Use this compact budget when plan-time or pre-edit checks need a shared shape:

```text
Complexity Budget:
- Artifact class:
- Target files / artifacts:
- Current pressure:
- Projected post-change pressure:
- Budget result: within-budget | at-risk | over-budget
- Planned governance:
```

## 4. Shared Pressure Signals

Typical pressure signals:

- 800+ line maintained source or maintained test file as a soft pressure signal,
  not an automatic edit ban
- 1200+ line maintained artifact, or a touched artifact in the largest
  5-10% of the target project, as a strong pressure signal
- touched cohesive block over roughly 80 lines
- deep nesting or mixed reasons to change
- generic owner receiving another responsibility
- fallback / adapter / guard / compatibility branch growth
- owner mismatch or duplicate-owner risk
- plan / process artifact fan-out that harms execution clarity
- repeated failed verification attempts in one slice without terminal evidence
- evidence sidecar fan-out where each retry creates a new bundle
- checkpoint or evidence markdown growing through append-only retry records
- multi-owner sprawl, duplicated decision text, unreadable work-log structure,
  or handoff-hostile artifact layout

Generated files, vendored files, lockfiles, framework-owned artifacts,
fixture-data-only updates, and purely mechanical formatting may be exempt when
the reason is explicit.

A new file is not automatically better. Prefer a new file only when owner,
contract, call path, and retirement story are clearer than add-in-place growth.

### Structural Improvement, Not Count Manipulation

Line counts locate pressure; a lower count alone does not establish structural
improvement or create growth allowance. Joining statements, compressing imports,
deleting useful explanation, or moving code solely to satisfy a count does not
resolve the pressure. Mechanical formatting may be valid work without being a
complexity repair.

For a structural claim, compare responsibilities, branches, dependency direction,
duplication and executable statements where available. Explain the dimensions
that changed and the behavior preserved; not every dimension must decrease.
Statement counts are supporting evidence, not a new threshold or mandatory tool.
Unavailable measurements stay unknown or inapplicable, never zero or passed.

A cohesive extraction can improve ownership with unchanged statement totals or
slightly more wiring. Check the new boundary, callers, dependencies and old-path
disposition; neither a new file nor a smaller original file proves improvement.

## 4.1 Pre-Edit Owner-Fit Decision

When the target edit file is already over-budget or mixed-purpose, the
implementation workflow must classify edit intent before non-trivial source
edits:

```text
Pre-Edit Owner-Fit Decision:
- Target edit file:
- Existing pressure signal:
- Edit intent: wiring-only | move-out / extract-first | local-fix-without-new-responsibility | new-responsibility | emergency / compatibility patch
- Owner fit:
- Safer edit boundary:
- Decision: edit-in-place | extract helper | add owner file | split task | pause for plan update
```

Default interpretation:

- `wiring-only` may edit in place when it only adjusts references, calls, or
  composition and does not add a responsibility.
- `move-out / extract-first` may touch an overloaded file only when the slice
  makes that owner thinner or clearer.
- `local-fix-without-new-responsibility` may edit in place when the fix stays
  inside the existing owner contract and does not add branches, routing,
  fallback, adapter, or state responsibilities.
- `new-responsibility` must not be added in place to an over-budget or
  mixed-purpose owner by default. Reuse or extract the correct owner, split the
  task, or pause for plan review.
- `emergency / compatibility patch` requires residual risk and a retirement
  trigger; do not present it as clean complexity closure.

If the edit intent is unclear, pause before source edits and return to plan
review instead of normalizing add-in-place growth.

## 5. Three-Stage Governance

1. **Plan-Time Complexity Check**: `brainstorming` and `writing-plans` inspect
   likely owner files and artifacts, estimate post-change pressure, and choose
   edit-in-place, extract helper, add owner file, split task, defer refactor,
   or revise the plan before code is written.
2. **Pre-Edit Complexity Check + Owner-Fit Decision**:
   `test-driven-development`, `systematic-debugging`, and `executing-plans`
   re-check the actual edit file or artifact, classify edit intent when an
   overloaded or mixed-purpose owner is involved, and pause for a plan update if
   the safest boundary differs from the plan.
3. **Complexity Delta + Complexity Governance Suggestion +
   Complexity Closure**: `verification-before-completion` compares the final
   diff against the planned budget and reports whether the slice is
   `within-budget`, `exceeded-and-governed`, or `exceeded-unresolved`.
   User-facing completion should summarize this in the unified Aegis impact /
   safety receipt's complexity-control field by default, and expand the cards
   below when meaningful pressure, release risk, audit needs, or user request
   requires detail.

## 6. Completion-Time Closure

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

```text
Complexity Closure:
- Budget status: within-budget | exceeded-and-governed | exceeded-unresolved
- Governed now:
- Deferred follow-up:
- Completion impact: complete | needs-follow-up | not-complete
```

If `Complexity Closure` is `exceeded-unresolved`, Aegis must not claim the task
is complete.

When completion-time complexity is over budget, classify whether the overrun
can be governed inside the current authorized slice:

```text
Completion-Time Complexity Repair Decision:
- Overrun:
- Authorized slice boundary:
- Decision: govern-now | follow-up-required | not-complete
- Why:
- Verification:
```

- `govern-now` may continue with owner extraction, helper extraction, or old
  path deletion only when the repair is inside the current authorized scope,
  reduces or stabilizes complexity, and has a clear verification boundary.
- `follow-up-required` reports residual risk and suggested scope without
  expanding the current task.
- `not-complete` means the overrun blocks the requested completion claim.

Before defaulting to user intervention, choose the smallest feasible repair
inside the authorized slice: reuse the correct owner or extract a cohesive
module; separate mixed responsibilities or simplify duplicated branches and
dependencies; then narrow the change only if the requested outcome remains met.
Each candidate needs a clear verification boundary. Continue an already
authorized repair without repeating approval. If none fits, report the limiting
constraint and concrete follow-up or decision needed; do not silently omit
required behavior. These are candidate paths, not compulsory refactoring steps,
permission for destructive work, or a numeric growth allowance.

## 7. Major Complexity Follow-up

When the current slice encounters a materially oversized maintained artifact
that it cannot fully govern, emit:

```text
Major Complexity Alert:
- Artifact:
- Why it is materially oversized:
- Why this slice cannot fully govern it:
- Recommended follow-up: monitor | schedule-refactor | split owner | open follow-up
```

## 8. Boundary

This baseline is method-pack governance discipline only.

It can block an Aegis completion claim when complexity overrun remains
unresolved, but it does not create runtime authority, final evidence
sufficiency, merge approval, or release authorization.
