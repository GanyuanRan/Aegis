# Aegis for Pi CLI

Guide for using Aegis with Pi CLI through Pi's Agent Skills and package
system.

This page only covers the Pi host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Pi CLI is skills-compatible with Aegis because Pi discovers Agent Skills from:

- global skills under `~/.pi/agent/skills/` and `~/.agents/skills/`
- project skills under `.pi/skills/` and `.agents/skills/`
- package `skills/` directories or `pi.skills` entries in `package.json`
- explicit CLI paths passed with `--skill <path>`

Aegis now exposes its `skills/` directory through the repository root
`package.json` as a Pi package resource. This makes the Pi package path the
recommended structural installation path.

This guide records structural compatibility and package-based install support.
It does **not** claim current release-level live smoke evidence for Pi CLI.

## Prerequisites

Install Pi CLI using the command documented by Pi:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Then authenticate Pi with `/login` or a provider API key according to your Pi
setup.

## Recommended Complete Installation

Install Aegis as a Pi package:

```bash
pi install git:github.com/GanyuanRan/Aegis
```

This lets Pi load Aegis skills from the package `skills/` directory declared by
the repository root `package.json`.

Pi normally clones global git packages under:

```text
~/.pi/agent/git/github.com/GanyuanRan/Aegis
```

If your Pi release uses a different package cache path, run `pi list` or check
`~/.pi/agent/settings.json`, then use the resolved package checkout as
`<aegis-method-pack-root>`.

Across hosts, that resolved `<aegis-method-pack-root>` should be treated as the
canonical Aegis body. Any copied skill directories under `~/.pi/agent/skills/`,
`.pi/skills/`, or `~/.agents/skills/` are compatibility views, not second
editable owners.

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

## Alternative Skill Directory Installation

Pi also discovers direct skill directories. If you prefer a transparent local
checkout instead of Pi package management:

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.pi/agent/aegis
mkdir -p ~/.pi/agent/skills
cp -R ~/.pi/agent/aegis/skills/* ~/.pi/agent/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.pi\agent\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.pi\agent\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.pi\agent\aegis\skills\*" "$env:USERPROFILE\.pi\agent\skills\"
```

The copy exposes each Aegis skill as:

```text
~/.pi/agent/skills/<skill-name>/SKILL.md
```

Pi also scans `~/.agents/skills/`, so an existing Codex-style Aegis install can
make the same skills visible to Pi. That proves skill discovery, but complete
workspace support still depends on keeping the Aegis method-pack root available
and verified with `aegis-doctor.py`.

Project-local installation is also possible:

```bash
mkdir -p .pi/skills
cp -R /path/to/Aegis/skills/* .pi/skills/
```

Use project-local installation only when you want Aegis scoped to one project.

## Verification

Restart Pi, run `/reload`, or start a new Pi session after installing.

If skill commands are enabled, load the entry skill:

```text
/skill:using-aegis
```

You can also ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

Expected result:

- Pi can see Aegis skills such as `using-aegis`, `systematic-debugging`, and
  `brainstorming`.
- Pi can load the relevant skill on demand.
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

When Aegis is installed as a Pi package, use Pi's package update flow first:

```bash
pi update --extensions
```

Then verify from the resolved Aegis method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

You can also register the Pi installation with Aegis's host-scoped updater:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host pi \
  --sync-mode repo-only \
  --reload-hint "restart Pi or run /reload"
python scripts/aegis-update.py update --host pi --json
```

The equivalent one-line registration begins with
`python scripts/aegis-update.py register --host pi`.

When `~/.config/aegis/config.toml` already declares `method_pack_root`, the
shared Aegis updater now prefers that canonical root for host registration by
default. Align Pi package/cache installs with that root when you want Pi and
other hosts to share one Aegis body.

For copy-based installs, update the checkout and copy skills again:

```bash
cd ~/.pi/agent/aegis
git pull
cp -R ~/.pi/agent/aegis/skills/* ~/.pi/agent/skills/
python scripts/aegis-doctor.py --write-config --json
```

Or register the copy-based compatibility exposure explicitly:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host pi-copy \
  --sync-mode copy-skills \
  --discovery-shape direct-child \
  --discovery-root ~/.pi/agent/skills \
  --reload-hint "restart Pi or run /reload"
python scripts/aegis-update.py update --host pi-copy --json
```

Restart Pi or run `/reload` after updating so the host reloads skill metadata.

## Activation Mode

Pi uses native skill discovery and routing. It does not currently use an Aegis
bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override Pi's own skill
matcher by itself. For explicit use, ask Pi to load an Aegis skill directly,
such as `/skill:using-aegis`, or name the skill in your request.

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

Restart Pi or run `/reload` after changing local Aegis config. For this host,
the command does not override Pi's native matcher.

## Uninstalling

For package installs:

```bash
pi remove git:github.com/GanyuanRan/Aegis
```

If your Pi settings pinned a specific URL or ref, remove the same package source
shown by `pi list`.

For copy-based installs, remove the copied Aegis skill directories from:

```text
~/.pi/agent/skills/
```

If you also keep personal skills there, delete only the Aegis skill folders
copied from this repository.

## Troubleshooting

### Skills are not visible

1. Run `pi list` and confirm Aegis is listed if you used package install.
2. Confirm the installed package checkout contains `skills/using-aegis/SKILL.md`.
3. Restart Pi, run `/reload`, or start a new session.
4. Check for a project-local skill with the same name taking precedence.
5. If you copied skills manually, confirm each skill directory contains
   `SKILL.md`.

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

### Package install path differs

Pi's package cache is host-managed. If
`~/.pi/agent/git/github.com/GanyuanRan/Aegis` is not present, inspect
`~/.pi/agent/settings.json` or run `pi list` to locate the package source, then
use that resolved checkout as `<aegis-method-pack-root>`.

## Official Pi References

- https://pi.dev/docs/latest/quickstart
- https://pi.dev/docs/latest/skills
- https://pi.dev/docs/latest/packages
