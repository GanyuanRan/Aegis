# Aegis E2E Bootstrap

This directory hosts the Phase 5 E2E verification suite for the Aegis fork.

Current status:

- `Phase 5 E2E verification slice` is complete within approved scope
- `layer1-fast-check.sh` is runnable now and defaults to a fast host profile
- `layer2-behavior-check.sh` is runnable now with fixture-backed transcript analysis and with/without Aegis comparison
- `layer3-scenario-check.sh` is runnable now with fixture-backed scenario orchestration and cross-host comparison
- scenario definitions, artifact fixtures, and transcript fixtures exist as advisory verification inputs, not as final authority

Authoritative plan:

- `docs/current/AEGIS_PHASE5_E2E_VERIFICATION_ATOMIC_PLAN.md`

Bootstrap entrypoints:

- `run-all.sh`
- `layer1-fast-check.sh`
- `layer2-behavior-check.sh`
- `boundary-compliance-check.sh`
- `artifact-schema-check.sh`
- `long-task-continuation-check.sh`
- `analyze-transcript.sh`

Layer 1 host profiles:

- `fast` (default): representative Codex natural + explicit smoke, OpenCode base suite, plugin sync
- `matrix`: full Codex matrices plus OpenCode base suite and plugin sync
- `none`: static boundary + schema checks only

Supporting bootstrap assets:

- `fixtures/artifacts/`
- `fixtures/transcripts/`
- `scenarios/`
- `scenarios/scenario-D-interrupted-long-task/`
- `baselines/without-aegis/`
- `prompts/`
