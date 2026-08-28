# Aegis TDD Mode

Status: `Approved`

## 1. Scope

This document defines `TDD Mode` for `Aegis Method Pack`.

TDD Mode controls automatic test-first discipline. It does not control
completion evidence, release readiness, merge approval, or a future runtime
core.

## 2. Modes

The default mode is:

```toml
tdd_mode = "off"
```

`off` disables automatic TDD routing by default. It does not delete tests,
prevent explicit user or project TDD requests, or weaken
`verification-before-completion`. In `off`, owner workflows must not
automatically select `TDD Route: strict`, load `test-driven-development`, or
require RED / GREEN from risk wording. A plan or execution review may record
`TDD Route: Mode: off / Decision: skipped` to make that non-strict boundary
auditable; the record is not TDD activation. Those workflows still choose
proportional reproduction, regression, and verification. An explicit
user/project request for `TDD Route: strict`, `strict TDD`, `test-first`, or
`RED / GREEN / REFACTOR` remains sufficient to authorize strict TDD.

Users can enable automatic TDD routing when they want it:

```toml
tdd_mode = "auto"
```

`auto` lets Aegis choose a `TDD Route` before implementation:

Route decisions are `strict`, `light`, and `skipped`.

- `strict`: use `test-driven-development`; write a failing test before
  production code, then RED / GREEN / REFACTOR.
- `light`: do not force strict TDD; use the smallest verification that proves
  the tiny change.
- `skipped`: do not use TDD because the task is read-only, docs-only,
  generated, throwaway exploratory work, or otherwise not a code behavior
  implementation.

`skipped` means “skip strict TDD,” not “skip testing.” Test evidence has three
different roles:

- **diagnostic reproduction** establishes or isolates a failure and may be a
  failing test, an existing test, instrumentation, or a manual reproduction;
  it is evidence, not a RED gate;
- **post-change regression** proves the selected repair after the minimum
  change and remains appropriate with `off` mode;
- **strict RED test** is the failing test that blocks production-code edits and
  is required only when `TDD Route: strict` is explicitly recorded.

An approved implementation plan does not itself authorize the third role.

On hosts that rely on native skill discovery rather than an Aegis bootstrap
router, `off` does not by itself override the host's own semantic matcher.
Those hosts need narrow automatic trigger wording for
`test-driven-development`, anchored to literal conversation markers such as
`TDD Route: strict`, `strict TDD`, `test-first`, or `RED / GREEN / REFACTOR`,
or a host profile that hides automatic TDD entry points. If the skill loads
without one of those markers while `off` is active, the skill body should exit
instead of inferring strict TDD from generic risky-code wording.

## 3. Route Heuristics

Use `strict` in `auto` mode when the change touches behavior, a bug fix, shared
or core logic, API or data contracts, persistence, permissions, migrations,
producer / consumer boundaries, or meaningful regression risk.

Use `light` when the task is tiny, low-risk, single-owner, and has an obvious
readback or command check, such as a wording edit, simple config adjustment, or
mechanical cleanup with no behavior change.

Use `skipped` when TDD does not fit the task shape: read-only diagnosis,
pure explanation, comment-only edits, generated or vendored files, throwaway
spikes, or environment-bound checks where automated tests cannot be written in
the current slice.

In `off`, use `Decision: skipped` for normal plan and execution readbacks
unless an explicit user/project strict request overrides it. Do not infer
`strict` from bug, architecture, contract, shared-module, or risk wording.

In `auto`, when implementation risk is clear and behavior needs regression
protection, choose `strict`.

Route precedence is explicit:

1. A current user/project instruction that explicitly requires strict or
   test-first TDD selects `strict`.
2. A higher-priority current instruction that explicitly forbids TDD blocks
   strict TDD, but does not weaken proportional regression or completion
   verification.
3. In `off`, select `skipped` unless rule 1 applies.
4. In `auto`, any strict-risk signal selects `strict`. Strict signals use OR
   semantics: one supported signal is enough.
5. `light` is valid only when the task is tiny, low-risk, single-owner, has no
   behavior change or strict-risk signal, and has an obvious focused check.
   Light eligibility uses AND semantics: every condition must hold.
6. If the task or risk boundary is still unknown, return to clarification,
   debugging, or planning. Unknown is not evidence for `light`.

In `auto`, absence of an explicit user TDD request is never evidence for
`light`. A high-risk implementation where strict TDD is currently infeasible
must use a supported `skipped` exception with the blocker and compensating
verification recorded; it must not be relabeled `light`.

### 3.1 Route Ownership And Consumption

The workflow that first authorizes production-source edits owns route
selection for that slice:

- `using-aegis` may select the route for a direct low-complexity slice;
- `writing-plans` selects it before decomposing planned implementation work;
- `systematic-debugging` selects it after Change Necessity and before the
  first repair edit;
- `executing-plans`, `test-driven-development`, and subagent workflows consume
  and validate the recorded route; they do not silently reclassify it.

An invalid or missing `auto` decision returns to the selecting workflow. It
must not be repaired as `light` merely to keep execution moving.

Every implementation route record uses this shape:

```text
TDD Route:
- Mode: auto | off
- Decision: strict | light | skipped
- Strict authority: explicit user/project request | recorded auto decision | not applicable
- Strict signals:
- Light eligibility:
- TDD-fit exception:
- Test posture: diagnostic reproduction | post-change regression | strict RED test
- Reason:
- Verification:
```

When business behavior, acceptance, success evidence, or user-visible
completion is unclear, route to `brainstorming` or `writing-plans` before TDD.

## 4. Configuration

User-local config path:

```text
~/.config/aegis/config.toml
```

Windows:

```text
%USERPROFILE%\.config\aegis\config.toml
```

From the installed method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py tdd-mode auto
python scripts/aegis-doctor.py tdd-mode off
```

Temporary environment override:

```bash
AEGIS_TDD_MODE=auto opencode
AEGIS_TDD_MODE=auto claude
# or explicitly keep the default disabled state:
AEGIS_TDD_MODE=off opencode
```

PowerShell:

```powershell
$env:AEGIS_TDD_MODE = "auto"
opencode
# or: claude
```

Read priority:

1. `AEGIS_TDD_MODE`
2. `~/.config/aegis/config.toml`
3. Default `off`

Restart, reload, or open a new host session after changing the mode. Existing
host sessions usually do not inherit changed environment variables or config.

On Codex's native-direct-skill path, the Aegis config file is not itself a
model-facing instruction source. Use the Codex host guide's `--agents-md`
command shape to project the selected mode into the managed Aegis block in
Codex's global `AGENTS.md`. That projection makes the mode visible to the
method workflow; it does not control the host's semantic skill matcher or grant
runtime authority. Generic hook-host configuration may use `--no-agents-md`.

## 5. Boundary

TDD Mode is method-pack guidance, not authoritative runtime policy.

It must not be packaged as an authoritative `GateDecision`, `PolicySnapshot`, or
completion authority. `off` only disables automatic test-first discipline;
completion still needs fresh evidence from `verification-before-completion`.
