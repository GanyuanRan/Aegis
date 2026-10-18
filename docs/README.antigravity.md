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
  - fresh local Windows evidence (`agy 1.4.0`, 2026-10-17) now covers the
    official install, plugin-surface lifecycle, updater-managed direct-child
    skill exposure, and update dry-run planning
  - live Aegis skill loading, representative task routing, and session refresh
    remain pending verification; the local Windows session was blocked by
    Antigravity's account eligibility check (environment-bound)
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
worth closing out next. Fresh local Aegis evidence (2026-10-17, Windows,
`agy 1.4.0`) now verifies the install, plugin surface, and updater-managed
direct-child exposure path on a real machine:

- the official PowerShell installer completed and `agy --version` reported
  `1.4.0`
- `agy plugin list --json` returned a machine-readable array without sign-in
- a scratch-plugin lifecycle verified `agy plugin install <local-path>`,
  `agy plugin list --json`, disable/enable, and uninstall; install copies the
  whole source directory and stages it under
  `~/.gemini/config/plugins/<plugin-name>/`
- registering `antigravity-cli` with `--sync-mode junction
  --discovery-root ~/.gemini/antigravity-cli/skills --discovery-shape
  direct-child` created one link per Aegis skill, and the register-time
  doctor readback reported `discoveryShapeStatus: current`
- `aegis-update.py update --host antigravity-cli --dry-run --json` planned the
  fetch/merge/verify steps for the registered checkout

Live Aegis verification remains pending. The local Windows session was
rejected by Antigravity's own account eligibility check before any model turn.
That check is host/account-side behavior rather than an Aegis install property.
A runnable signed-in CLI alone does not prove that Aegis skills are discovered,
loaded, routed correctly, or refreshed across sessions. The structural
readbacks above are **not** release-level live smoke evidence for Aegis.

## Retired Gemini CLI Boundary

Google announced on `2026-05-19` that consumer Gemini CLI and Gemini Code Assist
IDE extension usage is transitioning to Antigravity CLI and Antigravity 2.0.
The announced consumer service stop date is `2026-06-18` for free usage,
Google AI Pro / Ultra, and Gemini Code Assist for individuals.

Aegis has retired its Gemini CLI support surface. The repository no longer
ships `GEMINI.md`, `gemini-extension.json`, or a Gemini-specific tool mapping.
This is an Aegis product-support decision, not a claim that Gemini CLI is
unavailable to every enterprise, Google Cloud, or paid API-key user.

The documented `agy plugin import gemini` command remains relevant as upstream
migration history. New Google-host work should target Antigravity, whose Aegis
install and discovery path still requires its own fresh closeout evidence.

## Recommended Complete Installation

Keep a local Aegis checkout for workspace helper support:

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

### Antigravity CLI: updater-managed direct-child exposure

For `Antigravity CLI`, the locally verified structural path is the shared
updater's direct-child exposure under the CLI's global skills root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-update.py register \
  --host antigravity-cli \
  --sync-mode junction \
  --discovery-root ~/.gemini/antigravity-cli/skills \
  --discovery-shape direct-child \
  --reload-hint "restart or reload Antigravity CLI"
python scripts/aegis-update.py update --host antigravity-cli --json
```

Registration creates one link per Aegis skill under
`~/.gemini/antigravity-cli/skills/`, refreshes them at update time, and runs
the doctor discovery readback. Restart or reload the CLI afterward, and treat
the exposure as structurally verified when:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root ~/.gemini/antigravity-cli/skills
```

reports `discoveryShapeStatus: current`. The method-pack `skills/` tree stays
canonical; the CLI-visible entries are generated links rather than a second
editable owner.

### Other Antigravity shapes or manual exposure

For `Antigravity IDE`, the `Antigravity App`, or a manual CLI setup, install
or expose the `skills/` directories using the host's Skills or plugin
configuration UI / slash commands, then restart or reload the surface.

