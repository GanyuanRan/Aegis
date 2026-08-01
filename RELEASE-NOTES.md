# Aegis Release Notes

## v2.6.3 (2026-08-01)

### Current-Branch-First Git Lifecycle

- Made the current branch and workspace the default for ordinary coding tasks;
  complexity, planning, TDD, subagents, or a `main` / `master` branch name no
  longer justify a branch or worktree by themselves.
- Added a pre-write `TaskStartSnapshot`, coordinator-only Git mutation
  ownership, task-owned scoped staging, one coherent verified local commit,
  and explicit task-clean versus repository-clean readback.
- Limited branches to genuinely independent histories and worktrees to
  concurrent checkout or blocking unrelated dirty state; paired temporary
  resources with creator-owned, evidence-led cleanup.

### Capability-Preserving Context Budgets

- Replaced single hard size ceilings with warning targets and larger hard
  ceilings for high-frequency skills, plus route-bundle budgets for debugging,
  plan execution, and long-task flows.
- Made capability gates precede size gates so required routing, semantic slots,
  stop signals, owner rules, and discoverable reference triggers cannot be
  deleted merely to satisfy a byte limit.
- Restored the authority fast path, explicit passive `CONTEXT-MAP.md` /
  `CONTEXT.md` lookup, conditional subagent execution, strict-TDD authorization
  markers, authority-before-worktree placement, and complete
  commit-through-handoff stop signals.

### Regression And Distribution Safety

- Added deterministic budget-band tests, route-bundle checks, semantic-context
  assertions, worktree ordering checks, TDD-off contract coverage, and complete
  integration-stop assertions.
- Made the Kimi Code deterministic harness select `python3`, `py -3`, or
  `python` by verified availability, and made the repository test package
  explicit so Windows environments cannot resolve an unrelated package named
  `tests`.
- Verified the repaired behavior with the same read-only `gpt-5.6-sol` /
  `xhigh` pressure scenarios before and after the change; all six repaired
  decisions are now explicit in the owning skills.
- Reviewed all four manually copied global user-rule projections. No manual
  re-copy is required because this release changes task-specific skill behavior
  without changing profile-owned activation, TDD-default, authority-priority,
  or base completion-evidence semantics.

### Verification And Release Boundary

- The formal release gate remains
  `bash tests/e2e/run-all.sh --full --host-profile fast`; this release is
  published only after that gate and the version audit pass.
- Bumped all declared package and host manifest versions from `2.6.0` to
  `2.6.3` through `scripts/bump-version.sh`.
- This release remains `Aegis Method Pack (runtime-ready)` and does not add
  authoritative `GateDecision`, `PolicySnapshot`, runtime authority, or
  completion authority.

## v2.6.0 (2026-07-31)

### Measured Agentic Benchmark

- Published the corrected `gpt-5.6-sol` / `xhigh` extended held-out A/B
  benchmark as sanitized JSON, a deterministic SVG, and bilingual Markdown
  tables embedded in the public READMEs.
- Across 20 held-out cases, two arms, and three repetitions, 120 valid runs
  raised observable contract pass rate from `60.00%` without Aegis to `90.00%`
  with Aegis, a `+30.00` percentage-point difference. Unsafe outcomes fell
  from `11.67%` to `5.00%`.
- Added a deterministic case-cluster bootstrap interval of `+13.33` to `+48.33`
  percentage points. One timed-out attempt remained infrastructure-invalid,
  was retried, and did not enter the contract pass-rate calculation.

### Fairness And Reproducibility Hardening

- Advanced the agentic benchmark matrix to version 5, pinned the requested
  model and reasoning effort identically across both arms, and made provider
  preflight verify that the requested reasoning level is advertised for the
  selected model.
- Replaced brittle single-phrase response checks with frozen semantic claim
  groups and question-anywhere contracts while retaining exact wording checks
  when exact wording is the observable behavior under test.
- Kept the earlier defective-semantics batch as private superseded diagnostic
  history, reran the complete held-out batch, and preserved frozen case
  outcomes during arm-hidden technical review instead of relabeling results.
- Corrected rendered percentage-point deltas to derive from raw pass counts
  before display rounding.

### Public Evidence Boundary

- Added the measured comparison to `README.md` and `README.zh-CN.md`, with links
  to the sanitized report, deterministic chart, bilingual tables, and the
  benchmark methodology owner.
- Explicitly records that the benchmark is bounded advisory contract evidence,
  repetitions are case-clustered, deterministic response contracts remain
  conservative, and the arm-hidden technical review is not independent human
  review.
- Records the requested `gpt-5.6-sol` model and `xhigh` reasoning effort without
  fabricating observed model identity when the Codex host events omit it.
- Replaced a stale OpenCode version-pin example with a release-tag placeholder
  so host documentation does not acquire a second version owner.

### Verification And Release Boundary

- Fresh `bash tests/e2e/run-all.sh --full --host-profile fast` verification
  passed before the release tag was created, alongside the benchmark scorer,
  renderer, sanitization, README projection, and GitHub CI checks.
- Bumped every declared package and host manifest version from `2.5.5` to
  `2.6.0` through `scripts/bump-version.sh`, with no undeclared current-version
  references found by the version audit.
- This release remains `Aegis Method Pack (runtime-ready)`. Benchmark evidence
  does not grant authoritative `GateDecision`, `PolicySnapshot`, candidate
  promotion, runtime authority, or completion authority.

## v2.5.5 (2026-07-31)

### Isolated Agentic Benchmark Program

- Added a version 4 agentic benchmark contract with 30 cases across ten
  scenario classes, paired `baseline-no-aegis` and `aegis-auto` arms, and
  explicit development, standard held-out, and extended held-out profiles.
- Added deterministic scheduling with bounded workers, paid-attempt ceilings,
  infrastructure retry limits, persistent wall-clock accounting, crash-safe
  resume behavior, and preservation of every paid attempt result.
- Added Bubblewrap-based execution isolation, provider preflight, sealed auth
  handling, bounded process supervision, confidential artifact cleanup, and
  fail-closed exposure checks.

### Observable Scoring And Reproducible Reports

- Added observable-outcome scoring that is independent of arm vocabulary,
  validates exact workspace effects, and keeps scorer unknowns separate from
  infrastructure failures and contract failures.
- Added controlled replay, immutable verification inputs, matrix and case
  validators, sanitized Markdown/SVG report projection, and adversarial checks
  against report, path, metric, and publication-boundary drift.
- Kept benchmark results advisory: development evidence cannot be promoted into
  held-out or general product claims, and report output does not grant runtime
  authority or completion authority.

### Deeper-Cause Proof And Progressive Disclosure

- Strengthened systematic debugging so root-cause closure requires falsifiers,
  causal-topology evidence, recurrence analysis, quick-exit proof, and
  topology-specific anti-disguise checks when deeper-cause signals are present.
- Progressively disclosed debugging and verification detail into directly
  routed references while preserving the executable hot path, escalation
  triggers, compact completion receipt, and current default `TDD Mode: off`.
- Kept the quick bug lane proportional while requiring an explicit
  change-necessity and owner-fit decision before source edits.

### Reliability And Review Hardening

- Added shared secure atomic JSON writes, output and artifact limits, symlink
  boundary checks, structured destructive-tool classification, exact changed
  path contracts, and stronger semantic benchmark assertions.
- Closed independent review findings around confidential evidence boundaries,
  extended-profile wall budgets, interrupted wave persistence, and Linux CI
  sandbox provisioning.
- Kept the repository root free of branch-local `docs/aegis/` work records and
  excluded local `.codex/` configuration from the release surface.

### Verification And Release Boundary

- The formal release gate remains
  `bash tests/e2e/run-all.sh --full --host-profile fast`, with the Linux-only
  benchmark supervisor covered by the repository CI environment.
- Bumped all declared package and host manifest versions directly from `2.5.3`
  to `2.5.5`, following the selected release version, with no undeclared
  version references found by the version audit.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, benchmark promotion, or completion
  authority.

## v2.5.3 (2026-07-27)

### Benchmark Coverage Contract

- Reconciled the ten documented agentic benchmark scenario classes with the
  deterministic workflow-quality fixtures and the three checked-in controlled
  replay samples.
- Made deterministic coverage, controlled replay references, live eligibility,
  and actual pass evidence separate machine-checkable concepts so fixture
  presence can no longer be reported as evaluation success.
- Hard-cut the benchmark matrix and replay manifest to schema version 2 without
  retaining a legacy compatibility path.

### Tiered Comparative Evaluation

- Added an explicit four-tier evaluation contract covering deterministic static
  checks, controlled transcript replay, opt-in repeated held-out live
  evaluation, and sampled blind human review.
- Kept the current implementation deliberately bounded to deterministic checks
  and single-transcript development replays. Repeated live runs, variance,
  held-out execution, and blind review remain contract-only follow-up work.
- Defined exact current comparison arms for `baseline-no-aegis` and
  `aegis-auto`, while keeping `previous-aegis` conditional on a future candidate
  revision evaluation rather than a universal runtime arm.
- Added a versioned advisory JSON report with top-level and per-sample
  `overallPass`, structured failures, arm outcomes, comparison deltas, preserved
  unknowns, and a non-authoritative promotion status.

### Validation And Safety

- Added independent matrix and replay validation for scenario mappings,
  evaluation tiers, arm structure, expected pass semantics, promotion limits,
  and unsupported evidence claims.
- Added adversarial negative cases that reject coordinated fixture drift,
  duplicate or missing arms, premature `previous-aegis` use, held-out or live
  overclaims, automatic promotion, and comparison results that would otherwise
  hide an arm contract failure.
- Restricted generated replay workspaces and reports to strict children of the
  repository-local `.tmp` directory, including a sentinel regression proving
  that the `.tmp` root cannot be deleted.

### Verification And Release Boundary

- Fresh `bash tests/e2e/run-all.sh --full --host-profile fast` verification
  passed all four aggregate suites before release. Layer 1 passed `40/40`;
  Layer 2 and Layer 3 each passed `6/6`. The benchmark, controlled replay,
  boundary, context-budget, trigger-health, workflow-quality, and version-audit
  checks also passed.
- Bumped all declared package and host manifest versions from `2.5.2` to
  `2.5.3` with no undeclared version references found by the version audit.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, candidate promotion, or completion
  authority.

## v2.5.2 (2026-07-25)

### Global User-Rule Profiles

- Reframed the Lite and Advanced English/Chinese global user-rule files as
  optional, manually copied host/profile projections rather than method owners,
  installers, or skill-discovery evidence.
- Made Lite the sole owner of the copyable activation clause: `auto` remains
  the default, while `explicit` users replace that clause in Lite instead of
  keeping an automatic semantic-routing instruction active.
- Converted Advanced into a non-standalone additive governance overlay for
  Lite, removing duplicated activation, priority, fast-path, baseline
  completion-evidence, and method-layer authority rules.
- Aligned the Advanced overlay with the current default `tdd_mode = "off"`,
  correct-owner minimality, externally observable compatibility, prompt
  hygiene, and workflow-owned output semantics.
- Preserved all four public filenames and links while removing the stale
  `AGENTS_RULES.md` owner reference and consolidating template projection checks
  under `host-instruction-invariants-check.sh`.

### Manual Migration

- `aegis:update` does not modify global rules that users copied into a host.
  Existing users should re-copy the Lite base profile, choose its activation
  clause, and then append only the needed rules from the Advanced overlay.
- Changing local Aegis activation to `explicit` must be paired with the
  Lite profile's explicit-mode replacement clause. Host-native skill matchers
  may still behave according to host capabilities.

### README Badges

- Added a dynamic GitHub Stars badge immediately after the latest-release badge
  in both the English and Chinese README files.

### Verification And Release Surface

- Fresh `bash tests/e2e/run-all.sh --full --host-profile fast` verification
  passed all four suites. Layer 1 passed `40/40`; Layer 2 and Layer 3 each
  passed `6/6`.
- Bumped all declared package and host manifest versions from `2.5.1` to
  `2.5.2` with no undeclared version references found by the version audit.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.5.1 (2026-07-23)

### Kimi Code Automatic Routing

- Added a native root `kimi.plugin.json` that reuses the canonical `skills/`
  tree and establishes `sessionStart.skill = using-aegis` for new and resumed
  Kimi sessions.
- Made the Kimi plugin the default automatic installation path, while retaining
  updater-managed direct-child Agent Skills as an explicit compatibility mode.
- Defined a single-owner rule: the plugin, `$KIMI_CODE_HOME/skills/`, and
  `~/.agents/skills/` Aegis exposures must not be enabled together.
- Hardened all Kimi-visible skill frontmatter with quoted, trigger-oriented
  descriptions and a repository validator for Kimi's metadata boundary.

### Installation, Update, And Diagnostics

- Added read-only `kimi-code-auto` and `kimi-code-explicit` doctor profiles to
  verify plugin identity, managed root, version, session-start routing, and
  duplicate skill exposure without mutating Kimi state.
- Routed automatic Kimi installs and updates through Kimi's native plugin
  manager; kept `aegis-update.py` as the owner of explicit direct-child
  compatibility installations.
- Updated the universal quick-install prompt so plugin, hook, and session-start
  hosts must prove native activation and automatic entry instead of treating
  file discovery or a generic doctor result as completion evidence.
- Added migration, reload/new-session, rollback, and verification guidance to
  the Kimi host guide.

### Verification And Architecture

- Added deterministic Kimi metadata, manifest, doctor, collision, and host
  boundary coverage, plus an environment-bound five-case natural-language
  routing smoke and resumed-session check.
