# Contributing to Aegis Method Pack

Thanks for your interest in contributing.

This repository currently represents:

> `Aegis Method Pack (runtime-ready)`

It does **not** represent the full `Aegis Platform`, and it does **not** provide runtime-core authority.

Before opening any PR, read in this order:

1. `docs/current/README.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
4. task-relevant files in `docs/current/`
5. `AGENTS.md`

## What belongs in this repository

Good contributions for this repository include:

- method-pack skill improvements
- host installation and testing docs improvements
- distribution skeleton fixes
- verification, compatibility, and documentation improvements
- bug fixes that preserve the current method-pack boundary

Changes that do **not** belong here include:

- introducing runtime-core authority
- adding authoritative `GateDecision` behavior
- promoting host-specific implementation details into method-pack baseline
- project-specific or team-specific workflow logic that should live in another plugin or repo

## Contribution principles

Please keep these constraints in mind:

1. **Baseline first**
   - read the current baseline before changing behavior
2. **Minimal necessary change**
   - keep edits narrow and owner-oriented
3. **Evidence before claims**
   - do not say something is fixed or complete without fresh verification
4. **No authority drift**
   - this repo outputs drafts, hints, advisories, and verification evidence
5. **Plugin-installable is a hard requirement**
   - do not break multi-host distribution capability

## Issue first

For non-trivial changes, please open or link an issue before submitting a PR.

Good issue descriptions usually include:

- the problem being solved
- the current user impact
- why the change belongs in method-pack scope
- what alternatives were considered

## Pull request expectations

All PRs should:

1. solve one coherent problem
2. describe the real problem, not just the implementation
3. explain why the change belongs in this repository
4. include verification evidence
5. avoid bundling unrelated edits

Use the PR template in `.github/PULL_REQUEST_TEMPLATE.md`.

## Testing expectations

At minimum, run the most relevant checks for your change.

Common commands:

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

Read `docs/testing.md` for the current testing owners and host-specific notes.

If a check is not runnable in your environment, say so clearly in the PR.

## Skills changes

If you modify skills or other behavior-shaping content:

- treat that content as code, not prose
- preserve cross-host behavior unless you have strong evidence
- include adversarial evaluation evidence where appropriate

Relevant references:

- `skills/writing-skills/SKILL.md`
- `skills/verification-before-completion/SKILL.md`

## Review boundary

Maintainers may decline changes that:

- expand scope toward full platform claims
- add host-specific special cases without a retirement plan
- weaken current verification standards
- introduce project-specific logic into the shared method pack

## Security

Do not report security-sensitive issues through public issues.

Use `SECURITY.md` for the correct reporting path.
