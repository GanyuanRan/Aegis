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
- A product-scope decision, recorded in a current doc or ADR, that brings
  production rollout preparation into this repository's scope

---

### 2.3 OpenCode Config Fallback Is Still Retained

**Retained Item**
- OpenCode `config.skills.paths` compatibility fallback

**Retention Reason**
- The current canonical chain has already switched to the host's officially supported global skills path, but cross-version evidence that the fallback has zero compatibility value is still lacking
- When `~/.config/aegis/config.toml` declares `method_pack_root`, the OpenCode
  plugin now treats that configured checkout as the canonical Aegis source and
  generates the OpenCode-visible skills tree from it; the host-visible skills
  directory is still a compatibility view rather than a second editable owner,
  and `config.skills.paths` remains only a fallback exposure layer

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
- Each other host leaves this limitation only through a fresh verdict from the
  [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or through a documentation-only or retirement outcome of the
  [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.5 Codex Smoke Under Git Bash: Latency and Stability Require Separate Observation

**Retained Item**
- Codex representative smoke under Git Bash / MSYS2 environment

**Retention Reason**
- It has been confirmed that the working-dir / cmd bridge issues under Git Bash can be converged, but representative Codex smoke may still exhibit:
  - explicit skill requests may pass but take longer than expected
  - naive prompt smoke is unstable within the current timeout window
  - on some Windows Codex installations, the default workspace sandbox may
    fail before routing when it cannot spawn the configured PowerShell process
    (`CreateProcessAsUserW` access denied); an environment-controlled rerun can
    distinguish that host failure from an Aegis trigger regression

**Observation Metric**
- `env AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh brainstorming ...`
- `env AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh brainstorming ...`
- Bridge and parser behavior of `tests/helpers/codex-cli.sh`
- The trigger parser accepts a skill load only when a successful command result
  reads back matching `name` and `description` frontmatter. Failed reads remain
  negative regression cases rather than load evidence.
- Whether the same smoke reaches skill discovery with and without the failing
  Windows sandbox boundary

**Retirement Trigger**
- When representative Codex smoke under Git Bash passes stably within the
  current runner timeout window and the Windows sandbox can reliably spawn its
  configured shell

---

### 2.6 INDEX.md Append Dependency on Workflow Steps

**Retained Item**
- The completeness of `docs/aegis/INDEX.md` still depends on workflows using the shared workspace helper or explicitly performing the append operation

**Retention Reason**
- `scripts/aegis-workspace.py` now provides lifecycle commands (`new-work`, `add-checkpoint`, `add-attempt`, `add-evidence`, `add-drift-check`, `bundle`) and `append-index`, and `check` detects unindexed markdown. A workflow that writes to `docs/aegis/` must still call the helper or manually append the entry

**Observation Metric**
- `bash tests/e2e/aegis-workspace-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- During code review of new skills, check whether workspace helper usage or equivalent INDEX.md append logic is included

**Retirement Trigger**
- When `tests/e2e/workspace-helper-wiring-check.sh` covers every skill that
  writes `docs/aegis/`, and a frozen workflow-quality or benchmark case shows
  verification-before-completion running the helper check for touched
  workspaces

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
- When a frozen benchmark or workflow-quality case set with both sparse and
  content-rich fixture projects shows the bootstrap creating snapshots that
  cite concrete files and commands, and declining the sparse projects

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
- When a frozen workflow-quality or benchmark case shows
  verification-before-completion running the helper check for touched
  workspaces. Whether a project's later edits are semantically sufficient
  remains a permanent, project-owned boundary.

---

### 2.10 Copy-Only or Skills-Only Installs Do Not Prove Complete Workspace Support

**Retained Item**
- Copy-only / skills-only install paths can prove skill discovery but may not prove complete project workspace support

**Retention Reason**
- Some hosts support only copying `skills/` into a native discovery directory. That keeps workflows usable, but the repo-local workspace support scripts may not be discoverable unless the method-pack root remains available or is configured

**Observation Metric**
- `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`
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
- Permanent while the seven dimensions remain review prompts rather than
  measurements. Revisit when a zero-dependency measurement for a specific
  dimension is proposed through the Minimality Reference Existence Check.

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
- `cd <aegis-method-pack-root> && python scripts/aegis-update.py status --json`
- `cd <aegis-method-pack-root> && python scripts/aegis-update.py update --host <host> --json`
- `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`
- `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --discovery-root <host-skill-discovery-root>`
- Host-specific restart/reload plus skill discovery smoke where available

For copy-based and direct-child link compatibility exposures, the current
updater can refresh the direct-child skill directories from the canonical
`skills/` tree, prune stale Aegis-managed exposure entries, and run the same
discovery-root structural readback through `aegis-doctor.py`. This remains
method-pack-side structural verification only; host restart/reload may still be
required before the running host loads the refreshed content.

For `copy-skills`, the installation registry records copied-file digests and
their source/discovery-root/name-prefix scope. Only unchanged files recorded
in that scope may be replaced or retired; a directory name, prefix, or
`SKILL.md` alone is not ownership evidence. Unknown files and local changes
are preserved. A conflicting destination stops synchronization with the path
and recovery guidance before planned writes or retirement. Use a separate
discovery root or reconcile the conflicting file before retrying.

Legacy copies without a registry inventory can adopt files identical to the
current source. Differing same-name files require reconciliation; unidentified
stale copies remain until ownership can be established. Re-registration keeps
the inventory only for the same scope. Successful copy synchronization saves
its inventory independently of subsequent doctor verification, so a failed
doctor does not erase ownership evidence. This is local copy provenance,
not host-load proof or runtime authority.

Copied source names must be unambiguous under Unicode normalization and case
folding so one distribution works on case-insensitive discovery volumes too.
This portable-name check only rejects source collisions; it never grants
ownership of a destination. On platforms whose path normalization does not
match the volume's case behavior, a case-only rename combined with a content
change may require reconciliation. Back up and move the conflicting file
outside the discovery root, or choose a separate discovery root, then retry. Do not
infer ownership merely from a matching case-folded name or inode.

When `~/.config/aegis/config.toml` declares `method_pack_root`, the shared
updater now prefers that canonical root for new host registration defaults.
Multiple registered hosts may therefore share one method-pack checkout while
keeping different discovery roots, discovery shapes, reload hints, and
host-managed adapter behaviors.

When a host-scoped updater registration needs both transport and visibility
semantics, keep them separate:

- `syncMode` describes how Aegis reaches the host surface
- `discoveryShape` describes what the host should see there, such as
  `umbrella-root` or `direct-child`
- `discoveryNamePrefix` describes an optional host-visible direct-child
  directory name prefix, such as Copilot's repository skill view using
  `aegis-<skill-name>/SKILL.md`

Do not overload `syncMode` alone to carry transport, shape, and naming
semantics.

The update registry is host-scoped. Plain `aegis:update` should update the
current host installation only; all-host updates require an explicit `--all`
request.

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

### 2.14 ADR Auto Backfill Helper Exists, But Baseline Sync Still Depends On Workflow Judgment

**Retained Item**
- Helper-backed `new-adr`, `amend-adr`, and `supersede-adr` commands now exist,
  but they only scaffold target-project `docs/aegis/adr/` records and validate
  structure
- The semantic decision to create, amend, supersede, or skip an ADR, plus the
  truth of baseline sync closure, still depends on workflow judgment against the
  current authority docs

**Retention Reason**
- The repository now has helper-backed ADR lifecycle commands, owner-surface
  skill wiring, and e2e coverage, but those commands intentionally stop at
  structural method-pack support. `recording-architecture-decisions` and
  `verification-before-completion` still own ADR trigger judgment, owner-surface
  choice, and baseline sync closure

**Observation Metric**
- `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`
- `bash tests/e2e/aegis-workspace-check.sh`
- `bash tests/e2e/workspace-helper-wiring-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- Review of actual completion notes for explicit ADR Backfill and Baseline Sync
  closure when durable architecture surfaces changed

**Retirement Trigger**
- When a frozen workflow-quality or benchmark case set shows helper-backed ADR
  writeback and baseline sync closure completing without stale docs, skipped
  routing, or authority confusion

---

### 2.15 Antigravity CLI Structural Install Is Verified; Live Host Validation Is Pending

**Retained Item**
- `Antigravity CLI` is the active closeout target for the current Google-host
  slice: installation and structural discovery are verified, while live Aegis
  skill loading, task routing, and session refresh remain pending
- `Antigravity IDE` and `Antigravity App` remain structural targets:
  not release-level fresh smoke verdicts

**Retention Reason**
- Public Antigravity CLI changelogs document plugin discovery for skills and agents
  from installed plugin directories. The 2026-10-17 maintainer readback
  (Windows, `agy 1.4.0`) verified install, the plugin lifecycle, and
  updater-managed direct-child exposure with doctor
  `discoveryShapeStatus: current`; details are in the
  [Antigravity guide](../README.antigravity.md).
- Local signed-in sessions were rejected by the host's account eligibility
  check before any model turn. That blocker is environment-bound, not a
  method-pack defect.

**Observation Metric**
- `bash tests/e2e/antigravity-host-boundary-check.sh` and
  `bash tests/antigravity/run-tests.sh` (`--integration` is environment-bound)
- A runnable CLI session that records skill discovery, loading, representative
  routing, restart/reload behavior, and
  `cd <aegis-method-pack-root> && python scripts/aegis-doctor.py --write-config --json`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)
- `Antigravity IDE` and `Antigravity App` need their own evidence rather than
  CLI proof

---

### 2.16 Gemini CLI Support Is Retired

**Retired Item**
- The root `GEMINI.md`, `gemini-extension.json`, and Gemini-specific tool
  mapping were removed from the supported distribution surface; new
  Google-host work targets Antigravity

**Retirement Reason**
- Google moved consumer Gemini CLI usage to Antigravity (announced
  `2026-05-19`; consumer requests stopped on `2026-06-18`). The exact consumer
  and enterprise boundary is recorded in the matrix row `Gemini CLI`.

**Compatibility Impact**
- Enterprise, Google Cloud, or paid API-key Gemini CLI users may still run
  Gemini CLI, but Aegis no longer publishes or verifies an install path for it.
  This retirement is not an Antigravity closeout verdict.

**Verification**
- `bash tests/e2e/antigravity-host-boundary-check.sh`; repository scans show no
  current Gemini adapter, manifest, or tool-map owner

---

### 2.17 OpenClaw and Hermes Agent Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- OpenClaw and Hermes Agent are structural host targets:
  not release-level fresh smoke verdicts (matrix rows `OpenClaw`, `Hermes Agent`)

**Retention Reason**
- `openclaw skills install` installs individual skill directories, not the
  whole multi-skill pack. Hermes Agent supports GitHub path installs such as
  `hermes skills install owner/repo/skills/my-workflow`. Install shapes are in
  the [OpenClaw](../README.openclaw.md) and
  [Hermes Agent](../README.hermes-agent.md) guides.

**Observation Metric**
- `bash tests/e2e/popular-agent-host-boundary-check.sh`

**Retirement Trigger**
- For each host separately: a fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a
  documentation-only or retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule).
  The limitation stays for whichever host has not met one.

