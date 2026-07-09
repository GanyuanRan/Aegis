# Aegis for CodeBuddy

Guide for using Aegis with CodeBuddy through CodeBuddy's native skills and
plugin-compatible distribution paths.

This page only covers the CodeBuddy host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

CodeBuddy is structurally compatible with Aegis because it supports:

- `SKILL.md` skills
- user and project skill directories
- plugin bundles that can include `skills/`, `commands/`, and `hooks/`
- a CodeBuddy plugin metadata directory
- compatibility with Claude Code plugin metadata

Aegis now ships a CodeBuddy plugin skeleton:

- `.codebuddy-plugin/plugin.json`
- `.codebuddy-plugin/marketplace.json`
- `skills/`
- `commands/`
- `hooks/`

This means CodeBuddy is a supported product target. It does **not** mean
CodeBuddy has current release-level fresh smoke evidence yet. The current
compatibility matrix still records CodeBuddy as pending broader host rollout.

## Recommended Complete Installation

Keep a local Aegis checkout and install skills from it. This preserves both
skill discovery and project workspace support verification.

## Manual Skills Installation

Use this path when you want the most transparent install without relying on a
marketplace flow.

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codebuddy/aegis
mkdir -p ~/.codebuddy/skills
cp -R ~/.codebuddy/aegis/skills/* ~/.codebuddy/skills/
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codebuddy\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.codebuddy\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.codebuddy\aegis\skills\*" "$env:USERPROFILE\.codebuddy\skills\"
```

The copy puts each Aegis skill directly at:

```text
~/.codebuddy/skills/<skill-name>/SKILL.md
```

Because the checkout remains at `~/.codebuddy/aegis`, project workspace support
can be verified from that method-pack root.

## Project-Local Installation

Inside a project where you want Aegis to be available:

```bash
mkdir -p .codebuddy/skills
cp -R /path/to/Aegis/skills/* .codebuddy/skills/
```

Use a project-local install when you want Aegis scoped to one repository instead
of every CodeBuddy session on the machine.

## Plugin Installation

CodeBuddy supports plugin metadata. Aegis provides `.codebuddy-plugin/` for the
CodeBuddy-specific path and keeps `.claude-plugin/` as a compatible fallback.

For local development or smoke testing from a checked-out copy, use CodeBuddy's
local plugin or marketplace flow for the repository, then restart or reload
CodeBuddy according to the host prompt.

If the plugin command is unavailable or fails on a local machine, use the manual
skills installation above and treat the plugin flow as pending environment
verification.

## Verification

After installation, start a new CodeBuddy session and ask:

```text
Tell me about your Aegis skills and which one you would use before debugging a failing test.
```

Then run complete-install verification from the local Aegis checkout:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

Expected result:

- CodeBuddy can see Aegis skills such as `using-aegis`,
  `systematic-debugging`, and `brainstorming`.
- CodeBuddy can load the relevant skill on demand.
- Project workspace support can be verified when the local checkout remains
  available.
- CodeBuddy does not present Aegis as a full runtime platform or final
  completion authority.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

## Updating

### macOS / Linux

```bash
cd ~/.codebuddy/aegis
git pull
cp -R ~/.codebuddy/aegis/skills/* ~/.codebuddy/skills/
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.codebuddy\aegis"
git pull
Copy-Item -Recurse -Force "$env:USERPROFILE\.codebuddy\aegis\skills\*" "$env:USERPROFILE\.codebuddy\skills\"
```

Restart CodeBuddy after updating.

## Activation Mode

CodeBuddy uses native skill discovery for manually installed skills. The
`.codebuddy-plugin/` metadata exists for plugin distribution, but this
repository does not currently ship a CodeBuddy-specific bootstrap hook.

That means `AEGIS_ACTIVATION_MODE=explicit` does not override CodeBuddy's own
skill matcher by itself. For explicit use, ask CodeBuddy to load an Aegis skill
directly, such as `using-aegis` or `systematic-debugging`.

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

Restart CodeBuddy or start a new session after changing local Aegis config.
For this host, the command does not override CodeBuddy's native matcher.

## Uninstalling

For manual skills installs, remove the copied Aegis skill directories from:

```text
~/.codebuddy/skills/
```

If you installed through a CodeBuddy plugin flow, uninstall through CodeBuddy's
plugin manager and then restart the host.

## Troubleshooting

### Skills are not visible

1. Confirm a copied skill exists at `~/.codebuddy/skills/<skill-name>/SKILL.md`
   or `.codebuddy/skills/<skill-name>/SKILL.md`.
2. Restart CodeBuddy or start a new session.
3. Ask CodeBuddy to list or describe available Aegis skills.
4. Check whether a project-local skill with the same name is taking precedence.

### Project workspace support not verified

If Aegis was installed by copying only `skills/`, the host may discover skills
but not prove complete project workspace support. Keep or restore the local
checkout, then run this from that checkout, not from the target project
directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.

### CodeBuddy CLI is installed but not runnable

If `codebuddy --version` or `codebuddy --help` fails, fix the local CodeBuddy
CLI installation before treating any live smoke as valid. A binary on `PATH`
is not enough to claim release-level host compatibility.

## Official CodeBuddy References

- https://www.codebuddy.ai/docs/cli/skills
- https://www.codebuddy.ai/docs/cli/plugins
- https://www.codebuddy.ai/docs/cli/plugins-reference
