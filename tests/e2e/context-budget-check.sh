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

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

char_count() {
    wc -c < "$1" | tr -d '[:space:]'
}

assert_growth_budget() {
    local file="$1"
    local baseline="$2"
    local allowance="$3"
    local label="$4"

    if [[ ! -f "$file" ]]; then
        fail "$label exists"
        return
    fi

    local current ceiling
    current="$(char_count "$file")"
    ceiling=$((baseline + allowance))
    if (( current <= ceiling )); then
        pass "$label is <= ${ceiling} chars (${current})"
    else
        fail "$label is <= ${ceiling} chars (${current})"
    fi
}

echo "=== Context Budget Check ==="

using_aegis="skills/using-aegis/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
prompt_hygiene_doc="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
verification_skill="skills/verification-before-completion/SKILL.md"
log_window_script="scripts/log-window.sh"
max_hot_path_chars=2500
max_debugging_main_chars=10000
max_verification_main_chars=7000
max_combined_main_chars=17000

if [[ ! -f "$using_aegis" ]]; then
    fail "using-aegis skill exists"
else
    skill_chars="$(char_count "$using_aegis")"
    if (( skill_chars <= max_hot_path_chars )); then
        pass "using-aegis hot path is <= ${max_hot_path_chars} chars (${skill_chars})"
    else
        fail "using-aegis hot path is <= ${max_hot_path_chars} chars (${skill_chars})"
    fi
fi

debugging_skill="skills/systematic-debugging/SKILL.md"
debugging_advanced="skills/systematic-debugging/advanced-debugging-governance.md"
if [[ -f "$debugging_skill" && -f "$debugging_advanced" ]]; then
    debugging_chars="$(char_count "$debugging_skill")"
    if (( debugging_chars <= max_debugging_main_chars )); then
        pass "systematic-debugging main body is <= ${max_debugging_main_chars} chars (${debugging_chars})"
    else
        fail "systematic-debugging main body is <= ${max_debugging_main_chars} chars (${debugging_chars})"
    fi
    pass "systematic-debugging main and advanced owner both exist"
elif [[ -f "$debugging_skill" || -f "$debugging_advanced" ]]; then
    fail "systematic-debugging extraction rejects partial main/reference state"
else
    fail "systematic-debugging main and advanced owner exist"
fi

verification_expanded="skills/verification-before-completion/expanded-closeout.md"
if [[ -f "$verification_skill" && -f "$verification_expanded" ]]; then
    verification_chars="$(char_count "$verification_skill")"
    if (( verification_chars <= max_verification_main_chars )); then
        pass "verification main body is <= ${max_verification_main_chars} chars (${verification_chars})"
    else
        fail "verification main body is <= ${max_verification_main_chars} chars (${verification_chars})"
    fi
    pass "verification main and expanded owner both exist"
elif [[ -f "$verification_skill" || -f "$verification_expanded" ]]; then
    fail "verification extraction rejects partial main/reference state"
else
    fail "verification main and expanded owner exist"
fi

if [[ -f "$debugging_skill" && -f "$debugging_advanced" && -f "$verification_skill" && -f "$verification_expanded" ]]; then
    debugging_chars="$(char_count "$debugging_skill")"
    verification_chars="$(char_count "$verification_skill")"
    combined_chars=$((debugging_chars + verification_chars))
    if (( combined_chars <= max_combined_main_chars )); then
        pass "combined debugging and verification main bodies are <= ${max_combined_main_chars} chars (${combined_chars})"
    else
        fail "combined debugging and verification main bodies are <= ${max_combined_main_chars} chars (${combined_chars})"
    fi
else
    fail "combined main-body ceiling requires complete debugging/verification owners"
fi
assert_growth_budget "skills/executing-plans/SKILL.md" 7823 450 \
    "executing-plans bounded growth"
assert_growth_budget "skills/long-task-continuation/SKILL.md" 11247 650 \
    "long-task-continuation bounded growth"

if [[ -f "$discipline_ref" ]]; then
    pass "using-aegis discipline reference exists"
    assert_contains "$discipline_ref" "Red Flags" "discipline reference keeps red flags out of hot path"
    assert_contains "$discipline_ref" "Skill Priority" "discipline reference keeps priority details available"
else
    fail "using-aegis discipline reference exists"
fi