---

### 2.18 Pi CLI Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- Pi CLI is a structural host target; its current evidence is structural:
  not release-level fresh smoke verdicts (matrix row `Pi CLI`)

**Retention Reason**
- Pi discovers Agent Skills from `~/.pi/agent/skills/`, `~/.agents/skills/`,
  `.pi/skills/` and package `skills/` entries. Aegis exposes `./skills` through
  the root `package.json` for `pi install git:github.com/GanyuanRan/Aegis`;
  details are in the [Pi guide](../README.pi.md).

**Observation Metric**
- `bash tests/e2e/pi-host-boundary-check.sh` and
  `bash tests/pi-omp-extensions/test-shared-core.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.19 OMP Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- OMP (Oh My Pi) is a structural host target; its current evidence is
  structural: not release-level fresh smoke verdicts (matrix row `OMP (Oh My Pi)`)

**Retention Reason**
- OMP keeps Pi's Agent Skills discovery (its `agents` provider reads
  `~/.agents/skills/`), honors `alwaysApply: true` for `using-aegis`, and loads
  the shared Pi/OMP extension bundle from `~/.omp/agent/extensions/`; details
  are in the [OMP guide](../README.omp.md).

**Observation Metric**
- `bash tests/e2e/omp-host-boundary-check.sh` and
  `bash tests/pi-omp-extensions/test-shared-core.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.20 CC GUI Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- CC GUI (JetBrains IDEA) is a structural host target; its current evidence is
  structural: not release-level fresh smoke verdicts (matrix row `CC GUI (JetBrains IDEA)`)
