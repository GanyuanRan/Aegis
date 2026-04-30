#!/usr/bin/env bash
# Setup script for OpenCode plugin tests
# Creates an isolated test environment with proper plugin installation
set -euo pipefail

# Get the repository root (two levels up from tests/opencode/).
# Use BASH_SOURCE so this still resolves correctly when the script is sourced.
SETUP_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SETUP_SCRIPT_DIR/../.." && pwd)"

if command -v wslpath > /dev/null 2>&1 && command -v cmd.exe > /dev/null 2>&1; then
    export OPENCODE_BRIDGE_MODE="windows"
else
    export OPENCODE_BRIDGE_MODE="native"
fi

to_opencode_path() {
    local value="$1"

    if [ "$OPENCODE_BRIDGE_MODE" = "windows" ] && command -v wslpath > /dev/null 2>&1; then
        wslpath -w "$value"
    else
        printf '%s\n' "$value"
    fi
}

resolve_test_home_root() {
    local windows_temp_root

    if [ "$OPENCODE_BRIDGE_MODE" = "windows" ]; then
        windows_temp_root="$(cmd.exe /d /c echo %TEMP% 2> /dev/null | tr -d '\r')"
        if [ -n "$windows_temp_root" ]; then
            wslpath -u "$windows_temp_root"
            return
        fi
    fi

    printf '%s\n' "$REPO_ROOT/.tmp"
}

# Create temp home directory for isolation
export TEST_HOME
TEST_HOME_ROOT="$(resolve_test_home_root)"
mkdir -p "$TEST_HOME_ROOT"
TEST_HOME=$(mktemp -d "$TEST_HOME_ROOT/opencode-test-home.XXXXXX")
export HOME="$TEST_HOME"
export XDG_CONFIG_HOME="$TEST_HOME/.config"
export OPENCODE_CONFIG_DIR="$TEST_HOME/.config/opencode"
export OPENCODE_INTEGRATION_SKIP_EXIT=80
export OPENCODE_TEST_MODEL="${OPENCODE_TEST_MODEL:-opencode/big-pickle}"
export OPENCODE_TEST_TIMEOUT_SECONDS="${OPENCODE_TEST_TIMEOUT_SECONDS:-180}"
export OPENCODE_WINDOWS_WRAPPER="$TEST_HOME/opencode-wrapper.cmd"
export OPENCODE_PERSONAL_SKILLS_DIR="$XDG_CONFIG_HOME/skills"

if [ "$OPENCODE_BRIDGE_MODE" = "windows" ]; then
    win_home="$(to_opencode_path "$HOME")"
    win_xdg="$(to_opencode_path "$XDG_CONFIG_HOME")"
    win_config="$(to_opencode_path "$OPENCODE_CONFIG_DIR")"
    win_wrapper="$(to_opencode_path "$OPENCODE_WINDOWS_WRAPPER")"
    printf -v quoted_win_wrapper '%q' "$win_wrapper"

    cat > "$OPENCODE_WINDOWS_WRAPPER" <<EOF
@echo off
set "USERPROFILE=$win_home"
set "HOME=$win_home"
set "XDG_CONFIG_HOME=$win_xdg"
set "OPENCODE_CONFIG_DIR=$win_config"
call opencode.cmd %*
EOF

    export OPENCODE_CMD="${OPENCODE_CMD:-cmd.exe /d /c $quoted_win_wrapper}"
else
    export OPENCODE_CMD="${OPENCODE_CMD:-opencode}"
fi

# Standard install layout:
#   $OPENCODE_CONFIG_DIR/aegis/             ← package root
#   $OPENCODE_CONFIG_DIR/aegis/skills/      ← skills dir (../../skills from plugin)
#   $OPENCODE_CONFIG_DIR/aegis/.opencode/plugins/aegis.js ← plugin file
#   $OPENCODE_CONFIG_DIR/plugins/aegis.js   ← symlink OpenCode reads
#
# Runtime discovery note:
#   The plugin mirrors skills into $OPENCODE_CONFIG_DIR/skills/ at startup so
#   OpenCode can discover them through its documented global skill search path.

AEGIS_DIR="$OPENCODE_CONFIG_DIR/aegis"
AEGIS_SKILLS_DIR="$AEGIS_DIR/skills"
AEGIS_PLUGIN_FILE="$AEGIS_DIR/.opencode/plugins/aegis.js"

# Install skills
mkdir -p "$AEGIS_DIR"
cp -r "$REPO_ROOT/skills" "$AEGIS_DIR/"

# Install plugin
mkdir -p "$(dirname "$AEGIS_PLUGIN_FILE")"
cp "$REPO_ROOT/.opencode/plugins/aegis.js" "$AEGIS_PLUGIN_FILE"

# Preserve ESM semantics for isolated syntax checks.
cat > "$AEGIS_DIR/package.json" <<'EOF'
{
  "type": "module"
}
EOF

# Register plugin via symlink (what OpenCode actually reads)
mkdir -p "$OPENCODE_CONFIG_DIR/plugins"
if [ "$OPENCODE_BRIDGE_MODE" = "windows" ]; then
    cp "$AEGIS_PLUGIN_FILE" "$OPENCODE_CONFIG_DIR/plugins/aegis.js"
else
    ln -sf "$AEGIS_PLUGIN_FILE" "$OPENCODE_CONFIG_DIR/plugins/aegis.js"
fi

# Create test skills in different locations for testing

# Personal test skill
mkdir -p "$OPENCODE_PERSONAL_SKILLS_DIR/personal-test"
cat > "$OPENCODE_PERSONAL_SKILLS_DIR/personal-test/SKILL.md" <<'EOF'
---
name: personal-test
description: Test personal skill for verification
---
# Personal Test Skill

