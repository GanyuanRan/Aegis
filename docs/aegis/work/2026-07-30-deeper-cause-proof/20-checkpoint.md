# Prevent premature debugging root-cause closure - Checkpoint

- Task ID: 2026-07-30-deeper-cause-proof
- Current todo: Add pressure-scenario regression contracts before changing the skill.
- Active slice: Paused before test or skill edits; only baseline investigation is complete.
- Blocked on: None; intentionally paused for cross-device handoff.
- Next step: Run the documented RED assertions, then update the sole causal-proof owner and compact router.

## Checkpoint Update

- Current todo: Add deterministic premature-root pressure cases and assertions before skill edits.
- Active slice: Paused before any debugging contract/test implementation edits; workspace only contains handoff records.
- Completed todos:
- Read authority docs and current causal owners; run clean focused baseline; obtain isolated three-scenario pressure result.
- Evidence refs:
- baseline-pressure:A/B reveal quick-lane and existing-default trigger ambiguity; C remains valid quick lane
- focused-baseline:debugging patch-shape, workflow matrix, and context-budget checks pass
- Blocked on: Cross-device handoff requested by user; no technical blocker.
- Next step: On the new computer, fetch and switch to the WIP branch, validate workspace, then implement tests before skill changes.

## DriftCheckDraft

- Scope status: No implementation drift: no skill, baseline, fixture, validator, or test behavior was edited before pause.
- Compatibility status: Runtime-authority and host-distribution boundaries unchanged; WIP branch only.
- Retirement status: Planned retirement remains explicit: replace self-judged no-deeper-why closeout and stale independent-compound necessity wording; nothing retired yet.
- New risk signals:
- Quick-lane exemption currently depends on self-classification and existing default modification may evade patch-shape triggers.
- Advisory decision: pause-for-user

## ResumeStateHint

- Intended remote branch: `wip/deeper-cause-proof-20260730`
- Base commit before this checkpoint: `14b6daa fix: preserve debugging closure triggers`
- Source worktree branch before handoff: `feature/agentic-benchmark-p1`
- Remote default branch observed before handoff: `origin/main` at `9f8e157`
- Implementation state: no debugging skill, baseline, fixture, validator, or test
  behavior has been edited for this task. Only this resumable workspace record
  is new.
- Installed-host warning: `~/.codex/aegis/skills/systematic-debugging/SKILL.md`
  is not the repository source and may still contain the older, larger skill.
  Do not use it as the implementation target or copy it over the branch.

## Confirmed Diagnosis

The seven layers remain a localization taxonomy:

`L1 Symptom -> L2 Logic -> L3 System -> L4 Architecture -> L5 Cross-system Contract -> L6 Platform -> L7 Spec Gap`

Do not add an eighth layer. The defect is the stop proof, not the taxonomy.

The isolated pressure baseline established three facts:

1. A local `default` branch can look like the root after its current
   reproduction turns green even though an upstream configuration generator
   remains unchecked. Existing wording is ambiguous when the branch already
   existed rather than being newly added.
2. A canonical-owner L2 state transition can self-classify as a
   single-component quick bug and bypass the mechanical Pre-Claim Gate while
   the product/specification reason for that transition remains unchecked.
3. A true local typo whose value originates and terminates in one function,
   with negative history/same-pattern/config/contract/spec evidence and a
   passing variant counterfactual, should remain in the cheap quick lane.

Therefore the repair must distinguish `root` from `proximate` and
`contributing` causes. A green local intervention proves effectiveness at that
point; it does not by itself prove that the recurrence generator is closed.

## Approved Minimal Design

Keep `skills/systematic-debugging/root-cause-claim-contract.md` as the sole
deep causal-proof owner. Do not create a new skill or reference file.

Add a falsifiable `Deeper Cause Challenge` before a non-trivial root claim:

- identify the claimed cause and its causal role;
- identify the upstream generator and recurrence path;
- state the counterfactual intervention;
- actively generate at least one plausible deeper candidate;
- reject that candidate with evidence, not omission;
- classify status as `root`, `proximate`, `contributing`,
  `deepest-confirmed-root-unknown`, or `external-terminal`.

A `root` claim is allowed only when the upstream generator is accounted for,
the recurrence path is closed, the counterfactual eliminates the relevant bug
class, a plausible deeper candidate has been rejected with evidence, and the
topology/anti-disguise proof passes. If evidence ends before that point, use
`deepest-confirmed-root-unknown`; do not relabel the deepest observed mechanism
as root.

Preserve a lightweight quick lane through an explicit negative proof. It may
skip the full card only when evidence shows all of the following:

- the bad value/state originates and terminates at the canonical local owner;
- no upstream producer, configuration, default, contract, policy, or spec
  dependency can generate the bug class;
- history and same-pattern searches are negative;
- a variant counterfactual eliminates the bug class, not just the observed
  sample.

Keep the main `SKILL.md` compact. It should only strengthen the stop sentence,
add the direct read trigger for an unexcluded upstream producer/config/default/
contract/spec dependency, and route open recurrence/proximate/unknown closeout
signals. Detailed fields remain in the causal-proof owner.

## Planned File Changes

1. `tests/e2e/debugging-patch-shape-gate-check.sh`
   - Add static contract assertions for the deeper-cause challenge, quick-exit
     proof, causal status, open recurrence signal, and new H/D closeout checks.
2. `tests/e2e/fixtures/workflow-quality-matrix.json`
   - Add two premature-root positive cases and one true-local negative control.
   - Correct the stale topology fixture: the two independently sufficient
     active paths are an `independent-compound` candidate before anti-disguise
     collapse, not a `conjunctive-cluster`.
3. `tests/helpers/validate_workflow_quality_matrix.py`
   - Validate the new deeper-cause and quick-exit evidence fields.
   - Replace independent-compound `necessity` assertions with same-incident,
     per-root path, independence, and shared-upstream proof.
4. `docs/current/AEGIS_PROCESS_BASELINE.md`
   - Replace self-judged `DeeperCause = no` semantics with falsifiable generator,
     recurrence, deeper-candidate, and causal-status evidence.
5. `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`
   - Add the compact deeper-cause/quick-exit contract and acceptance behavior.
6. `skills/systematic-debugging/root-cause-claim-contract.md`
   - Own the full `Deeper Cause Challenge`, quick-exit proof, and status rules.
7. `skills/systematic-debugging/SKILL.md`
   - Add only direct trigger/stop routing while staying at or below 10,000
     bytes.
8. `skills/systematic-debugging/advanced-debugging-governance.md`
   - Add countable H/D closeout signals for open recurrence or unsupported root
     status; fix topology-specific compound proof wording.

## Required RED Baseline

Before editing the skill or current baselines, first add the new assertions and
behavior cases, then run:

```bash
bash tests/e2e/debugging-patch-shape-gate-check.sh
python3 tests/helpers/validate_workflow_quality_matrix.py \
  tests/e2e/fixtures/workflow-quality-matrix.json
```

Expected result at this point: failure because the repository contract does not
yet contain the new challenge/quick-exit/status behavior. Preserve the bounded
failure output in `90-evidence.md`; do not change assertions to accommodate the
old behavior.

## Post-Change Verification

Run the smallest checks first, then the repository-level regressions:

```bash
bash tests/e2e/debugging-patch-shape-gate-check.sh
python3 tests/helpers/validate_workflow_quality_matrix.py \
  tests/e2e/fixtures/workflow-quality-matrix.json
bash tests/e2e/workflow-quality-check.sh
bash tests/e2e/context-budget-check.sh
bash tests/e2e/boundary-compliance-check.sh
python3 tests/helpers/test_parse_codex_skills.py
bash tests/e2e/layer1-fast-check.sh --host-profile none
git diff --check
```

Acceptance constraints:

- `skills/systematic-debugging/SKILL.md <= 10000` bytes;
- debugging and verification main skills combined `<= 17000` bytes;
- scenarios A/B cannot claim root while the upstream generator/spec cause is
  open;
- scenario C stays quick and does not require the full Pre-Claim card;
- no new runtime authority, skill owner, host-distribution behavior, release,
  tag, or `main` update;
- repair and retirement tracks are explicit, including removal of stale
  self-judged stop and wrong independent-compound necessity wording.

## Cross-Device Resume Commands

```bash
git fetch origin
git switch --track origin/wip/deeper-cause-proof-20260730
python3 scripts/aegis-workspace.py check --root .
git status --short --branch
git rev-parse HEAD
```

Then read, in order:

1. this file;
2. `10-intent.md` and `90-evidence.md` in the same directory;
3. `docs/current/README.md`;
4. `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`;
5. `docs/current/AEGIS_PROCESS_BASELINE.md`;
6. `docs/current/AEGIS_WORKFLOW_QUALITY_BASELINE.md`;
7. the three files under `skills/systematic-debugging/` named in the plan.

Verify the fetched branch and commit before editing. Do not merge, rebase onto,
push, or publish `main` during this WIP continuation. Complete and verify the
task on the WIP branch first; publishing to the default branch remains a later,
separately authorized action.
