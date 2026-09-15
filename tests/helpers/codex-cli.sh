#!/usr/bin/env bash

# Shared launcher for Codex CLI in bash-based test suites.
#
# Environment overrides:
#   CODEX_CMD - command prefix used to launch Codex
#               (default: cmd.exe /d /c codex.cmd so WSL/bash tests use the Windows CLI)
#   CODEX_SMOKE_SUFFIX - optional extra instructions appended to smoke-test prompts

codex_uses_default_windows_launcher=0
if [ -n "${CODEX_CMD:-}" ]; then
    codex_cmd="$CODEX_CMD"
elif command -v cmd.exe >/dev/null 2>&1; then
    # Git Bash can rewrite /d and /c style cmd.exe arguments unless arg
    # conversion is explicitly disabled for this subprocess.
    codex_cmd="MSYS2_ARG_CONV_EXCL='*' cmd.exe /d /c codex.cmd"
    codex_uses_default_windows_launcher=1
else
    codex_cmd="codex"
fi
if [ "${CODEX_SMOKE_SUFFIX+x}" = "x" ]; then
    codex_smoke_suffix="$CODEX_SMOKE_SUFFIX"
else
    codex_smoke_suffix="For this smoke test, do not attempt implementation or modify files. Load the relevant task-specific skill, then briefly state that workflow's first next step only."
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

run_codex_persistent_exec_capture() {
    local prompt="$1"
    local working_dir="$2"
    local log_file="$3"
    local auto_compact_limit="${4:-}"
    local codex_working_dir
    local quoted_prompt
    local quoted_working_dir
    local compact_config=""
    local smoke_timeout="${CODEX_REENTRY_TIMEOUT_SECONDS:-300}"

    codex_working_dir="$(to_codex_working_dir "$working_dir")"
    printf -v quoted_prompt '%q' "$prompt"
    printf -v quoted_working_dir '%q' "$codex_working_dir"
    if [ -n "$auto_compact_limit" ]; then
        compact_config="-c model_auto_compact_token_limit=$auto_compact_limit"
    fi

    local cmd="$codex_cmd exec --json --color never --sandbox workspace-write --skip-git-repo-check --ignore-user-config --ignore-rules $compact_config -C $quoted_working_dir $quoted_prompt"

    timeout "$smoke_timeout" bash -lc "$cmd" > "$log_file" 2>&1
}

run_codex_resume_capture() {
    local thread_id="$1"
    local prompt="$2"
    local log_file="$3"
    local auto_compact_limit="${4:-}"
    local quoted_thread_id
    local quoted_prompt
    local compact_config=""
    local smoke_timeout="${CODEX_REENTRY_TIMEOUT_SECONDS:-300}"

    printf -v quoted_thread_id '%q' "$thread_id"
    printf -v quoted_prompt '%q' "$prompt"
    if [ -n "$auto_compact_limit" ]; then
        compact_config="-c model_auto_compact_token_limit=$auto_compact_limit"
    fi

    # `codex exec resume` intentionally has a narrower option surface than
    # `codex exec`; the persisted session carries its cwd and sandbox policy.
    local cmd="$codex_cmd exec resume --json --ignore-user-config --ignore-rules $compact_config $quoted_thread_id $quoted_prompt"

    timeout "$smoke_timeout" bash -lc "$cmd" > "$log_file" 2>&1
}

codex_thread_id_from_log() {
    local log_file="$1"

    codex_python "$codex_helper_dir/codex_reentry_evidence.py" thread-id "$log_file"
}

codex_log_records_route() {
    local skill_name="$1"
    local log_file="$2"

    codex_python "$codex_helper_dir/codex_reentry_evidence.py" route-record \
        --skill "$skill_name" \
        "$log_file"
}

print_codex_json_first_assistant_excerpt() {
    local log_file="$1"

    codex_python "$codex_helper_dir/codex_reentry_evidence.py" \
        assistant-excerpt "$log_file"
}

codex_session_home() {
    local session_home
    local windows_profile

    if [ -n "${CODEX_REENTRY_SESSION_HOME:-}" ]; then
        session_home="$CODEX_REENTRY_SESSION_HOME"
    elif [ -n "${CODEX_HOME:-}" ]; then
        session_home="$CODEX_HOME"
    elif [ -n "${USERPROFILE:-}" ]; then
        session_home="$USERPROFILE/.codex"
    elif [ "$codex_uses_default_windows_launcher" = "1" ]; then
        windows_profile="$(MSYS2_ARG_CONV_EXCL='*' powershell.exe -NoProfile -NonInteractive -Command '[Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)' 2>/dev/null | tr -d '\r' | tail -n 1)"
        if [ -z "$windows_profile" ]; then
            echo "cannot resolve the Windows Codex session home; set CODEX_REENTRY_SESSION_HOME" >&2
            return 1
        fi
        session_home="$windows_profile/.codex"
    else
        session_home="$HOME/.codex"
    fi

    if command -v wslpath >/dev/null 2>&1; then
        wslpath -u "$session_home"
    else
        printf '%s\n' "$session_home"
    fi
}

print_codex_session_evidence() {
    local thread_id="$1"
    local require_compaction="${2:-false}"
    local session_home

    session_home="$(codex_session_home)"
    codex_python "$codex_helper_dir/codex_reentry_evidence.py" session-summary \
        --codex-home "$session_home" \
        --thread-id "$thread_id" \
        --require-compaction "$require_compaction"
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
