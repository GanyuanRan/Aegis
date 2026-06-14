#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_not_contains_text() {
    local text="$1"
    local pattern="$2"
    local label="$3"

    if printf '%s' "$text" | grep -qE "$pattern"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== Activation Mode Check ==="

session_hook="hooks/session-start"
opencode_plugin=".opencode/plugins/aegis.js"
activation_doc="docs/current/AEGIS_ACTIVATION_MODE.md"
tdd_mode_doc="docs/current/AEGIS_TDD_MODE.md"

assert_contains "$activation_doc" "AEGIS_ACTIVATION_MODE" \
    "activation mode canonical doc names the environment variable"
assert_contains "$activation_doc" "auto.*explicit|explicit.*auto" \
    "activation mode canonical doc defines auto and explicit"
assert_contains "$activation_doc" "explicit" \
    "activation mode canonical doc preserves explicit invocation semantics"
assert_contains "$activation_doc" "environment" \
    "activation mode canonical doc says the mode is an environment variable"
assert_contains "$activation_doc" "PowerShell" \
    "activation mode canonical doc includes PowerShell usage"
assert_contains "$activation_doc" "zshrc|bashrc|PROFILE|system environment" \
    "activation mode canonical doc explains persistent setup"
assert_contains "$activation_doc" "~/.config/aegis/config.toml" \
    "activation mode canonical doc defines user-local config path"
assert_contains "$activation_doc" 'activation_mode = "explicit"' \
    "activation mode canonical doc shows explicit config value"
assert_contains "$activation_doc" 'aegis-doctor\.py activation-mode explicit' \
    "activation mode canonical doc documents doctor explicit command"
assert_contains "$activation_doc" 'aegis-doctor\.py activation-mode auto' \
    "activation mode canonical doc documents doctor auto command"
assert_contains "$activation_doc" 'restart|new host session' \
    "activation mode canonical doc states command changes need restart or new session"

assert_contains "$session_hook" "AEGIS_ACTIVATION_MODE" \
    "session hook reads activation mode"
assert_contains "$session_hook" "AEGIS_TDD_MODE" \
    "session hook reads TDD mode"
assert_contains "$session_hook" "explicit" \
    "session hook handles explicit activation mode"
if [[ -x "$session_hook" ]]; then
    pass "session hook is executable"
elif git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    && git ls-files -s "$session_hook" | grep -q '^100755 '; then
    pass "session hook is executable in git index"
else
    fail "session hook is executable"
fi

assert_contains "$opencode_plugin" "AEGIS_ACTIVATION_MODE" \
    "OpenCode plugin reads activation mode"
assert_contains "$opencode_plugin" "AEGIS_TDD_MODE" \
    "OpenCode plugin reads TDD mode"
assert_contains "$opencode_plugin" "explicit" \
    "OpenCode plugin handles explicit activation mode"

hook_auto_output="$("$session_hook")"
if printf '%s' "$hook_auto_output" | grep -q "You have Aegis"; then
    pass "session hook auto mode injects bootstrap by default"
else
    fail "session hook auto mode injects bootstrap by default"
fi
if printf '%s' "$hook_auto_output" | grep -q "Aegis TDD mode: auto"; then
    pass "session hook auto mode reports default TDD mode"
else
    fail "session hook auto mode reports default TDD mode"
fi

hook_tdd_off_output="$(AEGIS_TDD_MODE=off "$session_hook")"
if printf '%s' "$hook_tdd_off_output" | grep -q "Aegis TDD mode: off"; then
    pass "session hook environment variable overrides TDD mode"
else
    fail "session hook environment variable overrides TDD mode"
fi

hook_explicit_output="$(AEGIS_ACTIVATION_MODE=explicit "$session_hook")"
assert_not_contains_text "$hook_explicit_output" "You have Aegis" \
    "session hook explicit mode does not inject bootstrap"
assert_contains_text_pattern='^\{\}$|additionalContext": ""|additional_context": ""|additionalContext": null|additional_context": null'
if printf '%s' "$hook_explicit_output" | grep -qE "$assert_contains_text_pattern"; then
    pass "session hook explicit mode emits an empty context payload"
else
    fail "session hook explicit mode emits an empty context payload"
fi

tmp_home="$(mktemp -d)"
trap 'rm -rf "$tmp_home"' EXIT
mkdir -p "$tmp_home/.config/aegis"
cat > "$tmp_home/.config/aegis/config.toml" <<'EOF'
activation_mode = "explicit"
tdd_mode = "off"
EOF

hook_config_output="$(HOME="$tmp_home" "$session_hook")"
assert_not_contains_text "$hook_config_output" "You have Aegis" \
    "session hook reads explicit mode from user-local config"

hook_env_override_output="$(HOME="$tmp_home" AEGIS_ACTIVATION_MODE=auto "$session_hook")"
if printf '%s' "$hook_env_override_output" | grep -q "You have Aegis"; then
    pass "session hook environment variable overrides user-local config"