- Recorded the durable install/discovery decision in ADR-0002 while preserving
  the `Aegis Method Pack (runtime-ready)` authority boundary.
- Fresh `bash tests/e2e/run-all.sh --full --host-profile fast` verification
  passed all four suites. Layer 1 passed `40/40`, including representative
  Codex automatic and explicit skill-loading smoke, OpenCode base coverage,
  and Codex plugin-sync regression; Layer 2 and Layer 3 each passed `6/6`.
- The current release environment does not provide the `kimi` executable, so
  native Kimi plugin installation, reload/resume, and live model-routing smoke
  remain environment-bound and are not claimed as fresh host closeout.

### Release Surface

- Bumped all declared package and host manifest versions from `2.5.0` to
  `2.5.1`.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.5.0 (2026-07-19)

### Semantic Context Infrastructure

- Promoted project-level `CONTEXT.md` from an optional glossary into a stable,
  bounded semantic context surface for canonical terms, aliases, distinctions,
  and authority references.
- Split context handling into cheap passive consumption and explicitly owned
  active modeling, so ordinary work can reuse established language without
  loading a separate modeling workflow.
- Added evidence grades and fact-versus-decision authority rules: agents may
  record high-confidence resolved facts directly, while unresolved product or
  architecture decisions still require clarification.
- Added a compact root context baseline for `Aegis Method Pack`, `Host Adapter`,
  `Runtime Core`, and `runtime-ready artifact` without moving runtime authority
  into the method pack.

### Reliability And Workflow Integration

- Integrated semantic context as a thin input to planning, brainstorming,
  debugging, review, continuation, and verification workflows while retaining
  `establishing-project-context` as the single active-modeling owner.
- Required byte-stable no-op behavior, lazy first creation, pre-write readback,
  concurrent-edit protection, safe path resolution, legacy table readability,
  and instruction-like content isolation.
- Added trigger-health coverage that distinguishes passive reuse, resolved
  semantic changes, and tiny-task false positives.
- Documented stable semantic prefixes as a cache opportunity rather than a
  provider-independent cache-hit or token-savings guarantee.

### Verification

- Added a 15-case deterministic semantic-context matrix and wired it into the
  Layer 1 release gate.
- Added an opt-in, temporary-project live runner with checkout/installed source
  modes, installed-skill fingerprint protection, and no host-configuration
  mutation.
- Extended Codex smoke-log parsing to recognize direct POSIX `sed` skill reads
  while retaining the existing PowerShell coverage and transcript-noise guards.
- Representative Codex checkout runs passed first resolved-fact creation,
  byte-stable no-op handling, and passive context consumption. The installed
  old-skill fingerprint was rejected as stale by design; Claude CLI live
  coverage remains environment-bound and was not claimed.
- Fresh `bash tests/e2e/run-all.sh --full --host-profile fast` verification
  passed all four suites. Layer 1 passed `40/40`, including representative
  Codex automatic and explicit skill-loading smoke, OpenCode base coverage,
  and Codex plugin-sync regression; Layer 2 and Layer 3 each passed `6/6`.

### Release Surface

- Bumped all declared package and host manifest versions from `2.4.7` to
  `2.5.0`.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.4.7 (2026-07-14)

### Directional Reset Governance

- Preserved `PatchShape`, `CanonicalOwner`, `UpwardDrillSignal`, decision,
  latest outcome, and one bounded evidence reference after a locally green
  repair slice instead of letting a local pass erase the active direction.
- Required verification-driven unplanned repairs to read the retained state
  before editing and compare invariant, owner or contract seam, patch shape,
  and causal topology.
- Prevented renamed carriers from being treated as independent repair
  directions when their semantic direction still converges.
- Reused existing checkpoint prose and evidence-reference surfaces; no new
  artifact, schema field, workflow owner, or runtime authority was added.

### Workflow And Stability Safeguards

- Kept `systematic-debugging` as the sole owner of repair-direction judgment,
  while `executing-plans` performs the pre-edit routing and
  `long-task-continuation` carries only bounded state across slices.
- Preserved the normal quick path for proven independent canonical-owner bugs
  and added context-growth budgets around the three touched workflow skills.
- Added stateful trigger-health, workflow-quality, patch-shape, continuation,
  and context-budget regression coverage for local-green directional resets.
- Extended the Codex smoke transcript parser to recognize a constrained
  PowerShell path-array plus `foreach` skill-read shape while rejecting loops
  whose `Get-Content` call reads a different variable.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `bash scripts/bump-version.sh --audit`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`, and
  `git diff --check`.
- The final full/fast run passed all four suites. Layer 1 passed `39/39`,
  including representative Codex automatic and explicit skill-triggering
  smoke, OpenCode base coverage, and Codex plugin-sync regression; Layer 2 and
  Layer 3 each passed `6/6`.
- The current Codex Desktop installation provides `codex.exe` rather than
  `codex.cmd`, so the final host smoke used the documented `CODEX_CMD` override.
  A parser regression test also covers the real batched skill-read transcript
  shape observed during the release gate.

### Release Surface

- Bumped all declared package and host manifest versions from `2.4.6` to
  `2.4.7`.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.4.5 (2026-07-12)

### Quick Install In The Fast-Track Playbooks

- Promoted installation to the first section of both the English
  `Aegis Fast-Track Playbook` and the Chinese `Aegis 速通秘籍`.
- Added one copy-and-paste prompt that asks the user's AI coding agent to
  identify the current host, follow the correct global installation guide,
  restart or reload the host when needed, and run complete-install
  verification from the installed method-pack root.
- Defined the complete-install evidence explicitly: the doctor JSON must report
  `"ok": true`, `"workspaceSupport": "available"`, and
  `"configStatus": "configured"`, with discovery-root and skill-name-prefix
  checks when the host guide requires them.
- Clarified that copy-only or skills-only discovery can expose Aegis methods
  without proving complete project workspace support.
- Added direct manual-install entrypoints for Codex, OpenCode, Claude Code, and
  the full host compatibility matrix, plus the normal `update Aegis` /
  `aegis:update` follow-up path.

### Documentation Contract Coverage

- Renumbered both playbooks so installation precedes the first-use guide,
  lightweight operating model, engineering moats, project workspace,
  capability map, controls, trigger diagnosis, and deeper references.
- Updated the internal workspace anchor after the section move.
- Added workflow-quality regression checks that keep quick install first,
  preserve the complete-install JSON evidence, and distinguish skills-only
  discovery from complete installation.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.4.5`,
  `bash scripts/bump-version.sh --check`,
  `bash scripts/bump-version.sh --audit`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`, and
  `git diff --check`.
- The final full/fast run passed all four suites. Layer 1 passed `39/39`,
  including Codex automatic and explicit skill-triggering smoke, OpenCode base
  coverage, and Codex plugin-sync regression.
- The current Codex Desktop installation does not include
  `codex-windows-sandbox-setup.exe`. A workspace-write smoke attempt therefore
  reached the correct `brainstorming` route but could not read the skill file.
  The final release run used the working `codex.exe` with
  `-s danger-full-access`; log readback confirmed successful reads of both
  `using-aegis` and `brainstorming`, not parser-only load markers.

### Release Surface

- Bumped all declared package and host manifest versions from `2.4.4` to
  `2.4.5`.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.4.4 (2026-07-12)

### Grilling Mode

- Added a focused Grilling Mode inside `brainstorming` for decision interviews
  triggered by direct phrases such as `grill me`, `grill this plan`, `审问我`,
  `盘问我`, and `拷问我`.
- Added a one-time opening card, recommendation and trade-off framing, and one
  decision question per turn by default. Fast grilling can batch at most three
  independent decision questions.
- Kept grilling intentionally separate from implementation: it does not write
  plans, docs, or code, and PR/diff/current-code review still routes to the
  independent code-review workflow.
- Expanded trigger-health fixtures and regression checks for direct, soft,
  fast, Chinese-language, and negative grilling scenarios.

### TDD Off-Mode Enforcement

- Hardened the default `off` mode so risk wording alone cannot automatically
  route into or load strict TDD.
- Aligned `using-aegis`, systematic debugging, writing plans,
  subagent-driven development, and skill authoring with the same rule:
  explicit `strict TDD`, `test-first`, `TDD Route: strict`, or an enabled
  automatic mode is required for RED / GREEN routing.
- Preserved proportional regression tests and
  `verification-before-completion` when automatic TDD is off.
- Added policy and workflow-quality regression coverage that prevents owner
  workflows from reintroducing mandatory test-first behavior.

### Fast-Track Playbooks And Workspace Guidance

- Added English and Chinese user-facing quick-start guides:
  `Aegis Fast-Track Playbook` and `Aegis 速通秘籍`.
- Reworked the root README entrypoints around Aegis's lightweight operating
  model, natural trigger phrases, and progressive workflow depth.
- Highlighted five engineering moats: seven-layer root-cause analysis,
  first-principles decision review, the anti-entropy code-change loop,
  workspace-backed long-task continuity, and evidence-based closeout.
- Documented how the project-local `docs/aegis/` workspace initializes intent,
  baseline, checkpoint, evidence, drift, resume, proof-bundle, and optional ADR
  records without turning method-pack artifacts into project authority.
- Added a category-level comparison with standalone skill packs while avoiding
  fixed cost, time, token, or diff-size claims across arbitrary projects.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.4.4`,
  `bash scripts/bump-version.sh --check`,
  `bash scripts/bump-version.sh --audit`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/trigger-health-check.sh`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`, and
  `git diff --check`.
- The final full/fast run passed all four suites. Layer 1 passed `39/39`,
  including representative Codex automatic and explicit skill-triggering
  smoke, OpenCode base coverage, and Codex plugin-sync regression.
- The first full/fast attempt was environment-blocked because the current
  Codex Desktop install provides `codex.exe` but not `codex.cmd`. Re-running
  with `CODEX_CMD` pointed at the working `codex.exe` passed both targeted
  Codex smoke tests and the complete release gate; no Aegis routing regression
  was found.

### Release Surface

- Bumped all declared package and host manifest versions directly from
  `2.4.1` to `2.4.4`; no `v2.4.2` or `v2.4.3` tags are created by this release.
- This release remains `Aegis Method Pack (runtime-ready)`, preserves
  multi-host plugin-installable distribution, and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or completion authority.

## v2.4.1 (2026-07-12)

### Grok Build Host Support

- Added a dedicated Grok Build installation and verification guide covering
  native `$GROK_HOME/skills` discovery, `[skills] paths` configuration, and
  Claude-compatible plugin discovery.
- Added updater defaults for the `grok` and `grok-build` host aliases. The
  updater now exposes Aegis skills as generated direct-child entries under
  `$GROK_HOME/skills` or `~/.grok/skills` while keeping the method-pack
  checkout as the canonical source.
- Documented that native skills, extra skill paths, shared Agent Skills, and
  Claude-compatible plugins are alternative exposure routes. Enabling more
  than one route can create duplicate Aegis skill names with different
  freshness.

### Compatibility And Regression Coverage

- Added a Grok Build host-boundary check and included it in the Layer 1 release
  verification path.
- Added updater regression tests for Grok-native discovery defaults,
  `GROK_HOME`, host aliases, direct-child registration, and legacy registry
  normalization.
- Hardened Codex smoke-log parsing so one PowerShell command that reads
  multiple `SKILL.md` files records every loaded skill instead of only the
  first path.
- Updated the compatibility snapshot, known limitations, release checklist,
  root documentation, and testing guide to include the Grok Build surface.
- Preserved the Aegis Method Pack boundary: Grok owns host discovery, native
  routing, plugins, permissions, sessions, and reload behavior; Aegis does not
  provide authoritative `GateDecision`, `PolicySnapshot`, or completion
  authority.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.4.1`,
  `bash scripts/bump-version.sh --check`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`,
  `bash tests/e2e/grok-build-host-boundary-check.sh`,
  `python tests/helpers/test_aegis_update.py -k grok`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `grok plugin validate .`, and
  `git diff --check`.
- The full fast profile passed after using the documented `CODEX_CMD` override
  with a working local Codex executable and bypassing a missing local Windows
  sandbox helper. The initial failures were environment-bound CLI launch and
  sandbox errors, not Aegis workflow regressions.
- Local Grok Build `0.2.93` headless smoke passed both an explicit
  `using-aegis` route and an automatic debugging route. The current local
  profile also exposed Aegis through both shared Agent Skills and an older
  Claude plugin cache, so this release records structural and representative
  live-smoke evidence without claiming clean-install or release-level Grok
  closeout.

### Release Surface

- Bumped all declared package and host manifest versions from `2.4.0` to
  `2.4.1`.
- This release remains `Aegis Method Pack (runtime-ready)` and preserves
  plugin-installable distribution without claiming full-platform or full-host
  production rollout readiness.

## v2.4.0 (2026-07-09)

### Reviewer Agent Retirement

- Retired the root `agents/code-reviewer.md` prompt so Aegis no longer carries
  a second reviewer checklist outside the canonical skill-local template.
- Updated code-review dispatch guidance to use a general-purpose reviewer
  subagent with `skills/requesting-code-review/code-reviewer.md`.
- Removed root `agents/` exposure from the Cursor, Claude Code, and CodeBuddy
  public surfaces where it was still presented as part of the plugin skeleton.

### Compact Verification Closeout

- Reworked `verification-before-completion` around three closeout levels:
  `L0 fast-path`, `L1 compact receipt`, and `L2 triggered expansions`.
