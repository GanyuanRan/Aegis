# Aegis for Kimi Code CLI

Guide for installing Aegis through Kimi Code CLI's native plugin and Agent
Skills contracts.

This page owns the Kimi-specific install, migration, update, reload, and
verification path. For repository authority and release status, also read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

The default Kimi installation is the native Aegis plugin declared by the root
`kimi.plugin.json`. It exposes the canonical `skills/` tree and establishes
`sessionStart.skill = using-aegis`, so each new or resumed session gets a
stable routing entry before Kimi performs task-to-skill selection.

Natural-language task descriptions are the normal entry point. Explicit skill
invocation remains an override and diagnostic path.

The previous updater-managed direct-child installation remains supported as
an **explicit compatibility mode**. The plugin and direct-child views must not
be active together because that creates duplicate skill owners and unreliable
routing evidence.

This guide records implemented structural support. It does not claim current
release-level live smoke evidence; a real Kimi CLI, login/provider access, and
representative model-routing smoke are still required for that verdict.

Official references:

- `https://moonshotai.github.io/kimi-code/en/customization/skills`
- `https://moonshotai.github.io/kimi-code/en/customization/plugins`
- `https://moonshotai.github.io/kimi-code/en/configuration/config-files.html`
- `https://moonshotai.github.io/kimi-code/en/reference/kimi-command.html`

## Default Automatic Installation

Start Kimi Code CLI and run:

```text
/plugins install https://github.com/GanyuanRan/Aegis
```

Approve Kimi's third-party plugin trust confirmation after checking that the
source is `GanyuanRan/Aegis`. Then inspect the managed installation:

```text
/plugins info aegis
```

The result must identify one enabled plugin named `aegis`. It must expose the
repository `skills/` tree and the `using-aegis` session-start skill from the
same managed plugin root. Do not also expose Aegis under
`$KIMI_CODE_HOME/skills/` or `~/.agents/skills/`.

Activate the installed plugin in a clean host context:

```text
/reload
```

If the current Kimi build or session cannot reload plugins cleanly, use:

```text
/new
```

Kimi owns plugin download, managed-copy storage, enablement, reload, and
session-start loading. Editing another checkout does not update Kimi's managed
copy.

## Complete-Install Verification

Use `/plugins info aegis` to locate the managed plugin root. Run verification
from that root, not from a target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json --host-profile kimi-code-auto
```

Treat structural installation as complete only when the JSON reports:

- `"ok": true`
- `"hostProfile": "kimi-code-auto"`
- exactly one enabled Aegis plugin rooted at this method pack
- `"duplicateExposureStatus": "clean"`
- `"workspaceSupport": "available"`
- `"configStatus": "configured"`

The doctor is read-only with respect to Kimi's plugin registry and skill
roots. `--write-config` only writes Aegis's user-local method-pack config. Its
`"restartRequired": true` result is a conservative host-action reminder:
doctor cannot observe whether the running Kimi process has already reloaded.
Complete `/reload` or `/new` and verify the new session instead of changing
that field or treating it as a structural failure.

Finally, use a new or reloaded session and give Kimi representative natural
language tasks. File discovery and a generic doctor result are not sufficient
proof of automatic routing. The environment-bound repository lane is:

```bash
bash tests/kimi-code/run-live-smoke.sh
```

It checks positive routing, a negative fast-path case, and resumed-session
behavior. If CLI, login, provider, or trust prerequisites are absent, report
the lane as environment-bound rather than passed.

## Updating Automatic Installations

Kimi's plugin manager owns the automatic installation. Use its native
install/update flow against the same source, then reload or start a new
session:

```text
/plugins install https://github.com/GanyuanRan/Aegis
/plugins info aegis
/reload
```

If Kimi requires removal or confirmation before replacing the managed copy,
follow the exact prompt shown by the plugin manager. Do not substitute
`scripts/aegis-update.py update --host kimi-code` for a plugin-managed update.

After updating, rerun the `kimi-code-auto` doctor profile from the managed
plugin root and repeat the host-native automatic-entry smoke.

## Migrating From Direct-Child To Automatic Mode

Before plugin installation, inspect these Kimi user-level Agent Skills roots:

```text
$KIMI_CODE_HOME/skills/  (default: ~/.kimi-code/skills/)
~/.agents/skills/
```

Kimi also recognizes project-level `.kimi-code/skills/` and
`.agents/skills/`. If any of these contain Aegis direct-child skills, retire
that generated exposure using the updater or the method that created it. Do
not delete an unknown user-owned directory merely because its name matches an
Aegis skill.

Install the plugin only after the alternate Aegis exposure is gone. The
`kimi-code-auto` doctor profile rejects collisions instead of silently choosing
one owner.

The old Codex umbrella symlink
`~/.agents/skills/aegis -> ~/.codex/aegis/skills` is not a valid Kimi automatic
installation and must not be treated as the Kimi main path.

## Explicit Compatibility Installation

Use this mode only when native plugin installation is unavailable, when policy
forbids third-party plugins, or when the user deliberately wants explicit-only
entry. It exposes individual Aegis skills through Kimi's native direct-child
Agent Skills discovery and does not establish a session-start router.

Ensure the `aegis` plugin is disabled or uninstalled first. Then keep an Aegis
method-pack checkout separate and register the Kimi host.

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --reload-hint "restart Kimi Code CLI"
```

