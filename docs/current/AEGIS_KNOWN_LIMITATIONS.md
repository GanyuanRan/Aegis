# Aegis Known Limitations

Status: `Reviewed`

## 1. Document Scope

This document records the current known limitations, compatibility fallbacks, retention reasons, and retirement triggers of the `Aegis Method Pack`.

It only records limitations supported by current fresh evidence and does not speculate about the future.

---

## 2. Current Known Limitations

### 2.1 Current Repository Is Not a Complete Platform

**Retained Item**
- The layered boundary between `Method Pack` and future `Host Adapters + Runtime Core`

**Retention Reason**
- The current repository's formal scope is `Aegis Method Pack (runtime-ready)`, not a full platform

**Observation Metric**
- Whether current docs still constrain outputs to `draft / hint / projection`

**Retirement Trigger**
- Only when a future complete platform is independently unfolded in a new approved plan does this enter the next layer; this is not about "deleting this limitation"

---

### 2.2 Real-Environment Regression Is Deferred

**Retained Item**
- Multi-host release-level fresh install regression
- Real team task live sample verification

**Retention Reason**
- The current priority is method-pack strengthening and open-source preparation, not immediately declaring daily production rollout

**Observation Metric**
- Whether the release checklist and host compatibility snapshot still clearly distinguish method-pack readiness from production rollout readiness

**Retirement Trigger**
- When the user explicitly requests entry into production rollout preparation

---

### 2.3 OpenCode Config Fallback Is Still Retained

**Retained Item**
- OpenCode `config.skills.paths` compatibility fallback

**Retention Reason**
- The current canonical chain has already switched to the host's officially supported global skills path, but cross-version evidence that the fallback has zero compatibility value is still lacking

**Observation Metric**
- `bash tests/opencode/run-tests.sh --integration`
- Real fresh install verification

**Retirement Trigger**
- When the target OpenCode version set has proven that the native global skills path is sufficiently stable

---

### 2.4 Current Host Snapshot Is Not a Full-Host Release Verdict

**Retained Item**
- Currently only `Codex` and `OpenCode` have fresh-evidence-driven mainline verdicts

**Retention Reason**
- Other hosts are currently outside the verification scope of this slice

**Observation Metric**
- Whether `AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md` still clearly distinguishes "has fresh evidence" from "current verdict not yet formed"

**Retirement Trigger**
- When other hosts enter a separate approved slice and complete fresh closeout

---

### 2.5 Codex Smoke Under Git Bash: Latency and Stability Require Separate Observation

**Retained Item**
- Codex representative smoke under Git Bash / MSYS2 environment

**Retention Reason**
- It has been confirmed that the working-dir / cmd bridge issues under Git Bash can be converged, but representative Codex smoke may still exhibit:
  - explicit skill requests may pass but take longer than expected
  - naive prompt smoke is unstable within the current timeout window

**Observation Metric**
- `env AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh brainstorming ...`
- `env AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming ...`
- Bridge and parser behavior of `tests/helpers/codex-cli.sh`

**Retirement Trigger**
- When representative Codex smoke under Git Bash passes stably within the current runner timeout window

---

### 2.6 INDEX.md Append Dependency on Workflow Steps

**Retained Item**
- The completeness of `docs/aegis/INDEX.md` still depends on workflows using the shared workspace helper or explicitly performing the append operation

**Retention Reason**
- `scripts/aegis-workspace.py` now provides lifecycle commands (`new-work`, `add-checkpoint`, `add-evidence`, `add-drift-check`, `bundle`) and `append-index`, and `check` detects unindexed markdown. A workflow that writes to `docs/aegis/` must still call the helper or manually append the entry

