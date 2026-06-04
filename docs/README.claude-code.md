# Aegis for Claude Code

Guide for using Aegis with Claude Code through Claude Code's plugin marketplace flow.

This page only covers the Claude Code host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Aegis has a Claude Code plugin distribution skeleton:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `skills/`
- `agents/`
- `commands/`
- `hooks/`

This means Claude Code is a supported product target. It does **not** mean
Claude Code has current release-level fresh smoke evidence yet. The current
compatibility matrix still records Claude Code as pending broader host rollout.

In current compatibility terminology, Claude Code is treated as a
`hook-bootstrap` host: automatic Aegis entry depends mainly on the plugin's
startup hook and reload behavior. This label is a diagnostic aid only; the
Claude Code guide remains the canonical install authority for this host.

## Repository Access Prerequisite

Claude Code installation requires GitHub read access to the repository. Public
repository installs normally need no special access beyond standard network and
GitHub availability. Private forks still require the relevant GitHub access.

Verify access before installing:

```bash
git ls-remote https://github.com/GanyuanRan/Aegis.git
```

If this fails, fix GitHub authentication first. Do not paste personal access
tokens into documentation, shell history, or Claude Code settings.

## Marketplace Installation

Inside Claude Code, add the repository-backed marketplace:

```text
/plugin marketplace add GanyuanRan/Aegis
```

Then install Aegis from the marketplace name declared in
`.claude-plugin/marketplace.json`:

```text
/plugin install aegis@aegis-dev --scope user
```

Reload plugins or restart Claude Code:

```text
/reload-plugins
```

Equivalent CLI form:

```bash
claude plugin marketplace add GanyuanRan/Aegis
claude plugin install aegis@aegis-dev --scope user
```

Use `--scope project` only when you intentionally want the project to record
the plugin in `.claude/settings.json`. Use `--scope local` for machine-local
testing.

### Activation Mode

Aegis defaults to automatic mode. To switch Claude Code to explicit mode, edit:

```text
~/.config/aegis/config.toml
```

Windows:

```text
%USERPROFILE%\.config\aegis\config.toml
```

If the file does not exist, create it manually. Add:

```toml
activation_mode = "explicit"
```

You can also write the same config from the installed Aegis method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

Switch back to automatic mode with:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Then restart Claude Code or reload the plugin session. `AEGIS_ACTIVATION_MODE`
remains available as an environment-variable override for one-off runs:

```bash
AEGIS_ACTIVATION_MODE=explicit claude
```

It is not a field in this repository's plugin metadata. Environment variables
override the user-local config when both are set.

In `explicit` mode, the hook does not inject the compact `using-aegis`
bootstrap. The plugin and skills remain installed, so users can still call
`/aegis:using-aegis` or another Aegis skill directly.

Portable goal entry also works across hosts:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. Treat `/aegis-goal <task>` as
an optional shortcut only when the current host/session supports slash-style
aliases.

## Local Development Installation

For local development or smoke testing from a checked-out copy:

```bash
claude --plugin-dir /path/to/Aegis
```

On Windows PowerShell:

```powershell
claude --plugin-dir "X:\path\to\Aegis"
```

This loads the local plugin for that Claude Code session without installing it
into the user or project plugin cache.

## Verification

After installation, verify the plugin is visible:

```text
/help
```

Then test one namespaced skill:

```text
/aegis:using-aegis
```

You can also ask:

```text
Tell me about your Aegis skills and which one you would use before debugging a failing test.
```

When filesystem access to the installed plugin cache or local `--plugin-dir` is
available, run complete-install verification from the method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

Expected result:

- Claude Code can see the `aegis` plugin namespace.
- Aegis skills are listed or callable under the `aegis:` namespace.
- Project workspace support can be verified when the installed method-pack root
  remains available.
- Claude Code does not present Aegis as a full runtime platform or final
  completion authority.

For this host, the plugin-managed install path is the canonical path. If other
compatibility exposure shapes are added for different hosts, they should be
treated as generated compatibility views from the canonical method-pack root,
not as a second editable skill source for Claude Code.

## Updating

Marketplace-installed plugins are copied into Claude Code's plugin cache.
Update from Claude Code's plugin manager or reinstall after the repository
changes.

For local development with `--plugin-dir`, restart Claude Code or run:

```text
/reload-plugins
```

## Uninstalling

```bash
claude plugin uninstall aegis@aegis-dev --scope user
```

If you installed with another scope, pass the same scope when uninstalling.

## Troubleshooting

### No plugin commands

If Claude Code does not recognize `/plugin`, update Claude Code to a version
that supports plugins.

### Marketplace cannot be added

1. Verify repository access with `git ls-remote`.
2. Confirm `.claude-plugin/marketplace.json` exists in the repository root.
3. Confirm the marketplace name is `aegis-dev`.

### Plugin installs but skills are not visible

1. Run `/reload-plugins`.
2. Check `/help` for `aegis:` entries.
3. Confirm the installed plugin cache contains the `skills/` directory.

### Project workspace support not verified

Skill visibility alone does not prove complete project workspace support.
Confirm the installed plugin cache or local `--plugin-dir` still contains the
repository scripts, then run the doctor command from that method-pack root,
not from the target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and `"configStatus":
"configured"`.

### Windows hook behavior

Claude Code hooks on Windows use the wrapper documented in:

- `docs/windows/polyglot-hooks.md`

Git for Windows should be installed so the wrapper can find Git Bash.

### WSL2 startup hook permission denied

If a `v1.1.0` or `v1.1.1` install reports:

```text
/bin/sh: .../hooks/run-hook.cmd: Permission denied
```

upgrade or reinstall Aegis. `v1.1.2` and newer ship the Claude Code hook
wrapper with the Unix executable bit required by Linux / WSL2 plugin caches.

Temporary workaround for an already-installed old plugin cache:

```bash
chmod +x ~/.claude/plugins/cache/aegis-dev/aegis/1.1.0/hooks/run-hook.cmd
```

Use the actual cached version directory if it differs from `1.1.0`.

### Bootstrap intentionally absent

If Aegis skills are installed but the startup reminder is missing, check whether
`AEGIS_ACTIVATION_MODE=explicit` is set. In explicit mode this is expected.

## Official Claude Code References

- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/plugin-marketplaces
- https://code.claude.com/docs/en/plugins-reference
