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

## Verify

```bash
ls -la ~/.agents/skills/aegis
```

You should see a symlink or junction pointing to your aegis skills directory.

For full host guidance and troubleshooting details, read `docs/README.codex.md`.
