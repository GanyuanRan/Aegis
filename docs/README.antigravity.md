# Aegis for Google Antigravity

Guide for using Aegis with Google Antigravity CLI, Antigravity IDE, and the
Antigravity app platform.

This page only covers the Antigravity host support boundary. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Antigravity is a supported target surface for Aegis in three shapes:

- `Antigravity CLI` - terminal-first agent surface
- `Antigravity IDE` - editor-integrated agent surface
- `Antigravity App` - broader Antigravity 2.x app / project platform surface

The current Aegis support status is structural and advisory. It is based on
Google's public Antigravity positioning, which says Antigravity exposes Skills,
MCP, JSON Hooks, plugins, slash commands, and subagents across Antigravity
surfaces. It does **not** yet claim current release-level live smoke evidence
for any Antigravity shape.

The public `google-antigravity/antigravity-cli` repository confirms the CLI is
the terminal interface for the same Antigravity 2.0 agent engine, but it does
not currently provide a repository-level Aegis install smoke result for this
method pack.

The public Antigravity CLI `1.0.1` changelog says the CLI added plugin
discovery for skills and agents through installed plugin directories. Aegis
treats that as evidence that plugin-backed discovery is becoming available, not
as proof that this repository has a verified Antigravity manifest or install
directory yet.

## Gemini CLI Transition Boundary

Google announced on `2026-05-19` that consumer Gemini CLI and Gemini Code Assist
IDE extension usage is transitioning to Antigravity CLI and Antigravity 2.0.
The announced consumer service stop date is `2026-06-18` for free usage,
Google AI Pro / Ultra, and Gemini Code Assist for individuals.

Aegis keeps `GEMINI.md`, `gemini-extension.json`, and the Gemini tool mapping as
transitional compatibility surfaces for historical lineage, current Gemini CLI
users, and enterprise / paid API key paths. New Google-host work should target
Antigravity, while Gemini CLI remains available as a transition path.

## Recommended Complete Installation

Until Google's Antigravity plugin manifest and install contract have been
verified for this repository, use the manual complete install path:

1. Keep a local Aegis checkout for workspace helper support.
2. Install or expose the `skills/` directories using Antigravity's Skills or
   plugin configuration UI / slash commands.
3. Restart or reload the relevant Antigravity surface.
4. Run Aegis complete-install verification from the checkout root.

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/aegis
cd ~/aegis
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

Across hosts, that local checkout should be treated as the canonical Aegis
body. Any Antigravity-visible skill directories or plugin payloads should be
treated as generated or host-managed views into the same `method_pack_root`,
not as second editable copies.

If Antigravity exposes a separate skill discovery directory in the current
release you are using, also verify that directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root <antigravity-skill-discovery-root>
```

## Shape-Specific Notes

### Antigravity CLI

Use this shape for terminal-first Aegis workflows. Public Antigravity materials
describe CLI access to plugins, MCP, skills, hooks configuration, slash commands,
subagents, `/agents`, `/config`, and `/keybindings`.

Aegis should remain a method pack inside this surface. Antigravity's subagent
support may make subagent-heavy Aegis skills more natural than the transitional
Gemini CLI path, but Aegis still does not grant final completion authority.

### Antigravity IDE

Use this shape for editor-integrated workflows where Skills, MCPs, and JSON
Hooks can be global or workspace-scoped. Prefer workspace-scoped Aegis exposure
when experimenting, then move to global configuration only after skill discovery
and restart / reload behavior are understood.

### Antigravity App

Use this shape for the broader Antigravity project platform and agent manager.
Aegis artifacts such as `TaskIntentDraft`, `ImpactStatementDraft`,
`EvidenceBundleDraft`, and `ResumeStateHint` may map naturally to Antigravity
artifacts and project records, but in this repository they remain
runtime-ready drafts / hints / projections.

## Usage

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Explicit skill use:

```text
Use the Aegis `systematic-debugging` skill for this failure.
```

Antigravity-specific slash commands can be used when the current surface exposes
them, but Aegis docs should keep the portable text form as the stable path until
the host contract is verified.

To disable Aegis automatic bootstrap for hook/profile-aware surfaces, write the
shared local Aegis config from the installed method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

Switch back to automatic mode with:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Restart or reload the relevant Antigravity CLI / IDE / App surface after the
change. This command configures Aegis; it is not yet a verified Antigravity
slash command contract.

## Verification

After installing or updating Aegis in any Antigravity shape:

1. Restart or reload the Antigravity surface.
2. Ask the host to list or describe Aegis skills.
3. Ask it which Aegis skill it would use before debugging a failing test.
4. Do not run the doctor command from the target project directory. From the
   Aegis method-pack root, run
   `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`.
5. If a separate skill discovery directory exists, run
   `python scripts/aegis-doctor.py --discovery-root <path>`.

Expected result:

- Antigravity can see skills such as `using-aegis`, `brainstorming`, and
  `systematic-debugging`.
- Antigravity can load the relevant skill on demand.
- The local Aegis checkout remains available for workspace support.
- The host does not present Aegis as a full runtime platform, authoritative
  `GateDecision`, or final completion authority.

## Updating

```bash
cd <aegis-method-pack-root>
git pull
python scripts/aegis-doctor.py --write-config --json
```

Then refresh the Antigravity skill / plugin exposure using the host's current
configuration UI or slash commands and restart / reload the surface.

If you register Antigravity with the shared Aegis updater, prefer the same
canonical method-pack root already recorded in `~/.config/aegis/config.toml` so
Antigravity, Codex, OpenCode, and other hosts can share one Aegis body:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host antigravity-cli \
  --sync-mode repo-only \
  --reload-hint "restart or reload Antigravity CLI"
python scripts/aegis-update.py update --host antigravity-cli --json
```

If the verified Antigravity release you use exposes a separate skill discovery
directory, register that host-specific exposure shape instead of editing a
second checkout.

## Official Antigravity References

- https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/
- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/docs/cli-overview
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/product/antigravity-ide
