# Aegis for Kimi Code CLI

Guide for using Aegis with Kimi Code CLI through Kimi's native Agent Skills
discovery.

This page only covers the Kimi Code CLI host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Kimi Code CLI is structurally compatible with Aegis because Kimi discovers
Agent Skills from user and project skill roots. The official Kimi Code CLI
Agent Skills docs list the user-level roots as:

```text
$KIMI_CODE_HOME/skills/  (default: ~/.kimi-code/skills/)
~/.agents/skills/
```

They also list project-level roots:

```text
.kimi-code/skills/
.agents/skills/
```

Kimi's own user-level root moves with `KIMI_CODE_HOME`; the generic
`~/.agents/skills/` root stays under the real OS home and is a cross-tool
sharing surface.

For Aegis, the recommended Kimi install path is Kimi's native user-level root:

```text
$KIMI_CODE_HOME/skills/<skill-name>/SKILL.md
```

The generic `~/.agents/skills/` root remains a compatibility fallback, not the
canonical Kimi Aegis path. Do not rely on the Codex umbrella symlink
`~/.agents/skills/aegis -> ~/.codex/aegis/skills` as the Kimi main path.

This guide records structural compatibility and native install support. It does
not claim current release-level live smoke evidence.

Official references:

- `https://moonshotai.github.io/kimi-code/en/customization/skills`
- `https://moonshotai.github.io/kimi-code/en/configuration/config-files.html`
- `https://moonshotai.github.io/kimi-code/en/reference/kimi-command.html`

## Recommended Installation (Updater-Managed Direct-Child)

Keep the Aegis method-pack checkout separate, then register Kimi Code CLI with
Aegis's host-scoped updater. When the host is registered as `kimi`,
`kimi-code`, or `kimi-code-cli`, the updater defaults the discovery shape to
`direct-child`. If `--discovery-root` is omitted, it uses:

```text
$KIMI_CODE_HOME/skills
```

or, when `KIMI_CODE_HOME` is unset:

```text
~/.kimi-code/skills
```

This preserves:

- Kimi native user-level Agent Skills discovery
- Aegis project workspace support through the method-pack root
- update and doctor verification through Aegis scripts
- `~/.agents/skills/` as an optional compatibility fallback

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --reload-hint "restart Kimi Code CLI"
```

If you want to be explicit about the discovery root:

```bash
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --discovery-root "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills" \
  --reload-hint "restart Kimi Code CLI"
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
Set-Location "$env:USERPROFILE\.codex\aegis"
$kimiSkills = if ($env:KIMI_CODE_HOME) {
  Join-Path $env:KIMI_CODE_HOME "skills"
} else {
  Join-Path $env:USERPROFILE ".kimi-code\skills"
}
python scripts\aegis-update.py register `
  --host kimi-code `
  --sync-mode junction `
  --discovery-root $kimiSkills `
  --reload-hint "restart Kimi Code CLI"
```

Expected structural result:

```text
~/.kimi-code/skills/using-aegis/SKILL.md
~/.kimi-code/skills/systematic-debugging/SKILL.md
~/.kimi-code/skills/brainstorming/SKILL.md
```

The canonical source of truth remains the method-pack root `skills/` tree.
These direct-child directories are a generated host view for Kimi, not a second
editable skill tree.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

## Complete-Install Verification

Run complete-install verification from the installed Aegis method-pack root.
Do not run the doctor command from the target project directory.

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
python scripts/aegis-doctor.py --discovery-root "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills"
```

Treat the install as complete only when the JSON includes:

```json
{
  "ok": true,
  "workspaceSupport": "available",
  "configStatus": "configured"
}
```

After verification, restart Kimi Code CLI so the running host reloads the
refreshed skill content.

## Updating Aegis

From the method-pack root:

```bash
python scripts/aegis-update.py status --json
python scripts/aegis-update.py update --host kimi-code --json
```

The update registry is host-scoped. Do not update every registered host unless
you explicitly intend to use `--all`.

## Compatibility Fallback

Kimi also scans `~/.agents/skills/`, so a generic direct-child exposure there
can work as a fallback:

```bash
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart Kimi Code CLI"
```

Use this only when you intentionally want a cross-tool shared skill surface.
For Kimi-specific installs, prefer `$KIMI_CODE_HOME/skills`.

## Activation Mode

You can make Aegis explicit-only:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

This writes Aegis method-pack configuration only. It does not override Kimi Code CLI.
It does not control Kimi Code CLI's native skill matcher, slash command behavior,
or automatic skill loading rules.

## Authority Boundary

Aegis remains a method pack. Kimi host discovery, reload behavior, and native
skill invocation are Kimi Code CLI concerns. Aegis may provide workflow
discipline, runtime-ready drafts, and verification guidance, but it does not
provide authoritative `GateDecision`, authoritative `PolicySnapshot`, or final
completion authority.
