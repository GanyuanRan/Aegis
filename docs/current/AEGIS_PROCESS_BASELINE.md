# Aegis Process Baseline

Status: `Approved`

## 1. Scope and Reading

This is the shared method contract for `Aegis Method Pack (runtime-ready)`.
It owns outcome principles, the execution cycle, baseline roles, and architecture
review. It does not adjudicate a task's correctness or grant authoritative
`GateDecision`, `PolicySnapshot`, evidence sufficiency, or completion authority.

Read §2 for tradeoffs; §3 for execution; §4 for requirement/design alignment;
§5 for architecture review and baseline updates. Use §6 to find the specialist
owner only when its trigger applies. Do not read every linked document.
Skills carry portable operational projections; host adapters source the entry
skill. The authority order in `docs/current/README.md` remains unchanged.

## 2. Outcome Principles

> Understand the user's need accurately, complete the task correctly and
> reliably within authorization and business constraints, and deliver a complete,
> usable result that satisfies the need and can be verified.

These are the baseline's shared decision principles. Their abstraction does
not raise their instruction priority or authorize rewriting concrete acceptance
criteria. They add no checklist, artifact, approval step, universal
`goal-framing` invocation, or expansion of scope.

Project goals define supported capabilities, durable constraints and reliability;
the current task defines authorized delivery, and engineering supports both.
Project ambition never overrides the user's current scope, such as "analysis only";
one successful case never proves project-wide reliability.

### Task Fidelity Framework

Through understanding, transformation, execution and delivery, do not silently
change the task, evidence or result's meaning. Fidelity permits authorized
summaries, designs, edits and evidence-based corrections; it does not require
literal copying or establish that a source is true.

Use six review dimensions at existing relevant checkpoints:

1. **Goal fidelity.** Resolve the object, scope, requested actions, conditions,
   quantities, exclusions and deliverables from the conversation. Later requests
   may continue, amend, pause or replace work; preserve outstanding intent.
   Tool limitations do not authorize shrinking delivery. Keep unsupported needs
   visible. Clarify material ambiguity before dependent action and continue
   independent authorized work; a clear authorized request needs no extra approval.
2. **Semantic fidelity.** Preserve meaning needed for the user's decision or use
   within the authorized transformation. Check relevant relationships, behavior
   and ordering, identity/hierarchy/ownership, and explanations or qualifiers.
   Retaining every source word does not prove these meanings survive.
3. **Evidence and uncertainty fidelity.** Keep facts, inferences, proposals,
   unknowns and verified conclusions distinguishable with their relevant sources.
   New evidence may change confidence or conclusions; expose material corrections
   and do not turn an assumption or undefined choice into an established fact.
4. **Authority and responsibility alignment.** Respect authorization, business
   rules, non-goals, compatibility and user control. Evidence can justify a
   proposed goal change but cannot supply missing authority. Downstream work and
   reviewers may flag conflicts; they cannot add acceptance requirements or
   acquire Host permission and completion authority.
5. **Execution and delivery truthfulness.** Distinguish plans, attempts, execution,
   verification and actual usable delivery. Tests of real acceptance criteria can
   support acceptance within their covered scope; intermediate success alone
   cannot replace delivery. Distinguish task/slice completion from capability
   acceptance. Report delivered results, remaining work, reason and dependency;
   never label partial or failed work complete.
6. **Effective, behavior-preserving repair.** Fix the evidenced problem class at
   its owner and protect legitimate neighboring behavior. Preserve accepted
   obligations rather than incorrect old internals. Use proportionate checks;
   new complexity needs an evidenced need, not a single example made green.

Apply three methods proportionately:

- **Bidirectional review:** compare source requirements and the result for both
  omissions/weakening and unsupported additions/strengthening. Judge changes
  against the authorized transformation, not literal equality.
- **Cross-stage tracing:** follow source → understanding → expression → execution
  → delivery to the first evidenced distortion. That location is an observation,
  not proof of root cause; use the existing debugging method when needed.
- **Paired counterexamples and proportionate verification:** check that the defect
  is detected and a relevant valid case remains accepted. Scale evidence to
  impact and uncertainty; deterministic checks establish only their tested scope.

Reuse sufficient current evidence and read only sources that can materially
change the decision. Stop when required checks and material risks are resolved
or further inquiry repeats an assessed mechanism without decision value. Preserve
unresolved facts as unknown; no exhaustive lineage or universal semantic proof
is required. These are review criteria, not six model calls, compulsory reports,
new approval steps or a separate runtime gate.

## 3. Execution Cycle

