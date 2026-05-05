# Installing Aegis for OpenCode

This page only covers the OpenCode host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed

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

Then restart OpenCode. `AEGIS_ACTIVATION_MODE` remains available as an
environment-variable override for one-off runs:

```bash
AEGIS_ACTIVATION_MODE=explicit opencode
```

Before running runtime checks or integration tests, verify the CLI itself is runnable:

```bash
opencode --version
```

If this command fails with a platform-package error, fix the local OpenCode CLI installation first. A binary that exists on `PATH` but cannot execute is not enough for the integration suite.

## Migrating from the old symlink-based install

If you previously installed aegis using `git clone` and symlinks, remove the old setup:

```bash
rm -f ~/.config/opencode/plugins/aegis.js
rm -rf ~/.config/opencode/skills/aegis
rm -rf ~/.config/opencode/aegis
```

Then follow the installation steps above.

## Usage

Use OpenCode's native `skill` tool:

```text
use skill tool to list skills
use skill tool to load aegis/brainstorming
```

For current host behavior, fallback notes, and troubleshooting details, read `docs/README.opencode.md`.
