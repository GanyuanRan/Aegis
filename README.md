# Aegis

中文版本：[README.zh-CN.md](README.zh-CN.md)

## Minimal Install

If you are using an AI coding agent, you can ask it to install Aegis for you:

> Please read the installation instructions in https://github.com/GanyuanRan/Aegis carefully, identify the correct path for my AI coding host, install Aegis globally, restart or reload the host if needed, and verify that the Aegis skills are discoverable.

`Aegis` is an Architecture-Driven Development (ADD) method pack for AI coding agents.

It builds on the original `superpowers` methodology and adds evidence-driven governance, TLREF execution flow, and dual-track repair/retirement rules.

In Aegis, ADD means the agent should understand the project's baseline, architecture boundaries, owners, impact surface, compatibility constraints, and verification path before making substantial changes.

Current release shape:

> `Aegis Method Pack (runtime-ready)`

This repository is **not** the full `Aegis Platform`. It does not provide authoritative runtime-core decisions, authoritative `GateDecision`, or completion authority.

## Problems Aegis Solves

AI coding agents are strong at local execution, but long or risky software work often fails for process reasons:

- work starts before the task boundary and baseline are clear
- the agent claims completion without fresh evidence
- bug fixes add new fallback logic while old owners keep running
- long tasks lose state after compaction, handoff, or multi-agent work
- architecture drift is noticed only after the change has already spread

Aegis addresses those problems at the method-pack layer. It makes the agent frame the task,
read the relevant baseline, keep evidence close to claims, track repair and retirement together,
and maintain resumable checkpoints for long work.

## What Users Get

Installing Aegis gives an AI coding tool a stricter development discipline without requiring a new runtime platform:

- clearer task framing before edits
- safer debugging and refactoring loops
- fewer unsupported "done" claims
- better long-task continuity through todo checkpoints, resume hints, and drift checks
- explicit compatibility and retirement thinking when behavior changes
- portable workflows across Codex, OpenCode, Claude Code, and other skill-aware hosts

## What Aegis Adds

Aegis keeps the useful parts of `superpowers`:

- composable skills
- skill-triggered workflows
- multi-host install and plugin distribution skeletons
- implementation planning, review, debugging, and verification practices

Aegis adds a stricter governance spine:

- baseline-first work
- evidence before claims
- impact-aware task framing
- TLREF / DIVE / Reflection / QA execution discipline
- repair track plus retirement track for bug fixes, refactors, contract changes, and governance cleanup
- long-task continuation with todo checkpoints, resume hints, drift checks, and evidence bundles
- runtime-ready artifacts that remain drafts, hints, projections, and evidence bundles

## Current Scope

Aegis currently owns:

- method-pack skills
- initial instructions and contributor guardrails
- host installation guidance
- representative tests and verification assets
- runtime-ready artifact shapes
- release, rollback, known-limitation, and compatibility checklists for maintainers

Aegis does not currently own:

- `Host Adapters`
- `Runtime Core`
- authoritative `GateDecision`
- final completion authority
- full production rollout guarantees

For the current authority map, read:

- [docs/current/README.md](docs/current/README.md)
- [docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md](docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md)

## Host Compatibility

Aegis keeps the multi-host plugin-installable goal.

Current host-facing status:

| Host | Current status |
| --- | --- |
| `Codex` | Representative smoke path verified; Git Bash naive smoke still has known observation items |
| `OpenCode` | Base suite and integration closeout have passed in the current method-pack scope |
| `Claude Code` | Plugin skeleton and install guide exist; release-level fresh host smoke is still pending |

Other hosts remain product targets, but are not yet current release-level verdicts.

Read:

- [docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md](docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md)
- [docs/current/AEGIS_KNOWN_LIMITATIONS.md](docs/current/AEGIS_KNOWN_LIMITATIONS.md)

## Installation

Aegis can be installed through each host's native discovery or plugin path.
A public marketplace listing is not required for the paths below.

After installation and host restart, Aegis skills are discovered automatically.
For normal use, users can ask for development work naturally; the agent should
select the relevant Aegis method when the task matches a skill. Explicit skill
commands are still available when you want to force, test, or debug a workflow.