- Its OpenAI/GPT provider path discovers only direct-child skills, so Aegis
  exposes `~/.agents/skills/<skill-name>/SKILL.md` entries as a generated view
  of the canonical `skills/` tree. Selecting a GPT model profile does not change
  this discovery shape.

**Retention Reason**
- Entries such as `Tool: exec_command` are host adapter event normalization
  concerns owned by CC GUI. Aegis can reduce tool fan-out, but it does not own
  the IDE's event rendering; details are in the [CC GUI guide](../README.cc-gui.md).

**Observation Metric**
- `bash tests/e2e/cc-gui-host-boundary-check.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)
- IDE rendering claims additionally need direct CC GUI evidence

---

### 2.21 GitHub Copilot Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- GitHub Copilot is a structural host target, not a release-level fresh smoke verdict
  (matrix row `GitHub Copilot`)

**Retention Reason**
- Repository skills (`.github/skills/`), custom instructions, hooks and
  `AGENTS.md` are enough for method-pack exposure; see the
  [Copilot guide](../README.copilot.md).

**Observation Metric**
- `bash tests/e2e/copilot-qoder-host-boundary-check.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.22 Qoder Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- Qoder is a structural host target, not a release-level fresh smoke verdict
  (matrix row `Qoder`)

**Retention Reason**
- Native skills (`~/.qoder/skills/`, `.qoder/skills/`), project rules and
  `AGENTS.md` are enough for method-pack exposure; see the
  [Qoder guide](../README.qoder.md).

