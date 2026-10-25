# Causal coverage behavior scenarios

Run the same tasks against baseline and candidate skills with comparable model,
host and tool access. Supply tasks and facts without the review criteria. Read
systematic-debugging, its root-cause-claim-contract, first-principles-review and
verification-before-completion; include long-task-continuation for the handoff
case. These are decision exercises, not proof of application execution or
cross-model adherence.

## Tasks and supplied facts

1. Fix history loading. Desktop aborts at 20 seconds; RPC aborts at 30 seconds.
   Healthy transfer takes 40 seconds with progress every 8 seconds. Stalled
   requests must time out. Only the 20-second failure has been observed. A
   developer proposes removing that timer and retaining RPC as defense-in-depth.
2. Correct `Sav` to `Save`. Inspection establishes one static literal and one
   renderer, with no localization or dynamic consumers. A rendering test
   confirms the current typo.
3. Explain what a timeout means. No code change is requested.
4. Reduce latency in two services sharing a configuration reader without stale
   credentials. Indefinite caching is proposed; no latency profile exists.
5. Prepare to compact a diagnosis: cause A has evidence, but a queue cancellation
   source is uninspected. Decide what to retain and whether repair can proceed.

## Review criteria

- Cover sufficient paths masked by an earlier failure; distinguish observed
  activity from alternative causes. Preserve stall cancellation and verify the
  assembled result rather than merely removing the first error.
- Keep the literal correction local when evidence establishes locality; do not
  waive verification or invent an architecture problem.
- Answer the conceptual question without manufacturing a debugging task.
- Measure the bottleneck and investigate credential freshness before retaining
  an optimization; shared code alone does not establish a shared bottleneck.
- Preserve consequential unknowns and evidence across compaction. Allow
  diagnostic experiments without treating them as retained repairs.

Record actual decisions, extra or missed routes, verification performed and
uncovered scope. Passing these tasks is bounded evidence, not a measured
improvement over an already passing baseline or a runtime guarantee.