- Kept the `Aegis Impact and Safety Receipt` as the unified completion surface
  for non-trivial Aegis-shaped work while treating readiness, trace, baseline,
  ADR, complexity, and retirement details as conditional expansions.
- Moved detailed complexity governance fields back to the shared complexity
  reference and current baseline instead of inlining the full expanded card in
  the completion hot path.

### Workflow Quality Regression Coverage

- Updated workflow-quality fixtures and validators so the compact closeout
  contract remains auditable without reviving parallel final report owners.
- Added regression coverage that the retired root reviewer agent stays deleted
  and review dispatch no longer depends on the retired `aegis:code-reviewer`
  named-agent type.
- Updated host-adapter smoke validation so the Cursor manifest explicitly does
  not expose retired root agents.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.4.0`,
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `python tests/helpers/validate_host_adapter_smoke.py .`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/governance-completion-contract-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/artifact-schema-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/run-all.sh --full --host-profile none`, and
  `git diff --check`.
- `bash tests/e2e/run-all.sh --full --host-profile fast` was attempted, but
  the Codex representative live smoke checks were environment-blocked by local
  Codex CLI authentication: `401 Unauthorized` / missing bearer or basic
  authentication. The non-live method-pack, fixture, boundary, workflow, and
  scenario checks passed under `--host-profile none`.
- Release checklist readback confirmed that the release still ships
  `Aegis Method Pack (runtime-ready)` and does not add authoritative
  `GateDecision`, `PolicySnapshot`, or `completion authority`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.7` to `2.4.0`.
- This release preserves plugin-installable method-pack distribution and does
  not claim full-platform or full-host production rollout readiness.

## v2.3.7 (2026-07-09)

### Completion Receipt Boundary Hardening

- Clarified that `verification-before-completion` is the single completion
  closeout aggregator for non-trivial Aegis-shaped work.
- Defined completion-adjacent structures such as `Readiness Summary`,
  `Trace Digest`, `Goal Closure`, `ADR Backfill Check`, `Retirement Closure`,
  `Baseline Alignment`, and `Complexity Delta` as receipt inputs or optional
  expansions rather than competing final report owners.
- Preserved the method-pack boundary: the receipt owner contract is output
  conformance, not a new hot-path routing rule, runtime gate, or completion
  authority.

### Workflow Quality Regression Coverage

- Added a representative workflow-quality sample for real cleanup closeouts
  where fallback retirement, reference deletion, production DB impact checks,
  and verification evidence could otherwise be summarized without the unified
  impact/safety receipt.
- Expanded workflow-quality and governance-completion checks so adjacent
  completion structures cannot replace the `Aegis Impact and Safety Receipt`.
- Kept `using-aegis` out of the new closeout contract so trigger stability and
  context-budget discipline remain unchanged.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.3.7`,
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/governance-completion-contract-check.sh`,
  `bash tests/e2e/trigger-health-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`, and
  `git diff --check`.
- On this Windows host, `bash` resolves to the WSL launcher by default; release
  verification used Git Bash at `C:\Program Files\Git\bin\bash.exe`, matching
  the known release-checklist environment note.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.6` to `2.3.7`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.6 (2026-07-08)

### Aegis Impact and Safety Receipt

- Added `verification-before-completion` as the canonical owner of the unified
  `Aegis Impact and Safety Receipt` for non-trivial Aegis-shaped completion.
- Standardized the compact closeout around key judgment, avoided misfix,
  boundary held, baseline alignment, complexity control, evidence strength,
  uncovered risk, next verification, and Aegis path.
- Localized receipt titles, labels, and prose to the user's language while
  keeping commands, paths, code identifiers, enum values, and evidence strings
  in their original form.

### Workflow Closeout Consolidation

- Updated anti-entropy governance, execution, long-task continuation, and
  systematic debugging workflows so they feed completion evidence into the
  unified receipt instead of inventing independent final-response shapes.
- Retained expanded semantic slots such as `Governance Receipt`, `Baseline
  Alignment`, `Complexity Delta`, `Complexity Closure`, `Readiness Summary`,
  `Goal Closure`, `Retirement Closure`, and `ADR Backfill Check` for audit,
  release, architecture, and high-risk work.
- Clarified that the receipt remains advisory method-pack output and does not
  grant `GateDecision`, `PolicySnapshot`, or final `completion authority`.

### User Confidence Signals

- Added explicit safety-oriented closeout language for baseline alignment,
  implementation drift, design-defect visibility, complexity control, evidence
  strength, and residual risk.
- Strengthened workflow-quality fixtures and validator coverage so completion
  responses must preserve value, safety, localization, and auditability signals.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.3.6`,
  `bash scripts/bump-version.sh --check`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`,
  `python -m json.tool tests/e2e/fixtures/workflow-quality-matrix.json`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.5` to `2.3.6`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.5 (2026-07-04)

### TDD Default Mode

- Changed Aegis TDD mode to default to `off` across `aegis-doctor`, host
  bootstrap hooks, OpenCode integration, and public documentation.
- Kept automatic TDD routing available as an explicit opt-in through
  `tdd-mode auto`, `AEGIS_TDD_MODE=auto`, or direct query markers such as
  `TDD Route: strict`, `strict TDD`, `test-first`, and
  `RED / GREEN / REFACTOR`.
- Preserved `verification-before-completion` in both `off` and `auto` modes so
  turning off automatic TDD never weakens completion evidence.

### Complexity Governance

- Recalibrated 800+ line maintained artifacts as soft pressure signals rather
  than automatic edit bans.
- Added stronger pressure signals for 1200+ line maintained artifacts and files
  in the largest 5-10% of a target project.
- Added `Pre-Edit Owner-Fit Decision` to implementation workflows so overloaded
  or mixed-purpose owners classify edit intent before non-trivial source edits.
- Clarified that `new-responsibility` should not be added in place to an
  over-budget or mixed-purpose owner by default.
- Added `Completion-Time Complexity Repair Decision` so completion-time
  complexity overruns are classified as `govern-now`, `follow-up-required`, or
  `not-complete` before additional owner extraction or scope expansion.

### Final Output Semantics

- Updated the process baseline to treat `Facts -> Inferences -> Conclusions` as
  an information-ordering principle instead of a fixed top-level response
  template.
- Renamed `Final Output Contract` to `Final Output Semantic Slots / Attention
  Anchors` and clarified that these anchors must not override workflow-owned
  output structures such as findings-first code review, verification evidence
  slots, repair/retirement closure, complexity closure, `Aegis Visibility`,
  `Execution Readiness View`, or requested `Trace Digest`.
- Updated the global user rules template shipped by Aegis with the same
  anti-template guidance for future host configuration.

### Regression Coverage

- Expanded workflow-quality checks for default-off TDD mode, explicit TDD query
  markers, pre-edit owner-fit decisions, completion-time complexity repair
  decisions, and final-output semantic slots.
- Updated the workflow-quality matrix and validator so owner-fit and
  completion-time complexity decisions remain part of the expected workflow
  contracts.
- Updated activation-mode, TDD-policy, doctor, and workspace helper tests for
  the default-off TDD configuration.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.3.5`,
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `python -m pytest tests/helpers -q`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/tdd-policy-check.sh`,
  `bash tests/e2e/activation-mode-check.sh`,
  `bash tests/e2e/aegis-doctor-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.4` to `2.3.5`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.4 (2026-07-04)

### Final Output Ordering

- Reframed `Facts -> Inferences -> Conclusions` as a user-facing ordering
  principle instead of a mandatory top-level response template.
- Updated the English and Chinese workflow guides so final answers present
  evidence-backed facts before interpretation, and interpretation before
  recommendations, decisions, or completion claims.
- Clarified that the ordering principle must not override workflow-owned
  semantic slots or task-specific output contracts such as findings-first code
  review, verification evidence slots, readiness summaries, governance closure,
  `Execution Readiness View`, `Aegis Visibility`, or on-demand `Trace Digest`.

### Attention Anchors

- Added workflow-quality baseline language explaining that required output
  content acts as an attention anchor for the code, contract, evidence, or
  governance logic it names.
- Preserved the useful pressure created by required output content while
  preventing generic response structure from stealing structural ownership from
  the active workflow.

### Regression Coverage

- Added workflow-quality e2e assertions that protect the new ordering language
  in both workflow guides.
- Added baseline checks that ensure required output content remains an
  attention anchor and does not replace active workflow ownership.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/artifact-schema-check.sh`,
  `bash tests/e2e/governance-completion-contract-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`,
  `bash tests/e2e/run-all.sh --full --host-profile fast`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `python -m pytest tests/helpers -q`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.3` to `2.3.4`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.3 (2026-07-04)

### Execution Readiness View

- Added an advisory `Execution Readiness View` so medium/high-risk plans,
  subagent handoffs, long-running work, and contract-sensitive changes can make
  execution expectations explicit before implementation.
- Rendered the view from existing drafts, plans, checkpoints, and baseline docs
  instead of introducing a new authoritative artifact owner.
- Documented the view shape in the runtime-ready boundary: intent lock, scope
  fence, baseline lock, approved behavior, owner and contract constraints,
  compatibility boundary, retirement boundary, task batches, test obligations,
  review gates, drift and rewind rules, evidence required before completion,
  and advisory boundary.

### Workflow Integration

- Updated `writing-plans` to decide when the view is required and render it
  before execution handoff for architecture, contract, compatibility,
  retirement-sensitive, subagent, and long-running plans.
- Updated `executing-plans` and `long-task-continuation` so active slices are
  compared against the view during resume, implementation, and drift handling.
- Updated `verification-before-completion` so the view constrains readback and
  verification coverage without becoming verification evidence by itself.

### Boundary And Schema Discipline

- Updated the artifact schema, process baseline, workflow guide, and workflow
  quality baseline to keep `Execution Readiness View` human-readable and
  advisory.
- Explicitly rejected `Execution Readiness View` as a new JSON artifact type,
  authoritative `GateDecision`, authoritative `PolicySnapshot`, or final
  completion authority.
- Preserved the Aegis visibility behavior introduced in `v2.3.2`; this release
  does not weaken loaded-skill entry visibility or final closeout visibility.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `python -m pytest tests/helpers -q`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/long-task-continuation-check.sh`,
  `bash tests/e2e/artifact-schema-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/governance-completion-contract-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.2` to `2.3.3`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.2 (2026-07-02)

### Aegis Visibility Non-Omission

- Hardened `using-aegis` so non-trivial loaded Aegis skills must surface one
  natural visibility sentence at the first substantive user-visible stage.
- Hardened `verification-before-completion` so concise final answers still keep
  one task-specific Aegis closeout sentence tied to boundary, evidence, or
  residual risk.
- Updated the process and workflow-quality baselines to treat after-the-fact
  visibility explanations as recovery, not as a substitute for required entry
  visibility and final closeout.
- Added workflow-quality fixture coverage for loaded-skill entry visibility and
  compressed final answers that must preserve Aegis visibility.

### Kimi Code CLI Native Host Support

- Added a dedicated Kimi Code CLI install guide through native Agent Skills
  discovery at `$KIMI_CODE_HOME/skills/<skill-name>/SKILL.md`, with
  `~/.kimi-code/skills` as the default when `KIMI_CODE_HOME` is unset.
- Retired the old Kimi-as-Codex-umbrella assumption as the canonical path;
  `~/.agents/skills/` remains documented only as Kimi's official shared
  compatibility fallback.
- Updated `aegis-update.py` so `kimi`, `kimi-code`, and `kimi-code-cli` default
  to `direct-child` discovery, infer the native Kimi discovery root, and perform
  register-time sync plus doctor verification for direct-child sync modes.
- Added compatibility handling for legacy Kimi registry entries without an
  explicit `discoveryRoot`, using Kimi's native default root instead of failing
  the update path.
- Added a Kimi host boundary e2e check and wired it into the Layer 1 fast check
  suite.

### Documentation And Host Matrix

- Added `docs/README.kimi-code.md` and linked it from the root READMEs, current
  authority map, release checklist, install verification policy, activation
  mode policy, and goal-framing policy.
- Updated the host compatibility matrix and known limitations so Kimi remains a
  structural host target until a fresh live Kimi Code CLI smoke proves runtime
  skill discovery after restart.
- Updated `update-aegis` skill guidance with the Kimi direct-child registration
  example.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/test_aegis_update.py`,
  `python -m py_compile scripts/aegis-update.py tests/helpers/test_aegis_update.py`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `bash tests/e2e/kimi-code-host-boundary-check.sh`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/install-verification-policy-check.sh`,
  `bash tests/e2e/activation-mode-check.sh`,
  `bash tests/e2e/goal-framing-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.1` to `2.3.2`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.1 (2026-07-02)

### Owner-Workflow Aegis Visibility

- Added an `Aegis Visibility` semantic slot for task-owning workflows so
  non-trivial Aegis-shaped work can show why Aegis changed the decision path
  without falling back to a generic used-skills log.
- Distributed visibility across goal framing, brainstorming, planning,
  systematic debugging, TDD, plan execution, first-principles review,
  long-task continuation, code review, ADR recording, anti-entropy governance,
  and verification.
- Kept `using-aegis` route-only and preserved `Trace Digest` as an on-demand
  audit/debug/release/long-task surface rather than default ceremony.

### Workflow Quality Baseline

- Updated `AEGIS_WORKFLOW_QUALITY_BASELINE.md` and
  `AEGIS_PROCESS_BASELINE.md` so `Aegis Visibility` is owned by the active
  workflow and remains advisory method-pack discipline.
