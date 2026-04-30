#!/usr/bin/env bash

# Shared launcher for Claude Code CLI in bash-based test suites.
#
# Environment overrides:
#   CLAUDE_CMD        - command prefix used to launch Claude (default: claude)
#   CLAUDE_PLUGIN_DIR - optional plugin dir override for commands that need it

claude_cmd="${CLAUDE_CMD:-claude}"

claude_help_supports_plugin_dir() {
    eval "$claude_cmd -h" 2>&1 | grep -q -- '--plugin-dir'
}

run_claude_stream_json_with_plugin_dir() {
    local prompt="$1"
    local plugin_dir="$2"
    local max_turns="$3"
    local log_file="$4"
    local resolved_plugin_dir="${CLAUDE_PLUGIN_DIR:-$plugin_dir}"

    if ! claude_help_supports_plugin_dir; then
        cat > "$log_file" <<EOF
ERROR: Claude CLI command does not support --plugin-dir.
Current command: $claude_cmd
Set CLAUDE_CMD to a newer Claude Code CLI, or use a launcher that supports plugins.
EOF
        return 64
    fi

    local quoted_prompt
    local quoted_plugin_dir
    local quoted_log_file
    local quoted_max_turns

    printf -v quoted_prompt '%q' "$prompt"
    printf -v quoted_plugin_dir '%q' "$resolved_plugin_dir"
    printf -v quoted_log_file '%q' "$log_file"
    printf -v quoted_max_turns '%q' "$max_turns"

    local cmd="$claude_cmd -p $quoted_prompt --plugin-dir $quoted_plugin_dir --dangerously-skip-permissions --max-turns $quoted_max_turns --output-format stream-json --verbose"

    timeout 300 bash -lc "$cmd" > "$log_file" 2>&1 || true
}
