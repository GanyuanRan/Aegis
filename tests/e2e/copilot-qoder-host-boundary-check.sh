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

echo "=== Copilot + Qoder Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
copilot_guide="docs/README.copilot.md"
qoder_guide="docs/README.qoder.md"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

assert_contains "$matrix" "\`GitHub Copilot\`" \
    "compatibility matrix lists GitHub Copilot"
assert_contains "$matrix" "\`Qoder\`" \
    "compatibility matrix lists Qoder"
assert_contains "$matrix" "GitHub Copilot.*no current release-level fresh smoke verdict|GitHub Copilot.*no current fresh release verdict" \
    "compatibility matrix keeps GitHub Copilot out of fresh closeout"
assert_contains "$matrix" "Qoder.*no current release-level fresh smoke verdict|Qoder.*no current fresh release verdict" \
    "compatibility matrix keeps Qoder out of fresh closeout"
assert_contains "$matrix" "\\.github/skills|copilot-instructions\\.md|\\.github/hooks|AGENTS\\.md" \
    "compatibility matrix records Copilot repository surfaces"
assert_contains "$matrix" "~/.qoder/skills/|\\.qoder/skills/|\\.qoder/rules/|AGENTS\\.md" \
    "compatibility matrix records Qoder native surfaces"

assert_contains "$known_limits" "GitHub Copilot Structural Support" \
    "known limitations records GitHub Copilot structural support boundary"
assert_contains "$known_limits" "Qoder Structural Support" \
    "known limitations records Qoder structural support boundary"
assert_contains "$known_limits" "not a release-level fresh smoke verdict|not release-level fresh smoke verdict" \
    "known limitations avoids live smoke claim"

assert_contains "$release_checklist" "docs/README.copilot.md" \
    "release checklist includes GitHub Copilot host guide"
assert_contains "$release_checklist" "docs/README.qoder.md" \
    "release checklist includes Qoder host guide"
assert_contains "$prompt_hygiene" "Copilot" \
    "prompt hygiene covers Copilot"
assert_contains "$current_readme" "docs/README.copilot.md" \
    "current authority map includes Copilot guide"
assert_contains "$current_readme" "docs/README.qoder.md" \
    "current authority map includes Qoder guide"

assert_contains "$root_readme" "\`GitHub Copilot\`" \
    "English README lists GitHub Copilot"
assert_contains "$root_readme" "\`Qoder\`" \
    "English README lists Qoder"
assert_contains "$zh_readme" "\`GitHub Copilot\`" \
    "Chinese README lists GitHub Copilot"
assert_contains "$zh_readme" "\`Qoder\`" \
    "Chinese README lists Qoder"
assert_contains "$root_readme" "docs/README.copilot.md" \
    "English README links Copilot guide"
assert_contains "$root_readme" "docs/README.qoder.md" \
    "English README links Qoder guide"
assert_contains "$zh_readme" "docs/README.copilot.md" \
    "Chinese README links Copilot guide"
assert_contains "$zh_readme" "docs/README.qoder.md" \
    "Chinese README links Qoder guide"

if [[ -f "$copilot_guide" ]]; then
    pass "GitHub Copilot host guide exists"
else
    fail "GitHub Copilot host guide exists"
fi

if [[ -f "$qoder_guide" ]]; then
    pass "Qoder host guide exists"
else
    fail "Qoder host guide exists"
fi

assert_contains "$copilot_guide" "https://docs.github.com/.*/create-skills" \
    "Copilot guide cites official agent skills docs"
assert_contains "$copilot_guide" "https://docs.github.com/.*/use-hooks" \
    "Copilot guide cites official hooks docs"
assert_contains "$copilot_guide" "https://docs.github.com/.*/hooks-reference" \
    "Copilot guide cites hooks reference docs"
assert_contains "$copilot_guide" "copilot-instructions\\.md" \
    "Copilot guide records repository instructions surface"
assert_contains "$copilot_guide" "\\.github/skills/" \
    "Copilot guide documents repository skills path"