- Added an `executing-plans` compact contract to the workflow quality baseline,
  covering plan review, active todo, change necessity, complexity budget,
  pre-edit complexity, verification, and checkpoint evidence.
- Clarified that natural visibility may satisfy the governance surface when it
  names the task-specific boundary, evidence discipline, or residual risk that
  Aegis kept visible.

### Skill Coverage

- Updated owner workflow skills to expose task-specific visibility:
  `goal-framing`, `brainstorming`, `writing-plans`,
  `systematic-debugging`, `test-driven-development`, `executing-plans`,
  `first-principles-review`, `long-task-continuation`,
  `requesting-code-review`, `recording-architecture-decisions`,
  `anti-entropy-governance`, and `verification-before-completion`.
- Preserved fast-path cheapness: tiny work can remain implicit unless the user
  asks why Aegis did or did not shape the task.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh 2.3.1`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/trigger-health-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped declared package and host manifest versions from `2.3.0` to `2.3.1`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.3.0 (2026-07-01)

### Default English README

- Made the English README the default GitHub entry point at `README.md`.
- Moved the Chinese README to `README.zh-CN.md`.
- Kept `README.en.md` as a compatibility pointer so existing links continue to
  lead users to the current English and Chinese README files.

### User-Visible Governance

- Added a compact `Trace Digest` contract so Aegis can make governance work
  visible without exposing raw chain-of-thought.
- Added confidence labels, evidence-chain summaries, host capability markers,
  redaction guidance, and trace overhead budgets for user-facing workflow
  visibility.
- Added benchmark signals for trace digest coverage, static rule-effect
  attribution, external skill-call stability, and negative fast-path noise
  control.

### Change Necessity For New Source Paths

- Tightened `Change Necessity` so every new source-code path must surface the
  code-change necessity check before editing.
- Clarified that tiny helpers, guards, branches, fallback paths, adapters, and
  owner-creating code are not exempt merely because they are small.
- Kept pure documentation/config work and mechanical edits on lighter paths
  when no new source-code path is introduced.

### Workflow Quality Coverage

- Added smoke coverage for ordinary bug repair, requested fallback work, old
  path cleanup, new helper paths, strict TDD guard creation, executing-plan code
  creation, and white-box trace digest requests.
- Updated workflow-quality validation so new semantic slots stay owned by the
  relevant workflow rather than drifting into duplicate governance owners.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped all declared package and host manifest versions from `2.2.3` to
  `2.3.0`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.2.3 (2026-06-28)

### Quick Bug Routing

- Routed bug, failure, regression, and unexpected-behavior fast paths from
  `using-aegis` into `systematic-debugging` so small bug fixes still collect
  root-cause evidence before source edits.
- Kept `using-aegis` within its hot-path budget and preserved it as a compact
  router instead of moving the full `Change Necessity` checklist into the
  always-loaded entrypoint.
- Updated workflow-quality checks and doctor hot-path verification so this
  routing stays covered.

### Explicit Change Decisions

- Tightened `systematic-debugging` quick bug lane so natural prose still keeps
  an explicit decision token such as `Decision: code-change`.
- Clarified that minimum-boundary wording is not a substitute for the decision.
- Kept the decision advisory method-pack discipline, not a `GateDecision`,
  `PolicySnapshot`, or completion authority.

### Replay And Benchmark Calibration

- Added a quick-bug replay scenario for change necessity before the fix
  boundary.
- Extended the replay analyzer to score required skills, semantic slots,
  ordered semantic terms, and natural Chinese/English phrasings without turning
  keyword matching into runtime authority.
- Calibrated live replay evidence against multiple real Codex transcripts:
  the analyzer now treats direct live failures caused by missing aliases as
  test-oracle false negatives, while the no-Aegis baseline remains a failing
  contrast arm.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `python -m py_compile scripts/aegis-doctor.py tests/helpers/run_controlled_replay_samples.py tests/helpers/normalize_live_replay_log.py tests/helpers/validate_agentic_benchmark_matrix.py tests/helpers/validate_workflow_quality_matrix.py`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/controlled-replay-check.sh`,
  `bash tests/e2e/agentic-benchmark-check.sh`,
  live replay transcript rechecks for 11 post-skill Codex samples,
  no-Aegis baseline negative recheck,
  `bash tests/e2e/run-all.sh --full --host-profile fast`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped all declared package and host manifest versions from `2.2.2` to
  `2.2.3`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.2.2 (2026-06-28)

### Change Necessity Before Source Edits

- Added `Change Necessity Before Source Edits` to the process baseline so
  non-trivial source edits must make the code-change decision visible before
  implementation.
- Introduced the compact `Change Necessity` semantic slot with explicit
  `no-change`, `docs/config-only`, `code-change`, and `needs-clarification`
  decisions.
- Kept `using-aegis` compact and route-only. The hot path now delegates
  `Change Necessity` to the owning workflow instead of carrying a heavier
  checklist itself.

### Workflow Ownership

- Updated `writing-plans` so implementation plans state why code changes are
  necessary before task decomposition and carry the minimum boundary into files,
  tasks, and verification.
- Updated `systematic-debugging` so root-cause repair work surfaces
  `Change Necessity` before non-trivial repair code, while preserving
  Patch-Shape Triage, Ripple Signal Triage, Minimality Check, and Pre-Edit
  Complexity Check behavior.
- Updated `test-driven-development` so strict RED/GREEN work confirms code
  change necessity before entering production code edits.

### Workflow Quality Coverage

- Added a workflow-quality dimension and representative sample for
  change-necessity-before-code-change behavior.
- Extended compact output contracts and validation so `writing-plans`,
  `systematic-debugging`, and `test-driven-development` keep the semantic slot
  visible.
- Added e2e checks that confirm `using-aegis` delegates the responsibility
  without absorbing the heavier workflow contract.

### Verification

- Fresh checks passed:
  `bash scripts/bump-version.sh --check`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`,
  `bash tests/e2e/workflow-quality-check.sh`,
  `bash tests/e2e/context-budget-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/tdd-policy-check.sh`,
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`, and
  `git diff --check`.

### Release Surface

- Bumped all declared package and host manifest versions from `2.2.1` to
  `2.2.2`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.2.1 (2026-06-25)

### Discovery Contract

- Added explicit prefixed direct-child discovery verification to
  `aegis-doctor.py` through `--discovery-name-prefix`. Hosts that expose
  Aegis skills as `aegis-<skill-name>/SKILL.md` can now verify that generated
  view without renaming the canonical `skills/<skill-name>/SKILL.md` source
  tree.
- Added `discoveryNamePrefix` to the host-scoped update registry contract.
  `aegis-update.py` now uses the same prefix mapping when creating
  direct-child links, copying skill directories, and passing discovery
  verification through to doctor.
- Kept the canonical owner model unchanged: method-pack `skills/` remains the
  source of truth, while prefixed host directories are generated compatibility
  views rather than second editable skill owners.

### Copilot Verification

- Updated the GitHub Copilot guide to document the prefixed repository skill
  view at `.github/skills/aegis-<skill-name>/SKILL.md` and the matching doctor
  command:
  `python scripts/aegis-doctor.py --discovery-root <target-repo>/.github/skills --discovery-name-prefix aegis-`.
- Synced the host compatibility snapshot, known limitations, trigger-health
  baseline, release checklist, root install prompts, and `update-aegis` skill
  so prefixed discovery roots are recorded as an explicit host exposure
  contract.

### Verification

- Added helper and e2e coverage for canonical discovery roots, identity
  direct-child discovery roots, prefixed direct-child discovery roots, stale
  compatibility exposure rejection, update-registry prefix propagation, and
  prefixed direct-child copy/link sync.
- Fresh checks passed:
  `python tests/helpers/test_workspace_text_write_compat.py`,
  `python tests/helpers/test_aegis_update.py`,
  `python tests/helpers/test_parse_codex_skills.py`,
  `bash tests/e2e/aegis-doctor-check.sh`,
  `bash tests/e2e/copilot-qoder-host-boundary-check.sh`,
  `bash tests/e2e/install-verification-policy-check.sh`,
  `bash tests/e2e/trigger-health-check.sh`,
  `bash tests/e2e/boundary-compliance-check.sh`,
  `bash tests/e2e/governance-completion-contract-check.sh`,
  `bash tests/e2e/context-budget-check.sh`, and
  `bash tests/e2e/layer1-fast-check.sh --host-profile none`.

### Release Surface

- Bumped all declared package and host manifest versions from `2.2.0` to
  `2.2.1`.
- This release still ships `Aegis Method Pack (runtime-ready)`. It does not add
  authoritative `GateDecision`, `PolicySnapshot`, or `completion authority`.

## v2.2.0 (2026-06-24)

### Pre-Addition Minimality

- Added `Pre-Addition Minimality` to the process baseline. Before Aegis adds a
  new owner, skill, artifact, adapter, fallback, workflow step, or benchmark
  metric, the workflow now checks whether an existing owner can carry the
  behavior.
- Added the shared `Existence Check` contract for `brainstorming` and
  `writing-plans`, with explicit fields for proposed surface, reuse candidate,
  creation proof, entropy / retirement impact, and the final
  `reuse-existing` / `add-with-proof` / `defer` / `reject` decision.
- Extended `systematic-debugging` minimality discipline so candidate fixes that
  add branches, fallbacks, owners, adapters, or compatibility paths name the
  existing owner / reuse path and provide existence proof before editing.
- Added `docs/current/AEGIS_MINIMALITY_REFERENCE.md` as the public reference for
  checking before adding skills, artifacts, host adapters, fallbacks, and
  benchmark metrics. The reference remains advisory method-pack guidance and
  does not create a runtime gate or completion authority.

### Benchmark And Deferred Work Baselines

- Added `docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md` and its matrix
  fixture to define how Aegis can be measured against no-Aegis and explicit
  Aegis arms across representative agentic tasks.
- The benchmark baseline prioritizes governance-quality signals such as route
  correctness, evidence freshness, authority boundary, false-completion rate,
  owner-fix accuracy, retirement coverage, workspace laziness, and task
  completeness. Cost, time, token count, and diff size remain supporting
  metrics rather than primary Aegis success claims.
- Added `docs/current/AEGIS_DEFERRED_LEDGER.md` plus
  `scripts/aegis-deferred-ledger.py` for searchable `aegis-followup` and
  `aegis-retire` markers. The ledger records retained follow-up and retirement
  work, but does not decide whether a deferral is acceptable and does not grant
  completion authority.

### Host And Workflow Verification

- Added thin-bootstrap-adapter invariants so host bootstrap surfaces continue to
  source the canonical `skills/using-aegis/SKILL.md` hot path or a host-native
  reference instead of copying the full method body into a separate prompt
  owner.
- Added host instruction invariant checks for global rules, GitHub Copilot
  instructions, and Gemini references so agent-facing surfaces preserve the
  method-pack boundary, evidence-before-completion rule, and target-project
  priority order.
- Added a lightweight host adapter smoke check that parses core manifests,
  hook configs, version fields, expected assets, and the no-live-workspace
  boundary.
- Extended the workflow-quality matrix and validator for pre-addition
  minimality samples, `Existence Check` compact output contracts, and the
  expanded `Minimality Check` in debugging.

### Release Surface

- Bumped all declared package and host manifest versions from `2.1.8` to
  `2.2.0`.
- Registered the new agentic benchmark, host instruction invariant, bootstrap
  adapter contract, deferred ledger, minimality reference, and host adapter
  smoke checks in `tests/e2e/layer1-fast-check.sh`.

## v2.1.8 (2026-06-22)

### Root-Cause Claim Discipline

- Added a `Pre-Claim Gate` to `systematic-debugging` (new `Phase 3.5`). When a
  patch-shape signal fires (guard, fallback, consumer/caller patch,
  artifact/cache patch, or sample-only naming), the agent must pass five
  mechanical checks before claiming a root cause: causal closure, falsifier
  checked, adversarial self-refutation, topology classified, and layer-ceiling
  proof. This addresses recurring premature closure, where an intermediate
  breakpoint or ripple is summarized as the root cause. The gate is advisory
  method-pack discipline; it is not a `GateDecision`, `PolicySnapshot`, or
  completion authority. The quick bug lane is exempt when no patch-shape
  signal fires.
- Added a `Causal Topology Gate` that replaces the implicit single-root
  default with explicit classification into six topologies: `single-root`,
  `single-root-multi-symptom`, `chain`, `independent-compound`,
  `conjunctive-cluster`, and `disjunctive-or`. Cluster and compound
  classifications require member enumeration with necessity and sufficiency
  tests, plus an anti-disguise check that seeks a shared upstream cause (which
  collapses a cluster back to single-root-multi-symptom when found).
- Added two hard signals (`H14` cluster member not enumerated or necessity
  tested; `H15` anti-disguise check skipped) and two depth signals (`D6`
  topology explicitly classified; `D7` anti-disguise check executed) to the
  `systematic-debugging` quality gate.
- Added a supporting doc `root-cause-claim-contract.md` with the gate
  rationale, the six-topology table, member proof requirements, and a worked
  example replaying a real two-turn session where the gate would have caught
  both a premature L4 stop and a hidden second root.
- Added two workflow-quality fixtures: a conjunctive-cluster case that
  collapses to a spec-gap single root, and an independent-compound case with
  divergent chains. Extended the matrix validator to require the new
  `topology` field on layer-stop samples and to enforce topology-specific
  signals and prohibitions on the new fixtures.

### Release Surface

- Bumped all declared package and host manifest versions from `2.1.7` to
  `2.1.8`.
