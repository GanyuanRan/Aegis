#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/artifacts"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=python3
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD="py -3"
else
    PYTHON_CMD=python
fi

eval "$PYTHON_CMD" - "$FIXTURE_DIR" <<'PY'
import json
import os
import sys

fixture_dir = sys.argv[1]
schema_version = "aegis.schema.v0"
expected = {
    "task-intent-draft.sample.json": [
        "schemaVersion",
        "requestedOutcome",
        "scope",
        "changeKinds",
        "riskHints",
    ],
    "baseline-read-set-hint.sample.json": [
        "schemaVersion",
        "candidateDocs",
        "whyRelevant",
        "missingAuthority",
    ],
    "impact-statement-draft.sample.json": [
        "schemaVersion",
        "affectedLayers",
        "owners",
        "invariants",
        "compatBoundary",
        "nonGoals",
    ],
    "evidence-bundle-draft.sample.json": [
        "schemaVersion",
        "artifactKey",
        "type",
        "source",
        "summary",
        "verifier",
    ],
    "gate-input-pack.sample.json": [
        "schemaVersion",
        "baselineRefs",
        "impactStatement",
        "compatPlan",
        "retirementPlan",
        "evidenceBundle",
    ],
    "todo-checkpoint-draft.sample.json": [
        "schemaVersion",
        "taskId",
        "currentTodo",
        "completedTodos",
        "activeSlice",
        "evidenceRefs",
        "blockedOn",
        "nextStep",
        "updatedAt",
    ],
    "resume-state-hint.sample.json": [
        "schemaVersion",
        "taskId",
        "lastCheckpointRef",
        "resumeInstruction",
        "knownPartialWork",
        "mustReadBeforeContinuing",
        "unsafeToAssume",
    ],
    "drift-check-draft.sample.json": [
        "schemaVersion",
        "taskId",
        "taskIntentRef",
        "baselineRefs",
        "scopeStatus",
        "compatStatus",
        "retirementStatus",
        "newRiskSignals",
        "decision",
    ],
}

failures = []

for filename, fields in expected.items():
    path = os.path.join(fixture_dir, filename)
    if not os.path.exists(path):
        failures.append(f"{filename}: missing fixture file")
        continue

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        failures.append(f"{filename}: invalid json ({exc})")
        continue

    missing = [field for field in fields if field not in data]
    if missing:
        failures.append(f"{filename}: missing fields {', '.join(missing)}")
        continue

    if data.get("schemaVersion") != schema_version:
        failures.append(
            f"{filename}: schemaVersion must be {schema_version}, got {data.get('schemaVersion')}"
        )

    if filename == "drift-check-draft.sample.json":
        forbidden = {"gate-passed", "completion-granted", "authoritatively-safe"}
        if data.get("decision") in forbidden:
            failures.append(
                f"{filename}: decision must not be an authoritative completion value"
            )

if failures:
    for item in failures:
        print(item)
    sys.exit(1)

print("Artifact schema bootstrap fixtures passed.")
PY
