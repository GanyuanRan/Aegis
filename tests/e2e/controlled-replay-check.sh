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

echo "=== Controlled Replay Check ==="
REPORT_PATH=".tmp/e2e-controlled-replay-report/report.json"
"${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest tests/e2e/fixtures/replay-samples.json \
    --workspace-root .tmp/e2e-controlled-replay \
    --report-json "$REPORT_PATH"

"${PYTHON_CMD[@]}" - "$REPORT_PATH" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["version"] == 1
assert report["reportType"] == "controlled-replay-advisory"
assert report["authorityBoundary"] == "advisory-method-pack-evidence-not-completion-authority"
assert report["evaluationTier"] == "controlled-replay"
assert report["datasetPartition"] == "development"
assert report["runCount"] == 1
assert report["scoreSource"] == "static-transcript-contract-analysis"
assert report["promotionStatus"] == "not-evaluated"
assert report["overallPass"] is True
assert report["failures"] == []
assert set(report["unknowns"]) == {
    "tokens",
    "cost",
    "variance",
    "held-out-evidence",
    "blind-human-review-evidence",
}
assert len(report["samples"]) == 3

for sample in report["samples"]:
    assert sample["evaluationTier"] == "controlled-replay"
    assert sample["datasetPartition"] == "development"
    assert sample["overallPass"] is True
    assert sample["failures"] == []
    assert len(sample["arms"]) == 2
    for arm in sample["arms"]:
        assert isinstance(arm["actualContractPass"], bool)
        assert isinstance(arm["expectedContractPass"], bool)
        assert arm["actualContractPass"] == arm["expectedContractPass"]
        assert isinstance(arm["score"], int)
    assert len(sample["comparisons"]) == 1
    comparison = sample["comparisons"][0]
    assert comparison["pass"] is True
    assert comparison["scoreDelta"] > 0

forbidden_evidence_keys = {
    "tokens",
    "cost",
    "variance",
    "heldOutEvidence",
    "blindReviewEvidence",
    "blindHumanReviewEvidence",
}

def assert_no_fabricated_fields(value):
    if isinstance(value, dict):
        assert forbidden_evidence_keys.isdisjoint(value)
        for nested in value.values():
            assert_no_fabricated_fields(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_fabricated_fields(nested)

assert_no_fabricated_fields(report)
print("  [PASS] structured controlled replay report preserves tier, score, unknown, and advisory boundaries")
PY

ROOT_SENTINEL="$(mktemp "$REPO_ROOT/.tmp/controlled-replay-root-sentinel.XXXXXX")"
if "${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest tests/e2e/fixtures/replay-samples.json \
    --workspace-root .tmp >/dev/null 2>&1; then
    echo "  [FAIL] repo .tmp root was accepted as workspace root"
    exit 1
elif [[ ! -f "$ROOT_SENTINEL" ]]; then
    echo "  [FAIL] rejecting repo .tmp root removed an existing sentinel"
    exit 1
else
    echo "  [PASS] repo .tmp root was rejected without deleting existing contents"
fi
rm -f -- "$ROOT_SENTINEL"

if "${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest tests/e2e/fixtures/replay-samples.json \
    --workspace-root .tmp/e2e-controlled-replay \
    --report-json tests/e2e/controlled-replay-report.json >/dev/null 2>&1; then
    echo "  [FAIL] report path outside repo .tmp was accepted"
    exit 1
else
    echo "  [PASS] report path outside repo .tmp was rejected"
fi

FAILURE_ROOT=".tmp/e2e-controlled-replay-failure"
FAILURE_MANIFEST="$FAILURE_ROOT/replay-samples.json"
FAILURE_REPORT="$FAILURE_ROOT/report.json"
mkdir -p "$FAILURE_ROOT"
"${PYTHON_CMD[@]}" - tests/e2e/fixtures/replay-samples.json "$FAILURE_MANIFEST" <<'PY'
import json
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])
manifest = json.loads(source.read_text(encoding="utf-8"))
sample = manifest["samples"][0]
baseline_arm = next(arm for arm in sample["arms"] if arm["id"] == "baseline-no-aegis")
empty_behavior = target.parent / "empty-expected-behavior.json"
empty_artifacts = target.parent / "empty-expected-artifacts.json"
empty_behavior.write_text("{}\n", encoding="utf-8")
empty_artifacts.write_text("{}\n", encoding="utf-8")
baseline_arm["expectedBehaviorPath"] = empty_behavior.as_posix()
baseline_arm["expectedArtifactsPath"] = empty_artifacts.as_posix()
target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY

if "${PYTHON_CMD[@]}" tests/helpers/run_controlled_replay_samples.py \
    --manifest "$FAILURE_MANIFEST" \
    --workspace-root "$FAILURE_ROOT/workspaces" \
    --report-json "$FAILURE_REPORT" >"$FAILURE_ROOT/run.log" 2>&1; then
    echo "  [FAIL] controlled replay failure fixture unexpectedly passed"
    exit 1
fi

"${PYTHON_CMD[@]}" - "$FAILURE_REPORT" <<'PY'
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert report["overallPass"] is False
assert report["failures"]
sample = next(item for item in report["samples"] if item["id"] == "change-necessity-before-edit")
assert sample["overallPass"] is False
assert sample["failures"]
arm = next(item for item in sample["arms"] if item["id"] == "baseline-no-aegis")
assert arm["expectedContractPass"] is False
assert arm["actualContractPass"] is True
assert sample["comparisons"][0]["pass"] is True
assert any(failure["kind"] == "arm-contract-mismatch" for failure in sample["failures"])
assert any(failure["kind"] == "arm-contract-mismatch" for failure in report["failures"])
print("  [PASS] arm mismatch keeps sample/report failed even when comparison passes")
PY

echo ""
echo "Controlled replay check passed."
