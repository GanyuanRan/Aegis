#!/usr/bin/env bash
set -euo pipefail

PLANNED_EXIT=90
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$SCRIPT_DIR/../../.tmp/e2e-layer3"

case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [--bootstrap-status]"
        exit 0
        ;;
    --bootstrap-status)
        echo "PLANNED: Layer 3 scenario validation remains outside the bootstrap-only boundary."
        exit $PLANNED_EXIT
        ;;
esac

mkdir -p "$TMP_DIR"

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

passed=0
failed=0

run_scenario() {
    local scenario_name="$1"
    local transcript="$2"
    local expected_behavior="$3"
    local expected_artifacts="$4"
    local summary_json="$5"

    echo "Running scenario: $scenario_name"
    if bash "$SCRIPT_DIR/analyze-transcript.sh" \
        --transcript "$transcript" \
        --expected-behavior "$expected_behavior" \
        --expected-artifacts "$expected_artifacts" \
        --summary-json "$summary_json"; then
        echo "  [PASS] $scenario_name"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $scenario_name"
        failed=$((failed + 1))
    fi
    echo ""
}

run_environment_dependent_comparison() {
    local scenario_name="$1"
    local host_a_summary="$2"
    local host_b_summary="$3"

    echo "Running cross-host comparison: $scenario_name"
    if python_cmd - "$host_a_summary" "$host_b_summary" <<'PY'
import json
import sys
from pathlib import Path

host_a = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
host_b = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))

shared_pass = host_a["overallPass"] and host_b["overallPass"]
same_sequence = host_a["matchedSkillSequence"] == host_b["matchedSkillSequence"]
same_required_artifacts = host_a["requiredArtifactsPresent"] == host_b["requiredArtifactsPresent"]

comparison_pass = shared_pass and same_sequence and same_required_artifacts

print(f"Host A overall: {'PASS' if host_a['overallPass'] else 'FAIL'}")
print(f"Host B overall: {'PASS' if host_b['overallPass'] else 'FAIL'}")
print(f"Matched sequence equal: {'yes' if same_sequence else 'no'}")
print(f"Required artifacts equal: {'yes' if same_required_artifacts else 'no'}")
print(f"COMPARISON: {'PASS' if comparison_pass else 'FAIL'}")

sys.exit(0 if comparison_pass else 1)
PY
    then
        echo "  [PASS] $scenario_name"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $scenario_name"
        failed=$((failed + 1))
    fi
    echo ""
}

run_scenario \
    "scenario A new feature" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-A-new-feature.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-A-new-feature/expected-artifacts.json" \
    "$TMP_DIR/scenario-A.json"

run_scenario \
    "scenario B bug fix" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-B-bug-fix.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-B-bug-fix/expected-artifacts.json" \
    "$TMP_DIR/scenario-B.json"

run_scenario \
    "scenario C cross-host codex fixture" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-C-cross-host-codex.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-C-cross-host/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-C-cross-host/expected-artifacts.json" \
    "$TMP_DIR/scenario-C-codex.json"

run_scenario \
    "scenario C cross-host claude fixture" \
    "$SCRIPT_DIR/fixtures/transcripts/with-aegis/scenario-C-cross-host-claude.jsonl" \
    "$SCRIPT_DIR/scenarios/scenario-C-cross-host/expected-behavior.json" \
    "$SCRIPT_DIR/scenarios/scenario-C-cross-host/expected-artifacts.json" \
    "$TMP_DIR/scenario-C-claude.json"

run_environment_dependent_comparison \
    "scenario C cross-host comparison" \
    "$TMP_DIR/scenario-C-codex.json" \
    "$TMP_DIR/scenario-C-claude.json"

echo "Passed: $passed"
echo "Failed: $failed"

if [[ $failed -gt 0 ]]; then
    exit 1
fi

exit 0
