# Aegis for ZCode

Guide for using Aegis with ZCode through ZCode's native Claude-Code-compatible
plugin marketplace and `SKILL.md` skill system.

This page only covers the ZCode host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

ZCode is structurally compatible with Aegis because current official ZCode
guidance supports:

- a plugin marketplace that natively reads `.claude-plugin/marketplace.json`
  (Claude Code plugin format)
- skills defined by a `SKILL.md` file, invoked through the `@`-prefix picker
- repository guidance through `AGENTS.md`
- memory, plugin, command, hook, and MCP extension surfaces

This lets Aegis project its skill, rule, and plugin discipline into ZCode
without changing the method-pack boundary. Because ZCode natively reads the
Claude Code plugin format, Aegis's existing `.claude-plugin/` skeleton works
with zero code changes.

This guide records structural compatibility and native install support. It
does not claim current release-level live smoke evidence.

## Recommended Complete Installation

Keep a local Aegis checkout and expose the method-pack through ZCode's native
plugin marketplace flow. This preserves both skill discovery and project
workspace support verification.

The marketplace-install path copies Aegis into ZCode's plugin cache. The local
Aegis checkout remains the canonical method-pack root for doctor checks and
workspace helpers.

## Plugin Marketplace Installation

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

For local development or smoke testing from a checked-out copy, point the
marketplace at the local checkout:

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/Aegis
```

```text
/plugin marketplace add /home/<user>/Aegis
/plugin install aegis@aegis-dev --scope user
/reload-plugins
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\Aegis"
```

```text
/plugin marketplace add C:\Users\<user>\Aegis
/plugin install aegis@aegis-dev --scope user
/reload-plugins
```

Use `--scope project` only when you intentionally want the project to record
the plugin. Use `--scope local` for machine-local testing.

## Rules and Project Guidance

ZCode can also load:

- `AGENTS.md`
- ZCode Memory files (project conventions and code standards)

For Aegis, keep detailed workflow logic in `skills/`. Use `AGENTS.md` or
ZCode Memory only to reinforce routing, owner, and boundary discipline.

## Verification

Restart ZCode or start a new session, then open the `@`-prefix skill picker
or ask:

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

For complete-install verification, run this from the local Aegis checkout
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

Marketplace-installed plugins are copied into ZCode's plugin cache. Update
from ZCode's plugin manager or reinstall after the repository changes:

```text
/plugin install aegis@aegis-dev --scope user
/reload-plugins
```

For a local-development checkout, pull updates from the method-pack root:

```bash
cd <aegis-method-pack-root>
git pull
/reload-plugins
```

## Activation Mode

ZCode uses native skill discovery through the `@`-prefix picker. This
repository does not currently ship a ZCode-specific bootstrap hook.

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

```text
/plugin uninstall aegis@aegis-dev
```

If you also want to remove the marketplace source:

```text
/plugin marketplace remove aegis-dev
```

For a local-development checkout, remove the cloned Aegis directory after
uninstalling the plugin.

## Troubleshooting

### Skills are not visible

1. Confirm the `aegis` plugin appears in ZCode's plugin manager.
2. Run `/reload-plugins` or restart ZCode.
3. Re-open the `@`-prefix skill picker and look for Aegis skills.
4. Confirm the installed plugin cache contains the `skills/` directory.

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
