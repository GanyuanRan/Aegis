# Testing Aegis Skills

This document describes how to test Aegis skills, particularly the integration tests for complex skills like `subagent-driven-development`.

This page is an execution guide, not the authority source for current scope or release status.
For the current `Aegis Method Pack` authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

## Overview

Testing skills that involve subagents, workflows, and complex interactions requires running actual Claude Code sessions in headless mode and verifying their behavior through session transcripts.

## Test Structure

```
tests/
├── claude-code/
│   ├── test-helpers.sh                    # Shared test utilities
│   ├── test-subagent-driven-development-integration.sh
│   ├── analyze-token-usage.py             # Token analysis tool
│   └── run-skill-tests.sh                 # Test runner (if exists)
```

## Running Tests

### Integration Tests

Integration tests execute real Claude Code sessions with actual skills:

```bash
# Run the subagent-driven-development integration test
cd tests/claude-code
./test-subagent-driven-development-integration.sh
```

**Note:** Integration tests can take 10-30 minutes as they execute real implementation plans with multiple subagents.

### Wave 1 + Wave 2 Skill Smoke Tests With Codex

For the current lightweight `Aegis` Codex smoke matrix, the skill-triggering scripts also support Codex CLI:

```bash
AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming tests/skill-triggering/prompts/brainstorming.txt
AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh brainstorming tests/explicit-skill-requests/prompts/please-use-brainstorming.txt
AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh verification-before-completion tests/skill-triggering/prompts/verification-before-completion.txt
AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh verification-before-completion tests/explicit-skill-requests/prompts/use-verification-before-completion.txt
AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh writing-plans tests/skill-triggering/prompts/writing-plans.txt
AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh writing-plans tests/explicit-skill-requests/prompts/use-writing-plans.txt
AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh requesting-code-review tests/skill-triggering/prompts/requesting-code-review.txt
AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh requesting-code-review tests/explicit-skill-requests/prompts/use-requesting-code-review.txt
```

Notes:

- On Windows + bash/WSL, the helper defaults to `cmd.exe /c codex.cmd` so the smoke test uses the working Windows Codex CLI instead of any broken Linux-side install.
- Codex smoke artifacts are written under repo-local `.tmp/aegis-tests/` so the Windows CLI can read the same files and working directories.
- Override the executable with `CODEX_CMD=/path/to/codex` if needed.
- The Codex smoke runner verifies skill loading by looking for `<skill>/SKILL.md` reads in the CLI transcript.
- This is a minimal host-native smoke matrix for the currently approved Wave 1 + Wave 2 skills. It does not replace the deeper Claude transcript checks used elsewhere in this document.

### OpenCode Compatibility Review Tests

For the current `Aegis` compatibility review, the OpenCode suite runs in two layers:

```bash
bash tests/opencode/run-tests.sh
bash tests/opencode/run-tests.sh --integration
```

Notes:

- The base suite validates plugin structure, bootstrap wiring, and isolated syntax checks without requiring a runnable OpenCode CLI.
- On Windows + bash/WSL, the helper can bridge to `cmd.exe /d /c opencode.cmd` so the suite uses the working Windows CLI instead of a broken Linux-side shim.
- The integration suite now has two environment gates:
  - CLI runnable probe: `opencode --version`
  - Runtime readiness probe: `opencode run --pure --model ${OPENCODE_TEST_MODEL:-opencode/big-pickle} --print-logs "hello"`
- If the binary exists on `PATH` but fails the version probe because the wrong platform package was installed, the integration suite skips with an explicit CLI blocker.
- If the CLI is runnable but the runtime probe fails because of model/provider/auth/credit issues, the integration suite also skips with an explicit environment blocker instead of reporting a plugin regression.
- The current OpenCode compatibility assertions are anchored to the native `skill` tool plus scope visibility:
  - global/personal skill visibility outside project context
  - project skill visibility inside project context
  - no duplicate-name override contract
- Treat a skipped integration run as a recorded compatibility blocker, not as evidence that the OpenCode runtime path passed.

### Phase 5 E2E Verification

The current Phase 5 E2E work adds a new `tests/e2e/` owner path:

```bash
bash tests/e2e/layer1-fast-check.sh --skip-host-smoke
bash tests/e2e/run-all.sh --bootstrap
bash tests/e2e/layer1-fast-check.sh
bash tests/e2e/layer2-behavior-check.sh
bash tests/e2e/run-all.sh --full --host-profile fast
```

Notes:

- `--bootstrap` verifies the completed Slice 1 boundary: authority alignment, boundary compliance, artifact-schema fixtures, and planned owner entrypoints.
- `layer1-fast-check.sh` now owns the active Slice 2 fast profile: boundary compliance, artifact schema fixtures, representative Codex natural + explicit smoke, OpenCode base suite, and plugin sync regression.
- `layer2-behavior-check.sh` now owns the active Slice 3 behavior check: fixture-backed transcript analysis, scenario contract matching, and with/without Aegis comparison.
- `layer3-scenario-check.sh` now owns the active Slice 4b scenario check: fixture-backed scenario orchestration plus cross-host consistency comparison.
- `run-all.sh --full --host-profile fast` is the current aggregate closeout command for the completed Phase 5 E2E verification slice.
- Full host smoke remains owned by the existing Codex / OpenCode suites and can be pulled into later E2E slices after the fast profile is stable.

### Requirements

- Must run from the **aegis plugin directory** (not from temp directories)
- Claude Code must be installed and available as `claude` command
- Local dev marketplace must be enabled: `"aegis@aegis-dev": true` in `~/.claude/settings.json`

## Integration Test: subagent-driven-development

### What It Tests

The integration test verifies the `subagent-driven-development` skill correctly:

1. **Plan Loading**: Reads the plan once at the beginning
2. **Full Task Text**: Provides complete task descriptions to subagents (doesn't make them read files)
3. **Self-Review**: Ensures subagents perform self-review before reporting
4. **Review Order**: Runs spec compliance review before code quality review
5. **Review Loops**: Uses review loops when issues are found
6. **Independent Verification**: Spec reviewer reads code independently, doesn't trust implementer reports

### How It Works

1. **Setup**: Creates a temporary Node.js project with a minimal implementation plan
2. **Execution**: Runs Claude Code in headless mode with the skill
3. **Verification**: Parses the session transcript (`.jsonl` file) to verify:
   - Skill tool was invoked
   - Subagents were dispatched (Task tool)
   - TodoWrite was used for tracking
   - Implementation files were created
   - Tests pass
   - Git commits show proper workflow
4. **Token Analysis**: Shows token usage breakdown by subagent

### Test Output

```
========================================
 Integration Test: subagent-driven-development
========================================

Test project: /tmp/tmp.xyz123

=== Verification Tests ===

Test 1: Skill tool invoked...
  [PASS] subagent-driven-development skill was invoked

Test 2: Subagents dispatched...
  [PASS] 7 subagents dispatched

Test 3: Task tracking...
  [PASS] TodoWrite used 5 time(s)

Test 6: Implementation verification...
  [PASS] src/math.js created
  [PASS] add function exists
  [PASS] multiply function exists
  [PASS] test/math.test.js created
  [PASS] Tests pass

Test 7: Git commit history...
  [PASS] Multiple commits created (3 total)

Test 8: No extra features added...
  [PASS] No extra features added

=========================================
 Token Usage Analysis
=========================================

Usage Breakdown:
----------------------------------------------------------------------------------------------------
Agent           Description                          Msgs      Input     Output      Cache     Cost
----------------------------------------------------------------------------------------------------
main            Main session (coordinator)             34         27      3,996  1,213,703 $   4.09
3380c209        implementing Task 1: Create Add Function     1          2        787     24,989 $   0.09
34b00fde        implementing Task 2: Create Multiply Function     1          4        644     25,114 $   0.09
3801a732        reviewing whether an implementation matches...   1          5        703     25,742 $   0.09
4c142934        doing a final code review...                    1          6        854     25,319 $   0.09
5f017a42        a code reviewer. Review Task 2...               1          6        504     22,949 $   0.08
a6b7fbe4        a code reviewer. Review Task 1...               1          6        515     22,534 $   0.08
f15837c0        reviewing whether an implementation matches...   1          6        416     22,485 $   0.07
----------------------------------------------------------------------------------------------------

TOTALS:
  Total messages:         41
  Input tokens:           62
  Output tokens:          8,419
  Cache creation tokens:  132,742
  Cache read tokens:      1,382,835

  Total input (incl cache): 1,515,639
  Total tokens:             1,524,058

  Estimated cost: $4.67
  (at $3/$15 per M tokens for input/output)

========================================
 Test Summary
========================================

STATUS: PASSED
```

## Token Analysis Tool

### Usage

Analyze token usage from any Claude Code session:

```bash
python3 tests/claude-code/analyze-token-usage.py ~/.claude/projects/<project-dir>/<session-id>.jsonl
```

### Finding Session Files

Session transcripts are stored in `~/.claude/projects/` with the working directory path encoded:

```bash
# Example for /Users/jesse/Documents/GitHub/aegis/aegis
SESSION_DIR="$HOME/.claude/projects/-Users-jesse-Documents-GitHub-aegis-aegis"

# Find recent sessions
ls -lt "$SESSION_DIR"/*.jsonl | head -5
```

Transcript lookup is an explicit testing operation, not a default Aegis runtime
behavior. Keep every transcript search bounded by project directory, timestamp,
filename, or result limit. Do not run broad searches over `~/.claude/projects`,
`.codex/sessions`, `history.jsonl`, or large log directories unless the test is
specifically about transcript discovery or token analysis.

### What It Shows

- **Main session usage**: Token usage by the coordinator (you or main Claude instance)
- **Per-subagent breakdown**: Each Task invocation with:
  - Agent ID
  - Description (extracted from prompt)
  - Message count
  - Input/output tokens
  - Cache usage
  - Estimated cost
- **Totals**: Overall token usage and cost estimate

### Understanding the Output

- **High cache reads**: Good - means prompt caching is working
- **High input tokens on main**: Expected - coordinator has full context
- **Similar costs per subagent**: Expected - each gets similar task complexity
- **Cost per task**: Typical range is $0.05-$0.15 per subagent depending on task

## Troubleshooting

### Skills Not Loading

**Problem**: Skill not found when running headless tests

**Solutions**:
1. Ensure you're running FROM the aegis directory: `cd /path/to/aegis && tests/...`
2. Check `~/.claude/settings.json` has `"aegis@aegis-dev": true` in `enabledPlugins`
3. Verify skill exists in `skills/` directory

### Permission Errors

**Problem**: Claude blocked from writing files or accessing directories

**Solutions**:
1. Use `--permission-mode bypassPermissions` flag
2. Use `--add-dir /path/to/temp/dir` to grant access to test directories
3. Check file permissions on test directories

### Test Timeouts

**Problem**: Test takes too long and times out

**Solutions**:
1. Increase timeout: `timeout 1800 claude ...` (30 minutes)
2. Check for infinite loops in skill logic
3. Review subagent task complexity

### Session File Not Found

**Problem**: Can't find session transcript after test run

**Solutions**:
1. Check the correct project directory in `~/.claude/projects/`
2. Use a bounded search such as `find "$SESSION_DIR" -name "*.jsonl" -mmin -60 | head -5`
3. Verify test actually ran (check for errors in test output)

## Writing New Integration Tests

### Template

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/test-helpers.sh"

# Create test project
TEST_PROJECT=$(create_test_project)
trap "cleanup_test_project $TEST_PROJECT" EXIT

# Set up test files...
cd "$TEST_PROJECT"

# Run Claude with skill
PROMPT="Your test prompt here"
cd "$SCRIPT_DIR/../.." && timeout 1800 claude -p "$PROMPT" \
  --allowed-tools=all \
  --add-dir "$TEST_PROJECT" \
  --permission-mode bypassPermissions \
  2>&1 | tee output.txt

# Find and analyze session
WORKING_DIR_ESCAPED=$(echo "$SCRIPT_DIR/../.." | sed 's/\\//-/g' | sed 's/^-//')
SESSION_DIR="$HOME/.claude/projects/$WORKING_DIR_ESCAPED"
SESSION_FILE=$(find "$SESSION_DIR" -name "*.jsonl" -type f -mmin -60 | sort -r | head -1)

# Verify behavior by parsing session transcript
if grep -q '"name":"Skill".*"skill":"your-skill-name"' "$SESSION_FILE"; then
    echo "[PASS] Skill was invoked"
fi

# Show token analysis
python3 "$SCRIPT_DIR/analyze-token-usage.py" "$SESSION_FILE"
```

### Best Practices

1. **Always cleanup**: Use trap to cleanup temp directories
2. **Parse transcripts**: Don't grep user-facing output - parse the `.jsonl` session file
3. **Grant permissions**: Use `--permission-mode bypassPermissions` and `--add-dir`
4. **Run from plugin dir**: Skills only load when running from the aegis directory
5. **Show token usage**: Always include token analysis for cost visibility
6. **Test real behavior**: Verify actual files created, tests passing, commits made

## Session Transcript Format

Session transcripts are JSONL (JSON Lines) files where each line is a JSON object representing a message or tool result.

### Key Fields

```json
{
  "type": "assistant",
  "message": {
    "content": [...],
    "usage": {
      "input_tokens": 27,
      "output_tokens": 3996,
      "cache_read_input_tokens": 1213703
    }
  }
}
```

### Tool Results

```json
{
  "type": "user",
  "toolUseResult": {
    "agentId": "3380c209",
    "usage": {
      "input_tokens": 2,
      "output_tokens": 787,
      "cache_read_input_tokens": 24989
    },
    "prompt": "You are implementing Task 1...",
    "content": [{"type": "text", "text": "..."}]
  }
}
```

The `agentId` field links to subagent sessions, and the `usage` field contains token usage for that specific subagent invocation.
