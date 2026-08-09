#!/usr/bin/env bash
# Test explicit skill requests (user names a skill directly)
# Usage: ./run-test.sh <skill-name> <prompt-file>
#
# Tests whether Claude invokes a skill when the user explicitly requests it by name
# (without using the plugin namespace prefix)
#
# Runs in a scratch project directory, but under the caller's real HOME, so the
# locally installed Claude Code environment (user CLAUDE.md, skills, agents) is
# in scope for every run

set -e

SKILL_NAME="$1"
PROMPT_FILE="$2"
MAX_TURNS="${3:-3}"
TEST_CLI="${AEGIS_TEST_CLI:-${SUPERPOWERS_TEST_CLI:-claude}}"

if [ -z "$SKILL_NAME" ] || [ -z "$PROMPT_FILE" ]; then
    echo "Usage: $0 <skill-name> <prompt-file> [max-turns]"
    echo "Example: $0 subagent-driven-development ./prompts/subagent-driven-development-please.txt"
    exit 1
fi

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the Aegis plugin root (two levels up)
PLUGIN_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ "$TEST_CLI" = "codex" ]; then
    source "$PLUGIN_DIR/tests/helpers/codex-cli.sh"
else
    source "$PLUGIN_DIR/tests/helpers/claude-cli.sh"
fi

TIMESTAMP=$(date +%s)
if [ "$TEST_CLI" = "codex" ]; then
    OUTPUT_DIR="$PLUGIN_DIR/.tmp/aegis-tests/${TIMESTAMP}/explicit-skill-requests/${SKILL_NAME}"
else
    OUTPUT_DIR="/tmp/aegis-tests/${TIMESTAMP}/explicit-skill-requests/${SKILL_NAME}"
fi
mkdir -p "$OUTPUT_DIR"

# Read prompt from file
PROMPT=$(cat "$PROMPT_FILE")

echo "=== Explicit Skill Request Test ==="
echo "Skill: $SKILL_NAME"
echo "Prompt file: $PROMPT_FILE"
echo "Max turns: $MAX_TURNS"
echo "Output dir: $OUTPUT_DIR"
echo ""

# Copy prompt for reference
cp "$PROMPT_FILE" "$OUTPUT_DIR/prompt.txt"

# Create a minimal project directory for the test
PROJECT_DIR="$OUTPUT_DIR/project"
mkdir -p "$PROJECT_DIR/docs/aegis/plans"

if [ "$TEST_CLI" = "codex" ]; then
    mkdir -p "$PROJECT_DIR/docs/current" "$PROJECT_DIR/docs/adr" "$PROJECT_DIR/skills"
    cp "$PLUGIN_DIR/docs/current/README.md" "$PROJECT_DIR/docs/current/README.md"
    cp "$PLUGIN_DIR/docs/current/AEGIS_TARGET_STATE.md" "$PROJECT_DIR/docs/current/AEGIS_TARGET_STATE.md"
    cp "$PLUGIN_DIR/docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md" "$PROJECT_DIR/docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md"
    cp "$PLUGIN_DIR/docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md" "$PROJECT_DIR/docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md"
    cp -R "$PLUGIN_DIR/skills/using-aegis" "$PROJECT_DIR/skills/using-aegis"
    if [ -d "$PLUGIN_DIR/skills/$SKILL_NAME" ]; then
        cp -R "$PLUGIN_DIR/skills/$SKILL_NAME" "$PROJECT_DIR/skills/$SKILL_NAME"
    fi
fi

# Create a dummy plan file for mid-conversation tests
cat > "$PROJECT_DIR/docs/aegis/plans/auth-system.md" << 'EOF'
# Auth System Implementation Plan

## Task 1: Add User Model
Create user model with email and password fields.

## Task 2: Add Auth Routes
Create login and register endpoints.

## Task 3: Add JWT Middleware
Protect routes with JWT validation.
EOF

