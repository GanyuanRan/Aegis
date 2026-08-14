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
- `workspace-helper-resolution-check.sh`
- `project-bootstrap-policy-check.sh`
- `trigger-health-check.sh`
- `context-semantic-infrastructure-check.sh`
- `context-semantic-infrastructure-live-check.sh`
- `workflow-quality-check.sh`
- `agentic-benchmark-check.sh`
- `controlled-replay-check.sh`
- `live-replay-capture-check.sh`
- `live-replay-capture.sh`
- `host-instruction-invariants-check.sh`
- `bootstrap-adapter-contract-check.sh`
- `deferred-ledger-check.sh`
- `minimality-reference-check.sh`
- `host-adapter-smoke-check.sh`
- `goal-framing-check.sh`
- `first-principles-review-check.sh`
- `long-task-continuation-check.sh`
- `grok-build-host-boundary-check.sh`
- `analyze-transcript.sh`

Layer 1 host profiles:

- `fast` (default): representative Codex natural + explicit smoke, OpenCode base suite, plugin sync
- `matrix`: full Codex matrices plus OpenCode base suite and plugin sync
- `none`: static boundary + schema checks only

Supporting bootstrap assets:

- `fixtures/artifacts/`
- `fixtures/replay-projects/`
- `fixtures/transcripts/`
- `replay-samples/`
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
- `context-semantic-infrastructure-check.sh` deterministically verifies the
  semantic-context owner, passive/active consumer boundary, lifecycle/security
  matrix, self-hosting glossary, legacy compatibility, and no-authority-drift
  contract. It does not claim that a host model performed the state changes.
- `context-semantic-infrastructure-live-check.sh` is an opt-in, temporary-project
  runner for stateful host behavior. It fingerprints the skill source under
  test and keeps checkout-explicit behavior evidence distinct from native
  installed routing evidence.
- `workflow-quality-check.sh` verifies the workflow quality baseline, compact
  output contracts, and representative samples for fast-path cheapness,
  evidence freshness, artifact stability, and workspace laziness.
- `agentic-benchmark-check.sh` verifies the benchmark design fixture for
  with/without Aegis scenario coverage, isolation controls, metric boundaries,
  and no authority overclaim.
- `controlled-replay-check.sh` verifies benchmark-ready controlled replay
  samples by copying seeded fixture projects into per-arm temporary workspaces,
  analyzing captured transcripts through `analyze-transcript.sh`, and checking
  with/without Aegis contrast without using local user projects or live host
  execution.
- `live-replay-capture-check.sh` dry-runs the live replay capture entrypoint so
  Layer 1 can verify workspace preparation, explicit opt-in, and no fabricated
  no-Aegis baseline without invoking a host model.
- `live-replay-capture.sh` is an environment-bound, opt-in runner for capturing
  one live `aegis-auto` arm from a controlled replay sample. It requires
  `AEGIS_LIVE_REPLAY=1`, writes only under repo-local `.tmp/`, normalizes the
  raw host log for `analyze-transcript.sh`, and does not grant benchmark or
  completion authority.
- `host-instruction-invariants-check.sh` verifies that manually copied global
  rule projections and thin host instruction adapters preserve activation,
  priority, evidence, authority, projection budgets, and the Lite-base /
  Advanced-overlay role split without byte-for-byte copy checks.
- `bootstrap-adapter-contract-check.sh` verifies that bootstrap adapters source
  the canonical `using-aegis` hot path or host-native references while keeping
  host-specific activation, TDD mode, JSON, discovery, warning, and tool
  mapping logic outside the portable method body.
- `deferred-ledger-check.sh` verifies the deferred marker convention, parser,
  and current repository scan for malformed retained follow-up / retirement
  entries.
- `minimality-reference-check.sh` verifies the Aegis-specific reference for
  checking before adding new skills, artifacts, adapters, fallbacks, or
  benchmark metrics.
- `host-adapter-smoke-check.sh` parses core host manifests and hook configs for
  version alignment, expected paths, assets, and the no-live-workspace boundary.
- `tests/kimi-code/run-tests.sh` is the deterministic Kimi Code entrypoint for
  metadata, manifest, doctor-profile, duplicate-exposure, and host-boundary
  checks. Its `--integration` mode and `run-live-smoke.sh` are environment-bound
  and must not be represented as passed when CLI, login, provider, or trust
  prerequisites are absent.
- `goal-framing-check.sh` verifies the opt-in goal-framing entry, optional
  TaskIntentDraft goal fields, SubagentContextPacket shape, and no-file default
  policy.
- `first-principles-review-check.sh` verifies that first-principles review is
  available as a lightweight compositional skill without entering the
  always-loaded hot path or claiming authority.
- `grok-build-host-boundary-check.sh` verifies Grok Build's native
  direct-child discovery defaults, explicit config alternative, duplicate
  exposure guard, updater registration, and structural support wording.
- `deepseek-harness-host-boundary-check.sh` verifies the official DeepSeek
  Harness identity, native DSH direct-child discovery defaults, updater
  registration, duplicate-exposure guard, and developer-preview support
  boundary without conflating it with DeepSeek-TUI.
- The Aegis method-pack repository must not ship a live `docs/aegis/`
  workspace. The helper initializes and checks that workspace only in the
  target project root passed by the caller.
- The helper validates recognizable JSON sidecar artifacts structurally, but it
  does not judge evidence sufficiency or grant completion authority.
- The helper can create helper-backed task lifecycle records and assemble a
  structural proof bundle for review or handoff. The bundle is still advisory
  method-pack evidence, not a final gate.
- The helper can also create, amend, and supersede target-project
  `docs/aegis/adr/` records while keeping ADR numbering, supersession markers,
  and `INDEX.md` coverage inside the same target-project-only boundary.
- `workspace-helper-wiring-check.sh` verifies that skills which write
  `docs/aegis/` records route through the shared helper or run helper checks.
- `workspace-helper-resolution-check.sh` verifies that workflows resolve the
  helper from the installed method-pack support path and pass the target project
  separately with `--root`.
- `long-task-continuation-check.sh` verifies that long-task records are routed
  through the workspace helper discipline.
