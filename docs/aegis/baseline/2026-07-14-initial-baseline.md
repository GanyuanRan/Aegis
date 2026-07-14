# Aegis Repository Initial Workspace Baseline

Date: `2026-07-14`
Status: `initial dual-baseline snapshot`

## 1. Purpose

This snapshot bootstraps the repository-local `docs/aegis/` workspace without
replacing the approved public current baseline under `docs/current/`.

Use it to keep task-local specs, plans, checkpoints, and evidence aligned with
the repository's existing authority documents.

## 2. Workspace Structure

- `skills/` is the canonical method-pack workflow source.
- `tests/` contains structural, workflow-quality, trigger-health, host, and
  behavior-oriented verification surfaces.
- `scripts/` contains installation, workspace, release, and validation helpers.
- `docs/current/` contains the approved public current baseline.
- `docs/adr/` contains approved architecture decisions.
- `docs/aegis/` contains advisory task-local records; it is not current
  authority by itself.

## 3. Current Authority Surfaces

Authority order:

1. `AGENTS.md`
2. `docs/current/README.md`
3. approved ADRs in `docs/adr/`
4. task-relevant approved docs in `docs/current/`
5. host-specific docs and tests
6. installed Aegis skills and workflow guidance

## 4. Product / Requirement Baseline

### 4.1 Current Truth

- The repository is `Aegis Method Pack (runtime-ready)`.
- It owns skills, workflow discipline, host-installable distribution, and
  runtime-ready drafts, hints, and projections.
- It must remain useful across supported hosts while keeping simple tasks
  inexpensive.
- Workflow claims require evidence and must distinguish advisory method output
  from authoritative runtime decisions.

### 4.2 Non-negotiables

1. Do not turn method guidance into completion authority.
2. Do not silently break plugin-installable host surfaces.
3. Keep changes minimal, evidence-backed, and public-safe.
4. Preserve externally observable compatibility unless an approved decision
   explicitly changes it.

### 4.3 Product Non-goals

- Do not claim that the current repository is a complete runtime platform.
- Do not make every task pay the cost of a medium/high-risk workflow.

## 5. Architecture / Runtime Boundary Baseline

### 5.1 Current Truth

- `skills/` owns method behavior.
- Project current docs and ADRs own durable project truth.
- Host projections expose canonical skill content; they are not editable
  second owners.
- Workspace artifacts are advisory inputs and evidence trails.

### 5.2 Architecture Non-negotiables

1. Every workflow responsibility has one canonical owner.
2. Adapters, fallbacks, and projections do not acquire independent truth.
3. Old internal paths retire by default unless active external dependency
   evidence justifies compatibility retention.

### 5.3 Architecture Non-goals

- Do not create authoritative `GateDecision`, `PolicySnapshot`, or evidence
  sufficiency owners inside the method pack.
- Do not duplicate workflow contracts across skills when composition is
  sufficient.

## 6. Ownership / Contract Snapshot

- Task routing: `using-aegis`
- Debugging and repair-direction judgment: `systematic-debugging`
- Design/spec clarification: `brainstorming`
- Plan decomposition and execution handoff: `writing-plans`
- Plan execution: `executing-plans`
- Cross-session checkpoint and drift state: `long-task-continuation`
- Directional principle and owner falsification lens:
  `first-principles-review`
- Completion closeout aggregation: `verification-before-completion`

## 7. Current State and Risks

- Current skills contain strong one-turn owner, patch-shape, and retirement
  rules.
- Longitudinal execution still depends partly on the agent preserving and
  re-reading cumulative risk signals.
- Static contract tests can pass even when a real multi-turn execution does
  not carry enough state to trigger the intended stop condition.

## 8. Alignment Use

- Read the Product / Requirement Baseline for value, workflow behavior,
  acceptance, non-goals, and supported-host expectations.
- Read the Architecture / Runtime Boundary Baseline for owner, contract,
  source-of-truth, compatibility, and retirement decisions.
- Report `scope: both` when a workflow behavior change also moves an owner or
  runtime-ready boundary.

## 9. Compatibility Boundary

- Preserve current fast-path behavior for ordinary single-owner tasks.
- Preserve current host-installable distribution surfaces.
- Preserve the advisory Method Pack / future Runtime Core boundary.
