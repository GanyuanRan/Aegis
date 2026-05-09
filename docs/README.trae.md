# Aegis for Trae

Guide for using Aegis with Trae through Trae's native `SKILL.md` discovery.

This page only covers the Trae host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Trae is skills-compatible with Aegis because Trae supports skills defined by a
`SKILL.md` file and stores skill directories in:

- project skills: `.trae/skills/`
- global skills on macOS / Linux: `~/.trae/skills`
- global skills on Windows: `%userprofile%/.trae/skills`

Trae also documents a `.agents/skills/` directory option. For Aegis, the
canonical Trae path is still the native `.trae/skills/` or `~/.trae/skills`
directory, because it is explicit to this host and avoids relying on an optional
compatibility setting.

This guide records structural compatibility and manual install support. It does
not claim current release-level live smoke evidence for Trae.

## Recommended Complete Installation

Keep a local Aegis checkout and copy skills from it. This preserves both skill
discovery and project workspace support verification.

## Global Installation

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.trae/aegis
mkdir -p ~/.trae/skills
cp -R ~/.trae/aegis/skills/* ~/.trae/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.trae\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.trae\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.trae\aegis\skills\*" "$env:USERPROFILE\.trae\skills\"
```

The copy puts each Aegis skill directly at:

```text
~/.trae/skills/<skill-name>/SKILL.md
```

Because the checkout remains at `~/.trae/aegis`, project workspace support can
be verified from that method-pack root.

## Project-Local Installation

Inside a project where you want Aegis to be available:

```bash
mkdir -p .trae/skills
cp -R /path/to/Aegis/skills/* .trae/skills/
```

Use a project-local install when you want Aegis scoped to one repository instead
of every Trae session on the machine.

## Verification

Restart Trae or start a new session, then ask:

```text
Tell me about your Aegis skills and which one you would use before debugging a failing test.
```

Expected result:

- Trae can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`.
- Trae can load the relevant skill on demand.
- Project workspace support can be verified when the local checkout remains
  available.
- Trae does not present Aegis as a full runtime platform or final completion
  authority.

## Updating

### macOS / Linux

```bash
cd ~/.trae/aegis
git pull
cp -R ~/.trae/aegis/skills/* ~/.trae/skills/
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.trae\aegis"
git pull
Copy-Item -Recurse -Force "$env:USERPROFILE\.trae\aegis\skills\*" "$env:USERPROFILE\.trae\skills\"
```

Restart Trae after updating.

## Activation Mode

Trae uses native skill discovery. It does not currently use an Aegis bootstrap
hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override Trae's own skill
matcher by itself. For explicit use, ask Trae to load an Aegis skill directly,
such as `using-aegis` or `systematic-debugging`.

## Uninstalling

Remove the copied Aegis skill directories from:

```text
~/.trae/skills/
```

If you installed only Aegis into that directory, remove the directory contents
and then restart Trae. If you also keep personal skills there, delete only the
Aegis skill folders you copied from this repository.

## Troubleshooting

### Skills are not visible

1. Confirm a copied skill exists at `~/.trae/skills/<skill-name>/SKILL.md` or
   `.trae/skills/<skill-name>/SKILL.md`.
2. Restart Trae or start a new session.
3. Check Trae's Rules & Skills settings.
4. Check whether a project-local skill with the same name is taking precedence.

### Project workspace support not verified

If only `skills/` were copied and the local checkout was removed, skill
discovery may still work but complete project workspace support is not proven.
Restore the checkout and run `python scripts/aegis-doctor.py --json`.

## Official Trae References

- https://docs.trae.ai/ide/skills
