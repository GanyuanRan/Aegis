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

---

## 3. Baseline Readback

The following must be re-read before release:

1. `docs/current/README.md`
2. `docs/current/AEGIS_TARGET_STATE.md`
3. `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
4. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
5. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
6. `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`

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
6. `docs/README.trae.md`
7. `docs/README.copilot.md`
8. `docs/README.qoder.md`
9. `docs/README.antigravity.md`
10. `docs/README.cc-gui.md`
11. `docs/README.pi.md`
12. `docs/README.openclaw.md`
13. `docs/README.hermes-agent.md`
14. `docs/testing.md`

Confirm:

- Installation methods do not reference obsolete paths
- Host-specific fallbacks are not misrepresented as the canonical chain
- Testing docs are consistent with the naming of current owners
- CodeBuddy still distinguishes between `.codebuddy-plugin/` skeleton, manual `SKILL.md` install, and incomplete live smoke
- DeepSeek-TUI is still described as manual `SKILL.md` copy install, not a one-click GitHub installer for multi-skill repos
- Trae is still described as manual `.trae/skills` / `~/.trae/skills` install, and the `.agents/skills/` optional capability is not written as the canonical chain
- GitHub Copilot is still described through `.github/skills/`,
  `.github/copilot-instructions.md`, optional `.github/hooks/*.json`, and
  `AGENTS.md`, not as a repository-local runtime authority or a host adapter
  owned by Aegis
- Qoder is still described through native `~/.qoder/skills/`, `.qoder/skills/`,
  `.qoder/rules/`, and `AGENTS.md` surfaces, not as a fresh live smoke closeout
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
- OpenClaw is described as individual local `SKILL.md` skill-directory install,
  not a canonical whole-repo `git:GanyuanRan/Aegis` install
- Hermes Agent is described as structural skill-host exposure until a fresh
  Hermes install smoke proves the current local discovery path
- Gemini CLI is described as a transitional compatibility surface with the
  `2026-05-19` Google transition announcement and `2026-06-18` consumer
  service-stop boundary, while preserving enterprise and paid API key caveats
  and not claiming Aegis has retired Gemini CLI

---

## 6. Artifact / Boundary Checks

The following must be confirmed before release:

1. `Aegis` still produces `draft / hint / projection`
2. No new authoritative `GateDecision` has been added
3. No new authoritative `completion authority` has been added
4. No single-host implementation logic has been elevated to baseline

The following checks may be directly relied upon:

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/artifact-schema-check.sh
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

---

## 8. Stop Conditions

The release shall be stopped if any of the following occurs:

1. `tests/e2e/run-all.sh --full --host-profile fast` fails
2. Authority documents have conflicts regarding the current repository positioning
3. README and testing docs clearly deviate from current canonical owners
4. The current release attempts to promise full platform capabilities

---

## 9. Architecture Review

The final architecture review before release must answer:

- Does the current release still only ship `Method Pack`
- Does the current release maintain plugin-installable properties
- Has the current release misrepresented real-environment regression follow-ups as "completed"

Only when all three questions can be answered with a clear `yes / no` conclusion and there is no authority drift may the release proceed.
