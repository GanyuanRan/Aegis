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

The optional mode is:

```toml
tdd_mode = "off"
```

`off` disables automatic TDD routing. It does not delete tests, prevent explicit
user or project TDD requests, or weaken `verification-before-completion`.

On hosts that rely on native skill discovery rather than an Aegis bootstrap
router, `off` does not by itself override the host's own semantic matcher.
Those hosts need narrow automatic trigger wording for
`test-driven-development`, or a host profile that hides automatic TDD entry
points.

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

When implementation risk is clear and behavior needs regression protection,
choose `strict`.

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
AEGIS_TDD_MODE=off opencode
AEGIS_TDD_MODE=off claude
```

PowerShell:

```powershell
$env:AEGIS_TDD_MODE = "off"
opencode
# or: claude
```

Read priority:

1. `AEGIS_TDD_MODE`
2. `~/.config/aegis/config.toml`
3. Default `auto`

Restart, reload, or open a new host session after changing the mode. Existing
host sessions usually do not inherit changed environment variables or config.

## 5. Boundary

TDD Mode is method-pack guidance, not authoritative runtime policy.

It must not be packaged as an authoritative `GateDecision`, `PolicySnapshot`, or
completion authority. `off` only disables automatic test-first discipline;
completion still needs fresh evidence from `verification-before-completion`.