TLREF selects a risk-proportional path. Clear, bounded low-risk tasks use the
fast path: act within scope, verify the result, and retain factual evidence.
Task labels such as configuration or dependency upgrade do not by themselves
prove low risk. Non-trivial/ambiguous work uses the standard path below.

Maintain the task's complete steps and current state. At phase transitions,
re-read intent, acceptance, accepted constraints, remaining work, and the next
action. Use existing task state; do not create a record solely for this rule.

| DIVE stage | Required decision |
| --- | --- |
| Define | What/who/when/where/why/how/how much, environment, reproducible starting state, success criteria and acceptance method. |
| Investigate | Data flow, canonical owner, consumers, compatibility, business-required exceptions versus historical patches, and whether the issue exceeds the local boundary. |
| Validate | Does evidence support the judgment and requested outcome? Check acceptance, new risk, drift, and uncovered scope. |
| Evolve | Exit, continue, or escalate the problem definition. Decide whether the baseline, ADR, review, or verification strategy needs revision. |

Before edits, triage ripple signals: shared logic, contracts, persistence or
source of truth, producer/consumer changes, fallback/duplicate-owner retirement,
and consumer-side or sample-specific patch shapes. Identify the canonical owner,
affected consumers, contract/retirement risk, and proportional verification.
For debugging, the precise `PatchShape` / `CanonicalOwner` /
`UpwardDrillSignal` / `Decision` contract belongs to
`skills/systematic-debugging/SKILL.md`. Local green evidence cannot erase that
triage on retry or resume. A renamed carrier is not evidence of a new direction.
Owner/contract/source-of-truth changes and new fallbacks require the applicable
design alignment before implementation, reusing existing authorization.

Reflect at meaningful standard-path checkpoints using the existing semantic
slots: `Goal`, `DeeperCause`, `Evidence`, `Risk/Unknown`, `Decision`.
For debugging, root/recurrence claims and negative-proof quick exits are governed
by `skills/systematic-debugging/root-cause-claim-contract.md`; a successful
local intervention alone is not proof of a closed recurrence generator.

QA covers Remove/Restore, actual Complexity Delta for non-trivial code changes,
rollback boundaries, confidence, and reusable evidence. The verification skill
aggregates one closeout, including applicable architecture findings and
ADR/baseline sync. Output depth is proportional; do not append every skill's
template. Distinguish facts, inferences, and unknowns. Communication and quality
criteria belong to `AEGIS_WORKFLOW_QUALITY_BASELINE.md`.

### Stable Change

Minimal Necessary Change means the smallest sufficient change at the correct owner and abstraction layer.
Fix the problem class with proportional neighboring-case verification.
Neither fewest changed lines nor a hardcoded case-specific success justifies
fallback growth, duplicate owners, or unrelated redesign. Use
`AEGIS_MINIMALITY_REFERENCE.md` before proposing an additional surface.

### Preservation and Retirement

Before changing semantics, identify evidence-backed behavior to preserve, the
highest-risk counterexample, and material uninspected surfaces. Give each known
anchor/reference a disposition: preserve, rebind to its canonical owner, retire
with reason, or reject because of a conflict. Recheck accepted constraints
against the original goal at existing design, plan, and completion checkpoints.
Unknown relationships remain unknown; this is not exhaustive lineage proof.

Preserve published behavior/contracts by default, not every internal old path.
For responsibility-scoped retirement and its authorization boundary, use
`AEGIS_DUAL_TRACK_GOVERNANCE.md` §3.2; keep repair and retirement explicit.

### Test Failure Iron Law

Locate whether behavior or the test expectation is wrong against accepted
requirements before editing either. Fix wrong code; correct wrong tests.
Never change tests to hide business defects, change behavior to accommodate
incorrect tests, or adjust both merely to get green. The result must satisfy
business acceptance and accurately aligned test expectations.

### Workspace and Task Continuity

Use existing project authority and records first. Before non-trivial work,
read the smallest relevant requirement and architecture sections, not every
baseline. Sparse projects need a bounded scan; lack of documents does not
justify invented authority or an automatic full workspace.

Workspace support is lazy. Install/update/status and ordinary Q&A do not write
target-project records; the authorized baseline-bootstrap exception before
code-changing advice remains owned by
`skills/using-aegis/references/skill-discipline.md`. Workspace shell/bootstrap
and a task work record are separate. Long-task continuation needs a durable work
record for medium/high work, actual cross-session execution, required handoff,
or otherwise required resumable state. Possible compaction, multiple todos,
or subagent use alone do not force files.

