# Directional Reset Governance - Intent

## TaskIntentDraft

- Requested outcome: Strengthen Aegis so repeated same-class consumer-side fixes and plan-shape contradictions trigger a directional reset before more edits.
- Goal: Carry patch-shape and owner-risk signals across debugging, plan execution, and long-task checkpoints without creating a new authority owner.
- Success evidence:
- A written design approved by the user, a stateful baseline pressure scenario, targeted workflow changes, and regression verification that stops repeated same-root local patches while preserving ordinary single-owner fixes.
- Stop condition: Done only after approved design, implementation, targeted verification, workflow checks, and residual method-pack limitations are reported; otherwise blocked, needs-verification, or scope-exceeded.
- Non-goals:
- Create a new skill or runtime gate.
- Make the workspace helper decide architecture truth.
- Change host installation or public plugin identity.
- Scope: systematic-debugging, executing-plans, long-task-continuation, workflow quality and trigger-health scenarios, smallest relevant current docs
- Change kinds:
- contract
- Risk hints:
- A new global gate would duplicate owners or overstep the method-pack boundary.
- A naive second-fix counter could misclassify legitimate independent compound roots.

## BaselineReadSetHint

- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md

## BaselineUsageDraft

- Required baseline refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md
- Acknowledged before plan:
- none
- Cited in plan:
- none
- Missing refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md
- Advisory decision: needs-baseline-readback

## ImpactStatementDraft

- Compatibility boundary: Preserve fast-path behavior for ordinary single-owner fixes and preserve all supported host distribution surfaces.
- Affected layers:
- method-pack workflow discipline
- long-task advisory state
- workflow quality verification
- Owners:
- systematic-debugging owns directional repair judgment
- executing-plans and long-task-continuation propagate and pause on unresolved signals
- Invariants:
- No consumer becomes a second semantic owner because a later test exposes another carrier.
- Method-pack output remains advisory and never becomes GateDecision or completion authority.
- Non-goals:
- Create a new skill or runtime gate.
- Make the workspace helper decide architecture truth.
- Change host installation or public plugin identity.

These records are Method Pack drafts / hints, not authoritative runtime decisions.

## BaselineUsageDraft

- Required baseline refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md
- Delivered context refs:
- none
- Acknowledged before plan:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md
- Cited in plan:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_MINIMALITY_REFERENCE.md
- Missing refs:
- none
- Advisory decision: pause-for-user

## BaselineUsageDraft

- Required baseline refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md
- docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md
- Delivered context refs:
- none
- Acknowledged before plan:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md
- docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md
- Cited in plan:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md
- docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md
- docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md
- Missing refs:
- none
- Advisory decision: continue
