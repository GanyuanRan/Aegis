# Installing Aegis for Codex

This page only covers the Codex host install path. For the current `Aegis Method Pack`
authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Prerequisites

- OpenAI Codex CLI
- Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
   ```

2. Create the skills symlink:

   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/aegis/skills ~/.agents/skills/aegis
   ```

   **Windows (PowerShell):**

   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\aegis" "$env:USERPROFILE\.codex\aegis\skills"
   ```

3. Restart Codex.

4. Optional: enable multi-agent support for subagent-heavy skills:

   ```toml
   [features]
   multi_agent = true
   ```

## Activation Mode

`AEGIS_ACTIVATION_MODE=auto|explicit` is the cross-host Aegis activation
profile. It is an environment variable read by host processes that have an
Aegis bootstrap hook; it is not a Codex config file field. Codex uses native
skill discovery, so this environment variable does not override Codex's own
semantic matcher by itself. For an explicit-only Codex setup, keep Aegis skills
available for direct calls and avoid installing an automatic entry profile that
asks Codex to start every conversation with Aegis.

For hook-based hosts, the recommended user-local config is:

```text
~/.config/aegis/config.toml
```

with:

```toml
activation_mode = "explicit"
```

You can also write the shared config from the installed Aegis method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

Switch back to automatic mode with:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Restart Codex or start a new session after changing local Aegis config. In
Codex, this command does not override the host's own semantic skill matcher;
it only configures Aegis bootstrap/profile-aware surfaces.

## Verify

```bash
ls -la ~/.agents/skills/aegis
```

You should see a symlink or junction pointing to your aegis skills directory.

For full host guidance and troubleshooting details, read `docs/README.codex.md`.
