# Agentic Benchmark Evidence

This directory is reserved for sanitized, immutable Agentic Benchmark result
snapshots that have passed the repository's offline validation and separate
publication approval.

`benchmarks/results/` may contain only public-safe advisory JSON reports. A
valid report records the frozen batch and profile identity, host/model versions,
the requested model and reasoning effort, the observed model identity or an
explicit host-event unavailability status, the 33-case portfolio and 22-case
held-out design, all 44 `standard-held-out` or 132 `extended-held-out`
observable outcomes, case-cluster intervals, invalid-attempt counts, profile
limitations, review status, and unsupported claims. Generated SVG and bilingual
Markdown projections must derive from the same validated JSON; displayed
percentages, sample sizes, profile names, model settings, and limitations are
never entered manually.

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

The current public snapshot is the `gpt-5.6-sol` / `xhigh`
`extended-held-out` comparison for Aegis 2.7.6:

- [sanitized report](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.json)
- [deterministic SVG](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.svg)
- [English table](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.en.md)
- [Chinese table](results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6.zh-CN.md)

It contains 120 valid held-out outcomes across 20 cases and three repetitions
per arm/case combination, with zero invalid attempts. Its six mixed-result
subjects and twelve non-discriminating cases received arm-hidden technical
review before publication; that review did not rewrite any frozen outcome and
is not independent human review.

## Measurement Status

The current snapshot covers Aegis 2.7.6 (2026-08-11). It reports 61.67% →
93.33% contract pass rate (+31.67 percentage points) and 13.33% → 0% unsafe
outcomes, with a +15.00 to +50.00 percentage-point 95% case-cluster interval for the
pass-rate difference. No projected or interim numbers are presented as
evidence, and numbers from older snapshots are not evidence for newer releases.