assert_contains "$copilot_guide" "\\.github/hooks/\\*\\.json|\\.github/hooks/session-start\\.json" \
    "Copilot guide documents repository hooks path"
assert_contains "$copilot_guide" "AGENTS\\.md" \
    "Copilot guide records AGENTS guidance surface"
assert_contains "$copilot_guide" "aegis-doctor\\.py --write-config --json" \
    "Copilot guide includes complete-install doctor"
assert_contains "$copilot_guide" "--discovery-name-prefix aegis-" \
    "Copilot guide documents prefixed discovery-root doctor verification"
assert_contains "$copilot_guide" "Aegis goal:" \
    "Copilot guide documents portable goal entry"
assert_contains "$copilot_guide" "AEGIS_ACTIVATION_MODE=explicit" \
    "Copilot guide documents explicit activation caveat"
assert_contains "$copilot_guide" "does not override GitHub Copilot|controls only the optional Aegis bootstrap hook output" \
    "Copilot guide clarifies activation mode does not control native matcher"
assert_contains "$copilot_guide" "GateDecision|completion authority" \
    "Copilot guide preserves authority boundary"
assert_contains "$copilot_guide" "does \\*\\*not\\*\\* claim current release-level live smoke evidence|does not claim current release-level live smoke evidence" \
    "Copilot guide avoids live smoke claim"

if [[ -f ".github/hooks/session-start.json" ]]; then
    pass "Copilot repository hook config exists"
else
    fail "Copilot repository hook config exists"
fi

if [[ -f "hooks/copilot-session-start.ps1" ]]; then
    pass "Copilot PowerShell hook wrapper exists"
else
    fail "Copilot PowerShell hook wrapper exists"
fi

assert_contains "$qoder_guide" "https://docs.qoder.com/extensions/subagent" \
    "Qoder guide cites official skills docs"
assert_contains "$qoder_guide" "https://docs.qoder.com/user-guide/rules" \
    "Qoder guide cites official rules docs"
assert_contains "$qoder_guide" "~/.qoder/skills/|\\.qoder/skills/" \
    "Qoder guide documents native skill paths"
assert_contains "$qoder_guide" "\\.qoder/rules/" \
    "Qoder guide documents native rules path"
assert_contains "$qoder_guide" "AGENTS\\.md" \
    "Qoder guide records AGENTS guidance surface"
assert_contains "$qoder_guide" "aegis-doctor\\.py --write-config --json" \
    "Qoder guide includes complete-install doctor"
assert_contains "$qoder_guide" "Aegis goal:" \
    "Qoder guide documents portable goal entry"
assert_contains "$qoder_guide" "AEGIS_ACTIVATION_MODE=explicit" \
    "Qoder guide documents explicit activation caveat"
assert_contains "$qoder_guide" "does not override Qoder" \
    "Qoder guide clarifies activation mode does not control native matcher"
assert_contains "$qoder_guide" "GateDecision|completion authority" \
    "Qoder guide preserves authority boundary"
assert_contains "$qoder_guide" "does \\*\\*not\\*\\* claim current release-level live smoke evidence|does not claim current release-level live smoke evidence" \
    "Qoder guide avoids live smoke claim"

assert_contains "$install_check" "docs/README.copilot.md" \
    "install verification policy includes Copilot guide"
assert_contains "$install_check" "docs/README.qoder.md" \
    "install verification policy includes Qoder guide"
assert_contains "$goal_check" "docs/README.copilot.md" \
    "goal-framing policy includes Copilot guide"
assert_contains "$goal_check" "docs/README.qoder.md" \
    "goal-framing policy includes Qoder guide"
assert_contains "$activation_check" "docs/README.copilot.md" \
    "activation-mode policy includes Copilot guide"
assert_contains "$activation_check" "docs/README.qoder.md" \
    "activation-mode policy includes Qoder guide"

if (( failures > 0 )); then
    echo ""
    echo "Copilot + Qoder host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Copilot + Qoder host boundary check passed."