The current official Antigravity docs are useful as host references here. For
example, the docs show:

```bash
agy plugin list
agy plugin install /path/to/local/plugin
agy plugin import gemini
```

Those commands document the host plugin and migration surface. They do not by
themselves define the Aegis install contract: the locally verified Aegis
exposure path is the updater-managed direct-child root above, while a
repository-root Antigravity plugin manifest remains an explicit open decision
rather than a current Aegis distribution surface.

### Plugin installation (alternative)

Antigravity plugins require a `plugin.json` manifest (`name` plus optional
`description`, schema `additionalProperties: false`) at the plugin directory
root, with optional `skills/<skill-name>/SKILL.md` components. The local
plugin lifecycle was verified on `agy 1.4.0`:

- `agy plugin install <local-path>` copies the whole source directory and
  stages it under `~/.gemini/config/plugins/<plugin-name>/`
- `agy plugin list --json` reports the staged path and bundled skill names
  without sign-in
- disable, enable, and uninstall each updated or removed the staged copy

Treat a plugin installation as a host-managed copy. Do not enable it beside
the direct-child exposure above; two active Aegis exposure routes can produce
duplicate skill names with different freshness. GitHub URL installs follow the
same plugin contract but were not locally verified in this closeout.

## Shape-Specific Notes

### Antigravity CLI

Use this shape for terminal-first Aegis workflows. Public Antigravity materials
describe CLI access to plugins, MCP, skills, hooks configuration, slash
commands, subagents, `/agents`, `/config`, `/keybindings`, and the `agy`
executable.

Aegis should remain a method pack inside this surface. Antigravity's subagent
support may make subagent-heavy Aegis skills more natural than they were through
the retired Gemini CLI adapter, but Aegis still does not grant final completion
authority.

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
5. For the CLI direct-child exposure, run
   `python scripts/aegis-doctor.py --discovery-root ~/.gemini/antigravity-cli/skills`
   and expect `discoveryShapeStatus: current`.

Expected result:

- Antigravity can see skills such as `using-aegis`, `brainstorming`, and
  `systematic-debugging`.
- The CLI direct-child exposure resolves every visible skill into the
  canonical `skills/` tree.
- Antigravity can load the relevant skill on demand inside a signed-in session.
- The local Aegis checkout remains available for workspace support.
- The host does not present Aegis as a full runtime platform, authoritative
  `GateDecision`, or final completion authority.

Live closeout boundary: steps 2-3 require a runnable session — working
sign-in or a valid API key, plus an account that passes Antigravity's own
eligibility check. Live Aegis skill loading, representative task routing, and
restart/reload behavior remain pending verification; the local Windows session
was eligibility-blocked. Record these steps in an actually runnable session
instead of inferring routing from structural readbacks or sign-in alone.

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
  --sync-mode junction \
  --discovery-root ~/.gemini/antigravity-cli/skills \
  --discovery-shape direct-child \
  --reload-hint "restart or reload Antigravity CLI"
python scripts/aegis-update.py update --host antigravity-cli --json
```

The current recommended updater semantics are:

- `syncMode = junction` (link-based direct-child exposure; non-Windows
  platforms use symlinks for the same shape)
- `discoveryShape = direct-child`

Reason:

- the direct-child exposure was locally verified on `agy 1.4.0`: links are
  created at register time and the doctor readback reports
  `discoveryShapeStatus: current`
- `update --host antigravity-cli` refreshes and re-verifies the links, so the
  host stays a generated view of the canonical `skills/` tree instead of a
  second editable copy
- the CLI plugin surface remains an alternative host-managed copy; keep
  exactly one Aegis exposure route active per installation

## Official Antigravity References

- https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/
- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/docs/cli-install
- https://antigravity.google/docs/cli-plugins
- https://antigravity.google/docs/gcli-migration
- https://antigravity.google/docs/cli-overview
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/product/antigravity-ide
