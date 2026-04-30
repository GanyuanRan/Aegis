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