- Extended `debugging-patch-shape-gate-check`, `workflow-quality-check`, and
  the matrix validator so the pre-claim gate, topology gate, and new depth
  signals remain covered by automated policy verification.

## v2.1.7 (2026-06-20)

### Requirements Baseline Readiness

- Expanded the public `Product / Requirement Baseline` definition from a narrow
  problem / acceptance view into a fuller requirements baseline shape covering
  sources, goals and scope, users / scenarios, requirement item categories,
  acceptance and verification criteria, open questions, and change records.
- Added a lightweight `Requirement Ready Check` contract for design, planning,
  execution, and completion workflows. It remains method-pack guidance only and
  does not create a runtime gate, schema authority, or completion authority.
- Updated `brainstorming`, `writing-plans`, and
  `verification-before-completion` so requirement gaps are surfaced before
  design recommendation, task decomposition, or completion claims.
- Clarified completion wording so a completed task or slice is not overstated
  as accepted requirement satisfaction.

### TDD Trigger Boundary

- Narrowed native-host entry into `test-driven-development` to explicit TDD
  markers such as `TDD Route: strict`, `strict TDD`, `test-first`, or
  `RED / GREEN / REFACTOR`.
- Documented the `AEGIS_TDD_MODE=off` boundary for Codex and native
  direct-skill hosts: it disables automatic Aegis-side TDD routing but does not
  weaken completion verification.
- Added workflow-quality and TDD policy samples that prevent strict TDD from
  being inferred from risky implementation wording alone when TDD mode is off.

### Release Surface

- Bumped all declared package and host manifest versions from `2.1.6` to
  `2.1.7`.
- Extended workflow-quality checks so the requirements readiness and TDD trigger
  boundaries remain covered by automated policy verification.

## v2.1.5 (2026-06-15)

### ZCode Direct-Child Skill Discovery Fix

- Rewrote `docs/README.zcode.md` to document the direct-child skill-directory
  install (depth-1 discovery, mirroring CC GUI and Windsurf) as the primary
  path. The prior v2.1.4 plugin-marketplace-only guide could cause silent
  zero-skill discovery because ZCode's scanner does not read umbrella skill
  directories. The universal `README.en.md` Quick Install prompt now routes
  ZCode to the correct depth-1 steps with no ZCode-specific prompt needed.
- Added depth-1 direct-child discovery-shape wording to the host compatibility
  matrix (ZCode row and section 4), known-limitations section 2.22 Retention
  Reason, and the ZCode boundary test (`--discovery-root`,
  `--discovery-shape direct-child`, `mklink /J` / `ln -sfn` install shape,
  umbrella pitfall).
- Kept the Claude-Code-compatible plugin marketplace path as a documented
  secondary install with a fallback pointer to the verified direct-child path.
- Version bump 2.1.4 -> 2.1.5 across all 8 declared files.

## v2.1.4 (2026-06-14)

### ZCode Host Adaptation (Structural, Full Parity)

- Registered `ZCode` as a structural host target, on equal footing with the
  other 13 hosts. ZCode natively reads `.claude-plugin/marketplace.json`
  (Claude Code plugin format), so Aegis's existing plugin skeleton works with
  zero code changes.
- Documented the install path (`/plugin marketplace add GanyuanRan/Aegis` →
  `/plugin install aegis@aegis-dev`), `@`-prefix `SKILL.md` skill discovery,
  `AGENTS.md` repository guidance, and the ZCode Memory surface in the new
  `docs/README.zcode.md`.
- Added a dedicated `tests/e2e/zcode-host-boundary-check.sh` (25 assertions
  across 10 boundary surfaces plus guide content) and registered it in
  `layer1-fast-check.sh`, matching the per-host boundary-test convention used
  by every other host.

### Cross-Surface Host Registration

- Synced ZCode into the host compatibility matrix (§3.2 table, §4 prose, §5
  evidence sources), the method-pack release checklist (doc-check list plus a
  confirm bullet), a new `§2.22 ZCode Structural Support` known-limitations
  entry, the prompt-hygiene host list, and the English / Chinese root README
  host tables.
- Appended ZCode to the `install-verification`, `goal-framing`, and
  `activation-mode` policy test arrays so the host is held to the same
  complete-install and portable goal-entry contracts as every other host.
- Kept ZCode at `structural` status with no fresh-smoke claim, consistent with
  the other 12 non-Codex/OpenCode hosts; the fresh-smoke upgrade is deferred
  to the §2.22 Retirement Trigger.

## v2.1.3 (2026-06-13)

### Antigravity CLI Closeout Lane And Boundary Sync

- Reframed `Antigravity CLI` as the current active Google-host closeout target
  while keeping `Antigravity IDE` and `Antigravity App` explicitly structural.
- Added a dedicated `tests/antigravity/` verification lane plus current-doc,
  README, and release-checklist sync so the repo now records a precise
  environment blocker instead of a vague host-support gap when `agy` is absent.
- Kept updater and doctor semantics bounded to the verified current contract:
  `syncMode = repo-only`, `discoveryShape = host-managed`, and no claim that a
  plugin-managed Aegis install surface is already verified.

### Helper-Backed ADR Lifecycle Commands

- Extended `scripts/aegis-workspace.py` with helper-backed `new-adr`,
  `amend-adr`, and `supersede-adr` commands for target-project
  `docs/aegis/adr/` workspaces.
- Added structural ADR validation for filename shape, required sections,
  supersession markers, and `INDEX.md` coverage without turning the helper into
  architecture or completion authority.
- Wired the dedicated ADR and completion skills to route target-project ADR
  writeback through the shared workspace helper and to preserve helper `check`
  output as completion evidence.

### Workspace, Skill, And Release-Surface Coverage

- Expanded `tests/e2e/aegis-workspace-check.sh` to exercise ADR creation,
  amendment, supersession, duplicate rejection, and broken-ADR detection.
- Updated current docs so ADR Auto Backfill no longer claims helper automation
  is merely future work; the remaining limitation is now narrowed to workflow
  judgment for ADR triggering and baseline-sync truth.

## v2.1.1 (2026-06-11)

### Baseline Usage Draft And Attention-Drift Visibility

- Added `BaselineUsageDraft` as a runtime-ready advisory artifact that makes
  baseline/context attention drift visible without claiming host-level
  authoritative injection proof or internal model-attention proof.
- The artifact now records required baseline refs, acknowledged-before-plan
  refs, cited refs, missing refs, and an advisory decision, with optional
  host-projected `deliveredContextRefs`.

### Planning, Design, And Long-Task Workflow Integration

- Extended `brainstorming`, `writing-plans`, and `long-task-continuation` so
  baseline usage can be surfaced before design approval, before implementation
  planning, and during resumable execution slices.
- Tightened the user-visible workflow contracts so missing baseline refs can
  pause safely in `needs-baseline-readback` instead of silently allowing a
  plausible but under-constrained plan to continue.

### Workspace Helper, Fixtures, And Scenario Coverage

- Extended `scripts/aegis-workspace.py` with `BaselineUsageDraft` schema
  validation, lifecycle creation support, filename inference, and the new
  `add-baseline-usage` helper command.
- Added artifact fixtures, long-task checks, workflow-quality matrix updates,
  and representative scenario transcript coverage so the new artifact is
  exercised in both contract validation and release-facing behavior checks.

## v2.1.0 (2026-06-11)

### Artifact-Wide Complexity Governance

- Added `docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md` as the canonical
  current owner for complexity governance across maintained source, maintained
  test source, plan / decision artifacts, and process artifacts.
- Extended workflow contracts so planning and execution stages now carry
  `Complexity Budget`, and completion carries `Complexity Closure` plus
  `Major Complexity Alert`.
- Tightened the completion rule so `exceeded-unresolved` complexity overrun
  blocks an Aegis completion claim instead of being hidden inside a generic
  residual-risk note.

### Workflow Quality And Fixture Alignment

- Updated workflow-quality baselines, skill contracts, matrix fixtures, and
  validation helpers so maintained oversized test files and plan/process
  artifact sprawl are treated as first-class complexity signals.
- Added representative workflow-quality samples for oversized maintained test
  file governance and plan-artifact fan-out, keeping the forcing function
  visible in release-facing checks.

### Copilot Hook Hardening And Cross-Host Warning Hygiene

- Hardened the Copilot PowerShell session-start wrapper so Windows environments
  without `bash` still emit a valid compact `additionalContext` bootstrap
  instead of silently returning `{}`.
- Kept the fallback bounded to a minimal bootstrap path rather than cloning the
  full shared bash hook owner.
- Reworded the legacy custom-skills warning in `hooks/session-start` so it now
  points users to the current host's supported skills surface instead of
  assuming a Claude-only migration path.

### Claude Hook Contract Surface Realignment

- Restored `hooks/hooks.json` as the current Claude Code hook contract surface
  and synchronized the Windows hook guidance and permission check with that
  owner.
- Kept `hooks/run-hook.cmd` as the Windows-safe command wrapper Claude Code
  still invokes for `SessionStart`.

## v2.0.8 (2026-06-08)

### Claude Code Hook Contract Ownership Alignment

- Moved the Claude Code `SessionStart` hook contract into
  `.claude-plugin/plugin.json` so the Claude-specific hook owner now lives with
  the Claude plugin manifest instead of a generic root `hooks/` file.
- Removed the obsolete `hooks/hooks.json` compatibility surface and kept
  `hooks/run-hook.cmd` as the command wrapper Claude Code still invokes.

### Windows Hook Documentation And Verification Sync

- Updated `docs/windows/polyglot-hooks.md` so the Windows-safe hook guidance now
  points to `.claude-plugin/plugin.json`, explains why the Claude hook contract
  should stay out of the generic root `hooks/` surface, and preserves the
  reusable `.cmd` wrapper pattern.
- Updated `tests/e2e/claude-hook-permissions-check.sh` and the historical
  release-note readback so Claude hook verification now inspects the current
  manifest owner.

### README Surface And Skill-Path Boundary Clarifications

- Updated multiple release-facing end-to-end checks to match the current README
  surface layout where `README.md` is the Chinese default surface and
  `README.en.md` is the English companion.
- Clarified in `CLAUDE.md`, `GEMINI.md`, `docs/README.codex.md`, and
  `skills/writing-skills/SKILL.md` that repository `skills/` paths are the
  canonical source layout while hosts may load installed or generated views at
  runtime, and that bare supporting-file references inside a skill resolve
  relative to that skill directory unless stated otherwise.

## v2.0.7 (2026-06-07)

### Copilot Native Session-Start Hook Compatibility

- Added a repository-level GitHub Copilot `sessionStart` hook configuration at
  `.github/hooks/session-start.json` instead of reusing the Claude Code plugin
  `run-hook.cmd` command string in Copilot's Windows PowerShell execution path.
- Added a Windows PowerShell wrapper at `hooks/copilot-session-start.ps1` so
  Copilot can execute the Aegis bootstrap through the host's native
  `powershell` hook contract while still reusing the canonical `hooks/session-start`
  bootstrap owner.

### Compact Hook JSON Output For Copilot

- Extended `hooks/session-start` with a compact JSON output mode gated by
  `AEGIS_HOOK_JSON_STYLE=compact`.
- Kept existing Claude Code and Cursor hook output shapes intact while giving
  Copilot's command-hook contract the single-line JSON it expects.

### Copilot Host Docs And Boundary Baseline Alignment

- Updated the GitHub Copilot host guide to document optional repository hooks,
  the Windows PowerShell parse-error failure mode, and the correct
  `.github/hooks/session-start.json` usage path.
- Updated the current host compatibility snapshot, known limitations, and
  release checklist so Copilot's structural support now explicitly includes
  repository hooks without overstating fresh host closeout.

### Regression Coverage For Copilot Hook Surfaces

- Added targeted hook tests for compact JSON output and preserved Claude Code
  nested output shape behavior.

## v2.0.6 (2026-06-05)

### Dual-Baseline Bootstrap For New Project Workspaces

- Reframed the first `docs/aegis/baseline/YYYY-MM-DD-initial-baseline.md`
  expectation from a flat repo inventory into a dual-baseline bootstrap that
  explicitly separates `Product / Requirement Baseline` from
  `Architecture / Runtime Boundary Baseline`.
- Added an initial-baseline shape that requires current truth, non-negotiables,
  non-goals, alignment use, and compatibility boundaries instead of leaving
  early project baselines as generic structure snapshots.

### Workspace Helper Governance Template Alignment

- Updated `scripts/aegis-workspace.py init` so newly created
  `BASELINE-GOVERNANCE.md` files start with dual-baseline roles,
  `Design Defect` / `Implementation Drift`, and the shared
  `scope: requirements | architecture | both` vocabulary.
- Kept workspace `check` backward-compatible with existing legacy
  architecture-only governance files so older target-project workspaces are not
  broken by the template upgrade.

### Current Baseline And Skill Template Synchronization

- Updated the brainstorming skill's initial baseline template to make the first
  project baseline a true dual-baseline bootstrap artifact rather than a
  ten-field inventory checklist.
- Updated `AEGIS_PROCESS_BASELINE.md` so it now distinguishes the first
  bootstrap baseline from later change-date snapshots and explicitly forbids
  regressing to a flat repo-inventory checklist.

### Regression Coverage For Baseline Bootstrap Semantics

- Extended workspace helper verification so `init` must now emit the
  dual-baseline governance headings and scope taxonomy.
- Extended workflow-quality checks so the initial-baseline template and process
  baseline both keep the dual-baseline bootstrap language, non-negotiables, and
  non-goal structure release-visible.

