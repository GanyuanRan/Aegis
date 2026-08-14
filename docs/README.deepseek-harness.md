# Aegis for DeepSeek Harness

Guide for using Aegis with the official DeepSeek Harness (`dsh`) through its
native filesystem skill provider.

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

DeepSeek Harness is structurally skills-compatible with Aegis. Its filesystem
provider discovers direct child skill bundles from these roots, in host-defined
priority order:

- `<project>/.dsh/skills`
- `<project>/.agents/skills`
- configured custom skill directories
- `$DSH_HOME/skills`, or `~/.dsh/skills` when `DSH_HOME` is unset
- `$DSH_AGENTS_HOME/skills`, or `~/.agents/skills` when `DSH_AGENTS_HOME` is unset

Aegis uses the native direct-child shape:

```text
<skill-root>/<skill-name>/SKILL.md
```

DeepSeek Harness is currently a developer preview and warns that compatibility
breaking changes are expected. This guide records deterministic structural
support; it does not claim current release-level live routing evidence.

## Recommended Complete Installation

Keep one local Aegis checkout as the canonical method-pack source. Register a
generated direct-child view in DeepSeek Harness's native user skill root. Do not
also expose the same Aegis checkout through `~/.agents/skills` or a custom skill
directory.

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git "${DSH_HOME:-$HOME/.dsh}/aegis"
cd "${DSH_HOME:-$HOME/.dsh}/aegis"
python scripts/aegis-update.py register \
  --host deepseek-harness \
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
  --sync-mode junction `
  --reload-hint "start a new DeepSeek Harness session"
```

The host aliases `deepseek-harness` and `dsh` both resolve to the native DSH
skill root. Registration defaults to:

```text
discovery root: $DSH_HOME/skills or ~/.dsh/skills
discovery shape: direct-child
```

The updater creates one generated link per Aegis skill and refuses to overwrite
an existing non-link skill directory. The canonical editable owner remains:

```text
$DSH_HOME/aegis/skills/<skill-name>/SKILL.md
```

## Agent-Guided Quick Installation

A user may give the following instruction directly to a DeepSeek Harness agent:

```text
Install Aegis Method Pack for DeepSeek Harness. Keep one canonical checkout
under $DSH_HOME/aegis (default ~/.dsh/aegis), register host deepseek-harness
with Aegis's updater, and use direct-child skills under $DSH_HOME/skills.
Use symlink on macOS/Linux or junction on Windows. Do not also install Aegis
under .agents/skills or another custom skill root. Verify the updater and
Aegis doctor JSON, then ask me to start a new session. Do not modify my project.
```

The agent still needs normal filesystem and command approval from DeepSeek
Harness. Installation success does not retroactively route the session that
performed the install through Aegis.

## Skills-Only Compatibility Installation

For a temporary trial, copy the canonical `skills/` children directly into one
DeepSeek Harness skill root:

```bash
mkdir -p "${DSH_HOME:-$HOME/.dsh}/skills"
cp -R /path/to/Aegis/skills/* "${DSH_HOME:-$HOME/.dsh}/skills/"
```

This is a skills-only compatibility install, not the recommended complete
installation. If the Aegis checkout is discarded:

- project workspace support is not proven
- host-scoped updater registration is unavailable
- future updates require another copy and stale-skill cleanup

Do not mix copied Aegis skills with updater-managed links in the same or another
DeepSeek Harness discovery root.

## Project-Local Installation

For a repository-scoped trial, expose Aegis skills under exactly one of:

```text
<project>/.dsh/skills/<skill-name>/SKILL.md
<project>/.agents/skills/<skill-name>/SKILL.md
```

Prefer `.dsh/skills` for a DeepSeek Harness-specific project install. Project
roots outrank user roots, so a project-local Aegis copy can shadow a global
installation. Avoid duplicate project and user exposures with different
versions.

## Verification

Run these commands from the canonical method-pack root. Do not run the doctor
from the target project directory; pass target projects separately to workspace
helper commands.

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py status --host deepseek-harness --json
python scripts/aegis-doctor.py --write-config --json \
  --discovery-root "${DSH_HOME:-$HOME/.dsh}/skills" \
  --expected-discovery-shape direct-child
```

Treat structural installation as complete only when the readback reports:

- `"ok": true`
- `"workspaceSupport": "available"`
- `"configStatus": "configured"`
- direct-child discovery is current
- no duplicate or stale Aegis exposure is reported

Start a new DeepSeek Harness session in Standard mode and confirm its skill
catalog includes `using-aegis`, `systematic-debugging`, and
`verification-before-completion`. Ask the agent to load `using-aegis` through
the native `skill` tool before treating live routing as observed.

Portable goal entry remains:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

A catalog entry proves discovery, not automatic routing quality, complete
workflow execution, or release-level host closeout.

## Activation Mode

DeepSeek Harness owns its catalog and native model-facing `skill` loader. Aegis
has no bootstrap plugin for this host in the current repository.

Setting `AEGIS_ACTIVATION_MODE=explicit` or running:

```bash
python scripts/aegis-doctor.py activation-mode explicit
```

changes how a loaded Aegis skill proceeds. It does not override DeepSeek
Harness's native catalog, matcher, preset, or invocation policy. For an explicit
flow, ask the agent to load `using-aegis` through the native `skill` tool.

## Updating

Update only the DeepSeek Harness registration:

```bash
cd "${DSH_HOME:-$HOME/.dsh}/aegis"
python scripts/aegis-update.py update --host deepseek-harness --json
```

The update registry is host-scoped. Do not use `--all` unless every registered
Aegis host is intentionally in scope. Start a new DeepSeek Harness session after
updating to establish a fresh skill catalog and hot-path body.

## Uninstalling

Remove only updater-managed Aegis links from the configured DSH skill root and
remove the `deepseek-harness` installation entry using the same ownership-aware
method that created it. Do not delete `~/.dsh/skills` wholesale when it contains
personal or third-party skills.

The canonical checkout may be removed only after no registered host or workspace
helper depends on it.

## Runtime Boundary

This integration exposes the Aegis Method Pack through DeepSeek Harness's native
skill provider. It does not make this repository a DeepSeek Harness runtime
plugin, normalize Harness events, grant an authoritative `GateDecision`, or
provide final completion authority.

A dedicated Cordis plugin remains deferred until live evidence proves native
skill discovery and model routing are insufficient and the developer-preview
plugin API is stable enough to justify another compatibility surface.

## Official DeepSeek Harness References

- https://github.com/deepseek-ai/deepseek-harness
- https://deepseek.com/harness/
- https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md
- https://github.com/deepseek-ai/deepseek-harness/tree/master/packages/skill/skill-filesystem