**Observation Metric**
- `bash tests/e2e/copilot-qoder-host-boundary-check.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.23 Kimi Code CLI Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- Kimi Code CLI is a structural host target, not a release-level fresh smoke verdict
  (matrix row `Kimi Code CLI`)
- The default automatic path is the Kimi-managed plugin with
  `sessionStart.skill = using-aegis`; deterministic tests verify its manifest,
  doctor profile, and duplicate-exposure rejection, not live model routing
- Updater-managed `$KIMI_CODE_HOME/skills/` direct-child exposure is an explicit
  compatibility installation, and the generic `~/.agents/skills/` scan root is
  only an official fallback; neither is the default path

**Retention Reason**
- Kimi's plugin contract provides a stable session-start owner that plain skill
  discovery lacks. Compatibility installs expose individual
  `<skill-name>/SKILL.md` directories instead of relying on the Codex umbrella symlink;
  details are in the [Kimi Code guide](../README.kimi-code.md).

**Observation Metric**
- `bash tests/kimi-code/run-tests.sh`; its `--integration` mode and
  `run-live-smoke.sh` are environment-bound
- `python scripts/aegis-doctor.py --json --host-profile kimi-code-auto`

**Retirement Trigger**
- A fresh release-level Kimi run proves plugin install/update, new and resumed
  session routing, false-positive control, and project workspace support

---

### 2.24 ZCode Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- ZCode is a structural host target; its current evidence is structural:
  not release-level fresh smoke verdicts (matrix row `ZCode`)

**Retention Reason**
- ZCode scans depth-1 `~/.agents/skills/<skill-name>/SKILL.md` directories, so
  the umbrella `~/.agents/skills/aegis/` layout is invisible to it; use the
  updater-managed direct-child install. Its plugin marketplace reads
  `.claude-plugin/marketplace.json`, so the existing Claude Code skeleton
  applies unchanged; details are in the [ZCode guide](../README.zcode.md).

**Observation Metric**
- `bash tests/e2e/zcode-host-boundary-check.sh`

**Retirement Trigger**
- A fresh verdict through the [Host Closeout Recipe](AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md#host-closeout-recipe), or a documentation-only or
  retirement outcome of the [structural target review](AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md#35-structural-target-review-rule)

---

### 2.25 Grok Build Structural Support Is Not Yet Fresh Host Closeout

**Retained Item**
- Grok Build is a structural host target, not a release-level fresh smoke verdict
  (matrix row `Grok Build`)
- Grok's native skills, extra `[skills] paths`, shared Agent Skills, and
  Claude-compatible plugin scanners can expose duplicate Aegis skill names with
  different freshness; enable one exposure route

**Retention Reason**
- Aegis recommends updater-managed direct-child exposure under the Grok native
  user root (`$GROK_HOME/skills/`). Local `grok inspect --json` enumeration is
  not a clean-install, reload, trigger, and update closeout; details are in
  the [Grok Build guide](../README.grok-build.md).

**Observation Metric**
- `bash tests/e2e/grok-build-host-boundary-check.sh` and
  `python tests/helpers/test_aegis_update.py -k grok`
- `grok inspect --json` reports one canonical source for each Aegis skill name

**Retirement Trigger**
- A clean-install fresh verdict proves discovery, live triggering after
  restart, no duplicate exposure, and project workspace support

---

### 2.26 DeepSeek Harness Bundle Support Is Not Yet Fresh Host Closeout

**Retained Item**
- The official DeepSeek Harness (`deepseek-ai/deepseek-harness`) is a structural
  host target, not a release-level fresh smoke verdict (matrix row
  `DeepSeek Harness`); it and the community DeepSeek-TUI remain separate host
  surfaces
- Native runtime-context delivery is covered by deterministic tests and by
  published DSH `0.2.2-rc.3` loop tests with scripted model responses; live
  model routing in a fresh installed profile, the Desktop application, macOS,
  and UI resume/clear/compaction remain unverified
- Peer ranges use `>=0.1.0-rc.6` as an installation admission floor: future
  versions are admitted by version number, not certified in advance, and the
  three peers stay optional so other hosts gain no DSH runtime dependency
- Marketplace source selection is unverified. A third-party npm package
  (`aegis-method-pack@2.9.2`, published by an account the Aegis team does not
  operate) still carries stale peers. Aegis publishes the official scoped
  package `@ganyuan_ran/aegis`, verified by registry readback on 2026-11-14,
  and Plugin Hub `v2.0.0` removed its Git-source install channel. History:
  issues [#80](https://github.com/GanyuanRan/Aegis/issues/80),
  [#81](https://github.com/GanyuanRan/Aegis/issues/81), and
  [#83](https://github.com/GanyuanRan/Aegis/issues/83), and Plugin Hub
  [#120](https://github.com/dshplugin/dsh-plugin-hub/issues/120),
  [#130](https://github.com/dshplugin/dsh-plugin-hub/issues/130), and
  [#178](https://github.com/dshplugin/dsh-plugin-hub/issues/178)
- The Electron-owned `desktop` profile is managed only through the
  application's plugin manager; terminal examples apply to CLI-managed profiles
- The updater-managed direct-child install remains an explicit compatibility
  path rather than the default DSH installation
- The bootstrap skips subagents and does not install a hard pre-tool guard:
  legitimate `Route: fast-path` decisions are model-facing and are not reliable
  enough to support hard denial without false positives. The adapter does not
  duplicate skill bodies or add runtime authority.

**Retention Reason**
- The default DSH path is a thin package bundle declared through
  `dsh.bundle.patch` that mounts the canonical skills through the native
  provider and contributes the router through `systemPrompt.context`
  ([issue #102](https://github.com/GanyuanRan/Aegis/issues/102)). Host
  projection owns admission and deduplication; presets that suppress runtime
  context remain in control, and explicit native skill loading stays available.
- [Issue #75](https://github.com/GanyuanRan/Aegis/issues/75) showed that
  structural checks can pass while auto-entry is inactive. That lifecycle
  delivery path has since been replaced, so its contributor readback does not
  verify the native context path.
- Direct-child exposure remains necessary when the developer-preview bundle API
  is unavailable, local policy forbids third-party profile plugins, or `pnpm`
  cannot be provided to the DSH plugin manager. Enabling it together with the
  bundle can produce duplicate skill names with different freshness.
- The official host is a developer preview and warns that compatibility-breaking
  changes are expected. Installation, update, migration, and npm channel detail
  lives in the [DSH guide](../README.deepseek-harness.md).

**Observation Metric**
- `bash tests/deepseek-harness/run-tests.sh` (`--integration` is
  environment-bound) and `python tests/helpers/test_aegis_update.py -k deepseek_harness`
- a clean `dsh plugin --profile web add "git+https://github.com/GanyuanRan/Aegis.git"`
  readback lists `aegis` in `dsh.profile.bundles`, and
  `dsh --profile web --dump-config` contains exactly one enabled
  `aegis-method-pack` row
- `cd <aegis-method-pack-root> && python scripts/aegis-update.py register --host deepseek-harness --compatibility-mode --sync-mode junction --json`
  remains the explicit compatibility registration path
- A fresh DeepSeek Harness Standard-mode session receives the native bootstrap
  and either loads the appropriate task-specific skill or declares
  `Route: fast-path`, from exactly one canonical exposure

**Retirement Trigger**
- Retire the marketplace source-selection limitation after a live catalog or
  Desktop readback confirms that it selects the official scoped package or the
  documented Git route, and reports the installed version. A new GitHub release
  alone does not close it. Third-party historical npm artifacts are retained;
  taking ownership or unpublishing them is not part of this repair.
- Re-evaluate the direct-child compatibility path after a stable DeepSeek
  Harness release and two consecutive Aegis releases have verified bundle
  install/update, representative live triggering, session refresh, no duplicate
  exposure, and project workspace support. Until then it remains an explicit
  compatibility path, not a co-active fallback.
- Retire the live-routing limitation of the native context contribution only
  after fresh installed-profile evidence confirms router delivery on `startup`,
  `resume`, `clear`, and `compact`; deterministic host loop tests alone do not
  close it.

### 2.27 Six-Topology Diagnosis Assumes Acyclic Convergence On Discrete Mechanisms

**Retained Item**
- The `systematic-debugging` Causal Topology Gate classifies root claims into
  six acyclic shapes over discrete causes (`single-root`,
  `single-root-multi-symptom`, `chain`, `independent-compound`,
  `conjunctive-cluster`, `disjunctive-or`)
- Cyclic / feedback causation such as race conditions, retry storms, or cache
  invalidation loops, and emergent causes where the root is a relation between
  components rather than a mechanism node, are not yet first-class topology
  categories; current guidance force-fits such cases into `chain` or
  `conjunctive-cluster`
- Diagnostic layers L1-L7 are observation altitudes and remain valid entry
  points for these cases; only the topology vocabulary is incomplete

**Mitigation Today**
- When member-by-member repair keeps regenerating the symptom, the
  three-failed-fixes architecture escalation (`advanced-debugging-governance.md`)
  is the intended exit rather than adding another cluster member
- Workspace retries use `add-attempt` with a soft `process-artifact-pressure`
  signal after repeated failed attempts; `add-evidence` is reserved for
  terminal evidence, so failed verification does not produce another formal
  evidence bundle

**Promotion Trigger**
- A seventh topology becomes eligible only with a real worked replay case
  showing that force-fit classification caused a misrepair, plus the same
  matrix-sample and validator evidence standard the existing six topologies met

### 2.28 Codex Desktop Managed-Worktree Binding Still Needs Live Closeout

**Retained Item**
- Aegis now structurally requires native Worktree/Handoff behavior and a joint
  task-workspace/default-`cwd`/Git-root/`HEAD` readback on ChatGPT desktop app
  surfaces with managed workspaces
- Deterministic contract checks can prove the guidance and fail-closed wording,
  but they cannot observe the desktop UI's actual chat binding

**Retention Reason**
- `GanyuanRan/Aegis#30` demonstrated that `git worktree add` plus a
  command-level `workdir` can leave a Codex Desktop chat bound to Local while
  writes target another checkout
