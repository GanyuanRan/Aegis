# Aegis ADR Auto Backfill

Status: `Approved`

## 1. Purpose

ADR Auto Backfill is the Aegis method-pack workflow for turning completed
engineering work into durable architecture memory.

It prevents `docs/aegis/adr/` from becoming an empty placeholder while avoiding
the opposite failure mode: asking users to manually approve every architecture
record.

ADR Auto Backfill is evidence-led:

```text
completed work evidence
  -> ADR trigger check
  -> create / amend / supersede / skip
  -> baseline sync check
```

It is not a runtime gate, not an authoritative `GateDecision`, and not final
`completion authority`.

---

## 2. Position

ADRs answer:

> Why did this architecture decision become the chosen direction?

Baseline snapshots answer:

> What is the current architecture state after the decision landed?

These two records are linked, but they are not interchangeable:

- ADRs record decision context, alternatives, consequences, and trade-offs.
- Baselines record current owners, contracts, dependency direction, commands,
  compatibility boundaries, and known risks.
- An ADR may require a baseline update.
- A baseline update may cite an ADR.
- A baseline must not silently absorb an intentional architecture decision
  without a decision record when ADR trigger conditions are met.

---

## 3. Source Priority

ADR Auto Backfill uses the strongest available evidence source:

1. `docs/aegis/work/YYYY-MM-DD-<slug>/`
   - preferred source when a task created work records
   - read `proof-bundle.md`, `drift-check-draft.json`,
     `impact-statement-draft.json`, evidence bundles, and reflection notes
2. `docs/aegis/plans/YYYY-MM-DD-<topic>.md`
   - fallback when there is no work record, but the plan reflects completed
     execution and verification evidence is available
3. `docs/aegis/specs/YYYY-MM-DD-<topic>-brief.md` or
   `docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`
   - fallback when there is no work or plan record, but the spec describes a
     completed and verified decision
4. Current repository evidence
   - git diff, commits, tests, release notes, current docs, and command output
     may support the backfill decision

Do not create an accepted architecture memory from a speculative spec or plan
that has not been implemented or otherwise verified.

---

## 4. Trigger Conditions

Create, amend, or supersede an ADR only when completed work has durable
architecture value.

ADR Auto Backfill SHOULD trigger when the completed work changes or records one
of these surfaces:

- canonical owner or ownership map
- public API, schema, artifact shape, or behavior contract
- dependency direction or allowed cross-module relationship
- source-of-truth owner
- host compatibility strategy or install/discovery contract
- method-pack vs runtime-core boundary
- runtime-ready artifact boundary or evidence model
- repair plus retirement decision that keeps or removes a durable fallback,
  adapter, compatibility path, or duplicate owner
- intentional architecture-scoped Implementation Drift that is accepted and
  landed
- release or distribution strategy that future contributors would otherwise
  misread

ADR Auto Backfill MUST NOT trigger for:

- simple wording edits
- ordinary README link cleanup
- routine release note edits
- low-risk single-file changes
- tests that only improve coverage without changing architecture behavior
- bug fixes that restore the existing baseline without changing architecture
- implementation details with no durable trade-off
- decisions that fail the ADR creation gate

The ADR creation gate remains:

1. reversing the decision later would be costly
2. the decision would be surprising without context
3. real alternatives existed and a trade-off was made

---

## 5. Route Selection

Before writing an ADR, choose the correct owner surface:

1. If the target project has an established formal ADR system, write or propose
   the ADR there.
2. If the target project has no formal ADR system but has an Aegis workspace,
   write the method-pack ADR under `docs/aegis/adr/`.
3. If the work changes the Aegis Method Pack repository itself, use this
   repository's formal `docs/adr/` when the decision is repository-authoritative.
4. If the work only needs task-local evidence, keep it in `docs/aegis/work/`
   and do not promote it.

Do not duplicate the same decision into both a formal ADR directory and
`docs/aegis/adr/` unless one record explicitly references the other as a mirror
or local method-pack projection.

---

## 6. Action Selection

ADR Auto Backfill chooses one action:

### 6.1 Create

Create a new ADR when no existing ADR owns the durable decision.

### 6.2 Amend

Amend an existing ADR when the original decision still stands and the completed
work adds implementation evidence, compatibility notes, or consequences.

Accepted decision text should not be rewritten to hide history.

### 6.3 Supersede

Create a superseding ADR when the completed work replaces a previous durable
decision.

The new ADR must link to the prior ADR. The prior ADR should be marked or
referenced as superseded when that is safe within the project's ADR convention.