The updater defaults to `$KIMI_CODE_HOME/skills`, or
`~/.kimi-code/skills` when `KIMI_CODE_HOME` is unset. An explicit root is also
supported:

```bash
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --discovery-root "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills" \
  --reload-hint "restart Kimi Code CLI"
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
Set-Location "$env:USERPROFILE\.codex\aegis"
$kimiSkills = if ($env:KIMI_CODE_HOME) {
  Join-Path $env:KIMI_CODE_HOME "skills"
} else {
  Join-Path $env:USERPROFILE ".kimi-code\skills"
}
python scripts\aegis-update.py register `
  --host kimi-code `
  --sync-mode junction `
  --discovery-root $kimiSkills `
  --reload-hint "restart Kimi Code CLI"
```

Expected generated shape:

```text
~/.kimi-code/skills/using-aegis/SKILL.md
~/.kimi-code/skills/systematic-debugging/SKILL.md
~/.kimi-code/skills/brainstorming/SKILL.md
```

The repository `skills/` tree remains the editable source of truth. These
direct-child directories are generated compatibility views, not a second skill
owner.

Verify explicit compatibility mode from the method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json \
  --host-profile kimi-code-explicit \
  --discovery-root "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills"
```

The profile requires no enabled Aegis plugin and rejects alternate direct-child
exposures. Restart Kimi after registration or updates.

Update this compatibility installation with:

```bash
python scripts/aegis-update.py status --json
python scripts/aegis-update.py update --host kimi-code --json
```

Kimi also scans `~/.agents/skills/`, so it may be selected as a deliberate
cross-tool fallback by passing it as `--discovery-root`. Do not enable that
fallback together with `$KIMI_CODE_HOME/skills` or the plugin.

## Activation Mode

For Kimi, `auto` and `explicit` are installation profiles:

- `auto`: one enabled plugin with `sessionStart.skill = using-aegis`
- `explicit`: no enabled Aegis plugin and exactly one direct-child skill view

The generic method-pack command remains available:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

This writes Aegis method-pack configuration only. It does not override Kimi Code CLI.
It does not disable a Kimi plugin, remove its `sessionStart` entry, or control
Kimi's native skill matcher. To switch Kimi to explicit mode, change the
installation profile as described above and open a new or reloaded session.

Portable goal entry remains:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

## Authority Boundary

The plugin is a thin host adapter. It does not duplicate skill bodies, add a
daemon or MCP server, overwrite a global `AGENTS.md`, or create a second
router. Kimi session-start loading is host execution evidence only.

Aegis remains a method pack. It can provide workflow discipline,
runtime-ready drafts, and verification guidance, but it does not provide an
authoritative `GateDecision`, authoritative `PolicySnapshot`, or final
completion authority.