- The native lifecycle may be exposed through the UI or a deferred host tool;
  exact internal tool names are not treated as stable public contracts

**Mitigation Today**
- On a managed Desktop surface, use the native Worktree composer or Handoff,
  then verify trusted task workspace, default command `cwd`, Git worktree root,
  and intended `HEAD` before writes
- If native binding is unavailable or unverifiable, fail closed and preserve
  any manual worktree; missing tools/metadata leave the capability `unknown`
  rather than enabling fallback. Codex CLI and other surfaces retain the
  generic Git fallback only when trusted evidence positively classifies them as
  `non-managed`

**Observation Metric**
- `tests/e2e/workflow-quality-check.sh` verifies the portable owner, Codex
  projection, baseline sync, fail-closed rule, and generic-host compatibility
- A real ChatGPT desktop app run must cover Local-to-Worktree creation or
  Handoff, an already-bound Worktree chat, the default managed detached
  `HEAD`, unavailable native operation, unknown capability classification, an
  unbound manual worktree, and a workspace/`cwd`/Git/`HEAD` mismatch

**Retirement Trigger**
- Retire this limitation only after a fresh supported-version Desktop run
  proves the full matrix and confirms that UI, default `cwd`, Git state, and
  diff/review context stay bound to the same worktree

### 2.29 Native-Skill TDD Routing Remains Model-Mediated

