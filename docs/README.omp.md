# Aegis for OMP (Oh My Pi)

Guide for using Aegis with OMP (`omp`, the [Oh My Pi](https://github.com/can1357/oh-my-pi)
coding agent, a fork of Pi by Earendil).

This page only covers the OMP host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

OMP inherits the Agent Skills standard from Pi and discovers skills from
multiple providers, including the `agents` provider that reads
`~/.agents/skills/`. Aegis skills installed there are visible to OMP with no
OMP-specific packaging.

OMP also supports `alwaysApply` in skill frontmatter: a skill marked
`alwaysApply: true` has its full content injected into the system prompt.
Aegis marks `using-aegis` with `alwaysApply: true`, so OMP loads the compact
Aegis hot path automatically in every session.

This guide records structural compatibility and skill-view support. It does **not** claim current release-level live smoke evidence for OMP.

## Prerequisites

Install OMP using the command documented by OMP:

```bash
bun install -g @oh-my-pi/pi-coding-agent
```

Alternatives include Homebrew (`brew install can1357/tap/omp`) and the OMP
install script (`curl -fsSL https://omp.sh/install | sh` on macOS/Linux,
`irm https://omp.sh/install.ps1 | iex` on Windows PowerShell). Then
authenticate OMP according to your provider setup.

## Recommended Complete Installation

### 1. Expose Aegis skills to OMP

OMP's `agents` skill provider reads `~/.agents/skills/`, the same shared
Agent Skills surface Pi, Codex, and other harnesses use. Aegis supports a
copy-based install there:

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.agents/aegis
mkdir -p ~/.agents/skills
cp -R ~/.agents/aegis/skills/* ~/.agents/skills/
```

Windows PowerShell:

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.agents\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse -Force "$env:USERPROFILE\.agents\aegis\skills\*" "$env:USERPROFILE\.agents\skills\"
```

This exposes each Aegis skill as:

```text
~/.agents/skills/<skill-name>/SKILL.md
```

### 2. Optional: install the Aegis extension (routing guard)

OMP auto-discovers extensions under `~/.omp/agent/extensions/`, and its
`config.yml` `extensions` list can point at any path. The recommended way is
to reference the extension inside the Aegis checkout so the shared core can
resolve the method-pack root by itself:

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.omp/agent/aegis
```

Windows PowerShell:

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.omp\agent\aegis"
```

Then register the extension in `~/.omp/agent/config.yml`:

```yaml
extensions:
  - ~/.omp/agent/aegis/extensions/omp
```

When `~/.config/aegis/config.toml` already declares a `method_pack_root`, the
extension prefers that canonical Aegis body. Otherwise it falls back to the
nearest ancestor checkout containing `skills/using-aegis/SKILL.md` (the
`~/.omp/agent/aegis` clone above).

A copy-based install also works. Copy the extension bundle (including
`shared/`) into OMP's auto-discovery root and point the copy at a method pack:

```bash
mkdir -p ~/.omp/agent/extensions/aegis
cp -R /path/to/Aegis/extensions/* ~/.omp/agent/extensions/aegis/
```

For the copy-based layout, write the canonical method-pack root into
`~/.config/aegis/config.toml` (or export `AEGIS_METHOD_PACK_ROOT`) so the
extension can locate the skills body, for example:

```toml
method_pack_root = "/path/to/Aegis/checkout"
```

The extension bundle also declares `omp.extensions` in the repository root
`package.json` so future OMP package/marketplace installs can load it without
manual copying.

## Verification

Restart OMP or start a new session after installing.

Ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

Expected result:

- OMP sees Aegis skills such as `using-aegis`, `systematic-debugging`, and
  `brainstorming` (skills list is in the system prompt; content loads on demand
  via `read skill://<name>` or `read` on the SKILL.md path).
- Because `using-aegis` is marked `alwaysApply`, the compact Aegis hot path is
  part of the system prompt without any explicit request.
- With the extension installed, the routing guard marker appears on the first
  non-readonly tool call when no routing decision was recorded.
- Aegis remains a method pack; `GateDecision` and completion authority remain
  outside this repository.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

## Activation Mode

Aegis defaults to automatic mode. To switch to explicit mode, edit:

```text
~/.config/aegis/config.toml
```

(Windows: `%USERPROFILE%\.config\aegis\config.toml`) and add:

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

Restart OMP or start a new session after changing local Aegis config.

In `explicit` mode, OMP still sees `using-aegis` through skill discovery, but
Aegis's own extension stops injecting the bootstrap and the routing guard is
disabled. Name the skill explicitly (`/skill:using-aegis` or in your request)
when you want Aegis.

## Updating

For copy-based installs, update the checkout and copy the skills again:

```bash
cd ~/.agents/aegis
git pull
cp -R ~/.agents/aegis/skills/* ~/.agents/skills/
```

When the extension is referenced from `~/.omp/agent/aegis/extensions/omp`
(config.yml path), update the checkout to refresh the extension:

```bash
cd ~/.omp/agent/aegis
git pull
```

For copy-based extension installs, re-copy `extensions/` as well:

```bash
cp -R ~/.agents/aegis/extensions/* ~/.omp/agent/extensions/aegis/
```

You can register the OMP installation with Aegis's host-scoped updater:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host omp \
  --sync-mode copy-skills \
  --discovery-shape direct-child \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart OMP or start a new session"
python scripts/aegis-update.py update --host omp --json
```

The equivalent one-line registration begins with
`python scripts/aegis-update.py register --host omp`.

Restart OMP or start a new session after updating so the host reloads skill and
extension metadata.

## Uninstalling

Remove the copied Aegis skill directories from:

```text
~/.agents/skills/
```

Remove the extension bundle from:

```text
~/.omp/agent/extensions/aegis/
```

If you also keep personal skills in `~/.agents/skills/`, delete only the Aegis
skill folders copied from this repository.

## Troubleshooting

### Skills are not visible

1. Confirm `~/.agents/skills/using-aegis/SKILL.md` exists.
2. Restart OMP or start a new session.
3. Check for a project-local skill or plugin skill with the same name taking
   precedence (OMP dedupes by skill name, first wins).
4. `using-aegis` is marked `alwaysApply`; if OMP does not inject it, the
   installed OMP release may not support that field yet — the extension
   provides the same injection as a fallback.

### Routing guard not appearing

1. Confirm the extension is loaded: `~/.omp/agent/extensions/aegis/omp/index.ts`
   must exist and OMP must have been restarted.
2. Check whether `AEGIS_ACTIVATION_MODE=explicit` is set; explicit mode
   intentionally disables the automatic bootstrap injection and the guard.
3. The guard only fires once per session, on the first non-readonly tool call.

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

## Official OMP References

- https://github.com/can1357/oh-my-pi
- https://omp.sh/docs/skills
- https://omp.sh/docs/extensions