assert_contains "$using_aegis" "session|transcript|history|log" \
    "using-aegis hot path includes history/log search guardrail"
assert_contains "$using_aegis" "limit|bounded|scope|time" \
    "using-aegis hot path requires bounded historical searches"
assert_contains "$using_aegis" "candidates, not prompt payloads" \
    "using-aegis treats external outputs as evidence candidates"
assert_contains "$using_aegis" "Spec Brief or Design Spec only" \
    "using-aegis keeps spec/design as conditional routing, not default ceremony"
assert_not_contains "$using_aegis" "scripts/aegis-workspace.py init" \
    "using-aegis hot path does not hardcode workspace helper commands"

if [[ -f "$prompt_hygiene_doc" ]]; then
    pass "prompt hygiene canonical doc exists"
    assert_contains "$prompt_hygiene_doc" "Evidence Index Before Evidence Payload" \
        "prompt hygiene requires evidence index before raw payload"
    assert_contains "$prompt_hygiene_doc" "readbackNeeded" \
        "prompt hygiene defines readback-needed evidence indexing"
    assert_contains "$prompt_hygiene_doc" "PROMPT_POLICY_WARNING" \
        "prompt hygiene symbolises repeated policy warning text"
    assert_contains "$prompt_hygiene_doc" "Serena|semantic retrieval|MCP" \
        "prompt hygiene covers MCP and semantic retrieval output"
    assert_contains "$prompt_hygiene_doc" "not.*pollution source|not.*contamination source" \
        "prompt hygiene distinguishes tools from prompt payload contamination"
    assert_contains "$prompt_hygiene_doc" "complete error text.*repeatedly|full error text.*reflow|full error text.*repeated" \
        "prompt hygiene prevents repeated full policy warning text from re-entering context"
    assert_contains "$prompt_hygiene_doc" "Host Context Intake Discipline" \
        "prompt hygiene defines host context intake discipline"
    assert_contains "$prompt_hygiene_doc" "bounded evidence intake" \
        "prompt hygiene names bounded evidence intake as the stable owner"
    assert_contains "$prompt_hygiene_doc" "index.*window.*excerpt" \
        "prompt hygiene uses index-window-excerpt flow for large inputs"
else
    fail "prompt hygiene canonical doc exists"
fi

if [[ -f "$log_window_script" ]]; then
    pass "bounded log window helper exists"

    tmp_log="$(mktemp)"
    tmp_out="$(mktemp)"
    trap 'rm -f "$tmp_log" "$tmp_out"' EXIT
    cat > "$tmp_log" <<'EOF'
line one
first Invalid prompt
line three
latest Invalid prompt
line five
EOF

    if bash "$log_window_script" "$tmp_log" "Invalid prompt" 1 > "$tmp_out"; then
        assert_contains "$tmp_out" "match_line=4 window=3,5" \
            "bounded log window helper finds latest match and reports a small window"
        assert_contains "$tmp_out" "latest Invalid prompt" \
            "bounded log window helper includes matching line"
        assert_not_contains "$tmp_out" "line one" \
            "bounded log window helper does not emit unrelated log prefix"
    else
        fail "bounded log window helper runs on a file"
    fi

    if bash "$log_window_script" "." "Invalid prompt" 1 > "$tmp_out" 2>&1; then
        fail "bounded log window helper refuses directory input"
    else
        assert_contains "$tmp_out" "Refusing directory input" \
            "bounded log window helper refuses directory input"
    fi
else
    fail "bounded log window helper exists"
fi

assert_contains "$verification_skill" "Evidence Used|Not Loaded|Next Evidence|prompt hygiene" \
    "verification gate reports prompt hygiene evidence boundary when relevant"

assert_not_contains "hooks/session-start" "full content of your 'aegis:using-aegis' skill" \
    "Claude/Cursor/Copilot bootstrap does not advertise full skill injection"
assert_not_contains ".opencode/plugins/aegis.js" "full content|ALREADY LOADED" \
    "OpenCode bootstrap does not advertise full skill injection"
assert_not_contains "docs/README.opencode.md" "experimental\\.chat\\.system\\.transform" \
    "OpenCode docs describe current messages transform hook"
assert_contains "docs/testing.md" "Do not run broad searches over" \
    "testing docs warn against broad transcript/log searches"

if (( failures > 0 )); then
    echo ""
    echo "Context budget check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Context budget check passed."