**Retained Item**
- Codex can receive the selected Aegis TDD mode through the managed global
  `AGENTS.md` projection, and Aegis workflows now reject unsupported
  `auto/light` records before source edits
- Codex's native skill matcher and the model's method-layer route selection
  remain host/model behavior rather than an authoritative Aegis runtime gate

**Retention Reason**
- Static contracts and deterministic projection tests can prove that the mode,
  owner rules, invalid-state guards, and downstream consumers agree
- They cannot prove that every model run under every context-pressure shape
  will obey the method guidance; absolute prevention would require a future
  runtime-core or host-adapter gate outside this repository's current boundary

**Mitigation Today**
- Project `tdd_mode` into Codex `AGENTS.md`, keep the TDD skill's native trigger
  narrow, select the route in the workflow that first authorizes source edits,
  and reject missing or unsupported `auto` decisions during plan execution
- Score live smoke on the structured TDD route record, not only on whether the
  TDD skill appeared

**Observation Metric**
- `bash tests/e2e/tdd-policy-check.sh`
- `bash tests/e2e/aegis-doctor-check.sh`
- `bash tests/e2e/workflow-quality-check.sh`
- repeated Codex route smoke covering auto/high-risk, auto/tiny, off/high-risk,
  and off/explicit-strict cases
- `AEGIS_CODEX_REENTRY_REPETITIONS=3 bash tests/skill-triggering/run-codex-reentry-tests.sh`
  covers an unannounced work-type change and continuation after a Codex-proven
  compaction boundary. It scores a current-turn task-specific route before any
  repair step and reports the Codex CLI version, model, and sample count.