## v2.0.5 (2026-06-05)

### One Canonical Aegis Body Across Hosts

- Clarified and strengthened the cross-host rule that Aegis should keep one
  canonical `method_pack_root`, while host-facing discovery directories,
  plugin caches, copied skills trees, and compatibility exposures are treated
  as generated or host-managed views into that same body.
- Extended the shared updater and host docs so new host registrations prefer
  the configured `~/.config/aegis/config.toml` `method_pack_root` instead of
  silently creating another editable checkout per host.

### Shared-Root Updater Reuse Across Host Registrations

- Extended `scripts/aegis-update.py` to read the shared local Aegis config and
  use `method_pack_root` as the default registration target when available.
- Added shared-root update reuse so multiple registered hosts that point at the
  same method-pack checkout update that checkout once, then refresh each
  host-specific discovery or verification surface separately.
- Preserved host-level differences such as `discoveryRoot`, `discoveryShape`,
  `reloadHint`, and adapter ownership without turning them into a second source
  of truth.

### OpenCode Canonical-Root Preference And Mirror Hygiene

- Updated the OpenCode plugin so it prefers the configured canonical
  `method_pack_root` when generating the OpenCode-visible skills tree.
- Added mirror-manifest tracking so stale mirrored skill targets can be
  refreshed or pruned instead of being silently treated as current.
- Kept the OpenCode-visible `~/.config/opencode/skills/` tree as a generated
  compatibility view while retaining `config.skills.paths` only as a fallback
  exposure layer.

### Cross-Host Installation Guidance Expansion

- Updated Codex, OpenCode, Claude Code, Pi, and Antigravity docs so they all
  describe the same stable model: one canonical Aegis body, different
  host-appropriate exposure shapes.
- Updated the host compatibility snapshot and known limitations docs so the
  canonical-root / generated-view model is release-visible and does not stay
  hidden in session-only reasoning.
- Updated the `update-aegis` skill guidance so host maintenance keeps the
  canonical root and host view boundaries explicit.

### Regression Coverage For Shared-Root Behavior

- Added updater tests for config-driven default root selection and shared-root
  reuse across multiple host registrations.
- Extended the OpenCode plugin-loading coverage so the configured canonical
  method-pack root must win over the bundled plugin checkout when both exist.

## v2.0.4 (2026-06-04)

### Discovery-Shape Readback For Compatibility Exposures

- Extended `scripts/aegis-doctor.py` so discovery-root checks now classify the
  expected discovery shape instead of only proving that a path exists.
- Added explicit readback for canonical method-pack discovery roots versus
  direct-child compatibility exposures, including clear text and JSON fields
  for `expectedDiscoveryShape`, `discoveryShapeStatus`, and
  `compatibilityExposureStatus`.
- Hardened stale-copy detection so compatibility exposures that drift from the
  canonical `skills/` tree now fail structural verification instead of being
  silently treated as current.

### Host Update Registry Separation Of Transport And Visibility

- Extended `scripts/aegis-update.py` so host registrations can store a
  dedicated `discoveryShape` alongside `syncMode`.
- Kept transport semantics and host-visibility semantics separate: `syncMode`
  now describes how Aegis reaches the host surface, while `discoveryShape`
  describes what the host must see there.
- Added copy-mode pruning so stale copied Aegis skill directories are removed
  when refreshing direct-child compatibility exposures from the canonical
  method-pack tree.

### Trigger And Host Baseline Clarifications

- Updated trigger-health and host-compatibility current docs with a compact
  trigger-family vocabulary for diagnostic use without creating a new owner
  layer.
- Clarified in known limitations and host docs that direct-child compatibility
  exposures are generated views from the canonical `skills/` tree, not a second
  editable source of truth.
- Recorded the CC GUI direct-child discovery requirement more explicitly in the
  release-facing host guidance and verification policy.

### Completion Boundary Wording Tightening

- Compressed the `verification-before-completion` TDD completion boundary into
  a shorter, more conservative form.
- Clarified that completion judgment should match the claim to the highest
  available explicit boundary while keeping any higher open boundary visible.
- Kept the change at the wording and contract level without changing Aegis
  completion authority boundaries.

### Verification Coverage Expansion

- Expanded `tests/e2e/aegis-doctor-check.sh` to cover canonical discovery
  roots, direct-child compatibility exposures, and stale-copy rejection.
- Added helper coverage for updater discovery-shape registration, copy-mode
  doctor invocation, stale-skill pruning, and discovery-shape defaults.
- Extended install and CC GUI host boundary checks so the new structural
  discovery semantics stay release-visible.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `2.0.4`.

### Verification

- `bash scripts/bump-version.sh 2.0.4`
- `bash scripts/bump-version.sh --audit`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/cc-gui-host-boundary-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `python tests/helpers/test_aegis_update.py`
- `python tests/helpers/test_workspace_text_write_compat.py`
- `bash tests/e2e/run-all.sh --full --host-profile fast` attempted; all non-Codex
  release suites passed, but the current machine's Codex representative smoke
  was blocked by `401 Unauthorized` from the Responses websocket before any
  assistant reply was produced
- `git diff --check`

## v2.0.2 (2026-06-03)

### TDD Trigger Boundary Hardening For Native Skill Hosts

- Narrowed the `test-driven-development` skill trigger so native skill-discovery
  hosts no longer treat every feature or bugfix request as an automatic TDD
  entrypoint.
- Kept strict TDD auto-loading for explicit strict-TDD requests and already
  approved atomic tasks whose `TDD Route` is `strict`.
- Updated the skill-authoring guidance example so future skills do not regress
  to broad workflow-summary trigger wording.

### Codex TDD Mode Boundary Clarification

- Clarified in the canonical TDD-mode doc and Codex install guides that
  `AEGIS_TDD_MODE=off` disables Aegis-side automatic TDD routing, but does not
  directly override a host's native semantic skill matcher.
- Documented the retained limitation for native skill-discovery hosts: narrow
  trigger wording or host-profile visibility control is still required when the
  host can auto-match skills without the Aegis bootstrap router.

### TDD Policy Regression Coverage

- Expanded `tests/e2e/tdd-policy-check.sh` so release verification now locks the
  narrow `test-driven-development` trigger boundary and the Codex-specific TDD
  mode caveat.
- Updated the Codex-native trigger prompt fixture so TDD smoke coverage asks
  for explicit strict TDD rather than relying on a generic implementation
  request.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `2.0.2`.

### Verification

- `bash scripts/bump-version.sh 2.0.2`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/activation-mode-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast` attempted; non-Codex
  release suites passed, but the current machine's Codex representative smoke
  was blocked by `401 Unauthorized` from the Responses websocket
- `git diff --check`

## v2.0.1 (2026-06-02)

### GitHub Copilot And Qoder Structural Host Support

- Added dedicated host guides for GitHub Copilot and Qoder:
  `docs/README.copilot.md` and `docs/README.qoder.md`.
- Added repository guidance for GitHub Copilot through
  `.github/copilot-instructions.md`.
- Extended the public compatibility snapshot, release checklist, current-doc
  authority map, and known limitations so both hosts are visible as structural
  support surfaces without overstating them as fresh live-smoke closeout.

### Anti-Entropy Governance For Retirement And Deletion Safety

- Added the new `anti-entropy-governance` skill to classify retirement work as
  `delete-first`, `compat-exception`, or `confirmation-first`.
- Extended workflow and process baselines so internal old-path retirement,
  compatibility retention, and persistent-state deletion boundaries are more
  explicit and auditable.
- Added `Anti-Entropy Declaration` and `Data Destruction Guard` expectations to
  completion-time governance so destructive warnings cannot be mistaken for
  authorization.

### Workflow Quality And Verification Coverage Expansion

- Expanded the workflow quality baseline and representative matrix to cover
  duplicate-owner collapse, host fallback retention, internal trigger
  retirement, rebuildable derived-state cleanup, and persistent-state hard-stop
  cases.
- Added dedicated Copilot/Qoder host boundary checks and updated activation,
  goal-framing, install-verification, skill-triggering, and explicit-skill
  suites to include the new host surfaces and anti-entropy path.
- Kept the fast path explicit by adding coverage that plain tiny cleanup does
  not unnecessarily trigger anti-entropy governance.
- Excluded ignored `.opencode` dependency lockfiles from version-audit drift
  noise so release verification reports only Aegis-owned version surfaces.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `2.0.1`.

### Verification

- `bash scripts/bump-version.sh 2.0.1`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/copilot-qoder-host-boundary-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.9.8 (2026-06-02)

### More Perceptible Aegis Closeout

- Updated `verification-before-completion` so non-trivial closeout keeps
  `Aegis` explicitly visible in the final completion summary.
- Clarified that the closeout should show how Aegis shaped the judgment through
  boundary control, evidence discipline, or residual-risk visibility.
- Kept the output advisory and user-facing instead of turning Aegis visibility
  into authority language or an internal trace card.

### More Directly Auditable Completion Notes

- Removed the old single closeout phrase that made Aegis visibility feel too
  formulaic across unrelated tasks.
- Preserved the concise default for single-boundary cases while allowing Aegis
  to appear more than once when multiple governance effects materially shaped
  the judgment.
- Kept the wording tied to task-specific evidence, boundaries, and risk calls
  so the user can audit what Aegis actually contributed.

### Workflow Quality Baseline Alignment

- Updated the workflow quality baseline so Aegis visibility in completion
  output is judged by whether the user can naturally see the governance effect,
  not by whether one fixed sentence appears.
- Explicitly marked repeated identical Aegis closeout wording as a workflow
  quality miss.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.8`.

### Verification

- `bash scripts/bump-version.sh 1.9.8`
- `bash scripts/bump-version.sh --audit`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.9.7 (2026-06-01)

### Goal Closure Contract Coverage

- Added `Non-goals respected` to the `verification-before-completion` compact
  contract so goal closure checks cannot silently ignore scope drift.
- Extended the workflow quality matrix validator and `goal-framing` policy check
  to require the same field wherever completion is judged against a goal frame.

### TDD Local GREEN Dynamic Regression

- Added fixture-backed `scenario-E-tdd-local-green` coverage for the case where
  a strict TDD slice reaches GREEN while parent acceptance remains open.
- Locked the expected downgrade path: local GREEN must remain slice-local and
  report `needs-verification`, covered scope, and uncovered scope instead of
  claiming whole-task completion.
- Added with/without-Aegis transcript contrast fixtures so the regression check
  explicitly catches the premature-closeout behavior Aegis is meant to prevent.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.7`.

### Verification

- `bash scripts/bump-version.sh 1.9.7`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/goal-framing-check.sh`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/layer2-behavior-check.sh`
- `bash tests/e2e/layer3-scenario-check.sh`
- `git diff --check`

## v1.9.6 (2026-06-01)

### TDD Completion Boundary

- Clarified that a passing GREEN cycle proves only the currently expressed
  behavior slice.
- Prevented GREEN from being treated as parent-task acceptance or whole-task
  completion by itself.
- Routed unclear business behavior, success evidence, or acceptance back to
  `brainstorming` or `writing-plans` before strict TDD.

### Slice-Level vs Final Completion

- Clarified that a `Slice Card` goal anchors slice-level completeness only.
- Added explicit completion precedence across `Slice Card`,
  `TaskIntentDraft`, and parent plan/spec acceptance during
  `verification-before-completion`.
- Required covered and uncovered scope to stay visible when only the slice goal
  is satisfied.

### Workflow Quality Coverage

- Added the `tdd-green-local-not-final-completion` representative sample to
  the workflow quality matrix.
- Extended `long-task-continuation` contract coverage to require `Slice Card`
  visibility.
- Updated the matrix validator so `verification-before-completion` now
  requires `Goal status`, `Success evidence`, and `Stop state`.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.6`.

### Verification

- `bash scripts/bump-version.sh 1.9.6`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.9.5 (2026-05-30)

### Goal Framing Continues by Default

- Clarified across the workflow guides, README surfaces, and the
  `goal-framing` skill that `Aegis goal:` is a start protocol, not a stop
  point.
- Documented the default behavior: after producing the compact
  `TaskIntentDraft`, Aegis should continue into the routed workflow in the same
  turn when the user asked to do the work.
- Locked the explicit stop boundary: frame-only behavior applies only when the
  user clearly asks to only define the goal or stop condition, to not execute,
  to not implement, to not write a plan, or to wait for confirmation.

### Workflow Quality Contract Coverage

- Extended the workflow quality baseline and fixture matrix so `goal-framing`
  now requires a visible `Continuation` contract field.
- Added matrix and harness checks that forbid stopping after
  `TaskIntentDraft` in the default path and require continuation evidence in
  the routed workflow.
