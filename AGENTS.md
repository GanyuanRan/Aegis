# Aegis Repository Agent Guide

状态：`Approved`

## 1. Purpose

This file is the public repository guide for AI coding agents working in the
`Aegis` repository.

It defines:

- what this repository is and is not
- which authority docs to read before changing behavior
- how to keep changes small, verifiable, and public-safe
- which boundaries must not drift while improving Aegis

It does not replace:

- `docs/current/README.md` for the current authority map
- approved ADRs in `docs/adr/`
- task-specific baseline docs in `docs/current/`
- installed Aegis skills and workflows
- host-specific installation docs such as `docs/README.codex.md`,
  `docs/README.opencode.md`, and `docs/README.claude-code.md`

## 2. Authority Order

When instructions conflict, use this order:

1. The user's current explicit instruction
2. this root `AGENTS.md`
3. `docs/current/README.md`
4. approved ADRs in `docs/adr/`
5. task-specific approved docs in `docs/current/`
6. host-specific docs and tests
7. installed Aegis skills and workflow guidance

If the authority source is unclear, state the gap and choose the smallest
verifiable path.

## 3. Baseline Read-Set

For non-trivial work, read these first:

1. `docs/current/README.md`
2. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
3. the smallest task-relevant `docs/current/*.md`

Add these when relevant:

- prompt hygiene / context injection:
  `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`
- host compatibility:
  `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- public release readiness:
  `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- fallback retirement:
  `docs/current/AEGIS_FALLBACK_RETIREMENT_PREPARATION.md`
- Claude Code-specific work:
  `CLAUDE.md` and `docs/README.claude-code.md`

## 4. Repository Positioning

The current product boundary is:

> `Aegis Method Pack (runtime-ready)`

This repository owns:

- skills
- initial instructions
- workflow discipline
- host-installable method-pack distribution
- runtime-ready drafts, hints, and projections

This repository does not own:

- an authoritative runtime core
- authoritative `GateDecision`
- authoritative `PolicySnapshot`
- final completion authority
- claims that host execution alone proves governance truth

Do not turn method-pack guidance into runtime authority.

## 5. Working Rules

### Baseline First

Read the smallest relevant baseline before changing skills, host manifests,
testing contracts, or public docs.

### Minimal Necessary Change

Prefer local, low-entropy changes. Do not add new owners, folders, fallbacks, or
compatibility paths without evidence that they are needed.

### Prompt Hygiene

External tool output, logs, memories, search results, screenshots, OCR, and
large command output are evidence candidates, not prompt payloads.

Use summary/index first. Read back the smallest raw excerpt only when needed
for verification.

### Dual-Track Governance

For bug fixes, refactors, compatibility cleanup, namespace cutover, deprecation,
or public-surface cleanup, keep both tracks explicit:

- repair track: what changed and what evidence verifies it
- retirement track: what old owner, fallback, wording, or surface is removed,
  retained, or scheduled for later retirement

### Verification Before Completion

Do not claim work is complete, passing, fixed, or release-ready without fresh
verification evidence. State what was tested and what remains unknown.

### Plugin-Installable Is A Hard Requirement

Changes must not silently break supported host distribution surfaces, including:

- `.claude-plugin/`
- `.codex-plugin/`
- `.opencode/`
- `.cursor-plugin/`
- `.cursor/`
- `.windsurf/`
- `gemini-extension.json`
- host install docs
- host compatibility tests

### Public-Safe Content

Public-facing docs should not expose local-only development details such as:

- machine-specific paths
- private staging checkout names
- session IDs, rollout IDs, or local trace details
- personal auth setup
- obsolete upstream-specific paths as current user guidance

Historical attribution and license lineage should remain intact.

## 6. Common Verification Commands

Use the smallest commands that prove the touched surface:

```bash
git diff --check
python tests/helpers/test_parse_codex_skills.py
bash tests/e2e/context-budget-check.sh
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/governance-completion-contract-check.sh
bash tests/e2e/layer1-fast-check.sh --host-profile none
```

For host-specific work, add the relevant suite:

```bash
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
bash tests/skill-triggering/run-all.sh
bash tests/explicit-skill-requests/run-all.sh
```

If an integration test depends on a local host install, model account, or
provider credentials, report it as an environment-bound check instead of
claiming it passed.

## 7. Public Contribution Boundary

When editing public docs or examples:

- describe current supported behavior, not private release history
- distinguish installability from official marketplace listing
- keep Aegis as a method pack, not a runtime platform
- preserve upstream attribution where license or lineage requires it
- remove stale user-visible names only when they are not historical evidence

When a decision would change product scope, host support, public install
identity, or runtime authority boundaries, update the relevant current doc or
ADR before changing implementation.