Optional: for smoother host-level behavior, copy one of the global user rules
templates into your AI coding tool's global user rules:

- [English template](GLOBAL_USER_RULES_TEMPLATE.md)
- [Chinese template](GLOBAL_USER_RULES_TEMPLATE.zh-CN.md)

### Codex

macOS / Linux:

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/.codex/aegis
mkdir -p ~/.agents/skills
ln -s ~/.codex/aegis/skills ~/.agents/skills/aegis
```

Windows PowerShell:

```powershell
git clone https://github.com/GanyuanRan/Aegis.git "$env:USERPROFILE\.codex\aegis"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\aegis" "$env:USERPROFILE\.codex\aegis\skills"
```

Optional Codex config for subagent-heavy skills:

```toml
[features]
multi_agent = true
```

Restart Codex, then ask it to use `aegis:using-aegis` or an Aegis skill such as
`brainstorming`.

### OpenCode

Use the plugin shortcut by adding Aegis to the `plugin` array in your global or
project `opencode.json`:

```json
{
  "plugin": ["aegis@git+https://github.com/GanyuanRan/Aegis.git"]
}
```

If the file already has plugins, append Aegis:

```json
{
  "plugin": [
    "other-plugin",
    "aegis@git+https://github.com/GanyuanRan/Aegis.git"
  ]
}
```

Then restart OpenCode and verify:

```bash
opencode --version
```

Ask: `Tell me about your aegis`.

### Claude Code

Marketplace flow:

```bash
claude plugin marketplace add GanyuanRan/Aegis
claude plugin install aegis@aegis-dev --scope user
```

Local checkout flow:

```bash
git clone https://github.com/GanyuanRan/Aegis.git ~/aegis
claude --plugin-dir ~/aegis
```

Inside Claude Code, run `/reload-plugins`, then try `/aegis:using-aegis`.

Full host guides:

- [Claude Code](docs/README.claude-code.md)
- [Codex](docs/README.codex.md)
- [OpenCode](docs/README.opencode.md)

The project still preserves the broader multi-host distribution skeleton inherited from `superpowers`, including Cursor and Gemini-related package surfaces. Those surfaces should not be interpreted as current fresh release-level closeout unless the compatibility matrix says so.

## First Project Baseline

Aegis works best when the target project has a small, explicit baseline before
large development work starts. Without one, Aegis can still run, but task
framing, authority lookup, verification, and drift checks rely more on ad-hoc
context and may be less stable.

For a new or undocumented project, first ask the agent to create a lightweight
project baseline, for example:

```text
Use Aegis to establish this project's baseline before implementation:
purpose, current architecture, authority docs, run/test commands, compatibility
boundaries, non-goals, and verification expectations.
```

For an existing project, point the agent at the repository's current source of
truth, such as `README`, `CONTRIBUTING`, architecture docs, ADRs, or local
project rules, and ask it to treat those as baseline references before changing
code.

## Execution Model

Aegis is not a daemon, background runner, or authoritative runtime core.
It works through host-level skill discovery, bootstrap context, and explicit skill loading.

Automatic behavior:

- Codex discovers Aegis skills from the configured skills directory at startup.
- OpenCode loads the Aegis plugin, mirrors skills into OpenCode's global skills path,
  and injects compact bootstrap context.
- Claude Code loads Aegis through its plugin namespace or a local plugin directory.
- `using-aegis` tells the agent to check whether a task-specific skill applies before responding.
- In day-to-day use, you do not need to manually name a skill for every request;
  explicit commands are the override path when you want a specific method.

Explicit use:

- Ask for a skill by name, such as `aegis:brainstorming`,
  `aegis:systematic-debugging`, `aegis:long-task-continuation`,
  or `aegis:verification-before-completion`.
- In OpenCode, use the native `skill` tool, for example: `use skill tool to load aegis/brainstorming`.
- In Claude Code, use the plugin namespace, for example: `/aegis:using-aegis`.

Long-task behavior:

- Aegis can keep `TodoCheckpointDraft`, `ResumeStateHint`, `DriftCheckDraft`,
  and `EvidenceBundleDraft` discipline around long work.
- This improves resumability and reduces drift, but it does not create a host watchdog,
  automatic retry loop, or final completion authority.

## Core Workflow

The method pack is organized around agent workflows:

1. **Brainstorming**
   - clarify intent, scope, impact, and baseline read set before implementation
2. **Writing Plans**
   - produce bite-sized, verifiable plans with exact files, verification steps, and compatibility boundaries
3. **Systematic Debugging**
   - move from symptoms to root cause with evidence before fixes
4. **Test-Driven Development**
   - use red/green/refactor where applicable
5. **Requesting Code Review**
   - review for behavioral risks, regressions, and missing tests
6. **Verification Before Completion**
   - no completion claim without fresh verification evidence

For bug fixes, architecture changes, contract work, and governance cleanup, Aegis requires:

- **Repair track**
  - real root cause
  - canonical owner
  - smallest necessary change
  - compatibility boundary
  - verification method
- **Retirement track**
  - old owner / fallback / patch location
  - whether it is still active
  - reason to keep it, if any
  - deletion or convergence trigger
  - validation before removal

## Runtime-Ready Artifacts

Current method-pack outputs may include:

- `TaskIntentDraft`
- `BaselineReadSetHint`
- `ImpactStatementDraft`
- `EvidenceBundleDraft`
- `GateInputPack`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

These are advisory and runtime-ready. They are not authoritative runtime decisions.

Read:

- [docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md](docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md)
- [docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md](docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md)

## Testing

Primary verification entry:

```bash
bash tests/e2e/run-all.sh --full --host-profile fast
```

Focused checks:

```bash
bash tests/e2e/boundary-compliance-check.sh
bash tests/e2e/artifact-schema-check.sh
bash tests/opencode/run-tests.sh
bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
```

Read:

- [docs/testing.md](docs/testing.md)
- [docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md](docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md)

## Contributing

Read:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

Before changing behavior-shaping skill content, also read:

- [skills/writing-skills/SKILL.md](skills/writing-skills/SKILL.md)
- [skills/verification-before-completion/SKILL.md](skills/verification-before-completion/SKILL.md)

## Relationship To Superpowers

Aegis is derived from **[Superpowers](https://github.com/obra/superpowers)**, created by [Jesse Vincent](https://github.com/obra). Superpowers pioneered the idea of composable, multi-harness agent skills — the foundation this project builds on.

We are grateful to Jesse and all Superpowers contributors for creating and maintaining the original project under the MIT license, and for establishing the plugin distribution patterns (Claude Code, Codex, Cursor, OpenCode, Gemini CLI) that Aegis continues to use.

This project adds a governance-focused method layer and public release path for the `Aegis Method Pack`, while preserving Superpowers' zero-dependency philosophy and multi-harness compatibility.

## Acknowledgments

We thank [Matt Pocock](https://github.com/mattpocock) and all contributors to [mattpocock/skills](https://github.com/mattpocock/skills) (MIT license) for sharing their skill designs openly. Several ideas from that project — particularly around concise communication, shared language glossaries, and disciplined debugging — have influenced Aegis skill design.

| Aegis skill | Inspired by | What we adapted |
|-------------|-------------|-----------------|
| `communicating-concisely` | `/caveman` | Ultra-compressed communication mode with auto-clarity exception |
| `establishing-project-context` | `/grill-with-docs` | CONTEXT.md shared language system, terminology tightening during brainstorming |
| ADR creation gate | `/grill-with-docs` ADR discipline | Three-condition gate before creating architecture decision records |
| Feedback loop construction | `/diagnose` Phase 1 | Priority ladder for building automated bug reproduction loops |

These ideas were re-implemented in Aegis format — shorter, multi-harness compatible, and integrated with the TLREF/DIVE/Reflection governance spine rather than copied verbatim.

Internal implementation notes are kept out of the public release tree. The
public contract is the skill content, current authority docs, and this
acknowledgment.

## License

MIT License. See [LICENSE](LICENSE).
