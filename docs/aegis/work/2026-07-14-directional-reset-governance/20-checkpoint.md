# Directional Reset Governance - Checkpoint

- Task ID: 2026-07-14-directional-reset-governance
- Current todo: Write and review the design spec.
- Active slice: Design only; no skill or test implementation before user approval.
- Blocked on: none
- Next step: Create the Design Spec and append it to the workspace index.

## DriftCheckDraft

- Scope status: design completed within authorized scope
- Compatibility status: no implementation or host distribution change
- Retirement status: no new workflow owner introduced; user review pending
- New risk signals:
- user-review-pending
- Advisory decision: pause-for-user

## Checkpoint Update

- Current todo: Await user review of the written Design Spec.
- Active slice: Design review gate; no skill or test implementation is authorized yet.
- Completed todos:
- Read authority baseline and current workflow contracts.
- Run current-version read-only pressure scenario.
- Write and self-review the Directional Reset Governance Design Spec.
- Evidence refs:
- docs/aegis/specs/2026-07-14-directional-reset-governance-design.md
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-current-skill-pressure-readback.json
- Blocked on: User approval of the written Design Spec.
- Next step: After approval, invoke writing-plans and create the implementation plan.

## Checkpoint Update

- Current todo: Await user review of the self-reviewed Design Spec.
- Active slice: Revised design review gate; no skill, helper, schema baseline, or test implementation is authorized yet.
- Completed todos:
- Read authority baseline and current workflow contracts.
- Run current-version read-only pressure scenario.
- Write the Directional Reset Governance Design Spec.
- Complete second-pass first-principles self-review and tighten the state model.
- Evidence refs:
- docs/aegis/specs/2026-07-14-directional-reset-governance-design.md
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-current-skill-pressure-readback.json
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-design-self-review.json
- Blocked on: User approval of the revised Design Spec.
- Next step: After approval, invoke writing-plans and create an implementation plan that preserves the bounded state model.

## DriftCheckDraft

- Scope status: self-review completed within design-only scope
- Compatibility status: proposal remains backward compatible; no implementation or host distribution change
- Retirement status: no new workflow owner introduced; revised design awaits user approval
- New risk signals:
- user-review-pending
- Advisory decision: pause-for-user

## Checkpoint Update

- Current todo: Capture the unmodified multi-turn pressure and size baseline.
- Active slice: Task 1 baseline capture; no skill or helper edits yet.
- Completed todos:
- Read authority baseline and current workflow contracts.
- Run current-version explicit-summary pressure scenario.
- Write and self-review the Directional Reset Governance Design Spec.
- Receive user approval and write the implementation plan.
- Evidence refs:
- docs/aegis/specs/2026-07-14-directional-reset-governance-design.md
- docs/aegis/plans/2026-07-14-directional-reset-governance.md
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-implementation-authorization-and-plan.json
- Blocked on: none
- Next step: Run the bounded unmodified two-turn pressure replay and record size/test baselines.

## DriftCheckDraft

- Scope status: approved implementation plan matches the Design Spec
- Compatibility status: legacy v0 and ordinary call-path preservation are explicit
- Retirement status: locally-green direction reset will retire without a compat owner
- New risk signals:
- none
- Advisory decision: continue

## Checkpoint Update

- Current todo: Add stateful fixtures and context-budget guards for the reduced path.
- Active slice: Task 2 fixture and budget changes; helper, schema, router, descriptions, hosts, and user config remain out of scope.
- Completed todos:
- Run the approved falsifier against unmodified current skills.
- Retire the disproven structured-field/helper proposal.
- Rewrite and validate the Design Spec and implementation plan around existing checkpoint/evidence carriage.
- Evidence refs:
- docs/aegis/specs/2026-07-14-directional-reset-governance-design.md
- docs/aegis/plans/2026-07-14-directional-reset-governance.md
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-reduced-plan-validation.json
- Blocked on: none
- Next step: commit the reduced plan, then update existing test owners before skill wording.

## DriftCheckDraft

- Scope status: same user goal with the falsifier-proven smaller implementation
- Compatibility status: no schema, helper, CLI, router, description, host, or ordinary quick-path expansion
- Retirement status: repairDirectionSummary and helper lifecycle proposals retired before implementation
- New risk signals:
- none
- Advisory decision: continue

## Checkpoint Update

- Current todo: Revise the approved Design Spec and implementation plan to the falsifier-proven smaller path.
- Active slice: Directional reset to planning; all skill/helper edits remain frozen until spec and plan remove the disproven schema path.
- Completed todos:
- Read authority baseline and write the initial implementation plan.
- Run deterministic pre-change context, trigger, workflow, and artifact baselines.
- Run two positive stateful pressure variants and one independent-root negative control against unmodified skills.
- Evidence refs:
- docs/aegis/specs/2026-07-14-directional-reset-governance-design.md
- docs/aegis/plans/2026-07-14-directional-reset-governance.md
- docs/aegis/work/2026-07-14-directional-reset-governance/evidence-bundle-draft-unmodified-stateful-falsification.json
- Blocked on: none; the approved Design Spec pre-authorized reduction when its falsifier passed
- Next step: Rewrite the same Design Spec and plan around existing checkpoint/evidence carriage, stateful fixtures, and call-stability budgets.

## DriftCheckDraft

- Scope status: same user goal; implementation path reduced by the approved falsifier
- Compatibility status: risk reduced by removing schema/helper/CLI changes
- Retirement status: retire the unnecessary repairDirectionSummary proposal and locally-green history loss
- New risk signals:
- plan must be revised before source edits
- Advisory decision: continue
