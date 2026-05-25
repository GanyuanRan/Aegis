# Aegis for Hermes Agent

Guide for using Aegis with Hermes Agent through Hermes Agent's skill system.

This page only covers the Hermes Agent host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Hermes Agent is skills-compatible with Aegis because Hermes exposes a Skills Hub
and a local `SKILL.md` skill system. Hermes currently documents:

- local skills under `~/.hermes/skills/`
- GitHub path installs such as `hermes skills install owner/repo/skills/my-workflow`
- `hermes skills list` and related skill-management commands
- built-in coding-agent delegation skills for Claude Code, Codex, and OpenCode

The current Aegis support status is structural and advisory. It does **not**
claim current release-level live smoke evidence for Hermes Agent.

## Recommended Complete Installation

Keep a local Aegis checkout for workspace helper support, then expose Aegis
skill directories to Hermes using either the documented local skills directory
or the current Hermes skill installation surface.

The stable Aegis-side source layout is:

```text
<aegis-method-pack-root>/skills/<skill-name>/SKILL.md
```

Install at least these skills first:

- `using-aegis`
- `systematic-debugging`
- `brainstorming`
- `writing-plans`
- `verification-before-completion`

The most transparent path is to copy the individual Aegis skill directories
into `~/.hermes/skills/`. If your Hermes release supports GitHub path installs,
you may also install individual Aegis skills with paths such as:

```bash
hermes skills install GanyuanRan/Aegis/skills/using-aegis
hermes skills install GanyuanRan/Aegis/skills/systematic-debugging
hermes skills install GanyuanRan/Aegis/skills/brainstorming
```

Do not treat this repository root as a single Hermes skill. Aegis is a
multi-skill method pack.

## Suggested Local Layout

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.hermes/aegis
mkdir -p ~/.hermes/skills
cp -R ~/.hermes/aegis/skills/* ~/.hermes/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.hermes\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.hermes\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.hermes\aegis\skills\*" "$env:USERPROFILE\.hermes\skills\"
```

This layout keeps a complete Aegis checkout available while exposing individual
skill directories as:

```text
~/.hermes/skills/<skill-name>/SKILL.md
```

If the Hermes Agent release you are using provides a different documented
global or workspace skill path, prefer that host-native path and keep the Aegis
checkout available for doctor and workspace helper verification.

## Verification

Restart Hermes Agent or start a new session, then ask it to list or describe
available Aegis skills. If your Hermes release exposes the CLI, run:

```bash
hermes skills list
```

Expected result:

- Hermes can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`.
- Hermes can load the relevant skill on demand.
- The local Aegis checkout remains available for workspace support.
- Hermes does not present Aegis as a full runtime platform, authoritative
  `GateDecision`, or final completion authority.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward.

For complete-install verification, run this from the local Aegis checkout:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

If Hermes uses a separate skill discovery directory in your current release,
also verify it:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root <hermes-skill-discovery-root>
```

## Updating

### macOS / Linux

```bash
cd ~/.hermes/aegis
git pull
cp -R ~/.hermes/aegis/skills/* ~/.hermes/skills/
python scripts/aegis-doctor.py --write-config --json
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.hermes\aegis"
git pull
Copy-Item -Recurse -Force "$env:USERPROFILE\.hermes\aegis\skills\*" "$env:USERPROFILE\.hermes\skills\"
python scripts/aegis-doctor.py --write-config --json
```

Restart Hermes Agent or start a new session after updating.

## Activation Mode

Hermes Agent uses its native skill discovery and routing. It does not currently
use an Aegis bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override Hermes Agent's
own skill matcher by itself. For explicit use, ask Hermes to load an Aegis skill
directly.

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

Restart Hermes Agent or start a new session after changing local Aegis config.
For this host, the command does not override Hermes Agent's native matcher.

## Troubleshooting

### Skills are not visible

1. Confirm each exposed Aegis skill has `SKILL.md` at the skill root.
2. Run `hermes skills list` when available.
3. Restart Hermes Agent or start a new session.
4. Ask Hermes to list or describe Aegis skills.
5. Check whether a workspace or registry skill with the same name is taking
   precedence.

### Project workspace support not verified

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

## Official Hermes Agent References

- https://hermes-agent.nousresearch.com/docs/skills/
