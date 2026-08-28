#!/usr/bin/env bash
# Test skill triggering with naive prompts
# Usage: ./run-test.sh <skill-name> <prompt-file>
#
# Tests whether Claude triggers a skill based on a natural prompt
# (without explicitly mentioning the skill)

set -e

SKILL_NAME="$1"
PROMPT_FILE="$2"
MAX_TURNS="${3:-3}"
TEST_CLI="${AEGIS_TEST_CLI:-${SUPERPOWERS_TEST_CLI:-claude}}"

if [ -z "$SKILL_NAME" ] || [ -z "$PROMPT_FILE" ]; then
    echo "Usage: $0 <skill-name> <prompt-file> [max-turns]"
    echo "Example: $0 systematic-debugging ./test-prompts/debugging.txt"
    exit 1
fi

# Get the directory where this script lives (should be tests/skill-triggering)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the Aegis plugin root (two levels up from tests/skill-triggering)
PLUGIN_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ "$TEST_CLI" = "codex" ]; then
    source "$PLUGIN_DIR/tests/helpers/codex-cli.sh"
else
    source "$PLUGIN_DIR/tests/helpers/claude-cli.sh"
fi

TIMESTAMP=$(date +%s)
if [ "$TEST_CLI" = "codex" ]; then
    OUTPUT_DIR="$PLUGIN_DIR/.tmp/aegis-tests/${TIMESTAMP}/skill-triggering/${SKILL_NAME}"
else
    OUTPUT_DIR="/tmp/aegis-tests/${TIMESTAMP}/skill-triggering/${SKILL_NAME}"
fi
mkdir -p "$OUTPUT_DIR"

# Read prompt from file
PROMPT=$(cat "$PROMPT_FILE")

echo "=== Skill Triggering Test ==="
echo "Skill: $SKILL_NAME"
echo "Prompt file: $PROMPT_FILE"
echo "Max turns: $MAX_TURNS"
echo "Output dir: $OUTPUT_DIR"
echo ""

# Copy prompt for reference
cp "$PROMPT_FILE" "$OUTPUT_DIR/prompt.txt"

if [ "$TEST_CLI" = "codex" ]; then
    PROJECT_DIR="$OUTPUT_DIR/project"
    mkdir -p "$PROJECT_DIR/.agents/skills"
    cp -R "$PLUGIN_DIR/skills/using-aegis" "$PROJECT_DIR/.agents/skills/using-aegis"
    if [ "$SKILL_NAME" != "using-aegis" ] && [ -d "$PLUGIN_DIR/skills/$SKILL_NAME" ]; then
        cp -R "$PLUGIN_DIR/skills/$SKILL_NAME" "$PROJECT_DIR/.agents/skills/$SKILL_NAME"
    fi
else
    PROJECT_DIR="$PLUGIN_DIR"
fi

# Run Claude
if [ "$TEST_CLI" = "codex" ]; then
    LOG_FILE="$OUTPUT_DIR/codex-output.log"
else
    LOG_FILE="$OUTPUT_DIR/claude-output.json"
fi
cd "$OUTPUT_DIR"

echo "Plugin dir: $PLUGIN_DIR"
if [ "$TEST_CLI" = "codex" ]; then
    echo "Running Codex CLI with naive prompt..."
    run_codex_exec_capture "$PROMPT" "$PROJECT_DIR" "$LOG_FILE"
else
    echo "Running Claude CLI with naive prompt..."
    run_claude_stream_json_with_plugin_dir "$PROMPT" "$PLUGIN_DIR" "$MAX_TURNS" "$LOG_FILE"
fi

echo ""
echo "=== Results ==="

if [ "$TEST_CLI" = "codex" ]; then
    if codex_log_mentions_skill "$SKILL_NAME" "$LOG_FILE"; then
        echo "✅ PASS: Skill '$SKILL_NAME' was triggered"
        TRIGGERED=true
    else
        echo "❌ FAIL: Skill '$SKILL_NAME' was NOT triggered"
        TRIGGERED=false
    fi
else
    # Check if skill was triggered (look for Skill tool invocation)
    # In stream-json, tool invocations have "name":"Skill" (not "tool":"Skill")
    # Match either "skill":"skillname" or "skill":"namespace:skillname"
    SKILL_PATTERN='"skill":"([^"]*:)?'"${SKILL_NAME}"'"'
    if grep -q '"name":"Skill"' "$LOG_FILE" && grep -qE "$SKILL_PATTERN" "$LOG_FILE"; then
        echo "✅ PASS: Skill '$SKILL_NAME' was triggered"
        TRIGGERED=true
    else
        echo "❌ FAIL: Skill '$SKILL_NAME' was NOT triggered"
        TRIGGERED=false
    fi
fi

# Show what skills WERE triggered
echo ""
echo "Skills triggered in this run:"
if [ "$TEST_CLI" = "codex" ]; then
    print_codex_skills_triggered "$LOG_FILE" 2>/dev/null || echo "  (none)"
else
    grep -o '"skill":"[^"]*"' "$LOG_FILE" 2>/dev/null | sort -u || echo "  (none)"
fi

# Show first assistant message
echo ""
echo "First assistant response (truncated):"
if [ "$TEST_CLI" = "codex" ]; then
    print_codex_first_assistant_excerpt "$LOG_FILE" || echo "  (could not extract)"
else
    grep '"type":"assistant"' "$LOG_FILE" | head -1 | jq -r '.message.content[0].text // .message.content' 2>/dev/null | head -c 500 || echo "  (could not extract)"
fi

echo ""
echo "Full log: $LOG_FILE"
echo "Timestamp: $TIMESTAMP"

if [ "$TRIGGERED" = "true" ]; then
    exit 0
else
    exit 1
fi
