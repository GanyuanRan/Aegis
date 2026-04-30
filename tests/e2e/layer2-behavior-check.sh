#!/usr/bin/env bash
set -euo pipefail

PLANNED_EXIT=90
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$SCRIPT_DIR/../../.tmp/e2e-layer2"

python_cmd() {
    if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
        python3 "$@"
        return
    fi

    if command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
        py -3 "$@"
        return
    fi

    python "$@"
}

case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--bootstrap-status]"
        exit 0
        ;;
    --bootstrap-status)
        echo "PLANNED: Layer 2 behavior validation is outside the bootstrap-only boundary."
        exit $PLANNED_EXIT
        ;;
esac

mkdir -p "$TMP_DIR"

passed=0
failed=0

run_analysis() {
    local label="$1"
    local transcript="$2"
    local expected_behavior="$3"
    local expected_artifacts="$4"
    local summary_json="$5"

    echo "Running analysis: $label"
    if bash "$SCRIPT_DIR/analyze-transcript.sh" \
        --transcript "$transcript" \
        --expected-behavior "$expected_behavior" \
        --expected-artifacts "$expected_artifacts" \
        --summary-json "$summary_json"; then
        echo "  [PASS] $label"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $label"
        failed=$((failed + 1))
    fi
    echo ""
}

capture_analysis() {
    local label="$1"
    local transcript="$2"
    local expected_behavior="$3"
    local expected_artifacts="$4"
    local summary_json="$5"

    echo "Capturing contrast transcript: $label"
    if bash "$SCRIPT_DIR/analyze-transcript.sh" \
        --transcript "$transcript" \
        --expected-behavior "$expected_behavior" \
        --expected-artifacts "$expected_artifacts" \
        --summary-json "$summary_json" \
        --quiet; then
        echo "  [INFO] contrast transcript unexpectedly satisfied the full behavior contract"
    else
        echo "  [INFO] contrast transcript recorded for with/without comparison"
    fi
    echo ""
}

run_comparison() {
    local label="$1"
    local with_summary="$2"
    local without_summary="$3"

    echo "Running comparison: $label"
    if python_cmd - "$with_summary" "$without_summary" <<'PY'
import json
import sys
from pathlib import Path

with_summary = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
without_summary = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

with_score = len(with_summary["matchedSkillSequence"]) + len(with_summary["requiredArtifactsPresent"])
without_score = len(without_summary["matchedSkillSequence"]) + len(without_summary["requiredArtifactsPresent"])

without_weaker = (
    not without_summary["skillSequencePass"]
    or len(with_summary["matchedSkillSequence"]) > len(without_summary["matchedSkillSequence"])
    or len(with_summary["requiredArtifactsPresent"]) > len(without_summary["requiredArtifactsPresent"])
)

comparison_pass = with_summary["overallPass"] and with_score > without_score and without_weaker

print(f"With Aegis score: {with_score}")
print(f"Without Aegis score: {without_score}")
print(f"Without Aegis weaker: {'yes' if without_weaker else 'no'}")
print(f"COMPARISON: {'PASS' if comparison_pass else 'FAIL'}")

sys.exit(0 if comparison_pass else 1)
PY
    then
        echo "  [PASS] $label"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $label"
        failed=$((failed + 1))
    fi
    echo ""
}

run_analysis \
    "scenario A with Aegis behavior" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-A-new-feature.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-artifacts.json" \
    "$TMP_DIR/scenario-A-with-aegis.json"

capture_analysis \
    "scenario A without Aegis baseline" \
    "$SCRIPT_DIR/baselines/without-aegis/scenario-A-new-feature.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-artifacts.json" \
    "$TMP_DIR/scenario-A-without-aegis.json"

run_comparison \
    "scenario A with/without comparison" \
    "$TMP_DIR/scenario-A-with-aegis.json" \
    "$TMP_DIR/scenario-A-without-aegis.json"

run_analysis \
    "scenario B with Aegis behavior" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-B-bug-fix.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-artifacts.json" \
    "$TMP_DIR/scenario-B-with-aegis.json"

capture_analysis \
    "scenario B without Aegis baseline" \
    "$SCRIPT_DIR/baselines/without-aegis/scenario-B-bug-fix.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-artifacts.json" \
    "$TMP_DIR/scenario-B-without-aegis.json"

run_comparison \
    "scenario B with/without comparison" \
    "$TMP_DIR/scenario-B-with-aegis.json" \
    "$TMP_DIR/scenario-B-without-aegis.json"

echo "Passed: $passed"
echo "Failed: $failed"

if [[ $failed -gt 0 ]]; then
    exit 1
fi

exit 0
