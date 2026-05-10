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
- `aegis-doctor-check.sh`
- `workspace-helper-wiring-check.sh`
- `project-bootstrap-policy-check.sh`
- `trigger-health-check.sh`
- `first-principles-review-check.sh`
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
- `aegis-doctor-check.sh` verifies complete-install readiness: key skills,
  method-pack root, and project workspace support through a temporary target
  project.
- `project-bootstrap-policy-check.sh` verifies Project Baseline Bootstrap,
  Spec Brief, Workspace Shell, Task Work Record, and lazy workspace wording
  across the process baseline and skills.
- `trigger-health-check.sh` verifies the trigger-chain diagnostic baseline and
  representative positive/negative trigger-health matrix used when Aegis is
  installed but the expected skill does not trigger reliably.
- `first-principles-review-check.sh` verifies that first-principles review is
  available as a lightweight compositional skill without entering the
  always-loaded hot path or claiming authority.
- The Aegis method-pack repository must not ship a live `docs/aegis/`
  workspace. The helper initializes and checks that workspace only in the
  target project root passed by the caller.
- The helper validates recognizable JSON sidecar artifacts structurally, but it
  does not judge evidence sufficiency or grant completion authority.
- The helper can create helper-backed task lifecycle records and assemble a
  structural proof bundle for review or handoff. The bundle is still advisory
  method-pack evidence, not a final gate.
- `workspace-helper-wiring-check.sh` verifies that skills which write
  `docs/aegis/` records route through the shared helper or run helper checks.
- `long-task-continuation-check.sh` verifies that long-task `work/<slug>/`
  records are routed through the workspace helper discipline.
