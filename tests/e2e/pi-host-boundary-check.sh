#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

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

echo "=== Pi Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
prompt_hygiene="docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.en.md"
zh_readme="README.md"
pi_guide="docs/README.pi.md"
install_check="tests/e2e/install-verification-policy-check.sh"
goal_check="tests/e2e/goal-framing-check.sh"
activation_check="tests/e2e/activation-mode-check.sh"

"${PYTHON_CMD[@]}" - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("package.json").read_text(encoding="utf-8"))
keywords = data.get("keywords", [])
if "pi-package" not in keywords:
    raise SystemExit("package.json missing pi-package keyword")
pi = data.get("pi")
if not isinstance(pi, dict):
    raise SystemExit("package.json missing pi manifest")
skills = pi.get("skills")
if "./skills" not in skills:
    raise SystemExit("package.json pi.skills must include ./skills")
print("  [PASS] package.json exposes Aegis skills as a Pi package")
PY

assert_contains "$matrix" "\`Pi CLI\`" \
    "compatibility matrix lists Pi CLI"
assert_contains "$matrix" "Pi CLI.*no current release-level fresh smoke verdict|Pi CLI.*no current fresh release verdict" \
    "compatibility matrix keeps Pi CLI out of fresh closeout"
assert_contains "$matrix" "pi install git:github.com/GanyuanRan/Aegis" \
    "compatibility matrix records Pi git package install"
assert_contains "$matrix" "~/.pi/agent/skills/|~/.agents/skills/|\\.pi/skills/" \
    "compatibility matrix records Pi native skill locations"
assert_contains "$matrix" "package.*skills.*pi\\.skills|pi\\.skills.*package.*skills" \
    "compatibility matrix records Pi package skill discovery"

assert_contains "$known_limits" "Pi CLI Structural Support" \
    "known limitations records Pi structural support boundary"
assert_contains "$known_limits" "not release-level fresh[[:space:]]+smoke verdict" \
    "known limitations avoids Pi live smoke claim"
assert_contains "$known_limits" "pi install git:github.com/GanyuanRan/Aegis" \
    "known limitations records Pi package install evidence"
assert_contains "$known_limits" "~/.pi/agent/skills/|~/.agents/skills/|\\.pi/skills/" \
    "known limitations records Pi native skill paths"

assert_contains "$release_checklist" "docs/README.pi.md" \
    "release checklist includes Pi host guide"
assert_contains "$release_checklist" "Pi CLI" \
    "release checklist tracks Pi host status"
assert_contains "$prompt_hygiene" "Pi CLI" \
    "prompt hygiene covers Pi CLI"
assert_contains "$current_readme" "docs/README.pi.md" \
    "current authority map includes Pi guide"

assert_contains "$root_readme" "\`Pi CLI\`" \
    "English README lists Pi CLI"
assert_contains "$root_readme" "docs/README.pi.md" \
    "English README links Pi guide"
assert_contains "$zh_readme" "\`Pi CLI\`" \
    "Chinese README lists Pi CLI"
assert_contains "$zh_readme" "docs/README.pi.md" \
    "Chinese README links Pi guide"

if [[ -f "$pi_guide" ]]; then
    pass "Pi host guide exists"
else
    fail "Pi host guide exists"
fi

assert_contains "$pi_guide" "https://pi.dev/docs/latest/skills" \
    "Pi guide cites official skills docs"
assert_contains "$pi_guide" "https://pi.dev/docs/latest/packages" \
    "Pi guide cites official package docs"
assert_contains "$pi_guide" "npm install -g --ignore-scripts @earendil-works/pi-coding-agent" \
    "Pi guide documents Pi CLI installation source"
assert_contains "$pi_guide" "pi install git:github.com/GanyuanRan/Aegis" \
    "Pi guide documents git package install"
assert_contains "$pi_guide" "~/.pi/agent/skills/|~/.agents/skills/|\\.pi/skills/" \
    "Pi guide documents native skill paths"
assert_contains "$pi_guide" "aegis-doctor\\.py --write-config --json" \
    "Pi guide includes complete-install doctor"
assert_contains "$pi_guide" "aegis-update\\.py register[[:space:]]+\\\\?[[:space:]]+--host pi|aegis-update\\.py register --host pi" \
    "Pi guide registers host-scoped update metadata"
assert_contains "$pi_guide" "Aegis goal:" \
    "Pi guide documents portable goal entry"
assert_contains "$pi_guide" "AEGIS_ACTIVATION_MODE=explicit" \
    "Pi guide documents explicit activation caveat"
assert_contains "$pi_guide" "does not override Pi" \
    "Pi guide clarifies activation mode does not control Pi native matcher"
assert_contains "$pi_guide" "GateDecision|completion authority" \
    "Pi guide preserves authority boundary"
assert_contains "$pi_guide" "does \\*\\*not\\*\\* claim current release-level live smoke evidence|does not claim current release-level live smoke evidence" \
    "Pi guide avoids live smoke claim"
assert_not_contains "$pi_guide" "authoritative.*GateDecision|final completion authority" \
    "Pi guide does not elevate Aegis to runtime authority"

assert_contains "$install_check" "docs/README.pi.md" \
    "install verification policy includes Pi guide"
assert_contains "$goal_check" "docs/README.pi.md" \
    "goal-framing policy includes Pi guide"
assert_contains "$activation_check" "docs/README.pi.md" \
    "activation-mode policy includes Pi guide"

if (( failures > 0 )); then
    echo ""
    echo "Pi host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Pi host boundary check passed."
