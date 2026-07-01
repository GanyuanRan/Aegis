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

echo "=== ZCode Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
zcode_guide="docs/README.zcode.md"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

assert_contains "$matrix" "\`ZCode\`" \
    "compatibility matrix lists ZCode"
assert_contains "$matrix" "ZCode.*no current release-level fresh smoke verdict|ZCode.*no current fresh release verdict" \
    "compatibility matrix keeps ZCode out of fresh closeout"
assert_contains "$matrix" "ZCode.*\\.claude-plugin/marketplace\\.json|\\.claude-plugin/marketplace\\.json.*ZCode" \
    "compatibility matrix records ZCode Claude-Code-compatible plugin contract"
assert_contains "$matrix" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "compatibility matrix records ZCode direct-child skill-directory shape"

assert_contains "$known_limits" "ZCode Structural Support" \
    "known limitations records ZCode structural support boundary"
assert_contains "$known_limits" "not release-level fresh smoke verdict" \
    "known limitations avoids live smoke claim"
assert_contains "$known_limits" "\.claude-plugin/marketplace\.json" \
    "known limitations records ZCode plugin marketplace evidence"
assert_contains "$known_limits" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "known limitations records ZCode direct skill-directory path"

assert_contains "$release_checklist" "docs/README.zcode.md" \
    "release checklist includes ZCode host guide"
assert_contains "$prompt_hygiene" "ZCode" \
    "prompt hygiene covers ZCode"
assert_contains "$current_readme" "docs/README.zcode.md" \
    "current authority map includes ZCode guide"

assert_contains "$root_readme" "\`ZCode\`" \
    "English README lists ZCode"
assert_contains "$zh_readme" "\`ZCode\`" \
    "Chinese README lists ZCode"
assert_contains "$root_readme" "docs/README.zcode.md" \
    "English README links ZCode guide"
assert_contains "$zh_readme" "docs/README.zcode.md" \
    "Chinese README links ZCode guide"

if [[ -f "$zcode_guide" ]]; then
    pass "ZCode host guide exists"
else
    fail "ZCode host guide exists"
fi

assert_contains "$zcode_guide" "https://zcode.z.ai/cn/docs/plugin" \
    "ZCode guide cites official plugin docs"
assert_contains "$zcode_guide" "/plugin marketplace add GanyuanRan/Aegis" \
    "ZCode guide documents install command"
assert_contains "$zcode_guide" "aegis@aegis-dev" \
    "ZCode guide documents marketplace plugin install"
assert_contains "$zcode_guide" "\.claude-plugin/marketplace\.json" \
    "ZCode guide records Claude-Code-compatible plugin contract"
assert_contains "$zcode_guide" "not claim current release-level live smoke evidence|fresh host smoke evidence" \
    "ZCode guide avoids live smoke claim"
assert_contains "$zcode_guide" "aegis-doctor\\.py --write-config --json" \
    "ZCode guide includes complete-install doctor"
assert_contains "$zcode_guide" "GateDecision|completion authority" \
    "ZCode guide preserves authority boundary"
assert_contains "$zcode_guide" "AGENTS.md" \
    "ZCode guide documents AGENTS.md guidance surface"
assert_contains "$zcode_guide" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "ZCode guide documents direct skill-directory discovery shape"
assert_contains "$zcode_guide" "--discovery-root" \
    "ZCode guide includes skill discovery verification"
assert_contains "$zcode_guide" "defaults.*direct-child|direct-child.*default" \
    "ZCode guide records default direct-child updater discovery shape"
assert_contains "$zcode_guide" "mklink /J|ln -sfn" \
    "ZCode guide documents direct-child symlink/junction install shape"
assert_contains "$zcode_guide" "umbrella" \
    "ZCode guide warns against the umbrella symlink pitfall"

assert_contains "$install_check" "docs/README.zcode.md" \
    "install verification policy includes ZCode guide"
assert_contains "$goal_check" "docs/README.zcode.md" \
    "goal-framing policy includes ZCode guide"
assert_contains "$activation_check" "docs/README.zcode.md" \
    "activation-mode policy includes ZCode guide"

if (( failures > 0 )); then
    echo ""
    echo "ZCode host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "ZCode host boundary check passed."
