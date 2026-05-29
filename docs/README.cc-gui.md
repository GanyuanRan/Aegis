# Aegis for CC GUI

Guide for using Aegis with CC GUI, the JetBrains IDEA plugin layer for
Claude Code and OpenAI Codex.

This page only covers the CC GUI host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

CC GUI is an independent JetBrains IDEA plugin that wraps Claude Code and
OpenAI Codex through a visual IDE interface. Its public project describes an
Agent system, Skills slash commands, MCP support, and permission management:

- https://github.com/zhukunpenglinyutong/jetbrains-cc-gui
- https://plugins.jetbrains.com/plugin/29342-cc-gui-claude-or-codex-

For Aegis, the important compatibility boundary is the Codex-side skill
directory shape. CC GUI's Codex skill scanner reads `.agents/skills/` style
directories and expects each direct child skill directory to contain its own
`SKILL.md` file:

```text
~/.agents/skills/<skill-name>/SKILL.md
```

That differs from an umbrella directory such as:

```text
~/.agents/skills/aegis/ -> ~/.codex/aegis/skills/
```

The umbrella shape can keep native Codex workflows working, but it is not the
preferred CC GUI Codex-side exposure because `~/.agents/skills/aegis/` does not
itself contain `SKILL.md`.

This guide records structural CC GUI support. It does **not** claim current release-level live smoke evidence for CC GUI; fresh smoke is pending.

## Recommended Codex-Side Installation

Keep the Aegis method-pack checkout separate, then expose each Aegis skill as a
direct child under `~/.agents/skills/`. This preserves:

- CC GUI / Codex skill discovery through direct `SKILL.md` directories
- Aegis project workspace support through the method-pack root
- update and doctor verification through Aegis scripts

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"

Get-ChildItem "$env:USERPROFILE\.codex\aegis\skills" -Directory | ForEach-Object {
  $target = Join-Path "$env:USERPROFILE\.agents\skills" $_.Name
  if (-not (Test-Path -LiteralPath $target)) {
    cmd /c mklink /J "$target" "$($_.FullName)"
  }
}
```

If junctions are not allowed in your environment, use copies instead:

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.codex\aegis\skills\*" "$env:USERPROFILE\.agents\skills\"
```

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
mkdir -p ~/.agents/skills

for skill_dir in ~/.codex/aegis/skills/*; do
  [ -d "$skill_dir" ] || continue
  ln -sfn "$skill_dir" "$HOME/.agents/skills/$(basename "$skill_dir")"
done
```

Expected structural result:

```text
~/.agents/skills/using-aegis/SKILL.md
~/.agents/skills/systematic-debugging/SKILL.md
~/.agents/skills/brainstorming/SKILL.md
```

## Claude-Side Use

When CC GUI is used with Claude Code rather than OpenAI Codex, start from
`docs/README.claude-code.md` and CC GUI's own skill management UI. Verify the
same direct skill-directory invariant for any copied or linked skills:

```text
<claude-or-cc-gui-skill-root>/<skill-name>/SKILL.md
```

This page does not replace Claude Code installation guidance.

## Verification

Restart CC GUI, reload the IDE plugin window, or start a new CC GUI session
after installing.

For complete-install verification, run this from the installed Aegis method
pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

For Codex-side CC GUI skill discovery, also verify the discovery root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root ~/.agents/skills
```

PowerShell:

```powershell
Set-Location "$env:USERPROFILE\.codex\aegis"
python scripts\aegis-doctor.py --discovery-root "$env:USERPROFILE\.agents\skills"
```

Expected result:

- CC GUI / Codex can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`.
- CC GUI can load the relevant skill on demand.
- The installed Aegis method-pack root remains available for workspace support.
- Aegis remains a method pack; `GateDecision` and completion authority remain
  outside this repository.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

## Updating

For junction-based installs, update the Aegis checkout and restart or reload
CC GUI:

```bash
cd ~/.codex/aegis
git pull
python scripts/aegis-doctor.py --write-config --json
```

For copy-based installs, copy the skill directories again after updating the
checkout.

You can also register the installation with Aegis's host-scoped updater:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host cc-gui \
  --sync-mode junction \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart CC GUI or reload the IDE plugin"
python scripts/aegis-update.py update --host cc-gui --json
```

The update skill form is `aegis:update`. It uses the same host-scoped registry
and updates only the current host unless the user explicitly asks for `--all`.

## Activation Mode

CC GUI uses its own IDE/plugin layer around Claude Code and OpenAI Codex. It
does not currently use an Aegis bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override CC GUI, Codex, or
Claude Code native skill matching by itself. For explicit use, ask the host to
load an Aegis skill directly, such as `using-aegis`, or name the skill in your
request.

You can still write the shared user-local Aegis config from the installed
method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

Switch back to automatic mode with:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Restart CC GUI or start a new session after changing local Aegis config. For
this host, the command does not override CC GUI's native matcher.

## Tool Event Rendering Boundary

If a small task appears in CC GUI as repeated `Tool: exec_command` entries,
treat that as host adapter event rendering and normalization, not as an Aegis
method-pack authority claim.

Aegis can encourage a lower-tool fast path for simple tasks, and can make the
skill activation boundary clearer. It cannot guarantee that CC GUI folds,
groups, suppresses, or restyles tool events. The current compatibility snapshot
does not cover host adapter event normalization or complete live production
workflow orchestration.

## Troubleshooting

### Aegis skills are not visible

1. Confirm that direct skill directories exist:
   `~/.agents/skills/<skill-name>/SKILL.md`.
2. Avoid relying only on the umbrella directory
   `~/.agents/skills/aegis/ -> ~/.codex/aegis/skills/` for CC GUI.
3. Restart CC GUI or reload the IDE plugin window.
4. Run `python scripts/aegis-doctor.py --discovery-root ~/.agents/skills` from
   the Aegis method-pack root.

### Project workspace support is not verified

If only skill directories were copied and the local checkout was removed, skill
discovery may still work but complete project workspace support is not proven.
Restore the checkout and run this from the method-pack root, not from the
target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.
