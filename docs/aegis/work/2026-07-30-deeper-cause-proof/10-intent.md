# Prevent premature debugging root-cause closure - Intent

## TaskIntentDraft

- Requested outcome: Strengthen the seven-layer debugging stop contract so proximate causes cannot be claimed as roots while preserving the quick bug lane.
- Goal: Require falsifiable deeper-cause evidence before non-trivial root claims without making Aegis heavier.
- Success evidence:
- Pressure scenarios A and B remain open until upstream generator or specification causes are resolved; negative-control scenario C stays in the quick lane; focused, budget, boundary, parser, and Layer 1 checks pass.
- Stop condition: Done only after contract, baselines, behavior matrix, stale topology semantics, tests, review, and verification are complete; otherwise remain paused, needs-verification, blocked, or scope-exceeded.
- Non-goals:
- Do not add an eighth diagnostic layer, new skill, runtime gate, release, tag, or main-branch publication.
- Scope: systematic-debugging root-cause claim contract, lightweight main routing, advanced H/D closeout signals, current process/workflow baselines, workflow-quality fixtures and validators.
- Change kinds:
- contract
- Risk hints:
- Over-tightening could make tiny local bugs expensive; under-tightening preserves self-classified quick-lane escape.

## BaselineReadSetHint

- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md

## BaselineUsageDraft

- Required baseline refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- Acknowledged before plan:
- none
- Cited in plan:
- none
- Missing refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- Advisory decision: needs-baseline-readback

## ImpactStatementDraft

- Compatibility boundary: No runtime authority, no host distribution change, systematic-debugging/SKILL.md <= 10000 bytes, combined main skills <= 17000 bytes.
- Affected layers:
- Method-pack debugging contract and deterministic behavioral evidence
- Owners:
- skills/systematic-debugging/root-cause-claim-contract.md
- Invariants:
- Seven diagnostic layers remain a localization taxonomy; root claims require evidence that the recurrence generator is closed, while true local typos remain cheap.
- Non-goals:
- Do not add an eighth diagnostic layer, new skill, runtime gate, release, tag, or main-branch publication.

These records are Method Pack drafts / hints, not authoritative runtime decisions.

## BaselineUsageDraft

- Required baseline refs:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- Delivered context refs:
- none
- Acknowledged before plan:
- docs/current/README.md
- docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- Cited in plan:
- docs/current/AEGIS_PROCESS_BASELINE.md
- docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md
- Missing refs:
- none
- Advisory decision: pause-for-user
