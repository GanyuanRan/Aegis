# Agentic Benchmark Evidence

This directory is reserved for sanitized, immutable Agentic Benchmark result
snapshots that have passed the repository's offline validation and separate
publication approval.

`benchmarks/results/` may contain only public-safe advisory JSON reports. A
valid report records the frozen batch and profile identity, host/model versions,
the 30-case portfolio and 20-case held-out design, all 40 `standard-held-out`
or 120 `extended-held-out` observable outcomes, case-cluster intervals,
invalid-attempt counts, profile limitations, review status, and unsupported
claims. Generated SVG and bilingual Markdown projections must derive from the
same validated JSON; displayed percentages, sample sizes, profile names, and
limitations are never entered manually.

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

No result is currently published by this harness implementation change.
