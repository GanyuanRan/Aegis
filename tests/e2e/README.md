# Aegis E2E Bootstrap

This directory hosts the Phase 5 E2E verification suite for the Aegis fork.

Current status:

- `Phase 5 E2E verification slice` is complete within approved scope
- `layer1-fast-check.sh` is runnable now and defaults to a fast host profile
- `layer2-behavior-check.sh` is runnable now with fixture-backed transcript analysis and with/without Aegis comparison
- `layer3-scenario-check.sh` is runnable now with fixture-backed scenario orchestration and cross-host comparison
- scenario definitions, artifact fixtures, and transcript fixtures exist as advisory verification inputs, not as final authority

Current public baselines:

- `docs/current/README.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`

Bootstrap entrypoints:

- `run-all.sh`
- `layer1-fast-check.sh`
- `layer2-behavior-check.sh`
- `boundary-compliance-check.sh`
- `artifact-schema-check.sh`
- `aegis-workspace-check.sh`
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

Workspace helper coverage:

- `aegis-workspace-check.sh` verifies `scripts/aegis-workspace.py` against a
  temporary target project.
- The Aegis method-pack repository must not ship a live `docs/aegis/`
  workspace. The helper initializes and checks that workspace only in the
  target project root passed by the caller.
- The helper validates recognizable JSON sidecar artifacts structurally, but it
  does not judge evidence sufficiency or grant completion authority.
- `long-task-continuation-check.sh` verifies that long-task `work/<slug>/`
  records are routed through the workspace helper discipline.
