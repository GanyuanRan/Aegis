# Aegis Host Compatibility Matrix Snapshot

Status: `Reviewed`

## 1. Document Scope

This document records the current host compatibility snapshot of the `Aegis Method Pack`.

It answers:

- Which hosts have fresh evidence
- Which hosts only have structural goals without current fresh verification
- What is the reading order for the current compatibility verdict

It does not answer:

- Permanent support commitments for all hosts
- Complete platform-level runtime compatibility

---

## 2. Snapshot Date

The current snapshot is based on fresh evidence and current docs landed as of `2026-05-06`.

---

## 3. Current Verdict

### 3.1 Hosts With Fresh Evidence

| Host | Current Verdict | Evidence Owner |
| --- | --- | --- |
| `Codex` | Representative smoke mainline available; naive smoke under Git Bash still requires observation | `docs/testing.md`, `tests/skill-triggering/*`, `tests/explicit-skill-requests/*`, `docs/current/AEGIS_KNOWN_LIMITATIONS.md` |
| `OpenCode` | Base suite and integration closeout passed | `docs/testing.md`, `tests/opencode/*`, `docs/README.opencode.md` |

### 3.2 Hosts Without a Current Fresh Release Verdict

| Host | Current Status | Why Not Yet |
| --- | --- | --- |
| `Claude Code` | Has install guide and plugin skeleton; no current release-level fresh smoke verdict | `docs/README.claude-code.md` established, but real host regression is still deferred |
| `CodeBuddy` | Has `.codebuddy-plugin/` skeleton and native `SKILL.md` manual install instructions; no current release-level fresh smoke verdict | `docs/README.codebuddy.md` established; evidence from CodeBuddy skills/plugin docs and this repo's `.codebuddy-plugin/`; real host regression still deferred |
| `DeepSeek-TUI` | Native `SKILL.md` discovery supports manual installation; no current release-level fresh smoke verdict | `docs/README.deepseek-tui.md` established; evidence from DeepSeek-TUI README/source discovery contract; real host regression still deferred |
| `Trae` | Native `SKILL.md` discovery supports manual installation; no current release-level fresh smoke verdict | `docs/README.trae.md` established; evidence from Trae skills docs; real host regression still deferred |
| `Cursor` | Has `.cursor/INSTALL.md` install guide; no current release-level fresh smoke verdict | Structural goal established; not yet entered the current host regression slice |
| `Windsurf` | Has `.windsurf/INSTALL.md` install guide; no current release-level fresh smoke verdict | Structural goal established; not yet entered the current host regression slice |
| `Gemini CLI` | No current fresh release-level verdict | Not entered the current slice |

### 3.3 Hosts Requiring No Independent Adapter

| Host | Current Status | Rationale |
| --- | --- | --- |
| `Kimi Code CLI` | Minimal install prompt suffices; no independent adapter needed | Kimi Code CLI natively auto-discovers `.agents/skills/` (same path as Codex); Aegis Codex installation is Kimi installation |
| `Warp` | No independent adapter needed | As a terminal host, Warp runs third-party CLI agents (Claude Code / Codex / OpenCode) and does not provide its own skills system |

---

## 4. What This Snapshot Means

The current snapshot only states:

1. `Codex` and `OpenCode` are the two mainlines with the most fresh evidence
2. `Kimi Code CLI` reuses the Codex path (`.agents/skills/`); Aegis takes effect via a minimal install prompt
3. `CodeBuddy` can install Aegis via `.codebuddy-plugin/` or native `SKILL.md` discovery, but local CLI live smoke has not yet formed valid evidence
4. `DeepSeek-TUI` can manually install Aegis skills via native `SKILL.md` discovery, but `/skill install github:GanyuanRan/Aegis` is not the current canonical path
5. `Trae` can manually install Aegis skills via native `SKILL.md` discovery; `.agents/skills/` is an optional Trae capability, not Aegis's canonical Trae path
6. `Cursor` and `Windsurf` have structured install guides but have not yet entered release-level fresh smoke
7. `Warp`, as a terminal host, does not itself need an independent adapter
8. The current method-pack still retains the cross-host installation goal
9. "Support all plugin hosts" remains a product goal, not equivalent to "all hosts have current fresh closeout"

---

## 5. Evidence Sources

When reading the current host verdict, follow this order:

1. `docs/testing.md`
2. `docs/README.claude-code.md`
3. `docs/README.codex.md`
4. `docs/README.opencode.md`
5. `docs/README.codebuddy.md`
6. `docs/README.deepseek-tui.md`
7. `docs/README.trae.md`
8. `.windsurf/INSTALL.md`
9. `.cursor/INSTALL.md`

---

## 6. Compatibility Boundary

The current snapshot only covers:

- Method-pack installation and distribution
- skill discovery / representative triggering
- Project workspace support when the installed method-pack root remains
  available and can be verified by `scripts/aegis-doctor.py`
- Plugin loading / priority / distribution sync

The current snapshot does not cover:

- Runtime core integration
- Host adapter event normalization
- Complete live production workflow orchestration

Skill discovery and project workspace support are related but distinct. A
skills-only copy can make Aegis workflows visible to a host while failing to
prove complete project workspace support. A complete install should preserve
the method-pack root or equivalent configured support path so workspace
bootstrap, indexing, work records, and structural checks remain available.

---

## 7. Architecture Review

Three misjudgments must be avoided when reading this snapshot:

1. Mistaking the current pass of `Codex + OpenCode` for "all hosts have been formally closed out"
2. Mistaking current smoke / integration verdicts for full-platform readiness
3. Mistaking host compatibility work for elevating method-pack authority