### 6.4 Skip

Skip ADR creation when evidence is insufficient, the decision is reversible,
or the source is only speculative.

The skip reason should be recorded in reflection, proof bundle, or final output
for medium/high work.

---

## 7. Minimum ADR Shape

An auto-backfilled ADR should include:

- Status
- Source evidence
- Context
- Decision
- Alternatives considered
- Consequences
- Compatibility boundary
- Retirement impact
- Baseline sync
- Evidence references
- Supersedes / amended-by links when applicable

Use status values that describe evidence source instead of pretending to grant
runtime authority:

- `recorded-from-work`
- `recorded-from-plan`
- `recorded-from-spec`
- `amended`
- `superseded`

Projects with their own ADR convention may map these states to local terms.

---

## 8. Baseline Sync

ADR and baseline updates are linked.

After any ADR create, amend, or supersede action, run a baseline sync check.

Create or update a baseline snapshot when the ADR changes or confirms any of:

- ownership map
- contract inventory
- dependency direction convention
- source-of-truth owner
- compatibility boundary
- host support status
- runtime-ready artifact boundary
- retained fallback, adapter, or retirement schedule

The sync direction is:

```text
ADR records why
baseline records current state
```

If an ADR changes architecture state but no baseline update is made, the ADR
must state why the baseline remains valid.

If a baseline update reflects an intentional architecture decision, it must cite
the ADR or explain why ADR Auto Backfill skipped the decision.

---

## 9. Workflow Integration

ADR Auto Backfill belongs near completion, not at the beginning of design.

Skill responsibilities:

- `brainstorming`
  - may mark ADR signals in the design or spec
  - should not create accepted architecture memory from unexecuted ideas
- `writing-plans`
  - should preserve ADR signals, source refs, compatibility boundaries, and
    alternatives so completion can backfill later
- `long-task-continuation`
  - should keep work evidence, drift checks, and proof bundles usable as the
    preferred ADR source
- `recording-architecture-decisions`
  - should own direct ADR, architecture decision record, decision log, and
    baseline sync closure requests
  - must run the ADR creation gate, choose create / amend / supersede / skip,
    choose the owner surface, and close baseline sync before any writeback
  - when the chosen owner surface is target-project `docs/aegis/adr/`, should
    route create / amend / supersede writeback through
    `aegis-workspace.py new-adr`, `amend-adr`, or `supersede-adr`, then run
    `aegis-workspace.py check --root <target-project-root>`
  - does not replace completion verification and does not grant completion
    authority
- `verification-before-completion`
  - should run the ADR Auto Backfill check before final completion claims for
    medium/high work that touched architecture surfaces
  - should route create / amend / supersede actions, or needed / unknown
    baseline sync, through `recording-architecture-decisions`
  - when helper-backed ADR writeback happens in a target project, should keep
    the workspace helper `check --root` result inside the completion evidence
- `requesting-code-review`
  - should flag missing ADR or baseline sync when the diff shows durable
    architecture decisions
  - should flag missing `recording-architecture-decisions` handoff when ADR
    action or baseline sync closure is in scope

---

## 10. Non-Goals

ADR Auto Backfill does not:

- ask the user to manually approve every ADR
- turn Aegis into a runtime authority system
- decide that evidence is sufficient for final completion
- replace existing project ADR conventions
- rewrite accepted ADR history silently
- create ADRs for every plan, spec, or work record
- make `docs/aegis/adr/` the canonical authority when a project already has a
  formal ADR owner

---

## 11. Implementation Boundary

Current baseline behavior:

- ADR Auto Backfill is defined as a method-pack workflow requirement.
- Helper-backed ADR creation, amendment, and supersession now exist as
  zero-dependency support commands for target-project `docs/aegis/adr/`.
- `aegis-workspace.py new-adr` creates an indexed workspace ADR with the
  minimum required sections.
- `aegis-workspace.py amend-adr` appends an amendment record without rewriting
  accepted ADR history.
- `aegis-workspace.py supersede-adr` creates a new ADR, links it to the prior
  ADR, and marks the prior ADR as superseded.
- Helper checks validate ADR filename shape, required sections, index coverage,
  and recognizable workspace JSON sidecars.
- Helper checks must not decide architecture truth or completion authority.

Current helper support commands:

```text
aegis-workspace.py new-adr
aegis-workspace.py amend-adr
aegis-workspace.py supersede-adr
```

Any implementation must preserve the method-pack/runtime-core boundary defined
by `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`.
