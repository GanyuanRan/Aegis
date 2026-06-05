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

The current snapshot is based on fresh evidence and current docs landed as of
`2026-05-29`.

---

## 3. Current Verdict

### 3.1 Hosts With Fresh Evidence

| Host | Current Verdict | Evidence Owner |
| --- | --- | --- |
| `Codex` | Representative smoke mainline available; naive smoke under Git Bash still requires observation | `docs/testing.md`, `tests/skill-triggering/*`, `tests/explicit-skill-requests/*`, `docs/current/AEGIS_KNOWN_LIMITATIONS.md` |
| `OpenCode` | Base suite and integration closeout passed | `docs/testing.md`, `tests/opencode/*`, `docs/README.opencode.md`; current mainline prefers the configured `method_pack_root` as the canonical Aegis body and treats the OpenCode-visible skills tree as a generated host view |

### 3.2 Hosts Without a Current Fresh Release Verdict

| Host | Current Status | Why Not Yet |
| --- | --- | --- |
| `Claude Code` | Has install guide and plugin skeleton; no current release-level fresh smoke verdict | `docs/README.claude-code.md` established, but real host regression is still deferred |
| `CC GUI (JetBrains IDEA)` | Structural IDE plugin layer target for Claude Code / OpenAI-GPT provider paths; no current release-level fresh smoke verdict | `docs/README.cc-gui.md` established; CC GUI's OpenAI/Codex provider scanner expects direct `.agents/skills/<skill-name>/SKILL.md` skill directories regardless of the selected GPT model profile, so Aegis must expose individual skills rather than only an umbrella `~/.agents/skills/aegis` directory; live IDE plugin smoke and host adapter event rendering remain deferred |
| `CodeBuddy` | Has `.codebuddy-plugin/` skeleton and native `SKILL.md` manual install instructions; no current release-level fresh smoke verdict | `docs/README.codebuddy.md` established; evidence from CodeBuddy skills/plugin docs and this repo's `.codebuddy-plugin/`; real host regression still deferred |
| `DeepSeek-TUI` | Native `SKILL.md` discovery supports manual installation; no current release-level fresh smoke verdict | `docs/README.deepseek-tui.md` established; evidence from DeepSeek-TUI README/source discovery contract; real host regression still deferred |
| `Trae` | Native `SKILL.md` discovery supports manual installation; no current release-level fresh smoke verdict | `docs/README.trae.md` established; evidence from Trae skills docs; real host regression still deferred |
| `GitHub Copilot` | Supports repository skills and custom instructions; no current release-level fresh smoke verdict | `docs/README.copilot.md` established; evidence from GitHub Copilot agent skills and repository instructions docs, but real host regression is still deferred |
| `Qoder` | Native `SKILL.md` discovery and rules surfaces support structural install; no current release-level fresh smoke verdict | `docs/README.qoder.md` established; evidence from Qoder skills and rules docs, but real host regression is still deferred |
| `Cursor` | Has `.cursor/INSTALL.md` install guide; no current release-level fresh smoke verdict | Structural goal established; not yet entered the current host regression slice |
| `Windsurf` | Has `.windsurf/INSTALL.md` install guide; no current release-level fresh smoke verdict | Structural goal established; not yet entered the current host regression slice |
| `Antigravity CLI` | Structural target added; no current release-level fresh smoke verdict | Google positions Antigravity CLI as the successor terminal surface with skills, hooks, subagents, MCP, plugins, and slash-command configuration; the public CLI `1.0.1` changelog adds plugin discovery for skills and agents from installed plugin directories, but the Aegis install / discovery contract still needs fresh verification |
| `Antigravity IDE` | Structural target added; no current release-level fresh smoke verdict | Google positions Antigravity IDE as an editor surface with global or workspace-specific Skills, MCPs, and JSON Hooks; Aegis install path still needs fresh verification |
| `Antigravity App` | Structural target added; no current release-level fresh smoke verdict | Google Antigravity 2.x app / project platform can carry Aegis method-pack projections, but no live host closeout has been run |
| `Pi CLI` | Agent Skills and Pi package surface supports method-pack exposure; no current release-level fresh smoke verdict | Pi documents skill discovery from `~/.pi/agent/skills/`, `~/.agents/skills/`, `.pi/skills/`, package `skills/` directories or `pi.skills` entries, and `pi install git:github.com/GanyuanRan/Aegis` package installs; Aegis still needs current release live smoke before claiming host closeout |
| `OpenClaw` | Native `SKILL.md` skill installer supports local skill directories; no current release-level fresh smoke verdict | `docs/README.openclaw.md` established; evidence from OpenClaw `openclaw skills install` docs that Git/local installs expect `SKILL.md` at the source root; Aegis is multi-skill, so individual skill-directory install is the structural path pending live smoke |
| `Hermes Agent` | Skills Hub / `~/.hermes/skills/` skill host surface supports method-pack exposure; no current release-level fresh smoke verdict | `docs/README.hermes-agent.md` established; evidence from Hermes Skills Hub, documented local skills path, GitHub path installs, and built-in coding delegation skills; live host regression still deferred |

