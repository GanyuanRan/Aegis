# Testing Aegis Skills

This document describes how to test Aegis skills, particularly the integration tests for complex skills like `subagent-driven-development`.

This page is an execution guide, not the authority source for current scope or release status.
For the current `Aegis Method Pack` authority order, release gate, and known limitations, read:

- `docs/current/README.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`

For the repository test surface split, read:

- `tests/README.md`

Tracked suites under `tests/` are the public quality verification surface unless
their README marks them as optional host integration checks. Development-only or
machine-specific test cases belong in `tests/local/`; that directory is ignored
by git except for its README and must not be used by public CI or release gates.

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

### Codex TDD Route Smoke

The TDD route smoke checks the structured route decision rather than treating a
skill-load marker as proof that `auto` selected the correct discipline. Run it
from the release-candidate checkout:

```bash
AEGIS_TDD_ROUTE_REPETITIONS=3 bash tests/skill-triggering/run-tdd-route-tests.sh
```

It covers auto/high-risk, auto/tiny, off/high-risk, and off/explicit-strict
cases. Each case uses a temporary project `AGENTS.md` projection plus a
project-local copy of the current checkout's minimum relevant skills, and
prohibits implementation writes. This prevents a stale global install from
standing in for the release candidate. It is an environment-bound model smoke:
authentication, the Codex version, and the selected model must be reported with
the result. Static CI remains responsible for the portable policy and
projection contracts.

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

### Antigravity CLI Closeout Tests

For the current Google-host closeout slice, the Antigravity suite runs in two
layers:

```bash
bash tests/antigravity/run-tests.sh
bash tests/antigravity/run-tests.sh --integration
```

Notes:

- The base suite validates the current Antigravity doc/contract surface and the
  host-scoped updater registration/readback shape without requiring a runnable
  `agy` CLI on the machine.
- The integration suite is intentionally environment-bound and currently uses
  two gates:
  - CLI runnable probe: `agy --version`
  - CLI plugin surface probe: `agy plugin list`
- If `agy` is not on `PATH`, the suite skips with an explicit CLI blocker.
- If the CLI exists but the plugin surface cannot be exercised because of local
  auth/runtime/profile conditions, the suite skips with an explicit environment
  blocker instead of reporting an Aegis regression.
- If the CLI is runnable but no longer exposes the documented plugin surface,
  the integration suite should fail as a host-contract regression.
- Use `ANTIGRAVITY_CMD=/path/to/agy` when the executable is not directly on
  `PATH`.
- The current suite is CLI-first only. `Antigravity IDE` and `Antigravity App`
  remain structural target surfaces until they have their own fresh host smoke
  slice.

### Kimi Code Automatic-Routing Tests

The Kimi suite separates portable contract checks from credentialed model
routing:

```bash
bash tests/kimi-code/run-tests.sh
bash tests/kimi-code/run-tests.sh --integration
bash tests/kimi-code/run-live-smoke.sh
```

The base lane validates Kimi-safe skill metadata, the plugin manifest,
session-start wiring, doctor profiles, duplicate-exposure rejection, and the
public host boundary without requiring Kimi Code. The integration lane requires
an installed Kimi CLI and exactly one enabled Aegis plugin, then verifies the
managed plugin root through `aegis-doctor.py --host-profile kimi-code-auto`.

The live lane runs five non-mutating prompts through `kimi -p` with
`--output-format stream-json`, checks positive and negative Skill-tool routing,
and covers a resumed session. Missing CLI, login, provider credentials, or
third-party trust confirmation is environment-bound evidence, not a passing
live-host verdict.

### Grok Build Structural Host Tests

The Grok Build boundary check validates the native skill root, updater
defaults, config example, duplicate-exposure guard, public compatibility
wording, and release-surface links without changing the current user's Grok
profile:

```bash
bash tests/e2e/grok-build-host-boundary-check.sh
python tests/helpers/test_aegis_update.py -k grok
```

For an environment-bound discovery readback on a machine with Grok Build:

```bash
grok --version
grok inspect --json
```

`grok inspect --json` proves what the current Grok profile can enumerate. It
does not by itself prove a clean install, live skill triggering, or
release-level host closeout. Check that every Aegis skill name has one
canonical source; native Grok skills, `[skills] paths`, shared Agent Skills,
and Claude-compatible plugins can otherwise expose duplicate Aegis copies.

### DeepSeek Harness Bundle Host Tests

The deterministic DeepSeek Harness suite validates the official host identity,
root `dsh.bundle.patch` declaration, thin Cordis adapter, package-owned skill
root, deferred native lifecycle bootstrap across startup/resume/clear/compact
(armed at each boundary, injected once after the session's first durable
promotion signal), subagent and explicit-mode exclusions, explicit direct-child
compatibility path, duplicate-exposure guard, developer-preview boundary, and
public release links without changing the current user's DSH profile:

```bash
bash tests/deepseek-harness/run-tests.sh
python tests/helpers/test_aegis_update.py -k deepseek_harness
```

The opt-in integration lane requires local `dsh` and `pnpm`. It creates an
isolated temporary `DSH_HOME`, installs the current checkout into a Web profile,
checks dependency/bundle reconciliation, dump-config composition and module
loading, then removes the bundle:

```bash
bash tests/deepseek-harness/run-tests.sh --integration
```

These checks prove method-pack bundle installation, module loading, and
deterministic lifecycle-entry wiring only. A fresh Standard-mode session must
still prove catalog discovery, native task-specific `skill` loading,
representative routing versus `Route: fast-path`, false-positive behavior,
session refresh, and update behavior before DeepSeek Harness receives a
release-level host verdict.

### Workspace Helper ADR Lifecycle Tests

The workspace helper ADR lifecycle is covered by the existing target-project
e2e suite:

```bash
bash tests/e2e/aegis-workspace-check.sh
```

Notes:

- The suite verifies `aegis-workspace.py new-adr`, `amend-adr`, and
  `supersede-adr` against a temporary target project root.
- It checks ADR numbering, supersession markers, `INDEX.md` coverage, and
  structural `check --root` validation.
- It also preserves the repository boundary that the Aegis method-pack
  checkout itself must not ship a live `docs/aegis/` workspace.

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
- `goal-framing-check.sh` is part of Layer 1 and guards the opt-in goal entry,
  optional `TaskIntentDraft` goal fields, `SubagentContextPacket` shape, and
  no-file default policy.
- Full host smoke remains owned by the existing Codex / OpenCode suites and can be pulled into later E2E slices after the fast profile is stable.

### Controlled Replay And Live Capture

Controlled replay keeps benchmark samples off local user projects:

```bash
bash tests/e2e/controlled-replay-check.sh
```

This copies seeded fixture projects into repo-local `.tmp/` workspaces,
analyzes captured transcripts, and checks with/without Aegis contrast.

Live replay capture is opt-in and environment-bound:

```bash
bash tests/e2e/live-replay-capture.sh --sample change-necessity-before-edit --dry-run
AEGIS_LIVE_REPLAY=1 AEGIS_TEST_CLI=codex bash tests/e2e/live-replay-capture.sh --sample change-necessity-before-edit
```

The dry run only prepares the temporary workspace. The live run invokes the
selected host, captures the raw log, normalizes it for
`tests/e2e/analyze-transcript.sh`, and writes the summary under `.tmp/`.

The live capture path currently captures one `aegis-auto` arm at a time. It
does not create a trustworthy no-Aegis baseline automatically; that requires
explicit isolated host configuration and plugin discovery boundaries.

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
