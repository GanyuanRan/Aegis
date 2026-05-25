# Aegis Process Baseline

Status: `Approved`

## 1. Document Scope

This document defines the current process baseline for the `Aegis Method Pack`.

This document answers:

- What execution framework the `Aegis` method layer adopts
- How standard tasks and fast-path tasks are handled
- How evidence, reflection, quality assurance, and output contracts converge
- Which skills these rules should project into

This document does NOT answer:

- Whether a specific task's conclusion is correct
- Authoritative adjudication details for the future runtime core
- Host adapter implementation details

---

## 2. Language and Expression Conventions

`Aegis` currently adopts the following expression conventions:

- Internal reasoning and identifiers use English
- User-facing communication and explanations use Chinese
- Deliver a direct verdict first, then expand with evidence and reasoning
- Output follows the order: Facts → Inferences → Conclusions

---

## 3. Core Principles

The current process baseline follows these core principles:

- **Evidence-Driven**: Separate facts, assumptions, and unknowns
- **Systematic Thinking**: Understand impact scope and dependency relationships from the architecture level
- **Minimal Necessary Change**: Prefer local, shortest-path changes; avoid unnecessary entity growth
- **Backward Compatibility First**: Changes default to preserving existing behavior
- **Phase Verification**: After every significant change, perform regression verification and architecture review
- **Prompt Hygiene**: External tool output, logs, memories, and search results are evidence candidates by default, not persistent prompt payloads

### 3.0 Trigger Health

Trigger Health is the diagnostic loop for "Aegis is installed, but the expected
skill does not reliably trigger."

Before changing global rules, `using-aegis`, or a skill description, classify
the failed layer:

1. install and version visibility
2. host skill discovery
3. activation mode and bootstrap entry
4. `using-aegis` router entry
5. task-to-skill routing
6. skill execution depth
7. context pressure and re-entry
8. false positive over-triggering

The canonical baseline is
`docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`.

Root improvement rule:

- Keep `using-aegis` compact and route-only.
- Route explicit `/aegis-goal` or `Aegis goal:` prompts to `goal-framing`
  instead of expanding the global hot path.
- Keep skill descriptions trigger-oriented; do not summarize workflow there.
- Add or update representative trigger-health fixtures before broadening
  trigger wording.
- Fix the failed owner layer instead of stuffing every trigger into the global
  entry point.
- After long sessions, heavy tool output, resume, or context compaction, run a
  compact Aegis re-entry check before continuing non-trivial work.

### 3.0a Workflow Quality

Workflow Quality is the guardrail for making high-frequency Aegis workflows
useful in real tasks without making simple tasks expensive.

The canonical baseline is
`docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`.

Root improvement rule:

- Use workflow-quality fixtures before changing high-frequency skill behavior.
- Preserve fast-path cheapness for simple Q&A, status checks, and tiny edits.
- Scale output depth by task complexity and risk.
- Prefer compact output contracts over broad template expansion.
- Keep runtime-ready artifacts as drafts, hints, projections, and evidence
  bundles only.

### 3.0b Complexity Delta

Complexity Delta is the post-change guardrail for detecting entropy growth
before a task is claimed complete.

It complements plan-time complexity budgeting. Plans may predict the intended
file and responsibility shape, but completion-time review must compare the
actual diff against the final code shape.

For non-trivial code changes, `verification-before-completion` should report a
compact Complexity Delta before the final completion claim:

```text
Complexity Delta:
- Files over 800 lines:
- Files newly crossing 800 lines:
- Largest touched file delta:
- Largest touched function/block:
- New branches/fallbacks/adapters:
- Retired branches/fallbacks/adapters:
- Net entropy: decreased | stable | increased-with-justification
- Required follow-up:
```

The 800-line threshold is a review signal, not a universal failure gate.
Generated files, vendored files, fixtures, lockfiles, and framework-owned
artifacts may be exempt when the reason is explicit. For normal source files,
new work that pushes a file past 800 lines or continues adding logic to an
already oversized file must either justify the owner boundary or report a split
/ refactor follow-up.

Function, method, component, or similarly cohesive block growth should be
treated as the same entropy class. A touched block over roughly 80 lines, deeply
nested logic, or a block that combines multiple reasons to change should be
reported as a Complexity Delta risk even when the containing file is below 800
lines.

