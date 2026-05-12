# Aegis for DeepSeek-TUI

Guide for using Aegis with DeepSeek-TUI through its native `SKILL.md`
discovery.

This page only covers the DeepSeek-TUI host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

DeepSeek-TUI is skills-compatible with Aegis because it discovers skills from
directories that contain `SKILL.md`.

Supported path:

- copy Aegis skill directories into a DeepSeek-TUI skill discovery directory
- restart DeepSeek-TUI or start a new session
- verify with DeepSeek-TUI's `/skills` and `/skill <name>` commands

Not the canonical path:

- `/skill install github:GanyuanRan/Aegis`

That command shape is useful for single-skill repositories, but Aegis is a
multi-skill method-pack repository. Use the copy-based install below unless
DeepSeek-TUI adds a stable multi-skill repository installer.

This guide records structural compatibility and manual install support. It does
not claim current release-level live smoke evidence for DeepSeek-TUI.

## Recommended Complete Installation

Keep a local Aegis checkout and copy skills from it. This preserves both skill
discovery and project workspace support verification.

## Global Installation

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.deepseek/aegis
mkdir -p ~/.deepseek/skills
cp -R ~/.deepseek/aegis/skills/* ~/.deepseek/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.deepseek\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.deepseek\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.deepseek\aegis\skills\*" "$env:USERPROFILE\.deepseek\skills\"
```

The copy puts each Aegis skill directly at:

```text
~/.deepseek/skills/<skill-name>/SKILL.md
```

Because the checkout remains at `~/.deepseek/aegis`, project workspace support
can be verified from that method-pack root.

## Project-Local Installation

Inside a project where you want Aegis to be available:

```bash
mkdir -p .agents/skills
cp -R /path/to/Aegis/skills/* .agents/skills/
```

Use a project-local install when you want Aegis scoped to one repository instead
of every DeepSeek-TUI session on the machine.

## Verification

Restart DeepSeek-TUI or start a new session, then run:

```text
/skills
```

Expected result:

- Aegis skill names such as `using-aegis`, `systematic-debugging`, and
  `brainstorming` are listed.

Then load one skill:

```text
/skill using-aegis
```

or:

```text
/skill systematic-debugging
```

You can also ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

DeepSeek-TUI should treat Aegis as method-pack guidance, not as a full runtime
platform or final completion authority.

For complete install verification, also run this from the local Aegis checkout
when filesystem access is available:

```bash
python scripts/aegis-doctor.py --write-config --json
```

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

## Updating

### macOS / Linux

```bash
cd ~/.deepseek/aegis
git pull
cp -R ~/.deepseek/aegis/skills/* ~/.deepseek/skills/
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.deepseek\aegis"
git pull
Copy-Item -Recurse -Force "$env:USERPROFILE\.deepseek\aegis\skills\*" "$env:USERPROFILE\.deepseek\skills\"
```

Restart DeepSeek-TUI after updating.

## Activation Mode

DeepSeek-TUI uses native skill discovery. It does not currently use an Aegis
bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override DeepSeek-TUI's own
skill matcher by itself. For explicit use, load an Aegis skill directly with:

```text
/skill using-aegis
```

## Uninstalling

Remove the copied Aegis skill directories from:

```text
~/.deepseek/skills/
```

If you installed only Aegis into that directory, remove the directory contents
and then restart DeepSeek-TUI. If you also keep personal skills there, delete
only the Aegis skill folders you copied from this repository.

## Troubleshooting

### Skills are not listed

1. Confirm a copied skill exists at `~/.deepseek/skills/<skill-name>/SKILL.md`.
2. Restart DeepSeek-TUI or start a new session.
3. Run `/skills`.
4. Check whether a project-local skill with the same name is taking precedence.

### GitHub installer does not install all Aegis skills

Use the copy-based install in this guide. Aegis is a multi-skill repository, so a
single-skill GitHub installer is not the stable canonical path for this host.

### Project workspace support not verified

If only `skills/` were copied and the local checkout was removed, skill
discovery may still work but complete project workspace support is not proven.
Restore the checkout and run `python scripts/aegis-doctor.py --write-config
--json`. The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.

## DeepSeek-TUI References

- https://github.com/Hmbown/DeepSeek-TUI
