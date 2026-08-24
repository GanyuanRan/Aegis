# Aegis for DeepSeek Harness

Guide for installing Aegis through the official DeepSeek Harness (`dsh`)
profile-plugin and filesystem-skill contracts.

This page covers the `deepseek-ai/deepseek-harness` host. It does not replace
`docs/README.deepseek-tui.md`; DeepSeek Harness and the community DeepSeek-TUI
are separate hosts with separate install roots and compatibility evidence.

For the current `Aegis Method Pack` authority order, release gate, host
compatibility status, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

The default DeepSeek Harness installation is the thin Aegis bundle declared by
the root `package.json` through `dsh.bundle.patch`. The bundle contributes one
Cordis row named `aegis-method-pack`; that row delegates discovery to Harness's
native filesystem skill provider and points it at the installed package's
canonical `skills/` tree. In `auto` activation mode it also listens to Harness's
native `agent/session-start` lifecycle and defers a compact `using-aegis`
routing bootstrap on `startup`, `resume`, `clear`, and `compact`: each boundary
only arms the injection, which is delivered once after the session's first
durable promotion signal (`tool/call` or `assistant/message`), so the first
model request of every gated epoch stays free of injected Aegis context. The
bootstrap is prepared while the plugin is applied, so the delayed injection
does not race an asynchronous skill-file read.

The bundle does not copy skill bodies, replace Harness's model-facing `skill`
tool, add a daemon, install a hard pre-tool guard, or claim runtime authority.
It tells the model to use Harness's native `skill` tool for task-specific Aegis
methods or declare `Route: fast-path`; DeepSeek Harness remains the owner of
profiles, plugin installation, the skill catalog, skill loading, and execution.

The previous updater-managed direct-child installation remains supported as an
**explicit compatibility mode**. The bundle and direct-child views must not be
active together because that creates duplicate skill owners and unreliable
routing evidence.

DeepSeek Harness is currently a developer preview and warns that compatibility
breaking changes are expected. This guide records implemented structural bundle
support; it does not claim current release-level live routing evidence.

## Prerequisites

Install a current DeepSeek Harness release and ensure `pnpm` is on `PATH`.
Harness forwards `dsh plugin` operations to `pnpm`, so being able to start the
Web UI through `npx` alone is not sufficient for profile-plugin management.

Verify both commands before installing Aegis:

```bash
dsh --version
pnpm --version
```

If Harness is normally launched through `npx`, the following equivalent form
may be used for the DSH commands below:

```bash
npx @deepseek-ai/dsh --version
```

## Default Bundle Installation

Install Aegis into every DSH profile that should expose it. For the Web profile:

```bash
dsh plugin --profile web add "git+https://github.com/GanyuanRan/Aegis.git"
```

For the Headless profile, install it separately:

```bash
dsh plugin --profile headless add "git+https://github.com/GanyuanRan/Aegis.git"
```

An `aegis` dependency that is installed in one profile is not automatically
active in another profile. Do not also register Aegis under `$DSH_HOME/skills`,
`$DSH_AGENTS_HOME/skills`, a project `.dsh/skills` directory, or a custom skill
directory.

After a bundle-bearing Aegis release exists, a release tag may be pinned:

```bash
dsh plugin --profile web add "git+https://github.com/GanyuanRan/Aegis.git#vX.Y.Z"
```

The explicit `git+https://` form is intentional. Do not shorten it to
`github:GanyuanRan/Aegis`: some DSH/pnpm combinations resolve that shorthand
through SSH, which would require users to configure GitHub SSH credentials for
this public repository.

This is repository/profile installation, not a claim that Aegis has an official
DeepSeek marketplace listing.

## Agent-Guided Quick Installation

A user may give the following instruction directly to a DeepSeek Harness agent:

```text
Install Aegis Method Pack into my current official DeepSeek Harness (`dsh`)
profile through `dsh plugin --profile <profile> add "git+https://github.com/GanyuanRan/Aegis.git"`.
Treat this native profile plugin as the default even when I asked for a minimal
or global install. Do not silently substitute a direct-child installation; use
that only if the plugin manager is unavailable and I explicitly approve
compatibility mode. Confirm pnpm is available, verify the profile manifest and
dump-config readback, then ask me to restart that profile. In the fresh session,
verify the native Aegis lifecycle bootstrap and a representative task-specific
`skill` load. Do not also install Aegis under .dsh/skills, .agents/skills, or
another custom skill root. Do not modify my project.
```

The agent still needs normal command approval from DeepSeek Harness. Installation
success does not retroactively route the session that performed the install
through Aegis.

## Bundle Verification

First verify that the selected profile owns the installed package:

```bash
dsh plugin --profile web list --depth 0
```

The output must list `aegis`. Then inspect the composed profile without starting
the application:

```bash
dsh --profile web --dump-config
```

The dump must contain exactly one enabled row with:

```text
id: aegis-method-pack
name: aegis/extensions/dsh/index.js
```

The profile manifest under `$DSH_HOME/profiles/web/package.json` (default
`~/.dsh/profiles/web/package.json`) must list `aegis` in both `dependencies` and
`dsh.profile.bundles`. A package present only in `dependencies` is not an active
DSH bundle.

Locate the profile-managed package root (normally
`$DSH_HOME/profiles/web/node_modules/aegis`), then run the method-pack doctor
from that root, not from a target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Treat structural installation as complete only when the native bundle readback
passes and the doctor reports:

- `"ok": true`
- `"workspaceSupport": "available"`
- `"configStatus": "configured"`

