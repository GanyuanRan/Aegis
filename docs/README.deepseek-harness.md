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
native `agent/created` lifecycle and the older `agent/session-start` event,
then defers a compact `using-aegis` routing bootstrap on
`startup`, `resume`, `clear`, and `compact`: each boundary only arms the
injection, which is delivered once after the session's first
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

The package declares DSH host peers with a `>=0.1.0-rc.6` admission floor and
no upper version bound. DSH includes prereleases when checking these ranges,
so a newer minor, major, or preview version is not rejected solely because
its version number increased. This is an installation policy, not a promise
that future host APIs remain compatible. See the compatibility matrix and
known limitations for the evidence available for particular host versions.

Install DeepSeek Harness at or above that floor. For CLI-managed profiles,
ensure `pnpm` is on `PATH`. Harness forwards `dsh plugin` operations to `pnpm`,
so being able to start the Web UI through `npx` alone is not sufficient for
CLI profile-plugin management. Electron Desktop uses its application's
runtime and plugin manager.

Verify both commands before a CLI-managed installation:

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

Install Aegis through the manager that owns the intended profile. The following
terminal commands apply to CLI-managed Web and Headless profiles. For Web:

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

### Desktop (Electron)

DSH `0.2.0-rc.2` reserves the `desktop` profile for the Electron application.
Terminal plugin commands for that profile fail with
`profile "desktop" is managed exclusively by the Electron application`.
Use the desktop application's plugin manager for installation, inspection,
update, and removal. Do not substitute `web`: it is a different profile and
does not make the plugin active in Desktop.

When the application's own installer supports an explicit Git target, select
the official repository and a fixed release, for example:

```text
git+https://github.com/GanyuanRan/Aegis.git#v2.12.2
```

Read back the actual dependency name, source/ref, installed package version,
and bundle through the application or its profile manifest. Do not assume a
community marketplace's catalog button or custom Git input preserves the
requested target; see the source-selection limitation below. Do not edit the
Electron-managed profile to bypass its manager.

