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

    if grep -qE -- "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE -- "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== Antigravity Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
skill_discipline="skills/using-aegis/references/skill-discipline.md"
antigravity_guide="docs/README.antigravity.md"
antigravity_tools="skills/using-aegis/references/antigravity-tools.md"
install_check="tests/e2e/install-verification-policy-check.sh"

assert_contains "$matrix" "\`Antigravity CLI\`" \
    "compatibility matrix lists Antigravity CLI"
assert_contains "$matrix" "\`Antigravity IDE\`" \
    "compatibility matrix lists Antigravity IDE"
assert_contains "$matrix" "\`Antigravity App\`" \
    "compatibility matrix lists Antigravity App"
assert_contains "$matrix" "plugin discovery.*skills.*agents|skills.*agents.*plugin discovery" \
    "compatibility matrix records Antigravity CLI plugin discovery evidence"
assert_contains "$matrix" "\`Gemini CLI\`.*[Tt]ransitional|[Tt]ransitional.*\`Gemini CLI\`" \
    "compatibility matrix marks Gemini CLI as transitional"
assert_not_contains "$matrix" "\`Gemini CLI\`.*retir(ed|ing)?|retir(ed|ing)?.*\`Gemini CLI\`" \
    "compatibility matrix does not mark Gemini CLI as retired or retiring"
assert_contains "$matrix" "2026-05-19" \
    "compatibility matrix records Google transition announcement date"
assert_contains "$matrix" "2026-06-18" \
    "compatibility matrix records consumer service stop date"
assert_contains "$matrix" "Google AI Pro|Ultra|Gemini Code Assist for individuals" \
    "compatibility matrix records consumer-surface scope"
assert_contains "$matrix" "Standard|Enterprise|paid.*API key|API key.*paid" \
    "compatibility matrix preserves enterprise or paid API key exception"
assert_not_contains "$matrix" "\`Gemini CLI\` \| No current fresh release-level verdict" \
    "compatibility matrix no longer treats Gemini CLI as ordinary pending host"

assert_contains "$known_limits" "Gemini CLI" \
    "known limitations records Gemini CLI transition boundary"
assert_contains "$known_limits" "Transitional Compatibility|transitional compatibility" \
    "known limitations labels the Gemini CLI surface as transitional compatibility"
assert_contains "$known_limits" "Antigravity CLI|Antigravity IDE|Antigravity App" \
    "known limitations records Antigravity structural support boundary"
assert_contains "$known_limits" "plugin discovery.*skills.*agents|skills.*agents.*plugin discovery" \
    "known limitations records Antigravity CLI plugin discovery evidence"
assert_contains "$prompt_hygiene" "Antigravity CLI|Antigravity IDE|Antigravity App" \
    "prompt hygiene covers Antigravity host surfaces"
assert_contains "$release_checklist" "docs/README.antigravity.md" \
    "release checklist includes Antigravity host guide"
assert_contains "$root_readme" "Antigravity CLI|Antigravity IDE|Antigravity App" \
    "English README lists Antigravity host surfaces"
assert_contains "$zh_readme" "Antigravity CLI|Antigravity IDE|Antigravity App" \
    "Chinese README lists Antigravity host surfaces"
assert_contains "$skill_discipline" "references/antigravity-tools.md" \
    "skill discipline links Antigravity tool mapping"
assert_contains "$install_check" "docs/README.antigravity.md" \
    "install verification policy includes Antigravity host guide"

if [[ -f "$antigravity_guide" ]]; then
    pass "Antigravity host guide exists"
else
    fail "Antigravity host guide exists"
fi

if [[ -f "$antigravity_tools" ]]; then
    pass "Antigravity tool mapping exists"
else
    fail "Antigravity tool mapping exists"
fi

assert_contains "$antigravity_guide" "https://github.com/google-antigravity/antigravity-cli" \
    "Antigravity guide cites official CLI repository"
assert_contains "$antigravity_guide" "discovery for skills and agents" \
    "Antigravity guide records CLI plugin discovery evidence"
assert_contains "$antigravity_guide" "release-level live smoke evidence|release-level live smoke|fresh host smoke" \
    "Antigravity guide avoids claiming unverified live smoke"
assert_not_contains "$antigravity_guide" "legacy Gemini CLI|retire Gemini CLI|retiring compatibility|legacy / retiring" \
    "Antigravity guide keeps Gemini CLI transitional rather than legacy or retired"
assert_contains "$antigravity_tools" "transitional compatibility" \
    "Antigravity tool mapping records transitional Gemini boundary"
assert_contains "$antigravity_tools" "plugin discovery.*skills.*agents|skills.*agents.*plugin discovery" \
    "Antigravity tool mapping records CLI plugin discovery evidence"
assert_not_contains "$antigravity_tools" "legacy Gemini CLI|retire Gemini CLI|retiring compatibility|legacy / retiring" \
    "Antigravity tool mapping does not retire Gemini CLI"
assert_not_contains "$prompt_hygiene" "legacy Gemini CLI|retire Gemini CLI|retiring compatibility|legacy / retiring" \
    "prompt hygiene keeps Gemini CLI transitional rather than legacy or retired"

if (( failures > 0 )); then
    echo ""
    echo "Antigravity host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Antigravity host boundary check passed."