When the diff adds fallback, adapter, compatibility, guard, or branch logic, the
Complexity Delta must be read together with Retirement Closure. Net new paths
without deleted or scheduled old paths count as entropy increase and must be
explained in `Risk/Unknown`.

### 3.0c Strong-Opinion Review Lenses

Strong-Opinion Review Lenses are compact task-specific checks that make Aegis
more decisive without turning the method pack into a roleplay system or runtime
approval layer.

Canonical lenses:

- `Product Risk Lens` in `brainstorming`: value, non-goals, trade-offs,
  decision-needed, and whether the idea deserves implementation
- `Plan Pressure Test` in `writing-plans`: owner / contract / retirement risk,
  verification scope, and task executability
- `Findings First` in `requesting-code-review`: bugs first, risk first, tests
  first, with findings before summary
- `Readiness Summary` in `verification-before-completion`: tests, docs,
  version, host compatibility, uncovered scope, and residual risk
- `Retro / Memory Filter` in `recording-architecture-decisions`: executed
  durable decisions may become ADR/baseline memory; unexecuted ideas stay out of
  accepted architecture memory

These lenses are review structures, not persona commands. They do not grant
merge approval, publish authorization, authoritative `GateDecision`, or
completion authority.

### 3.1 Ripple Signal Triage

Ripple Signal Triage is the pre-change entry point for dependency-aware work.

Before implementation, check whether the requested change touches any ripple
signal:

- shared module, core logic, or cross-module behavior
- public API, schema, data contract, or compatibility boundary
- persistence, cache, export/copy/readback path, or source-of-truth candidate
- fallback, adapter, duplicate owner, legacy path, or retirement boundary
- producer and consumer both implicated by the same change
- bug fix proposed at a consumer/caller instead of the canonical owner
- candidate fix adds keyword, phrase, regex, negation-word list,
  sample-text exception, local guard, one-off branch, fallback, adapter,
  compatibility branch, prompt branch, or legacy path expansion
- downstream logic re-parses raw text or re-infers action/state while typed
  intent, normalized state, contract, or another source-of-truth already exists
- artifact, download, export, readback, or cache behavior is patched without
  first locating the producer and source-of-truth owner

If no signal is hit, continue through the normal workflow without extra output.

If any signal is hit, perform the smallest sufficient triage before code
changes:

1. Identify the canonical owner and affected downstream consumers
2. State whether any source-of-truth, contract, fallback, or retirement risk exists
3. Expand verification scope when producer/consumer, contract, shared module, or
   real user paths are affected
4. If the candidate fix shape itself is the signal, record
   `PatchShape`, `CanonicalOwner`, `UpwardDrillSignal`, and `Decision`
   before editing
5. Record the result as a short note or in `ImpactStatementDraft` when the task is
   medium/high complexity

If the triage requires changing the canonical owner, changing a public contract,
making a cache/export/copy into a source of truth, retaining two owners, or
adding a fallback/adapter/compatibility branch, pause for design or explicit
alignment before implementation.

`Cascade proliferation` in the Architecture Review remains the post-change
review of whether the implemented change introduced unexpected ripple scope.

---

## 4. Prompt Hygiene and Evidence Injection Boundary

The current process baseline uses `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md` as the canonical owner for prompt hygiene.

Minimum rules:

- External tool output, logs, memories, and search results default to summary-first, with raw excerpts cited on demand.
- Large raw output is isolated at its source by default; only source, scope, summary, refs, and unknowns enter the prompt.
- When a summary is insufficient, read back the smallest raw excerpt or run fresh verification — do not lower the judgment standard.
- When information is still insufficient, the conclusion MUST be downgraded to `unknown`, `partial`, or `needs-verification`.
- Reducing persistent context must not weaken baseline-first, evidence-before-claims, impact review, root-cause-first debugging, or verification-before-completion.

---

## 5. Todo Recitation Loop

For standard-path tasks, the todo recitation loop MUST be explicitly executed:

1. Create or update the todo list when the task begins
2. List complete steps
3. Re-read the todo list before every phase transition
4. Write back current state and next step

The goal of the todo recitation loop is not formal checkmarking — it is to prevent scope drift during analysis, execution, or verification phases.

---

## 6. TLREF: Path Selection

`Aegis` currently adopts the path-selection layer of the three-layer reflective execution framework:

### 6.1 Fast Path

Applicable tasks:

- Knowledge Q&A
- Configuration adjustments
- Dependency upgrades
- Other low-risk, clearly bounded problems not requiring deep governance

Execution requirements:

- Execute directly
- Verify results
- Must retain factual evidence

### 6.2 Standard Path

Applicable tasks:

- Diagnosis
- Feature work
- Architecture work
- Refactoring
- Performance work

Execution requirements:

- Problem definition
- Analysis and decision-making
- Execution and verification
- Quality assurance

The todo recitation loop must run throughout the standard path.

---

## 7. DIVE: Standard Path Minimum Cycle

For standard-path tasks, the current minimum execution cycle is:

- `Define`
- `Investigate`
- `Validate`
- `Evolve`

### 7.1 Define

Must cover at minimum:

- `What / Who / When / Where / Why / How / How much`
- Current environment and reproducible baseline
- Success criteria and acceptance method

### 7.2 Investigate

Must cover at minimum:

- Data flow and owner
- Compatibility boundary
- Whether special cases are business-required or historical patches
- Whether the local issue has escalated to the architecture level

### 7.3 Validate

Must cover at minimum:

- Whether evidence supports the current judgment
- Whether acceptance criteria are met after implementation
- Whether new risks, drift, or hidden gaps have been introduced

### 7.4 Evolve

Must cover at minimum:

- Whether the current conclusion should exit, continue iterating, or escalate the problem definition
- Whether baseline, ADR, review, or verification strategy needs revision
- Whether completed work should backfill, amend, supersede, or skip an ADR
  based on `docs/current/AEGIS_ADR_AUTO_BACKFILL.md`

---

## 8. Reflection Checklist

For standard-path tasks, every round MUST complete the minimum reflection:

- `Goal`
- `DeeperCause`
- `Evidence`
- `Risk/Unknown`
- `Decision`

Where:

- If `DeeperCause` cannot be clearly answered as "no", do not exit directly
- If `Evidence` cannot support the current judgment, do not package inferences as conclusions
- If there remain issues not yet drilled upward to indivisible root causes, do not treat the diagnostic task as complete
- Diagnosis must drill upward layer by layer from symptoms (L1 Symptom → L2 Logic → L3 System → L4 Architecture → L5 Cross-system Contract → L6 Platform/Framework Constraint → L7 Spec Gap); the chain's endpoint is "the root cause that cannot be further decomposed", not a fixed layer
- Candidate fixes that add keyword, phrase, regex, negation-word lists, local
  guards, one-off branches, fallbacks, adapters, compatibility branches,
  prompt branches, legacy path expansion, consumer-side patches, or downstream
  re-parsing while a typed contract/source-of-truth exists are hard signals to
  continue upward drilling before implementation
- Watch for compound root causes: when symptoms persist after a fix, perform differential diagnosis to distinguish "incomplete fix", "compound root cause", and "chain-causal failure" before deciding the next action
- Watch for terminal unactionable root causes: when the required change exceeds system boundaries (T-class hard signals), record the root cause and boundary, then choose a mitigation/fallback/escalation strategy — do not package a local patch as root-cause repair

---

## 9. Quality Assurance

For standard-path tasks, after exiting the reflection loop, enter quality assurance:

- `Remove/Restore`
- Complexity Delta
- Rollback preparation
- Confidence assessment
- Asset capture

Minimum principle:

- Do not end at "the feature seems to work"
- Must state side effects, residual risks, and rollback boundaries
- For non-trivial code changes, must state whether the actual diff decreased,
  preserved, or increased complexity before claiming completion

---

## 10. Test Failure Iron Law

The current process baseline explicitly rejects the following behaviors:

- Modifying tests to cover up business code defects
- Modifying business code to accommodate incorrect tests
- Bidirectional accommodation without first locating the error source

The enforced principle is:

- Code is wrong → fix the code
- Test is wrong → fix the test
- Final guarantee: business behavior is genuinely correct AND test expectations are accurately aligned

---

## 11. Final Output Contract

The current minimum `Aegis` output must include:

- `Facts`
- `Evidence`
- `Recommendation/Approach`
- `Impact Scope`

Extended by task type:

- Diagnosis: reproduction steps, root cause, blocking points
- Feature work: acceptance criteria, interface or data contract changes
- Architecture work: option comparison, trade-offs, ADR references
- Refactoring: hotspots, test safety net, complexity changes
- Performance: baseline, bottleneck, gains
- Risk and rollback: trigger conditions, rollback steps, feature flags

---

## 12. Project Workspace, Baseline Bootstrap, and Complexity Routing

### 12.1 Project Baseline Bootstrap

Project Baseline Bootstrap is the first active-project guardrail.

When the user is inside a codebase and asks a project-related question or asks
what to do next, Aegis should check whether a project baseline already exists
before giving code-changing advice. Existing project authority docs, ADRs,
README, local agent rules, and `docs/aegis/baseline/` all count as candidate
baseline sources.

If no usable baseline is found, do a bounded repo scan using an index-first
flow:

1. identify project root and git state
2. list files with `rg --files` or equivalent
3. ignore generated, dependency, build, vendor, and output directories
4. read README, manifests, config, entry points, key `src` files, and tests
5. infer stack, module owners, contracts, dependency direction, run/test commands,
   and compatibility boundaries

If there is sufficient project content, create the first baseline snapshot
under `docs/aegis/baseline/` and continue answering the user's original
question. If content is too sparse, do not generate an empty baseline; tell the
user that the baseline was skipped because sufficient project content is not
available, then still answer the original question from the evidence that
exists.

### 12.2 Lazy Workspace Support

Aegis Project Workspace hard binary rule:

- **Global install** (plugin registration, version query, skill listing,
  updating Aegis itself): NEVER write target-project files.
- **Fast path** (normal Q&A, simple explanation, version status, git status,
  tiny wording/format edits, and low-risk single-file changes): do not create
  `docs/aegis/` unless a workflow explicitly needs a reusable project record.
- **Active project record needed**: initialize or use `docs/aegis/` only when
  baseline bootstrap, spec writing, plan writing, medium/high debugging, ripple
  triage, long-task continuation, or work evidence requires persistent files.

Use configured Aegis workspace support when it is available. The current
repository ships zero-dependency scripts for workspace initialization,
lifecycle records, proof-bundle assembly, and structural checks, but these are
method-pack support tools. They validate structure and index coverage only;
they do not decide evidence sufficiency and do not grant completion authority.
Resolve the helper from the installed method-pack support path, then pass the
target project separately, for example
`python <aegis-workspace-helper> check --root <target-project-root>`.

The Aegis method-pack repository itself must not ship a precreated live
`docs/aegis/` workspace. That directory belongs to the concrete target project
where Aegis records are being written.

### 12.3 Workspace Shell and Task Work Record

Workspace Shell is the lightweight project-local container:

```text
docs/aegis/
├── README.md
├── INDEX.md
├── BASELINE-GOVERNANCE.md
├── adr/
├── baseline/
├── specs/
├── plans/
└── work/
```

Task Work Record is created only for medium/high or long-running work:

```text
docs/aegis/work/YYYY-MM-DD-<slug>/
├── 10-intent.md
├── 20-checkpoint.md
├── 90-evidence.md
├── 99-reflection.md
├── *-draft.json / *-hint.json / gate-input-pack.json
└── proof-bundle.md
```

Every new file under `docs/aegis/` must be indexed in `INDEX.md`.

### 12.4 Spec Brief and Design Spec

Use the smallest spec artifact that stabilizes the task:

- **Spec Brief** (`docs/aegis/specs/YYYY-MM-DD-<topic>-brief.md`): medium tasks
  where what/why/acceptance needs to be pinned before planning, but no formal
  architecture design is needed.
- **Design Spec** (`docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`): high
  complexity, architecture, contract, migration, cross-module, or ambiguous
  product behavior that needs user review before planning.

Both are advisory method-pack artifacts. Existing project docs and ADRs remain
the preferred authority when they already own the truth.

### 12.5 Complexity Routing

- **Low complexity**: concise intent + baseline check → TDD, no `work/` created
- **Medium complexity**: baseline read-set + Spec Brief or requirements + plan
  + atomic tasks → TDD; create `work/` only when a process trail is needed
- **High complexity**: Design Spec + plan + user confirmation → TDD, `work/`
  created

Mid-stream complexity escalation: pause implementation, initialize workspace if
missing, backfill required artifacts, then continue.