A parent-owned micro-slice reuses its plan/spec; a direct bounded mechanical
request uses `Parent plan/spec: none — direct bounded request`. Both use a
compact Slice Card, inline unless the durable-record selector applies. New
ownership, contract, schema, API, migration, persistence, security, release,
or unclear verification boundaries require re-evaluation; slice completion
reconciles with the parent or direct request and any active goal frame.

Index new `docs/aegis/` files when that workspace is used. Configured workspace
helpers belong to the installed method pack, not an assumed target-project
script. Their checks/proof bundles validate structure, not evidence sufficiency.
For bootstrap/spec depth use skill-discipline and brainstorming's
`expanded-design-guidance.md`; for durable state and drift use
`long-task-continuation` and `AEGIS_ARTIFACT_SCHEMA_BASELINE.md`.

## 4. Baseline Roles and Alignment

Keep these roles separate, whether held in one small document or several:

| Role | What it owns |
| --- | --- |
| Product / Requirement Baseline | Confirmed sources, goals/scope, users/scenarios, functional, quality, constraint and delivery-transition requirements, acceptance/verification criteria, non-goals, workflow constraints, open questions, and change/alignment records. |
| Architecture / Runtime Boundary Baseline | Canonical owners, contracts, source of truth, dependency direction, compatibility, retirement, and method-pack/runtime boundaries. |

Business/mission requirements belong inside goals/scope. Do not introduce a
separate top-level `Business Requirements Baseline` owner. A task intent or
conversation can authorize current work and inform a baseline check without
automatically becoming durable project authority. Snapshots evidence current
state; ADRs record why; approved baselines/current docs record what is true now.

### Requirement Ready Check

Before a dependent design, plan, execution, or acceptance decision, establish
requirement sources, goals/scope, users/scenarios, requirement items,
acceptance/verification criteria, and open blocker questions. Reuse references
rather than require a new form. Report the needed decision:
`ready | needs-source | needs-goal-alignment | needs-scenario |
needs-acceptance-criteria | needs-clarification | needs-user-decision | blocked`.

`ready` means sufficient for the next method step, not implemented, verified,
accepted, or granted completion authority. A clear local task may be ready
while project-wide acceptance remains unproven; missing durable documents alone
do not invalidate explicit task authorization.

### Design Defect and Implementation Drift

Existing implementation or test limitations are not automatically business
restrictions. Resolve a suspected mismatch against the confirmed requirements
and architecture roles before choosing the wrong-party correction below.

- `Design Defect`: a confirmed error, gap, contradiction, or wrong abstraction
  in the requirement/design/baseline itself. Examples include contradicting
  accepted user goals/criteria, conflicting authority docs, or placing a
  responsibility at the wrong owner or layer. Confirm the baseline is wrong,
  correct the relevant requirement/design/current authority first, then align
  implementation. Do not patch around a defective baseline.
- `Implementation Drift`: implementation, plan, review, or documentation
  deviates from a confirmed correct and unchanged baseline. Examples include
  out-of-scope behavior, duplicate owners, undocumented contracts, or reversed
  dependencies. Restore alignment through the simplest stable path. An
  intentional change follows the relevant requirement/spec/ADR review first;
  do not rewrite the baseline merely to bless drift.
- Historical `Architecture Defect` and `Architecture Drift` remain aliases
  for architecture-scoped Design Defect and Implementation Drift.

Before non-trivial changes, read the current candidates for both roles, compare
the proposed/actual behavior with acceptance and owner/contract boundaries,
and check for known anti-pattern recurrence. The shared Baseline Role Alignment
result is `aligned | Design Defect | Implementation Drift | missing-authority |
needs-clarification`, with `scope: requirements | architecture | both`,
evidence, and next action. Do not turn an unresolved authority gap into
permission, or require a new approval where current instructions already resolve it.

## 5. Architecture Review and Baseline Updates

For non-trivial changes, review the relevant dimensions below; record why an
unaffected dimension is not applicable instead of inventing work. Findings feed
existing reflection and verification; no separate universal artifact is needed.

| Dimension | Passing condition | Reflection destination on finding |
| --- | --- | --- |
| Ownership integrity | One canonical owner per responsibility; no duplicate authority. | Risk/Unknown: duplicate owner. |
| Module boundaries | No unauthorized coupling or boundary erosion. | Risk/Unknown: eroded boundary. |
| Contract changes | Changes documented; compatibility preserved or break explicitly accepted. | Evidence: changed contract and acceptance. |
| Cascade proliferation | Ripple scope stays within justified expectations. | Risk/Unknown: unexpected/uninspected impact. |
| Dependency direction | No unintended cycles or reversed dependency direction. | Risk/Unknown: cycle/reversal. |
| Retirement completeness | Old responsibilities removed, retained with reason, or scheduled explicitly. | Risk/Unknown: remaining work and schedule. |
| Entropy flow | Complexity decreases or remains justified and bounded. | DeeperCause: unexplained growth; use actual Complexity Delta. |

