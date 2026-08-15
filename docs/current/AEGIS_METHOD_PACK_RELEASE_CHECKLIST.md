# Aegis Method Pack Release Checklist

Status: `Reviewed`

## 1. Document Scope

This document defines the minimum release checklist for the current `Aegis Method Pack` prior to an open-source release or controlled release.

This document applies only to:

- `Aegis Method Pack (runtime-ready)`
- Multi-host plugin-installable distribution skeleton

This document does not apply to:

- The full `Aegis Platform`
- `Host Adapters`
- `Runtime Core`

---

## 2. Release Gate

Before executing any formal release, the following must be confirmed item by item:

1. The current release target is still `Aegis Method Pack`
2. Current authority docs do not misrepresent this repository as a full platform
3. Current host installation instructions and testing instructions can point back to the real owner
4. Current known limitations have been written back, rather than hidden in session conclusions
5. If activation, TDD, routing, priority, verification, or authority semantics
   changed, all four global user-rule projections were reviewed and any manual-copy migration was documented

---

## 3. Baseline Readback

The following must be re-read before release:

1. `docs/current/README.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
4. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
5. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
6. `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`
7. `docs/current/AEGIS_RULE_LAYERING.md`
8. `docs/current/AEGIS_ACTIVATION_MODE.md`
9. `docs/current/AEGIS_TDD_MODE.md`

If there are conflicts among these documents, resolve them according to the authority order in `docs/current/README.md`.

---

## 4. Required Verification

Minimum fresh verification for the current method-pack release:

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

If this release explicitly includes OpenCode runtime-side changes, it is recommended to supplement with:

```bash
bash tests/opencode/run-tests.sh --integration
```

If this release explicitly includes Codex distribution chain changes, it is recommended to supplement with:

```bash
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

If this release explicitly includes Antigravity host-surface changes, it is
recommended to supplement with:

```bash
bash tests/antigravity/run-tests.sh
bash tests/antigravity/run-tests.sh --integration
```

If this release explicitly includes Grok Build host-surface changes, supplement
with:

```bash
bash tests/e2e/grok-build-host-boundary-check.sh
python tests/helpers/test_aegis_update.py -k grok
```

If this release explicitly includes DeepSeek Harness bundle changes, supplement
with:

```bash
bash tests/deepseek-harness/run-tests.sh
bash tests/deepseek-harness/run-tests.sh --integration
python tests/helpers/test_aegis_update.py -k deepseek_harness
```

The integration lane is environment-bound when local `dsh` or `pnpm` is absent.
It proves profile installation and module loading, not representative model
routing or release-level host closeout.

When Grok Build is installed locally, also capture `grok inspect --json` as an
environment-bound discovery readback. Do not treat enumeration alone as a
clean-install or live-trigger closeout.

If the current machine's default `bash` points to the WSL launcher rather than a usable Git Bash, or if known smoke latency still exists under Git Bash,
record it in `AEGIS_KNOWN_LIMITATIONS.md`; do not misdiagnose environment and latency blockers as method-pack boundary regressions.

---

## 5. Required Doc Checks

The following host documentation must be re-read before release:

1. `docs/README.codex.md`
2. `docs/README.opencode.md`
3. `docs/README.claude-code.md`
4. `docs/README.codebuddy.md`
5. `docs/README.deepseek-tui.md`
6. `docs/README.deepseek-harness.md`
7. `docs/README.trae.md`
8. `docs/README.copilot.md`
9. `docs/README.qoder.md`
10. `docs/README.antigravity.md`
11. `docs/README.cc-gui.md`
12. `docs/README.kimi-code.md`
13. `docs/README.pi.md`
14. `docs/README.omp.md`
15. `docs/README.openclaw.md`
16. `docs/README.hermes-agent.md`
17. `docs/README.zcode.md`
18. `docs/README.grok-build.md`
19. `docs/testing.md`

Confirm:

- Installation methods do not reference obsolete paths
- Host-specific fallbacks are not misrepresented as the canonical chain
- Testing docs are consistent with the naming of current owners
- CodeBuddy still distinguishes between `.codebuddy-plugin/` skeleton, manual `SKILL.md` install, and incomplete live smoke
- DeepSeek-TUI is still described as manual `SKILL.md` copy install, not a one-click GitHub installer for multi-skill repos
- DeepSeek Harness is distinct from DeepSeek-TUI and remains a developer-preview
  structural target; its default install uses the thin Aegis `dsh.bundle` and
  package-owned `skills/` tree, while updater-managed direct-child links under
  `$DSH_HOME/skills` (`~/.dsh/skills` by default), project `.dsh/skills`, shared
  `.agents/skills`, and custom directories are explicit compatibility routes
  that must not be active beside the bundle
- The GitHub `dsh-plugin` topic is added only after the public default revision
  contains the bundle and a fresh package/profile install has passed; the topic
  means ecosystem discoverability, not an official DeepSeek marketplace listing