### 3.2a Transitional Compatibility Host Surfaces

| Host | Current Status | Why Retained |
| --- | --- | --- |
| `Gemini CLI` | Transitional compatibility surface; kept outside ordinary pending-host status | Google announced on `2026-05-19` that consumer Gemini CLI and Gemini Code Assist IDE extension usage transitions to Antigravity CLI / Antigravity 2.0. On `2026-06-18`, requests stop being served for free usage, Google AI Pro / Ultra, and Gemini Code Assist for individuals. Enterprise Standard / Enterprise, Google Cloud-backed Gemini Code Assist for GitHub, and paid Gemini / Gemini Enterprise Agent Platform API key paths remain outside that consumer stop boundary. Aegis keeps Gemini CLI support while Antigravity CLI / IDE / App support matures. |

### 3.3 Hosts Requiring No Independent Adapter

| Host | Current Status | Rationale |
| --- | --- | --- |
| `Kimi Code CLI` | Minimal install prompt suffices; no independent adapter needed | Kimi Code CLI natively auto-discovers `.agents/skills/` (same path as Codex); Aegis Codex installation is Kimi installation |
| `Warp` | No independent adapter needed | As a terminal host, Warp runs third-party CLI agents (Claude Code / Codex / OpenCode) and does not provide its own skills system |

### 3.4 Trigger-Family Vocabulary

The current docs may refer to these trigger families as a compact compatibility
aid:

- `hook-bootstrap`
- `native-direct-skill`
- `provider-hybrid`

This vocabulary is advisory and diagnostic only. It does **not** replace
host-specific docs as the canonical owner for install roots, reload behavior,
or supported discovery shapes.

---

## 4. What This Snapshot Means

The current snapshot only states:

1. `Codex` and `OpenCode` are the two mainlines with the most fresh evidence
   - `OpenCode` now prefers the configured `method_pack_root` as its canonical Aegis source when available, then generates the host-visible skills view from that source instead of treating the host cache as a second editable owner
