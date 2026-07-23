# Aegis Activation Mode

Status: `Approved`

## 1. Document Scope

This document defines the host activation mode for `Aegis Method Pack`.

This document is only responsible for answering the following questions:

- Whether Aegis injects startup discipline automatically by default
- How users disable automatic injection while preserving explicit invocation
- Which layer the switch belongs to: method-pack / host profile / runtime core

This document is not responsible for answering the following questions:

- Final policy enforcement of a future runtime core
- Per-host internal token budget implementation
- Automatic TDD strictness; see `docs/current/AEGIS_TDD_MODE.md`
- Whether the host-native skill matcher still auto-matches a skill when bootstrap is not injected

---

## 2. Bottom Line Up Front

Aegis host-side activation mode is jointly defined by the user's local configuration and environment variables:

- `auto`: Default mode. Aegis may automatically inject a compact bootstrap and participate in skill routing discipline.
- `explicit`: Explicit mode. Aegis does not automatically inject bootstrap; the agent only uses Aegis when the user explicitly invokes Aegis or a specific Aegis skill.

No configuration file is required by default; the absence of configuration is equivalent to:

```text
activation_mode = "auto"
```

Currently only `auto` and `explicit` are defined. `off` is not defined for now, to avoid confusing "disable automatic intervention" with "uninstall or hide all skills."

---

## 3. Explicit Invocation Semantics

The recommended configuration method is a user-local configuration file:

```text
~/.config/aegis/config.toml
```

Windows:

```text
%USERPROFILE%\.config\aegis\config.toml
```

Installation does not automatically create this file. When explicit mode is needed, manually create the directory and file, and write:

```toml
activation_mode = "explicit"
```

The same config can be written from the installed Aegis method-pack root:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode explicit
```

To switch back to auto mode, write:

```toml
activation_mode = "auto"
```

You may also delete the file to return to the default `auto`. The command form
is:

```bash
cd <aegis-method-pack-root>
python scripts/aegis-doctor.py activation-mode auto
```

Do not run these commands from the target project directory; `aegis-doctor.py`
belongs to the installed Aegis method-pack root.

The advanced temporary override method is the environment variable `AEGIS_ACTIVATION_MODE`. It must be present in the process environment before the host process starts, and takes precedence over the user-local configuration file.

One-shot terminal launch examples:

```bash
AEGIS_ACTIVATION_MODE=explicit opencode
AEGIS_ACTIVATION_MODE=explicit claude
```

PowerShell one-shot launch examples:

```powershell
$env:AEGIS_ACTIVATION_MODE = "explicit"
opencode
# or: claude
```

Long-term configuration methods:

- bash/zsh users may write `export AEGIS_ACTIVATION_MODE=explicit` into `~/.zshrc` or `~/.bashrc`
- PowerShell users may write `$env:AEGIS_ACTIVATION_MODE = "explicit"` into `$PROFILE`, or use `[Environment]::SetEnvironmentVariable(...)` to set a system / user environment variable
- GUI-launched hosts must be started from a launcher, shell, or system environment that already carries the environment variable
- After modification, the host must be restarted, reloaded, or opened as a new host session; an already-running session typically does not automatically inherit the new value

Read priority:

1. `AEGIS_ACTIVATION_MODE`
2. `~/.config/aegis/config.toml`
3. Default `auto`

In `explicit` mode, the following inputs should still allow Aegis to be used:

- `use aegis`
- `用 Aegis`
- `aegis:using-aegis`
- `use aegis:brainstorming`
- `调用 aegis:test-driven-development`
- Other direct skill invocation forms supported by the host

`explicit` only disables automatic bootstrap injection; it does not remove Aegis skills, uninstall the plugin, or prohibit the user from invoking Aegis by name.

---

## 4. Layering Boundary

This switch belongs to the host / profile rule layer:

- The method-pack defines the mode semantics
- The host install surface is responsible for reading the variable and adjusting bootstrap injection
- A future host adapter may upgrade it to a more formal profile configuration
- Only a future runtime core can assume authoritative enforcement

Therefore, `explicit` mode must not be written as a final `GateDecision`, `PolicySnapshot`, or completion authority.

---

## 5. Host Behavior

Hosts that support automatic bootstrap injection should follow these rules:

1. `auto` or unset: maintain existing automatic injection behavior.
2. `explicit`: do not automatically inject `using-aegis` bootstrap.
3. Unrecognized value: conservatively fall back to `auto`, to avoid silently disabling Aegis.

Hosts that rely solely on host-native skill discovery should state in installation docs:

- Aegis can be explicitly invoked
- The host's own semantic skill matcher may still be controlled by the host
- If the user needs to enforce explicit mode, they should use host-supported profile / install configuration to hide or not install the auto-entry skill

Kimi Code CLI uses installation profiles to make this boundary enforceable:

- `kimi-code-auto` requires exactly one enabled Aegis plugin whose
  `sessionStart.skill` is `using-aegis`, with no direct-child Aegis exposure.
- `kimi-code-explicit` requires no enabled Aegis plugin and exactly one
  updater-managed direct-child discovery root.

Writing `activation_mode = "explicit"` does not disable Kimi's plugin or
override its native session-start contract. The user must switch the Kimi
installation profile and then `/reload` or open `/new`.

---

## 6. Verification Boundary

Minimum verification includes:

- `auto` mode still injects bootstrap
- `explicit` mode does not inject bootstrap
- Aegis skills remain installed and discoverable
- Documentation clearly states that explicit invocation is still available

These verifications are method-pack evidence only and do not grant authoritative runtime completion.
