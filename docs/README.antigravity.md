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

Antigravity remains a supported Google-host target surface for Aegis in three
shapes:

- `Antigravity CLI` - terminal-first agent surface
- `Antigravity IDE` - editor-integrated agent surface
- `Antigravity App` - broader Antigravity 2.x app / project platform surface

The current active closeout target is **`Antigravity CLI`**.

Current Aegis status by shape:

- `Antigravity CLI`
  - active closeout target
  - no current release-level fresh smoke verdict yet
- `Antigravity IDE`
  - structural target surface retained
  - not the active closeout slice
- `Antigravity App`
  - structural target surface retained
  - not the active closeout slice

This split is evidence-driven rather than aspirational. Google's public
Antigravity materials now establish several CLI-side facts that are relevant to
closeout:

- the installer and getting-started docs use the `agy` executable
- the Plugins & Skills docs describe `agy plugin list` and
  `agy plugin install /path/to/local/plugin`
- the Gemini migration docs describe `agy plugin import gemini` and adapting
  legacy custom-skills paths
- the public `1.0.1` changelog says the CLI added plugin discovery for skills and agents through installed plugin directories
- the public `1.0.8` changelog says custom skills and system slash commands now
  reload dynamically on conversation switch or `/add-dir`

Aegis treats those facts as host-contract evidence that `Antigravity CLI` is
worth closing out next. They are **not** yet treated as proof that this
repository has a verified Antigravity install/discovery path for the current
method pack, and they do **not** yet count as release-level live smoke
evidence for Aegis.

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

Until Aegis records a fresh local Antigravity CLI install smoke, use the manual
complete install path:

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

The current official Antigravity docs are useful as host references here, but
they do not automatically make one Aegis installation path canonical. For
example, the docs now show:

```bash
agy plugin list
agy plugin install /path/to/local/plugin
agy plugin import gemini
```

Those commands prove the host has a documented plugin and migration surface.
They do **not** yet prove which Aegis repository path or manifest shape should
be written as the verified Antigravity install contract for this method pack.

If Antigravity exposes a separate skill discovery directory in the current
release you are using, also verify that directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root <antigravity-skill-discovery-root>
```

## Shape-Specific Notes

### Antigravity CLI

Use this shape for terminal-first Aegis workflows. Public Antigravity materials
describe CLI access to plugins, MCP, skills, hooks configuration, slash
commands, subagents, `/agents`, `/config`, `/keybindings`, and the `agy`
executable.

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

## Current Aegis Verification Lane

The current Aegis closeout lane for Google-host work is CLI-first:

```bash
bash tests/antigravity/run-tests.sh
bash tests/antigravity/run-tests.sh --integration
```

Interpretation:

- the base suite validates the Aegis-side host contract for docs and
  registration/readback
- the integration suite probes the local `agy` surface and classifies missing
  CLI/runtime/auth conditions as explicit environment blockers
- a skipped integration run is a recorded blocker, not a fresh host closeout
- `Antigravity IDE` and `Antigravity App` stay structural until they have their
  own fresh host evidence slice

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

The current recommended updater semantics stay:

- `syncMode = repo-only`
- `discoveryShape = host-managed`

Reason:

- the official Antigravity docs now prove that a plugin surface exists
- they do **not** yet prove which Aegis repository layout or manifest should be
  treated as the verified staged-plugin contract for this method pack
- until that contract is verified, Aegis should keep one canonical checkout and
  avoid pretending it already owns an Antigravity-managed plugin cache layout

If the verified Antigravity release you use exposes a separate skill discovery
directory, register that host-specific exposure shape instead of editing a
second checkout.

## Official Antigravity References

- https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/
- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/docs/cli-install
- https://antigravity.google/docs/cli-plugins
- https://antigravity.google/docs/gcli-migration
- https://antigravity.google/docs/cli-overview
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/product/antigravity-ide
