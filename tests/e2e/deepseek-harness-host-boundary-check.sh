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

echo "=== DeepSeek Harness Host Boundary Check ==="

guide="docs/README.deepseek-harness.md"
tui_guide="docs/README.deepseek-tui.md"
matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
fast_track="docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md"
fast_track_zh="docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md"
testing_doc="docs/testing.md"
layer1="tests/e2e/layer1-fast-check.sh"
updater="scripts/aegis-update.py"
updater_tests="tests/helpers/test_aegis_update.py"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

assert_contains "$guide" 'deepseek-ai/deepseek-harness' \
    "Harness guide cites the official DeepSeek repository"
assert_contains "$guide" 'separate hosts|does not replace.*deepseek-tui' \
    "Harness guide stays distinct from DeepSeek-TUI"
assert_contains "$tui_guide" 'Hmbown/DeepSeek-TUI' \
    "DeepSeek-TUI guide retains its separate host reference"
assert_contains "$guide" '\$DSH_HOME/skills|~/.dsh/skills' \
    "Harness guide documents the native user skill root"
assert_contains "$guide" '<project>/.dsh/skills|\.dsh/skills' \
    "Harness guide documents the project skill root"
assert_contains "$guide" 'direct-child' \
    "Harness guide records the direct-child discovery shape"
assert_contains "$guide" '--host deepseek-harness' \
    "Harness guide registers the host-scoped updater"
assert_contains "$guide" 'duplicate|exactly one|Do not also|Do not mix' \
    "Harness guide prevents duplicate Aegis exposure"
assert_contains "$guide" 'workspaceSupport.*available' \
    "Harness guide preserves complete-install workspace verification"
assert_contains "$guide" 'developer preview|developer-preview' \
    "Harness guide records the developer-preview boundary"
assert_contains "$guide" 'method pack|method-pack' \
    "Harness guide preserves the method-pack boundary"
assert_not_contains "$guide" 'authoritative GateDecision|final completion authority is provided by Aegis' \
    "Harness guide does not elevate Aegis into runtime authority"

assert_contains "$updater" 'DEEPSEEK_HARNESS_HOST_ALIASES' \
    "updater recognizes DeepSeek Harness host aliases"
assert_contains "$updater" 'DSH_HOME' \
    "updater honors DSH_HOME"
assert_contains "$updater_tests" 'defaults_deepseek_harness_to_native_direct_child' \
    "updater tests lock native Harness discovery defaults"
assert_contains "$updater_tests" 'legacy_deepseek_harness_entry_uses_native_default_discovery_root' \
    "updater tests cover legacy Harness registry entries"

assert_contains "$matrix" '`DeepSeek Harness`' \
    "compatibility matrix lists DeepSeek Harness"
assert_contains "$matrix" 'DeepSeek Harness.*no current release-level fresh smoke verdict|DeepSeek Harness.*structural' \
    "compatibility matrix keeps Harness outside release-level closeout"
assert_contains "$known_limits" 'DeepSeek Harness Structural Support' \
    "known limitations records Harness structural support"
assert_contains "$release_checklist" 'docs/README\.deepseek-harness\.md' \
    "release checklist includes the Harness guide"
assert_contains "$current_readme" 'docs/README\.deepseek-harness\.md' \
    "current authority map includes the Harness guide"
assert_contains "$root_readme" 'DeepSeek Harness.*README\.deepseek-harness\.md' \
    "root README links the Harness guide"
assert_contains "$zh_readme" 'DeepSeek Harness.*README\.deepseek-harness\.md' \
    "Chinese README links the Harness guide"
assert_contains "$fast_track" 'DeepSeek Harness.*README\.deepseek-harness\.md' \
    "Fast-Track Playbook links the Harness guide"
assert_contains "$fast_track_zh" 'DeepSeek Harness.*README\.deepseek-harness\.md' \
    "Chinese Fast-Track Playbook links the Harness guide"
assert_contains "$testing_doc" 'deepseek-harness-host-boundary-check\.sh' \
    "testing docs name the Harness boundary check"
assert_contains "$layer1" 'deepseek-harness-host-boundary-check\.sh' \
    "Layer 1 runs the Harness boundary check"
assert_contains "$install_check" 'docs/README\.deepseek-harness\.md' \
    "install verification policy includes the Harness guide"
assert_contains "$goal_check" 'docs/README\.deepseek-harness\.md' \
    "goal-framing policy includes the Harness guide"
assert_contains "$activation_check" 'docs/README\.deepseek-harness\.md' \
    "activation-mode policy includes the Harness guide"

if (( failures > 0 )); then
    echo ""
    echo "DeepSeek Harness host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "DeepSeek Harness host boundary check passed."
