# Aegis for ZCode

Guide for using Aegis with ZCode through ZCode's native skill discovery and its
Claude-Code-compatible plugin marketplace.

This page only covers the ZCode host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

ZCode is structurally compatible with Aegis because ZCode discovers skills
defined by a `SKILL.md` file under user-level and project-level roots such as
`~/.agents/skills/`, `~/.zcode/skills/`, `.zcode/skills/`, and `.agents/skills/`,
and reads repository guidance through `AGENTS.md`.

ZCode's skill scanner reads each root's *direct* subdirectories and expects:

```text
<root>/<skill-name>/SKILL.md
```

This is a depth-1 scan, like CC GUI and Windsurf. An umbrella directory such as:

```text
~/.agents/skills/aegis/ -> ~/.codex/aegis/skills/
```

does **not** work for ZCode, because `aegis/` does not itself contain a
`SKILL.md`; the real skills live one level deeper. Use the direct-child
installation below instead.

ZCode also exposes a plugin marketplace that natively reads
`.claude-plugin/marketplace.json` (Claude Code plugin format), plus memory,
command, hook, and MCP extension surfaces.

This guide records structural compatibility and native install support. It does
not claim current release-level live smoke evidence.

## Recommended Installation (Updater-Managed Direct-Child)

Keep the Aegis method-pack checkout separate, then register ZCode with Aegis's
host-scoped updater. When the host is recognized as `zcode`, the updater defaults
the discovery shape to `direct-child`, creates the skill links under
`~/.agents/skills/`, writes the host registry entry, and runs doctor
verification in one step.

This preserves:

- ZCode depth-1 skill discovery through direct `SKILL.md` directories
- Aegis project workspace support through the method-pack root
- update and doctor verification through Aegis scripts

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host zcode \
  --sync-mode junction \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart ZCode"
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
Set-Location "$env:USERPROFILE\.codex\aegis"
python scripts\aegis-update.py register `
  --host zcode `
  --sync-mode junction `
  --discovery-root "$env:USERPROFILE\.agents\skills" `
  --reload-hint "restart ZCode"
