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

echo "=== Kimi Code CLI Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
kimi_guide="docs/README.kimi-code.md"
kimi_manifest="kimi.plugin.json"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"
fast_track="docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md"
fast_track_zh="docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md"
trigger_health="docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md"
update_skill="skills/update-aegis/SKILL.md"
updater="scripts/aegis-update.py"
updater_tests="tests/helpers/test_aegis_update.py"

assert_contains "$matrix" "\`Kimi Code CLI\`" \
    "compatibility matrix lists Kimi Code CLI"
assert_contains "$matrix" "Kimi Code CLI.*no current release-level fresh smoke verdict|Kimi Code CLI.*no current fresh release verdict" \
    "compatibility matrix keeps Kimi out of fresh closeout"
assert_contains "$matrix" '\$KIMI_CODE_HOME/skills/|~/.kimi-code/skills/' \
    "compatibility matrix records Kimi explicit compatibility root"
assert_contains "$matrix" 'kimi\.plugin\.json|sessionStart\.skill|sessionStart' \
    "compatibility matrix records Kimi automatic plugin bootstrap"
assert_contains "$matrix" "~/.agents/skills/" \
    "compatibility matrix retains Kimi shared fallback root"
assert_not_contains "$matrix" "Kimi Code CLI.*reuses the Codex path|Aegis Codex installation is Kimi installation" \
    "compatibility matrix retires Codex-path Kimi claim"

assert_contains "$known_limits" "Kimi Code CLI Structural Support" \
    "known limitations records Kimi structural support boundary"
assert_contains "$known_limits" "not a release-level fresh smoke verdict|not release-level fresh smoke verdict" \
    "known limitations avoids Kimi live smoke claim"
assert_contains "$known_limits" '\$KIMI_CODE_HOME/skills/|~/.kimi-code/skills/' \
    "known limitations records Kimi explicit compatibility root"
assert_contains "$known_limits" 'Kimi-managed plugin' \
    "known limitations records Kimi plugin automatic path"
assert_contains "$known_limits" 'sessionStart\.skill' \
    "known limitations records Kimi session-start entry"
assert_contains "$known_limits" "~/.agents/skills/" \
    "known limitations retains official fallback"
assert_contains "$known_limits" "Codex umbrella symlink" \
    "known limitations names retired Codex umbrella path"

assert_contains "$release_checklist" "docs/README.kimi-code.md" \
    "release checklist includes Kimi host guide"
assert_contains "$release_checklist" '\$KIMI_CODE_HOME/skills/|~/.kimi-code/skills/' \
    "release checklist guards Kimi explicit compatibility root"
assert_contains "$release_checklist" 'Kimi.*plugin|plugin.*Kimi' \
    "release checklist guards Kimi plugin default"
assert_contains "$current_readme" "docs/README.kimi-code.md" \
    "current authority map includes Kimi guide"

assert_contains "$root_readme" "\`Kimi Code CLI\`" \
    "English README lists Kimi Code CLI"
assert_contains "$zh_readme" "\`Kimi Code CLI\`" \
    "Chinese README lists Kimi Code CLI"
assert_contains "$root_readme" "docs/README.kimi-code.md" \
    "English README links Kimi guide"
assert_contains "$zh_readme" "docs/README.kimi-code.md" \
    "Chinese README links Kimi guide"

if [[ -f "$kimi_guide" ]]; then
    pass "Kimi Code CLI host guide exists"
else
    fail "Kimi Code CLI host guide exists"
fi

assert_contains "$kimi_guide" "https://moonshotai.github.io/kimi-code/en/customization/skills" \
    "Kimi guide cites official Agent Skills docs"
assert_contains "$kimi_guide" "https://moonshotai.github.io/kimi-code/en/customization/plugins" \
    "Kimi guide cites official Plugins docs"
assert_contains "$kimi_guide" "https://moonshotai.github.io/kimi-code/en/configuration/config-files.html" \
    "Kimi guide cites official config docs"
assert_contains "$kimi_guide" '\$KIMI_CODE_HOME/skills/|~/.kimi-code/skills/' \
    "Kimi guide documents native user skill root"
assert_contains "$kimi_guide" "~/.agents/skills/" \
    "Kimi guide documents shared fallback root"
assert_contains "$kimi_guide" "Codex umbrella" \
    "Kimi guide warns against Codex umbrella main path"