- Static checks and prompts that announce resume or compaction do not count as
  live re-entry evidence. If the multi-turn smoke has not run or cannot prove
  the host compaction boundary, report this half as unobserved; a proven
  boundary followed by a route miss is observed negative evidence.
- Fresh maintainer evidence on 2026-09-15 (Codex CLI 0.154.0,
  `gpt-6-astra`, three runs per shape) recorded the expected route after the
  unannounced work-type change and missed the current-turn route after a
  host-proven compaction boundary. This is observed negative evidence, not the
  repeated evidence needed for retirement.

**Retirement Trigger**
- Retire only when a supported runtime/host boundary can enforce route validity
  before source-edit tools, or repeated live evidence establishes an approved
  replacement boundary without claiming method-pack runtime authority
- For the re-entry half, repeated multi-turn runs on a supported Codex version
  must show the expected route after an unannounced work-type change and after
  host-proven compaction, with model, host version, and sample count reported

### 2.30 Recent Benchmark Skill Changes Need Repeated Current-Build Evidence

**Retained Item**
- A repeated, exact-tag end-to-end success verdict for the inherited completion
  claim and external-unknown retirement cases tracked in issues #67 and #68

**Retention Reason**
- The latest published standard snapshot covers Aegis 2.13.0 (2026-10-11),
  after the September revisions recorded below, with one observation per case
  and arm. Its `long-task-preservation-boundary` case failed the same response
  check in both arms; the contributor reports that both attempts noted the
  stale handoff claim in progress messages but neither final response restated
  the correction ([snapshot notes](../../benchmarks/README.md#aegis-2130-standard-snapshot)).
  Revisions after 2.13.0 have only isolated non-benchmark checks. Earlier
  snapshots' failing cases also informed the revisions and cannot serve as
  independent evidence of a new version's performance or complete elimination
  of intermittent failures.
- The [current disposition of #67](https://github.com/GanyuanRan/Aegis/issues/67#issuecomment-5909286564)
  pauses further default-skill changes aimed solely at repeating historical
  corrections in the final reply. The omission is accepted as a known
  limitation only when the requested work is correct, verification claims are
  supported, and active handoff records are accurate; concrete evidence of
  incorrect claims affecting acceptance or subsequent work can reopen
  investigation. This is a prioritization decision, not a change to skill
  requirements, optional reconciliation checks, historical scores, or a claim
  that #67 is fixed.
- A [non-benchmark repeated readback for #67](https://github.com/GanyuanRan/Aegis/issues/67#issuecomment-5854204268)
  found that all nine candidate Aegis attempts recognized the false inherited
  claim during work while only one disclosed it in the final answer. This
  small, non-blind sample shows #67 remains observed; the maintainer has not
  independently reviewed the private raw attempts.
- The optional [Codex reconciliation profile](../README.codex-reconciliation.md)
  passed its selected-case diagnostic gate (S1–S4, three repetitions each,
  twelve records and replies accepted by independent semantic review) after
  earlier candidates had success receipts rejected as false positives and
  inconsistent decisions on an ambiguous-record control. Skill-only tasks with
  the revised rules still omitted the record correction and final disclosure.
  This non-blind development evidence does not resolve default skill-only #67,
  independently prepared case coverage, other host/model behavior, or general
  automatic-fix reliability; evidence qualifications are in
  `tests/codex-reconciliation/README.md`.
- Small, non-blind #68 diagnostics (three fresh copies at `25c0f57`; six frozen
  v2.11.2 workspaces on 2026-09-29) showed the expected risk disclosure, scoped
  confirmation, and unchanged workspaces. They are not independently authored
  held-out cases, a comparative improvement, or proof that intermittent #68 is
  eliminated, and the requested model identity was not independently observed.
- The quick-bug concrete-rationale tag (`implementation-rationale-specific`)
  is available only to future scoring contracts; the published matrix-v7
  contract remains frozen, including the `change necessity` label asymmetry
  recorded in the [benchmark baseline](AEGIS_AGENTIC_BENCHMARK_BASELINE.md).

**Observation Metric**
- Exact-tag diagnostic rerun with per-case checks, changed paths, active
  handoff state, final disclosure, model/host identity, and invalid attempts
- Separately frozen repeated cases and review of flagged outcomes before any
  claim of stable improvement

**Retirement Trigger**
- Repeated current-build evidence and independently prepared cases support a
  scoped claim without changing frozen prompts or scoring after seeing results

---

### 2.31 UI/UX Rules Do Not Establish Product Usability

**Retained Item**
- Task-scoped `ui-ux-governance` rules and advisory experience judgments

**Retention Reason**
- Skill loading, scenario contracts, and bounded agent observations verify
  method behavior, not measured usability of an implemented product
- Browser/device, assistive-technology, realistic-content, and relevant user
  evidence must come from the affected project and supported conditions

**Observation Metric**
- The skill's conditional verification reference, actual task checks, and
  explicit separation of executed evidence from proposed checks

**Retirement Trigger**
- None: this is a permanent evidence boundary. Project-specific evidence can
  support a project's exact experience claim, but no method-pack release
  retires the boundary itself.

---

### 2.32 Offline Benchmark Fixture Has a Limited Target Mapping

**Retained Item**
- The Linux target mapping in `tests/e2e/agentic-benchmark-check.sh`

**Retention Reason**
- The offline launcher/runtime fixture currently maps only Linux
  `x86_64`/`aarch64`; Windows Python reports `AMD64` and fails that check
- An isolated Linux container can execute the unchanged policy checks; this
  is a test-environment limitation, not a Linux-only host-install requirement
- Native macOS fixture execution was not checked; the target mapping alone
  does not establish which macOS configurations can execute the fixture

**Observation Metric**
- Run the original aggregate check under Linux and distinguish its result
  from native Windows host skill-loading evidence

**Retirement Trigger**
- A portable fixture with explicit Windows and macOS regression evidence
  replaces the current Linux-only test mapping

---

## 3. Default Reading Rule

If a limitation appears simultaneously in README, host docs, or test descriptions, use this document as the current reading entry point.

---

## 4. Architecture Review

The core requirements for current limitation management are:

1. Do not conceal limitations
2. Do not write limitations as permanent defects
3. Do not add fallbacks without retirement plans in order to mask limitations

For defect/drift judgment and the seven architecture review dimensions, read
`AEGIS_PROCESS_BASELINE.md` §4–§5. Use only the limitation relevant to the current
task; this catalogue is not a default full read.
