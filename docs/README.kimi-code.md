# Aegis for Kimi Code CLI

Guide for using Aegis with Kimi Code CLI through Kimi's native Agent Skills
discovery.

Design status: the updater-managed direct-child path documented below is the
current supported structural path. A Kimi-native plugin path for reliable
automatic router entry is approved in direction but is not implemented or
release-verified yet.

This page only covers the Kimi Code CLI host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

Kimi Code CLI is structurally compatible with Aegis because Kimi discovers
Agent Skills from user and project skill roots. The official Kimi Code CLI
Agent Skills docs list the user-level roots as:

```text
$KIMI_CODE_HOME/skills/  (default: ~/.kimi-code/skills/)
~/.agents/skills/
```

They also list project-level roots:

```text
.kimi-code/skills/
.agents/skills/
```

Kimi's own user-level root moves with `KIMI_CODE_HOME`; the generic
`~/.agents/skills/` root stays under the real OS home and is a cross-tool
sharing surface.

For Aegis, the recommended Kimi install path is Kimi's native user-level root:

```text
$KIMI_CODE_HOME/skills/<skill-name>/SKILL.md
```

The generic `~/.agents/skills/` root remains a compatibility fallback, not the
canonical Kimi Aegis path. Do not rely on the Codex umbrella symlink
`~/.agents/skills/aegis -> ~/.codex/aegis/skills` as the Kimi main path.

This guide records structural compatibility and native install support. It does
not claim current release-level live smoke evidence.

Official references:

- `https://moonshotai.github.io/kimi-code/en/customization/skills`
- `https://moonshotai.github.io/kimi-code/en/customization/plugins`
- `https://moonshotai.github.io/kimi-code/en/configuration/config-files.html`
- `https://moonshotai.github.io/kimi-code/en/reference/kimi-command.html`

## Automatic Routing Design (Pending Implementation)

This section records the proposed implementation boundary. It is not a current
installation instruction and must not be used to claim Kimi live-host
closeout.

### Target Outcome

The default Kimi `auto` installation must establish a stable Aegis router entry
for every new or resumed Kimi session. Users should normally describe work in
natural language; explicit `/skill:<name>` invocation remains an override and
diagnostic path, not the expected daily entry path.

Installing files and making Kimi discover individual skills are necessary but
not sufficient. Automatic routing is considered available only after the host
has loaded `using-aegis` at session start and representative natural-language
tasks route correctly without creating unacceptable false positives.

### Canonical Owners

- The repository `skills/` tree remains the only editable owner of Aegis skill
  bodies.
- A root `kimi.plugin.json` will be the Kimi-native distribution and automatic
  bootstrap manifest. It will reference `./skills/` rather than copy skill
  bodies into a Kimi-only tree.
- `skills/using-aegis/SKILL.md` remains the portable routing owner.
- Kimi owns plugin installation, managed-copy storage, enablement, reload,
  session-start loading, and native model invocation.
- `docs/README.kimi-code.md` owns Kimi-specific install, migration, update,
  reload, and verification instructions.

For the current `2.5.0` release line, the intended minimal manifest behavior is:

```json
{
  "name": "aegis",
  "version": "2.5.0",
  "skills": "./skills/",
  "sessionStart": {
    "skill": "using-aegis"
  }
}
```

The manifest is a thin host adapter. It must not duplicate the `using-aegis`
body, introduce a second router, execute startup code, or grant runtime or
completion authority. Later releases must synchronize this field with the
repository release version.

### Alternatives Considered

1. Keep only direct-child skills and tune descriptions or `whenToUse`.
   - Necessary metadata hygiene, but it still depends on the model choosing the
     router before Aegis routing discipline can run.
2. Write Aegis bootstrap rules into the user's global Kimi `AGENTS.md`.
   - Can improve entry probability, but mutates a user-owned cross-project rule
     surface and creates a second bootstrap owner.
3. Use a thin Kimi-native plugin with `sessionStart.skill` and reuse the
   canonical `skills/` tree.
   - Chosen direction because it uses the host's explicit initialization
     contract without duplicating method behavior or overwriting user rules.

### Install Modes And Duplicate-Owner Rule

Kimi installations must expose Aegis through exactly one active route:

- `auto` (default): install the Kimi plugin and use
  `sessionStart.skill = using-aegis`.
- `explicit` (compatibility mode): retain updater-managed direct-child Agent
  Skills without a session-start bootstrap.

The plugin and direct-child Aegis views must not be enabled together. Migration
and doctor checks must detect an existing alternate route and either retire it
safely or stop with exact user instructions. The shared `~/.agents/skills/`
surface remains a compatibility fallback only; it is not a second automatic
route.

The current direct-child installation remains supported until plugin install,
update, rollback, and live-trigger evidence are complete. Its retirement can be
reconsidered only after active dependency evidence is collected; it must not
be deleted merely because the plugin path exists.

### Skill Metadata Repair Track

The host bootstrap does not replace valid skill metadata. Before the plugin
path can be called reliable, every directory-form `SKILL.md` must satisfy the
Kimi parser contract:

- explicit `name` and `description`
- quoted YAML string values when punctuation could change scalar parsing
- concise trigger-oriented descriptions within Kimi's model-visible limit
- no accidental `type: flow` or `disableModelInvocation: true`
- `whenToUse` only where it adds a clear boundary instead of duplicating or
  broadening the description

Parser failure is a release failure. In particular, metadata containing an
unquoted `: ` sequence must be rejected by repository tests rather than being
silently omitted by Kimi.

### Universal Quick-Install Prompt Boundary

The universal quick-install prompt remains the recommended user entry point,
but it must stay an orchestrator rather than embed every host's commands. Its
contract is:

1. identify the active host and use its default activation mode unless the
   user explicitly requests another supported mode