- Trae is still described as manual `.trae/skills` / `~/.trae/skills` install, and the `.agents/skills/` optional capability is not written as the canonical chain
- GitHub Copilot is still described through prefixed
  `.github/skills/aegis-<skill-name>/SKILL.md`,
  `.github/copilot-instructions.md`, optional `.github/hooks/*.json`, and
  `AGENTS.md`, not as a repository-local runtime authority or a host adapter
  owned by Aegis
- Qoder is still described through native `~/.qoder/skills/`, `.qoder/skills/`,
  `.qoder/rules/`, and `AGENTS.md` surfaces, not as a fresh live smoke closeout
- Kimi Code CLI defaults to the native Aegis plugin declared by
  `kimi.plugin.json`, with `sessionStart.skill = using-aegis`; plugin identity,
  managed root, version, reload/new-session boundary, and automatic-entry smoke
  are required in addition to generic doctor evidence
- Kimi's updater-managed `$KIMI_CODE_HOME/skills/`
  (`~/.kimi-code/skills/` by default) direct-child discovery remains an
  explicit compatibility installation, while `~/.agents/skills/` is only a
  shared fallback; the plugin and either direct-child route must not be active
  together
- Antigravity CLI is described as the current active closeout target, while
  Antigravity IDE and Antigravity App remain structural target surfaces until
  they have separate fresh evidence
- `docs/testing.md` names `tests/antigravity/run-tests.sh` and its
  `--integration` lane as the current Antigravity CLI verification entrypoints
- CC GUI is described as a structural JetBrains IDEA plugin layer target,
  direct `~/.agents/skills/<skill-name>/SKILL.md` skill-directory exposure is
  preserved for its OpenAI/GPT provider scanner regardless of selected GPT
  model profile, and host adapter event normalization is not claimed as
  Aegis-owned
- Pi CLI is described as a structural Agent Skills / Pi package host surface,
  not current release-level fresh smoke closeout
- OMP (Oh My Pi) is described as a structural `~/.agents/skills/` skill-view
  host surface with `alwaysApply` native injection plus an optional extension
  routing guard, not current release-level fresh smoke closeout
- OpenClaw is described as individual local `SKILL.md` skill-directory install,
  not a canonical whole-repo `git:GanyuanRan/Aegis` install
- Hermes Agent is described as structural skill-host exposure until a fresh
  Hermes install smoke proves the current local discovery path
- ZCode is described as a structural host target that natively reads
  `.claude-plugin/marketplace.json` (Claude Code plugin format), so the
  existing Claude Code plugin skeleton works with zero code changes, not as
  fresh live smoke closeout
- Grok Build is described through one canonical Aegis exposure route at a
  time: updater-managed `$GROK_HOME/skills` direct-child entries, explicit
  `[skills] paths`, or a Claude-compatible plugin. `grok inspect --json`
  enumeration is not misrepresented as clean-install and live-trigger closeout
- Gemini CLI is described as retired and unsupported by Aegis; enterprise,
  Google Cloud, and paid API-key caveats remain explicit so the repository does
  not imply that the upstream CLI itself has ceased to exist
- Gemini retirement does not upgrade Antigravity CLI, IDE, or App beyond their
  separately verified current status

---

## 6. Artifact / Boundary Checks

The following must be confirmed before release:

1. `Aegis` still produces `draft / hint / projection`
2. No new authoritative `GateDecision` has been added
3. No new authoritative `completion authority` has been added
4. No single-host implementation logic has been elevated to baseline
5. Global user rules remain manual host/profile projections rather than a second method owner
6. Lite remains the sole base projection for activation, priority, fast-path,
   baseline completion evidence, and method-layer authority; Advanced remains
   an additive governance overlay without duplicate base rules, across English
   and Chinese
7. Changes to manually copied profile semantics include a release-note migration notice

The following checks may be directly relied upon:

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/artifact-schema-check.sh
bash tests/e2e/host-instruction-invariants-check.sh
```

---

## 7. Release Output Package

A single method-pack release must include at minimum:

1. Installable repository state
2. Host installation instructions
3. Testing docs
4. Compatibility snapshot
5. Known limitations
6. Release notes or tag notes
7. A manual-copy migration note when global user-rule profile semantics changed

---

## 8. Stop Conditions

The release shall be stopped if any of the following occurs:

1. `tests/e2e/run-all.sh --full --host-profile fast` fails
2. Authority documents have conflicts regarding the current repository positioning
3. README and testing docs clearly deviate from current canonical owners
4. The current release attempts to promise full platform capabilities
5. Global user-rule projections conflict with current activation, TDD, priority, verification, or authority semantics

---

## 9. Architecture Review

The final architecture review before release must answer:

- Does the current release still only ship `Method Pack`
- Does the current release maintain plugin-installable properties
- Has the current release misrepresented real-environment regression follow-ups as "completed"

Only when all three questions can be answered with a clear `yes / no` conclusion and there is no authority drift may the release proceed.