else
    fail "session hook environment variable overrides user-local config"
fi
if printf '%s' "$hook_env_override_output" | grep -q "Aegis TDD mode: off"; then
    pass "session hook reads TDD mode from user-local config"
else
    fail "session hook reads TDD mode from user-local config"
fi

assert_contains "$tdd_mode_doc" "AEGIS_TDD_MODE" \
    "TDD mode canonical doc names the environment variable"
assert_contains "$tdd_mode_doc" 'tdd_mode = "off"' \
    "TDD mode canonical doc shows off config value"
assert_contains "$tdd_mode_doc" 'aegis-doctor\.py tdd-mode off' \
    "TDD mode canonical doc documents doctor off command"
assert_contains "$tdd_mode_doc" 'restart|new host session' \
    "TDD mode canonical doc states command changes need restart or new session"

assert_contains "docs/README.opencode.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "OpenCode guide documents explicit activation mode"
assert_contains "docs/README.opencode.md" 'not a field in `opencode.json`' \
    "OpenCode guide clarifies activation mode is not opencode.json config"
assert_contains "docs/README.opencode.md" 'aegis-doctor\.py activation-mode explicit' \
    "OpenCode guide documents doctor activation command"
assert_contains "docs/README.claude-code.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "Claude Code guide documents explicit activation mode"
assert_contains "docs/README.claude-code.md" "PowerShell" \
    "Claude Code guide includes PowerShell usage"
assert_contains "docs/README.claude-code.md" 'aegis-doctor\.py activation-mode explicit' \
    "Claude Code guide documents doctor activation command"
assert_contains "docs/README.cc-gui.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "CC GUI guide documents explicit activation caveat"
assert_contains "docs/README.cc-gui.md" "does not override CC GUI" \
    "CC GUI guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.codex.md" "explicit" \
    "Codex guide documents explicit activation caveat"
assert_contains "docs/README.codex.md" 'aegis-doctor\.py activation-mode explicit' \
    "Codex guide documents doctor activation command"
assert_contains "docs/README.codebuddy.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "CodeBuddy guide documents explicit activation caveat"
assert_contains "docs/README.codebuddy.md" "does not override CodeBuddy" \
    "CodeBuddy guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.deepseek-tui.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "DeepSeek-TUI guide documents explicit activation caveat"
assert_contains "docs/README.deepseek-tui.md" "does not override DeepSeek-TUI" \
    "DeepSeek-TUI guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.trae.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "Trae guide documents explicit activation caveat"
assert_contains "docs/README.trae.md" "does not override Trae" \
    "Trae guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.copilot.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "GitHub Copilot guide documents explicit activation caveat"
assert_contains "docs/README.copilot.md" "does not override GitHub Copilot" \
    "GitHub Copilot guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.qoder.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "Qoder guide documents explicit activation caveat"
assert_contains "docs/README.qoder.md" "does not override Qoder" \
    "Qoder guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.pi.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "Pi guide documents explicit activation caveat"
assert_contains "docs/README.pi.md" "does not override Pi" \
    "Pi guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.openclaw.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "OpenClaw guide documents explicit activation caveat"
assert_contains "docs/README.openclaw.md" "does not override OpenClaw" \
    "OpenClaw guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.hermes-agent.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "Hermes Agent guide documents explicit activation caveat"
assert_contains "docs/README.hermes-agent.md" "does not override Hermes Agent" \
    "Hermes Agent guide clarifies activation mode does not control native matcher"
assert_contains "docs/README.zcode.md" "AEGIS_ACTIVATION_MODE=explicit" \
    "ZCode guide documents explicit activation caveat"
assert_contains "docs/README.zcode.md" "does not override ZCode" \
    "ZCode guide clarifies activation mode does not control native matcher"
assert_contains "README.en.md" 'aegis-doctor\.py activation-mode explicit' \
    "English README gives concise doctor activation command"
assert_contains "README.md" 'aegis-doctor\.py activation-mode explicit' \
    "Chinese README gives concise doctor activation command"
assert_contains "README.md" 'docs/current/AEGIS_ACTIVATION_MODE\.md' \
    "Chinese README delegates detailed activation setup to canonical docs"
assert_contains ".codex/INSTALL.md" 'aegis-doctor\.py activation-mode explicit' \
    "Codex install surface documents doctor activation command"
assert_contains ".opencode/INSTALL.md" 'aegis-doctor\.py activation-mode explicit' \
    "OpenCode install surface documents doctor activation command"
assert_contains ".cursor/INSTALL.md" 'aegis-doctor\.py activation-mode explicit' \
    "Cursor install surface documents doctor activation command"
assert_contains ".windsurf/INSTALL.md" 'aegis-doctor\.py activation-mode explicit' \
    "Windsurf install surface documents doctor activation command"

if (( failures > 0 )); then
    echo ""
    echo "Activation mode check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Activation mode check passed."