[Issue #81](https://github.com/GanyuanRan/Aegis/issues/81#issuecomment-6072156389)
reports successful installation and a visible plugin through the desktop
application's manager. Its installed source/version and native skill loading
were not reported, so it is bounded installation-recovery evidence.

### Official Source and Third-Party npm Packages

Aegis officially supports the Git installation above. Aegis does not maintain
an official npm registry channel. The public npm `aegis-method-pack` package
is published by an external account, not the Aegis team. Its repository or
author metadata does not establish official publication. The bundle's Cordis
row ID `aegis-method-pack` is a plugin identifier, not a registry package name.

The third-party npm `2.9.2` artifact retains `^0.1.0-rc.6` peers and is rejected
by DSH `0.2.0-rc.2`. Marketplace repository searches can select that stale
artifact even when the Git source is current. Preserve the explicit Git URL
and any pinned tag; check the actual selected source and installed version.
In [Plugin Hub issue #120](https://github.com/dshplugin/dsh-plugin-hub/issues/120#issuecomment-6060567215),
the maintainer retained npm-first resolution and closed the report as a known
limitation. Hub `v1.6.0` improves profile-specific hints and pnpm diagnostics;
it does not remove this source substitution. Its repository-install path also
normalizes Git URLs to a repository identity and rebuilds an unpinned URL
before npm lookup. This source-level finding is not a live Desktop GUI test.
The fixed-ref follow-up is
[Plugin Hub issue #130](https://github.com/dshplugin/dsh-plugin-hub/issues/130).
A GitHub release does not update a third-party registry artifact or repair the
marketplace's source selection. Version admission also does not establish live
routing compatibility.

If a previous marketplace attempt installed `aegis-method-pack`, first inspect
the intended profile with `dsh plugin --profile web list --depth 0`. Remove
that dependency only if it is present, using
`dsh plugin --profile web remove aegis-method-pack`, then install the Git source
above and repeat the bundle verification below. Use the corresponding CLI
profile name only for CLI-managed profiles. For Desktop, perform dependency
inspection and removal through the application's manager. A rejected install
may have left no dependency to remove. Keep
exactly one Aegis bundle and do not delete user or project skill directories.

## Agent-Guided Quick Installation

A user may give the following instruction directly to a DeepSeek Harness agent:

```text
Install Aegis Method Pack into my current official DeepSeek Harness (`dsh`)
profile. First identify the profile's owner. For CLI-managed Web/Headless, use
`dsh plugin --profile <profile> add "git+https://github.com/GanyuanRan/Aegis.git"`.
For Electron Desktop, use the application's plugin manager; do not run CLI
commands for desktop or substitute web. Verify the actual source/ref/version.
Treat this native profile plugin as the default even when I asked for a minimal
or global install. Do not silently substitute a direct-child installation; use
that only if the plugin manager is unavailable and I explicitly approve
compatibility mode. For CLI-managed profiles, confirm pnpm is available and
verify the profile manifest and dump-config. For Desktop, inspect the same
bundle through the application or its manifest. Then ask me to restart that
profile. In the fresh session,
verify the native Aegis lifecycle bootstrap and a representative task-specific
`skill` load. Do not also install Aegis under .dsh/skills, .agents/skills, or
another custom skill root. Do not modify my project.
```

The agent still needs normal command approval from DeepSeek Harness. Installation
success does not retroactively route the session that performed the install
through Aegis.

## Bundle Verification

The CLI examples below apply to Web. For Electron Desktop, inspect the
corresponding dependency and bundle through the application's manager or its
profile manifest, then restart Desktop and verify native skill discovery and
loading there. CLI configuration dumps and Web skill discovery do not verify
the Desktop profile.

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

### Installed-Profile Lifecycle Readback

Use a separate test profile/home with one Aegis bundle, `activation_mode = auto`,
and no manual `AGENTS.md` bootstrap or direct-child Aegis exposure. Record the
Aegis commit or bundle hash as well as its package version, the DSH version,
and the selected profile. Agree on a model-call budget before live checks.

For each boundary below, distinguish observations from a real installed host
from deterministic checks using a host double:

| Boundary | Expected observation |
| --- | --- |
| Fresh Standard-mode session | No injection while arming; one plugin-sourced bootstrap after the first durable promotion signal |
| Resume, clear, compact (each separately) | One deferred injection for the new boundary, without duplicate delivery on subsequent turns |
| Subagent | No Aegis lifecycle bootstrap injected into the subagent session |
| Explicit activation, after profile restart | No bundle-owned bootstrap; native explicit skill loading remains available |

Count injected messages by plugin provenance (`source.kind` beginning with
`plugin:`), Aegis bootstrap identity, and session/boundary, rather than counting
marker substrings. Model quotations and recalled text can repeat the marker
without another injection. Check the model-facing messages for the first
request; on DSH `0.1.7-rc.2`, `request/header` alone is not a per-request
message list.

The first route decision may precede deferred injection. Record event ordering
and assess a task-specific native `skill` load or `Route: fast-path` on a step
after delivery; do not attribute a preceding skill call to this bootstrap.
Report unobserved boundaries explicitly. Retain raw sessions privately and
share only sanitized source identity, boundary/injection counts, ordering,
route outcomes, and errors. The current evidence and remaining gaps for
[issue #75](https://github.com/GanyuanRan/Aegis/issues/75) live in
[known limitations](current/AEGIS_KNOWN_LIMITATIONS.md#226-deepseek-harness-bundle-support-is-not-yet-fresh-host-closeout).

## Activation Mode

In `auto` mode, the Aegis bundle defers a compact `using-aegis` bootstrap to the first
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

For Electron Desktop, update through the application's plugin manager and
inspect the actual source/ref/version there. The terminal examples in this
section apply to CLI-managed profiles.

Aegis `v2.11.1` was published with the old `^0.1.0-rc.6` peer range and can be
rejected by DSH `0.2.0-rc.1` before plugin code is loaded. Select a
revision containing the admission-range fix; retrying the same old tag does
not change its manifest. Version exemptions are not required by the fixed
manifest.

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

For Electron Desktop, remove the intended bundle through the application's
plugin manager. The terminal example below applies to Web.

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
DSH plugin manager. Ensure both `aegis` and `aegis-method-pack` dependencies are
absent from the selected profile first.

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
