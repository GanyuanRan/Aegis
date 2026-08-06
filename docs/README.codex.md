# Aegis for Codex

Guide for using Aegis with OpenAI Codex via native skill discovery.

This page only covers the Codex host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Quick Install

Tell Codex:

```
Read https://github.com/GanyuanRan/Aegis, install Aegis globally for Codex, restart Codex if needed, then run complete-install verification from the installed Aegis method-pack root. Do not run the doctor command from the target project directory. First locate `<aegis-method-pack-root>`, then run `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`. Treat the install as complete only if the JSON includes `"ok": true`, `"workspaceSupport": "available"`, and `"configStatus": "configured"`; also verify Codex's skill discovery directory with `--discovery-root <path>`.
```

## Manual Installation

### Prerequisites

- OpenAI Codex CLI
- Git

### Steps

1. Clone the repo:
   ```bash
   git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
   ```

2. Create the skills symlink:
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/aegis/skills ~/.agents/skills/aegis
   ```

3. Restart Codex.

4. **For subagent skills** (optional): Skills like `dispatching-parallel-agents` and `subagent-driven-development` require Codex's multi-agent feature. Add to your Codex config:
   ```toml
   [features]
   multi_agent = true
   ```

### Windows

Use a junction instead of a symlink (works without Developer Mode):

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\aegis" "$env:USERPROFILE\.codex\aegis\skills"
```

## How It Works

Do not assume the current repository checkout is the active runtime skill
source. Codex normally loads Aegis through the installed method-pack root and
its host-visible skill view.

Codex has native skill discovery — it scans `~/.agents/skills/` at startup, parses SKILL.md frontmatter, and loads skills on demand. Aegis skills are made visible through a single symlink:

```
~/.agents/skills/aegis/ → ~/.codex/aegis/skills/
```

The `using-aegis` skill is discovered automatically and enforces skill usage discipline — no additional configuration needed.

This recommended install keeps the Aegis method-pack root at
`~/.codex/aegis`, so project workspace support can also be verified. The skills
symlink alone proves skill discovery; the full install proves both skill
discovery and project workspace support.

Across hosts, this method-pack root is the canonical Aegis body. Discovery
paths such as `~/.agents/skills/aegis` are generated host views into that same
body rather than second editable copies.

## Usage

Skills are discovered automatically. Codex activates them when:
- You mention a skill by name (e.g., "use brainstorming")
- The task matches a skill's description
- The `using-aegis` skill directs Codex to use one

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

### Personal Skills

Create your own skills in `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills/my-skill
```

Create `~/.agents/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Use when [condition] - [what it does]
---

# My Skill

[Your skill content here]
```

The `description` field is how Codex decides when to activate a skill automatically — write it as a clear trigger condition.

## Activation Mode

`AEGIS_ACTIVATION_MODE=auto|explicit` is the cross-host Aegis activation
profile. It is an environment variable read by host processes that have an
Aegis bootstrap hook; it is not a Codex config file field.

Codex uses native skill discovery rather than an Aegis bootstrap hook. That
means `AEGIS_ACTIVATION_MODE=explicit` does not override Codex's own semantic
skill matcher by itself. To use an explicit-only Codex setup, keep Aegis
available for direct calls but avoid installing an automatic entry skill/profile
that tells Codex to start every conversation with Aegis. You can still invoke
Aegis directly by naming a skill, such as `aegis:using-aegis` or
`aegis:brainstorming`.

**How `explicit` works on Codex.** Because Codex has no Aegis bootstrap hook,
`AEGIS_ACTIVATION_MODE=explicit` does not stop Codex from auto-loading a skill
whose description matches the task. The method pack handles this at the skill
execution layer: doc/checklist workflows (`using-aegis`, `brainstorming`,
`writing-plans`, `verification-before-completion`) carry an
`EXPLICIT-MODE-GATE` that fast-exits when activation mode is `explicit` and the
user did not explicitly invoke Aegis or the skill by name. Explicit invocation
(e.g. `use aegis:brainstorming`) still works normally.

