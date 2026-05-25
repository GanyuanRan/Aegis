# Aegis for OpenClaw

Guide for using Aegis with OpenClaw through OpenClaw's native `SKILL.md`
skill system.

This page only covers the OpenClaw host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

OpenClaw is skills-compatible with Aegis because OpenClaw supports installing
skills from Git repositories and local directories whose source root contains a
`SKILL.md` file.

OpenClaw's documented `openclaw skills install git:owner/repo[@ref]` path is
best suited to single-skill repositories. Aegis is a multi-skill method-pack
repository whose individual skills live under `skills/<skill-name>/SKILL.md`,
so the recommended Aegis path is:

- keep a local Aegis checkout for workspace helper support
- install or copy individual Aegis skill directories from `skills/`
- verify visibility with `openclaw skills list` or `openclaw skills check`
- verify complete install support with `aegis-doctor.py`

This guide records structural compatibility and manual install support. It does
not claim current release-level live smoke evidence for OpenClaw.

## Recommended Complete Installation

Keep a local Aegis checkout and install individual skill directories from it.
This preserves both skill discovery and project workspace support verification.

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.openclaw/aegis
cd ~/.openclaw/aegis

openclaw skills install ./skills/using-aegis --as using-aegis --global
openclaw skills install ./skills/systematic-debugging --as systematic-debugging --global
openclaw skills install ./skills/brainstorming --as brainstorming --global
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.openclaw\aegis"
Set-Location "$env:USERPROFILE\.openclaw\aegis"

openclaw skills install .\skills\using-aegis --as using-aegis --global
openclaw skills install .\skills\systematic-debugging --as systematic-debugging --global
openclaw skills install .\skills\brainstorming --as brainstorming --global
```

Install additional Aegis skills the same way when you need them. For example:

```bash
openclaw skills install ./skills/writing-plans --as writing-plans --global
openclaw skills install ./skills/verification-before-completion --as verification-before-completion --global
```

Use `--agent <id>` instead of `--global` when you want Aegis scoped to one
configured OpenClaw agent workspace.

## Project-Local Installation

Inside a project where you want Aegis to be available only to that workspace:

```bash
git clone https://github.com/GanyuanRan/Aegis.git .aegis-method-pack
openclaw skills install ./.aegis-method-pack/skills/using-aegis --as using-aegis
openclaw skills install ./.aegis-method-pack/skills/systematic-debugging --as systematic-debugging
openclaw skills install ./.aegis-method-pack/skills/brainstorming --as brainstorming
```

Project-local installs are useful for experimenting. Keep the checkout in place
if you also want Aegis workspace support, doctor checks, and future updates.

## Verification

Restart OpenClaw or start a new session, then run:

```bash
openclaw skills list
openclaw skills check
```

Expected result:

- OpenClaw can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`.
- OpenClaw can load the relevant skill on demand.
- The local Aegis checkout remains available for workspace support.
- OpenClaw does not present Aegis as a full runtime platform, authoritative
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

If OpenClaw exposes or you choose a separate skill discovery directory, also
verify it:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root <openclaw-skill-discovery-root>
```

## Updating

### macOS / Linux

```bash
cd ~/.openclaw/aegis
git pull
openclaw skills install ./skills/using-aegis --as using-aegis --global --force
openclaw skills install ./skills/systematic-debugging --as systematic-debugging --global --force
openclaw skills install ./skills/brainstorming --as brainstorming --global --force
python scripts/aegis-doctor.py --write-config --json
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.openclaw\aegis"
git pull
openclaw skills install .\skills\using-aegis --as using-aegis --global --force
openclaw skills install .\skills\systematic-debugging --as systematic-debugging --global --force
openclaw skills install .\skills\brainstorming --as brainstorming --global --force
python scripts/aegis-doctor.py --write-config --json
```

Restart OpenClaw or start a new session after updating.

## Activation Mode

OpenClaw uses native skill discovery. It does not currently use an Aegis
bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override OpenClaw's own
skill matcher by itself. For explicit use, ask OpenClaw to load an Aegis skill
directly or use the OpenClaw skill command surface when available.

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

Restart OpenClaw or start a new session after changing local Aegis config. For
this host, the command does not override OpenClaw's native matcher.

## Troubleshooting

### Git repository install does not install all Aegis skills

Use the local-directory install shown above. OpenClaw's Git and local directory
installer expects `SKILL.md` at the source root. Aegis stores many skills under
`skills/<skill-name>/SKILL.md`, so the stable path is to install the individual
skill directories.

### Skills are not visible

1. Confirm each installed skill source root contains `SKILL.md`.
2. Run `openclaw skills list`.
3. Run `openclaw skills check`.
4. Restart OpenClaw or start a new session.
5. Check whether a workspace skill with the same name is taking precedence.

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

## Official OpenClaw References

- https://docs.openclaw.ai/cli/skills