TDD is the implementation discipline, not the first entry point for medium- or
high-complexity tasks.

### 12.6 Workspace Integrity Checks

When configured Aegis workspace support is available, workflows that write
`docs/aegis/` should use the shared support path for:

- appending `INDEX.md`
- creating task work records
- adding checkpoints, evidence, and drift checks
- assembling proof bundles
- checking workspace structure before pause, handoff, or completion candidate

The generated proof bundle is a structural review/handoff package. It is not a
final evidence-sufficiency decision, not an authoritative `GateDecision`, and
not completion authority.

### 12.7 ADR Auto Backfill

ADR Auto Backfill is the completion-time workflow for turning completed
engineering work into architecture memory.

It uses the strongest available source in this order:

1. `docs/aegis/work/YYYY-MM-DD-<slug>/`
2. `docs/aegis/plans/YYYY-MM-DD-<topic>.md`
3. `docs/aegis/specs/YYYY-MM-DD-<topic>-brief.md` or
   `docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`
4. git diff, commits, verification output, release notes, and current docs

The workflow may create, amend, supersede, or skip an ADR. It must not promote
speculative, unexecuted plans into durable architecture memory.

If an ADR action changes or confirms ownership, contract inventory, dependency
direction, source-of-truth ownership, compatibility boundary, host support
status, runtime-ready artifact boundary, or retirement schedule, a baseline sync
check is mandatory.

Canonical rule:

```text
ADR records why.
Baseline records current state.
```

Detailed trigger and sync rules live in
`docs/current/AEGIS_ADR_AUTO_BACKFILL.md`.

---

## 13. Projection Targets for Existing Skills

This process baseline should be projected into the following skills as a priority:

- `brainstorming`
  - Own design/spec clarification for new, ambiguous, architecture, contract,
    cross-module, or medium/high-complexity work; do not force low-complexity
    fast-path work through full design ceremony
- `first-principles-review`
  - Provide a lightweight compositional review for first-principles, Occam,
    ambiguous direction, repeated fixes, fallback growth, duplicate owners, or
    architecture/product direction risk; own the decision hygiene escalation for
    invariants, owner / retirement, and falsification checks before risky specs
    or plans are endorsed; do not add it to the always-loaded hot path
- `using-aegis`
  - Add complexity routing, project workspace creation boundary, and prompt hygiene hot path
- `systematic-debugging`
  - Explicitly cover the "Symptom → Logic → System → Architecture" diagnostic layers
- `writing-plans`
  - Introduce impact, compat, retirement, and verification perspectives
- `test-driven-development`
  - Position TDD as the implementation discipline for approved atomic tasks, preventing medium/high-complexity tasks from bypassing planning
- `requesting-code-review`
  - Add evidence sufficiency, architecture drift checks, and missing ADR /
    baseline sync findings for durable architecture decisions
- `verification-before-completion`
  - Align with reflection, QA, final output contract, and ADR Auto Backfill for
    completed medium/high work that touched architecture surfaces

---

## 14. Current Constraints

All subsequent skill modifications must satisfy:

- Rules must be triggerable and executable, not philosophical prose
- Process constraints should fall into specific workflows, not remain as abstract slogans
- The method pack can organize reasoning and artifacts, but must not overstep into claiming authoritative completion

---

## 15. Architecture Review — 7-Dimension Operational Definition

After every non-trivial change, perform the following 7-dimension check. The
`Cascade proliferation` dimension is a post-change review companion to the
pre-change Ripple Signal Triage in §3.1.

| # | Dimension | Check Question | Pass Criterion |
|---|-----------|---------------|----------------|
| 1 | Ownership integrity | Does every component have exactly one canonical owner? Any new duplicate owners? | No new duplicate owners |
| 2 | Module boundaries | Any unauthorized cross-module coupling? Does new code respect existing module boundaries? | Boundaries not eroded |
| 3 | Contract changes | Any API/signature/behavior contract changes? Are they documented? Backward compatible? | Changes documented, compatible or explicitly broken |
| 4 | Cascade proliferation | Any new cascading dependency chains? Does a single change ripple beyond expected scope? | Ripple scope ≤ expected |
| 5 | Dependency direction | Do dependencies flow toward stability? Any circular or reverse dependencies? | No cycles, direction correct |
| 6 | Retirement completeness | Old owners/fallbacks/paths deleted or scheduled? Any "add only, never remove" patterns? | Retirement track explicit |
| 7 | Entropy flow | Net complexity decreased or increased? Any unjustified new entities, branches, or adapters? | Entropy decreased or stable |