2. follow the current host-specific guide
3. complete method-pack verification from the installed method-pack root
4. complete the host-native discovery, activation, reload, and automatic-entry
   checks required by that guide
5. report any trust confirmation or restart/new-session action that still
   requires the user

For Kimi `auto`, a successful generic doctor result or a populated skill
directory alone is not completion evidence. The host-specific check must also
prove plugin identity/version, enabled state, clean reload or new-session
activation, `using-aegis` session-start entry, and representative automatic
routing behavior.

The quick-install prompt should therefore add one stable clause rather than
Kimi-specific commands:

```text
Also complete the host guide's native activation and automatic-entry checks;
file discovery or a generic doctor result alone is not sufficient when the
host provides a plugin, hook, or session-start bootstrap contract.
```

### Verification Contract

Implementation and release evidence must cover three layers:

1. Deterministic repository checks
   - parse every skill frontmatter with a Kimi-compatible YAML parser
   - validate manifest schema, release-version synchronization, in-repository
     paths, and `sessionStart.skill`
   - reject duplicate Kimi exposure routes in managed test fixtures
2. Isolated host-contract checks
   - install from a release and inspect plugin diagnostics
   - verify enable, disable, update, reload/new-session, resume, and rollback
   - verify the loaded plugin version and managed-copy behavior
3. Live model-routing smoke
   - ambiguous feature -> `brainstorming`
   - bug/regression -> `systematic-debugging`
   - completion claim -> `verification-before-completion`
   - explicit Aegis goal -> `goal-framing`
   - simple factual question -> fast path without a full workflow

The live smoke must report false negatives, false positives, duplicate loads,
and environment-bound gaps. Structural tests alone cannot promote Kimi to a
fresh release-level host verdict.

### Compatibility, Rollback, And Non-Goals

- Existing direct-child users retain a documented rollback path until the
  plugin path has fresh release evidence.
- Plugin updates require the Kimi-native reinstall/update plus `/reload` or a
  new session; editing the original checkout does not mutate Kimi's managed
  copy.
- Installation must not overwrite a user's global `AGENTS.md` or make it a
  second Aegis bootstrap owner.
- The design does not add an MCP server, daemon, background process, new Aegis
  router, or Kimi-only copies of skill bodies.
- Kimi session-start loading is host execution evidence only. It is not an
  authoritative `GateDecision`, `PolicySnapshot`, evidence-sufficiency ruling,
  or final completion authority.

### ADR And Baseline Signal

This direction changes the Kimi install/discovery contract and retains a
compatibility path, so it is ADR-relevant after implementation evidence exists.
Do not create accepted architecture memory from this pending design. At
completion, run the ADR creation gate and synchronize the host compatibility,
known-limitations, activation, trigger-health, release-checklist, and quick-
install baselines with the verified current state.

## Recommended Installation (Updater-Managed Direct-Child)

Keep the Aegis method-pack checkout separate, then register Kimi Code CLI with
Aegis's host-scoped updater. When the host is registered as `kimi`,
`kimi-code`, or `kimi-code-cli`, the updater defaults the discovery shape to
`direct-child`. If `--discovery-root` is omitted, it uses:

```text
$KIMI_CODE_HOME/skills
```

or, when `KIMI_CODE_HOME` is unset:

```text
~/.kimi-code/skills
```

This preserves:

- Kimi native user-level Agent Skills discovery
- Aegis project workspace support through the method-pack root
- update and doctor verification through Aegis scripts
- `~/.agents/skills/` as an optional compatibility fallback

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
cd ~/.codex/aegis
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --reload-hint "restart Kimi Code CLI"
```

If you want to be explicit about the discovery root:

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

Expected structural result:

```text
~/.kimi-code/skills/using-aegis/SKILL.md
~/.kimi-code/skills/systematic-debugging/SKILL.md
~/.kimi-code/skills/brainstorming/SKILL.md
```

The canonical source of truth remains the method-pack root `skills/` tree.
These direct-child directories are a generated host view for Kimi, not a second
editable skill tree.

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

## Complete-Install Verification

Run complete-install verification from the installed Aegis method-pack root.
Do not run the doctor command from the target project directory.

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
python scripts/aegis-doctor.py --discovery-root "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills"
```

Treat the install as complete only when the JSON includes:

```json
{
  "ok": true,
  "workspaceSupport": "available",
  "configStatus": "configured"
}
```

After verification, restart Kimi Code CLI so the running host reloads the
refreshed skill content.

## Updating Aegis

From the method-pack root:

```bash
python scripts/aegis-update.py status --json
python scripts/aegis-update.py update --host kimi-code --json
```

The update registry is host-scoped. Do not update every registered host unless
you explicitly intend to use `--all`.

## Compatibility Fallback

Kimi also scans `~/.agents/skills/`, so a generic direct-child exposure there
can work as a fallback:

```bash
python scripts/aegis-update.py register \
  --host kimi-code \
  --sync-mode junction \
  --discovery-root ~/.agents/skills \
  --reload-hint "restart Kimi Code CLI"
```

Use this only when you intentionally want a cross-tool shared skill surface.
For Kimi-specific installs, prefer `$KIMI_CODE_HOME/skills`.

## Activation Mode

You can make Aegis explicit-only:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

This writes Aegis method-pack configuration only. It does not override Kimi Code CLI.
It does not control Kimi Code CLI's native skill matcher, slash command behavior,
or automatic skill loading rules.

## Authority Boundary

Aegis remains a method pack. Kimi host discovery, reload behavior, and native
skill invocation are Kimi Code CLI concerns. Aegis may provide workflow
discipline, runtime-ready drafts, and verification guidance, but it does not
provide authoritative `GateDecision`, authoritative `PolicySnapshot`, or final
completion authority.
