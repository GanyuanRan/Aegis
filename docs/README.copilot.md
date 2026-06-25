# Aegis for GitHub Copilot

Guide for using Aegis with GitHub Copilot through Copilot coding agent skills,
repository instructions, optional repository hooks, and AGENTS-style project
guidance.

This page only covers the GitHub Copilot host install path. For the current
`Aegis Method Pack` authority order, release gate, host compatibility status,
and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Current Verdict

GitHub Copilot is structurally compatible with Aegis because current official
Copilot guidance supports:

- repository-scoped agent skills under `.github/skills/`
- repository custom instructions under `.github/copilot-instructions.md`
- repository hooks under `.github/hooks/*.json`
- project guidance through `AGENTS.md`

Aegis can reuse those surfaces without changing its method-pack boundary.

This guide records structural compatibility and repository-surface install
support. It does **not** claim current release-level live smoke evidence for
GitHub Copilot.

## Recommended Complete Installation

Keep a local Aegis checkout and expose the method-pack through repository
surfaces that Copilot already understands. This preserves both skill
discoverability and project workspace support verification.

## Repository Installation

Inside the target repository:

### macOS / Linux

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.copilot/aegis
mkdir -p .github/skills

for skill_dir in ~/.copilot/aegis/skills/*/; do
  skill_name=$(basename "$skill_dir")
  ln -sfn "$skill_dir" ".github/skills/aegis-${skill_name}"
done
```

### Windows PowerShell

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.copilot\aegis"
New-Item -ItemType Directory -Force -Path ".github\skills" | Out-Null

Get-ChildItem "$env:USERPROFILE\.copilot\aegis\skills" -Directory | ForEach-Object {
  $linkPath = ".github\skills\aegis-$($_.Name)"
  if (Test-Path $linkPath) { Remove-Item $linkPath -Recurse -Force }
  New-Item -ItemType Junction -Path $linkPath -Target $_.FullName | Out-Null
}
```

This exposes each Aegis skill directly at:

```text
.github/skills/aegis-<skill-name>/SKILL.md
```

The `aegis-` prefix is only the Copilot-visible repository skill name policy.
The canonical method-pack source remains `skills/<skill-name>/SKILL.md`.

Because the checkout remains at `~/.copilot/aegis`, project workspace support
can be verified from that method-pack root.

## Optional Repository Hook Bootstrap

GitHub Copilot can also read repository hook files from:

```text
.github/hooks/*.json
```

This repository now ships a Copilot-native `sessionStart` hook config at:

```text
.github/hooks/session-start.json
```

It uses:

- `bash` on macOS and Linux
- `powershell` on Windows

The hook reuses [hooks/session-start](/E:/Aegis/hooks/session-start:1) as the
canonical bootstrap owner and forces compact single-line JSON output for
Copilot's command-hook contract.

If you want the same bootstrap in another repository, copy:

- `.github/hooks/session-start.json`
- `hooks/session-start`
- `hooks/copilot-session-start.ps1`

Keep the local Aegis checkout when you also need complete workspace support
verification. The hook bootstrap is optional convenience, not the complete
install boundary by itself.

## Repository Guidance Surfaces

GitHub Copilot can also read:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/hooks/session-start.json`

For Aegis, these files should reinforce routing and boundary discipline, not
replace the skill bodies. Keep detailed workflow logic in `skills/`, and keep
repository instructions concise.

## Verification

Open the repository in a Copilot-supported environment and ask:

```text
Tell me which Aegis skill you would use before debugging a failing test.
```

Expected result:

- Copilot can see Aegis skills under `.github/skills/`
- Copilot can load the relevant skill on demand
- Copilot can inject the compact Aegis bootstrap when `.github/hooks/session-start.json` is active
- repository instructions can point back to `AGENTS.md` and Aegis guidance
- Aegis remains method-pack discipline, not a full runtime platform or final
  completion authority

Portable goal entry:

```text
Aegis goal: Fix the auth refresh bug without rewriting the auth system.
```

Use this when you want `goal-framing` to set goal, success evidence, stop
condition, and non-goals before routing onward. `/aegis-goal <task>` is an
optional shortcut only when the current host/session supports slash-style
aliases.

For complete-install verification, also run this from the local Aegis checkout
when filesystem access is available:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

Do not run the doctor command from the target project directory; it belongs to
the installed Aegis method-pack root.

Treat the install as complete only if the JSON reports `"ok": true`,
`"workspaceSupport": "available"`, and `"configStatus": "configured"`.

To verify the Copilot-visible repository skill discovery view, run doctor from
the method-pack checkout and pass the target repository's `.github/skills`
directory plus the explicit name prefix:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --discovery-root <target-repo>/.github/skills --discovery-name-prefix aegis-
```

This checks that `.github/skills/aegis-<skill-name>/SKILL.md` still exposes the
current canonical skill bodies without making the prefixed repository view a
second source of truth.

## Updating

### macOS / Linux

```bash
cd ~/.copilot/aegis
git pull
```

### Windows PowerShell

```powershell
Set-Location "$env:USERPROFILE\.copilot\aegis"
git pull
```

The skill links point into the checkout, so they pick up changes automatically.
Restart the Copilot session or reopen the repository if the host caches skill
metadata.

## Activation Mode

GitHub Copilot uses native repository skills, instructions, and optional hooks.

If the repository hook bootstrap is enabled, `AEGIS_ACTIVATION_MODE=explicit`
still disables the injected Aegis bootstrap by making the hook emit `{}`.
Copilot's native skill matcher remains separate. For explicit use, ask Copilot
to load an Aegis skill directly, or mention the relevant skill name in your
request.

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

Restart the Copilot session after changing local Aegis config. For this host,
the command controls only the optional Aegis bootstrap hook output; it does not
override GitHub Copilot's native matcher.
It does not override GitHub Copilot itself or turn Copilot's native repository
matcher into an Aegis-owned routing decision.

## Uninstalling

Remove the linked Aegis skill directories from:

```text
.github/skills/
```

If you no longer want the local checkout, remove `~/.copilot/aegis` after the
repository links are gone.

## Troubleshooting

### Skills are not visible

1. Confirm `.github/skills/aegis-<skill-name>/SKILL.md` exists.
2. From the method-pack checkout, run `python scripts/aegis-doctor.py --discovery-root <target-repo>/.github/skills --discovery-name-prefix aegis-`.
3. Reopen the repository or start a new Copilot session.
4. Check whether another repository instruction surface is shadowing the skill
   request.
5. Keep detailed workflow logic in the skill body instead of only in
   `.github/copilot-instructions.md`.

### Session-start hook fails on Windows

If a Copilot repository hook reports a PowerShell parse error around:

```text
"...run-hook.cmd" session-start
```

do not point Copilot at `hooks/run-hook.cmd`. That wrapper belongs to the
Claude Code plugin hook contract, not Copilot's repository hook contract.

Use `.github/hooks/session-start.json` instead. On Windows, Copilot expects a
`powershell` hook entry or a PowerShell-safe command string.

### Project workspace support not verified

If only the `.github/skills/` surface remains and the local checkout was
removed, skill discovery may still work but complete project workspace support
is not proven. Restore the checkout and run this from the method-pack root, not
from the target project directory:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py --write-config --json
```

The JSON should include `"workspaceSupport": "available"` and
`"configStatus": "configured"`.

## Official GitHub Copilot References

- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks
- https://docs.github.com/en/copilot/reference/hooks-reference
