# Aegis Current Docs

Status: `Approved`

## 1. Purpose and Reading Route

This directory is the public current baseline for `Aegis Method Pack`.
Use it as a decision index, not a default reading bundle.

For non-trivial work, read the authority order below and ADR-0001, then select
the smallest relevant row in §4. Read its heading/section first; expand for
affected dependencies, contradictory authority, or missing evidence. Reuse
already-read, still-current context. Do not recursively open every link.

For choices about scope, user outcomes, stable repair, or completion, read
[Outcome Principles](AEGIS_PROCESS_BASELINE.md#2-outcome-principles).
For procedure/output details, load the active skill, not every workflow.
Baseline rules are not replaced by this index; an unresolved gap stays explicit.

## 2. Repository Boundary

The repository is `Aegis Method Pack (runtime-ready)`. It owns skills,
workflow discipline, host-installable distribution, explicitly enabled advisory
host callbacks, runtime-ready drafts/hints/projections, and public docs.
It does not own an authoritative runtime core, `GateDecision`,
`PolicySnapshot`, or final `completion authority`.

## 3. Authority Order

When public docs conflict, use this order (the user's current explicit
instruction takes precedence as defined by `AGENTS.md`):

1. `AGENTS.md`
2. `docs/current/README.md`
3. approved ADRs in `docs/adr/`
4. task-relevant docs in `docs/current/`
5. host-specific docs such as `docs/README.codex.md`,
   `docs/README.opencode.md`, `docs/README.claude-code.md`,
   `docs/README.cc-gui.md`, `docs/README.codebuddy.md`,
   `docs/README.deepseek-tui.md`, `docs/README.deepseek-harness.md`,
   `docs/README.trae.md`, `docs/README.copilot.md`, `docs/README.qoder.md`,
   `docs/README.kimi-code.md`, `docs/README.pi.md`,
   `docs/README.openclaw.md`, `docs/README.hermes-agent.md`,
   `docs/README.zcode.md`, `docs/README.grok-build.md`, `docs/README.omp.md`
6. tests and fixtures

## 4. Task-to-Owner Map

These are the public current documents and their distinct responsibilities.
Choose by the decision being made; guides explain usage, while normative
semantics remain at their named owner.

| Task / decision | Current owner and bounded starting point |
| --- | --- |
| Project purpose and long-term direction | `docs/current/AEGIS_TARGET_STATE.md`: target state and non-goals. |
| Product scope / owned surfaces | `docs/current/AEGIS_PRODUCT_BASELINE.md`: relevant product boundary; ADR-0001 below. |
| Goal tradeoff, execution cycle, requirement/design alignment | `docs/current/AEGIS_PROCESS_BASELINE.md`: §2 outcomes, §3 execution, §4 baseline roles, §5 architecture review; §6 conditional specialist map. |
| Workflow acceptance or context budget | `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`: §2 criteria, §3 operational owners, §4 budgets, §5 evaluation. |
| Complexity growth / closure | `docs/current/AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md`: relevant planning, pre-edit or completion stage. |
| Quick-start usage | `docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md` or `docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md`: user's language and relevant entry phrase. |
| Workflow explanation | `docs/current/AEGIS_WORKFLOW_GUIDE.md` or `docs/current/AEGIS_WORKFLOW_GUIDE_ZH.md`: relevant stage; not additional rule owners. |
| Activation auto/explicit | `docs/current/AEGIS_ACTIVATION_MODE.md`: mode semantics and selected host. |
| TDD off/auto/explicit strict | `docs/current/AEGIS_TDD_MODE.md`: route authority and verification. |
| External output or context injection | `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`: relevant intake/source policy. |
| Portable versus host/repo rules | `docs/current/AEGIS_RULE_LAYERING.md`: ownership and projections. |
| Installed skill fails to trigger / overtriggers | `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`: classify failed layer, then its diagnostic section. |
| Agentic behavior or performance claims | `docs/current/AEGIS_AGENTIC_BENCHMARK_BASELINE.md`: evidence/claim scope and selected evaluation lane. |
| Deferred follow-up / retirement marker | `docs/current/AEGIS_DEFERRED_LEDGER.md`: marker convention. |
| Proposing a new owner, skill, artifact, adapter, fallback or metric | `docs/current/AEGIS_MINIMALITY_REFERENCE.md`: pre-addition check. |
| Repair plus retirement / source-of-truth cleanup | `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`: repair/retirement and authorization boundary. |
| Executed architecture decision / baseline sync | `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`: triggers and current-state sync. |
| Draft/hint/projection structure | `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`: relevant artifact only. |
| Runtime-ready versus runtime authority | `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`: relevant boundary. |
| Release or supported-host readiness | `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`: applicable gates; `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`: selected host and evidence scope. |
| Known limitation / retained compatibility | `docs/current/AEGIS_KNOWN_LIMITATIONS.md`: search headings for the affected surface; do not load the whole catalogue by default. |
| Fundamental product boundary | `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`. |
| Kimi automatic entry | `docs/adr/ADR-0002-kimi-native-plugin-is-the-automatic-entry.md`. |
| Branch/worktree/commit/integration lifecycle | `docs/adr/ADR-0003-current-branch-first-git-lifecycle.md`: relevant lifecycle section. |

## 5. Ownership and Update Rule

Shared principles and baseline-role vocabulary belong to Process; acceptance
criteria and payload budgets belong to Workflow Quality; specialist semantics
belong to their named current doc; procedures and output contracts belong to
skills. The entry is a portable short projection for routing and tradeoffs,
including installs that copy skills without current docs.

When public behavior, installation, release gates, runtime-ready artifacts, or
authority boundaries change, update the smallest current owner before the
implementation. Rebind existing readers/tests when moving responsibility.
Do not preserve a stale duplicate merely to satisfy a literal-location check,
or weaken an invariant to make a shorter document pass.

## 6. Local Archive Rule

`docs/archive/` is local-only and ignored by git. Implementation history,
private smoke notes, migration plans and session evidence belong there, not
in the public current surface. Do not reference it from public README files,
host install docs or release instructions. Process evidence alone is not a
new current authority document.
