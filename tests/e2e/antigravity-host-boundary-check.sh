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
testing_doc="docs/testing.md"

assert_contains "$matrix" "\`Antigravity CLI\`" \
    "compatibility matrix lists Antigravity CLI"
assert_contains "$matrix" "\`Antigravity IDE\`" \
    "compatibility matrix lists Antigravity IDE"
assert_contains "$matrix" "\`Antigravity App\`" \
    "compatibility matrix lists Antigravity App"
assert_contains "$matrix" "plugin discovery.*skills.*agents|skills.*agents.*plugin discovery" \
    "compatibility matrix records Antigravity CLI plugin discovery evidence"
assert_contains "$matrix" "Active closeout target|active closeout target" \
    "compatibility matrix marks Antigravity CLI as the active closeout target"
assert_contains "$matrix" "\`Gemini CLI\`.*[Rr]etired|[Rr]etired.*\`Gemini CLI\`" \
    "compatibility matrix marks Gemini CLI as retired"
assert_contains "$matrix" "unsupported by Aegis" \
    "compatibility matrix removes the Gemini CLI support promise"
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
    "known limitations records Gemini CLI retirement boundary"
assert_contains "$known_limits" "Support Is Retired|support is retired" \
    "known limitations labels Gemini CLI support as retired"
assert_contains "$known_limits" "Antigravity CLI|Antigravity IDE|Antigravity App" \
    "known limitations records Antigravity structural support boundary"
assert_contains "$known_limits" "active closeout target" \
    "known limitations marks Antigravity CLI as the active closeout target"
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
assert_contains "$testing_doc" "tests/antigravity/run-tests\\.sh" \
    "testing docs include the Antigravity suite"
assert_contains "$testing_doc" "agy --version" \
    "testing docs include the Antigravity CLI runnable probe"
assert_contains "$testing_doc" "agy plugin list" \
    "testing docs include the Antigravity plugin surface probe"

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
assert_contains "$antigravity_guide" "active closeout target" \
    "Antigravity guide marks Antigravity CLI as the active closeout target"
assert_contains "$antigravity_guide" "\bagy\b" \
    "Antigravity guide records the agy executable surface"
assert_contains "$antigravity_guide" "agy plugin list" \
    "Antigravity guide records the plugin list command"
assert_contains "$antigravity_guide" "agy plugin install /path/to/local/plugin" \
    "Antigravity guide records the local plugin install command"
assert_contains "$antigravity_guide" "agy plugin import gemini" \
    "Antigravity guide records the Gemini migration import command"
assert_contains "$antigravity_guide" "discovery for skills and agents" \
    "Antigravity guide records CLI plugin discovery evidence"
assert_contains "$antigravity_guide" "release-level live smoke evidence|release-level live smoke|fresh host smoke" \
    "Antigravity guide avoids claiming unverified live smoke"
assert_contains "$antigravity_guide" "retired its Gemini CLI support surface" \
    "Antigravity guide records the Aegis Gemini CLI retirement"
assert_contains "$antigravity_tools" "no longer ships or verifies a Gemini CLI adapter" \
    "Antigravity tool mapping records the retired Gemini boundary"
assert_contains "$antigravity_tools" "plugin discovery.*skills.*agents|skills.*agents.*plugin discovery" \
    "Antigravity tool mapping records CLI plugin discovery evidence"
assert_not_contains "$prompt_hygiene" "Gemini CLI" \
    "prompt hygiene no longer lists retired Gemini CLI as a supported host"

for retired_path in GEMINI.md gemini-extension.json skills/using-aegis/references/gemini-tools.md; do
    if [[ -e "$retired_path" ]]; then
        fail "retired Gemini surface is absent: $retired_path"
    else
        pass "retired Gemini surface is absent: $retired_path"
    fi
done

if (( failures > 0 )); then
    echo ""
    echo "Antigravity host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Antigravity host boundary check passed."