2. `Kimi Code CLI` reuses the Codex path (`.agents/skills/`); Aegis takes effect via a minimal install prompt
3. `CC GUI (JetBrains IDEA)` can expose Aegis to its OpenAI/GPT provider path through direct `~/.agents/skills/<skill-name>/SKILL.md` directories, but the selected GPT model profile does not by itself change the skill discovery shape, and live IDE plugin behavior, reload behavior, and `Tool: exec_command` rendering remain fresh-smoke pending
4. `CodeBuddy` can install Aegis via `.codebuddy-plugin/` or native `SKILL.md` discovery, but local CLI live smoke has not yet formed valid evidence
5. `DeepSeek-TUI` can manually install Aegis skills via native `SKILL.md` discovery, but `/skill install github:GanyuanRan/Aegis` is not the current canonical path
6. `Trae` can manually install Aegis skills via native `SKILL.md` discovery; `.agents/skills/` is an optional Trae capability, not Aegis's canonical Trae path
7. `GitHub Copilot` can expose Aegis through `.github/skills/`, `.github/copilot-instructions.md`, and `AGENTS.md`, but support remains structural until a fresh Copilot install and agent smoke proves it for the current release
8. `Qoder` can expose Aegis through `~/.qoder/skills/`, `.qoder/skills/`, `.qoder/rules/`, and `AGENTS.md`, but support remains structural until a fresh Qoder install smoke proves it for the current release
9. `Cursor` and `Windsurf` have structured install guides but have not yet entered release-level fresh smoke
10. `Antigravity CLI`, `Antigravity IDE`, and `Antigravity App` are now structural target surfaces, but still lack release-level fresh smoke evidence
11. `Gemini CLI` is retained as a transitional compatibility surface after Google's `2026-05-19` transition announcement while Antigravity support matures
12. `Pi CLI` can expose Aegis through `pi install git:github.com/GanyuanRan/Aegis`, Pi package `skills/` / `pi.skills` discovery, `~/.pi/agent/skills/`, `~/.agents/skills/`, or `.pi/skills/`, but support remains structural until a fresh Pi install smoke proves it for the current release
13. `OpenClaw` can expose Aegis through individual local skill-directory installs, but `git:owner/repo` should not be written as the canonical whole-repo Aegis installer because OpenClaw expects `SKILL.md` at the source root
14. `Hermes Agent` can expose Aegis through `~/.hermes/skills/` or documented GitHub path installs, but support remains structural until a fresh Hermes install smoke proves it for the current release
15. `Warp`, as a terminal host, does not itself need an independent adapter
16. The current method-pack still retains the cross-host installation goal
17. "Support all plugin hosts" remains a product goal, not equivalent to "all hosts have current fresh closeout"
18. Some hosts may require a compatibility exposure shape that differs from a
    mainline host's canonical install shape; when that happens, the method-pack
    `skills/` tree remains the canonical source and the extra exposure should be
    treated as a generated compatibility view rather than a second editable
    owner
19. The shared local `~/.config/aegis/config.toml` may declare one canonical
    `method_pack_root`; when it does, new host registrations should prefer that
    root and treat host-specific discovery roots, plugin caches, or copied skill
    trees as generated or host-managed views into the same Aegis body

---

## 5. Evidence Sources

When reading the current host verdict, follow this order:

1. `docs/testing.md`
2. `docs/README.claude-code.md`
3. `docs/README.codex.md`
4. `docs/README.cc-gui.md`
5. `docs/README.opencode.md`
6. `docs/README.codebuddy.md`
7. `docs/README.deepseek-tui.md`
8. `docs/README.trae.md`
9. `docs/README.copilot.md`
10. `docs/README.qoder.md`
11. `docs/README.antigravity.md`
12. `docs/README.pi.md`
13. `docs/README.openclaw.md`
14. `docs/README.hermes-agent.md`
15. `.windsurf/INSTALL.md`
16. `.cursor/INSTALL.md`

---

## 6. Compatibility Boundary

The current snapshot only covers:

- Method-pack installation and distribution
- skill discovery / representative triggering
- Project workspace support when the installed method-pack root remains
  available and can be verified by
  `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`
- Host-scoped explicit update registration through
  `python scripts/aegis-update.py status --json` and
  `python scripts/aegis-update.py update --host <host> --json`
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
Complete-install verification should write local helper paths and read back
`"ok": true`, `"workspaceSupport": "available"`, and `"configStatus":
"configured"` from `aegis-doctor.py`.

Do not run `aegis-doctor.py` from the target project directory. The script
belongs to the installed Aegis method-pack root; target projects are passed
separately to workspace helper commands with `--root <target-project-root>`.

---

## 7. Architecture Review

Three misjudgments must be avoided when reading this snapshot:

1. Mistaking the current pass of `Codex + OpenCode` for "all hosts have been formally closed out"
2. Mistaking current smoke / integration verdicts for full-platform readiness
3. Mistaking host compatibility work for elevating method-pack authority
