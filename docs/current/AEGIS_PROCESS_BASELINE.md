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
- If there remain issues not yet drilled down to indivisible root causes, do not treat the diagnostic task as complete
- Diagnosis must drill down layer by layer from symptoms (L1 Symptom → L2 Logic → L3 System → L4 Architecture → L5 Cross-system Contract → L6 Platform/Framework Constraint → L7 Spec Gap); the chain's endpoint is "the root cause that cannot be further decomposed", not a fixed layer
- Watch for compound root causes: when symptoms persist after a fix, perform differential diagnosis to distinguish "incomplete fix", "compound root cause", and "chain-causal failure" before deciding the next action
- Watch for terminal unactionable root causes: when the required change exceeds system boundaries (T-class hard signals), record the root cause and boundary, then choose a mitigation/fallback/escalation strategy — do not package a local patch as root-cause repair

---

## 9. Quality Assurance

For standard-path tasks, after exiting the reflection loop, enter quality assurance:

- `Remove/Restore`
- Rollback preparation
- Confidence assessment
- Asset capture

Minimum principle:

- Do not end at "the feature seems to work"
- Must state side effects, residual risks, and rollback boundaries

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

## 12. Project Workspace and Complexity Routing

### 12.1 Creation Rule (Hard Binary)

- **Global install** (plugin registration, version query, skill listing): NEVER write project files.
- **Active project** (user has a codebase loaded): workspace creation is triggered by these workflow file-writing steps:
  * brainstorming checklist item 8 (write design doc)
  * writing-plans save step (write plan file)
  * systematic-debugging Quality Gate (non-trivial task)
  When triggered and `docs/aegis/` is missing, create the minimum workspace immediately. Do not ask. Do not defer.
  If `docs/aegis/` already exists, use it — do not recreate.
- When `scripts/aegis-workspace.py` is available in the active Aegis
  method-pack checkout, prefer it for target-project workspace initialization,
  task lifecycle records, proof-bundle assembly, and validation:
  `python scripts/aegis-workspace.py init --root <target-project-root>`,
  `python scripts/aegis-workspace.py new-work --root <target-project-root> ...`,
  `python scripts/aegis-workspace.py bundle --root <target-project-root> --work YYYY-MM-DD-<slug>`,
  and `python scripts/aegis-workspace.py check --root <target-project-root>`.
- The Aegis method-pack repository itself must not ship a precreated live
  `docs/aegis/` workspace; that directory belongs to the concrete target
  project where Aegis records are being written.

### 12.2 Directory Structure

```text
docs/aegis/
├── README.md                   # workspace purpose and structure
├── INDEX.md                    # dated index of all files
├── BASELINE-GOVERNANCE.md      # constitution: defect/drift rules, check protocol, hard boundaries
├── adr/                        # Aegis-triggered architecture decision records
│   └── YYYY-MM-DD-<title>.md
├── baseline/                   # architecture snapshots (per task/phase)
│   └── YYYY-MM-DD-<scope>-baseline.md
├── specs/                      # design documents (brainstorming output, sole canonical)
│   └── YYYY-MM-DD-<topic>-design.md
├── plans/                      # implementation plans (writing-plans output, sole canonical)
│   └── YYYY-MM-DD-<feature>.md
└── work/                       # process trail (medium+ complexity tasks only)
    └── YYYY-MM-DD-<slug>/
        ├── 10-intent.md
        ├── 20-checkpoint.md
        ├── 90-evidence.md
        ├── 99-reflection.md
        ├── *-draft.json / *-hint.json / gate-input-pack.json
        └── proof-bundle.md
```

### 12.3 Complexity Routing

- **Low complexity**: concise intent + baseline check → TDD, no `work/` created
- **Medium complexity**: baseline read-set + plan + atomic tasks → TDD, `work/` created
- **High complexity**: spec/design + plan + user confirmation → TDD, `work/` created

Mid-stream complexity escalation: pause implementation, initialize workspace if missing, backfill required artifacts, then continue.

TDD is the implementation discipline, not the first entry point for medium- or high-complexity tasks.

### 12.4 INDEX.md Maintenance

Every time a new file is created under `docs/aegis/`, an entry MUST be appended to `INDEX.md`.

When available, use the workspace helper:

```bash
python scripts/aegis-workspace.py append-index --root <target-project-root> --path docs/aegis/<subpath>.md --kind <kind> --title "<title>"
```

`verification-before-completion` should run `python scripts/aegis-workspace.py
check --root <target-project-root>` when a task created or modified a
`docs/aegis/` workspace. The helper also validates recognizable JSON sidecar
artifacts under `docs/aegis/` against
`docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`; this is only a structure
check, not a completion or evidence-sufficiency decision.

For long-task continuation records under `docs/aegis/work/YYYY-MM-DD-<slug>/`,
`long-task-continuation` should prefer helper-backed lifecycle commands:

```bash
python scripts/aegis-workspace.py new-work --root <target-project-root> ...
python scripts/aegis-workspace.py add-checkpoint --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python scripts/aegis-workspace.py add-evidence --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python scripts/aegis-workspace.py add-drift-check --root <target-project-root> --work YYYY-MM-DD-<slug> ...
python scripts/aegis-workspace.py bundle --root <target-project-root> --work YYYY-MM-DD-<slug>
python scripts/aegis-workspace.py check --root <target-project-root>
```

The generated proof bundle is a structural review/handoff package. It is not a
final evidence-sufficiency decision, not an authoritative `GateDecision`, and
not completion authority.

---

## 13. Projection Targets for Existing Skills

This process baseline should be projected into the following skills as a priority:

- `brainstorming`
  - Add TLREF problem definition and scope judgment
- `using-aegis`
  - Add complexity routing, project workspace creation boundary, and prompt hygiene hot path
- `systematic-debugging`
  - Explicitly cover the "Symptom → Logic → System → Architecture" diagnostic layers
- `writing-plans`
  - Introduce impact, compat, retirement, and verification perspectives
- `test-driven-development`
  - Position TDD as the implementation discipline for approved atomic tasks, preventing medium/high-complexity tasks from bypassing planning
- `requesting-code-review`
  - Add evidence sufficiency and architecture drift checks
- `verification-before-completion`
  - Align with reflection, QA, and final output contract

---

## 14. Current Constraints

All subsequent skill modifications must satisfy:

- Rules must be triggerable and executable, not philosophical prose
- Process constraints should fall into specific workflows, not remain as abstract slogans
- The method pack can organize reasoning and artifacts, but must not overstep into claiming authoritative completion

---

## 15. Architecture Review — 7-Dimension Operational Definition

After every non-trivial change, perform the following 7-dimension check:

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

The 7-dimension check results MUST be entered into the Reflection Risk/Unknown field (mapping rules in §17).

### 15.1 Baseline Snapshot Update Trigger

A new `baseline/YYYY-MM-DD-<scope>-baseline.md` MUST be created when any of the following conditions are met:

1. **Architecture review found material drift and it has been resolved** — implementation has returned to baseline or baseline has been updated via ADR; a new snapshot is needed to record the corrected state.
2. **Architecture review found a defect and it has been corrected** — baseline document has been fixed; a new snapshot is needed to solidify the correction.
3. **Reflection Evolve decision is "revise baseline"** — regardless of trigger source, if Reflection determines the baseline needs revision, a new snapshot must be written.
4. **Ownership map, contract inventory, or dependency direction convention has changed** — even if all 7 dimensions pass, if any of these three items changes, a new snapshot is required.

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
