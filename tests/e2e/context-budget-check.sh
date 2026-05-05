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

echo "=== Context Budget Check ==="

using_aegis="skills/using-aegis/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
prompt_hygiene_doc="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
verification_skill="skills/verification-before-completion/SKILL.md"
log_window_script="scripts/log-window.sh"
max_hot_path_chars=2500

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
    assert_contains "$prompt_hygiene_doc" "不是污染源|not.*pollution source|not.*contamination source" \
        "prompt hygiene distinguishes tools from prompt payload contamination"
    assert_contains "$prompt_hygiene_doc" "完整错误文案.*反复回流|full error text.*reflow|full error text.*repeated" \
        "prompt hygiene prevents repeated full policy warning text from re-entering context"
    assert_contains "$prompt_hygiene_doc" "Host Context Intake Discipline" \
        "prompt hygiene defines host context intake discipline"
    assert_contains "$prompt_hygiene_doc" "bounded evidence intake" \
        "prompt hygiene names bounded evidence intake as the stable owner"
    assert_contains "$prompt_hygiene_doc" "index.*window.*excerpt|索引.*窗口.*摘录" \
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