- Updated the workflow quality matrix validator so the `goal-framing` contract
  explicitly checks both `Stop condition` and `Continuation`.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.5`.

### Verification

- `bash scripts/bump-version.sh 1.9.5`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/goal-framing-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.9.4 (2026-05-30)

### Semantic Slots and Natural Surface

- Added `Semantic Slots and Natural Surface` to the workflow quality baseline so
  Aegis can preserve governance forcing functions without making every
  user-facing response look like an internal process log.
- Clarified that required governance checks may appear as localized headings,
  natural prose, or compact cards when the required slots remain explicit and
  auditable.
- Kept fixed skill traces, used-skill lists, and stage handoff logs reserved
  for audit, debug, release, long-task review, or explicit user request.

### Verification Evidence Slots

- Updated `verification-before-completion` from a rigid `Evidence Card` shape to
  required evidence semantic slots: evidence action, result, covered scope,
  uncovered scope, residual risk, and confidence grade.
- Added `Governance Receipt` as the compact closeout form for non-trivial
  Aegis-shaped work while preserving the boundary that method-pack evidence does
  not grant completion authority.
- Clarified that natural completion notes are valid only when they preserve the
  required evidence, residual-risk, confidence, retirement, baseline, and
  architecture fields.

### Workflow Quality Matrix Coverage

- Added representative matrix samples for natural governance transitions and
  natural completion notes that still expose verification evidence, covered and
  uncovered scope, residual risk, and confidence.
- Updated verification-related expected output shapes from legacy
  `evidence-card` wording to semantic evidence slot wording.
- Extended the matrix validator to require the new semantic-slot samples,
  contract fields, output shapes, and verification signals.

### Contract Test Updates

- Updated `workflow-quality-check.sh` to lock the new semantic-slot baseline,
  verification skill contract, natural-surface allowance, and governance receipt
  expectations.
- Updated `governance-completion-contract-check.sh` to check residual-risk
  semantics instead of only a fixed English field label.
- Preserved owner separation: `using-aegis` remains the routing hot path and
  does not absorb the verification output contract.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.4`.

### Verification

- `bash scripts/bump-version.sh 1.9.4`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.9.0 (2026-05-30)

### Baseline Role Alignment

- Added `Baseline Role Alignment` as the shared workflow quality lens for
  separating product / requirement truth from architecture / runtime boundary
  truth.
- Defined `Product / Requirement Baseline` for accepted problem, success
  evidence, non-goals, workflow constraints, and approved requirement/spec
  intent.
- Defined `Architecture / Runtime Boundary Baseline` for canonical owner,
  contract, source-of-truth boundary, dependency direction, compatibility,
  runtime-ready/method-pack boundary, and retirement state.

### Unified Defect / Drift Vocabulary

- Promoted `Design Defect` and `Implementation Drift` as the primary result
  vocabulary across process baseline, workflow quality baseline, brainstorming,
  completion verification, requesting-code-review, and code-reviewer templates.
- Demoted `Architecture Defect` and `Architecture Drift` to compatibility
  aliases for architecture-scoped `Design Defect` and architecture-scoped
  `Implementation Drift`.
- Updated review prompts and verification contracts so legacy phrases map back
  to the shared vocabulary instead of becoming a second result line.

### Aegis Invocation Visibility

- Added a natural Aegis closeout pattern for non-trivial tasks, so agents can
  briefly name the boundary or quality risk Aegis held steady without emitting
  stiff `Used skills` / `Stage handoffs` cards by default.
- Preserved the method-pack authority boundary: invocation visibility remains
  advisory workflow discipline and does not grant completion authority,
  `GateDecision`, or `PolicySnapshot`.
- Clarified user-language output: user-facing labels and prose follow the
  user's language, while exact commands, paths, identifiers, enum values, and
  necessary Aegis identifiers remain stable.

### Workflow Quality Harness Entropy Reduction

- Kept `tests/e2e/workflow-quality-check.sh` as the stable shell entrypoint
  while extracting heavy workflow quality matrix validation into
  `tests/helpers/validate_workflow_quality_matrix.py`.
- Reduced mixed ownership in the shell harness: doc/skill contract lint stays
  in the shell entrypoint, while scenario matrix validation now has a dedicated
  Python helper.
- Added release-audit hygiene so local ignored incubator content does not create
  false version-drift reports during version bumps.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.9.0`.

### Verification

- `bash scripts/bump-version.sh 1.9.0`
- `bash scripts/bump-version.sh --audit`
- `python -m py_compile tests/helpers/validate_workflow_quality_matrix.py`
- `python tests/helpers/validate_workflow_quality_matrix.py tests/e2e/fixtures/workflow-quality-matrix.json`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.8.5 (2026-05-29)

### Micro-Slice Artifact Budget

- Added the `Micro-Slice Artifact Budget` to the workflow quality baseline so
  long-running workstreams do not create a durable plan or spec for every tiny
  execution slice.
- Defined the `Planless Slice Lane` for micro-slices that are already owned by
  an existing parent spec or parent plan.
- Added the compact `Slice Card` shape for micro-slices: goal, parent
  plan/spec, files, boundary, verification, and stop condition.
- Kept escalation back to durable plan/spec artifacts only for new owner,
  contract, schema, public API, architecture boundary, migration, persistence,
  security/permission, distribution/release, or unclear verification surfaces.

### Workflow Integration

- Updated `writing-plans` so tiny slices under an existing parent plan/spec do
  not save a new plan and instead record a `Slice Card`.
- Updated `long-task-continuation` so micro-slices reuse the parent plan and
  update checkpoint, evidence, and drift state instead of creating per-slice
  plan/spec files.
- Updated the process baseline so the artifact budget becomes part of Aegis's
  long-task governance discipline without expanding the hot path or adding
  runtime authority.

### Workflow Quality Coverage

- Extended `tests/e2e/workflow-quality-check.sh` to lock the micro-slice
  artifact budget into the workflow-quality baseline, process baseline,
  planning skill, and long-task continuation skill.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.8.5`.

### Verification

- `bash scripts/bump-version.sh 1.8.5`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/workflow-quality-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.8.4 (2026-05-29)

### CC GUI Structural Host Support

- Added `docs/README.cc-gui.md` for CC GUI, the JetBrains IDEA plugin layer
  that wraps Claude Code and OpenAI/GPT provider paths.
- Documented the CC GUI OpenAI/GPT provider skill discovery shape:
  `~/.agents/skills/<skill-name>/SKILL.md`, with Windows junction/copy and
  macOS / Linux symlink installation examples.
- Clarified that umbrella installs such as
  `~/.agents/skills/aegis -> ~/.codex/aegis/skills` can keep native Codex
  workflows working but are not the preferred CC GUI OpenAI/GPT provider
  exposure because the umbrella directory does not itself contain `SKILL.md`.
- Clarified that selecting a specific GPT model profile in CC GUI does not by
  itself change the skill discovery shape.
- Kept CC GUI support structural and explicitly fresh-smoke pending; this
  release does not claim live JetBrains plugin smoke, reload behavior, or host
  adapter event rendering closeout.

### Host Compatibility Boundary

- Added CC GUI to the host compatibility matrix, known limitations, release
  checklist, prompt-hygiene boundary, current authority map, and English /
  Chinese README host tables.
- Added `tests/e2e/cc-gui-host-boundary-check.sh` and wired it into the Layer 1
  fast check so future releases keep CC GUI out of release-level fresh smoke
  claims until direct host evidence exists.
- Extended install-verification, goal-framing, and activation-mode checks so
  the CC GUI guide keeps complete-install doctor verification, portable
  `Aegis goal:` entry, and explicit activation-mode caveats aligned with other
  hosts.
- Clarified that visible entries such as `Tool: exec_command` are host adapter
  event rendering concerns. Aegis can reduce unnecessary tool fan-out through
  workflow discipline, but it does not own CC GUI visual folding,
  normalization, or live IDE event behavior.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.8.4`.

### Verification

- `bash scripts/bump-version.sh 1.8.4`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/cc-gui-host-boundary-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `bash tests/e2e/goal-framing-check.sh`
- `bash tests/e2e/activation-mode-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.8.3 (2026-05-29)

### Architecture Integrity Lens

- Added the `Architecture Integrity Lens` to `first-principles-review` as a
  compact advisory check for executable plans that may still encode the wrong
  owner, abstraction, contract boundary, or retirement path.
- The lens now asks for the invariant, canonical owner / contract,
  responsibility overlap, higher-level simplification, retirement / falsifier,
  and verdict before risky approach selection or task decomposition proceeds.
- Kept the lens inside the Aegis Method Pack boundary: it produces guidance and
  residual-risk signals, not an authoritative `GateDecision`, `PolicySnapshot`,
  or completion authority.

### Workflow Integration

- Wired `Architecture Integrity Lens` into `brainstorming` and `writing-plans`
  so architecture-coherence risks are checked before recommendation or
  task decomposition.
- Extended the code-review checklist to ask whether a change solves the problem
  at the highest appropriate owner / contract layer and whether caller-side
  fallbacks are masking source-of-truth or contract fixes.
- Added `Integrity Residual Risk` to completion-time architecture alignment so
  retained overlap, fallback, stale path, or missed higher-level fixes remain
  visible before completion claims.

### Workflow Quality Coverage

- Added the `architecture-integrity-higher-level-path` representative sample to
  `tests/e2e/fixtures/workflow-quality-matrix.json`.
- Extended `tests/e2e/workflow-quality-check.sh` to lock the new lens into the
  workflow-quality baseline, process baseline, planning skills, review
  checklist, and completion check.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.8.3`.

### Verification

- `bash scripts/bump-version.sh 1.8.3`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/first-principles-review-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `python tests/helpers/test_parse_codex_skills.py`
- `git diff --check`

## v1.8.2 (2026-05-28)

### Pi CLI Structural Support

- Added Pi CLI as a structural Agent Skills host target for the Aegis Method
  Pack.
- Added `docs/README.pi.md` with Pi package installation, native skill
  directory installation, complete-install doctor verification, update
  registration, activation-mode caveats, and official Pi reference links.
- Exposed Aegis skills through the root `package.json` with the `pi-package`
  keyword and `pi.skills: ["./skills"]`, so Pi can load Aegis as a package
  resource.
- Updated the host compatibility matrix, known limitations, release checklist,
  prompt-hygiene boundary, and English / Chinese README host tables to include
  Pi CLI without claiming release-level live smoke evidence.

### Host Boundary Guardrails

- Added `tests/e2e/pi-host-boundary-check.sh` and wired it into the Layer 1
  fast check.
- Extended install-verification, goal-framing, and activation-mode policy
  checks so future host docs keep Pi aligned with the existing method-pack
  install and authority boundary.
- Kept Pi support structural until a future Pi live smoke proves skill
  discovery, reload behavior, and `aegis-doctor.py --write-config --json`
  from the installed method-pack root.

### Repository Hygiene

- Added `Aegis_Codeflow/` to `.gitignore` so the incubator workspace stays out
  of the public method-pack release payload.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.8.2`.

### Verification

- `bash scripts/bump-version.sh 1.8.2`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/pi-host-boundary-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `python tests/helpers/test_parse_codex_skills.py`
- `python -m json.tool package.json`
- `git diff --check`

## v1.8.1 (2026-05-27)

### README Install And Update Clarity

- Split the root README quick-start flow into a pure install path and a
  separate update path.
- Simplified the copyable install prompt so it no longer mixes first-time
  installation with method-pack updates.
- Documented both natural-language update requests and the explicit
  `aegis:update` skill request as routes into the local `scripts/aegis-update.py`
  host-scoped update path.

### Command-First Activation Mode

- Simplified activation-mode guidance in the English and Chinese root READMEs:
  users now run `python scripts/aegis-doctor.py activation-mode explicit`
  from the installed method-pack root instead of manually creating
  `config.toml`.
- Kept detailed configuration paths and host caveats in the canonical
  activation-mode current doc.
- Updated the activation-mode e2e policy check so root READMEs are validated
  for the command-first path.

### Version

- Bumped all declared plugin, marketplace, package, and extension manifests to
  `1.8.1`.

### Verification

- `bash scripts/bump-version.sh 1.8.1`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/activation-mode-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `git diff --check`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.8.0 (2026-05-26)

### Host-Scoped Aegis Updates

- Added `aegis:update` as an explicit user-triggered update workflow for
  installed Aegis method packs.
- Added `scripts/aegis-update.py` with host-scoped installation registration,
  status readback, dry-run support, and explicit `--all` handling for users who
  want to update every registered host.
- Preserved predictable multi-host behavior: a plain update targets the current
  or explicitly selected host, while all-host updates require an explicit
  request.
- Kept automatic background updates out of the default path. The registry can
  record `updateMode`, but the method pack does not become a daemon, runtime
  core, or final update authority.

### Install And Documentation Updates

- Added an `update-aegis` skill that routes `aegis:update` requests through the
  host-scoped registry rather than re-discovering every install from scratch.
- Updated Codex install guidance to register the Codex host, verify the
  discovery root, and update through `aegis-update.py update --host codex`.
- Updated the root READMEs, compatibility snapshot, and known limitations to
  describe the new explicit update behavior and its multi-host boundary.
- Refreshed Cursor and Windsurf skill counts and skill tables so their install
  guides match the current method-pack skill set.

### Verification

- `bash scripts/bump-version.sh 1.8.0`
- `python tests/helpers/test_aegis_update.py`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.7.0 (2026-05-25)

### Adaptive TDD Mode

- Added `TDD Mode` with two user-facing modes: `auto` and `off`.
- In `auto`, Aegis now routes implementation through a `TDD Route`:
  `strict` for risky behavior or contract work, `light` for tiny low-risk
  edits, and `skipped` when TDD does not fit the task shape.
- In `off`, Aegis disables automatic TDD routing while preserving explicit
  user/project TDD requests and `verification-before-completion`.
- Added `docs/current/AEGIS_TDD_MODE.md` and updated the process baseline,
  workflow guides, workflow quality baseline, and README guidance to clarify
  that TDD Mode controls test-first discipline, not completion evidence.

### Configuration And Host Bootstrap

- Extended `scripts/aegis-doctor.py` with:
  - `python scripts/aegis-doctor.py tdd-mode auto`
  - `python scripts/aegis-doctor.py tdd-mode off`
- Added `tdd_mode` to user-local config while preserving existing
  `activation_mode` behavior.
