# CLAUDE.md

This file provides Claude Code-specific guidance for working in the Aegis
repository.

For repository-wide rules, read `AGENTS.md` first. For the current authority
map, read `docs/current/README.md`.

## Project Overview

`Aegis` is a zero-dependency method-pack plugin for AI coding agents. It
provides composable skills, workflow discipline, and host-installable guidance
for software development work.

Aegis is structured as a multi-harness plugin:

- Claude Code
- OpenAI Codex
- OpenCode
- Cursor
- Windsurf
- Gemini CLI
- CodeBuddy
- DeepSeek-TUI
- Trae
- Kimi Code CLI
- Warp (terminal host, no adapter needed)

Current product boundary:

> `Aegis Method Pack (runtime-ready)`

Aegis produces workflow guidance, drafts, hints, projections, and verification
evidence. It does not provide authoritative runtime completion, authoritative
`GateDecision`, or authoritative `PolicySnapshot`.

## Authority Read Order

For non-trivial work:

1. `AGENTS.md`
2. `docs/current/README.md`
3. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`
4. the smallest task-relevant `docs/current/*.md`
5. host-specific docs, when relevant

For Claude Code installation and plugin behavior, also read:

- `docs/README.claude-code.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `docs/windows/polyglot-hooks.md` for Windows hook behavior

## Key Design Constraints

- **Zero dependencies:** no npm packages or third-party services in core plugin
  logic.
- **Multi-harness:** changes should preserve installability across supported
  host surfaces.
- **Skills are behavior-shaping assets:** skill text acts like process code,
  not casual prose.
- **Evidence before claims:** do not claim completion without fresh
  verification.
- **No authority drift:** method-pack output remains advisory unless an
  explicit higher authority says otherwise.
- **Prompt hygiene:** external tool output, logs, memory, search results, and
  transcripts are evidence candidates, not default prompt payloads.

## Repository Layout

```text
.
├── skills/<name>/SKILL.md        # composable agent skills
├── commands/<name>.md            # host command prompts
├── agents/                       # agent definition prompts
├── hooks/                        # Claude Code hooks
├── scripts/                      # maintenance scripts
├── tests/                        # host and workflow tests
├── .claude-plugin/               # Claude Code plugin manifest
├── .codex-plugin/                # Codex plugin manifest
├── .opencode/                    # OpenCode integration
├── .cursor-plugin/               # Cursor plugin manifest
├── docs/adr/                     # architecture decisions
├── docs/current/                 # current authority and baseline docs
├── docs/windows/                 # Windows host compatibility notes
└── AGENTS.md                     # repository-wide agent guide
```

## Skill Format

Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter:

In this repository, `skills/<name>/SKILL.md` is the canonical source layout.
At runtime, hosts may load installed or generated views rather than the current
checkout.

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions]
---
```

Rules:

- `name`: letters, numbers, and hyphens only.
- `description`: starts with `Use when...`, describes triggering conditions,
  and does not summarize the workflow.
- Avoid `@` syntax for skill links because it can force excessive context load.
- See `skills/writing-skills/SKILL.md` for the complete skill authoring guide.

## Common Commands

Version management:

```bash
bash scripts/bump-version.sh
```

Codex plugin sync:

```bash
bash scripts/sync-to-codex-plugin.sh
```

Fast verification:

```bash
git diff --check
python tests/helpers/test_parse_codex_skills.py
bash tests/e2e/layer1-fast-check.sh --host-profile none
```

Boundary and context checks:

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/context-budget-check.sh
bash tests/e2e/governance-completion-contract-check.sh
```

OpenCode compatibility:

```bash
bash tests/opencode/run-tests.sh
bash tests/opencode/run-tests.sh --integration
```

Skill-triggering tests:

```bash
AEGIS_TEST_CLI=claude bash tests/skill-triggering/run-test.sh <skill-name> tests/skill-triggering/prompts/<name>.txt
bash tests/skill-triggering/run-all.sh
```

Explicit skill request tests:

```bash
AEGIS_TEST_CLI=claude bash tests/explicit-skill-requests/run-test.sh <skill-name> tests/explicit-skill-requests/prompts/<name>.txt
bash tests/explicit-skill-requests/run-all.sh
```

Claude Code integration tests can take 10-30 minutes and require a working
Claude Code environment:

```bash
cd tests/claude-code
./test-subagent-driven-development-integration.sh
```

## Claude Code Notes

- Claude Code plugin metadata lives in `.claude-plugin/`.
- Hooks live in `hooks/`.
- On Windows, hook commands should use the documented wrapper strategy in
  `docs/windows/polyglot-hooks.md`.
- Do not hard-code private machine paths, local session IDs, or personal auth
  details in public docs or fixtures.

## Development Guardrails

### Baseline First

Read current authority docs before modifying skills, host manifests, public
installation docs, or verification contracts.

### Dual-Track Closure

For bug fixes, cleanup, compatibility work, namespace changes, deprecations, or
public-surface changes, final reporting must include:

- repair track
- retirement track
- residual risk
- verification evidence

### Prompt Hygiene

When logs, transcripts, memories, search results, or tool outputs shape the
work, summarize first and read back only the smallest needed raw excerpt.

If prompt hygiene affects the conclusion, final reporting should identify:

- evidence used
- large payloads not loaded
- confidence
- next evidence needed

### Public-Safe Docs

Public docs should describe current supported behavior and stable contribution
rules. Keep private staging history, local machine details, and transient
phase-management notes in current records only when they are genuine historical
evidence.

## Current Status

Do not infer current release, compatibility, or production readiness from this
file. Use these authority docs instead:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