# Run CLI in the scratch project directory
if [ "$TEST_CLI" = "codex" ]; then
    LOG_FILE="$OUTPUT_DIR/codex-output.log"
else
    LOG_FILE="$OUTPUT_DIR/claude-output.json"
fi
cd "$PROJECT_DIR"

echo "Plugin dir: $PLUGIN_DIR"
if [ "$TEST_CLI" = "codex" ]; then
    echo "Running Codex CLI with explicit skill request..."
else
    echo "Running Claude CLI with explicit skill request..."
fi
echo "Prompt: $PROMPT"
echo ""

if [ "$TEST_CLI" = "codex" ]; then
    run_codex_exec_capture "$PROMPT" "$PROJECT_DIR" "$LOG_FILE"
else
    run_claude_stream_json_with_plugin_dir "$PROMPT" "$PLUGIN_DIR" "$MAX_TURNS" "$LOG_FILE"
fi

echo ""
echo "=== Results ==="

if [ "$TEST_CLI" = "codex" ]; then
    if codex_log_mentions_skill "$SKILL_NAME" "$LOG_FILE"; then
        echo "PASS: Skill '$SKILL_NAME' was triggered"
        TRIGGERED=true
    else
        echo "FAIL: Skill '$SKILL_NAME' was NOT triggered"
        TRIGGERED=false
    fi
else
    # Check if skill was triggered (look for Skill tool invocation)
    # Match either "skill":"skillname" or "skill":"namespace:skillname"
    SKILL_PATTERN='"skill":"([^"]*:)?'"${SKILL_NAME}"'"'
    if grep -q '"name":"Skill"' "$LOG_FILE" && grep -qE "$SKILL_PATTERN" "$LOG_FILE"; then
        echo "PASS: Skill '$SKILL_NAME' was triggered"
        TRIGGERED=true
    else
        echo "FAIL: Skill '$SKILL_NAME' was NOT triggered"
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

# Check if Claude took action BEFORE invoking the skill (the failure mode)
echo ""
echo "Checking for premature action..."

if [ "$TEST_CLI" = "codex" ]; then
    FIRST_SKILL_LINE=$(codex_first_skill_load_line "$SKILL_NAME" "$LOG_FILE")
    if [ -n "$FIRST_SKILL_LINE" ]; then
        PREMATURE_EXECS=$(head -n "$FIRST_SKILL_LINE" "$LOG_FILE" | \
            grep -a '^exec$' || true)
        if [ -n "$PREMATURE_EXECS" ]; then
            echo "WARNING: Commands were executed before the skill file was loaded"
            echo "This Codex smoke runner only guarantees the requested skill became visible."
        else
            echo "OK: No command markers detected before the requested skill load"
        fi
    else
        echo "WARNING: No skill load marker found at all"
    fi
else
    # Look for tool invocations before the Skill invocation
    # This detects the failure mode where Claude starts doing work without loading the skill
    FIRST_SKILL_LINE=$(grep -n '"name":"Skill"' "$LOG_FILE" | head -1 | cut -d: -f1)
    if [ -n "$FIRST_SKILL_LINE" ]; then
        # Check if any non-Skill, non-system tools were invoked before the first Skill invocation
        # Filter out system messages, TodoWrite (planning is ok), and other non-action tools
        PREMATURE_TOOLS=$(head -n "$FIRST_SKILL_LINE" "$LOG_FILE" | \
            grep '"type":"tool_use"' | \
            grep -v '"name":"Skill"' | \
            grep -v '"name":"TodoWrite"' || true)
        if [ -n "$PREMATURE_TOOLS" ]; then
            echo "WARNING: Tools invoked BEFORE Skill tool:"
            echo "$PREMATURE_TOOLS" | head -5
            echo ""
            echo "This indicates Claude started working before loading the requested skill."
        else
            echo "OK: No premature tool invocations detected"
        fi
    else
        echo "WARNING: No Skill invocation found at all"
    fi
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
