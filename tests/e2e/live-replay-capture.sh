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

SAMPLE_ID=""
ARM_ID="aegis-auto"
HOST="${AEGIS_TEST_CLI:-codex}"
MAX_TURNS="${AEGIS_LIVE_REPLAY_MAX_TURNS:-3}"
TIMESTAMP="$(date +%s)"
WORKSPACE_ROOT="${AEGIS_LIVE_REPLAY_ROOT:-.tmp/e2e-live-replay/${TIMESTAMP}}"
DRY_RUN=0
REQUIRE_PASS=0

usage() {
    cat <<'EOF'
Usage: live-replay-capture.sh --sample <sample-id> [--arm aegis-auto] [--host codex|claude] [--dry-run] [--require-pass]

Environment:
  AEGIS_LIVE_REPLAY=1       Required for real host execution.
  AEGIS_TEST_CLI=codex      Default host when --host is omitted.
  AEGIS_LIVE_REPLAY_ROOT    Optional repo-local .tmp output root.
  CODEX_CMD / CLAUDE_CMD    Optional host command overrides.

This script captures one live host arm into a temporary fixture workspace. It
does not create a no-Aegis baseline automatically.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --sample)
            SAMPLE_ID="$2"
            shift 2
            ;;
        --arm)
            ARM_ID="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --workspace-root)
            WORKSPACE_ROOT="$2"
            shift 2
            ;;
        --max-turns)
            MAX_TURNS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --require-pass)
            REQUIRE_PASS=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 2
            ;;
    esac
done

if [[ -z "$SAMPLE_ID" ]]; then
    echo "ERROR: --sample is required"
    usage
    exit 2
fi

if [[ "$HOST" != "codex" && "$HOST" != "claude" ]]; then
    echo "ERROR: --host must be codex or claude"
    exit 2
fi

if [[ "$ARM_ID" != "aegis-auto" ]]; then
    echo "ERROR: live replay capture currently supports only aegis-auto."
    echo "Reason: a trustworthy no-Aegis arm requires isolated host config that this script does not create yet."
    exit 64
fi

mkdir -p "$WORKSPACE_ROOT"
PREP_JSON_PATH="$WORKSPACE_ROOT/prepared-${SAMPLE_ID}-${ARM_ID}.json"

"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest tests/e2e/fixtures/replay-samples.json \
    --workspace-root "$WORKSPACE_ROOT" \
    --prepare-live-run \
    --sample "$SAMPLE_ID" \
    --arm "$ARM_ID" > "$PREP_JSON_PATH"

json_value() {
    "${PYTHON_CMD[@]}" - "$PREP_JSON_PATH" "$1" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data[sys.argv[2]])
PY
}

PROMPT_PATH="$(json_value promptPath)"
WORKSPACE_PATH="$(json_value workspacePath)"
RAW_LOG_PATH="$(json_value rawLogPath)"
TRANSCRIPT_PATH="$(json_value normalizedTranscriptPath)"
SUMMARY_PATH="$(json_value summaryPath)"
EXPECTED_BEHAVIOR_PATH="$(json_value expectedBehaviorPath)"
EXPECTED_ARTIFACTS_PATH="$(json_value expectedArtifactsPath)"
METADATA_PATH="$(json_value metadataPath)"

echo "=== Live Replay Capture ==="
echo "Sample: $SAMPLE_ID"
echo "Arm: $ARM_ID"
echo "Host: $HOST"
echo "Workspace: $WORKSPACE_PATH"
echo "Metadata: $METADATA_PATH"

if [[ "$DRY_RUN" == "1" ]]; then
    echo "Dry run: prepared live replay workspace without invoking host CLI."
    exit 0
fi

if [[ "${AEGIS_LIVE_REPLAY:-0}" != "1" ]]; then
    echo "SKIP: set AEGIS_LIVE_REPLAY=1 to run a live host replay."
    echo "Prepared workspace remains at: $WORKSPACE_PATH"
    exit 90
fi

PROMPT="$(cat "$PROMPT_PATH")"
mkdir -p "$(dirname "$RAW_LOG_PATH")"

case "$HOST" in
    codex)
        CODEX_SMOKE_SUFFIX="${CODEX_SMOKE_SUFFIX-}"
        export CODEX_SMOKE_SUFFIX
        source "$REPO_ROOT/tests/helpers/codex-cli.sh"
        echo "Running Codex live replay..."
        run_codex_exec_capture "$PROMPT" "$WORKSPACE_PATH" "$RAW_LOG_PATH"
        ;;
    claude)
        source "$REPO_ROOT/tests/helpers/claude-cli.sh"
        echo "Running Claude live replay..."
        run_claude_stream_json_with_plugin_dir "$PROMPT" "$REPO_ROOT" "$MAX_TURNS" "$RAW_LOG_PATH"
        ;;
esac

"${PYTHON_CMD[@]}" tests/helpers/normalize_live_replay_log.py \
    --host "$HOST" \
    --raw-log "$RAW_LOG_PATH" \
    --prompt "$PROMPT_PATH" \
    --transcript "$TRANSCRIPT_PATH"

set +e
bash "$SCRIPT_DIR/analyze-transcript.sh" \
    --transcript "$TRANSCRIPT_PATH" \
    --expected-behavior "$EXPECTED_BEHAVIOR_PATH" \
    --expected-artifacts "$EXPECTED_ARTIFACTS_PATH" \
    --summary-json "$SUMMARY_PATH"
ANALYSIS_STATUS=$?
set -e

echo "$ANALYSIS_STATUS" > "$(dirname "$SUMMARY_PATH")/analysis-exit-code.txt"
echo "Raw log: $RAW_LOG_PATH"
echo "Normalized transcript: $TRANSCRIPT_PATH"
echo "Summary: $SUMMARY_PATH"

if [[ "$ANALYSIS_STATUS" -ne 0 && "$REQUIRE_PASS" == "1" ]]; then
    echo "Live replay behavior contract failed."
    exit "$ANALYSIS_STATUS"
fi

if [[ "$ANALYSIS_STATUS" -ne 0 ]]; then
    echo "Live replay captured, but behavior contract did not pass. Treat this as environment-bound evidence."
    exit 0
fi

echo "Live replay captured and behavior contract passed."
