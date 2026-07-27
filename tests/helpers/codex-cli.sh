#!/usr/bin/env bash

# Shared launcher for Codex CLI in bash-based test suites.
#
# Environment overrides:
#   CODEX_CMD - command prefix used to launch Codex
#               (default: cmd.exe /d /c codex.cmd so WSL/bash tests use the Windows CLI)
#   CODEX_SMOKE_SUFFIX - optional extra instructions appended to smoke-test prompts

if [ -n "${CODEX_CMD:-}" ]; then
    codex_cmd="$CODEX_CMD"
elif command -v cmd.exe >/dev/null 2>&1; then
    # Git Bash can rewrite /d and /c style cmd.exe arguments unless arg
    # conversion is explicitly disabled for this subprocess.
    codex_cmd="MSYS2_ARG_CONV_EXCL='*' cmd.exe /d /c codex.cmd"
else
    codex_cmd="codex"
fi
if [ "${CODEX_SMOKE_SUFFIX+x}" = "x" ]; then
    codex_smoke_suffix="$CODEX_SMOKE_SUFFIX"
else
    codex_smoke_suffix="For this smoke test, do not attempt full implementation. Briefly state the first skill/workflow you would use and the first next step only."
fi
codex_helper_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex_parser_script="$codex_helper_dir/parse_codex_skills.py"

codex_python() {
    if [ -n "${CODEX_PYTHON_CMD:-}" ]; then
        "$CODEX_PYTHON_CMD" "$@"
        return
    fi

    if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
        python3 "$@"
        return
    fi

    if command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
        py -3 "$@"
        return
    fi

    python "$@"
}

to_codex_working_dir() {
    local working_dir="$1"

    if command -v cygpath >/dev/null 2>&1; then
        cygpath -aw "$working_dir"
        return
    fi

    if command -v wslpath >/dev/null 2>&1; then
        wslpath -w "$working_dir"
        return
    else
        printf '%s\n' "$working_dir"
    fi
}

run_codex_exec_capture() {
    local prompt="$1"
    local working_dir="$2"
    local log_file="$3"
    local codex_working_dir
    local effective_prompt

    local quoted_prompt
    local quoted_working_dir

    codex_working_dir="$(to_codex_working_dir "$working_dir")"
    effective_prompt="$prompt"
    if [ -n "$codex_smoke_suffix" ]; then
        effective_prompt="${effective_prompt}"$'\n\n'"${codex_smoke_suffix}"
    fi
    printf -v quoted_prompt '%q' "$effective_prompt"
    printf -v quoted_working_dir '%q' "$codex_working_dir"

    local cmd="$codex_cmd exec --color never --skip-git-repo-check --ephemeral -C $quoted_working_dir $quoted_prompt"

    timeout 300 bash -lc "$cmd" > "$log_file" 2>&1 || true
}

run_codex_benchmark_capture() {
    local prompt="$1"
    local working_dir="$2"
    local log_file="$3"
    local codex_working_dir
    local quoted_prompt
    local quoted_working_dir
    local benchmark_cmd="${CODEX_BENCHMARK_CMD:-$codex_cmd}"
    local benchmark_timeout="${CODEX_BENCHMARK_TIMEOUT_SECONDS:-300}"

    codex_working_dir="$(to_codex_working_dir "$working_dir")"
    printf -v quoted_prompt '%q' "$prompt"
    printf -v quoted_working_dir '%q' "$codex_working_dir"

    local cmd="$benchmark_cmd exec --json --color never --sandbox workspace-write --skip-git-repo-check --ephemeral -C $quoted_working_dir $quoted_prompt"

    timeout "$benchmark_timeout" bash -lc "$cmd" > "$log_file" 2>&1
}

codex_log_mentions_skill() {
    local skill_name="$1"
    local log_file="$2"

    codex_loaded_skills "$log_file" | grep -Fxq "$skill_name"
}

codex_loaded_skills() {
    local log_file="$1"
    codex_python "$codex_parser_script" loaded-skills "$log_file"
}

codex_first_skill_load_line() {
    local skill_name="$1"
    local log_file="$2"

    codex_python "$codex_parser_script" first-skill-load-line "$log_file" "$skill_name"
}

print_codex_skills_triggered() {
    local log_file="$1"

    codex_loaded_skills "$log_file"
}

print_codex_first_assistant_excerpt() {
    local log_file="$1"

    awk '
        /^codex$/ { getline; print; exit }
    ' "$log_file" | head -c 500
}
