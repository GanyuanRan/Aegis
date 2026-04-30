# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aegis** is a zero-dependency plugin that provides a complete software development methodology for AI coding agents. It is structured as a multi-harness plugin (Claude Code, Cursor, OpenAI Codex, OpenCode, Gemini CLI) and is installable from multiple marketplaces.

This fork (`Aegis`) builds on Aegis with evidence-driven governance, ADD-style authority boundaries, and the TLREF execution framework. See `AGENTS.md` for fork-specific guardrails and `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md` for the current method-pack vs runtime-core boundary.

### Key Design Constraints

- **Zero dependencies**: No npm packages, no third-party services in core plugins
- **Multi-harness**: Must remain installable on all supported platforms
- **Skills not prose**: Skill content is behavior-shaping code, not documentation
- **TDD for skills**: Every skill change requires adversarial eval evidence

## Codebase Architecture

```
.
├── skills/<name>/SKILL.md    # Composable agent skills (16 skills)
├── commands/<name>.md        # Slash commands (brainstorm, write-plan, execute-plan)
├── agents/                   # Agent definition prompts (code-reviewer)
├── hooks/                    # Claude Code hooks (session-start, etc.)
├── scripts/                  # Utility scripts (version bump, codex sync)
├── tests/                    # Test suites per harness
│   ├── claude-code/          #   Integration tests with real Claude sessions
│   ├── explicit-skill-requests/  #   Explicit skill invocation tests
│   ├── skill-triggering/     #   Automatic skill triggering tests
│   ├── opencode/             #   OpenCode compatibility tests
│   ├── helpers/              #   Shared test utilities
│   └── subagent-driven-dev/  #   SDD-specific tests
├── .claude-plugin/           # Claude Code plugin manifest
├── .cursor-plugin/           # Cursor plugin manifest
├── .codex-plugin/            # Codex CLI plugin manifest
├── .opencode/                # OpenCode integration
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   ├── current/              # Aegis baseline & governance docs
│   └── aegis/          # Plans & spec documents
├── assets/                   # App icon, branding
└── AGENTS.md                 # Aegis fork development guardrails
```

### Skills Format

Each skill lives in `skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name-with-hyphens
description: "Use when [specific triggering conditions] - describes WHEN to use, NOT what it does"
---
```

Key frontmatter rules:
- `name`: Letters, numbers, hyphens only
- `description`: Starts with "Use when...", third-person, no workflow summary (Claude will follow the description instead of reading the skill body)
- Max 1024 chars total, keep under 500 if possible
- See `skills/writing-skills/SKILL.md` for the complete guide

### Multi-Harness Version Management

Version is centrally managed in `.version-bump.json` which syncs to:
- `package.json` → `version`
- `.claude-plugin/plugin.json` → `version`
- `.cursor-plugin/plugin.json` → `version`
- `.codex-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins.0.version`
- `gemini-extension.json` → `version`

## Commands

### Version Management
```bash
bash scripts/bump-version.sh          # Bump version across all plugin manifests
```

### Codex Plugin Sync
```bash
bash scripts/sync-to-codex-plugin.sh  # Sync skills to Codex format
```

### Testing

**Skill-triggering tests** (tests if skills auto-activate from natural prompts):
```bash
# Test auto-triggering for a specific skill
AEGIS_TEST_CLI=claude bash tests/skill-triggering/run-test.sh <skill-name> tests/skill-triggering/prompts/<name>.txt

# Run all skill-triggering tests
bash tests/skill-triggering/run-all.sh
```

**Explicit skill request tests** (tests if skills work when explicitly named):
```bash
# Test explicit invocation for a specific skill
AEGIS_TEST_CLI=claude bash tests/explicit-skill-requests/run-test.sh <skill-name> tests/explicit-skill-requests/prompts/<name>.txt

# Run all explicit-request tests
bash tests/explicit-skill-requests/run-all.sh
```

**Codex CLI smoke tests**:
```bash
AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh <skill-name> tests/skill-triggering/prompts/<name>.txt
AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh <skill-name> tests/explicit-skill-requests/prompts/<name>.txt
```

**OpenCode compatibility**:
```bash
# Base suite (plugin structure, bootstrap wiring)
bash tests/opencode/run-tests.sh

# Integration suite (requires runnable OpenCode CLI)
bash tests/opencode/run-tests.sh --integration
```

**Integration tests** (real Claude Code sessions, 10-30 min):
```bash
cd tests/claude-code
./test-subagent-driven-development-integration.sh
```

**Token analysis**:
```bash
python3 tests/claude-code/analyze-token-usage.py ~/.claude/projects/<session-file>.jsonl
```

### Test environment requirements
- Tests must run from the **aegis plugin root directory**
- Claude Code must be `claude` on PATH
- For Codex tests: `CODEX_CMD=/path/to/codex` overrides
- `~/.claude/settings.json` must have `"aegis@aegis-dev": true` in `enabledPlugins`
- Headless tests use `--permission-mode bypassPermissions` and `--allowed-tools=all`

## Skills Development Workflow

Skills follow the `writing-skills` skill's RED-GREEN-REFACTOR cycle (TDD for process docs):

1. **RED**: Run baseline test WITHOUT the skill → document failure rationalizations
2. **GREEN**: Write minimal skill content addressing those specific failures
3. **REFACTOR**: Close loopholes, add rationalization tables, re-test

Key principles:
- "No skill without a failing test first" — untested skills are not acceptable
- Skill descriptions must NEVER summarize workflow (causes Claude to skip reading the body)
- Cross-reference: `**REQUIRED SUB-SKILL:** Use aegis:test-driven-development`
- No `@` syntax for skill links (forces 200k+ context load)
- Each skill has: overview, when to use, implementation, common mistakes, red flags

## Fork Governance (Aegis)

This is an Aegis fork. Key constraints from `AGENTS.md`:

- **Dual-track**: Bug fixes and architecture changes require both a fix track and a retire track (default delete, evidence required to retain)
- **No authority drift**: This repo outputs drafts/hints/advisories only, NOT authoritative GateDecisions
- **Baseline first**: Read baseline docs before modifying skills
- **Plugin-installable is hard requirement**: Don't break multi-harness distribution

### Current Fork Status

- Current approved repo shape: `Aegis Method Pack (runtime-ready)`
- Phase status as of `2026-04-27`: `Phase 5 / Runtime-ready Hardening complete within current method-pack scope`
- Latest completed slice: `Phase 5 overall closeout (method-pack scope)`
- OpenCode runtime closeout is recorded in `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
- Phase 5 E2E closeout is recorded in `docs/current/AEGIS_PHASE5_E2E_COMPLETION_RECORD.md`
- Phase 5 overall closeout is recorded in `docs/current/AEGIS_PHASE5_COMPLETION_RECORD.md`
- Production-strengthening follow-up is tracked in `docs/current/AEGIS_PRODUCTION_READINESS_GAPS.md`

For current host compatibility facts, prefer these documents in order:

1. `docs/current/README.md`
2. `docs/current/AEGIS_PHASE4_COMPLETION_RECORD.md`
3. `docs/README.opencode.md`
4. `docs/testing.md`

Reading order for fork contributors: `docs/current/README.md` → `AGENTS.md` → `ADR-0001` → task-specific docs → `CLAUDE.md` (for upstream PR rules).
