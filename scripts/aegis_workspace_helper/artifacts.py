"""Artifact schemas, structural validation, and ``validate-artifact``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import WorkspaceError
from .inputs import load_json_file


SCHEMA_VERSION = "aegis.schema.v0"
EVIDENCE_STATUSES = {
    "attempted",
    "evidence-finalized",
    "blocked",
    "abandoned",
    "superseded",
}
TERMINAL_EVIDENCE_STATUSES = {
    "evidence-finalized",
    "blocked",
    "abandoned",
}
ATTEMPT_STATUSES = {
    "attempted",
    "failed",
    "blocked",
}
ARTIFACT_SCHEMAS = {
    "TaskIntentDraft": (
        "schemaVersion",
        "requestedOutcome",
        "scope",
        "changeKinds",
        "riskHints",
    ),
    "BaselineUsageDraft": (
        "schemaVersion",
        "taskId",
        "requiredBaselineRefs",
        "acknowledgedBeforePlanRefs",
        "citedInPlanRefs",
        "missingRefs",
        "decision",
    ),
    "SubagentContextPacket": (
        "schemaVersion",
        "task",
        "goal",
        "stopCondition",
        "relevantBaselineRefs",
        "relevantFiles",
        "knownFacts",
        "unknowns",
        "nonGoals",
        "expectedOutput",
        "verificationExpected",
        "mustReadExcerpts",
        "unsafeAssumptions",
    ),
    "BaselineReadSetHint": (
        "schemaVersion",
        "candidateDocs",
        "whyRelevant",
        "missingAuthority",
    ),
    "ImpactStatementDraft": (
        "schemaVersion",
        "affectedLayers",
        "owners",
        "invariants",
        "compatBoundary",
        "nonGoals",
    ),
    "EvidenceBundleDraft": (
        "schemaVersion",
        "artifactKey",
        "type",
        "source",
        "summary",
        "verifier",
    ),
    "GateInputPack": (
        "schemaVersion",
        "baselineRefs",
        "impactStatement",
        "compatPlan",
        "retirementPlan",
        "evidenceBundle",
    ),
    "TodoCheckpointDraft": (
        "schemaVersion",
        "taskId",
        "currentTodo",
        "completedTodos",
        "activeSlice",
        "evidenceRefs",
        "blockedOn",
        "nextStep",
        "updatedAt",
    ),
    "ResumeStateHint": (
        "schemaVersion",
        "taskId",
        "lastCheckpointRef",
        "resumeInstruction",
        "knownPartialWork",
        "mustReadBeforeContinuing",
        "unsafeToAssume",
    ),
    "DriftCheckDraft": (
        "schemaVersion",
        "taskId",
        "taskIntentRef",
        "baselineRefs",
        "scopeStatus",
        "compatStatus",
        "retirementStatus",
        "newRiskSignals",
        "decision",
    ),
}
ARTIFACT_FILENAME_TYPES = {
    "task-intent-draft": "TaskIntentDraft",
    "baseline-usage-draft": "BaselineUsageDraft",
    "subagent-context-packet": "SubagentContextPacket",
    "baseline-read-set-hint": "BaselineReadSetHint",
    "impact-statement-draft": "ImpactStatementDraft",
    "evidence-bundle-draft": "EvidenceBundleDraft",
    "gate-input-pack": "GateInputPack",
    "todo-checkpoint-draft": "TodoCheckpointDraft",
    "resume-state-hint": "ResumeStateHint",
    "drift-check-draft": "DriftCheckDraft",
}
DRIFT_DECISIONS = {
    "continue",
    "pause-for-user",
    "needs-baseline-readback",
    "needs-verification",
    "blocked",
}
BASELINE_USAGE_DECISIONS = DRIFT_DECISIONS


def infer_artifact_type(path: Path) -> str | None:
    filename = path.name.lower()
    if not filename.endswith(".json"):
        return None
    stem = filename[:-5]
    for prefix, artifact_type in ARTIFACT_FILENAME_TYPES.items():
        if stem == prefix or stem.startswith(f"{prefix}-"):
            return artifact_type
    return None


def validate_artifact_data(artifact_type: str, data: object, source: Path) -> list[str]:
    fields = ARTIFACT_SCHEMAS.get(artifact_type)
    if fields is None:
        return [f"{source}: unknown artifact type: {artifact_type}"]
    if not isinstance(data, dict):
        return [f"{source}: artifact must be a JSON object"]

    failures = []
    for field in fields:
        if field not in data:
            failures.append(f"{source}: {artifact_type} missing field: {field}")

    schema_version = data.get("schemaVersion")
    if schema_version != SCHEMA_VERSION:
        failures.append(
            f"{source}: schemaVersion must be {SCHEMA_VERSION}, got {schema_version}"
        )

    if artifact_type == "DriftCheckDraft":
        decision = data.get("decision")
        if decision not in DRIFT_DECISIONS:
            failures.append(
                f"{source}: DriftCheckDraft decision must be advisory, got {decision}"
            )
    if artifact_type == "BaselineUsageDraft":
        decision = data.get("decision")
        if decision not in BASELINE_USAGE_DECISIONS:
            failures.append(
                f"{source}: BaselineUsageDraft decision must be advisory, got {decision}"
            )
    if artifact_type == "EvidenceBundleDraft":
        evidence_status = data.get("evidenceStatus")
        if evidence_status is not None and evidence_status not in EVIDENCE_STATUSES:
            failures.append(
                f"{source}: EvidenceBundleDraft evidenceStatus must be advisory, got {evidence_status}"
            )
        slice_id = data.get("sliceId")
        if slice_id is not None and (not isinstance(slice_id, str) or not slice_id.strip()):
            failures.append(f"{source}: EvidenceBundleDraft sliceId must be a non-empty string")
        attempts = data.get("attempts")
        if attempts is not None:
            if not isinstance(attempts, list):
                failures.append(f"{source}: EvidenceBundleDraft attempts must be a list")
            else:
                for index, attempt in enumerate(attempts):
                    if not isinstance(attempt, dict):
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} must be an object"
                        )
                        continue
                    attempt_id = attempt.get("attemptId")
                    if not isinstance(attempt_id, str) or not attempt_id.strip():
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} missing attemptId"
                        )
                    attempt_status = attempt.get("attemptStatus")
                    if attempt_status not in ATTEMPT_STATUSES:
                        failures.append(
                            f"{source}: EvidenceBundleDraft attempt {index} attemptStatus must be advisory, got {attempt_status}"
                        )

    return failures


def validate_artifact_file(artifact_type: str, path: Path) -> list[str]:
    data = load_json_file(path)
    return validate_artifact_data(artifact_type, data, path)


def command_validate_artifact(args: argparse.Namespace) -> int:
    path = Path(args.file).expanduser().resolve()
    artifact_type = args.type or infer_artifact_type(path)
    if not artifact_type:
        raise WorkspaceError(f"could not infer artifact type from filename: {path.name}")

    failures = validate_artifact_file(artifact_type, path)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"{artifact_type} structure check passed: {path}")
    return 0
