#!/usr/bin/env bash
# Test: Skill Scope Resolution
# Verifies the current OpenCode skill visibility contract:
# - personal skills are available globally
# - project skills are available in project context
# - project skills are not available outside project context
#
# Duplicate skill names across scopes are intentionally NOT used here.
# OpenCode's official skills docs require skill names to stay unique, so
# duplicate-name override behavior is not treated as a compatibility contract.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Skill Scope Resolution ==="

source "$SCRIPT_DIR/setup.sh"
trap cleanup_test_env EXIT

echo "Setting up scope test fixtures..."

mkdir -p "$OPENCODE_PERSONAL_SKILLS_DIR/personal-scope-test"
cat > "$OPENCODE_PERSONAL_SKILLS_DIR/personal-scope-test/SKILL.md" <<'EOF'
---
name: personal-scope-test
description: Personal scope test skill
---
# Personal Scope Test Skill

PERSONAL_SCOPE_MARKER_12345
EOF

mkdir -p "$TEST_HOME/test-project/.opencode/skills/project-scope-test"
cat > "$TEST_HOME/test-project/.opencode/skills/project-scope-test/SKILL.md" <<'EOF'
---
name: project-scope-test
description: Project scope test skill
---
# Project Scope Test Skill

PROJECT_SCOPE_MARKER_67890
EOF

echo "  Created personal-scope-test and project-scope-test fixtures"

echo ""
echo "Test 1: Verifying test fixtures..."

if [ -f "$OPENCODE_PERSONAL_SKILLS_DIR/personal-scope-test/SKILL.md" ]; then
    echo "  [PASS] Personal scope fixture exists"
else
    echo "  [FAIL] Personal scope fixture missing"
    exit 1
fi

if [ -f "$TEST_HOME/test-project/.opencode/skills/project-scope-test/SKILL.md" ]; then
    echo "  [PASS] Project scope fixture exists"
else
    echo "  [FAIL] Project scope fixture missing"
    exit 1
fi

require_runnable_opencode_or_skip
require_working_opencode_runtime_or_skip

echo ""
echo "Test 2: Testing visible skills outside project..."

cd "$HOME"
output=$(opencode_run_capture "You must call the skill tool right now. List the available skills in the current environment and return only the raw skill names you can access." "$PWD" 2>&1) || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "  [FAIL] OpenCode timed out after ${OPENCODE_TEST_TIMEOUT_SECONDS}s"
        exit 1
    fi
}

normalized_output=$(printf '%s\n' "$output" | tr -d '\r')

if grep -qi "personal-scope-test" <<< "$normalized_output" \
    && ! grep -qi "project-scope-test" <<< "$normalized_output"; then
    echo "  [PASS] Outside project, personal skill is visible and project skill is hidden"
else
    echo "  [FAIL] Outside-project skill visibility did not match expectation"
    echo "  Output snippet:"
    echo "$output" | head -20
    exit 1
fi

echo ""
echo "Test 3: Testing visible skills inside project..."

cd "$TEST_HOME/test-project"
output=$(opencode_run_capture "You must call the skill tool right now. List the available skills in the current environment and return only the raw skill names you can access." "$PWD" 2>&1) || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "  [FAIL] OpenCode timed out after ${OPENCODE_TEST_TIMEOUT_SECONDS}s"
        exit 1
    fi
}

normalized_output=$(printf '%s\n' "$output" | tr -d '\r')

if grep -qi "personal-scope-test" <<< "$normalized_output" \
    && grep -qi "project-scope-test" <<< "$normalized_output"; then
    echo "  [PASS] Inside project, both personal and project skills are visible"
else
    echo "  [FAIL] Inside-project skill visibility did not match expectation"
    echo "  Output snippet:"
    echo "$output" | head -20
    exit 1
fi

echo ""
echo "=== All scope tests passed ==="
