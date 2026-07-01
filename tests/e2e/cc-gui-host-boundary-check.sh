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

echo "=== CC GUI Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
cc_gui_guide="docs/README.cc-gui.md"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

assert_contains "$matrix" "\`CC GUI" \
    "compatibility matrix lists CC GUI"
assert_contains "$matrix" "CC GUI.*no current release-level fresh smoke verdict|CC GUI.*no current fresh release verdict" \
    "compatibility matrix keeps CC GUI out of fresh closeout"
assert_contains "$matrix" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "compatibility matrix records direct Codex skill-directory shape"
assert_contains "$matrix" "JetBrains|IDEA" \
    "compatibility matrix records JetBrains IDEA host layer"

assert_contains "$known_limits" "CC GUI Structural Support" \
    "known limitations records CC GUI structural support boundary"
assert_contains "$known_limits" "not release-level fresh[[:space:]]+smoke verdict" \
    "known limitations avoids CC GUI live smoke claim"
assert_contains "$known_limits" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "known limitations records direct skill-directory path"
assert_contains "$known_limits" "Tool: exec_command|host adapter event normalization" \
    "known limitations keeps tool-event rendering at host adapter boundary"

assert_contains "$release_checklist" "docs/README.cc-gui.md" \
    "release checklist includes CC GUI host guide"
assert_contains "$release_checklist" "CC GUI" \
    "release checklist tracks CC GUI host status"
assert_contains "$prompt_hygiene" "CC GUI" \
    "prompt hygiene covers CC GUI"
assert_contains "$current_readme" "docs/README.cc-gui.md" \
    "current authority map includes CC GUI guide"

assert_contains "$root_readme" "\`CC GUI" \
    "English README lists CC GUI"
assert_contains "$root_readme" "docs/README.cc-gui.md" \
    "English README links CC GUI guide"
assert_contains "$zh_readme" "\`CC GUI" \
    "Chinese README lists CC GUI"
assert_contains "$zh_readme" "docs/README.cc-gui.md" \
    "Chinese README links CC GUI guide"

if [[ -f "$cc_gui_guide" ]]; then
    pass "CC GUI host guide exists"
else
    fail "CC GUI host guide exists"
fi

assert_contains "$cc_gui_guide" "https://github.com/zhukunpenglinyutong/jetbrains-cc-gui" \
    "CC GUI guide cites source repository"
assert_contains "$cc_gui_guide" "plugins.jetbrains.com/plugin/29342-cc-gui-claude-or-codex-" \
    "CC GUI guide cites JetBrains plugin page"
assert_contains "$cc_gui_guide" "Claude Code.*OpenAI Codex|OpenAI Codex.*Claude Code" \
    "CC GUI guide records wrapped provider scope"
assert_contains "$cc_gui_guide" "\.agents/skills/<skill-name>/SKILL\.md|~/.agents/skills/<skill-name>/SKILL\.md" \
    "CC GUI guide documents direct Codex skill-directory shape"
assert_contains "$cc_gui_guide" "mklink /J|Copy-Item" \
    "CC GUI guide includes Windows installation shape"
assert_contains "$cc_gui_guide" "aegis-doctor\\.py --write-config --json" \
    "CC GUI guide includes complete-install doctor"
assert_contains "$cc_gui_guide" "--discovery-root" \
    "CC GUI guide includes skill discovery verification"
assert_contains "$cc_gui_guide" "--discovery-shape direct-child" \
    "CC GUI guide records direct-child updater discovery shape"
assert_contains "$cc_gui_guide" "Tool: exec_command" \
    "CC GUI guide documents tool-event rendering boundary"
assert_contains "$cc_gui_guide" "AEGIS_ACTIVATION_MODE=explicit" \
    "CC GUI guide documents explicit activation caveat"
assert_contains "$cc_gui_guide" "does not override CC GUI|does not override Codex|does not override Claude" \
    "CC GUI guide clarifies activation mode does not control native matcher"
assert_contains "$cc_gui_guide" "GateDecision|completion authority" \
    "CC GUI guide preserves authority boundary"
assert_contains "$cc_gui_guide" "does \\*\\*not\\*\\* claim current release-level live smoke evidence|does not claim current release-level live smoke evidence|fresh smoke pending" \
    "CC GUI guide avoids live smoke claim"
assert_not_contains "$cc_gui_guide" "authoritative.*GateDecision|final completion authority" \
    "CC GUI guide does not elevate Aegis to runtime authority"

assert_contains "$install_check" "docs/README.cc-gui.md" \
    "install verification policy includes CC GUI guide"
assert_contains "$goal_check" "docs/README.cc-gui.md" \
    "goal-framing policy includes CC GUI guide"
assert_contains "$activation_check" "docs/README.cc-gui.md" \
    "activation-mode policy includes CC GUI guide"

if (( failures > 0 )); then
    echo ""
    echo "CC GUI host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "CC GUI host boundary check passed."