**One-command AGENTS.md management.** `aegis-doctor.py activation-mode
explicit|auto` can also manage the Aegis routing block in
`~/.codex/AGENTS.md` so auto-loading noise drops instead of just being exited
after load:

- First run: backs up `~/.codex/AGENTS.md`, wraps the existing Aegis routing
  paragraph in an `AEGIS-ROUTING-BEGIN/END` marker block, and records the
  original text in `~/.config/aegis/agents-md-state.json`.
- `explicit`: the block is replaced with the narrowed version (Aegis only on
  explicit invocation; simple tasks stay on the fast path).
- `auto`: the block is restored to the recorded original text, so automatic
  Aegis routing behavior is unchanged.
- Skip AGENTS.md management with `--no-agents-md` (config only).
- Manual rollback: restore the backup file, e.g.
  `Copy-Item "$env:USERPROFILE\.codex\AGENTS.md.bak-aegis-<ts>" "$env:USERPROFILE\.codex\AGENTS.md"`.

TDD mode defaults to `off`. `AEGIS_TDD_MODE=auto` or
`aegis-doctor.py tdd-mode auto` enables Aegis-side automatic TDD route
semantics, but this does not directly control Codex's native matcher. Keep the
`test-driven-development` trigger narrow, anchored to literal conversation
markers such as `TDD Route: strict`, `strict TDD`, `test-first`, or
`RED / GREEN / REFACTOR`, and rely on explicit invocation or
`using-aegis`-selected strict-route work instead of expecting the environment
variable alone to suppress or force every automatic TDD load. If Codex loads
the skill without those markers while TDD mode is `off`, the skill should exit
back to non-TDD routing rather than starting RED by inference.

For hook-based hosts, the recommended user-local config is:

```text
~/.config/aegis/config.toml
```

with:

```toml
activation_mode = "explicit"
```

You can also write the same config from the installed Aegis method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

Switch back to automatic mode with:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Restart Codex or start a new session after changing local Aegis config. In
Codex, this command does not override the host's own semantic skill matcher;
it only configures Aegis bootstrap/profile-aware surfaces.

For hosts with bootstrap hooks, the one-time terminal shape is:

```bash
AEGIS_ACTIVATION_MODE=explicit opencode
AEGIS_ACTIVATION_MODE=explicit claude
```

PowerShell:

```powershell
$env:AEGIS_ACTIVATION_MODE = "explicit"
opencode
# or: claude
```

## Updating

```bash
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host codex \
  --sync-mode junction \
  --discovery-root ~/.agents/skills/aegis \
  --reload-hint "restart Codex"
python scripts/aegis-update.py update --host codex --json
```

The update skill form is `aegis:update`. It uses the same host-scoped registry
and updates only the current host unless the user explicitly asks for `--all`.
Skills update instantly through the symlink. After updating, restart Codex if
needed. The updater runs the doctor command from the installed method-pack root,
not from the target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The update is complete only when the JSON reports `"ok":
true`, `"workspaceSupport": "available"`, and `"configStatus": "configured"`;
also pass `--discovery-root <path>` when checking Codex's skill discovery
directory.

## Uninstalling

```bash
rm ~/.agents/skills/aegis
```

**Windows (PowerShell):**
```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\aegis"
```

Optionally delete the clone: `rm -rf ~/.codex/aegis` (Windows: `Remove-Item -Recurse -Force "$env:USERPROFILE\.codex\aegis"`).

## Troubleshooting

### Skills not showing up

1. Verify the symlink: `ls -la ~/.agents/skills/aegis`
2. Check skills exist: `ls ~/.codex/aegis/skills`
3. Restart Codex — skills are discovered at startup

### Project workspace support not verified

1. Confirm the method-pack root still exists: `ls ~/.codex/aegis`
2. Do not run the doctor command from the target project directory. From the method-pack root, run: `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`
3. Treat the install as complete only if the JSON reports `"workspaceSupport":
   "available"` and `"configStatus": "configured"`.

### Windows junction issues

Junctions normally work without special permissions. If creation fails, try running PowerShell as administrator.

## Getting Help

- Report issues: https://github.com/GanyuanRan/Aegis/issues
- Main documentation: https://github.com/GanyuanRan/Aegis
