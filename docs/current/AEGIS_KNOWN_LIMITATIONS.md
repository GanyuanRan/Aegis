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
- `scripts/aegis-workspace.py append-index` now provides an automated append path and `check` detects unindexed markdown, but a workflow that writes to `docs/aegis/` must still call the helper or manually append the entry

**Observation Metric**
- `bash tests/e2e/aegis-workspace-check.sh`
- During code review of new skills, check whether workspace helper usage or equivalent INDEX.md append logic is included

**Retirement Trigger**
- When all skills that write to docs/aegis/ invoke the shared workspace helper and verification-before-completion checks helper output for touched workspaces

---

### 2.7 Low-Complexity Task Skips Workspace: Gap Window

**Retained Item**
- Low-complexity tasks do not trigger workspace creation; if later upgraded to medium complexity, there is a brief no-workspace window before the using-aegis hot path Rule 2 mid-stream upgrade trigger fires

**Retention Reason**
- The definition of low-complexity tasks itself is "no workspace artifacts needed"; premature creation would produce noise files. The mid-stream upgrade trigger is the current simplest remediation

**Observation Metric**
- The hit frequency of the mid-stream upgrade trigger in actual usage; if hit frequently, the initial complexity classification threshold needs adjustment

**Retirement Trigger**
- When sufficient actual usage data supports a more precise initial complexity determination

---

### 2.8 BASELINE-GOVERNANCE.md Template Depends on Correct Agent Execution

**Retained Item**
- The content quality of BASELINE-GOVERNANCE.md still depends on the agent or workflow choosing the correct target project and preserving project-specific review

**Retention Reason**
- `scripts/aegis-workspace.py init` now writes the standard baseline governance template and `check` verifies required headings and boundary phrases, but it cannot judge whether a target project's later edits are semantically sufficient

**Observation Metric**
- `bash tests/e2e/aegis-workspace-check.sh`
- Field fill rate and semantic usefulness in actually created BASELINE-GOVERNANCE.md files

**Retirement Trigger**
- When verification-before-completion consistently runs the helper check for touched workspaces and real target-project usage shows the generated template is semantically sufficient

---

### 2.9 Architecture Review: 7 Dimensions Partially Depend on Agent Qualitative Judgment

**Retained Item**
- Some dimensions among the 7 (especially Entropy flow, Cascade proliferation) depend on agent qualitative judgment and have no quantitative measurement tools

**Retention Reason**
- Quantitative architecture measurement requires specialized static analysis toolchains, currently beyond the method-pack scope

**Observation Metric**
- Consistency of qualitative judgments in actual architecture reviews; if contentious judgments appear frequently, quantitative baselines need to be introduced

**Retirement Trigger**
- When integrable quantitative architecture measurement tools become available

---

## 3. Default Reading Rule

If a limitation appears simultaneously in README, host docs, or test descriptions, use this document as the current reading entry point.

---

## 4. Architecture Review

The core requirements for current limitation management are:

1. Do not conceal limitations
2. Do not write limitations as permanent defects
3. Do not add fallbacks without retirement plans in order to mask limitations

For the 7-dimension operational definitions and defect/drift judgment criteria for architecture review, see `AEGIS_PROCESS_BASELINE.md` §15-§17.
