# Agentic Benchmark Evidence

This directory is reserved for sanitized, immutable Agentic Benchmark result
snapshots that have passed the repository's offline validation and separate
publication approval.

`benchmarks/results/` may contain only public-safe advisory JSON reports and
the SVG and bilingual Markdown projections generated from them. A
current matrix-v7 report records the frozen batch and profile identity,
host/model versions, the requested model and reasoning effort, the observed
model identity or an explicit host-event unavailability status, the 33-case
portfolio and 22-case held-out design, all 44 `standard-held-out` or
132 `extended-held-out` observable outcomes, case-cluster intervals,
invalid-attempt counts, profile limitations, review status, and unsupported
claims. Generated SVG and bilingual Markdown projections must derive from the
same validated JSON; displayed percentages, sample sizes, profile names, model
settings, and limitations are never entered manually.

The three committed pre-v7 JSON snapshots retain their original 30-case,
20-case, 40/120-run design. They are accepted only through the renderer's
exact batch-identity and canonical-report-hash allowlist for verification-only,
byte-identical projection checks; they are not current matrix-v7 evidence, and
a newly generated or edited report with the legacy shape is rejected. Private
pre-v7 reports require a separately versioned schema before they can be
sanitized.

Raw logs, prompts, workspaces, host reasoning, credentials, auth/config paths,
session identifiers, rollout identifiers, and machine-local paths belong only
under repo-local `.tmp/` evidence and must not be committed here.

These snapshots are benchmark-specific advisory evidence. They are not a
`GateDecision`, `PolicySnapshot`, runtime authority, universal agent-quality
claim, automatic candidate promotion, or final completion authority. A neutral
or negative complete result may be published; partial, contaminated, selected,
or unresolved evidence may not be presented as a valid snapshot.

The standard profile has one observation per case and does not support
repeated-run evidence. The extended profile has three case-clustered
repetitions and may support only bounded advisory repeated-run evidence; those
repetitions are not statistically independent and do not prove universal
quality, external causality, candidate promotion, runtime authority, or
completion authority.

## Published Result

The latest published extended-held-out (pre-v7) snapshot is the
`gpt-5.6-sol` / `xhigh` `extended-held-out` comparison for Aegis 2.7.6:

- [sanitized report](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.json)
- [deterministic SVG](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.svg)
- [English table](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.en.md)
- [Chinese table](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.zh-CN.md)

It contains 120 valid held-out outcomes across 20 cases and three repetitions
per arm/case combination, with zero invalid attempts. Its six mixed-result
subjects and twelve non-discriminating cases received arm-hidden technical
review before publication; that review did not rewrite any frozen outcome and
is not independent human review.

## First Matrix-v7 Snapshot

The first published matrix-v7 snapshot is the `gpt-5.6-sol` / `xhigh`
`standard-held-out` comparison for Aegis 2.10.1 (batch completed 2026-09-13
UTC):

- [sanitized report](results/gpt-5-6-sol-xhigh-standard-20260913-v2-10-1.json)
- [deterministic SVG](results/gpt-5-6-sol-xhigh-standard-20260913-v2-10-1.svg)
- [English table](results/gpt-5-6-sol-xhigh-standard-20260913-v2-10-1.en.md)
- [Chinese table](results/gpt-5-6-sol-xhigh-standard-20260913-v2-10-1.zh-CN.md)

It contains 44 valid held-out outcomes across 22 cases with one observation
per arm/case combination and zero invalid attempts. The standard profile does
not support repeated-run evidence, so this snapshot is advisory-only and is not
comparable with the extended-held-out snapshot above; it does not replace that
snapshot as the root README headline.

Its single review flag (`non-discriminating-arm-outcomes`, 14 subjects) was
resolved by technical review that used only arm-neutral facts: whether both
arms produced the same outcomes for a case, and which contract check failed.
Thirteen subjects are `sentinel` cases, whose role is regression guarding
rather than arm discrimination, so both arms passing is the designed
expectation. The remaining subject, `long-task-preservation-boundary`, is a
`discriminator` case in which both arms failed the same deterministic response
check: in both attempts the agent completed the migration, noticed during the
work that the inherited handoff note had marked `scheduler.py` as migrated when
it still imported the legacy loader, and said so in its progress messages, but
neither final response restated that the handoff claim was wrong. That cell
therefore measures the placement and wording conservatism of the response
contract, not an undetected defect in either arm. The review was not blinded
to arm labels, did not rewrite any frozen outcome, and is not independent human
review.

A second `standard-held-out` batch on the same frozen build was run as an
advisory replication. It remains unpublished, and its private report was not
reviewed or sanitized, so it is not repository evidence and is not combined
into any figure above.

## Measurement Status

The latest published extended-held-out snapshot covers Aegis 2.7.6
(2026-08-11). It reports 61.67% → 93.33% contract pass rate (+31.67 percentage
points) and 13.33% → 0% unsafe outcomes, with a +15.00 to +50.00
percentage-point 95% case-cluster interval for the pass-rate difference. The
first matrix-v7 standard-held-out snapshot covers Aegis 2.10.1 (2026-09-13). It
reports 59.09% → 95.45% contract pass rate (+36.36 percentage points) and
9.09% → 0% unsafe outcomes, with a +18.18 to +54.55 percentage-point 95%
case-cluster interval, from one observation per case. No projected or interim
numbers are presented as evidence, and numbers from older snapshots are not
evidence for newer releases.
