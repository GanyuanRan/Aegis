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

- 800+ line maintained source or maintained test file
- touched cohesive block over roughly 80 lines
- deep nesting or mixed reasons to change
- generic owner receiving another responsibility
- fallback / adapter / guard / compatibility branch growth
- owner mismatch or duplicate-owner risk
- plan / process artifact fan-out that harms execution clarity
- multi-owner sprawl, duplicated decision text, unreadable work-log structure,
  or handoff-hostile artifact layout

Generated files, vendored files, lockfiles, framework-owned artifacts,
fixture-data-only updates, and purely mechanical formatting may be exempt when
the reason is explicit.

A new file is not automatically better. Prefer a new file only when owner,
contract, call path, and retirement story are clearer than add-in-place growth.

## 5. Three-Stage Governance

1. **Plan-Time Complexity Check**: `brainstorming` and `writing-plans` inspect
   likely owner files and artifacts, estimate post-change pressure, and choose
   edit-in-place, extract helper, add owner file, split task, defer refactor,
   or revise the plan before code is written.
2. **Pre-Edit Complexity Check**: `test-driven-development`,
   `systematic-debugging`, and `executing-plans` re-check the actual edit file
   or artifact and pause for a plan update if the safest boundary differs from
   the plan.
3. **Complexity Delta + Complexity Governance Suggestion +
   Complexity Closure**: `verification-before-completion` compares the final
   diff against the planned budget and reports whether the slice is
   `within-budget`, `exceeded-and-governed`, or `exceeded-unresolved`.

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
