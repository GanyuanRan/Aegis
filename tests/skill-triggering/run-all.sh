#!/usr/bin/env bash
# Run all skill triggering tests
# Usage: ./run-all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
TEST_CLI="${AEGIS_TEST_CLI:-${SUPERPOWERS_TEST_CLI:-claude}}"

if [ "$TEST_CLI" = "codex" ]; then
    # Codex currently provides the lightweight active Wave 1 + Wave 2 smoke matrix.
    SKILLS=(
        "brainstorming"
        "communicating-concisely"
        "establishing-project-context"
        "systematic-debugging"
        "verification-before-completion"
        "writing-plans"
        "requesting-code-review"
    )
else
    SKILLS=(
        "brainstorming"
        "communicating-concisely"
        "establishing-project-context"
        "systematic-debugging"
        "verification-before-completion"
        "test-driven-development"
        "writing-plans"
        "dispatching-parallel-agents"
        "executing-plans"
        "requesting-code-review"
    )
fi

echo "=== Running Skill Triggering Tests ==="
echo ""

PASSED=0
FAILED=0
RESULTS=()

for skill in "${SKILLS[@]}"; do
    prompt_file="$PROMPTS_DIR/${skill}.txt"

    if [ ! -f "$prompt_file" ]; then
        echo "⚠️  SKIP: No prompt file for $skill"
        continue
    fi

    echo "Testing: $skill"

    if "$SCRIPT_DIR/run-test.sh" "$skill" "$prompt_file" 3 2>&1 | tee /tmp/skill-test-$skill.log; then
        PASSED=$((PASSED + 1))
        RESULTS+=("✅ $skill")
    else
        FAILED=$((FAILED + 1))
        RESULTS+=("❌ $skill")
    fi

    echo ""
    echo "---"
    echo ""
done

echo ""
echo "=== Summary ==="
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
echo ""
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -gt 0 ]; then
    exit 1
fi
