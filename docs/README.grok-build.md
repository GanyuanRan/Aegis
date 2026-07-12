# Aegis for Grok Build

Guide for using Aegis with Grok Build through Grok's native skill discovery.

This page only covers the Grok Build host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Grok Build is structurally compatible with Aegis. Grok discovers skills from:

```text
./.grok/skills/
$GROK_HOME/skills/  (default: ~/.grok/skills/)
enabled plugin skills/
extra paths declared by [skills] paths in ~/.grok/config.toml
~/.agents/skills/
```

Grok also reads `AGENTS.md` and Claude Code compatibility surfaces, including
Claude skills and plugins. These overlapping discovery routes make duplicate
Aegis exposure possible. Use one canonical Aegis install path for Grok; do not
enable the updater-managed native path, an extra `[skills] paths` entry, and a
Claude-compatible Aegis plugin at the same time.

This guide recommends Grok's native user-level skill root:

```text
$GROK_HOME/skills/<skill-name>/SKILL.md
```

or, when `GROK_HOME` is unset:

```text
~/.grok/skills/<skill-name>/SKILL.md
```

Current development evidence confirms that `grok inspect --json` can enumerate
Aegis skills and Aegis guidance on Grok Build. This is structural discovery
evidence, not a release-level clean-install and live-trigger closeout.

Official references:

- https://docs.x.ai/build/overview
- https://docs.x.ai/build/features/skills-plugins-marketplaces
- https://docs.x.ai/build/settings
- https://docs.x.ai/build/settings/reference
- https://docs.x.ai/build/cli/reference

## Recommended Installation (Updater-Managed Direct-Child)

Keep one Aegis method-pack checkout as the canonical source, then register
Grok Build with Aegis's host-scoped updater. The host names `grok` and
`grok-build` default to:

- discovery shape: `direct-child`
- discovery root: `$GROK_HOME/skills` or `~/.grok/skills`

The updater creates one generated host-visible link per Aegis skill, records
the Grok installation, and runs method-pack-side doctor verification.

### macOS / Linux / WSL

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host grok-build \
  --sync-mode symlink \
  --reload-hint "restart Grok Build"
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
Set-Location "$env:USERPROFILE\.codex\aegis"
python scripts\aegis-update.py register `
  --host grok-build `
  --sync-mode junction `
  --reload-hint "restart Grok Build"
```

If `GROK_HOME` is set, the updater uses `<GROK_HOME>/skills`. Otherwise it uses
`~/.grok/skills` (or `%USERPROFILE%\.grok\skills` on Windows).

Expected structural result:

```text
~/.grok/skills/using-aegis/SKILL.md
~/.grok/skills/systematic-debugging/SKILL.md
~/.grok/skills/brainstorming/SKILL.md
~/.grok/skills/update-aegis/SKILL.md
```

The canonical source remains `<aegis-method-pack-root>/skills`. Direct-child
entries under the Grok skill root are generated links, not a second editable
skill owner.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. Slash-style aliases are
optional and depend on the current Grok session's command surface.

## Alternative: Explicit Grok Config

Grok can read additional skill directories from its user config:

```text
~/.grok/config.toml
```

Windows uses:

```text
%USERPROFILE%\.grok\config.toml
```

Example:

```toml
[skills]
paths = ["/absolute/path/to/Aegis/skills"]
```

Windows example using forward slashes:

```toml
[skills]
paths = ["C:/Users/<user>/.codex/aegis/skills"]
```

After editing the config, run:

```bash
grok inspect --json
```

This config path is a supported alternative when you want Grok to read the
canonical Aegis skill tree directly. Do not also create updater-managed Aegis
entries under `~/.grok/skills` or enable a Claude-compatible Aegis plugin for
the same Grok profile.

When using this alternative, register the checkout for host-scoped updates
without asking Aegis to manage Grok's config file:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host grok-build \
  --sync-mode repo-only \
  --discovery-shape host-managed \
  --reload-hint "restart Grok Build"
```

## Claude-Compatible Plugin Alternative

Grok documents Claude Code compatibility and can read Claude-compatible plugin
surfaces. Aegis already ships `.claude-plugin/` metadata, so an existing Claude
plugin installation may be visible to Grok without a Grok-specific manifest.

Treat this as an alternative, not an additional install. If Grok already sees
the Aegis Claude plugin in `grok inspect --json`, do not also expose Aegis via
`~/.grok/skills` or `[skills] paths`.

## Complete-Install Verification

Run Aegis verification from the installed method-pack root, not from the target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
python scripts/aegis-doctor.py --discovery-root "${GROK_HOME:-$HOME/.grok}/skills"
```

PowerShell:

```powershell
Set-Location "$env:USERPROFILE\.codex\aegis"
$grokSkills = if ($env:GROK_HOME) {
  Join-Path $env:GROK_HOME "skills"
} else {
  Join-Path $env:USERPROFILE ".grok\skills"
}
python scripts\aegis-doctor.py --write-config --json
python scripts\aegis-doctor.py --discovery-root $grokSkills
```

Treat the Aegis install as complete only when the JSON includes:

```json
{
  "ok": true,
  "workspaceSupport": "available",
  "configStatus": "configured"
}
```

Then verify Grok's own discovery view:

```bash
grok inspect --json
```

Check that:

- `using-aegis`, `systematic-debugging`, `brainstorming`, and `update-aegis`
  are present
- each Aegis skill name has one canonical source
- `AGENTS.md` is visible for repository-specific guidance when present
- no stale Claude plugin cache or shared skill root exposes a second Aegis copy

Restart Grok Build or start a new session after changing skill exposure.

## Updating Aegis

From the method-pack root:

```bash
python scripts/aegis-update.py status --host grok-build --json
python scripts/aegis-update.py update --host grok-build --json
```

The update registry is host-scoped. Do not use `--all` unless you explicitly
intend to update every registered host.

Grok Build itself has a separate host update command:

```bash
grok update
```

`grok update` updates Grok Build; `aegis-update.py` updates Aegis. They have
different owners and should not be conflated.

## Activation And TDD Modes

Aegis configuration remains user-local to Aegis:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
python scripts/aegis-doctor.py tdd-mode off
```

Aegis local configuration does not override Grok Build's native semantic
matcher or permission mode. TDD mode defaults to `off`; completion verification
still applies.

## Troubleshooting

### Duplicate Aegis skills

Run `grok inspect --json` and inspect each Aegis skill's source. Keep one of:

1. updater-managed `$GROK_HOME/skills`
2. `[skills] paths` pointing at the canonical method-pack `skills/`
3. a Claude-compatible Aegis plugin

Remove or disable the other exposure routes, then restart Grok Build. Do not
edit generated skill links as if they were a second source tree.

### Skills are not visible

1. Confirm `$GROK_HOME/skills/<skill-name>/SKILL.md` exists.
2. Run `python scripts/aegis-doctor.py --discovery-root <grok-skills-root>`
   from the method-pack root.
3. Run `grok inspect --json` in the target repository.
4. Restart Grok Build or start a new session.

### Project workspace support is not verified

Skill discovery alone does not prove that Aegis workspace helper support is
available. Keep the complete method-pack checkout and run:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

## Authority Boundary

Aegis remains a method pack. Grok owns host discovery, native skill matching,
plugins, permissions, sessions, and reload behavior. Aegis may provide workflow
discipline, runtime-ready drafts, hints, and projections, but it does not
provide authoritative `GateDecision`, authoritative `PolicySnapshot`, or final
completion authority.
