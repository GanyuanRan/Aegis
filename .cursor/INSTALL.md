# Installing Aegis for Cursor

This page only covers the Cursor host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Quick Install

Tell Cursor's agent:

```
Fetch and follow instructions from https://raw.githubusercontent.com/GanyuanRan/Aegis/refs/heads/main/.cursor/INSTALL.md
```

## Prerequisites

- Cursor editor with agent mode enabled
- Git

## Installation

Aegis contains 17 skills following the agentskills.io specification. Cursor
discovers skills from the skills directory. Each Aegis skill is symlinked
individually with an `aegis-` prefix.

### Global Install (available in all workspaces)

**macOS / Linux:**

```bash
AEGIS_DIR="${HOME}/.cursor/aegis"
SKILLS_DIR="${HOME}/.cursor/skills"

git clone https://github.com/GanyuanRan/Aegis.git "$AEGIS_DIR"
mkdir -p "$SKILLS_DIR"

for skill_dir in "$AEGIS_DIR/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  ln -sfn "$skill_dir" "$SKILLS_DIR/aegis-${skill_name}"
done
```

**Windows (PowerShell):**

```powershell
$AegisDir = "$env:USERPROFILE\.cursor\aegis"
$SkillsDir = "$env:USERPROFILE\.cursor\skills"

git clone https://github.com/GanyuanRan/Aegis.git $AegisDir
New-Item -ItemType Directory -Force -Path $SkillsDir -ErrorAction SilentlyContinue | Out-Null

Get-ChildItem "$AegisDir\skills" -Directory | ForEach-Object {
  $linkPath = "$SkillsDir\aegis-$($_.Name)"
  if (Test-Path $linkPath) { Remove-Item $linkPath -Recurse -Force }
  New-Item -ItemType Junction -Path $linkPath -Target $_.FullName | Out-Null
}
```

### Workspace Install (project-specific)

From your project root, symlink into `.cursor/skills/` instead:

**macOS / Linux:**

```bash
AEGIS_DIR="${HOME}/.cursor/aegis"
mkdir -p .cursor/skills

for skill_dir in "$AEGIS_DIR/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  ln -sfn "$skill_dir" ".cursor/skills/aegis-${skill_name}"
done
```

**Windows (PowerShell):**

```powershell
$AegisDir = "$env:USERPROFILE\.cursor\aegis"
New-Item -ItemType Directory -Force -Path ".cursor\skills" -ErrorAction SilentlyContinue | Out-Null

Get-ChildItem "$AegisDir\skills" -Directory | ForEach-Object {
  $linkPath = ".cursor\skills\aegis-$($_.Name)"
  if (Test-Path $linkPath) { Remove-Item $linkPath -Recurse -Force }
  New-Item -ItemType Junction -Path $linkPath -Target $_.FullName | Out-Null
}
```

### Extension Method (alternative)

Cursor is built on VS Code and supports extensions. The `.cursor-plugin/plugin.json`
manifest allows Cursor to discover Aegis as a plugin when the repo directory is
registered as an extension:

**macOS / Linux:**

```bash
ln -s ~/.cursor/aegis ~/.cursor/extensions/aegis
```

**Windows (PowerShell):**

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.cursor\extensions\aegis" -Target "$env:USERPROFILE\.cursor\aegis"
```

Restart Cursor after installation.

## Updating

To update Aegis skills after installation:

```bash
git -C ~/.cursor/aegis pull
```

Symlinks point into the repo directory and pick up changes automatically.

## Activation Mode

Aegis defaults to automatic mode. The SessionStart hook
(`hooks/hooks-cursor.json`) injects the Aegis discipline hot path at session
start when Cursor loads the plugin.

To switch to explicit mode:

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

Restart Cursor or start a new agent session after changing local Aegis config.

## Skill Names

After installation, the following skills are available in Cursor's agent:

| Skill Name | Description |
|------------|-------------|
| `aegis-using-aegis` | Aegis discipline hot path |
| `aegis-brainstorming` | Design before implementation |
| `aegis-communicating-concisely` | Clear, concise communication |
| `aegis-dispatching-parallel-agents` | Parallel agent orchestration |
| `aegis-establishing-project-context` | Project context baseline |
| `aegis-executing-plans` | Batch plan execution |
| `aegis-finishing-a-development-branch` | Branch completion |
| `aegis-long-task-continuation` | Cross-session task resume |
| `aegis-receiving-code-review` | Code review response |
| `aegis-requesting-code-review` | Code review request |
| `aegis-subagent-driven-development` | Fresh subagent per task |
| `aegis-systematic-debugging` | Root cause analysis |
| `aegis-test-driven-development` | RED-GREEN-REFACTOR cycle |
| `aegis-using-git-worktrees` | Git worktree isolation |
| `aegis-verification-before-completion` | Evidence before claims |
| `aegis-writing-plans` | Implementation plans |
| `aegis-writing-skills` | Skill authoring guide |

## Verify

```bash
ls -la ~/.cursor/skills/aegis-*
```

You should see 17 symlinks or junctions pointing into the Aegis skills directory.

Open a project in Cursor, start a new agent session, and verify the SessionStart
hook loads Aegis context. You can also ask the agent:

> Load the aegis:using-aegis skill and confirm Aegis is active.

## Status

This Cursor adapter is a structural target. It has not yet received a fresh
release-level host regression verdict. See
`docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md` for the current
compatibility status.