```

Expected structural result:

```text
~/.agents/skills/using-aegis/SKILL.md
~/.agents/skills/systematic-debugging/SKILL.md
~/.agents/skills/brainstorming/SKILL.md
```

The canonical source of truth remains the method-pack root `skills/` tree. These
direct-child directories are a compatibility exposure for ZCode's depth-1
scanner, not a second editable skill tree.

### Manual Fallback (Not Recommended)

Use this only when the updater is unavailable. The updater-managed path above is
preferred because it also records the host registry entry, prunes retired Aegis
links, and runs doctor verification.

macOS / Linux:

```bash
mkdir -p ~/.agents/skills
for skill_dir in ~/.codex/aegis/skills/*; do
  [ -d "$skill_dir" ] || continue
  ln -sfn "$skill_dir" "$HOME/.agents/skills/$(basename "$skill_dir")"
done
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
Get-ChildItem "$env:USERPROFILE\.codex\aegis\skills" -Directory | ForEach-Object {
  $target = Join-Path "$env:USERPROFILE\.agents\skills" $_.Name
  if (-not (Test-Path -LiteralPath $target)) {
    cmd /c mklink /J "$target" "$($_.FullName)"
  }
}
```

## Plugin Marketplace Installation (Alternative)

ZCode's plugin marketplace also reads `.claude-plugin/marketplace.json`
natively, so Aegis's existing plugin skeleton works without code changes.

### macOS / Linux

Inside ZCode, add the repository-backed marketplace:

```text
/plugin marketplace add GanyuanRan/Aegis
```

Then install Aegis from the marketplace name declared in
`.claude-plugin/marketplace.json`:

```text
/plugin install aegis@aegis-dev --scope user
```

Reload plugins or restart ZCode:

```text
/reload-plugins
```

### Windows PowerShell

For local development or smoke testing from a checked-out copy:

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\Aegis"
```

```text
/plugin marketplace add C:\Users\<user>\Aegis
/plugin install aegis@aegis-dev --scope user
/reload-plugins
```

If plugin-cache skill discovery does not expose all Aegis skills after this
install, use the direct-child installation above, which is the verified
structural path for ZCode's depth-1 scanner.

## Rules and Project Guidance

ZCode can also load:

- `AGENTS.md`
- ZCode Memory files (project conventions and code standards)

For Aegis, keep detailed workflow logic in `skills/`. Use `AGENTS.md` or ZCode
Memory only to reinforce routing, owner, and boundary discipline.

## Verification

Restart ZCode or start a new session, then open the `@`-prefix skill picker or
ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

Expected result:

- ZCode can see Aegis skills such as `using-aegis`, `systematic-debugging`,
  and `brainstorming`
- ZCode can load the relevant skill on demand through the `@`-prefix picker
- `AGENTS.md` and ZCode Memory can reinforce repository-specific guidance
- Aegis remains method-pack discipline, not a full runtime platform,
  authoritative `GateDecision`, or final completion authority

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

For complete-install verification, run this from the local Aegis checkout:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

For ZCode skill discovery, also verify the discovery root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root ~/.agents/skills
```

PowerShell:

```powershell
Set-Location "$env:USERPROFILE\.codex\aegis"
python scripts\aegis-doctor.py --discovery-root "$env:USERPROFILE\.agents\skills"
```

## Updating

For registered direct-child installs, the updater refreshes the method-pack
checkout, keeps the direct-child links current, prunes retired Aegis links, and
runs doctor verification:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py update --host zcode --json
```

If the installation was created manually, register it once. For `--host zcode`,
the updater defaults `discoveryShape` to `direct-child`, so no explicit
`--discovery-shape` flag is required:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host zcode \
  --sync-mode junction \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart ZCode"
```

The update skill form is `aegis:update`. It uses the same host-scoped registry
and updates only the current host unless the user explicitly asks for `--all`.

For marketplace installs, reinstall after the repository changes:

```text
/plugin install aegis@aegis-dev --scope user
/reload-plugins
```

## Activation Mode

ZCode uses native skill discovery through the `@`-prefix picker. It does not
currently use an Aegis bootstrap hook from this repository.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override ZCode's own
matcher by itself. For explicit use, ask ZCode to load an Aegis skill directly,
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

Restart ZCode or start a new session after changing local Aegis config. For
this host, the command does not override ZCode's native matcher.

## Uninstalling

For direct-child installs, remove the Aegis skill directories from:

```text
~/.agents/skills/
```

If you installed only Aegis into that directory, remove the Aegis skill folders
and restart ZCode. If you also keep personal skills there, delete only the
Aegis skill folders that point into `~/.codex/aegis/skills/`.

For marketplace installs:

```text
/plugin uninstall aegis@aegis-dev
/plugin marketplace remove aegis-dev
```

## Troubleshooting

### Skills are not visible (umbrella symlink pitfall)

Do not use the Codex umbrella symlink (`~/.agents/skills/aegis/ ->
~/.codex/aegis/skills/`) for ZCode. ZCode's depth-1 scanner expects each
direct child of `~/.agents/skills/` to contain a `SKILL.md`. The umbrella
`aegis/` directory does not, so ZCode discovers zero Aegis skills.

Use the direct-child installation above instead, which exposes each Aegis skill
as `~/.agents/skills/<skill-name>/SKILL.md`. This is the same shape CC GUI and
Windsurf require.

### Skills are not visible (general)

1. Confirm that direct skill directories exist:
   `~/.agents/skills/<skill-name>/SKILL.md`.
2. Avoid relying only on the umbrella directory for ZCode skill discovery.
3. Restart ZCode or start a new session.
4. Re-open the `@`-prefix skill picker and look for Aegis skills.
5. Run `python scripts/aegis-doctor.py --discovery-root ~/.agents/skills` from
   the Aegis method-pack root.

### Project workspace support not verified

Skill visibility alone does not prove complete project workspace support.
Confirm the local checkout still contains the repository scripts, then run the
doctor command from that method-pack root, not from the target project
directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.

### Marketplace cannot be added

1. Verify repository access with `git ls-remote https://github.com/GanyuanRan/Aegis.git`.
2. Confirm `.claude-plugin/marketplace.json` exists in the repository root.
3. Confirm the marketplace name is `aegis-dev`.

## Official ZCode References

- https://zcode.z.ai/cn/docs/plugin
- https://zcode.z.ai/cn/docs/skill
