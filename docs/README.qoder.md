# Aegis for Qoder

Guide for using Aegis with Qoder through Qoder's native skills, rules, and
project guidance surfaces.

This page only covers the Qoder host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Qoder is structurally compatible with Aegis because current official Qoder
guidance supports:

- global skills under `~/.qoder/skills/`
- project skills under `.qoder/skills/`
- project rules under `.qoder/rules/`
- repository guidance through `AGENTS.md`

This lets Aegis project its skill and rule discipline into Qoder without
changing the method-pack boundary.

This guide records structural compatibility and native install support. It does not claim current release-level live smoke evidence.

## Recommended Complete Installation

Keep a local Aegis checkout and expose the method-pack through Qoder's native
skill surfaces. This preserves both skill discovery and project workspace
support verification.

## Global Installation

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.qoder/aegis
mkdir -p ~/.qoder/skills
cp -R ~/.qoder/aegis/skills/* ~/.qoder/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.qoder\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.qoder\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.qoder\aegis\skills\*" "$env:USERPROFILE\.qoder\skills\"
```

The copy puts each Aegis skill directly at:

```text
~/.qoder/skills/<skill-name>/SKILL.md
```

Because the checkout remains at `~/.qoder/aegis`, project workspace support can
be verified from that method-pack root.

## Project-Local Installation

Inside a project where you want Aegis to be available:

```bash
mkdir -p .qoder/skills
cp -R /path/to/Aegis/skills/* .qoder/skills/
```

Use a project-local install when you want Aegis scoped to one repository
instead of every Qoder session on the machine.

## Rules and Project Guidance

Qoder can also load:

- `.qoder/rules/`
- `AGENTS.md`

For Aegis, keep detailed workflow logic in `skills/`. Use `.qoder/rules/` or
`AGENTS.md` only to reinforce routing, owner, and boundary discipline.

## Verification

Restart Qoder or start a new session, then ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

Expected result:

- Qoder can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`
- Qoder can load the relevant skill on demand
- `AGENTS.md` and `.qoder/rules/` can reinforce repository-specific guidance
- Aegis remains method-pack discipline, not a full runtime platform or final
  completion authority

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

For complete-install verification, also run this from the local Aegis checkout
when filesystem access is available:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

## Updating

### macOS / Linux

```bash
cd ~/.qoder/aegis
git pull
cp -R ~/.qoder/aegis/skills/* ~/.qoder/skills/
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.qoder\aegis"
git pull
Copy-Item -Recurse -Force "$env:USERPROFILE\.qoder\aegis\skills\*" "$env:USERPROFILE\.qoder\skills\"
```

Restart Qoder after updating.

## Activation Mode

Qoder uses native skill discovery and rules loading. This repository does not
currently ship a Qoder-specific bootstrap hook.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override Qoder's own
matcher by itself. For explicit use, ask Qoder to load an Aegis skill directly,
or name the relevant skill in your request.

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

Restart Qoder or start a new session after changing local Aegis config. For
this host, the command does not override Qoder's native matcher.

## Uninstalling

Remove the copied Aegis skill directories from:

```text
~/.qoder/skills/
```

If you installed only Aegis into that directory, remove the directory contents
and then restart Qoder. If you also keep personal skills there, delete only the
Aegis skill folders you copied from this repository.

## Troubleshooting

### Skills are not visible

1. Confirm a copied skill exists at `~/.qoder/skills/<skill-name>/SKILL.md` or
   `.qoder/skills/<skill-name>/SKILL.md`.
2. Restart Qoder or start a new session.
3. Check whether a project-local skill with the same name is taking precedence.
4. Keep detailed workflow logic in the skill body instead of only in
   `.qoder/rules/`.

### Project workspace support not verified

If only `skills/` were copied and the local checkout was removed, skill
discovery may still work but complete project workspace support is not proven.
Restore the checkout and run this from the method-pack root, not from the
target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.

## Official Qoder References

- https://docs.qoder.com/extensions/subagent
- https://docs.qoder.com/user-guide/rules
