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

warn() {
    echo "  [WARN] $1"
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

byte_count() {
    wc -c < "$1" | tr -d '[:space:]'
}

budget_band() {
    local current="$1"
    local target="$2"
    local hard="$3"

    if (( current <= target )); then
        echo "target"
    elif (( current <= hard )); then
        echo "warning"
    else
        echo "hard-failure"
    fi
}

assert_budget() {
    local file="$1"
    local target="$2"
    local hard="$3"
    local label="$4"

    if [[ ! -f "$file" ]]; then
        fail "$label exists"
        return
    fi

    local current
    current="$(byte_count "$file")"
    case "$(budget_band "$current" "$target" "$hard")" in
        target) pass "$label meets target <= ${target} bytes (${current})" ;;
        warning) warn "$label exceeds target ${target} but remains within hard ceiling ${hard} bytes (${current})" ;;
        hard-failure) fail "$label exceeds hard ceiling ${hard} bytes (${current})" ;;
    esac
}

assert_total_budget() {
    local current="$1"
    local target="$2"
    local hard="$3"
    local label="$4"

    case "$(budget_band "$current" "$target" "$hard")" in
        target) pass "$label meets target <= ${target} bytes (${current})" ;;
        warning) warn "$label exceeds target ${target} but remains within hard ceiling ${hard} bytes (${current})" ;;
        hard-failure) fail "$label exceeds hard ceiling ${hard} bytes (${current})" ;;
    esac
}

echo "=== Context Budget Check ==="

if [[ "$(budget_band 100 100 120)" == "target" && \
      "$(budget_band 101 100 120)" == "warning" && \
      "$(budget_band 121 100 120)" == "hard-failure" ]]; then
    pass "budget bands distinguish target, warning, and hard failure"
else
    fail "budget bands distinguish target, warning, and hard failure"
fi

using_aegis="skills/using-aegis/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
prompt_hygiene_doc="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
verification_skill="skills/verification-before-completion/SKILL.md"
workflow_quality_doc="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
log_window_script="scripts/log-window.sh"
using_target_bytes=2800
using_hard_bytes=3200
debugging_target_bytes=10500
debugging_hard_bytes=12000
verification_target_bytes=7500
verification_hard_bytes=9000
executing_target_bytes=9000
executing_hard_bytes=10500
long_task_target_bytes=12500
long_task_hard_bytes=14000

assert_budget "$using_aegis" "$using_target_bytes" "$using_hard_bytes" \
    "using-aegis hot path"

debugging_skill="skills/systematic-debugging/SKILL.md"
debugging_advanced="skills/systematic-debugging/advanced-debugging-governance.md"
if [[ -f "$debugging_skill" && -f "$debugging_advanced" ]]; then
    assert_budget "$debugging_skill" "$debugging_target_bytes" \
        "$debugging_hard_bytes" "systematic-debugging main body"
    pass "systematic-debugging main and advanced owner both exist"
elif [[ -f "$debugging_skill" || -f "$debugging_advanced" ]]; then
    fail "systematic-debugging extraction rejects partial main/reference state"
else
    fail "systematic-debugging main and advanced owner exist"
fi

verification_expanded="skills/verification-before-completion/expanded-closeout.md"
if [[ -f "$verification_skill" && -f "$verification_expanded" ]]; then
    assert_budget "$verification_skill" "$verification_target_bytes" \
        "$verification_hard_bytes" "verification main body"
    pass "verification main and expanded owner both exist"
elif [[ -f "$verification_skill" || -f "$verification_expanded" ]]; then
    fail "verification extraction rejects partial main/reference state"
else
    fail "verification main and expanded owner exist"
fi

if [[ -f "$debugging_skill" && -f "$debugging_advanced" && -f "$verification_skill" && -f "$verification_expanded" ]]; then
    debugging_bytes="$(byte_count "$debugging_skill")"
    verification_bytes="$(byte_count "$verification_skill")"
    combined_bytes=$((debugging_bytes + verification_bytes))
    assert_total_budget "$combined_bytes" 19000 22000 \
        "combined debugging and verification main bodies"
else
    fail "combined main-body ceiling requires complete debugging/verification owners"
fi

executing_skill="skills/executing-plans/SKILL.md"
long_task_skill="skills/long-task-continuation/SKILL.md"
assert_budget "$executing_skill" "$executing_target_bytes" \
    "$executing_hard_bytes" "executing-plans main body"
assert_budget "$long_task_skill" "$long_task_target_bytes" \
    "$long_task_hard_bytes" "long-task-continuation main body"

if [[ -f "$using_aegis" && -f "$debugging_skill" && -f "$debugging_advanced" && \
      -f "$verification_skill" && -f "$verification_expanded" ]]; then
    using_bytes="$(byte_count "$using_aegis")"
    assert_total_budget "$((using_bytes + debugging_bytes + verification_bytes))" \
        22000 26000 "debug route bundle"
else
    fail "debug route bundle requires complete owners"
fi

if [[ -f "$using_aegis" && -f "$executing_skill" && -f "$verification_skill" && \
      -f "$verification_expanded" ]]; then
    using_bytes="$(byte_count "$using_aegis")"
    executing_bytes="$(byte_count "$executing_skill")"
    assert_total_budget "$((using_bytes + executing_bytes + verification_bytes))" \
        20000 24000 "plan-execution route bundle"
else
    fail "plan-execution route bundle requires complete owners"
fi

if [[ -f "$using_aegis" && -f "$executing_skill" && -f "$long_task_skill" && \
      -f "$verification_skill" && -f "$verification_expanded" ]]; then
    long_task_bytes="$(byte_count "$long_task_skill")"
    assert_total_budget "$((using_bytes + executing_bytes + long_task_bytes + verification_bytes))" \
        33000 40000 "long-task route bundle"
else
    fail "long-task route bundle requires complete owners"
fi

assert_contains "$workflow_quality_doc" "warning target" \
    "workflow quality baseline defines warning targets"
assert_contains "$workflow_quality_doc" "hard ceiling" \
    "workflow quality baseline defines hard ceilings"
assert_contains "$workflow_quality_doc" "route-bundle budgets" \
    "workflow quality baseline defines route-bundle budgets"

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
