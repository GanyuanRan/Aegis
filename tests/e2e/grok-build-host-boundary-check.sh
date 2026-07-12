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

echo "=== Grok Build Host Boundary Check ==="

guide="docs/README.grok-build.md"
matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
testing_doc="docs/testing.md"
layer1="tests/e2e/layer1-fast-check.sh"
updater="scripts/aegis-update.py"
updater_tests="tests/helpers/test_aegis_update.py"

assert_contains "$guide" '\$GROK_HOME/skills|~/.grok/skills' \
    "Grok guide documents the native user skill root"
assert_contains "$guide" '\[skills\]' \
    "Grok guide includes a skills config example"
assert_contains "$guide" 'paths = \[' \
    "Grok guide shows the extra skill paths setting"
assert_contains "$guide" 'grok inspect --json' \
    "Grok guide uses host-native discovery inspection"
assert_contains "$guide" 'aegis-update\.py register.*|--host grok-build' \
    "Grok guide registers host-scoped Aegis updates"
assert_contains "$guide" 'direct-child' \
    "Grok guide records the direct-child discovery shape"
assert_contains "$guide" 'duplicate|one canonical|do not.*same time' \
    "Grok guide prevents duplicate Aegis exposure"
assert_contains "$guide" 'workspaceSupport.*available' \
    "Grok guide preserves complete-install workspace verification"
assert_contains "$guide" 'method pack|method-pack' \
    "Grok guide preserves the method-pack boundary"
assert_not_contains "$guide" 'authoritative GateDecision|final completion authority is provided by Aegis' \
    "Grok guide does not elevate Aegis into runtime authority"

assert_contains "$updater" 'GROK_HOST_ALIASES' \
    "updater recognizes Grok host aliases"
assert_contains "$updater" 'GROK_HOME' \
    "updater honors GROK_HOME"
assert_contains "$updater_tests" 'defaults_grok_to_native_direct_child' \
    "updater tests lock Grok native discovery defaults"
assert_contains "$updater_tests" 'legacy_grok_entry_uses_native_default_discovery_root' \
    "updater tests cover legacy Grok registry entries"

assert_contains "$matrix" '`Grok Build`' \
    "compatibility matrix lists Grok Build"
assert_contains "$matrix" 'Grok Build.*no current release-level fresh smoke verdict|Grok Build.*structural' \
    "compatibility matrix keeps Grok outside release-level closeout"
assert_contains "$known_limits" 'Grok Build Structural Support' \
    "known limitations records Grok structural support"
assert_contains "$release_checklist" 'docs/README\.grok-build\.md' \
    "release checklist includes the Grok guide"
assert_contains "$current_readme" 'docs/README\.grok-build\.md' \
    "current authority map includes the Grok guide"
assert_contains "$root_readme" 'Grok Build.*README\.grok-build\.md' \
    "root README links the Grok guide"
assert_contains "$zh_readme" 'Grok Build.*README\.grok-build\.md' \
    "Chinese README links the Grok guide"
assert_contains "$testing_doc" 'grok-build-host-boundary-check\.sh' \
    "testing docs name the Grok boundary check"
assert_contains "$layer1" 'grok-build-host-boundary-check\.sh' \
    "Layer 1 runs the Grok boundary check"

if (( failures > 0 )); then
    echo ""
    echo "Grok Build host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Grok Build host boundary check passed."
