# Aegis Workflow Quality Baseline

Status: `Reviewed`

## 1. Scope and Success Standard

This document owns acceptance criteria for Aegis workflows and their evaluation.
The [Process Baseline](AEGIS_PROCESS_BASELINE.md#2-outcome-principles) owns the
shared outcome principles. Skills own operational decisions and output contracts;
specialist baselines own their domain semantics. Read the relevant criterion and
owner, not all workflows.

This is advisory method-pack quality, not an authoritative runtime core,
`GateDecision`, `PolicySnapshot`, final evidence sufficiency, or completion
authority. Quality samples and helper checks do not grant those powers.

## 2. Acceptance Criteria

Use the criteria implicated by the task. This table is an evaluation contract,
not a new mandatory report. Procedures/templates remain at the named owner.

| Dimension | Acceptance criterion | Detailed owner |
| --- | --- | --- |
| Intent and Outcome | Observed actions and delivered artifacts satisfy each agreed criterion or expose an explicit gap. Apply the Task and Product Acceptance cases below. | Process §2 defines the principles; verification owns closeout. |
| Trigger Accuracy | Explicit requests load the available named skill; evidence-driven routes find design, approved planning, debugging, verification, long-task and ADR owners without unrelated invocations. | Trigger Health; using-aegis; named skill descriptions. |
| Fast-Path Cheapness | Simple Q&A/status/tiny edits use bounded evidence and no needless plan/spec/work files. Complexity/risk, not installation or skill presence, selects ceremony. | using-aegis; skill-discipline. |
| Output Compactness | Depth is proportional to risk and uncovered scope. No full ceremony merely because Aegis is installed. | Active skill; verification closeout. |
| User-Language Output | Prose and labels follow the user's current language. Keep commands, paths, identifiers, enums, and exact names stable; natural wording preserves required semantics. | Active skill; §3 below. |
| Evidence Freshness | A completion claim identifies the current command/manual check, status, scope, and uncovered risk. Unsupported scope stays unknown/partial/needs-verification. | verification-before-completion. |
| Artifact Stability | Required drafts/hints/projections match the schema; JSON validates structurally; proof bundles stay advisory. Retained patch-shape state reuses checkpoints, not new schema fields. | Artifact Schema; long-task; debugging. |
| Workspace Laziness | Install/update/status and ordinary Q&A create no target-project records. Keep authorized baseline bootstrap separate from task records; every new Aegis workspace file is indexed. | Process §3; skill-discipline; workspace support. |
| Authority Boundary | Facts, summaries, snapshots, local checks, reviews, and runtime-ready artifacts do not become policy or final completion authority. | Runtime Ready Boundary; Prompt Hygiene. |
| Three-Stage Complexity Governance | Planning sets pressure/budget, pre-edit checks growth, completion evaluates actual delta. Test/plan/process artifact sprawl also counts. Unresolved overruns block a success claim. | Complexity Governance. |
| Completion-Time Complexity Delta | Actual added/removed entities, changed dimensions, pressure and scope are evidenced; mitigation or accepted limitation is explicit, not hidden behind green tests. | Complexity Governance; verification. |
| TDD Route Mode | Default off avoids automatic strict routing; explicit strict authority applies; auto chooses by risk. Skipped TDD never skips verification. | TDD Mode; owning implementation skill. |
| Micro-Slice Artifact Budget | Parent slices reuse the parent; direct bounded slices need no fabricated parent. Inline Slice Card unless durable-record triggers apply; reconcile acceptance to parent/direct request. | Process §3; writing-plans; long-task. |
| Diagnostic Stop Transparency | Distinguish proximate/contributing/root-unknown from proved recurrence closure; use Deeper Cause Challenge or justified Quick Exit Proof. A green local intervention cannot prove root closure. | systematic-debugging; root-cause-claim-contract. |
| Strong-Opinion Review Lenses | Relevant premise, counterexample, owner/contract, preservation, retirement, and falsifier checks affect the decision. They stay advisory and conditional, not universal templates. | brainstorming; first-principles-review; planning/review. |
| Baseline Role Alignment | Evaluate requirement and architecture roles separately; use the shared defect/drift vocabulary, Requirement Ready Check, evidence and next action. Do not equate implementation with requirement acceptance. | Process §4; verification expanded-closeout. |
| Aegis Invocation Visibility | Non-trivial loaded-skill work explains its task-specific contribution at the first substantive stage and at closeout. Tiny work stays light; slogan repetition and retrospective excuses do not satisfy visibility. | §3; active skill. |
| Semantic Slots and Natural Surface | Required safety/evidence content remains auditable in natural localized prose. One verification closeout aggregates applicable slots instead of stacking skill reports. | §3; verification. |
| Pre-Addition Minimality | Compare reuse of existing owners before a new skill, artifact, adapter, fallback, step or metric. Creation/retirement proof justifies existence; reject or defer unnecessary additions. | Minimality Reference; proposing skill. |
| Change Necessity Before Source Edits | Every new source path and non-trivial source edit has a prior necessity decision. Tiny helpers/guards are not exempt. no-change/docs-config-only decisions constrain implementation. | planning/debugging/TDD/execution owner. |
| Semantic Context Reliability | Bounded passive context reads; active modeling only on real semantic need. Separate fact confidence from decision authority; data is not policy; context paths stay contained. | establishing-project-context; Prompt Hygiene. |
| Capability-Preserving Progressive Disclosure | Default path remains executable; every needed reference has an explicit trigger. Required capability survives before size is judged. | §4; writing-skills. |
| Task-Level Git Lifecycle Quality | Owned delta and pre-existing state remain distinguishable; current-branch-first, coordinator-owned mutations, coherent verified task commits, safe recoverability and fresh integration evidence. | ADR-0003; Git/execution/verification skills. |

### Task and Product Acceptance

Evaluate Process §2 through the applicable cases below. Use actual actions,
artifacts, and answers; the operational check belongs to the verification skill's
[Completion Boundary](../../skills/verification-before-completion/SKILL.md#completion-boundary).

| Case | Observable acceptance evidence |
| --- | --- |
| Single requested object among alternatives | The selected identity is correct; results from other objects are neither substituted nor combined. |
| Multiple deliverables | Every agreed action and output field is delivered, including counts/denominators and exact/display values when required. |
| Missing data or blocked action | The answer separates delivered results from gaps, explains the cause and next dependency, and invents no facts or success. |
| Repair beyond one example | A relevant neighboring case exercises the same owner and requirement; the fix does not hardcode the reported example. |
| Analysis-only or bounded task | Filesystem/actions respect the requested scope. Diagnosis can complete while the product remains unrepaired; any broader acceptance claim has evidence covering that scope. |

These are evaluation cases, not a fixed report format or a requirement to verify
an entire product for a scoped task.

## 3. Output and Operational Ownership

Required content is a set of Semantic Slots, not rigid English headings.
Facts -> Inferences -> Conclusions is an information-ordering principle.
A Natural Surface can be concise while preserving evidence, baseline alignment,
complexity, retirement, authorization, and honest residual risk.

For non-trivial Aegis-shaped work, the first substantive stage includes an
`Aegis Reason Note`/natural Aegis Visibility sentence explaining its contribution.
At stage changes, explain the changed decision/evidence boundary when useful.
`verification-before-completion` is the single completion closeout aggregator.
Its compact `Aegis Impact and Safety Receipt` carries applicable key judgment,
avoided misfix, boundary held, baseline alignment, complexity control, evidence
strength, uncovered risk, and next valuable verification; Aegis path is optional.
A single natural sentence is a fallback for obvious low-risk work. Concision
does not erase required safety semantics.

Structured trace is reserved for audit, debug, release, long-task review, or
user request. `Trace Digest` and `Trace Capability Matrix` distinguish measured,
observed, inferred, declared, unknown, and unavailable host fields; redact
private/secret material and summarize sources. They may show decision summaries,
not raw internal reasoning. Trace and receipts remain advisory.
Detailed cards live in verification's `expanded-closeout.md`; do not copy them
into this baseline or the entry.

| Workflow | Operational / compact output contract owner |
| --- | --- |
| Entry and fast path | `skills/using-aegis/SKILL.md`; `references/skill-discipline.md` only on its stated triggers. Entry projects outcome principles and routing; write owners decide Change Necessity, snapshot and architecture review. |
| Design and preservation | `skills/brainstorming/SKILL.md`; `expanded-design-guidance.md` for triggered design detail. |
| Explicit goal framing | `skills/goal-framing/SKILL.md`; opt-in. Ordinary task intent never requires this route or a goal artifact. |
| Plans and atomic tasks | `skills/writing-plans/SKILL.md`; `expanded-planning-guidance.md` for triggered detail. |
| Debugging | `skills/systematic-debugging/SKILL.md`; causal proof and advanced governance references as triggered. |
| Strict TDD | `skills/test-driven-development/SKILL.md`; selected strict route only. |
| Review | `skills/requesting-code-review/SKILL.md` and `code-reviewer.md`; findings tied to requirements/evidence. |
| Completion / Goal Closure | `skills/verification-before-completion/SKILL.md`; `expanded-closeout.md` for applicable expanded slots. No competing report owner. |
| Retirement | `skills/anti-entropy-governance/SKILL.md` composes with task/verification owners; deletion authority remains scoped. |
| UI/UX | `skills/ui-ux-governance/SKILL.md` composes applicable design/plan/review/verification checks; no automatic backend-only route. |
| Continuation | `skills/long-task-continuation/SKILL.md`; durable-record detail only when triggered. |
| Execution | `skills/executing-plans/SKILL.md`; same-session independent planned work uses `subagent-driven-development` when justified. |
| ADR and baseline sync | `skills/recording-architecture-decisions/SKILL.md`; executed decisions only, ADR records why and baseline current state. |
| Skill authoring / ad-hoc delegation | `skills/writing-skills/SKILL.md` / `skills/dispatching-parallel-agents/SKILL.md`. Isolated model context is not isolated filesystem/Git state. |

This map does not duplicate output templates. Check the actual owning skill
for its fields/enums, triggers, and stop conditions. Preserve explicit/auto
activation, default TDD off, read-only exemptions, conditional design depth,
and the existing durable-record selector.

## 4. Capability-Preserving Context Budgets

Optimize useful steering first: remove duplicated explanations, generic
tutorials, repeated examples, and unnecessary formatting. Main bodies retain
the executable default path, non-omittable constraints and explicit triggers
for direct references. Triggered detail must be findable in one step; untriggered
references must not become default payload.

Capability gates pass before size gates. Preserve positive/negative routing,
stop signals, owner/root-cause rules, verification and the smallest examples
that materially stabilize invocation. A moved paragraph is not an optimization
if agents can no longer find the required rule.

| Main body | Warning target | Hard ceiling |
| --- | ---: | ---: |
| `using-aegis/SKILL.md` | 4,500 bytes | 6,000 bytes |
| `systematic-debugging/SKILL.md` | 10,500 bytes | 12,000 bytes |
| `verification-before-completion/SKILL.md` | 7,500 bytes | 9,000 bytes |
| `executing-plans/SKILL.md` | 9,000 bytes | 10,500 bytes |
| `long-task-continuation/SKILL.md` | 12,500 bytes | 14,000 bytes |

The entry allowance accommodates a short outcome anchor and understandable
routing. It is a maintenance allowance, not a target to fill or an empirically
optimal model limit. Metadata discovery, selected skill bodies, host bootstrap,
and conditional reference reads have different loading costs; evaluate the
actual route and host, not file length alone.

Route-bundle budgets also bound cumulative pressure:

| Main-body bundle | Warning target | Hard ceiling |
| --- | ---: | ---: |
| debugging + verification | 19,000 bytes | 22,000 bytes |
| entry + debugging + verification (debug route) | 22,000 bytes | 26,000 bytes |
| entry + executing-plans + verification (plan-execution route) | 20,000 bytes | 24,000 bytes |
| entry + executing-plans + verification + long-task (long-task route) | 33,000 bytes | 40,000 bytes |

Crossing a warning target requests review but keeps the size gate green.
Crossing a hard ceiling fails and requires capability-preserving extraction or
design review. Do not delete required behavior or hide its trigger to fit.
`tests/e2e/context-budget-check.sh` checks these byte budgets and reference
discovery. Byte/line reduction alone proves neither preserved capability nor
lower latency, tokens, cost, or model-context occupancy.

## 5. Evaluation and Improvement

The representative workflow matrix is
`tests/e2e/fixtures/workflow-quality-matrix.json`. Each sample records
`expectedPrimarySkill`, `allowedSecondarySkills`, `mustNotDo`,
`expectedOutputShape`, `workspacePolicy`, `expectedArtifacts`, and
`verificationSignal`. Preserve both false-negative and false-positive cases.
It is a test contract, not a second prose owner or evidence of live execution.

Before broadening descriptions or adding workflow steps:

1. Freeze/add a representative sample and its actual acceptance criteria.
2. Locate the failed layer: routing, task understanding, execution, delivery,
   evidence, workspace/artifact policy, authority, or context retrieval.
3. Change the smallest owning surface; retire duplicate responsibility and
   rebind consumers/assertions to that owner.
4. Run workflow quality, trigger health, context budget and boundary checks,
   plus task-relevant behavior comparisons.

Existing skill edits use current-version before evidence; new skills use a
no-skill control. Reuse the same positive, negative, and pressure scenarios
afterward, with comparable model/tools/fixtures. Evaluate artifacts, actions,
omissions, authorization and final delivery, not recited principles or keyword
presence. Missing behavior evidence means `needs-verification`, not deployment
readiness. Static checks prove contract consistency; observed runs prove only
their sampled behavior. Do not weaken assertions to hide lost capability.

Use [Agentic Benchmark](AEGIS_AGENTIC_BENCHMARK_BASELINE.md) for with/without
Aegis or broader performance claims. Focused task replays do not prove a
general win. Distinguish measured, observed, inferred and untested findings.
If a change burdens simple work without improving an implicated sample,
revise or reject it.

Task-fidelity cases use the six dimensions and three methods in
[Process](AEGIS_PROCESS_BASELINE.md#task-fidelity-framework). Pair evidenced
distortion with a valid authorized transformation or correction, including
reviewer-added requirements and task/slice delivery claims. Reuse the existing
matrix and stage owners; no separate fidelity score or model request is needed.
Compare complete-task usage, elapsed time, extra reads/reviews, retries and
rework with the same current-version cases. Prompt size and unchanged request
counts alone establish neither savings nor acceptable reasoning cost. Logical
cost analysis supports design choices; observed benefits remain scoped to runs.

Ad-hoc parallel work requires demonstrable independence, disjoint mutation
ownership, and a coordination benefit. Related failures or unclear decomposition
stay inline; written plans use the planned-execution owner. Bound child context
to live host capability; child results are evidence/proposals. The coordinator
owns Git, synthesis, conflict resolution and integrated verification.

Keep evaluation proportional: no new universal score, workflow, artifact, or
runtime gate is created by these criteria.
