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

echo "=== OMP Host Boundary Check ==="

matrix="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"
known_limits="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
release_checklist="docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md"
current_readme="docs/current/README.md"
root_readme="README.md"
zh_readme="README.zh-CN.md"
omp_guide="docs/README.omp.md"
pi_guide="docs/README.pi.md"
using_aegis="skills/using-aegis/SKILL.md"
shared_core="extensions/shared/aegis-bootstrap.ts"
omp_ext="extensions/omp/index.ts"
pi_ext="extensions/pi/index.ts"

"${PYTHON_CMD[@]}" - <<'PY'
import json
from pathlib import Path

data = json.loads(Path("package.json").read_text(encoding="utf-8"))
pi = data.get("pi")
if not isinstance(pi, dict) or "./extensions/pi" not in pi.get("extensions", []):
    raise SystemExit("package.json pi.extensions must include ./extensions/pi")
omp = data.get("omp")
if not isinstance(omp, dict) or "./extensions/omp" not in omp.get("extensions", []):
    raise SystemExit("package.json omp.extensions must include ./extensions/omp")
print("  [PASS] package.json declares pi.extensions and omp.extensions bundles")
PY

for f in "$shared_core" "$pi_ext" "$omp_ext"; do
    if [ -f "$f" ]; then
        pass "extension file exists: $f"
    else
        fail "extension file exists: $f"
    fi
done

assert_contains "$using_aegis" "alwaysApply: true" \
    "using-aegis is marked alwaysApply for OMP native injection"

assert_contains "$matrix" "\`OMP \(Oh My Pi\)\`" \
    "compatibility matrix lists OMP (Oh My Pi)"
assert_contains "$matrix" "OMP.*no current release-level fresh smoke verdict|OMP.*no current fresh release verdict" \
    "compatibility matrix keeps OMP out of fresh closeout"
assert_contains "$matrix" "~/.omp/agent/extensions/" \
    "compatibility matrix records OMP extension root"

assert_contains "$known_limits" "OMP Structural Support" \
    "known limitations records OMP structural support boundary"
assert_contains "$known_limits" "not release-level fresh[[:space:]]+smoke verdict" \
    "known limitations avoids OMP live smoke claim"

assert_contains "$release_checklist" "docs/README.omp.md" \
    "release checklist includes OMP host guide"

assert_contains "$current_readme" "docs/README.omp.md" \
    "current authority map includes OMP guide"

assert_contains "$root_readme" "\`OMP\`" \
    "English README lists OMP"
assert_contains "$root_readme" "docs/README.omp.md" \
    "English README links OMP guide"
assert_contains "$zh_readme" "\`OMP\`" \
    "Chinese README lists OMP"
assert_contains "$zh_readme" "docs/README.omp.md" \
    "Chinese README links OMP guide"

if [[ -f "$omp_guide" ]]; then
    pass "OMP host guide exists"
else
    fail "OMP host guide exists"
fi

assert_contains "$omp_guide" "github.com/can1357/oh-my-pi" \
    "OMP guide cites the official OMP repository"
assert_contains "$omp_guide" "@oh-my-pi/pi-coding-agent" \
    "OMP guide documents the OMP CLI package"
assert_contains "$omp_guide" "~/.agents/skills/" \
    "OMP guide documents agents-provider skill discovery"
assert_contains "$omp_guide" "alwaysApply" \
    "OMP guide documents alwaysApply native injection"
assert_contains "$omp_guide" "~/.omp/agent/extensions/" \
    "OMP guide documents extension loading root"
assert_contains "$omp_guide" "aegis-update\\.py register[[:space:]]+\\\\?[[:space:]]+--host omp|aegis-update\\.py register --host omp" \
    "OMP guide registers host-scoped update metadata"
assert_contains "$omp_guide" "Aegis goal:" \
    "OMP guide documents portable goal entry"
assert_contains "$omp_guide" "AEGIS_ACTIVATION_MODE=explicit" \
    "OMP guide documents explicit activation mode"
assert_contains "$omp_guide" "GateDecision|completion authority" \
    "OMP guide preserves authority boundary"
assert_contains "$omp_guide" "does \\*\\*not\\*\\* claim current release-level live smoke evidence|does not claim current release-level live smoke evidence" \
    "OMP guide avoids live smoke claim"
assert_not_contains "$omp_guide" "authoritative.*GateDecision|final completion authority" \
    "OMP guide does not elevate Aegis to runtime authority"

assert_contains "$pi_guide" "extensions/pi" \
    "Pi guide documents the Pi extension bundle"

if (( failures > 0 )); then
    echo ""
    echo "OMP host boundary check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "OMP host boundary check passed."
