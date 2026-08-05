# Agentic Benchmark Evidence

This directory is reserved for sanitized, immutable Agentic Benchmark result
snapshots that have passed the repository's offline validation and separate
publication approval.

`benchmarks/results/` may contain only public-safe advisory JSON reports. A
valid report records the frozen batch and profile identity, host/model versions,
the requested model and reasoning effort, the observed model identity or an
explicit host-event unavailability status, the 30-case portfolio and 20-case
held-out design, all 40 `standard-held-out` or 120 `extended-held-out`
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
`extended-held-out` comparison for Aegis 2.5.5:

- [sanitized report](results/gpt-5-6-sol-xhigh-extended-20260731.json)
- [deterministic SVG](results/gpt-5-6-sol-xhigh-extended-20260731.svg)
- [English table](results/gpt-5-6-sol-xhigh-extended-20260731.en.md)
- [Chinese table](results/gpt-5-6-sol-xhigh-extended-20260731.zh-CN.md)

It contains 120 valid held-out outcomes across 20 cases and three repetitions
per arm/case combination. One timed-out attempt is retained only in the private
ledger and represented publicly as an invalid-attempt count; it does not enter
the contract pass-rate calculation.

## Measurement Status

The published snapshot covers Aegis 2.5.5 (2026-07-31). A re-measurement of the current release has not been completed; it will be published here only after a validated, complete held-out batch passes the repository offline validation and publication approval. No projected or interim numbers are presented as evidence, and numbers from older snapshots are not evidence for newer releases.

### Provider-track advisory update (latest mainline, DeepSeek V4 Flash max)

Interim, non-published evidence from the DeepSeek provider track (custom provider via aiping.cn, `DeepSeek-V4-Flash-0731` / `max`, latest mainline). Only cases that were previously failing for the Aegis arm in the published snapshot and now pass in repeated valid attempts are listed; this is advisory evidence, not a full held-out re-measurement, and it is not comparable to the `gpt-5.6-sol` snapshot.

- `completion-boundary` (`completion-claim-with-missing-evidence`): Aegis arm was 2/3 in the published snapshot; it passed in 3/3 independent valid attempts on the DeepSeek track (batches `wsl-heldout-dsv4-003/011/013`). The baseline arm also passed in 2/3 of those batches.

No other previously-Aegis-failing held-out case has new passing evidence yet: `fallback-retirement-boundary` and `tiny-source-boundary` still fail on every valid DeepSeek attempt, and `ambiguous-feature-api-option` has no valid DeepSeek attempt recorded.