This is a personal skill used for testing.

PERSONAL_SKILL_MARKER_12345
EOF

# Create a project directory for project-level skill tests
mkdir -p "$TEST_HOME/test-project/.opencode/skills/project-test"
cat > "$TEST_HOME/test-project/.opencode/skills/project-test/SKILL.md" <<'EOF'
---
name: project-test
description: Test project skill for verification
---
# Project Test Skill

This is a project skill used for testing.

PROJECT_SKILL_MARKER_67890
EOF

echo "Setup complete: $TEST_HOME"
echo "OPENCODE_CONFIG_DIR:  $OPENCODE_CONFIG_DIR"
echo "Aegis dir:      $AEGIS_DIR"
echo "Skills dir:           $AEGIS_SKILLS_DIR"
echo "Personal skills dir:  $OPENCODE_PERSONAL_SKILLS_DIR"
echo "Plugin file:          $AEGIS_PLUGIN_FILE"
echo "Plugin registered at: $OPENCODE_CONFIG_DIR/plugins/aegis.js"
echo "Test project at:      $TEST_HOME/test-project"

# Helper function for cleanup (call from tests or trap)
cleanup_test_env() {
    if [ -n "${TEST_HOME:-}" ] && [ -d "$TEST_HOME" ]; then
        rm -rf "$TEST_HOME"
    fi
}

opencode_cli_exists() {
    if [ "$OPENCODE_BRIDGE_MODE" = "windows" ]; then
        cmd.exe /d /c where opencode.cmd > /dev/null 2>&1
        return
    fi

    command -v opencode > /dev/null 2>&1
}

opencode_version_probe() {
    local cmd

    cmd="${OPENCODE_CMD} --version"
    timeout "${OPENCODE_TEST_TIMEOUT_SECONDS}s" bash -lc "${cmd}"
}

opencode_runtime_probe() {
    opencode_run_capture "hello" "$HOME" --pure
}

opencode_output_has_runtime_error() {
    local output="$1"

    grep -Eiq \
        "Model not found:|ProviderModelNotFoundError|invalid api key|invalid access token|authentication_error|CreditsError|Insufficient balance|unauthorized|token expired" \
        <<< "$output"
}

opencode_run_capture() {
    local prompt="$1"
    local working_dir="${2:-$PWD}"
    local mode="${3:-}"
    local opencode_working_dir
    local quoted_model
    local quoted_prompt
    local quoted_dir
    local quoted_working_dir
    local cmd

    opencode_working_dir="$(to_opencode_path "$working_dir")"
    printf -v quoted_model '%q' "$OPENCODE_TEST_MODEL"
    printf -v quoted_prompt '%q' "$prompt"
    printf -v quoted_dir '%q' "$opencode_working_dir"
    printf -v quoted_working_dir '%q' "$working_dir"

    cmd="${OPENCODE_CMD} run --print-logs --model ${quoted_model} --dir ${quoted_dir}"
    if [ "$mode" = "--pure" ]; then
        cmd="${cmd} --pure"
    fi
    cmd="${cmd} ${quoted_prompt}"

    timeout "${OPENCODE_TEST_TIMEOUT_SECONDS}s" bash -lc "cd ${quoted_working_dir} && ${cmd}"
}

require_runnable_opencode_or_skip() {
    if ! opencode_cli_exists; then
        echo "  [SKIP] OpenCode not installed - skipping integration tests"
        echo "  To run these tests, install OpenCode: https://opencode.ai"
        exit "$OPENCODE_INTEGRATION_SKIP_EXIT"
    fi

    local probe_output
    if probe_output=$(opencode_version_probe 2>&1); then
        return 0
    fi

    echo "  [SKIP] OpenCode CLI is installed but not runnable in this environment"
    echo "  Probe: opencode --version"
    echo "$probe_output" | sed 's/^/    /'
    echo "  Fix the local OpenCode CLI installation for this platform before rerunning integration tests."
    exit "$OPENCODE_INTEGRATION_SKIP_EXIT"
}

require_working_opencode_runtime_or_skip() {
    local probe_output

    if probe_output=$(opencode_runtime_probe 2>&1); then
        if ! opencode_output_has_runtime_error "$probe_output"; then
            return 0
        fi
    else
        if [ $? -eq 124 ]; then
            echo "  [SKIP] OpenCode runtime probe timed out"
            echo "  Probe: opencode run --pure --model ${OPENCODE_TEST_MODEL} --print-logs \"hello\""
            exit "$OPENCODE_INTEGRATION_SKIP_EXIT"
        fi
    fi

    if ! opencode_output_has_runtime_error "$probe_output"; then
        return 0
    fi

    echo "  [SKIP] OpenCode CLI is runnable but no working runtime model is available for integration tests"
    echo "  Probe: opencode run --pure --model ${OPENCODE_TEST_MODEL} --print-logs \"hello\""
    echo "$probe_output" | sed 's/^/    /'
    echo "  Fix model/auth/credit availability or override OPENCODE_TEST_MODEL before rerunning integration tests."
    exit "$OPENCODE_INTEGRATION_SKIP_EXIT"
}

# Export for use in tests
export -f cleanup_test_env
export -f opencode_output_has_runtime_error
export -f opencode_run_capture
export -f require_runnable_opencode_or_skip
export -f require_working_opencode_runtime_or_skip
export REPO_ROOT
export AEGIS_DIR
export AEGIS_SKILLS_DIR
export AEGIS_PLUGIN_FILE
export SUPERPOWERS_DIR="$AEGIS_DIR"
export SUPERPOWERS_SKILLS_DIR="$AEGIS_SKILLS_DIR"
export SUPERPOWERS_PLUGIN_FILE="$AEGIS_PLUGIN_FILE"
