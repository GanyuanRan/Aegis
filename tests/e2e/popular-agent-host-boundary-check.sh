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

echo "=== Popular Agent Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.en.md"
zh_readme="README.md"
openclaw_guide="docs/README.openclaw.md"
hermes_guide="docs/README.hermes-agent.md"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

assert_contains "$matrix" "\`OpenClaw\`" \
    "compatibility matrix lists OpenClaw"
assert_contains "$matrix" "\`Hermes Agent\`" \
    "compatibility matrix lists Hermes Agent"
assert_contains "$matrix" "OpenClaw.*no current release-level fresh smoke verdict|OpenClaw.*no current fresh release verdict" \
    "compatibility matrix keeps OpenClaw out of fresh closeout"
assert_contains "$matrix" "Hermes Agent.*no current release-level fresh smoke verdict|Hermes Agent.*no current fresh release verdict" \
    "compatibility matrix keeps Hermes Agent out of fresh closeout"
assert_contains "$matrix" "OpenClaw.*individual.*skill-directory" \
    "compatibility matrix records OpenClaw individual skill-directory install"
assert_contains "$matrix" "Hermes Agent.*~/.hermes/skills/|~/.hermes/skills/.*Hermes Agent" \
    "compatibility matrix records Hermes local skills path"

assert_contains "$known_limits" "OpenClaw and Hermes Agent Structural Support" \
    "known limitations records popular-agent structural support boundary"
assert_contains "$known_limits" "not release-level fresh[[:space:]]+smoke verdicts" \
    "known limitations avoids live smoke claim"
assert_contains "$known_limits" "openclaw skills install" \
    "known limitations records OpenClaw installer evidence"
assert_contains "$known_limits" "hermes skills install owner/repo/skills/my-workflow" \
    "known limitations records Hermes path install evidence"

assert_contains "$release_checklist" "docs/README.openclaw.md" \
    "release checklist includes OpenClaw host guide"
assert_contains "$release_checklist" "docs/README.hermes-agent.md" \
    "release checklist includes Hermes Agent host guide"
assert_contains "$prompt_hygiene" "OpenClaw" \
    "prompt hygiene covers OpenClaw"
assert_contains "$prompt_hygiene" "Hermes Agent" \
    "prompt hygiene covers Hermes Agent"
assert_contains "$current_readme" "docs/README.openclaw.md" \
    "current authority map includes OpenClaw guide"
assert_contains "$current_readme" "docs/README.hermes-agent.md" \
    "current authority map includes Hermes guide"

assert_contains "$root_readme" "\`OpenClaw\`" \
    "English README lists OpenClaw"
assert_contains "$root_readme" "\`Hermes Agent\`" \
    "English README lists Hermes Agent"
assert_contains "$zh_readme" "\`OpenClaw\`" \
    "Chinese README lists OpenClaw"
assert_contains "$zh_readme" "\`Hermes Agent\`" \
    "Chinese README lists Hermes Agent"
assert_contains "$root_readme" "docs/README.openclaw.md" \
    "English README links OpenClaw guide"
assert_contains "$root_readme" "docs/README.hermes-agent.md" \
    "English README links Hermes guide"
assert_contains "$zh_readme" "docs/README.openclaw.md" \
    "Chinese README links OpenClaw guide"
assert_contains "$zh_readme" "docs/README.hermes-agent.md" \
    "Chinese README links Hermes guide"

if [[ -f "$openclaw_guide" ]]; then
    pass "OpenClaw host guide exists"
else
    fail "OpenClaw host guide exists"
fi

if [[ -f "$hermes_guide" ]]; then
    pass "Hermes Agent host guide exists"
else
    fail "Hermes Agent host guide exists"
fi

assert_contains "$openclaw_guide" "https://docs.openclaw.ai/cli/skills" \
    "OpenClaw guide cites official skill docs"
assert_contains "$openclaw_guide" "openclaw skills install" \
    "OpenClaw guide documents install command"
assert_contains "$openclaw_guide" "SKILL.md.*source root|source root.*SKILL.md" \
    "OpenClaw guide records SKILL.md source-root contract"
assert_contains "$openclaw_guide" "not claim current release-level live smoke evidence|fresh host smoke evidence" \
    "OpenClaw guide avoids live smoke claim"
assert_contains "$openclaw_guide" "aegis-doctor\\.py --write-config --json" \
    "OpenClaw guide includes complete-install doctor"
assert_contains "$openclaw_guide" "GateDecision|completion authority" \
    "OpenClaw guide preserves authority boundary"
assert_not_contains "$openclaw_guide" "openclaw skills install git:GanyuanRan/Aegis" \
    "OpenClaw guide does not recommend canonical whole-repo git install"

assert_contains "$hermes_guide" "https://hermes-agent.nousresearch.com/docs/skills/" \
    "Hermes guide cites official skills hub"
assert_contains "$hermes_guide" "Skills Hub" \
    "Hermes guide records Skills Hub evidence"
assert_contains "$hermes_guide" "~/.hermes/skills/" \
    "Hermes guide records local skills path"
assert_contains "$hermes_guide" "hermes skills install GanyuanRan/Aegis/skills/using-aegis" \
    "Hermes guide documents individual GitHub path install"
assert_contains "$hermes_guide" "hermes skills list" \
    "Hermes guide documents skill listing verification"
assert_contains "$hermes_guide" "does \\*\\*not\\*\\*|does not" \
    "Hermes guide includes negative live smoke qualifier"
assert_contains "$hermes_guide" "claim current release-level live smoke evidence" \
    "Hermes guide avoids live smoke claim"
assert_contains "$hermes_guide" "aegis-doctor\\.py --write-config --json" \
    "Hermes guide includes complete-install doctor"
assert_contains "$hermes_guide" "GateDecision|completion authority" \
    "Hermes guide preserves authority boundary"

assert_contains "$install_check" "docs/README.openclaw.md" \
    "install verification policy includes OpenClaw guide"
assert_contains "$install_check" "docs/README.hermes-agent.md" \
    "install verification policy includes Hermes guide"
assert_contains "$goal_check" "docs/README.openclaw.md" \
    "goal-framing policy includes OpenClaw guide"
assert_contains "$goal_check" "docs/README.hermes-agent.md" \
    "goal-framing policy includes Hermes guide"
assert_contains "$activation_check" "docs/README.openclaw.md" \
    "activation-mode policy includes OpenClaw guide"
assert_contains "$activation_check" "docs/README.hermes-agent.md" \
    "activation-mode policy includes Hermes guide"

if (( failures > 0 )); then
    echo ""
    echo "Popular agent host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Popular agent host boundary check passed."
