#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

SCENARIO_DIR="$SCRIPT_DIR/scenarios/scenario-D-interrupted-long-task"
ARTIFACT_DIR="$SCRIPT_DIR/fixtures/artifacts"

required_files=(
    "$SCENARIO_DIR/README.md"
    "$SCENARIO_DIR/prompt.txt"
    "$SCENARIO_DIR/expected-artifacts.json"
    "$SCENARIO_DIR/expected-behavior.json"
    "$ARTIFACT_DIR/baseline-usage-draft.sample.json"
    "$ARTIFACT_DIR/todo-checkpoint-draft.sample.json"
    "$ARTIFACT_DIR/resume-state-hint.sample.json"
    "$ARTIFACT_DIR/drift-check-draft.sample.json"
    "skills/long-task-continuation/SKILL.md"
)

for path in "${required_files[@]}"; do
    if [[ ! -f "$path" ]]; then
        echo "Missing required long-task continuation file: $path"
        exit 1
    fi
done

skill_text="$(cat skills/long-task-continuation/SKILL.md)"

for pattern in \
    "<aegis-workspace-helper> init" \
    "<aegis-workspace-helper> new-work" \
    "<aegis-workspace-helper> add-checkpoint" \
    "<aegis-workspace-helper> add-baseline-usage" \
    "<aegis-workspace-helper> add-attempt" \
    "<aegis-workspace-helper> add-evidence" \
    "<aegis-workspace-helper> add-drift-check" \
    "Retry Convergence Protocol" \
    "process-artifact-pressure" \
    "<aegis-workspace-helper> bundle" \
    "<aegis-workspace-helper> check" \
    "todo-checkpoint-draft.json" \
    "drift-check-draft.json" \
    "PatchShape" \
    "CanonicalOwner" \
    "UpwardDrillSignal" \
    "locally green result does not clear" \
    "bounded evidence ref" \
    "do not copy raw logs or full diffs" \
    "route comparison to" \
    "carrier name alone does not prove a new direction"
do
    if [[ "$skill_text" != *"$pattern"* ]]; then
        echo "long-task-continuation skill missing helper integration pattern: $pattern"
        exit 1
    fi
done

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD="py -3"
else
    PYTHON_CMD=python
fi

eval "$PYTHON_CMD" - "$SCENARIO_DIR" "$ARTIFACT_DIR" <<'PY'
import json
import pathlib
import sys

scenario_dir = pathlib.Path(sys.argv[1])
artifact_dir = pathlib.Path(sys.argv[2])

expected_artifacts = json.loads((scenario_dir / "expected-artifacts.json").read_text(encoding="utf-8"))
expected_behavior = json.loads((scenario_dir / "expected-behavior.json").read_text(encoding="utf-8"))
baseline_usage = json.loads((artifact_dir / "baseline-usage-draft.sample.json").read_text(encoding="utf-8"))
checkpoint = json.loads((artifact_dir / "todo-checkpoint-draft.sample.json").read_text(encoding="utf-8"))
resume = json.loads((artifact_dir / "resume-state-hint.sample.json").read_text(encoding="utf-8"))
drift = json.loads((artifact_dir / "drift-check-draft.sample.json").read_text(encoding="utf-8"))

failures = []

for artifact_name in ["BaselineUsageDraft", "TodoCheckpointDraft", "ResumeStateHint", "DriftCheckDraft"]:
    if artifact_name not in expected_artifacts["requiredArtifacts"]:
        failures.append(f"Scenario D missing required artifact {artifact_name}")

for forbidden in expected_artifacts["forbiddenDecisions"]:
    if drift.get("decision") == forbidden:
        failures.append(f"DriftCheckDraft uses forbidden decision {forbidden}")

if checkpoint.get("taskId") != resume.get("taskId") or checkpoint.get("taskId") != drift.get("taskId"):
    failures.append("Long-task artifact taskId values must match")
if checkpoint.get("taskId") != baseline_usage.get("taskId"):
    failures.append("BaselineUsageDraft taskId must match long-task artifacts")

if not checkpoint.get("nextStep"):
    failures.append("TodoCheckpointDraft must include nextStep")

if not resume.get("mustReadBeforeContinuing"):
    failures.append("ResumeStateHint must include mustReadBeforeContinuing")

if drift.get("decision") not in {"continue", "pause-for-user", "needs-baseline-readback", "needs-verification", "blocked"}:
    failures.append("DriftCheckDraft decision is not an allowed advisory value")
if baseline_usage.get("decision") not in {"continue", "pause-for-user", "needs-baseline-readback", "needs-verification", "blocked"}:
    failures.append("BaselineUsageDraft decision is not an allowed advisory value")

prompt_text = (scenario_dir / "prompt.txt").read_text(encoding="utf-8").lower()
for token in expected_behavior["mustMention"]:
    if token.lower() not in prompt_text:
        failures.append(f"Scenario D prompt must mention {token}")

if failures:
    for failure in failures:
        print(failure)
    sys.exit(1)

print("Long-task continuation scenario fixtures passed.")
PY
