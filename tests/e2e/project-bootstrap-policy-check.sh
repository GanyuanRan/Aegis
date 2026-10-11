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

    if grep -qE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

assert_not_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        fail "$label"
    else
        pass "$label"
    fi
}

echo "=== Project Bootstrap Policy Check ==="

process_doc="docs/current/AEGIS_PROCESS_BASELINE.md"
using_skill="skills/using-aegis/SKILL.md"
discipline_ref="skills/using-aegis/references/skill-discipline.md"
brainstorming_skill="skills/brainstorming/SKILL.md"
plans_skill="skills/writing-plans/SKILL.md"
tdd_skill="skills/test-driven-development/SKILL.md"
debugging_skill="skills/systematic-debugging/SKILL.md"
verification_skill="skills/verification-before-completion/SKILL.md"
limitations_doc="docs/current/AEGIS_KNOWN_LIMITATIONS.md"
compat_doc="docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md"

assert_contains "docs/current/AEGIS_PROCESS_BASELINE.md" 'skills/using-aegis/references/skill-discipline.md' \
    'process baseline points to the bootstrap/workspace owner'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'Project Baseline Bootstrap' \
    'discipline owner defines baseline bootstrap'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'bounded repo scan' \
    'discipline owner requires a bounded baseline scan'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'too sparse' \
    'discipline owner preserves sparse-project no-op'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'Workspace Shell' \
    'discipline owner distinguishes workspace shell'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'Task Work Record' \
    'discipline owner distinguishes task records'
assert_contains "skills/using-aegis/references/skill-discipline.md" 'Spec Brief vs Design Spec' \
    'discipline owner separates conditional spec depth'
assert_contains "$process_doc" "Lazy Workspace Support|lazy" \
    "process baseline defines lazy workspace support"
assert_contains "skills/using-aegis/references/skill-discipline.md" 'normal Q&A|simple explanation|version/status' \
    'discipline owner lists no-workspace fast paths'

assert_contains "$using_skill" "Active codebase question|what next" \
    "using-aegis hot path includes project baseline bootstrap trigger"
assert_contains "$using_skill" "bounded" \
    "using-aegis hot path keeps baseline scan bounded"
assert_contains "$using_skill" "index-first scan" \
    "using-aegis hot path keeps scan bounded"
assert_contains "$using_skill" "lazy" \
    "using-aegis hot path states workspace support is lazy"
assert_not_contains "$using_skill" "scripts/aegis-workspace.py init" \
    "using-aegis hot path no longer hardcodes target-project helper command"

assert_contains "$discipline_ref" "Project Baseline Bootstrap" \
    "discipline reference expands baseline bootstrap policy"
assert_contains "$discipline_ref" "Workspace Shell" \
    "discipline reference names workspace shell"
assert_contains "$discipline_ref" "Task Work Record" \
    "discipline reference names task work record"
assert_contains "$discipline_ref" "Spec Brief" \
    "discipline reference explains spec brief"
assert_contains "$discipline_ref" "configured Aegis workspace support|installed Aegis workspace support" \
    "discipline reference avoids target-project helper ownership"

assert_contains "$brainstorming_skill" "Spec Brief" \
    "brainstorming supports spec brief"
assert_contains "$brainstorming_skill" "Do not force this workflow onto low-complexity work" \
    "brainstorming does not over-trigger on low-complexity work"
assert_contains "$brainstorming_skill" "single-owner bug fix|simple config/status question|local utility change" \
    "brainstorming defines fast-path examples"
assert_contains "$brainstorming_skill" "Write the validated spec artifact when needed" \
    "brainstorming writes specs conditionally"
assert_not_contains "$brainstorming_skill" "Every project goes through this process" \
    "brainstorming retired universal design ceremony wording"
assert_not_contains "$discipline_ref" "1%" \
    "discipline reference retired 1 percent over-trigger rule"
assert_contains "$plans_skill" "Spec Brief" \
    "writing-plans accepts spec brief as medium-task input"
assert_contains "$tdd_skill" "configured Aegis workspace support|installed Aegis workspace support" \
    "TDD references configured workspace support"
assert_contains "$debugging_skill" "fast bug fix|quick bug fix|quick fix" \
    "debugging pressure path covers quick bug fix triage"
assert_contains "$verification_skill" "configured Aegis workspace support|installed Aegis workspace support" \
    "verification uses configured workspace support"

assert_contains "$limitations_doc" "sparse|sufficient project content" \
    "known limitations records sparse baseline boundary"
assert_contains "$limitations_doc" "copy-only|skills-only|skills only" \
    "known limitations records copy-only install boundary"
assert_contains "$compat_doc" "project workspace support" \
    "compatibility snapshot distinguishes project workspace support"
assert_contains "$compat_doc" "skill discovery" \
    "compatibility snapshot still names skill discovery"

if (( failures > 0 )); then
    echo ""
    echo "Project bootstrap policy check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Project bootstrap policy check passed."