Restart the selected profile. In a fresh Standard-mode Web session, confirm the
skill catalog includes `using-aegis`, `systematic-debugging`, and
`verification-before-completion`. Then give a representative natural-language
task and confirm the injected Aegis bootstrap enters the decision path: the
agent should either load an appropriate task-specific method through Harness's
native `skill` tool or explicitly declare `Route: fast-path`. Also make one
explicit request to load `using-aegis` through the native `skill` tool.

A catalog entry and structural bootstrap test prove discovery and deterministic
entry wiring, not live automatic-routing quality, complete workflow execution,
or release-level host closeout.

## Activation Mode

mode, the Aegis bundle defers a compact `using-aegis` bootstrap to the first
durable promotion signal (`tool/call` or `assistant/message`) after each native
session start, resume, clear, and compact boundary, keeping the first model
request of every gated epoch free of injected context. It skips subagent
sessions. This stabilizes router entry without replacing Harness's
matcher, native `skill` tool, or execution policy.

Setting `AEGIS_ACTIVATION_MODE=explicit` or running:

```bash
python scripts/aegis-doctor.py activation-mode explicit
```

disables that bundle-owned lifecycle injection after the profile is restarted.
It does not override DeepSeek Harness's native catalog, matcher, preset, or
invocation policy, and installed skills remain explicitly invocable. For an
explicit flow, ask the agent to load `using-aegis` through the native `skill`
tool.

Portable goal entry remains:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

## Updating

Update Aegis through the plugin manager of each profile where it is installed:

```bash
dsh plugin --profile web update aegis
dsh plugin --profile web list --depth 0
dsh --profile web --dump-config
```

Repeat the command with `--profile headless` only when that profile also owns an
Aegis installation. Restart the updated profile and repeat the native catalog,
automatic-entry, and task-specific skill-load verification.

Do not use `scripts/aegis-update.py update --host deepseek-harness` for a
bundle-managed installation. That updater command owns only the explicit
direct-child compatibility mode.

## Uninstalling the Bundle

Remove Aegis only from the intended profile:

```bash
dsh plugin --profile web remove aegis
dsh plugin --profile web list --depth 0
dsh --profile web --dump-config
```

The final dump must no longer contain `aegis-method-pack`. Removing the bundle
does not authorize deleting `$DSH_HOME/skills`, `$DSH_AGENTS_HOME/skills`, or
project skill directories; those locations may contain user-owned content.

## Explicit Direct-Child Compatibility Installation

Use this mode only when the developer-preview bundle API is unavailable, local
policy forbids third-party profile plugins, or `pnpm` cannot be provided to the
DSH plugin manager. Ensure `aegis` is absent from the selected profile first.

Keep one local Aegis checkout as the canonical method-pack source and register a
generated direct-child view in the native DSH user skill root.

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git "${DSH_HOME:-$HOME/.dsh}/aegis"
cd "${DSH_HOME:-$HOME/.dsh}/aegis"
python scripts/aegis-update.py register \
  --host deepseek-harness \
  --compatibility-mode \
  --sync-mode symlink \
  --reload-hint "start a new DeepSeek Harness session"
```

### Windows PowerShell

```powershell
$dshHome = if ($env:DSH_HOME) {
  $env:DSH_HOME
} else {
  Join-Path $env:USERPROFILE ".dsh"
}

git clone https://github.com/GanyuanRan/Aegis.git (Join-Path $dshHome "aegis")
Set-Location (Join-Path $dshHome "aegis")
python scripts\aegis-update.py register `
  --host deepseek-harness `
  --compatibility-mode `
  --sync-mode junction `
  --reload-hint "start a new DeepSeek Harness session"
```

The host aliases `deepseek-harness` and `dsh` both resolve to
`$DSH_HOME/skills` (`~/.dsh/skills` by default). The updater creates one
generated link per Aegis skill and refuses to overwrite an existing non-link
skill directory. Do not also enable the Aegis profile bundle, project
`.dsh/skills`, shared `.agents/skills`, or a custom Aegis skill directory.
This compatibility exposure has no bundle-owned lifecycle bootstrap; router
entry depends on Harness's native matcher or explicit skill invocation.

Verify this compatibility mode from the canonical checkout:

```bash
python scripts/aegis-update.py status --host deepseek-harness --json
python scripts/aegis-doctor.py --write-config --json \
  --discovery-root "${DSH_HOME:-$HOME/.dsh}/skills" \
  --expected-discovery-shape direct-child
```

Update only this compatibility installation with:

```bash
python scripts/aegis-update.py update --host deepseek-harness --json
```

## Project-Local Compatibility

For a repository-scoped trial, expose Aegis skills under exactly one of:

```text
<project>/.dsh/skills/<skill-name>/SKILL.md
<project>/.agents/skills/<skill-name>/SKILL.md
```

Prefer `.dsh/skills` for a DeepSeek Harness-specific project install. Project
roots can shadow the bundle or a user-root installation, so do not use this
shape while the Aegis bundle is active for the same profile.

## Runtime Boundary

The DSH bundle is a thin distribution and advisory-bootstrap adapter over
Harness's native profile, lifecycle, injection, and skill-provider contracts.
It does not normalize Harness events, replace the agent loop, hard-block tool
execution, grant an authoritative `GateDecision`, provide an authoritative
`PolicySnapshot`, or provide final completion authority.

DeepSeek Harness profile activation and skill loading are host execution
evidence only. Aegis remains `Aegis Method Pack (runtime-ready)`.

## Official DeepSeek Harness References

- https://github.com/deepseek-ai/deepseek-harness
- https://deepseek.com/harness/
- https://github.com/deepseek-ai/deepseek-harness/blob/master/README.zh.md
- https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.md
- https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
- https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md
