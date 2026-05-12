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
Read https://github.com/GanyuanRan/Aegis, install Aegis globally for Codex, restart Codex if needed, then run `python scripts/aegis-doctor.py --write-config --json` from the Aegis method-pack root. Treat the install as complete only if the JSON includes `"ok": true`, `"workspaceSupport": "available"`, and `"configStatus": "configured"`; also verify Codex's skill discovery directory with `--discovery-root <path>`.
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

Codex has native skill discovery — it scans `~/.agents/skills/` at startup, parses SKILL.md frontmatter, and loads skills on demand. Aegis skills are made visible through a single symlink:

```
~/.agents/skills/aegis/ → ~/.codex/aegis/skills/
```

The `using-aegis` skill is discovered automatically and enforces skill usage discipline — no additional configuration needed.

This recommended install keeps the Aegis method-pack root at
`~/.codex/aegis`, so project workspace support can also be verified. The skills
symlink alone proves skill discovery; the full install proves both skill
discovery and project workspace support.

## Usage

Skills are discovered automatically. Codex activates them when:
- You mention a skill by name (e.g., "use brainstorming")
- The task matches a skill's description
- The `using-aegis` skill directs Codex to use one

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

For hook-based hosts, the recommended user-local config is:

```text
~/.config/aegis/config.toml
```

with:

```toml
activation_mode = "explicit"
```

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
cd ~/.codex/aegis && git pull
```

Skills update instantly through the symlink. After updating, restart Codex if
needed and run `python scripts/aegis-doctor.py --write-config --json` from the
method-pack root. The update is complete only when the JSON reports `"ok":
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
2. From the method-pack root, run: `python scripts/aegis-doctor.py --write-config --json`
3. Treat the install as complete only if the JSON reports `"workspaceSupport":
   "available"` and `"configStatus": "configured"`.

### Windows junction issues

Junctions normally work without special permissions. If creation fails, try running PowerShell as administrator.

## Getting Help

- Report issues: https://github.com/GanyuanRan/Aegis/issues
- Main documentation: https://github.com/GanyuanRan/Aegis
