#!/usr/bin/env bash
# Run all explicit skill request tests
# Usage: ./run-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
TEST_CLI="${AEGIS_TEST_CLI:-${SUPERPOWERS_TEST_CLI:-claude}}"

echo "=== Running All Explicit Skill Request Tests ==="
echo ""

PASSED=0
FAILED=0
RESULTS=""

# Codex run-all is intentionally limited to the approved lightweight smoke matrix.
if [ "$TEST_CLI" != "codex" ]; then
    # Test: subagent-driven-development, please
    echo ">>> Test 1: subagent-driven-development-please"
    if "$SCRIPT_DIR/run-test.sh" "subagent-driven-development" "$PROMPTS_DIR/subagent-driven-development-please.txt"; then
        PASSED=$((PASSED + 1))
        RESULTS="$RESULTS\nPASS: subagent-driven-development-please"
    else
        FAILED=$((FAILED + 1))
        RESULTS="$RESULTS\nFAIL: subagent-driven-development-please"
    fi
    echo ""
fi

# Test: use systematic-debugging
if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 1: use-systematic-debugging"
else
    echo ">>> Test 2: use-systematic-debugging"
fi
if "$SCRIPT_DIR/run-test.sh" "systematic-debugging" "$PROMPTS_DIR/use-systematic-debugging.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-systematic-debugging"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-systematic-debugging"
fi
echo ""

# Test: please use brainstorming
if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 2: please-use-brainstorming"
else
    echo ">>> Test 3: please-use-brainstorming"
fi
if "$SCRIPT_DIR/run-test.sh" "brainstorming" "$PROMPTS_DIR/please-use-brainstorming.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: please-use-brainstorming"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: please-use-brainstorming"
fi
echo ""

# Test: use verification-before-completion
if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 3: use-verification-before-completion"
else
    echo ">>> Test 4: use-verification-before-completion"
fi
if "$SCRIPT_DIR/run-test.sh" "verification-before-completion" "$PROMPTS_DIR/use-verification-before-completion.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-verification-before-completion"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-verification-before-completion"
fi
echo ""

if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 4: use-anti-entropy-governance"
else
    echo ">>> Test 5: use-anti-entropy-governance"
fi
if "$SCRIPT_DIR/run-test.sh" "anti-entropy-governance" "$PROMPTS_DIR/use-anti-entropy-governance.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-anti-entropy-governance"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-anti-entropy-governance"
fi
echo ""

if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 5: use-writing-plans"
    if "$SCRIPT_DIR/run-test.sh" "writing-plans" "$PROMPTS_DIR/use-writing-plans.txt"; then
        PASSED=$((PASSED + 1))
        RESULTS="$RESULTS\nPASS: use-writing-plans"
    else
        FAILED=$((FAILED + 1))
        RESULTS="$RESULTS\nFAIL: use-writing-plans"
    fi
    echo ""
fi

if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 6: use-requesting-code-review"
    if "$SCRIPT_DIR/run-test.sh" "requesting-code-review" "$PROMPTS_DIR/use-requesting-code-review.txt"; then
        PASSED=$((PASSED + 1))
        RESULTS="$RESULTS\nPASS: use-requesting-code-review"
    else
        FAILED=$((FAILED + 1))
        RESULTS="$RESULTS\nFAIL: use-requesting-code-review"
    fi
    echo ""
fi

if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 7: use-recording-architecture-decisions"
else
    echo ">>> Test 7: use-recording-architecture-decisions"
fi
if "$SCRIPT_DIR/run-test.sh" "recording-architecture-decisions" "$PROMPTS_DIR/use-recording-architecture-decisions.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-recording-architecture-decisions"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-recording-architecture-decisions"
fi
echo ""

if [ "$TEST_CLI" != "codex" ]; then
    # Test: mid-conversation execute plan
    echo ">>> Test 8: mid-conversation-execute-plan"
    if "$SCRIPT_DIR/run-test.sh" "subagent-driven-development" "$PROMPTS_DIR/mid-conversation-execute-plan.txt"; then
        PASSED=$((PASSED + 1))
        RESULTS="$RESULTS\nPASS: mid-conversation-execute-plan"
    else
        FAILED=$((FAILED + 1))
        RESULTS="$RESULTS\nFAIL: mid-conversation-execute-plan"
    fi
    echo ""
fi

# Test: use-communicating-concisely
if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 8: use-communicating-concisely"
else
    echo ">>> Test 9: use-communicating-concisely"
fi
if "$SCRIPT_DIR/run-test.sh" "communicating-concisely" "$PROMPTS_DIR/use-communicating-concisely.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-communicating-concisely"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-communicating-concisely"
fi
echo ""

# Test: use-establishing-project-context
if [ "$TEST_CLI" = "codex" ]; then
    echo ">>> Test 9: use-establishing-project-context"
else
    echo ">>> Test 10: use-establishing-project-context"
fi
if "$SCRIPT_DIR/run-test.sh" "establishing-project-context" "$PROMPTS_DIR/use-establishing-project-context.txt"; then
    PASSED=$((PASSED + 1))
    RESULTS="$RESULTS\nPASS: use-establishing-project-context"
else
    FAILED=$((FAILED + 1))
    RESULTS="$RESULTS\nFAIL: use-establishing-project-context"
fi
echo ""

echo "=== Summary ==="
echo -e "$RESULTS"
echo ""
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total: $((PASSED + FAILED))"

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi
