# Aegis Release Notes

## v1.5.0 (2026-05-19)

### Completion-Time Complexity Delta

- Added a completion-time `Complexity Delta` guardrail so non-trivial code
  changes report actual entropy movement before a completion claim.
- The completion check now calls out maintained source files over 800 lines,
  files newly crossing 800 lines, largest touched file delta, largest touched
  function/block, new branches/fallbacks/adapters, retired paths, net entropy,
  and required follow-up.
- The 800-line file threshold is documented as a review signal rather than a
  universal failure gate, with generated, vendored, fixture, lockfile, and
  framework-owned artifacts exempt only when the reason is explicit.
- Added block-level complexity guidance for touched functions, methods,
  components, or cohesive blocks over roughly 80 lines, deeply nested logic, or
  mixed reasons to change.

### Retirement Closure

- Extended `verification-before-completion` with a `Retirement Closure` card
  for work that adds, replaces, or retains old logic.
- The closure now asks agents to record old logic location, deletion status,
  retained logic, retention reason, retirement trigger, and lingering-reference
  checks.
- Complexity Delta and Retirement Closure are linked: new fallback, adapter,
  compatibility, guard, or branch logic without deleted or scheduled old paths
  is reported as entropy increase and residual risk.

### Workflow Quality Coverage

- Added the `Completion-Time Complexity Delta` dimension to the workflow
  quality baseline.
- Added a representative workflow-quality sample for a core file that may cross
  the 800-line threshold before completion.
- Expanded `workflow-quality-check.sh` so process docs, workflow quality docs,
  the verification skill, compact contracts, and the matrix all lock the new
  completion-time complexity behavior.

### Verification

- `bash scripts/bump-version.sh 1.5.0`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/run-all.sh --full --host-profile none`

## v1.4.6 (2026-05-18)

### Workspace Helper Resolution Boundary

- Added `aegis-doctor.py helper-path --json` so hosts and agents can resolve the
  installed Aegis workspace helper without assuming the target project owns
  `scripts/aegis-workspace.py`.
- Updated workspace-writing skills and current docs to use
  `python <aegis-workspace-helper> ... --root <target-project-root>`, keeping
  the helper owner and target project root as separate concepts.
- Added `workspace-helper-resolution-check.sh` and Layer 1 coverage for helper
  path resolution, uninitialized target-project reporting, and target-project
  helper ownership wording.

### Verification

- `bash scripts/bump-version.sh 1.4.6`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workspace-helper-resolution-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- `bash tests/e2e/long-task-continuation-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/project-bootstrap-policy-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/run-all.sh --full --host-profile none`

## v1.4.5 (2026-05-17)

### Completion Architecture Alignment

- Added an explicit `Architecture Alignment` completion card for work that
  touches durable architecture surfaces or project rules that require
  architecture reporting.
- The card records trigger status, scope, checked baseline, result
  (`aligned`, `architecture drift`, or `architecture defect`), evidence, and
  residual architecture risk.
- Added a lightweight `ArchitectureReviewRequired` signal in `using-aegis` so
  medium/high, contract, cross-module, owner, source-of-truth,
  fallback/adapter, and project-baseline tasks carry the signal into
  `verification-before-completion`.

### User-Language Output Contract

- Added a completion-time `User-Language Output` rule requiring user-facing
  section labels, field labels, and explanatory prose to follow the user's
  current language.
- Preserved precision for commands, paths, code identifiers, stable enum
  values, and Aegis product terms, with first-use bilingual labels recommended
  for important product terms.
- Extended the workflow quality baseline with a dedicated `User-Language
  Output` dimension so localization is checked as a workflow quality property,
  not only as a governance-closure detail.

### Workflow Quality Coverage

- Updated the workflow quality matrix so architecture completion checks require
  both `Architecture Alignment` and `ADR Backfill Check` signals.
- Expanded e2e checks to guard user-language completion cards, architecture
  alignment output, and the compact `ArchitectureReviewRequired` routing
  signal.
- Kept the new rules inside the method-pack boundary: they are advisory
  workflow discipline and do not add a runtime gate, authoritative
  `GateDecision`, `PolicySnapshot`, evidence sufficiency decision, or
  `completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.4.5`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.4.3 (2026-05-15)

### ADR Backfill Signal Hardening

- **Completion-time ADR Backfill Check** — extended
  `verification-before-completion` with an advisory ADR Backfill Check that
  records trigger status, suggested action, evidence source, baseline sync,
  skip reason, and method-pack boundary.
- **Workflow quality guardrails** — expanded the workflow quality baseline and
  fixture coverage so ADR backfill behavior is locked as a representative
  completion signal rather than a runtime authority decision.
- **Boundary preservation** — kept ADR backfill as method-pack signal and
  review discipline only; this release does not add authoritative
  `GateDecision`, `PolicySnapshot`, evidence sufficiency, or
  `completion authority`.

### ADR Signal Propagation

- Aligned ADR signal handling across `brainstorming`, `writing-plans`,
  `long-task-continuation`, `requesting-code-review`, and
  `verification-before-completion`.
- Preserved ADR signals, source references, alternatives, compatibility
  questions, baseline-sync questions, work records, proof bundles, drift
  checks, and evidence references across workflow handoffs.
- Clarified that long-task records and verification evidence are preferred
  sources for ADR Auto Backfill review.

### Code Review Routing And Baseline Awareness

- Demoted `requesting-code-review` from the default generic completion path so
  normal completion claims route to `verification-before-completion`.
- Retained code review as an explicit or high-risk independent escalation path
  with representative trigger-health and workflow-quality coverage.
- Made review baseline-aware by requiring reviewers to distinguish baseline
  defects from architecture drift and to check ADR Auto Backfill / baseline
  sync findings.

### Reviewer Compatibility Projection

- Marked `agents/code-reviewer.md` as a host compatibility projection rather
  than a second canonical owner.
- Kept `skills/requesting-code-review/code-reviewer.md` as the canonical
  reviewer template while mirroring the key baseline-aware and ADR review
  semantics into the compatibility projection.

### Verification

- `bash scripts/bump-version.sh 1.4.3`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.4.0 (2026-05-14)

### Goal Framing

- **Opt-in goal entry** — added `goal-framing` for `/aegis-goal <task>` and
  portable `Aegis goal: <task>` prompts.
- **Thin goal frame** — the new entry records the goal, success evidence, stop
  condition, non-goals, route, and next action before handing work to the
  appropriate workflow.
- **Explicit stop states** — goal-framed work distinguishes `done`, `blocked`,
  `needs-verification`, and `scope-exceeded` instead of making the host infer
  when to continue or stop.

### Goal Closure And Routing

- Added a goal signal routing matrix for fast path / TDD, systematic debugging,
  brainstorming, writing plans, long-task continuation, and
  verification-before-completion.
- Extended `verification-before-completion` with Goal Closure so completion
  claims compare fresh evidence against the latest goal frame, stop state, and
  non-goals.
- Kept `using-aegis` compact by routing explicit goal prompts to
  `goal-framing` instead of expanding the always-loaded hot path.

### Subagent Handoff And Runtime-Ready Artifacts

- Added `SubagentContextPacket` as a compact delegation packet for subagents,
  with relevant baseline refs, files, known facts, unknowns, non-goals,
  expected output, expected verification, must-read excerpts, and unsafe
  assumptions.
- Extended `TaskIntentDraft` with optional goal-framing fields:
  `goal`, `successEvidence`, `stopCondition`, and `nonGoals`.
- Updated `scripts/aegis-workspace.py new-work` with optional `--goal`,
  `--success-evidence`, and `--stop-condition` arguments while preserving
  backward-compatible defaults.

### Host And Documentation Updates

- Documented portable `Aegis goal:` usage in the English and Chinese README
  files, English and Chinese workflow guides, and the Codex, OpenCode, Claude
  Code, CodeBuddy, DeepSeek-TUI, and Trae host guides.
- Added `goal-framing` to doctor key skill detection, trigger/workflow quality
  fixtures, artifact schema fixtures, and Layer 1 fast verification.
- Added `tests/e2e/goal-framing-check.sh` to guard the opt-in entry, no-file
  default, Goal Closure contract, and SubagentContextPacket shape.

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. Goal Framing,
Goal Closure, and SubagentContextPacket are advisory method-pack discipline and
runtime-ready inputs only. They do not add an authoritative `GateDecision`,
`PolicySnapshot`, evidence sufficiency decision, host daemon, automatic stop
enforcement, or `completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.4.0`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python -m py_compile scripts/aegis-doctor.py scripts/aegis-workspace.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `python tests/helpers/test_workspace_text_write_compat.py`
- `bash tests/e2e/goal-framing-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.3.0 (2026-05-12)

### Workflow Quality Hardening

- **Workflow Quality baseline** — added
  `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md` to define quality
  dimensions for high-frequency Aegis workflows: trigger accuracy, fast-path
  cheapness, output compactness, evidence freshness, artifact stability,
  workspace laziness, and authority boundary.
- **Representative quality matrix** — added
  `tests/e2e/fixtures/workflow-quality-matrix.json` with sample-driven
  expectations for simple Q&A, tiny wording edits, version/status checks, bug
  fixes, failing tests, ambiguous features, approved specs, completion claims,
  long-task resume, and governance cleanup.
- **Regression guardrail** — added `tests/e2e/workflow-quality-check.sh` and
  wired it into Layer 1 fast verification so workflow hardening is checked
  before broadening skill behavior.

### Compact Workflow Contracts

- **Leaner routing** — kept `using-aegis` within the hot-path budget while
  adding a compact `Route / Why / Next` contract for useful routing output.
- **Scaled workflow depth** — clarified compact contracts for `brainstorming`,
  `writing-plans`, `systematic-debugging`, `verification-before-completion`,
  and `long-task-continuation` so everyday tasks stay light and medium/high
  risk tasks still produce reusable evidence.
- **Quick bug lane** — added a compact low-risk debugging lane that still
  requires root-cause evidence before editing and escalates when fallback,
  duplicate owner, consumer-side patching, contract, shared logic, or
  cross-module risk appears.
- **Evidence Card** — formalized the compact verification output shape:
  command/check, exit status, covered scope, uncovered scope, residual risk,
  and confidence.

### Documentation And Release Hygiene

- Added Workflow Quality to the current docs index, process baseline, trigger
  health baseline, English README, Chinese README, and E2E bootstrap docs.
- Updated version audit exclusions so ignored `.tmp/` dependency caches do not
  appear as Aegis version drift during release checks.

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. Workflow Quality
Hardening adds method-pack guardrails, samples, and compact output contracts.
It does not add an authoritative `GateDecision`, `PolicySnapshot`, evidence
sufficiency decision, or `completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.3.0`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/project-bootstrap-policy-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- `bash tests/e2e/long-task-continuation-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

## v1.2.2 (2026-05-12)

### Decision Hygiene Review

- **First-principles escalation** — strengthened
  `first-principles-review` with a compact `Decision Hygiene Review` escalation
  for risky proposal, spec, and plan decisions.
- **Owner and retirement clarity** — added first-principles invariants,
  owner / retirement matrix, and falsification matrix prompts before a workflow
  endorses new owners, duplicate owners, fallbacks, adapters, compat-only
  carriers, delete-first questions, or long-term stability claims.
- **Workflow routing** — wired `brainstorming` to invoke the escalation before
  risky approach selection and `writing-plans` before risky task decomposition
  when the spec has not already settled the decision.
- **Guide and baseline alignment** — updated the English and Chinese workflow
  guides plus the process baseline so decision hygiene remains an escalation
  inside the method pack, not a new always-on ceremony.

### Regression Coverage

- Expanded `tests/e2e/first-principles-review-check.sh` to guard the decision
  hygiene template, escalation signals, advisory verdict wording, workflow guide
  coverage, and the unchanged `using-aegis` hot path.

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. Decision Hygiene
Review is advisory method-pack workflow discipline. It does not add an
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.2.2`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/first-principles-review-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.2.1 (2026-05-12)

### Hardened Install Verification

- **Complete-install gate** — tightened the root English and Chinese README
  install/update prompts so agents must run
  `python scripts/aegis-doctor.py --write-config --json` from the Aegis
  method-pack root.
- **Durable helper path readback** — documented that installation or update is
  complete only when the doctor JSON reports `"ok": true`,
  `"workspaceSupport": "available"`, and `"configStatus": "configured"`.
- **Discovery-root check** — kept separate host skill discovery validation via
  `--discovery-root <path>` for hosts that expose a distinct skill discovery
  directory, reducing the chance that a stale copied skill tree is mistaken for
  a complete install.

### Host Documentation

- Updated Codex, OpenCode, Claude Code, CodeBuddy, DeepSeek-TUI, and Trae
  install/troubleshooting guides to use the hardened complete-install
  verification command.
- Updated the host compatibility snapshot, known limitations, and trigger
  health baseline so install/version diagnosis uses the same configured helper
  path readback.

### Regression Coverage

- Added `tests/e2e/install-verification-policy-check.sh` to prevent public
  install docs from regressing to weak "skill discovery only" verification.
- Wired the new install verification policy check into Layer 1 fast
  verification.

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. The hardened
doctor readback verifies method-pack installation and workspace-helper wiring;
it does not grant authoritative `GateDecision`, `PolicySnapshot`, or
`completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.2.1`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python -m py_compile scripts/aegis-doctor.py scripts/aegis-workspace.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/install-verification-policy-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.2.0 (2026-05-12)

### ADR Auto Backfill

- **Completion-time ADR memory** — added
  `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`, defining how completed work should
  be backfilled into durable architecture decision records without turning ADRs
  into a manual user approval burden.
- **Evidence-source priority** — documented the source order for ADR backfill:
  `work -> plan -> spec -> git / verification evidence`. Work records remain
  the preferred source when available.
- **Create / amend / supersede / skip policy** — clarified when Aegis should
  create a new ADR, amend an existing ADR, supersede a prior decision, or skip
  ADR creation for low-value or speculative decisions.
- **ADR and baseline sync** — formalized the rule that ADRs record why a
  decision exists, while baselines record the current architecture state. ADR
  actions that change or confirm owners, contracts, dependency direction,
  source-of-truth ownership, compatibility boundaries, runtime-ready artifact
  boundaries, or retirement schedules now require a baseline sync check.

### Documentation Wiring

- Added ADR Auto Backfill to the public current docs index.
- Updated the process baseline and both workflow guides so users can understand
  ADR backfill as a completion-time workflow rather than a pre-execution
  ceremony.
- Recorded the current limitation that helper-backed `new-adr`, `amend-adr`,
  and `supersede-adr` commands are not implemented yet.

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. ADR Auto Backfill
is method-pack workflow discipline only. It does not add authoritative
`GateDecision`, `PolicySnapshot`, or `completion authority`.

### Verification

- `bash scripts/bump-version.sh 1.2.0`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python -m py_compile scripts/aegis-workspace.py scripts/aegis-doctor.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/project-bootstrap-policy-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.1.6 (2026-05-11)

### 工作流程入口

- **新增英文工作流程说明** — 增加
  `docs/current/AEGIS_WORKFLOW_GUIDE.md`，面向用户和贡献者说明 Aegis
  如何触发、路由、分级、基线读取、执行、验证和收口。
- **新增中文工作流程说明** — 增加
  `docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md`，帮助中文用户在安装前快速理解
  Aegis 的实际工作方式。
- **README 快速入口** — 在根目录 `README.md` 的 `Minimal Install` 前、以及
  `README.zh-CN.md` 的 `极简安装` 前加入中英文 workflow guide 链接，方便新用户
  先阅读流程再安装。
- **Current docs 索引** — 将两份 workflow guide 纳入 `docs/current/README.md`
  的 public current baseline 与 document roles。

### 边界

- 两份 workflow guide 仅作为说明型入口，不新增 runtime authority。
- 本版本仍然发布 `Aegis Method Pack (runtime-ready)`，不新增 authoritative
  `GateDecision`、`PolicySnapshot` 或 `completion authority`。

### 验证

- `bash scripts/bump-version.sh 1.1.6`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.1.5 (2026-05-10)

### Trigger Reliability

- **Trigger Health baseline** — added a current baseline for diagnosing cases
  where Aegis is installed but the expected skill does not reliably trigger.
  The new diagnostic chain separates install/version, host discovery,
  activation/bootstrap, router entry, task routing, execution depth, context
  pressure, and false-positive control.
- **Context-pressure re-entry** — strengthened `using-aegis` so agents re-check
  routing on start, resume, and context compaction before continuing
  non-trivial work.
- **Doctor visibility** — extended `aegis-doctor.py` to report the Trigger
  Health baseline and layers, including context-pressure re-entry.

### Skill Trigger Hygiene

- Refined skill description guidance from strict "trigger-only" language to
  "trigger-oriented" wording: descriptions may mention user-facing outcomes
  when they help discovery, but must not summarize workflow steps.
- Cleaned active skill descriptions so they focus on trigger conditions and
  avoid workflow-summary shortcuts.

### Regression Coverage

- Added `tests/e2e/trigger-health-check.sh` and
  `tests/e2e/fixtures/trigger-health-matrix.json`.
- Wired Trigger Health checks into Layer 1 fast verification.
- Updated doctor and first-principles checks to lock the new terminology and
  context-pressure layer.

### Verification

- `bash scripts/bump-version.sh 1.1.5`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/first-principles-review-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.1.3 (2026-05-10)

### Patch Fix

- **Pre-change local patch suppression gate** — added a patch-shape gate to
  systematic debugging so agents must pause before turning quick local guards,
  keyword rules, fallback growth, consumer-side fixes, or sample-specific
  exceptions into implementation changes.
- **Owner-first repair discipline** — strengthened the debugging baseline so
  suspicious patch shapes must identify the canonical owner, source-of-truth
  boundary, and decision path before code edits.

### Regression Coverage

- Added `tests/e2e/debugging-patch-shape-gate-check.sh` to lock the new debugging
  policy and ensure the patch-shape gate remains present.
- Added the new debugging policy check to Layer 1 fast verification.
- Updated the TDD policy check to expect both patch-shape triage and ripple
  signal triage before risky fixes.

### Verification

- `bash scripts/bump-version.sh 1.1.3`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/debugging-patch-shape-gate-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.1.2 (2026-05-10)

### Patch Fix

- **Claude Code hook permissions** — marked `hooks/run-hook.cmd` as executable
  in Git so Linux / WSL2 Claude Code plugin caches can run the SessionStart
  wrapper without `/bin/sh: ... Permission denied`.
- **WSL2 troubleshooting note** — documented the old-cache workaround for
  `v1.1.0` / `v1.1.1` installs and directed users to upgrade or reinstall.

### Regression Coverage

- Added `tests/e2e/claude-hook-permissions-check.sh` to verify that
  `hooks/run-hook.cmd` and `hooks/session-start` are tracked as `100755`.
- Added the Claude hook permission check to Layer 1 fast verification.
- The check also parses `hooks/hooks.json` to confirm Claude Code SessionStart
  still routes through `hooks/run-hook.cmd`.

### Verification

- `bash scripts/bump-version.sh 1.1.2`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/claude-hook-permissions-check.sh`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `python scripts/aegis-doctor.py --json`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile none`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.1.1 (2026-05-09)

### Patch Fix

- **Workspace helper Python compatibility** — replaced
  `Path.write_text(..., newline="\n")` write paths in the workspace helper with
  an explicit LF writer based on `Path.open(..., newline="\n")`, so
  `new-work` works on Python versions where `Path.write_text` does not support
  the `newline` parameter.
- **Doctor config write compatibility** — applied the same LF writer to
  `scripts/aegis-doctor.py`, keeping complete-install verification compatible
  with older Python runtimes.

### Regression Coverage

- Added `tests/helpers/test_workspace_text_write_compat.py` to simulate the old
  `Path.write_text` signature and verify both `aegis-workspace.py new-work`
  and `aegis-doctor.py` config writing.
- Updated `tests/e2e/layer1-fast-check.sh` to run the compatibility test using
  a portable Python resolver (`python3`, `py -3`, then `python`).

### Verification

- `bash scripts/bump-version.sh 1.1.1`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python -m py_compile scripts/aegis-workspace.py scripts/aegis-doctor.py tests/helpers/test_workspace_text_write_compat.py`
- `python tests/helpers/test_workspace_text_write_compat.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `python scripts/aegis-doctor.py --json`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile none`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.1.0 (2026-05-09)

### First-Principles Review

- **New compositional skill** — added `first-principles-review` for explicit
  first-principles / Occam's razor requests and complex decisions with
  ambiguous goals, competing constraints, repeated fixes, fallback growth,
  duplicate owners, or architecture / product direction risk.
- **Compact decision surface** — the skill uses a five-line review shape:
  `First Principle`, `Non-negotiables`, `Assumptions to Drop`,
  `Smallest Sufficient Path`, and `Escalation Signal`.
- **Method-pack boundary preserved** — the new skill is advisory only. It does
  not create authoritative `GateDecision`, `PolicySnapshot`, or completion
  authority, and it is not loaded by the always-on `using-aegis` hot path.

### Leaner Routing And Project Bootstrap

- **Leaner `using-aegis` hot path** — tightened the always-loaded entrypoint so
  it stays a compact router, loads only clearly relevant skills, and avoids
  turning every small task into a full design ceremony.
- **Project Baseline Bootstrap** — active project questions and "what next"
  requests now check baseline candidates first. If no usable baseline exists,
  Aegis performs a bounded repo scan, creates an initial baseline only when
  there is sufficient project content, and still answers the user's original
  question.
- **Spec scope clarified** — introduced the distinction between lightweight
  `Spec Brief` for medium tasks and fuller `Design Spec` for high-complexity,
  architecture, contract, migration, cross-module, or ambiguous behavior work.
- **Lazy workspace support** — normal Q&A, status checks, tiny edits, and
  low-risk single-file changes should not create project records. Baseline,
  spec, plan, work, and evidence records are created only when the workflow
  needs persistent project evidence.

### Install Readiness And Host Boundaries

- **Aegis doctor** — added `scripts/aegis-doctor.py` to verify key skills,
  current hot-path content, method-pack root, workspace helper availability,
  absence of a live `docs/aegis/` workspace in the method-pack repository, and
  optional host skill discovery root freshness.
- **Complete install guidance** — README and host docs now ask agents to verify
  that Aegis is fully available, including skill discovery and project
  workspace support.
- **Skills-only boundary documented** — known limitations and compatibility
  docs now distinguish skill discovery from full project workspace support.
  Copy-only / skills-only installs can expose workflows, but they do not prove
  complete workspace helper availability.

### Verification

- `bash scripts/bump-version.sh 1.1.0`
- `git diff --check`
- `python -m py_compile scripts/aegis-doctor.py scripts/aegis-workspace.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `python scripts/aegis-doctor.py --json`
- `bash tests/e2e/first-principles-review-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.0.17 (2026-05-08)

### 用户入口体验优化

- **安装 / 更新提示词可直接复制** — `README.md` 与 `README.zh-CN.md`
  中的安装和更新提示词已改为代码块，用户可以直接复制给 AI 编程 agent，
  让它识别当前宿主、选择正确路径、完成安装或更新，并验证 Aegis skills
  是否可发现。
- **轻量全局规则模板** — 新增可复制的 Lite Global Rules / 轻量全局规则
  入口，并放在“更新 Aegis”之后，帮助用户更稳定地触发 Aegis skill，
  同时避免把完整 workflow 塞进全局规则。
- **高级模板保留为进阶选项** — 完整全局规则模板仍然保留，适合治理要求
  更强的团队或大型项目按需合并。

### 涟漪信号分诊

- **前置影响面分诊** — 新增 `Ripple Signal Triage`，作为代码修改前的
  依赖影响面分诊入口。共享模块、跨模块行为、契约、缓存、持久化、
  导出 / 回读、fallback、adapter、重复 owner、producer / consumer 边界等
  信号命中时，agent 需要先分诊再进入代码更改。
- **现有机制统一收口** — `ImpactStatementDraft` 承接涟漪分诊结果，
  双轨治理承接旧 owner、fallback、adapter、legacy path 与退役边界，
  `systematic-debugging` 在候选修复命中信号时先分诊再修复，
  `test-driven-development` 扩大验证范围到 producer + consumer 或真实用户路径，
  `writing-plans` 记录 owner、下游、契约、事实源和验证范围变化。
- **后置复核保持轻量** — 7 维架构检查中的 `Cascade proliferation` 保留为
  实施后的复核项，形成“实施前分诊、实施中承接、实施后复核”的闭环。

### 测试护栏

- **快速修 bug 场景覆盖** — Scenario B bug-fix 现在模拟“用户要求快速修
  共享缓存 / export-readback 相关 bug”的压力场景，验证 agent 仍然会先触发
  `Ripple Signal Triage`，而不是直接进入代码修改。
- **assistant 侧行为断言** — `analyze-transcript.sh` 新增
  `assistantMustContain`，确保关键行为必须出现在 assistant 输出中，避免只因
  用户 prompt 自带关键词而误判通过。
- **策略检查同步** — `tdd-policy-check.sh` 增加涟漪分诊相关护栏，确认流程
  基线、系统化调试、TDD 和 Scenario B 都承接这条纪律。

### Verification

- `bash scripts/bump-version.sh 1.0.17`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/layer2-behavior-check.sh`
- `bash tests/e2e/layer3-scenario-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

### Boundary

This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v1.0.15 (2026-05-07)

### Helper-Backed Task Lifecycle

- **Workspace helper v2** — extended `scripts/aegis-workspace.py` with
  `new-work`, `add-checkpoint`, `add-evidence`, `add-drift-check`, and
  `bundle` commands for target-project `docs/aegis/work/YYYY-MM-DD-<slug>/`
  records.
- **Structural proof bundle** — the helper can assemble `gate-input-pack.json`
  and `proof-bundle.md` as review / handoff packages for future runtime input.
  They remain advisory Method Pack records, not authoritative gate decisions.
- **Safer lifecycle creation** — `new-work` rejects duplicate work directories
  and nested work slugs so existing target-project records are not silently
  overwritten.

### Skill Wiring And Integrity Gates

- **High-value writer paths routed through the helper** — `using-aegis`,
  `brainstorming`, `writing-plans`, `test-driven-development`,
  `systematic-debugging`, `long-task-continuation`, and
  `verification-before-completion` now point to helper-backed workspace
  creation, lifecycle updates, bundle assembly, or workspace checks where
  relevant.
- **Current docs updated** — process, artifact schema, and known-limitations
  docs now describe helper-backed lifecycle records and retain the
  method-pack/runtime-core authority boundary.
- **Wiring regression added** — `workspace-helper-wiring-check.sh` verifies that
  skills writing `docs/aegis/` records keep routing through the shared helper or
  run helper checks.

### README Link Cleanup

- Updated the Linux.do badge link in both English and Chinese README files to
  point at the project topic page.

### Verification

- `bash scripts/bump-version.sh 1.0.15`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/aegis-workspace-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- `bash tests/e2e/long-task-continuation-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.0.14 (2026-05-07)

### Workspace Helper And Integrity Checks

- **Target-project workspace helper** — added `scripts/aegis-workspace.py`
  with `init`, `check`, `append-index`, and `validate-artifact` commands for
  target-project `docs/aegis/` workspaces.
- **Workspace completeness checks** — the helper now validates required
  workspace files, `BASELINE-GOVERNANCE.md` headings, `INDEX.md` coverage for
  markdown artifacts, and rejects unsafe/outside-path index entries.
- **No repository-local live workspace** — the Aegis method-pack repository
  still does not pre-create a root `docs/aegis/`; that workspace belongs to the
  user's target project.

### Runtime-Ready Artifact Validation

- **JSON sidecar validation** — added structural validation for the current
  runtime-ready artifact schemas:
  `TaskIntentDraft`, `BaselineReadSetHint`, `ImpactStatementDraft`,
  `EvidenceBundleDraft`, `GateInputPack`, `TodoCheckpointDraft`,
  `ResumeStateHint`, and `DriftCheckDraft`.
- **Advisory boundary retained** — artifact validation checks shape,
  `schemaVersion`, and boundary-sensitive fields only. It does not determine
  evidence sufficiency, produce authoritative `GateDecision`, or grant
  `completion authority`.

### Skill And Test Integration

- **Long-task continuation helper path** — `long-task-continuation` now routes
  `docs/aegis/work/<slug>/` records through the shared workspace helper and
  documents optional checkpoint, resume, drift, and evidence sidecars.
- **Workflow docs aligned** — brainstorming, writing-plans, TDD,
  verification-before-completion, and using-aegis guidance now point to the
  helper-backed workspace path where relevant.
- **Release gates expanded** — added `tests/e2e/aegis-workspace-check.sh` and
  wired it into the fast e2e layer.

### Verification

- `bash scripts/bump-version.sh 1.0.14`
- `git diff --check`
- `python -m py_compile scripts/aegis-workspace.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/aegis-workspace-check.sh`
- `bash tests/e2e/long-task-continuation-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.0.13 (2026-05-06)

### Method Baseline Convergence

- **Current authority docs normalized** — aligned the public current baseline
  docs to a single English-first structure (`Status`, `Document Scope`,
  `Bottom Line Up Front`, and consistent section naming) so product boundary,
  process baseline, activation mode, runtime-ready boundary, host snapshot,
  limitations, and rule layering now read as one coherent method-pack surface.
- **Dual-track governance docs simplified** — retired the separate public
  Chinese duplicate of dual-track governance and kept the public current set on
  one canonical document path.
- **Repository guide sync** — updated `AGENTS.md` and `docs/current/README.md`
  so the public authority map matches the trimmed current-doc surface.

### Prompt Hygiene And Debugging Tightening

- **Prompt hygiene baseline refined** — strengthened the wording around bounded
  evidence intake, repeated error-text re-entry, and host-side context
  discipline so Aegis stays evidence-rich without encouraging raw context
  inflation.
- **Systematic debugging closure clarified** — tightened the
  `systematic-debugging` skill around stop conditions, hard-signal placement,
  differential diagnosis, repair vs retirement closure, and confidence rules.
- **TDD / context-budget assertions synced** — updated the e2e checks so the
  policy tests match the refreshed baseline wording instead of stale phrasing.

### Verification

- `bash scripts/bump-version.sh 1.0.13`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

## v1.0.12 (2026-05-06)

### Aegis Project Workspace — Ecosystem Closed Loop

- **Hard binary workspace creation** — replaced the ambiguous "lazy creation"
  policy with explicit triggers: brainstorming design doc write, writing-plans
  save, and systematic-debugging Quality Gate for non-trivial tasks. Global
  install never writes project files; active projects create workspace
  immediately when a trigger fires.
- **Single canonical paths** — eliminated the dual-path ambiguity (`work/` vs
  `specs/`/`plans/`). Spec always goes to `specs/`, plan always to `plans/`,
  process trail stays in `work/<slug>/`. No more "promote to" uncertainty.
- **BASELINE-GOVERNANCE.md** — each project gets a constitution-level governance
  file defining architecture defect vs drift, baseline check protocol, and 7
  dimensions of architecture review. Triggered on first workspace creation by
  any entry path.
- **7-dimension architecture review** — operationalized the architecture
  retrospective across 7 measurable dimensions: ownership integrity, module
  boundaries, contract changes, cascade proliferation, dependency direction,
  retirement completeness, and entropy flow. Results mapped to Reflection
  checklist to prevent findings from being lost.
- **Mid-task complexity escalation** — if a task escalates from low to medium
  complexity mid-stream, the agent pauses, initializes workspace, and backfills
  required artifacts before continuing.
- **CONTEXT.md vs baseline/ boundary** — clarified separation: CONTEXT.md owns
  domain language, baseline/ owns technical architecture snapshots. Both
  skills (establishing-project-context, brainstorming) updated accordingly.
- **code-reviewer agent 7-dimension alignment** — code-reviewer now reports
  architecture review findings per dimension (PASS/FINDING/RISK) with severity
  and recommended action.

### Host Adapter Expansion

- **CodeBuddy** — added `.codebuddy-plugin/` skeleton with plugin metadata and
  marketplace manifest. Native `SKILL.md` discovery supports manual install.
  Installation guide in `docs/README.codebuddy.md`.
- **DeepSeek-TUI** — confirmed native `SKILL.md` discovery compatible. Manual
  install via skill directory copy. Installation guide in
  `docs/README.deepseek-tui.md`.
- **Trae** — confirmed native `SKILL.md` discovery compatible. Manual install
  via `.trae/skills/` directory. Installation guide in
  `docs/README.trae.md`.
- **Host compatibility matrix** — updated with CodeBuddy, DeepSeek-TUI, and
  Trae status entries. Release checklist and authority docs sync'd.
- **sync-to-codex-plugin.sh** — added `.codebuddy-plugin/`, `.cursor/`, and
  `.windsurf/` to EXCLUDES to prevent cross-host file leakage.
- **version-bump.json** — added `.codebuddy-plugin/` entries for consistent
  version management across all host manifests.

### Known Limitations

- Recorded 4 new known limitations: INDEX.md append dependency on workflow
  steps, low-complexity task workspace window, BASELINE-GOVERNANCE.md template
  quality dependency, and 7-dimension qualitative judgment dependency.

## v1.0.11 (2026-05-06)

### Systematic Debugging Depth Upgrade

- **Open-ended diagnostic chain** — upgraded `systematic-debugging` from a fixed
  four-layer check into a deeper L1-L7 diagnostic chain: symptom, logic, system,
  architecture, cross-system contract, platform/framework constraint, and spec
  gap. Architecture is no longer treated as the automatic endpoint; the chain
  stops at the deepest evidence-backed root cause or a terminal boundary.
- **Hard signal gate** — added H/T/D hard signals to debugging completion:
  H-class signals force further drilling, T-class signals switch the work into
  mitigation mode, and D-class signals define the minimum depth needed before a
  fix can be presented as complete.
- **Post-fix differential diagnosis** — added a required diagnosis step when a
  fix only partially resolves a symptom, separating incomplete fixes, wrong-depth
  patches, compound root causes, and chain-causal failures.
- **Process baseline alignment** — updated the method-layer process baseline and
  root-cause tracing reference so the debugging workflow, examples, and current
  authority docs all describe the same diagnostic model.

### Public Current Docs Trim

- **Smaller public current surface** — reduced `docs/current` to the public
  baseline docs needed by users, contributors, host installs, and release
  verification.
- **Local archive retired from git** — moved internal implementation records,
  private smoke notes, cutover plans, and migration checklists into local
  `docs/archive/`, then ignored that directory so those records stay out of the
  public repository.
- **Reference cleanup** — updated public docs, e2e fixtures, and explicit skill
  request tests so they reference the retained current baseline instead of
  archived process records.

### Verification

- `git diff --check`
- `bash -n tests/explicit-skill-requests/run-test.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile none`

## v1.0.10 (2026-05-06)

### Host Adapter Expansion

- **Windsurf host adapter** — added `.windsurf/INSTALL.md` with global and
  workspace install paths (macOS / Linux / Windows). Windsurf discovers
  skills via agentskills.io native discovery at `.windsurf/skills/` (workspace)
  or `~/.codeium/windsurf/skills/` (global). Each Aegis skill symlinked with
  `aegis-` prefix, invocable via `@aegis-<skill-name>` in Cascade.
- **Cursor host adapter** — added `.cursor/INSTALL.md` with skills symlink
  install as the primary path and VS Code extension registration as an
  alternative. Cursor discovers skills from `.cursor/skills/` and supports the
  `.cursor-plugin/plugin.json` extension manifest.
- **Kimi Code CLI compatibility confirmed** — Kimi Code CLI auto-discovers
  skills from `.agents/skills/` (same path as Codex). The existing Aegis
  minimal-install prompt works directly; no separate adapter needed.
  Configuration supports 6 provider types: `kimi`, `openai_legacy`,
  `openai_responses`, `anthropic`, `gemini`, and `vertexai`.
- **Warp compatibility confirmed** — Warp hosts third-party CLI agents
  (Claude Code, Codex, OpenCode) rather than providing its own skills system.
  Users install Aegis on their chosen CLI agent; no separate adapter needed.
- **Host compatibility matrix updated** — `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
  now reflects all 8 hosts (Codex, OpenCode, Claude Code, Cursor, Windsurf,
  Gemini CLI, Kimi Code CLI, Warp), with evidence levels and adapter status.
- **AGENTS.md** — added `.cursor/` and `.windsurf/` to the plugin-installable
  surface list.

### Verification

- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- Verified: 17 `aegis-*` symlinks created for both Windsurf and Cursor paths

## v1.0.9 (2026-05-05)

### Skill File Cognitive Load Reduction

- **Execute summaries** — added top-level `# Execute` blocks to 6 core skill files
  (`systematic-debugging`, `test-driven-development`, `verification-before-completion`,
  `brainstorming`, `subagent-driven-development`, `writing-plans`). Each block is a
  5-8 line condensed decision tree that agents can scan without reading the full
  reference prose.
- **Content deduplication** — removed narrative prose that repeated executable
  instructions already present in the Execute block, and removed motivational text,
  dot diagrams, and redundant rationalization tables that added cognitive load
  without improving decision quality.
- **51% total line reduction** across the 6 files (from 1,452 to 712 lines) while
  preserving all rule semantics, compliance-check phrases, and dual-track governance
  requirements.
- **Verification** — all Layer 1 fast checks, context budget checks, governance
  completion contract checks, TDD policy checks, and Codex plugin sync tests pass.

### Verification

- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`

## v1.0.8 (2026-05-05)

### Context Control And Explicit Activation

- **Explicit activation mode** — added a cross-host `auto|explicit` activation
  profile. Supported bootstrap hooks now read `AEGIS_ACTIVATION_MODE` or the
  user-local `~/.config/aegis/config.toml`; `explicit` mode stops automatic
  bootstrap injection while keeping direct Aegis skill calls available.
- **Host documentation updates** — documented the activation mode flow in the
  root README files and Codex, OpenCode, and Claude Code install guides, with
  host-specific caveats where native skill routing remains host-controlled.
- **Bounded context intake** — added host context intake discipline to the
  prompt hygiene boundary: large logs, transcripts, histories, diffs, and test
  output should flow through index -> window -> excerpt instead of broad raw
  prompt ingestion.
- **Log window helper** — added `scripts/log-window.sh` for small-window log
  inspection, including directory refusal and bounded window limits.
- **Guardrail tests** — added activation mode checks to the Layer 1 fast suite
  and expanded context budget checks for the bounded evidence intake workflow.

### Verification

- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `bash tests/opencode/run-tests.sh --integration`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
- `git diff --check`

## v1.0.6 (2026-05-05)

### Public Repository Hardening

- **Prompt hygiene boundary** — added a current authority document for how
  external tools, logs, memories, transcripts, and search results enter prompt
  context. Large raw payloads are treated as evidence candidates, summarized
  first, and read back only when needed for verification.
- **Governance completion contract** — strengthened the completion gate for
  cleanup, migration, compatibility, namespace cutover, public release,
  deprecation, policy boundary, and retirement work. Governance closeout now
  requires repair track, retirement track, residual risk, and verification
  evidence in the user's language.
- **Public surface cleanup** — removed upstream-specific historical specs from
  the user-visible docs tree and narrowed stale `superpowers` references away
  from active paths.
- **Contributor guidance refresh** — rewrote `AGENTS.md`, `CLAUDE.md`, and
  Claude Code guidance for public repository use instead of private workflow
  assumptions.
- **Test surface split** — documented tracked public quality verification
  suites and added `tests/local/` as an ignored home for development-only test
  cases.

### Verification

- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --bootstrap`

## v1.0.0 (2026-05-03)

### Aegis Method Pack 1.0

- **Aegis version reset** — reset public package and plugin manifests to
  `1.0.0` for the Aegis Method Pack release line.
- **Complexity routing before implementation** — `using-aegis` now directs
  agents to classify task complexity before coding. Medium- and
  high-complexity work must produce planning artifacts and atomic tasks before
  TDD; high-complexity work may require spec/design review first.
- **TDD preflight gate** — `test-driven-development` is now explicitly framed
  as the implementation discipline for approved atomic tasks, not the first
  entrypoint for multi-file, multi-flow, contract, migration, or ambiguous
  product work.
- **Lazy Aegis Project Workspace** — `brainstorming` and `writing-plans` now
  describe task-scoped `docs/aegis/work/...` records and only promote reusable
  outputs into `baseline/`, `adr/`, `specs/`, or `plans/` when needed. Global
  installation still does not write project files.
- **Update prompt docs** — README files now include a copyable prompt users can
  give their AI coding agent to update an installed Aegis checkout from the
  latest `main` branch.

### Verification

- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/run-all.sh --bootstrap`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`

## Legacy Superpowers Release Notes

## v5.0.7 (2026-03-31)

### GitHub Copilot CLI Support

- **SessionStart context injection** — Copilot CLI v1.0.11 added support for `additionalContext` in sessionStart hook output. The session-start hook now detects the `COPILOT_CLI` environment variable and emits the SDK-standard `{ "additionalContext": "..." }` format, giving Copilot CLI users the full superpowers bootstrap at session start. (Original fix by @culinablaz in PR #910)
- **Tool mapping** — added `references/copilot-tools.md` with the full Claude Code to Copilot CLI tool equivalence table
- **Skill and README updates** — added Copilot CLI to the `using-superpowers` skill's platform instructions and README installation section

### OpenCode Fixes

- **Skills path consistency** — the bootstrap text no longer advertises a misleading `configDir/skills/superpowers/` path that didn't match the runtime path. The agent should use the native `skill` tool, not navigate to files by path. Tests now use consistent paths derived from a single source of truth. (#847, #916)
- **Bootstrap as user message** — moved bootstrap injection from `experimental.chat.system.transform` to `experimental.chat.messages.transform`, prepending to the first user message instead of adding a system message. Avoids token bloat from system messages repeated every turn (#750) and fixes compatibility with Qwen and other models that break on multiple system messages (#894).

## v5.0.6 (2026-03-24)

### Inline Self-Review Replaces Subagent Review Loops

The subagent review loop (dispatching a fresh agent to review plans/specs) doubled execution time (~25 min overhead) without measurably improving plan quality. Regression testing across 5 versions with 5 trials each showed identical quality scores regardless of whether the review loop ran.

- **brainstorming** — replaced Spec Review Loop (subagent dispatch + 3-iteration cap) with inline Spec Self-Review checklist: placeholder scan, internal consistency, scope check, ambiguity check
- **writing-plans** — replaced Plan Review Loop (subagent dispatch + 3-iteration cap) with inline Self-Review checklist: spec coverage, placeholder scan, type consistency
- **writing-plans** — added explicit "No Placeholders" section defining plan failures (TBD, vague descriptions, undefined references, "similar to Task N")
- Self-review catches 3-5 real bugs per run in ~30s instead of ~25 min, with comparable defect rates to the subagent approach

### Brainstorm Server

- **Session directory restructured** — the brainstorm server session directory now contains two peer subdirectories: `content/` (HTML files served to the browser) and `state/` (events, server-info, pid, log). Previously, server state and user interaction data were stored alongside served content, making them accessible over HTTP. The `screen_dir` and `state_dir` paths are both included in the server-started JSON. (Reported by 吉田仁)

### Bug Fixes

- **Owner-PID lifecycle fixes** — the brainstorm server's owner-PID monitoring had two bugs causing false shutdowns within 60 seconds: (1) EPERM from cross-user PIDs (Tailscale SSH, etc.) was treated as "process dead", and (2) on WSL the grandparent PID resolves to a short-lived subprocess that exits before the first lifecycle check. Fixed by treating EPERM as "alive" and validating the owner PID at startup — if it's already dead, monitoring is disabled and the server relies on the 30-minute idle timeout. This also removes the Windows/MSYS2-specific carve-out from `start-server.sh` since the server now handles it generically. (#879)
- **writing-skills** — corrected false claim that SKILL.md frontmatter supports "only two fields"; now says "two required fields" and links to the agentskills.io specification for all supported fields (PR #882 by @arittr)

### Codex App Compatibility

- **codex-tools** — added named agent dispatch mapping documenting how to translate Claude Code's named agent types to Codex's `spawn_agent` with worker roles (PR #647 by @arittr)
- **codex-tools** — added environment detection and Codex App finishing sections for worktree-aware skills (by @arittr)
- **Design spec** — added Codex App compatibility design spec (PRI-823) covering read-only environment detection, worktree-safe skill behavior, and sandbox fallback patterns (by @arittr)

## v5.0.5 (2026-03-17)

### Bug Fixes

- **Brainstorm server ESM fix** — renamed `server.js` → `server.cjs` so the brainstorming server starts correctly on Node.js 22+ where the root `package.json` `"type": "module"` caused `require()` to fail. (PR #784 by @sarbojitrana, fixes #774, #780, #783)
- **Brainstorm owner-PID on Windows** — skip PID lifecycle monitoring on Windows/MSYS2 where the PID namespace is invisible to Node.js, preventing the server from self-terminating after 60 seconds. (#770, docs from PR #768 by @lucasyhzlu-debug)
- **stop-server.sh reliability** — verify the server process actually died before reporting success. SIGTERM + 2s wait + SIGKILL fallback. (#723)

### Changed

- **Execution handoff** — restore user choice between subagent-driven and inline execution after plan writing. Subagent-driven is recommended but no longer mandatory.

## v5.0.4 (2026-03-16)

### Review Loop Refinements

Dramatically reduces token usage and speeds up spec and plan reviews by eliminating unnecessary review passes and tightening reviewer focus.

- **Single whole-plan review** — plan reviewer now reviews the complete plan in one pass instead of chunk-by-chunk. Removed all chunk-related concepts (`## Chunk N:` headings, 1000-line chunk limits, per-chunk dispatch).
- **Raised the bar for blocking issues** — both spec and plan reviewer prompts now include a "Calibration" section: only flag issues that would cause real problems during implementation. Minor wording, stylistic preferences, and formatting quibbles should not block approval.
- **Reduced max review iterations** — from 5 to 3 for both spec and plan review loops. If the reviewer is calibrated correctly, 3 rounds is plenty.
- **Streamlined reviewer checklists** — spec reviewer trimmed from 7 categories to 5; plan reviewer from 7 to 4. Removed formatting-focused checks (task syntax, chunk size) in favor of substance (buildability, spec alignment).

### OpenCode

- **One-line plugin install** — OpenCode plugin now auto-registers the skills directory via a `config` hook. No symlinks or `skills.paths` config needed. Install is just adding one line to `opencode.json`. (PR #753)
- **Added `package.json`** so OpenCode can install superpowers as an npm package from git.

### Bug Fixes

- **Verify server actually stopped** — `stop-server.sh` now confirms the process is dead before reporting success. SIGTERM + 2s wait + SIGKILL fallback. Reports failure if the process survives. (PR #751)
- **Generic agent language** — brainstorm companion waiting page now says "the agent" instead of "Claude".

## v5.0.3 (2026-03-15)

### Cursor Support

- **Cursor hooks** — added `hooks/hooks-cursor.json` with Cursor's camelCase format (`sessionStart`, `version: 1`) and updated `.cursor-plugin/plugin.json` to reference it. Fixed platform detection in `session-start` to check `CURSOR_PLUGIN_ROOT` first (Cursor may also set `CLAUDE_PLUGIN_ROOT`). (Based on PR #709)

### Bug Fixes

- **Stop firing SessionStart hook on `--resume`** — the startup hook was re-injecting context on resumed sessions, which already have the context in their conversation history. The hook now fires only on `startup`, `clear`, and `compact`.
- **Bash 5.3+ hook hang** — replaced heredoc (`cat <<EOF`) with `printf` in `hooks/session-start`. Fixes indefinite hang on macOS with Homebrew bash 5.3+ caused by a bash regression with large variable expansion in heredocs. (#572, #571)
- **POSIX-safe hook script** — replaced `${BASH_SOURCE[0]:-$0}` with `$0` in `hooks/session-start`. Fixes "Bad substitution" error on Ubuntu/Debian where `/bin/sh` is dash. (#553)
- **Portable shebangs** — replaced `#!/bin/bash` with `#!/usr/bin/env bash` in all shell scripts. Fixes execution on NixOS, FreeBSD, and macOS with Homebrew bash where `/bin/bash` is outdated or missing. (#700)
- **Brainstorm server on Windows** — auto-detect Windows/Git Bash (`OSTYPE=msys*`, `MSYSTEM`) and switch to foreground mode, fixing silent server failure caused by `nohup`/`disown` process reaping. (#737)
- **Codex docs fix** — replaced deprecated `collab` flag with `multi_agent` in Codex documentation. (PR #749)

## v5.0.2 (2026-03-11)

### Zero-Dependency Brainstorm Server

**Removed all vendored node_modules — server.js is now fully self-contained**

- Replaced Express/Chokidar/WebSocket dependencies with zero-dependency Node.js server using built-in `http`, `fs`, and `crypto` modules
- Removed ~1,200 lines of vendored `node_modules/`, `package.json`, and `package-lock.json`
- Custom WebSocket protocol implementation (RFC 6455 framing, ping/pong, proper close handshake)
- Native `fs.watch()` file watching replaces Chokidar
- Full test suite: HTTP serving, WebSocket protocol, file watching, and integration tests

### Brainstorm Server Reliability

- **Auto-exit after 30 minutes idle** — server shuts down when no clients are connected, preventing orphaned processes
- **Owner process tracking** — server monitors the parent harness PID and exits when the owning session dies
- **Liveness check** — skill verifies server is responsive before reusing an existing instance
- **Encoding fix** — proper `<meta charset="utf-8">` on served HTML pages

### Subagent Context Isolation

- All delegation skills (brainstorming, dispatching-parallel-agents, requesting-code-review, subagent-driven-development, writing-plans) now include context isolation principle
- Subagents receive only the context they need, preventing context window pollution

## v5.0.1 (2026-03-10)

### Agentskills Compliance

**Brainstorm-server moved into skill directory**

- Moved `lib/brainstorm-server/` → `skills/brainstorming/scripts/` per the [agentskills.io](https://agentskills.io) specification
- All `${CLAUDE_PLUGIN_ROOT}/lib/brainstorm-server/` references replaced with relative `scripts/` paths
- Skills are now fully portable across platforms — no platform-specific env vars needed to locate scripts
- `lib/` directory removed (was the last remaining content)

### New Features

**Gemini CLI extension**

- Native Gemini CLI extension support via `gemini-extension.json` and `GEMINI.md` at repo root
- `GEMINI.md` @imports `using-superpowers` skill and tool mapping table at session start
- Gemini CLI tool mapping reference (`skills/using-superpowers/references/gemini-tools.md`) — translates Claude Code tool names (Read, Write, Edit, Bash, etc.) to Gemini CLI equivalents (read_file, write_file, replace, etc.)
- Documents Gemini CLI limitations: no subagent support, skills fall back to `executing-plans`
- Extension root at repo root for cross-platform compatibility (avoids Windows symlink issues)
- Install instructions added to README

### Improvements

**Multi-platform brainstorm server launch**

- Per-platform launch instructions in visual-companion.md: Claude Code (default mode), Codex (auto-foreground via `CODEX_CI`), Gemini CLI (`--foreground` with `is_background`), and fallback for other environments
- Server now writes startup JSON to `$SCREEN_DIR/.server-info` so agents can find the URL and port even when stdout is hidden by background execution

**Brainstorm server dependencies bundled**

- `node_modules` vendored into the repo so the brainstorm server works immediately on fresh plugin installs without requiring `npm` at runtime
- Removed `fsevents` from bundled deps (macOS-only native binary; chokidar falls back gracefully without it)
- Fallback auto-install via `npm install` if `node_modules` is missing

**OpenCode tool mapping fix**

- `TodoWrite` → `todowrite` (was incorrectly mapped to `update_plan`); verified against OpenCode source

### Bug Fixes

**Windows/Linux: single quotes break SessionStart hook** (#577, #529, #644, PR #585)

- Single quotes around `${CLAUDE_PLUGIN_ROOT}` in hooks.json fail on Windows (cmd.exe doesn't recognize single quotes as path delimiters) and on Linux (single quotes prevent variable expansion)
- Fix: replaced single quotes with escaped double quotes — works across macOS bash, Windows cmd.exe, Windows Git Bash, and Linux, with and without spaces in paths
- Verified on Windows 11 (NT 10.0.26200.0) with Claude Code 2.1.72 and Git for Windows

**Brainstorming spec review loop skipped** (#677)

- The spec review loop (dispatch spec-document-reviewer subagent, iterate until approved) existed in the prose "After the Design" section but was missing from the checklist and process flow diagram
- Since agents follow the diagram and checklist more reliably than prose, the spec review step was being skipped entirely
- Added step 7 (spec review loop) to the checklist and corresponding nodes to the dot graph
- Tested with `claude --plugin-dir` and `claude-session-driver`: worker now correctly dispatches the reviewer

**Cursor install command** (PR #676)

- Fixed Cursor install command in README: `/plugin-add` → `/add-plugin` (confirmed via Cursor 2.5 release announcement)

**User review gate in brainstorming** (#565)

- Added explicit user review step between spec completion and writing-plans handoff
- User must approve the spec before implementation planning begins
- Checklist, process flow, and prose updated with the new gate

**Session-start hook emits context only once per platform**

- Hook now detects whether it's running in Claude Code or another platform
- Emits `hookSpecificOutput` for Claude Code, `additional_context` for others — prevents double context injection

**Linting fix in token analysis script**

- `except:` → `except Exception:` in `tests/claude-code/analyze-token-usage.py`

### Maintenance

**Removed dead code**

- Deleted `lib/skills-core.js` and its test (`tests/opencode/test-skills-core.js`) — unused since February 2026
- Removed skills-core existence check from `tests/opencode/test-plugin-loading.sh`

### Community

- @karuturi — Claude Code official marketplace install instructions (PR #610)
- @mvanhorn — session-start hook dual-emit fix, OpenCode tool mapping fix
- @daniel-graham — linting fix for bare except
- PR #585 author — Windows/Linux hooks quoting fix

---

## v5.0.0 (2026-03-09)

### Breaking Changes

**Specs and plans directory restructured**

- Specs (brainstorming output) now save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Plans (writing-plans output) now save to `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- User preferences for spec/plan locations override these defaults
- All internal skill references, test files, and example paths updated to match
- Migration: move existing files from `docs/plans/` to new locations if desired

**Subagent-driven development mandatory on capable harnesses**

Writing-plans no longer offers a choice between subagent-driven and executing-plans. On harnesses with subagent support (Claude Code, Codex), subagent-driven-development is required. Executing-plans is reserved for harnesses without subagent capability, and now tells the user that Superpowers works better on a subagent-capable platform.

**Executing-plans no longer batches**

Removed the "execute 3 tasks then stop for review" pattern. Plans now execute continuously, stopping only for blockers.

**Slash commands deprecated**

`/brainstorm`, `/write-plan`, and `/execute-plan` now show deprecation notices pointing users to the corresponding skills. Commands will be removed in the next major release.

### New Features

**Visual brainstorming companion**

Optional browser-based companion for brainstorming sessions. When a topic would benefit from visuals, the brainstorming skill offers to show mockups, diagrams, comparisons, and other content in a browser window alongside terminal conversation.

- `lib/brainstorm-server/` — WebSocket server with browser helper library, session management scripts, and dark/light themed frame template ("Superpowers Brainstorming" with GitHub link)
- `skills/brainstorming/visual-companion.md` — Progressive disclosure guide for server workflow, screen authoring, and feedback collection
- Brainstorming skill adds a visual companion decision point to its process flow: after exploring project context, the skill evaluates whether upcoming questions involve visual content and offers the companion in its own message
- Per-question decision: even after accepting, each question is evaluated for whether browser or terminal is more appropriate
- Integration tests in `tests/brainstorm-server/`

**Document review system**

Automated review loops for spec and plan documents using subagent dispatch:

- `skills/brainstorming/spec-document-reviewer-prompt.md` — Reviewer checks completeness, consistency, architecture, and YAGNI
- `skills/writing-plans/plan-document-reviewer-prompt.md` — Reviewer checks spec alignment, task decomposition, file structure, and file size
- Brainstorming dispatches spec reviewer after writing the design doc
- Writing-plans includes chunk-based plan review loop after each section
- Review loops repeat until approved or escalate after 5 iterations
- End-to-end tests in `tests/claude-code/test-document-review-system.sh`
- Design spec and implementation plan in `docs/superpowers/`

**Architecture guidance across the skill pipeline**

Design-for-isolation and file-size-awareness guidance added to brainstorming, writing-plans, and subagent-driven-development:

- **Brainstorming** — New sections: "Design for isolation and clarity" (clear boundaries, well-defined interfaces, independently testable units) and "Working in existing codebases" (follow existing patterns, targeted improvements only)
- **Writing-plans** — New "File Structure" section: map out files and responsibilities before defining tasks. New "Scope Check" backstop: catch multi-subsystem specs that should have been decomposed during brainstorming
- **SDD implementer** — New "Code Organization" section (follow plan's file structure, report concerns about growing files) and "When You're in Over Your Head" escalation guidance
- **SDD code quality reviewer** — Now checks architecture, unit decomposition, plan conformance, and file growth
- **Spec/plan reviewers** — Architecture and file size added to review criteria
- **Scope assessment** — Brainstorming now assesses whether a project is too large for a single spec. Multi-subsystem requests are flagged early and decomposed into sub-projects, each with its own spec → plan → implementation cycle

**Subagent-driven development improvements**

- **Model selection** — Guidance for choosing model capability by task type: cheap models for mechanical implementation, standard for integration, capable for architecture and review
- **Implementer status protocol** — Subagents now report DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT. Controller handles each status appropriately: re-dispatching with more context, upgrading model capability, breaking tasks apart, or escalating to human

### Improvements

**Instruction priority hierarchy**

Added explicit priority ordering to using-superpowers:

1. User's explicit instructions (CLAUDE.md, AGENTS.md, direct requests) — highest priority
2. Superpowers skills — override default system behavior
3. Default system prompt — lowest priority

If CLAUDE.md or AGENTS.md says "don't use TDD" and a skill says "always use TDD," the user's instructions win.

**SUBAGENT-STOP gate**

Added `<SUBAGENT-STOP>` block to using-superpowers. Subagents dispatched for specific tasks now skip the skill instead of activating the 1% rule and invoking full skill workflows.

**Multi-platform improvements**

- Codex tool mapping moved to progressive disclosure reference file (`references/codex-tools.md`)
- Platform Adaptation pointer added so non-Claude-Code platforms can find tool equivalents
- Plan headers now address "agentic workers" instead of "Claude" specifically
- Collab feature requirement documented in `docs/README.codex.md`

**Writing-plans template updates**

- Plan steps now use checkbox syntax (`- [ ] **Step N:**`) for progress tracking
- Plan header references both subagent-driven-development and executing-plans with platform-aware routing

---

## v4.3.1 (2026-02-21)

### Added

**Cursor support**

Superpowers now works with Cursor's plugin system. Includes a `.cursor-plugin/plugin.json` manifest and Cursor-specific installation instructions in the README. The SessionStart hook output now includes an `additional_context` field alongside the existing `hookSpecificOutput.additionalContext` for Cursor hook compatibility.

### Fixed

**Windows: Restored polyglot wrapper for reliable hook execution (#518, #504, #491, #487, #466, #440)**

Claude Code's `.sh` auto-detection on Windows was prepending `bash` to the hook command, breaking execution. The fix:

- Renamed `session-start.sh` to `session-start` (extensionless) so auto-detection doesn't interfere
- Restored `run-hook.cmd` polyglot wrapper with multi-location bash discovery (standard Git for Windows paths, then PATH fallback)
- Exits silently if no bash is found rather than erroring
- On Unix, the wrapper runs the script directly via `exec bash`
- Uses POSIX-safe `dirname "$0"` path resolution (works on dash/sh, not just bash)

This fixes SessionStart failures on Windows with spaces in paths, missing WSL, `set -euo pipefail` fragility on MSYS, and backslash mangling.

## v4.3.0 (2026-02-12)

This fix should dramatically improve superpowers skills compliance and should reduce the chances of Claude entering its native plan mode unintentionally.

### Changed

**Brainstorming skill now enforces its workflow instead of describing it**

Models were skipping the design phase and jumping straight to implementation skills like frontend-design, or collapsing the entire brainstorming process into a single text block. The skill now uses hard gates, a mandatory checklist, and a graphviz process flow to enforce compliance:

- `<HARD-GATE>`: no implementation skills, code, or scaffolding until design is presented and user approves
- Explicit checklist (6 items) that must be created as tasks and completed in order
- Graphviz process flow with `writing-plans` as the only valid terminal state
- Anti-pattern callout for "this is too simple to need a design" — the exact rationalization models use to skip the process
- Design section sizing based on section complexity, not project complexity

**Using-superpowers workflow graph intercepts EnterPlanMode**

Added an `EnterPlanMode` intercept to the skill flow graph. When the model is about to enter Claude's native plan mode, it checks whether brainstorming has happened and routes through the brainstorming skill instead. Plan mode is never entered.

### Fixed

**SessionStart hook now runs synchronously**

Changed `async: true` to `async: false` in hooks.json. When async, the hook could fail to complete before the model's first turn, meaning using-superpowers instructions weren't in context for the first message.

## v4.2.0 (2026-02-05)

### Breaking Changes

**Codex: Replaced bootstrap CLI with native skill discovery**

The `superpowers-codex` bootstrap CLI, Windows `.cmd` wrapper, and related bootstrap content file have been removed. Codex now uses native skill discovery via `~/.agents/skills/superpowers/` symlink, so the old `use_skill`/`find_skills` CLI tools are no longer needed.

Installation is now just clone + symlink (documented in INSTALL.md). No Node.js dependency required. The old `~/.codex/skills/` path is deprecated.

### Fixes

**Windows: Fixed Claude Code 2.1.x hook execution (#331)**

Claude Code 2.1.x changed how hooks execute on Windows: it now auto-detects `.sh` files in commands and prepends `bash`. This broke the polyglot wrapper pattern because `bash "run-hook.cmd" session-start.sh` tries to execute the `.cmd` file as a bash script.

Fix: hooks.json now calls session-start.sh directly. Claude Code 2.1.x handles the bash invocation automatically. Also added .gitattributes to enforce LF line endings for shell scripts (fixes CRLF issues on Windows checkout).

**Windows: SessionStart hook runs async to prevent terminal freeze (#404, #413, #414, #419)**

The synchronous SessionStart hook blocked the TUI from entering raw mode on Windows, freezing all keyboard input. Running the hook async prevents the freeze while still injecting superpowers context.

**Windows: Fixed O(n^2) `escape_for_json` performance**

The character-by-character loop using `${input:$i:1}` was O(n^2) in bash due to substring copy overhead. On Windows Git Bash this took 60+ seconds. Replaced with bash parameter substitution (`${s//old/new}`) which runs each pattern as a single C-level pass — 7x faster on macOS, dramatically faster on Windows.

**Codex: Fixed Windows/PowerShell invocation (#285, #243)**

- Windows doesn't respect shebangs, so directly invoking the extensionless `superpowers-codex` script triggered an "Open with" dialog. All invocations now prefixed with `node`.
- Fixed `~/` path expansion on Windows — PowerShell doesn't expand `~` when passed as an argument to `node`. Changed to `$HOME` which expands correctly in both bash and PowerShell.

**Codex: Fixed path resolution in installer**

Used `fileURLToPath()` instead of manual URL pathname parsing to correctly handle paths with spaces and special characters on all platforms.

**Codex: Fixed stale skills path in writing-skills**

Updated `~/.codex/skills/` reference (deprecated) to `~/.agents/skills/` for native discovery.

### Improvements

**Worktree isolation now required before implementation**

Added `using-git-worktrees` as a required skill for both `subagent-driven-development` and `executing-plans`. Implementation workflows now explicitly require setting up an isolated worktree before starting work, preventing accidental work directly on main.

**Main branch protection softened to require explicit consent**

Instead of prohibiting main branch work entirely, the skills now allow it with explicit user consent. More flexible while still ensuring users are aware of the implications.

**Simplified installation verification**

Removed `/help` command check and specific slash command list from verification steps. Skills are primarily invoked by describing what you want to do, not by running specific commands.

**Codex: Clarified subagent tool mapping in bootstrap**

Improved documentation of how Codex tools map to Claude Code equivalents for subagent workflows.

### Tests

- Added worktree requirement test for subagent-driven-development
- Added main branch red flag warning test
- Fixed case sensitivity in skill recognition test assertions

---

## v4.1.1 (2026-01-23)

### Fixes

**OpenCode: Standardized on `plugins/` directory per official docs (#343)**

OpenCode's official documentation uses `~/.config/opencode/plugins/` (plural). Our docs previously used `plugin/` (singular). While OpenCode accepts both forms, we've standardized on the official convention to avoid confusion.

Changes:
- Renamed `.opencode/plugin/` to `.opencode/plugins/` in repo structure
- Updated all installation docs (INSTALL.md, README.opencode.md) across all platforms
- Updated test scripts to match

**OpenCode: Fixed symlink instructions (#339, #342)**

- Added explicit `rm` before `ln -s` (fixes "file already exists" errors on reinstall)
- Added missing skills symlink step that was absent from INSTALL.md
- Updated from deprecated `use_skill`/`find_skills` to native `skill` tool references

---

## v4.1.0 (2026-01-23)

### Breaking Changes

**OpenCode: Switched to native skills system**

Superpowers for OpenCode now uses OpenCode's native `skill` tool instead of custom `use_skill`/`find_skills` tools. This is a cleaner integration that works with OpenCode's built-in skill discovery.

**Migration required:** Skills must be symlinked to `~/.config/opencode/skills/superpowers/` (see updated installation docs).

### Fixes

**OpenCode: Fixed agent reset on session start (#226)**

The previous bootstrap injection method using `session.prompt({ noReply: true })` caused OpenCode to reset the selected agent to "build" on first message. Now uses `experimental.chat.system.transform` hook which modifies the system prompt directly without side effects.

**OpenCode: Fixed Windows installation (#232)**

- Removed dependency on `skills-core.js` (eliminates broken relative imports when file is copied instead of symlinked)
- Added comprehensive Windows installation docs for cmd.exe, PowerShell, and Git Bash
- Documented proper symlink vs junction usage for each platform

**Claude Code: Fixed Windows hook execution for Claude Code 2.1.x**

Claude Code 2.1.x changed how hooks execute on Windows: it now auto-detects `.sh` files in commands and prepends `bash `. This broke the polyglot wrapper pattern because `bash "run-hook.cmd" session-start.sh` tries to execute the .cmd file as a bash script.

Fix: hooks.json now calls session-start.sh directly. Claude Code 2.1.x handles the bash invocation automatically. Also added .gitattributes to enforce LF line endings for shell scripts (fixes CRLF issues on Windows checkout).

---

## v4.0.3 (2025-12-26)

### Improvements

**Strengthened using-superpowers skill for explicit skill requests**

Addressed a failure mode where Claude would skip invoking a skill even when the user explicitly requested it by name (e.g., "subagent-driven-development, please"). Claude would think "I know what that means" and start working directly instead of loading the skill.

Changes:
- Updated "The Rule" to say "Invoke relevant or requested skills" instead of "Check for skills" - emphasizing active invocation over passive checking
- Added "BEFORE any response or action" - the original wording only mentioned "response" but Claude would sometimes take action without responding first
- Added reassurance that invoking a wrong skill is okay - reduces hesitation
- Added new red flag: "I know what that means" → Knowing the concept ≠ using the skill

**Added explicit skill request tests**

New test suite in `tests/explicit-skill-requests/` that verifies Claude correctly invokes skills when users request them by name. Includes single-turn and multi-turn test scenarios.

## v4.0.2 (2025-12-23)

### Fixes

**Slash commands now user-only**

Added `disable-model-invocation: true` to all three slash commands (`/brainstorm`, `/execute-plan`, `/write-plan`). Claude can no longer invoke these commands via the Skill tool—they're restricted to manual user invocation only.

The underlying skills (`superpowers:brainstorming`, `superpowers:executing-plans`, `superpowers:writing-plans`) remain available for Claude to invoke autonomously. This change prevents confusion when Claude would invoke a command that just redirects to a skill anyway.

## v4.0.1 (2025-12-23)

### Fixes

**Clarified how to access skills in Claude Code**

Fixed a confusing pattern where Claude would invoke a skill via the Skill tool, then try to Read the skill file separately. The `using-superpowers` skill now explicitly states that the Skill tool loads skill content directly—no need to read files.

- Added "How to Access Skills" section to `using-superpowers`
- Changed "read the skill" → "invoke the skill" in instructions
- Updated slash commands to use fully qualified skill names (e.g., `superpowers:brainstorming`)

**Added GitHub thread reply guidance to receiving-code-review** (h/t @ralphbean)

Added a note about replying to inline review comments in the original thread rather than as top-level PR comments.

**Added automation-over-documentation guidance to writing-skills** (h/t @EthanJStark)

Added guidance that mechanical constraints should be automated, not documented—save skills for judgment calls.

## v4.0.0 (2025-12-17)

### New Features

**Two-stage code review in subagent-driven-development**

Subagent workflows now use two separate review stages after each task:

1. **Spec compliance review** - Skeptical reviewer verifies implementation matches spec exactly. Catches missing requirements AND over-building. Won't trust implementer's report—reads actual code.

2. **Code quality review** - Only runs after spec compliance passes. Reviews for clean code, test coverage, maintainability.

This catches the common failure mode where code is well-written but doesn't match what was requested. Reviews are loops, not one-shot: if reviewer finds issues, implementer fixes them, then reviewer checks again.

Other subagent workflow improvements:
- Controller provides full task text to workers (not file references)
- Workers can ask clarifying questions before AND during work
- Self-review checklist before reporting completion
- Plan read once at start, extracted to TodoWrite

New prompt templates in `skills/subagent-driven-development/`:
- `implementer-prompt.md` - Includes self-review checklist, encourages questions
- `spec-reviewer-prompt.md` - Skeptical verification against requirements
- `code-quality-reviewer-prompt.md` - Standard code review

**Debugging techniques consolidated with tools**

`systematic-debugging` now bundles supporting techniques and tools:
- `root-cause-tracing.md` - Trace bugs backward through call stack
- `defense-in-depth.md` - Add validation at multiple layers
- `condition-based-waiting.md` - Replace arbitrary timeouts with condition polling
- `find-polluter.sh` - Bisection script to find which test creates pollution
- `condition-based-waiting-example.ts` - Complete implementation from real debugging session

**Testing anti-patterns reference**

`test-driven-development` now includes `testing-anti-patterns.md` covering:
- Testing mock behavior instead of real behavior
- Adding test-only methods to production classes
- Mocking without understanding dependencies
- Incomplete mocks that hide structural assumptions

**Skill test infrastructure**

Three new test frameworks for validating skill behavior:

`tests/skill-triggering/` - Validates skills trigger from naive prompts without explicit naming. Tests 6 skills to ensure descriptions alone are sufficient.

`tests/claude-code/` - Integration tests using `claude -p` for headless testing. Verifies skill usage via session transcript (JSONL) analysis. Includes `analyze-token-usage.py` for cost tracking.

`tests/subagent-driven-dev/` - End-to-end workflow validation with two complete test projects:
- `go-fractals/` - CLI tool with Sierpinski/Mandelbrot (10 tasks)
- `svelte-todo/` - CRUD app with localStorage and Playwright (12 tasks)

### Major Changes

**DOT flowcharts as executable specifications**

Rewrote key skills using DOT/GraphViz flowcharts as the authoritative process definition. Prose becomes supporting content.

**The Description Trap** (documented in `writing-skills`): Discovered that skill descriptions override flowchart content when descriptions contain workflow summaries. Claude follows the short description instead of reading the detailed flowchart. Fix: descriptions must be trigger-only ("Use when X") with no process details.

**Skill priority in using-superpowers**

When multiple skills apply, process skills (brainstorming, debugging) now explicitly come before implementation skills. "Build X" triggers brainstorming first, then domain skills.

**brainstorming trigger strengthened**

Description changed to imperative: "You MUST use this before any creative work—creating features, building components, adding functionality, or modifying behavior."

### Breaking Changes

**Skill consolidation** - Six standalone skills merged:
- `root-cause-tracing`, `defense-in-depth`, `condition-based-waiting` → bundled in `systematic-debugging/`
- `testing-skills-with-subagents` → bundled in `writing-skills/`
- `testing-anti-patterns` → bundled in `test-driven-development/`
- `sharing-skills` removed (obsolete)

### Other Improvements

- **render-graphs.js** - Tool to extract DOT diagrams from skills and render to SVG
- **Rationalizations table** in using-superpowers - Scannable format including new entries: "I need more context first", "Let me explore first", "This feels productive"
- **docs/testing.md** - Guide to testing skills with Claude Code integration tests

---

## v3.6.2 (2025-12-03)

### Fixed

- **Linux Compatibility**: Fixed polyglot hook wrapper (`run-hook.cmd`) to use POSIX-compliant syntax
  - Replaced bash-specific `${BASH_SOURCE[0]:-$0}` with standard `$0` on line 16
  - Resolves "Bad substitution" error on Ubuntu/Debian systems where `/bin/sh` is dash
  - Fixes #141

---

## v3.5.1 (2025-11-24)

### Changed

- **OpenCode Bootstrap Refactor**: Switched from `chat.message` hook to `session.created` event for bootstrap injection
  - Bootstrap now injects at session creation via `session.prompt()` with `noReply: true`
  - Explicitly tells the model that using-superpowers is already loaded to prevent redundant skill loading
  - Consolidated bootstrap content generation into shared `getBootstrapContent()` helper
  - Cleaner single-implementation approach (removed fallback pattern)

---

## v3.5.0 (2025-11-23)

### Added

- **OpenCode Support**: Native JavaScript plugin for OpenCode.ai
  - Custom tools: `use_skill` and `find_skills`
  - Message insertion pattern for skill persistence across context compaction
  - Automatic context injection via chat.message hook
  - Auto re-injection on session.compacted events
  - Three-tier skill priority: project > personal > superpowers
  - Project-local skills support (`.opencode/skills/`)
  - Shared core module (`lib/skills-core.js`) for code reuse with Codex
  - Automated test suite with proper isolation (`tests/opencode/`)
  - Platform-specific documentation (`docs/README.opencode.md`, `docs/README.codex.md`)

### Changed

- **Refactored Codex Implementation**: Now uses shared `lib/skills-core.js` ES module
  - Eliminates code duplication between Codex and OpenCode
  - Single source of truth for skill discovery and parsing
  - Codex successfully loads ES modules via Node.js interop

- **Improved Documentation**: Rewrote README to explain problem/solution clearly
  - Removed duplicate sections and conflicting information
  - Added complete workflow description (brainstorm → plan → execute → finish)
  - Simplified platform installation instructions
  - Emphasized skill-checking protocol over automatic activation claims

---

## v3.4.1 (2025-10-31)

### Improvements

- Optimized superpowers bootstrap to eliminate redundant skill execution. The `using-superpowers` skill content is now provided directly in session context, with clear guidance to use the Skill tool only for other skills. This reduces overhead and prevents the confusing loop where agents would execute `using-superpowers` manually despite already having the content from session start.

## v3.4.0 (2025-10-30)

### Improvements

- Simplified `brainstorming` skill to return to original conversational vision. Removed heavyweight 6-phase process with formal checklists in favor of natural dialogue: ask questions one at a time, then present design in 200-300 word sections with validation. Keeps documentation and implementation handoff features.

## v3.3.1 (2025-10-28)

### Improvements

- Updated `brainstorming` skill to require autonomous recon before questioning, encourage recommendation-driven decisions, and prevent agents from delegating prioritization back to humans.
- Applied writing clarity improvements to `brainstorming` skill following Strunk's "Elements of Style" principles (omitted needless words, converted negative to positive form, improved parallel construction).

### Bug Fixes

- Clarified `writing-skills` guidance so it points to the correct agent-specific personal skill directories (`~/.claude/skills` for Claude Code, `~/.codex/skills` for Codex).

## v3.3.0 (2025-10-28)

### New Features

**Experimental Codex Support**
- Added unified `superpowers-codex` script with bootstrap/use-skill/find-skills commands
- Cross-platform Node.js implementation (works on Windows, macOS, Linux)
- Namespaced skills: `superpowers:skill-name` for superpowers skills, `skill-name` for personal
- Personal skills override superpowers skills when names match
- Clean skill display: shows name/description without raw frontmatter
- Helpful context: shows supporting files directory for each skill
- Tool mapping for Codex: TodoWrite→update_plan, subagents→manual fallback, etc.
- Bootstrap integration with minimal AGENTS.md for automatic startup
- Complete installation guide and bootstrap instructions specific to Codex

**Key differences from Claude Code integration:**
- Single unified script instead of separate tools
- Tool substitution system for Codex-specific equivalents
- Simplified subagent handling (manual work instead of delegation)
- Updated terminology: "Superpowers skills" instead of "Core skills"

### Files Added
- `.codex/INSTALL.md` - Installation guide for Codex users
- `.codex/superpowers-bootstrap.md` - Bootstrap instructions with Codex adaptations
- `.codex/superpowers-codex` - Unified Node.js executable with all functionality

**Note:** Codex support is experimental. The integration provides core superpowers functionality but may require refinement based on user feedback.

## v3.2.3 (2025-10-23)

### Improvements

**Updated using-superpowers skill to use Skill tool instead of Read tool**
- Changed skill invocation instructions from Read tool to Skill tool
- Updated description: "using Read tool" → "using Skill tool"
- Updated step 3: "Use the Read tool" → "Use the Skill tool to read and run"
- Updated rationalization list: "Read the current version" → "Run the current version"

The Skill tool is the proper mechanism for invoking skills in Claude Code. This update corrects the bootstrap instructions to guide agents toward the correct tool.

### Files Changed
- Updated: `skills/using-superpowers/SKILL.md` - Changed tool references from Read to Skill

## v3.2.2 (2025-10-21)

### Improvements

**Strengthened using-superpowers skill against agent rationalization**
- Added EXTREMELY-IMPORTANT block with absolute language about mandatory skill checking
  - "If even 1% chance a skill applies, you MUST read it"
  - "You do not have a choice. You cannot rationalize your way out."
- Added MANDATORY FIRST RESPONSE PROTOCOL checklist
  - 5-step process agents must complete before any response
  - Explicit "responding without this = failure" consequence
- Added Common Rationalizations section with 8 specific evasion patterns
  - "This is just a simple question" → WRONG
  - "I can check files quickly" → WRONG
  - "Let me gather information first" → WRONG
  - Plus 5 more common patterns observed in agent behavior

These changes address observed agent behavior where they rationalize around skill usage despite clear instructions. The forceful language and pre-emptive counter-arguments aim to make non-compliance harder.

### Files Changed
- Updated: `skills/using-superpowers/SKILL.md` - Added three layers of enforcement to prevent skill-skipping rationalization

## v3.2.1 (2025-10-20)

### New Features

**Code reviewer agent now included in plugin**
- Added `superpowers:code-reviewer` agent to plugin's `agents/` directory
- Agent provides systematic code review against plans and coding standards
- Previously required users to have personal agent configuration
- All skill references updated to use namespaced `superpowers:code-reviewer`
- Fixes #55

### Files Changed
- New: `agents/code-reviewer.md` - Agent definition with review checklist and output format
- Updated: `skills/requesting-code-review/SKILL.md` - References to `superpowers:code-reviewer`
- Updated: `skills/subagent-driven-development/SKILL.md` - References to `superpowers:code-reviewer`

## v3.2.0 (2025-10-18)

### New Features

**Design documentation in brainstorming workflow**
- Added Phase 4: Design Documentation to brainstorming skill
- Design documents now written to `docs/plans/YYYY-MM-DD-<topic>-design.md` before implementation
- Restores functionality from original brainstorming command that was lost during skill conversion
- Documents written before worktree setup and implementation planning
- Tested with subagent to verify compliance under time pressure

### Breaking Changes

**Skill reference namespace standardization**
- All internal skill references now use `superpowers:` namespace prefix
- Updated format: `superpowers:test-driven-development` (previously just `test-driven-development`)
- Affects all REQUIRED SUB-SKILL, RECOMMENDED SUB-SKILL, and REQUIRED BACKGROUND references
- Aligns with how skills are invoked using the Skill tool
- Files updated: brainstorming, executing-plans, subagent-driven-development, systematic-debugging, testing-skills-with-subagents, writing-plans, writing-skills

### Improvements

**Design vs implementation plan naming**
- Design documents use `-design.md` suffix to prevent filename collisions
- Implementation plans continue using existing `YYYY-MM-DD-<feature-name>.md` format
- Both stored in `docs/plans/` directory with clear naming distinction

## v3.1.1 (2025-10-17)

### Bug Fixes

- **Fixed command syntax in README** (#44) - Updated all command references to use correct namespaced syntax (`/superpowers:brainstorm` instead of `/brainstorm`). Plugin-provided commands are automatically namespaced by Claude Code to avoid conflicts between plugins.

## v3.1.0 (2025-10-17)

### Breaking Changes

**Skill names standardized to lowercase**
- All skill frontmatter `name:` fields now use lowercase kebab-case matching directory names
- Examples: `brainstorming`, `test-driven-development`, `using-git-worktrees`
- All skill announcements and cross-references updated to lowercase format
- This ensures consistent naming across directory names, frontmatter, and documentation

### New Features

**Enhanced brainstorming skill**
- Added Quick Reference table showing phases, activities, and tool usage
- Added copyable workflow checklist for tracking progress
- Added decision flowchart for when to revisit earlier phases
- Added comprehensive AskUserQuestion tool guidance with concrete examples
- Added "Question Patterns" section explaining when to use structured vs open-ended questions
- Restructured Key Principles as scannable table

**Anthropic best practices integration**
- Added `skills/writing-skills/anthropic-best-practices.md` - Official Anthropic skill authoring guide
- Referenced in writing-skills SKILL.md for comprehensive guidance
- Provides patterns for progressive disclosure, workflows, and evaluation

### Improvements

**Skill cross-reference clarity**
- All skill references now use explicit requirement markers:
  - `**REQUIRED BACKGROUND:**` - Prerequisites you must understand
  - `**REQUIRED SUB-SKILL:**` - Skills that must be used in workflow
  - `**Complementary skills:**` - Optional but helpful related skills
- Removed old path format (`skills/collaboration/X` → just `X`)
- Updated Integration sections with categorized relationships (Required vs Complementary)
- Updated cross-reference documentation with best practices

**Alignment with Anthropic best practices**
- Fixed description grammar and voice (fully third-person)
- Added Quick Reference tables for scanning
- Added workflow checklists Claude can copy and track
- Appropriate use of flowcharts for non-obvious decision points
- Improved scannable table formats
- All skills well under 500-line recommendation

### Bug Fixes

- **Re-added missing command redirects** - Restored `commands/brainstorm.md` and `commands/write-plan.md` that were accidentally removed in v3.0 migration
- Fixed `defense-in-depth` name mismatch (was `Defense-in-Depth-Validation`)
- Fixed `receiving-code-review` name mismatch (was `Code-Review-Reception`)
- Fixed `commands/brainstorm.md` reference to correct skill name
- Removed references to non-existent related skills

### Documentation

**writing-skills improvements**
- Updated cross-referencing guidance with explicit requirement markers
- Added reference to Anthropic's official best practices
- Improved examples showing proper skill reference format

## v3.0.1 (2025-10-16)

### Changes

We now use Anthropic's first-party skills system!

## v2.0.2 (2025-10-12)

### Bug Fixes

- **Fixed false warning when local skills repo is ahead of upstream** - The initialization script was incorrectly warning "New skills available from upstream" when the local repository had commits ahead of upstream. The logic now correctly distinguishes between three git states: local behind (should update), local ahead (no warning), and diverged (should warn).

## v2.0.1 (2025-10-12)

### Bug Fixes

- **Fixed session-start hook execution in plugin context** (#8, PR #9) - The hook was failing silently with "Plugin hook error" preventing skills context from loading. Fixed by:
  - Using `${BASH_SOURCE[0]:-$0}` fallback when BASH_SOURCE is unbound in Claude Code's execution context
  - Adding `|| true` to handle empty grep results gracefully when filtering status flags

---

# Superpowers v2.0.0 Release Notes

## Overview

Superpowers v2.0 makes skills more accessible, maintainable, and community-driven through a major architectural shift.

The headline change is **skills repository separation**: all skills, scripts, and documentation have moved from the plugin into a dedicated repository ([obra/superpowers-skills](https://github.com/obra/superpowers-skills)). This transforms superpowers from a monolithic plugin into a lightweight shim that manages a local clone of the skills repository. Skills auto-update on session start. Users fork and contribute improvements via standard git workflows. The skills library versions independently from the plugin.

Beyond infrastructure, this release adds nine new skills focused on problem-solving, research, and architecture. We rewrote the core **using-skills** documentation with imperative tone and clearer structure, making it easier for Claude to understand when and how to use skills. **find-skills** now outputs paths you can paste directly into the Read tool, eliminating friction in the skills discovery workflow.

Users experience seamless operation: the plugin handles cloning, forking, and updating automatically. Contributors find the new architecture makes improving and sharing skills trivial. This release lays the foundation for skills to evolve rapidly as a community resource.

## Breaking Changes

### Skills Repository Separation

**The biggest change:** Skills no longer live in the plugin. They've been moved to a separate repository at [obra/superpowers-skills](https://github.com/obra/superpowers-skills).

**What this means for you:**

- **First install:** Plugin automatically clones skills to `~/.config/superpowers/skills/`
- **Forking:** During setup, you'll be offered the option to fork the skills repo (if `gh` is installed)
- **Updates:** Skills auto-update on session start (fast-forward when possible)
- **Contributing:** Work on branches, commit locally, submit PRs to upstream
- **No more shadowing:** Old two-tier system (personal/core) replaced with single-repo branch workflow

**Migration:**

If you have an existing installation:
1. Your old `~/.config/superpowers/.git` will be backed up to `~/.config/superpowers/.git.bak`
2. Old skills will be backed up to `~/.config/superpowers/skills.bak`
3. Fresh clone of obra/superpowers-skills will be created at `~/.config/superpowers/skills/`

### Removed Features

- **Personal superpowers overlay system** - Replaced with git branch workflow
- **setup-personal-superpowers hook** - Replaced by initialize-skills.sh

## New Features

### Skills Repository Infrastructure

**Automatic Clone & Setup** (`lib/initialize-skills.sh`)
- Clones obra/superpowers-skills on first run
- Offers fork creation if GitHub CLI is installed
- Sets up upstream/origin remotes correctly
- Handles migration from old installation

**Auto-Update**
- Fetches from tracking remote on every session start
- Auto-merges with fast-forward when possible
- Notifies when manual sync needed (branch diverged)
- Uses pulling-updates-from-skills-repository skill for manual sync

### New Skills

**Problem-Solving Skills** (`skills/problem-solving/`)
- **collision-zone-thinking** - Force unrelated concepts together for emergent insights
- **inversion-exercise** - Flip assumptions to reveal hidden constraints
- **meta-pattern-recognition** - Spot universal principles across domains
- **scale-game** - Test at extremes to expose fundamental truths
- **simplification-cascades** - Find insights that eliminate multiple components
- **when-stuck** - Dispatch to right problem-solving technique

**Research Skills** (`skills/research/`)
- **tracing-knowledge-lineages** - Understand how ideas evolved over time

**Architecture Skills** (`skills/architecture/`)
- **preserving-productive-tensions** - Keep multiple valid approaches instead of forcing premature resolution

### Skills Improvements

**using-skills (formerly getting-started)**
- Renamed from getting-started to using-skills
- Complete rewrite with imperative tone (v4.0.0)
- Front-loaded critical rules
- Added "Why" explanations for all workflows
- Always includes /SKILL.md suffix in references
- Clearer distinction between rigid rules and flexible patterns

**writing-skills**
- Cross-referencing guidance moved from using-skills
- Added token efficiency section (word count targets)
- Improved CSO (Claude Search Optimization) guidance

**sharing-skills**
- Updated for new branch-and-PR workflow (v2.0.0)
- Removed personal/core split references

**pulling-updates-from-skills-repository** (new)
- Complete workflow for syncing with upstream
- Replaces old "updating-skills" skill

### Tools Improvements

**find-skills**
- Now outputs full paths with /SKILL.md suffix
- Makes paths directly usable with Read tool
- Updated help text

**skill-run**
- Moved from scripts/ to skills/using-skills/
- Improved documentation

### Plugin Infrastructure

**Session Start Hook**
- Now loads from skills repository location
- Shows full skills list at session start
- Prints skills location info
- Shows update status (updated successfully / behind upstream)
- Moved "skills behind" warning to end of output

**Environment Variables**
- `SUPERPOWERS_SKILLS_ROOT` set to `~/.config/superpowers/skills`
- Used consistently throughout all paths

## Bug Fixes

- Fixed duplicate upstream remote addition when forking
- Fixed find-skills double "skills/" prefix in output
- Removed obsolete setup-personal-superpowers call from session-start
- Fixed path references throughout hooks and commands

## Documentation

### README
- Updated for new skills repository architecture
- Prominent link to superpowers-skills repo
- Updated auto-update description
- Fixed skill names and references
- Updated Meta skills list

### Testing Documentation
- Added comprehensive testing checklist (`docs/TESTING-CHECKLIST.md`)
- Created local marketplace config for testing
- Documented manual testing scenarios

## Technical Details

### File Changes

**Added:**
- `lib/initialize-skills.sh` - Skills repo initialization and auto-update
- `docs/TESTING-CHECKLIST.md` - Manual testing scenarios
- `.claude-plugin/marketplace.json` - Local testing config

**Removed:**
- `skills/` directory (82 files) - Now in obra/superpowers-skills
- `scripts/` directory - Now in obra/superpowers-skills/skills/using-skills/
- `hooks/setup-personal-superpowers.sh` - Obsolete

**Modified:**
- `hooks/session-start.sh` - Use skills from ~/.config/superpowers/skills
- `commands/brainstorm.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `commands/write-plan.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `commands/execute-plan.md` - Updated paths to SUPERPOWERS_SKILLS_ROOT
- `README.md` - Complete rewrite for new architecture

### Commit History

This release includes:
- 20+ commits for skills repository separation
- PR #1: Amplifier-inspired problem-solving and research skills
- PR #2: Personal superpowers overlay system (later replaced)
- Multiple skill refinements and documentation improvements

## Upgrade Instructions

### Fresh Install

```bash
# In Claude Code
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

The plugin handles everything automatically.

### Upgrading from v1.x

1. **Backup your personal skills** (if you have any):
   ```bash
   cp -r ~/.config/superpowers/skills ~/superpowers-skills-backup
   ```

2. **Update the plugin:**
   ```bash
   /plugin update superpowers
   ```

3. **On next session start:**
   - Old installation will be backed up automatically
   - Fresh skills repo will be cloned
   - If you have GitHub CLI, you'll be offered the option to fork

4. **Migrate personal skills** (if you had any):
   - Create a branch in your local skills repo
   - Copy your personal skills from backup
   - Commit and push to your fork
   - Consider contributing back via PR

## What's Next

### For Users

- Explore the new problem-solving skills
- Try the branch-based workflow for skill improvements
- Contribute skills back to the community

### For Contributors

- Skills repository is now at https://github.com/obra/superpowers-skills
- Fork → Branch → PR workflow
- See skills/meta/writing-skills/SKILL.md for TDD approach to documentation

## Known Issues

None at this time.

## Credits

- Problem-solving skills inspired by Amplifier patterns
- Community contributions and feedback
- Extensive testing and iteration on skill effectiveness

---

**Full Changelog:** https://github.com/obra/superpowers/compare/dd013f6...main
**Skills Repository:** https://github.com/obra/superpowers-skills
**Issues:** https://github.com/obra/superpowers/issues
