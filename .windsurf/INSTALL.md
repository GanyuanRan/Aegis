# Installing Aegis for Windsurf

This page only covers the Windsurf host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Quick Install

Tell Windsurf:

```
Fetch and follow instructions from https://raw.githubusercontent.com/GanyuanRan/Aegis/refs/heads/main/.windsurf/INSTALL.md
```

## Prerequisites

- Windsurf editor or Windsurf CLI
- Git

## Installation

Aegis contains 17 skills. Windsurf discovers skills one level under the skills directory,
so each Aegis skill is symlinked individually with an `aegis-` prefix.

### Global Install (available in all workspaces)

**macOS / Linux:**

```bash
AEGIS_DIR="${HOME}/.codeium/windsurf/aegis"
SKILLS_DIR="${HOME}/.codeium/windsurf/skills"

git clone https://github.com/GanyuanRan/Aegis.git "$AEGIS_DIR"
mkdir -p "$SKILLS_DIR"

for skill_dir in "$AEGIS_DIR/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  ln -sfn "$skill_dir" "$SKILLS_DIR/aegis-${skill_name}"
done
```

**Windows (PowerShell):**

```powershell
$AegisDir = "$env:USERPROFILE\.codeium\windsurf\aegis"
$SkillsDir = "$env:USERPROFILE\.codeium\windsurf\skills"

git clone https://github.com/GanyuanRan/Aegis.git $AegisDir
New-Item -ItemType Directory -Force -Path $SkillsDir -ErrorAction SilentlyContinue | Out-Null

Get-ChildItem "$AegisDir\skills" -Directory | ForEach-Object {
  $linkPath = "$SkillsDir\aegis-$($_.Name)"
  if (Test-Path $linkPath) { Remove-Item $linkPath -Recurse -Force }
  New-Item -ItemType Junction -Path $linkPath -Target $_.FullName | Out-Null
}
```

### Workspace Install (project-specific)

From your project root, symlink into `.windsurf/skills/` instead:

**macOS / Linux:**

```bash
AEGIS_DIR="${HOME}/.codeium/windsurf/aegis"
mkdir -p .windsurf/skills

for skill_dir in "$AEGIS_DIR/skills/"*/; do
  skill_name=$(basename "$skill_dir")
  ln -sfn "$skill_dir" ".windsurf/skills/aegis-${skill_name}"
done
```

**Windows (PowerShell):**

```powershell
$AegisDir = "$env:USERPROFILE\.codeium\windsurf\aegis"
New-Item -ItemType Directory -Force -Path ".windsurf\skills" -ErrorAction SilentlyContinue | Out-Null

Get-ChildItem "$AegisDir\skills" -Directory | ForEach-Object {
  $linkPath = ".windsurf\skills\aegis-$($_.Name)"
  if (Test-Path $linkPath) { Remove-Item $linkPath -Recurse -Force }
  New-Item -ItemType Junction -Path $linkPath -Target $_.FullName | Out-Null
}
```

## Updating

To update Aegis skills after installation:

```bash
git -C ~/.codeium/windsurf/aegis pull
```

No need to recreate symlinks — they point into the repo directory and pick up
changes automatically.

## Activation Mode

Aegis defaults to automatic mode. Windsurf discovers skills via the
agentskills.io native discovery mechanism — skills are listed in the Cascade
customization menu and can be invoked via `@aegis-<skill-name>`.

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

Restart Windsurf or start a new Cascade session after changing local Aegis
config. For this host, the command does not override native skill matching.

## Skill Names

After installation, the following skills are available in Cascade:

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
ls -la ~/.codeium/windsurf/skills/aegis-*
```

You should see 17 symlinks or junctions pointing into the Aegis skills directory.

Open a project in Windsurf, open Cascade, and type `@aegis-` to see the
auto-completion list of available Aegis skills.

For full host guidance and troubleshooting details, read `docs/README.claude-code.md`
(Windsurf uses the same agentskills.io specification as Claude Code skills).
