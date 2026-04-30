#!/usr/bin/env bash
# Test: Native Skill Tool Functionality
# Verifies that OpenCode's native skill tool discovers and loads skills correctly
# NOTE: These tests require OpenCode to be installed and configured
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Test: Tools Functionality ==="

# Source setup to create isolated environment
source "$SCRIPT_DIR/setup.sh"

# Trap to cleanup on exit
trap cleanup_test_env EXIT

require_runnable_opencode_or_skip
require_working_opencode_runtime_or_skip

# Test 1: Test skill listing behavior via native skill tool prompt
echo "Test 1: Testing skill listing..."
echo "  Running opencode with skill listing request..."

# Use timeout to prevent hanging, capture both stdout and stderr
output=$(opencode_run_capture "You must call the skill tool right now. List the available skills in the current environment and return only the raw skill names you can access." 2>&1) || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "  [FAIL] OpenCode timed out after ${OPENCODE_TEST_TIMEOUT_SECONDS}s"
        exit 1
    fi
    echo "  [WARN] OpenCode returned non-zero exit code: $exit_code"
}

# Check for exact skill-name lines emitted by the model after calling the skill tool
if grep -qx "brainstorming" <<< "$output" \
    && grep -qx "using-aegis" <<< "$output" \
    && grep -qx "personal-test" <<< "$output"; then
    echo "  [PASS] skill listing discovered aegis skills"
else
    echo "  [FAIL] skill listing did not return expected skills"
    echo "  Output was:"
    echo "$output" | head -50
    exit 1
fi

# Test 2: Test use_skill tool
echo ""
echo "Test 2: Testing skill loading..."
echo "  Running opencode with skill request..."

output=$(opencode_run_capture "You must call the skill tool with the skill name personal-test. Return the exact content you received, including any PERSONAL_SKILL_MARKER text." 2>&1) || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "  [FAIL] OpenCode timed out after ${OPENCODE_TEST_TIMEOUT_SECONDS}s"
        exit 1
    fi
    echo "  [WARN] OpenCode returned non-zero exit code: $exit_code"
}

# Check for the skill marker we embedded
if echo "$output" | grep -qi "PERSONAL_SKILL_MARKER_12345\|Personal Test Skill\|Launching skill"; then
    echo "  [PASS] use_skill loaded personal-test skill content"
else
    echo "  [FAIL] use_skill did not load personal-test skill correctly"
    echo "  Output was:"
    echo "$output" | head -50
    exit 1
fi

# Test 3: Test use_skill with aegis: prefix
echo ""
echo "Test 3: Testing aegis skill loading..."
echo "  Running opencode with brainstorming skill..."

output=$(opencode_run_capture "You must call the skill tool with the skill name brainstorming. Return the first few lines of the loaded skill content." 2>&1) || {
    exit_code=$?
    if [ $exit_code -eq 124 ]; then
        echo "  [FAIL] OpenCode timed out after ${OPENCODE_TEST_TIMEOUT_SECONDS}s"
        exit 1
    fi
    echo "  [WARN] OpenCode returned non-zero exit code: $exit_code"
}

# Check for expected content from brainstorming skill
if echo "$output" | grep -qi "Brainstorming Ideas Into Designs\|current project context and authority boundary\|fully formed designs and specs"; then
    echo "  [PASS] skill loading returned brainstorming content"
else
    echo "  [FAIL] skill loading did not return brainstorming content"
    echo "  Output was:"
    echo "$output" | head -50
    exit 1
fi

echo ""
echo "=== All tools tests passed ==="
