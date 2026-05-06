---
name: long-task-continuation
description: Use when a task is multi-step, may span context resets or sessions, uses subagents, or risks losing state before completion - keeps todo, checkpoint, resume, drift, and evidence discipline without granting completion authority
---

# Long Task Continuation

## Overview

Use this skill to keep long tasks checkpointed, resumable, drift-aware, and evidence-gated.

This is a protocol skill. It does not execute plans, dispatch subagents, run tests, or grant completion authority.

## Authority Boundary

Current owner:

- Method Pack protocol discipline

Not owned here:

- plan execution
- subagent dispatch
- host daemon / watchdog / automatic retry
- authoritative `GateDecision`
- evidence sufficiency final judgment
- completion authority

## When To Use

Use this skill when any of these are true:

- the task has multiple phases or more than one meaningful work slice
- the task may be interrupted, compacted, resumed, or handed off
- the task uses subagents
- the user explicitly asks for long-task continuity, resume safety, or avoiding drift
- the task changes architecture, contracts, shared workflows, or verification gates

For short direct answers or one-command checks, do not force this protocol.

## Required Artifacts

Maintain artifacts under `docs/aegis/work/YYYY-MM-DD-<slug>/`:

| Artifact | File | When |
|----------|------|------|
| TaskIntentDraft | `10-intent.md` | Start protocol |
| BaselineReadSetHint | `10-intent.md` (inline) | Start protocol |
| ImpactStatementDraft | `10-intent.md` (inline) | Start protocol |
| TodoCheckpointDraft | `20-checkpoint.md` | Each checkpoint |
| ResumeStateHint | `20-checkpoint.md` (inline) | Each pause/handoff |
| DriftCheckDraft | `20-checkpoint.md` (inline) | Per-slice protocol |
| EvidenceBundleDraft | `90-evidence.md` | Per-slice protocol |
| Reflection | `99-reflection.md` | Completion candidate |

For medium+ complexity tasks only. Low-complexity tasks skip work/.

These are draft / hint / projection inputs. They are not authoritative runtime records.

## Start Protocol

Before long-task execution:

1. State the requested outcome, scope, non-goals, and risk hints.
2. Identify baseline refs that must be read before changing files.
3. Create or update the todo map.
4. Create the first checkpoint:
   - current todo
   - active slice
   - completed todos
   - evidence refs
   - blocked-on items
   - next step
5. If baseline refs are missing, pause in `needs-baseline-readback`.

## Per-Slice Protocol

Before each work slice, restate:

1. current goal
2. current todo
3. intended edits
4. explicit non-edits
5. verification command or manual check

After each work slice, update:

1. completed todos
2. evidence refs
3. blockers
4. next step
5. drift check

If no fresh evidence exists, the state is `needs-verification` or `partial`.

## Resume Protocol

When resuming:

1. Read latest checkpoint.
2. Read latest resume hint if present.
3. Re-read original task intent.
4. Re-read required baseline refs.
5. Compare current worktree state with checkpoint claims.
6. If checkpoint, baseline, and worktree disagree, pause and ask for direction.

Never resume from memory alone.

## Drift Check

Answer these after each slice:

- Does the current work still serve the original task intent?
- Did the slice stay inside the compatibility boundary?
- Did any new owner, fallback, adapter, or branch appear?
- Is the retirement track still explicit?
- Did the evidence bundle grow enough to support the next claim?

Allowed decisions:

- `continue`
- `pause-for-user`
- `needs-baseline-readback`
- `needs-verification`
- `blocked`

Forbidden decisions:

- `gate-passed`
- `completion-granted`
- `authoritatively-safe`

## Completion Candidate Protocol

Before saying work is complete:

1. Use aegis:verification-before-completion.
2. Confirm every todo has a status.
3. Confirm blockers are resolved or externalized.
4. Confirm evidence refs cover the acceptance criteria.
5. Confirm drift check has no blocking state.
6. Assemble `GateInputPack` if useful.

Method Pack output is verified evidence and advisory judgment only. It is not authoritative completion.

## Minimal Reporting Shape

Use this shape for long-task updates:

- `TodoCheckpointDraft`: current todo, completed todos, active slice, next step
- `Evidence`: commands, files, logs, or manual checks
- `DriftCheckDraft`: scope, compatibility, retirement, decision
- `Risk / Unknown`: unresolved blockers or missing evidence
- `Next`: the next smallest safe action
