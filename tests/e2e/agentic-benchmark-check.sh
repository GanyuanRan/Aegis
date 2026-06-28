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

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

echo "=== Agentic Benchmark Check ==="

baseline="docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md"
current_index="docs/current/README.md"
workflow_quality="docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md"
matrix="tests/e2e/fixtures/agentic-benchmark-matrix.json"
replay_manifest="tests/e2e/fixtures/replay-samples.json"

if [[ -f "$baseline" ]]; then
    pass "agentic benchmark baseline exists"
else
    fail "agentic benchmark baseline exists"
fi

if [[ -f "$matrix" ]]; then
    pass "agentic benchmark matrix exists"
else
    fail "agentic benchmark matrix exists"
fi

if [[ -f "$replay_manifest" ]]; then
    pass "controlled replay manifest exists"
else
    fail "controlled replay manifest exists"
fi

assert_contains "$current_index" "AEGIS_AGENTIC_BENCHMARK_BASELINE.md" \
    "current docs index lists agentic benchmark baseline"
assert_contains "$workflow_quality" "agentic benchmark" \
    "workflow quality baseline references agentic benchmark"
assert_contains "$baseline" "baseline-no-aegis" \
    "benchmark baseline defines no-Aegis arm"
assert_contains "$baseline" "aegis-auto" \
    "benchmark baseline defines Aegis auto arm"
assert_contains "$baseline" "route-correctness" \
    "benchmark baseline prioritizes route correctness"
assert_contains "$baseline" "false-completion-rate" \
    "benchmark baseline measures false completion"
assert_contains "$baseline" "owner-fix-accuracy" \
    "benchmark baseline measures owner fix accuracy"
assert_contains "$baseline" "retirement-track-coverage" \
    "benchmark baseline measures retirement coverage"
assert_contains "$baseline" "workspace-laziness" \
    "benchmark baseline measures workspace laziness"
assert_contains "$baseline" "isolated workspace and configuration boundary|isolate host config" \
    "benchmark baseline requires run isolation"
assert_contains "$baseline" "must not say" \
    "benchmark baseline forbids overclaiming"
assert_contains "$baseline" "completion authority" \
    "benchmark baseline preserves completion authority boundary"
assert_contains "$baseline" "Controlled Replay Samples" \
    "benchmark baseline describes controlled replay sample layer"
assert_contains "$baseline" "does not run a live host agent" \
    "benchmark baseline keeps replay separate from live host execution"
assert_contains "$baseline" "Live Replay Capture" \
    "benchmark baseline describes opt-in live replay capture"
assert_contains "$baseline" "AEGIS_LIVE_REPLAY=1" \
    "benchmark baseline gates live capture behind explicit opt-in"
assert_contains "$baseline" "must not fabricate a no-Aegis baseline" \
    "benchmark baseline forbids fabricated live no-Aegis baseline"

"${PYTHON_CMD[@]}" tests/helpers/validate_agentic_benchmark_matrix.py "$matrix"
"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py --validate-only

if (( failures > 0 )); then
    echo ""
    echo "Agentic benchmark check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Agentic benchmark check passed."