assert_contains "$kimi_guide" "--host kimi-code" \
    "Kimi guide documents updater host id"
assert_contains "$kimi_guide" "direct-child" \
    "Kimi guide documents explicit direct-child compatibility shape"
assert_contains "$kimi_guide" "/plugins install https://github\.com/GanyuanRan/Aegis" \
    "Kimi guide installs automatic mode through native plugin manager"
assert_contains "$kimi_guide" "/plugins info aegis" \
    "Kimi guide verifies managed plugin identity"
assert_contains "$kimi_guide" "/reload|/new" \
    "Kimi guide requires native reload or new session"
assert_contains "$kimi_guide" "--host-profile kimi-code-auto" \
    "Kimi guide uses automatic doctor profile"
assert_contains "$kimi_guide" "Explicit Compatibility Installation" \
    "Kimi guide names explicit compatibility installation"
assert_contains "$kimi_guide" "aegis-doctor\\.py --write-config --json" \
    "Kimi guide includes complete-install doctor"
assert_contains "$kimi_guide" "--discovery-root" \
    "Kimi guide includes skill discovery verification"
assert_contains "$kimi_guide" "target project directory" \
    "Kimi guide warns not to run doctor from target project"
assert_contains "$kimi_guide" "AEGIS_ACTIVATION_MODE=explicit|activation-mode explicit" \
    "Kimi guide documents explicit activation caveat"
assert_contains "$kimi_guide" "does not override Kimi Code CLI" \
    "Kimi guide clarifies activation mode does not control native matcher"
assert_contains "$kimi_guide" "GateDecision|completion authority" \
    "Kimi guide preserves authority boundary"
assert_contains "$kimi_guide" "does not claim current|not claim current" \
    "Kimi guide avoids live smoke claim"

if [[ -f "$kimi_manifest" ]]; then
    pass "Kimi plugin manifest exists"
else
    fail "Kimi plugin manifest exists"
fi
assert_contains "$kimi_manifest" '"name": "aegis"' \
    "Kimi plugin manifest uses stable plugin id"
assert_contains "$kimi_manifest" '"skills": "\./skills/"' \
    "Kimi plugin manifest reuses canonical skills tree"
assert_contains "$kimi_manifest" '"skill": "using-aegis"' \
    "Kimi plugin manifest establishes session-start router entry"

assert_contains "$updater" "KIMI_HOST_ALIASES" \
    "updater recognizes Kimi host aliases"
assert_contains "$updater" "default_kimi_discovery_root" \
    "updater owns Kimi default discovery root"
assert_contains "$updater" "should_sync_and_verify_at_register" \
    "updater uses shape-based register-time sync"
assert_contains "$updater_tests" "defaults_kimi_to_native_direct_child" \
    "updater tests Kimi direct-child default"
assert_contains "$updater_tests" "syncs_and_verifies_kimi_installation" \
    "updater tests Kimi register-time sync"

assert_contains "$install_check" "docs/README.kimi-code.md" \
    "install verification policy includes Kimi guide"
assert_contains "$goal_check" "docs/README.kimi-code.md" \
    "goal-framing policy includes Kimi guide"
assert_contains "$activation_check" "docs/README.kimi-code.md" \
    "activation-mode policy includes Kimi guide"

assert_contains "$fast_track" "native activation and automatic-entry checks" \
    "English quick-install prompt requires native activation proof"
assert_contains "$fast_track_zh" "原生活化与自动入口验证" \
    "Chinese quick-install prompt requires native activation proof"
assert_contains "$trigger_health" "Kimi.*hook-bootstrap|hook-bootstrap.*Kimi" \
    "trigger health maps Kimi auto to hook bootstrap"
assert_contains "$trigger_health" "Kimi.*native-direct-skill|native-direct-skill.*Kimi" \
    "trigger health maps Kimi explicit to native direct skill"
assert_contains "$update_skill" "/plugins install https://github\.com/GanyuanRan/Aegis" \
    "update skill routes Kimi auto through plugin manager"
assert_contains "$update_skill" "Explicit Compatibility Installation|explicit compatibility" \
    "update skill retains Kimi explicit updater path"

if (( failures > 0 )); then
    echo ""
    echo "Kimi Code CLI host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Kimi Code CLI host boundary check passed."