A failed dimension requires an explicit fix-now, scheduled-fix, or known-limit
disposition, with evidence and residual risk. A disposition is not acceptance
of an unmet requirement; unresolved blocking constraints still prevent a full
completion claim.

### Baseline Snapshot Update Trigger

Record the corrected current state when material Implementation Drift is
resolved, an architecture-scoped Design Defect is corrected, reflection chooses
"revise baseline", or ownership/contract inventory/dependency direction changes.
Also run baseline sync when ADR creation/amendment/supersession changes current
architecture: update the baseline or explain why it remains valid.

Use the project's existing current baseline owner and snapshot convention.
If the project uses Aegis workspace snapshots, create the corresponding
`baseline/YYYY-MM-DD-<scope>-baseline.md`; do not add a competing authority.
For the first baseline, use the dual-role bootstrap from brainstorming.
Snapshots contain verified state and explicit unknowns, never speculative
design or copied transcript. Low-risk work needs no new snapshot unless a
trigger above applies. Detailed ADR triggers and executed-decision evidence
belong to `AEGIS_ADR_AUTO_BACKFILL.md`.

## 6. Conditional Owner Map

Read the named owner only for the decision in the first column. Linked
procedures and templates are not a default read-set.

| Decision / trigger | Canonical detail |
| --- | --- |
| Installed but routing fails, false positives, context re-entry | [Trigger Health](AEGIS_TRIGGER_HEALTH_BASELINE.md); `using-aegis/references/skill-discipline.md`. Keep the entry compact; repair the failed layer. |
| Output quality, visibility, context budgets, evaluating behavior | [Workflow Quality](AEGIS_WORKFLOW_QUALITY_BASELINE.md); active skills own their output semantics. |
| Explicit goal/success/stop framing | `skills/goal-framing/SKILL.md`; ordinary intent understanding does not invoke it. |
| Source-change necessity or proposed new owner/path/artifact | Owning design/plan/debugging/execution skill and [Pre-Addition Minimality](AEGIS_MINIMALITY_REFERENCE.md). `no-change` and `docs/config-only` constrain edits. |
| Complexity before plan, before edit, at completion | [Complexity Governance](AEGIS_COMPLEXITY_GOVERNANCE_BASELINE.md). Unresolved overruns block a success claim. |
| TDD route | [TDD Mode](AEGIS_TDD_MODE.md): default `off`; explicit strict instruction applies; verification remains mandatory. |
| Task-Level Git Lifecycle | [ADR-0003](../adr/ADR-0003-current-branch-first-git-lifecycle.md); execution, worktree, finishing and verification skills. Current-branch-first; task-start snapshot; one coordinator owns Git mutations; managed-host constraints and integration checks stay with those owners. |
| Ambiguous design, competing constraints, preservation/falsification | `brainstorming`, `first-principles-review`; accepted requirements and current scope constrain design. |
| Bug class, causal stop, patch shape, retry | `systematic-debugging/SKILL.md`, `advanced-debugging-governance.md`, `root-cause-claim-contract.md`. |
| UI/UX effects | `ui-ux-governance` composes with the task owner; reduce total user effort while preserving accessibility, control, safeguards, and accepted requirements. |
| Semantic Context Infrastructure | `establishing-project-context`: passive relevant context reads; active modeling for actual conflicts/renames/deprecation, not every task. Facts/confidence are not decision authority. |
| External output, logs, memory, search, bounded history | [Prompt Hygiene](AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md): summary/index first, smallest verification excerpt, insufficient evidence stays unknown/partial/needs-verification. |
| Deprecation, fallback, source-of-truth or owner retirement | [Dual-Track Governance](AEGIS_DUAL_TRACK_GOVERNANCE.md); `anti-entropy-governance`. |
| Completion, review, and durable decision closure | `verification-before-completion` aggregates; `requesting-code-review` reviews; `recording-architecture-decisions` and [ADR Auto Backfill](AEGIS_ADR_AUTO_BACKFILL.md) sync executed decisions. |

Rules must affect decisions in their owning workflow. Keep shared invariants
here, specialist semantics at their owner, and operational instructions in the
skills. Do not reproduce a whole workflow in the entry, baseline index, or
host-specific prompt.