**Observation Metric**
- `bash tests/e2e/aegis-workspace-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- During code review of new skills, check whether workspace helper usage or equivalent INDEX.md append logic is included

**Retirement Trigger**
- When all skills that write to docs/aegis/ invoke the shared workspace helper and verification-before-completion checks helper output for touched workspaces in real target-project usage

---

### 2.7 Lazy Workspace Support Depends on Correct Triggering

**Retained Item**
- Workspace records are created lazily, not for every Aegis-assisted turn

**Retention Reason**
- Normal Q&A, simple explanation, version/status checks, and low-risk small edits should not create project files. Baseline/spec/plan/work records are written only when the workflow needs persistent project evidence

**Observation Metric**
- `bash tests/e2e/project-bootstrap-policy-check.sh`
- Actual hit rate of mid-stream escalation into baseline/spec/plan/work records

**Retirement Trigger**
- When a future runtime core can observe task state and trigger workspace support without relying on method-layer judgment

---

### 2.8 Project Baseline Bootstrap Depends on Sufficient Project Content

**Retained Item**
- Initial project baseline semantic quality depends on bounded repo scan results and sufficient project content

**Retention Reason**
- Aegis can index files, read key docs, infer owners/contracts, and create a structured baseline, but sparse repos or placeholder-only projects do not contain enough evidence for a useful baseline

**Observation Metric**
- Whether agents skip empty baselines when content is too sparse
- Whether generated baseline snapshots cite concrete files and commands instead of generic guesses

**Retirement Trigger**
- When real target-project usage shows the bootstrap consistently creates useful baseline snapshots or correctly declines sparse projects

---

### 2.9 BASELINE-GOVERNANCE.md Template Depends on Correct Agent Execution

**Retained Item**
- The content quality of BASELINE-GOVERNANCE.md still depends on the agent or workflow choosing the correct target project and preserving project-specific review

**Retention Reason**
- `<aegis-workspace-helper> init` now writes the standard baseline governance template and `check` verifies required headings and boundary phrases, but it cannot judge whether a target project's later edits are semantically sufficient

**Observation Metric**
- `bash tests/e2e/aegis-workspace-check.sh`
- Field fill rate and semantic usefulness in actually created BASELINE-GOVERNANCE.md files

**Retirement Trigger**
- When verification-before-completion consistently runs the helper check for touched workspaces and real target-project usage shows the generated template is semantically sufficient

---

### 2.10 Copy-Only or Skills-Only Installs Do Not Prove Complete Workspace Support

**Retained Item**
- Copy-only / skills-only install paths can prove skill discovery but may not prove complete project workspace support

**Retention Reason**
- Some hosts support only copying `skills/` into a native discovery directory. That keeps workflows usable, but the repo-local workspace support scripts may not be discoverable unless the method-pack root remains available or is configured

**Observation Metric**
- `python scripts/aegis-doctor.py --write-config --json`
- JSON readback includes `"workspaceSupport": "available"` and
  `"configStatus": "configured"`
- Host docs distinguish recommended complete install from compatibility fallback

**Retirement Trigger**
- When each supported host has a verified install path that preserves both skill discovery and project workspace support

---

### 2.11 Architecture Review: 7 Dimensions Partially Depend on Agent Qualitative Judgment

**Retained Item**
- Some dimensions among the 7 (especially Entropy flow, Cascade proliferation) depend on agent qualitative judgment and have no quantitative measurement tools

**Retention Reason**
- Quantitative architecture measurement requires specialized static analysis toolchains, currently beyond the method-pack scope

**Observation Metric**
- Consistency of qualitative judgments in actual architecture reviews; if contentious judgments appear frequently, quantitative baselines need to be introduced

**Retirement Trigger**
- When integrable quantitative architecture measurement tools become available

---

### 2.12 Host-Loaded Skill Freshness Depends on Install Chain

**Retained Item**
- A repository-local skill update does not prove the current AI coding host is
  already loading that updated skill content

**Retention Reason**
- Some hosts scan skills at startup, use a copied skills directory, or resolve a
  host-specific discovery path. Aegis can verify the method-pack checkout and
  optional discovery root, but the host may still require restart/reload before
  the updated hot path is active.

**Observation Metric**
- `python scripts/aegis-doctor.py --write-config --json`
- `python scripts/aegis-doctor.py --discovery-root <host-skill-discovery-root>`
- Host-specific restart/reload plus skill discovery smoke where available

**Retirement Trigger**
- When each supported host has a verified install/update path that proves both
  skill discovery and current hot-path content after reload

---

### 2.13 Hot-Path Budget Requires Continuous Guardrails

**Retained Item**
- `using-aegis` must stay a compact router instead of becoming the container for
  every Aegis workflow detail

**Retention Reason**
- Overloading the always-loaded entrypoint increases context pressure and can
  reduce task quality. Detailed rules belong in task-specific skills or
  references, not the hot path.

**Observation Metric**
- `bash tests/e2e/context-budget-check.sh`
- `using-aegis` hot-path character count
- Absence of helper command details and universal design/spec ceremony wording
  in the hot path

**Retirement Trigger**
- This is an ongoing guardrail rather than a defect to delete; future runtime
  support may replace the method-layer budget check with host/runtime telemetry.

---

### 2.14 ADR Auto Backfill Is Baseline-Defined Before Helper Automation

**Retained Item**
- ADR Auto Backfill is currently defined as a method-pack workflow baseline, but
  helper-backed `new-adr`, `amend-adr`, and `supersede-adr` commands are not yet
  implemented

**Retention Reason**
- The workflow boundary must be stable before helper automation is added. The
  current repository already defines how completed work should backfill ADRs and
  when baseline sync is mandatory, but script support and skill wiring still
  need a separate implementation slice

**Observation Metric**
- `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`
- Future helper tests for ADR creation, amendment, supersession, index coverage,
  and baseline sync checks
- Review of `verification-before-completion`, `long-task-continuation`,
  `writing-plans`, and `requesting-code-review` skill wiring

**Retirement Trigger**
- When helper-backed ADR lifecycle commands exist, affected skills invoke ADR
  Auto Backfill at completion time, and e2e tests prove ADR/index/baseline sync
  behavior without granting runtime authority

---

### 2.15 Antigravity Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- Antigravity CLI, Antigravity IDE, and Antigravity App are structural target
  surfaces, not release-level fresh smoke verdicts

**Retention Reason**
- Google positions Antigravity as the successor Google agent platform and
  documents public capabilities such as Skills, MCP, JSON Hooks, plugins,
  slash commands, and subagents. The public Antigravity CLI `1.0.1` changelog
  says plugin discovery for skills and agents from installed plugin directories
  exists, but the stable local install / discovery contract for this Aegis
  method pack still needs current release verification before Aegis can claim
  host closeout.

**Observation Metric**
- `docs/README.antigravity.md`
- `bash tests/e2e/antigravity-host-boundary-check.sh`
- Future Antigravity CLI / IDE / App install smoke that proves skill discovery,
  restart or reload behavior, and `python scripts/aegis-doctor.py
  --write-config --json`

**Retirement Trigger**
- When each Antigravity shape has a verified install/update path that proves
  both skill discovery and project workspace support without turning Aegis into
  an authoritative runtime core

---

### 2.16 Gemini CLI Is a Transitional Compatibility Surface

**Retained Item**
- `GEMINI.md`, `gemini-extension.json`, and the Gemini CLI tool mapping remain
  as transitional compatibility surfaces

**Retention Reason**
- Google announced on `2026-05-19` that consumer Gemini CLI and Gemini Code
  Assist IDE extension usage is transitioning to Antigravity CLI and
  Antigravity 2.0. On `2026-06-18`, requests stop being served for free usage,
  Google AI Pro / Ultra, and Gemini Code Assist for individuals. Enterprise
  Standard / Enterprise, Google Cloud-backed Gemini Code Assist for GitHub, and
  paid Gemini / Gemini Enterprise Agent Platform API key paths remain outside
  that consumer stop boundary. Aegis keeps Gemini CLI support as a transition
  path while Antigravity CLI, Antigravity IDE, and Antigravity App support
  matures.

**Observation Metric**
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/README.antigravity.md`
- Future evidence about whether relevant users have moved to Antigravity and
  whether the transitional Gemini surfaces still provide compatibility value

**Reclassification Trigger**
- When Antigravity install surfaces have their own stable, verified package
  artifacts and maintainers explicitly decide whether Gemini CLI remains
  transitional, becomes legacy-only, or needs a separate retirement proposal in
  a future cleanup

## 3. Default Reading Rule

If a limitation appears simultaneously in README, host docs, or test descriptions, use this document as the current reading entry point.

---

## 4. Architecture Review

The core requirements for current limitation management are:

1. Do not conceal limitations
2. Do not write limitations as permanent defects
3. Do not add fallbacks without retirement plans in order to mask limitations

For the 7-dimension operational definitions and defect/drift judgment criteria for architecture review, see `AEGIS_PROCESS_BASELINE.md` §15-§17.