- Updated the Claude/Cursor/Copilot session-start hook and OpenCode plugin to
  read `AEGIS_TDD_MODE` or `tdd_mode` and inject a compact TDD mode boundary
  line without expanding the `using-aegis` hot path.

### Workflow Quality Coverage

- Updated `test-driven-development` so strict RED / GREEN / REFACTOR is tied
  to `TDD Route: strict`, not forced onto every tiny edit.
- Updated `using-aegis` and its discipline reference to route low-complexity
  implementation through `TDD Route + verification` while keeping the hot path
  under the context budget.
- Added workflow-quality samples and e2e checks for `auto` small-task light
  verification, `auto` risky-code strict TDD, and `off` no-automatic-TDD
  behavior.
- Preserved the method-pack boundary: TDD Mode is advisory workflow discipline
  only and does not add authoritative `GateDecision`, `PolicySnapshot`, or
  completion authority.

### Verification

- `bash scripts/bump-version.sh 1.7.0`
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/activation-mode-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `python tests/helpers/test_workspace_text_write_compat.py`
- `git diff --check`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.6.6 (2026-05-25)

### README And Install Guidance

- Streamlined the English and Chinese root READMEs into compact user-facing
  entry points that emphasize Aegis as a baseline-first, evidence-driven
  method-pack upgrade for AI coding agents.
- Replaced separate minimal install and update prompts with a single
  install-or-update prompt that asks the agent to detect the current host,
  install or update Aegis, reload when needed, and verify from the installed
  method-pack root.
- Moved optional lite global rules into dedicated English and Chinese files so
  the root README stays focused on the information users need before trying
  Aegis.

### Host Compatibility

- Added structural host guidance for OpenClaw and Hermes Agent, including
  individual `SKILL.md` skill-directory install paths, update guidance, doctor
  verification, activation-mode caveats, and authority-boundary reminders.
- Updated the compatibility matrix, known limitations, release checklist,
  prompt-hygiene boundary, current docs index, and README host lists to include
  OpenClaw and Hermes Agent without claiming release-level fresh host smoke.
- Added `popular-agent-host-boundary-check.sh` and wired it into the Layer 1
  fast check to guard these host boundaries.

### Complexity And Repair Discipline

- Expanded complexity governance from a completion-only delta into a
  three-stage advisory flow: `Plan-Time Complexity Check`,
  `Pre-Edit Complexity Check`, and completion-time
  `Complexity Governance Suggestion`.
- Updated `brainstorming`, `writing-plans`, `test-driven-development`,
  `systematic-debugging`, `executing-plans`, and
  `verification-before-completion` so agents can choose safer owner/file
  boundaries before code edits and report useful follow-up recommendations
  after the diff exists.
- Tightened `Minimal Necessary Change` into `Minimal Sufficient Stable Repair`:
  the smallest acceptable repair is the smallest sufficient fix at the correct
  owner and abstraction layer, not the smallest textual diff.
- Added a `Minimality Check` for fallback, guard, adapter, special-case, or
  duplicate-owner repairs so local patches remain bounded mitigations with
  retention reasons and retirement triggers.

### Workflow Quality Coverage

- Added representative workflow-quality samples for plan-time complexity,
  pre-edit complexity, completion-time governance suggestions, and minimal
  sufficient repair.
- Extended e2e checks for workflow-quality contracts, first-principles repair
  classification, debugging patch-shape gates, install verification policy,
  activation-mode host caveats, and goal-framing host documentation coverage.
- Preserved the method-pack boundary: all new checks are advisory workflow
  discipline and do not grant authoritative `GateDecision`, `PolicySnapshot`,
  publish approval, or completion authority.

### Verification

- `bash scripts/bump-version.sh 1.6.6`
- `bash scripts/bump-version.sh --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/debugging-patch-shape-gate-check.sh`
- `bash tests/e2e/first-principles-review-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.6.0 (2026-05-25)

### Strong-Opinion Review Lenses

- Added `Strong-Opinion Review Lenses` to the workflow quality and process
  baselines so high-value workflows can catch weak direction earlier without
  becoming persona commands, approval gates, or runtime authority.
- Added a `Product Risk Lens` to `brainstorming` for value, non-goals,
  trade-offs, and decision-needed clarity before implementation.
- Added a `Plan Pressure Test` to `writing-plans` for owner / contract /
  retirement risk, verification scope, and task executability before task
  decomposition.

### Review, Readiness, And Memory Closure

- Updated `requesting-code-review` and the canonical reviewer template with a
  `Findings First` lens that prioritizes bugs first, risk first, tests first.
- Added a `Readiness Summary` to `verification-before-completion` for release,
  merge, and handoff checks covering tests, docs, version, host compatibility,
  uncovered scope, and residual risk.
- Added a `Retro / Memory Filter` to `recording-architecture-decisions` so
  executed durable decisions can become ADR or baseline memory while unexecuted
  ideas stay out of accepted architecture memory.

### Workflow Quality Coverage

- Added six representative workflow-quality samples covering product risk,
  plan pressure, findings-first review, release readiness, retro memory
  filtering, and fast-path no-persona behavior.
- Extended `workflow-quality-check.sh` to lock the new lenses, compact output
  contracts, and boundary rules across the owning skills.
- Preserved the method-pack boundary: these lenses are advisory workflow
  structures only and do not add merge approval, publish authorization,
  authoritative `GateDecision`, or completion authority.

### Verification

- `bash scripts/bump-version.sh 1.6.0`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/artifact-schema-check.sh`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `python tests/helpers/test_parse_codex_skills.py`
- `git diff --check`

## v1.5.7 (2026-05-24)

### Method-Pack Root Doctor Commands

- Hardened install and update guidance so agents run `aegis-doctor.py` from
  the installed Aegis method-pack root instead of the target project directory.
- Updated root, host-specific, hidden install, compatibility, known-limitation,
  and trigger-health docs with `cd <aegis-method-pack-root>` anchored command
  shapes.
- Extended install verification guardrails so future docs must keep the doctor
  command rooted at the method-pack install location.

### Activation Mode CLI

- Added `python scripts/aegis-doctor.py activation-mode explicit` and
  `python scripts/aegis-doctor.py activation-mode auto` as concise commands for
  switching Aegis automatic bootstrap behavior through the user-local config.
- Kept the boundary explicit: the command writes Aegis config and requires a
  restart, reload, or new host session; it is not an authoritative runtime
  decision or a guaranteed same-session slash command for every host.
- Updated activation mode docs for Codex, OpenCode, Claude Code, CodeBuddy,
  DeepSeek-TUI, Trae, Cursor, Windsurf, and Antigravity surfaces.

### Doctor Usability

- Fixed `aegis-doctor.py helper-path` text output so it no longer crashes when
  run without `--json`.
- Preserved an existing `activation_mode` value when `--write-config` refreshes
  method-pack and workspace-helper paths, avoiding accidental resets from
  `explicit` back to `auto`.

### Verification

- `bash scripts/bump-version.sh 1.5.7`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/activation-mode-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `bash tests/e2e/workspace-helper-resolution-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `python tests/helpers/test_parse_codex_skills.py`
- `python tests/helpers/test_workspace_text_write_compat.py`
- `git diff --check`

## v1.5.6 (2026-05-24)

### Diagnostic Stop Transparency

- Added a `Layer Stop Card` to `systematic-debugging` for cases where the
  diagnostic stop layer affects the fix boundary, contract owner, spec/product
  decision, or user correction path.
- The card makes the current stop layer, checked path, evidence for stop,
  excluded layers, falsifier, user intervention point, and next action explicit.
- Kept the card advisory inside the `Aegis Method Pack (runtime-ready)`
  boundary. It does not grant `GateDecision`, `PolicySnapshot`, or completion
  authority.

### Workflow Quality Samples

- Added five workflow-quality samples covering local L3 root cause, L5
  cross-system contract mismatch, L7 spec gap, fast-path no-card behavior, and
  user falsifier correction from an initial L7-style diagnosis back to L5.
- Extended the workflow-quality e2e check so future changes must keep the card
  structured, falsifiable, user-interruptible, and absent from ordinary
  fast-path explanations.

### Verification

- `bash scripts/bump-version.sh 1.5.6`
- `bash scripts/bump-version.sh --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/trigger-health-check.sh`
- `bash tests/e2e/debugging-patch-shape-gate-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`
- `git diff --check`

## v1.5.5 (2026-05-23)

### Retired Browser Visual Companion

- Removed the inherited browser-based visual companion from the `brainstorming`
  workflow. Aegis no longer offers to open a local browser URL for mockups,
  diagrams, or visual option selection during brainstorming.
- Deleted the companion guide, local server scripts, frame/helper assets, and
  `tests/brainstorm-server/` lifecycle/protocol suite.
- Kept brainstorming focused on method-pack design discipline: context intake,
  clarifying questions, options, design/spec approval, and handoff to
  `writing-plans`.

### Maintenance Guardrails

- Removed the retired `brainstorm-server` version-audit exclusion and updated
  the Codex plugin sync comment so maintenance scripts no longer refer to the
  deleted companion surface.
- Added a workflow-quality regression check that prevents `brainstorming` from
  reintroducing browser visual companion prompts.

### Verification

- `bash scripts/bump-version.sh 1.5.5`
- `bash scripts/bump-version.sh --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/antigravity-host-boundary-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile none`
- `bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `git diff --check`

## v1.5.4 (2026-05-23)

### Antigravity Host Targets

- Added Google Antigravity as a documented Aegis host target across three
  structural surfaces: `Antigravity CLI`, `Antigravity IDE`, and
  `Antigravity App`.
- Added `docs/README.antigravity.md` with install guidance, shape-specific
  notes, verification expectations, and official reference links.
- Added `skills/using-aegis/references/antigravity-tools.md` so Aegis skills can
  map file, shell, search, skill, subagent, and web-tool references onto
  Antigravity host equivalents.

### Gemini CLI Transition Boundary

- Kept Gemini CLI as a transitional compatibility surface instead of retiring
  it in this release.
- Documented Google's `2026-05-19` transition announcement, the `2026-06-18`
  consumer service-stop boundary, and the enterprise / paid API key caveats.
- Preserved `GEMINI.md`, `gemini-extension.json`, and the Gemini tool mapping
  while Antigravity CLI / IDE / App support matures.

### Host Compatibility Guardrails

- Updated the host compatibility matrix, known limitations, release checklist,
  prompt hygiene boundary, README files, and skill references for Antigravity
  support.
- Added `tests/e2e/antigravity-host-boundary-check.sh` and wired it into the
  Layer 1 fast check.
- The new guardrail records Antigravity as structural support only, captures
  Antigravity CLI `1.0.1` plugin discovery evidence, and prevents wording that
  marks Gemini CLI as retired or retiring.

### Verification

- `bash scripts/bump-version.sh 1.5.4`
- `bash scripts/bump-version.sh --check`
- `bash tests/e2e/antigravity-host-boundary-check.sh`
- `bash tests/e2e/install-verification-policy-check.sh`
- `python tests/helpers/test_parse_codex_skills.py`
- `git diff --check`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

## v1.5.3 (2026-05-21)

### Recording Architecture Decisions

- Added `recording-architecture-decisions` as the dedicated ADR lifecycle
  skill for direct ADR, architecture decision record, decision log, and
  baseline sync closure requests.
- The new skill runs the ADR creation gate, chooses create / amend /
  supersede / skip, selects the owner surface, and closes Baseline Sync before
  any ADR or baseline writeback.
- Kept the boundary explicit: ADR handling remains advisory method-pack
  discipline and does not become completion authority, an authoritative
  `GateDecision`, or a `PolicySnapshot`.

### Baseline Sync Closure

- Updated ADR Auto Backfill guidance so create, amend, supersede, needed, or
  unknown baseline sync outcomes route through `recording-architecture-decisions`.
- Extended `verification-before-completion` and `requesting-code-review` so
  completion and review flows flag missing ADR lifecycle handoff when durable
  architecture decisions or baseline sync closure are in scope.
- Documented the compact output contract in the workflow quality baseline:
  Decision Candidate, ADR Gate, ADR Action, Owner Surface, Baseline Sync, and
  Boundary.

### Trigger And Release Coverage

- Added `recording-architecture-decisions` to doctor key skill detection and
  skill-triggering / explicit-skill request coverage.
- Expanded workflow quality fixtures and checks with direct ADR lifecycle and
  ADR-skip samples, including no-forced-ADR and no-forced-baseline-writeback
  guardrails.
- Bumped public package and host distribution manifests to `1.5.3`.

### Verification

- `bash scripts/bump-version.sh 1.5.3`
- `bash scripts/bump-version.sh --check`
- `git diff --check`
- `python tests/helpers/test_parse_codex_skills.py`
- `bash tests/e2e/workflow-quality-check.sh`
- `bash tests/e2e/context-budget-check.sh`
- `bash tests/e2e/boundary-compliance-check.sh`
- `bash tests/e2e/governance-completion-contract-check.sh`
- `bash tests/e2e/layer1-fast-check.sh --host-profile none`
- `bash tests/e2e/run-all.sh --full --host-profile fast`

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
  the user-visible docs tree and narrowed stale upstream-name references away
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

## Legacy Upstream Lineage Notes

Current Aegis release notes begin at `v1.0.0` and track the independent Aegis
Method Pack release line. Earlier upstream release history is intentionally not
copied into this file so current Aegis releases are not mixed with legacy
upstream implementation names, paths, commands, or install instructions.

For lineage and attribution, see the relationship notes in `README.md` and
`README.en.md`.
