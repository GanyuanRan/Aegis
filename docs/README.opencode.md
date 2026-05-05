# Aegis for OpenCode

Complete guide for using Aegis with [OpenCode.ai](https://opencode.ai).

This page only covers the OpenCode host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Installation

Add aegis to the `plugin` array in your `opencode.json` (global or project-level):

```json
{
  "plugin": ["aegis@git+https://github.com/GanyuanRan/Aegis.git"]
}
```

Restart OpenCode. The plugin auto-installs via Bun, mirrors aegis skills into
OpenCode's global `~/.config/opencode/skills/` discovery path, and injects the bootstrap context automatically.

Verify by asking: "Tell me about your aegis"

### Activation Mode

Aegis defaults to automatic mode. To switch OpenCode to explicit mode, edit:

```text
~/.config/aegis/config.toml
```

Windows:

```text
%USERPROFILE%\.config\aegis\config.toml
```

If the file does not exist, create it manually. Add:

```toml
activation_mode = "explicit"
```

Then restart OpenCode.

`AEGIS_ACTIVATION_MODE` is still available as an environment-variable override
for one-off runs:

```bash
AEGIS_ACTIVATION_MODE=explicit opencode
```

PowerShell one-off run:

```powershell
$env:AEGIS_ACTIVATION_MODE = "explicit"
opencode
```

It is not a field in `opencode.json`. Environment variables override the
user-local config when both are set.

In `explicit` mode, the plugin still mirrors Aegis skills into OpenCode's skill
discovery path, but it does not prepend the compact bootstrap. Use OpenCode's
native `skill` tool or name an Aegis skill directly when you want Aegis.

Before running runtime checks or integration tests, verify the CLI itself is runnable:

```bash
opencode --version
```

If this command fails with a platform-package error, fix the local OpenCode CLI installation first. A binary that exists on `PATH` but cannot execute is not enough for the integration suite.

The current bash-based integration helper also supports Windows CLI bridging. On Windows + bash/WSL it can invoke `cmd.exe /d /c opencode.cmd`, so the next blocker is usually runtime model/auth readiness rather than CLI discovery.

### Migrating from the old symlink-based install

If you previously installed aegis using `git clone` and symlinks, remove the old setup:

```bash
# Remove old symlinks
rm -f ~/.config/opencode/plugins/aegis.js
rm -rf ~/.config/opencode/skills/aegis

# Optionally remove the cloned repo
rm -rf ~/.config/opencode/aegis

# Remove skills.paths from opencode.json if you added one for aegis
```

Then follow the installation steps above.

## Usage

### Finding Skills

Use OpenCode's native `skill` tool to list all available skills:

```
use skill tool to list skills
```

### Loading a Skill

```
use skill tool to load aegis/brainstorming
```

Notes:

- In current OpenCode runtime, bare skill names are the most reliable way to load a skill the host has already discovered.
- OpenCode's official skills docs require skill names to remain unique across locations.
- Project-local skill discovery is based on the current working directory walking up to the git worktree root.
- Do not assume `aegis:` or `project:` prefixes will override duplicate-name resolution. Treat explicit namespace forcing as host-defined unless verified on your exact OpenCode version.

### Personal Skills

Create your own skills in `~/.config/opencode/skills/`:

```bash
mkdir -p ~/.config/opencode/skills/my-skill
```

Create `~/.config/opencode/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Use when [condition] - [what it does]
---

# My Skill

[Your skill content here]
```

### Project Skills

Create project-specific skills in `.opencode/skills/` within your project.

**Skill Priority:** Project skills > Personal skills > Aegis skills

## Updating

Aegis updates automatically when you restart OpenCode. The plugin is re-installed from the git repository on each launch.

To pin a specific version, use a branch or tag:

```json
{
  "plugin": ["aegis@git+https://github.com/GanyuanRan/Aegis.git#v5.0.3"]
}
```

## How It Works

The plugin does two things:

1. **Injects compact bootstrap context** via the `experimental.chat.messages.transform` hook, adding aegis awareness to the first user message without repeating a system message every turn.
2. **Mirrors aegis skills into OpenCode's native global skills path** (`~/.config/opencode/skills/`) so the host discovers them using its documented skill search rules.

The plugin still appends that mirrored path to `config.skills.paths` as a compatibility fallback, but the canonical discovery chain is now the host's documented skills directory rather than an undocumented config-only contract.
Fallback retention and retirement are tracked in `docs/current/AEGIS_KNOWN_LIMITATIONS.md`, not in this host guide.

### Tool Mapping

Skills written for Claude Code are automatically adapted for OpenCode:

- `TodoWrite` → `todowrite`
- `Task` with subagents → OpenCode's `@mention` system
- `Skill` tool → OpenCode's native `skill` tool
- File operations → Native OpenCode tools

## Troubleshooting

### CLI exists but is not runnable

If `command -v opencode` succeeds but `opencode --version` fails, the local OpenCode install is not usable for integration testing on this platform.

Reinstall the correct platform-specific OpenCode package first, then rerun:

```bash
opencode --version
opencode run --print-logs "hello"
```

The `tests/opencode/run-tests.sh --integration` suite treats this as an environment blocker and skips the integration assertions until the CLI is runnable.

### CLI runs, but real sessions fail

If `opencode --version` works but `opencode run ...` fails with model-not-found, invalid-key, expired-token, or insufficient-credit errors, the CLI is present but the runtime is still not healthy enough for integration tests.

The integration suite now probes runtime readiness with:

```bash
OPENCODE_TEST_MODEL=opencode/glm-5 bash tests/opencode/run-tests.sh --integration
```

Override `OPENCODE_TEST_MODEL` to a model/provider pair that is valid on your machine before expecting the integration assertions to run.

### Plugin not loading

1. Check OpenCode logs: `opencode run --print-logs "hello" 2>&1 | grep -i aegis`
2. Verify the plugin line in your `opencode.json` is correct
3. Make sure you're running a recent version of OpenCode

### Skills not found

1. Use OpenCode's `skill` tool to list available skills
2. Check that the plugin is loading (see above)
3. Check that `~/.config/opencode/skills/<skill-name>/SKILL.md` (or the test HOME equivalent) exists after startup
4. Each skill needs a `SKILL.md` file with valid YAML frontmatter

### Bootstrap not appearing

1. Check OpenCode version supports the `experimental.chat.messages.transform` hook
2. Restart OpenCode after config changes
3. Check whether `AEGIS_ACTIVATION_MODE=explicit` is set; explicit mode
   intentionally disables automatic bootstrap injection

## Getting Help

- Report issues: https://github.com/GanyuanRan/Aegis/issues
- Main documentation: https://github.com/GanyuanRan/Aegis
- OpenCode docs: https://opencode.ai/docs/
