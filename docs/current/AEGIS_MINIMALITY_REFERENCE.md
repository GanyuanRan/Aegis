# Aegis Minimality Reference

Status: `Draft`

## 1. Purpose

This document defines Aegis-specific "check before adding" prompts.

The goal is not to make Aegis optimize for fewer lines of code. The goal is to
avoid adding new owners, artifacts, adapters, fallbacks, and workflow ceremony
when an existing Aegis surface already carries the responsibility.

## 2. Shared Existence Check

Use this compact shape when a workflow may add a new owner, skill, artifact,
host adapter, fallback, compatibility path, workflow step, or benchmark metric:

```text
Existence Check:
- Proposed new surface:
- Existing owner / reuse candidate:
- Why existing surface is insufficient:
- Creation proof:
- Entropy / retirement impact:
- Decision: reuse-existing | add-with-proof | defer | reject | needs-first-principles-review
```

If `Decision` is `reuse-existing`, update the existing owner instead of adding a
new surface. If `Decision` is `add-with-proof`, carry the proof, verification
signal, and any retirement trigger into the design, plan, or completion
evidence.

## 3. Before Adding A Skill

Check:

- Can an existing skill description or reference cover the trigger?
- Is the gap a routing sample, execution-depth issue, or missing baseline
  wording instead of a new workflow?
- Would adding a skill create overlap with an existing owner?
- Can the improvement be expressed as a small fixture and wording change?

Prefer:

- update the smallest owning skill
- add a representative workflow-quality or trigger-health sample
- keep `using-aegis` compact

## 4. Before Adding An Artifact

Check:

- Can an existing runtime-ready draft or hint represent the need?
- Is this a reusable project record or only process evidence for one task?
- Does the artifact need a JSON sidecar, or is natural prose enough?
- Will the artifact fan out into plan/spec/work sprawl?

Prefer:

- reuse `TaskIntentDraft`, `BaselineUsageDraft`, `ImpactStatementDraft`,
  `EvidenceBundleDraft`, `DriftCheckDraft`, or `GateInputPack`
- use a `Slice Card` for bounded micro-slices under an existing parent plan
- keep process evidence out of `docs/current` unless it is public baseline

## 5. Before Adding A Host Adapter

Check:

- Can the host consume existing skills directly?
- Can a short host-native reference point at `skills/using-aegis/SKILL.md`?
- Is the gap discovery, activation, JSON shape, or tool mapping?
- Does the adapter need tests for version, path, hook, and authority boundary?

Prefer:

- thin adapters
- canonical skill bodies as the source of method behavior
- host-specific tool mapping outside the portable method body

## 6. Before Adding A Fallback Or Compatibility Path

Check:

- Is there active external dependency evidence?
- Is the fallback protecting a published host boundary, or preserving internal
  history?
- What is the observation metric?
- What is the retirement trigger?
- Can the canonical owner be fixed instead?

Prefer:

- delete-first for internal code retirement
- compatibility exceptions only with active dependency evidence
- explicit retirement closure when old logic remains

## 7. Before Adding A Benchmark Metric

Check:

- Does the metric measure Aegis value, or only incidental code size?
- Can the metric be gamed by making tasks smaller while losing evidence?
- Does the report boundary forbid authority and savings overclaims?
- Does the scorer have self-tests?

Prefer:

- route correctness
- evidence freshness
- authority boundary
- false completion rate
- owner fix accuracy
- retirement coverage
- workspace laziness

## 8. Boundary

This reference is advisory method-pack guidance. It helps agents find the
smallest stable owner, but it does not override user instructions, project
authority docs, compatibility evidence, or completion verification.