If any dimension fails → record as an architecture finding → decide: fix now / schedule fix / record as known limitation.

The 7-dimension check results MUST be entered into the Reflection Risk/Unknown field (mapping rules in §17). For non-trivial code changes, the Entropy flow finding should be backed by the completion-time Complexity Delta when available.

### 15.1 Baseline Snapshot Update Trigger

A new `baseline/YYYY-MM-DD-<scope>-baseline.md` MUST be created when any of the following conditions are met:

1. **Architecture review found material drift and it has been resolved** — implementation has returned to baseline or baseline has been updated via ADR; a new snapshot is needed to record the corrected state.
2. **Architecture review found a defect and it has been corrected** — baseline document has been fixed; a new snapshot is needed to solidify the correction.
3. **Reflection Evolve decision is "revise baseline"** — regardless of trigger source, if Reflection determines the baseline needs revision, a new snapshot must be written.
4. **Ownership map, contract inventory, or dependency direction convention has changed** — even if all 7 dimensions pass, if any of these three items changes, a new snapshot is required.
5. **ADR Auto Backfill created, amended, or superseded a decision that changes current architecture state** — the baseline must either be updated or explicitly state why the existing baseline remains valid.

Name the new snapshot by change date and use the 10-field template (see `brainstorming/SKILL.md` Initial Baseline Snapshot Template). Snapshots are evidence, not authority — BASELINE-GOVERNANCE.md remains the constitution.

Low-complexity tasks (no `work/`, no 7-dimension review) do not trigger snapshot updates.

---

## 16. Architecture Defect and Architecture Drift

### 16.1 Architecture Defect

Definition: a confirmed error, gap, or internal contradiction IN the baseline itself.

Criteria:
- The ownership map recorded in the baseline contradicts the actual code structure
- A contract declared in the baseline is inconsistent with the implementation (and the implementation is correct)
- The dependency direction convention recorded in the baseline is violated by the baseline itself
- An unresolved contradiction exists between two baseline documents

Process:
1. Confirm the baseline is the wrong party (not implementation drift)
2. Fix the baseline document
3. If the implementation deviated due to the defective baseline → align implementation to the corrected baseline
4. NEVER patch the implementation side to accommodate a defective baseline

### 16.2 Architecture Drift

Definition: implementation has deviated from a confirmed, correct, and unchanged baseline.

Criteria:
- New code introduced a new owner not recorded in the baseline
- New code modified a contract recorded in the baseline without updating the contract document
- New code violated the dependency direction convention recorded in the baseline
- New code duplicated the responsibility of an existing canonical owner in the baseline

Process:
1. Confirm the baseline is correct (not a baseline defect)
2. Return the implementation to the baseline via the simplest path
3. If the drift is intentional → update the baseline first (via ADR process), then align the implementation
4. NEVER "update the baseline to match the drift" without explicit review

### 16.3 Baseline Check Protocol

Before every non-trivial change:
1. Read the latest snapshot in `baseline/`
2. Compare current code structure against the ownership map
3. Compare current contracts against the contract inventory
4. Check whether known anti-patterns have new instances
5. Report: aligned / minor drift (self-correctable) / material drift (needs review)

---

## 17. Architecture Review → Reflection Risk/Unknown Mapping

Explicit mapping from 7-dimension check results to Reflection checklist:

| Architecture Dimension | Reflection Field | Mapping Rule |
|------------------------|-----------------|--------------|
| Ownership integrity | Risk/Unknown | New duplicate owner → record as Risk |
| Module boundaries | Risk/Unknown | Boundary erosion → record as Risk |
| Contract changes | Evidence | Contract change → cite as Evidence |
| Cascade proliferation | Risk/Unknown | Ripple beyond expected → record as Unknown |
| Dependency direction | Risk/Unknown | Cycle/reversal → record as Risk |
| Retirement completeness | Risk/Unknown | Not retired → record as Risk, note schedule |
| Entropy flow | DeeperCause | Entropy increase → check for unanalyzed deeper cause |

This mapping ensures architecture review findings are not lost during the Reflection phase.
