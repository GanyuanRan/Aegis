# Aegis Agentic Benchmark Baseline

Status: `Draft`

## 1. Purpose

This document defines the public baseline for an Aegis agentic benchmark.

The benchmark exists to measure whether `Aegis Method Pack` guidance improves
real agent behavior in representative tasks without increasing prompt noise or
crossing the runtime authority boundary.

It does not measure:

- final evidence sufficiency
- authoritative routing decisions
- authoritative `GateDecision`
- authoritative `PolicySnapshot`
- final completion authority
- generic per-repository savings claims

## 2. Benchmark Question

The primary question is:

> Does Aegis make representative agent work more evidence-aware, boundary-safe,
> and correctly scoped than the same task without Aegis?

The benchmark should compare at least these arms:

- `baseline-no-aegis`
- `aegis-auto`
- `aegis-explicit`, when the task is about explicit Aegis invocation

Every arm must use the same task prompt, the same seeded repository, and an
isolated workspace and configuration boundary.

## 3. Required Metrics

The benchmark should prioritize governance-quality metrics over code-size
metrics:

- `route-correctness`
- `evidence-freshness`
- `authority-boundary`
- `false-completion-rate`
- `owner-fix-accuracy`
- `retirement-track-coverage`
- `workspace-laziness`
- `prompt-bloat-risk`
- `task-completeness`

Cost, time, token count, and diff size may be collected as supporting metrics.
They are not primary success claims for Aegis.

## 4. Required Scenario Classes

The minimum benchmark suite should include:

- ambiguous feature shaping before implementation
- quick bug repair that must surface Change Necessity before source edits
- shared-owner bug repair instead of caller-side fallback
- completion claim with missing evidence
- fallback or compatibility cleanup with retirement trigger
- fast-path tiny task that must stay cheap
- destructive or source-of-truth cleanup that must stop for confirmation

Each scenario needs:

- a prompt that does not disclose the expected route
- a seeded repository state
- expected positive behavior
- expected negative behavior
- scorer checks or transcript checks
- residual-risk fields in the report

## 5. Isolation Controls

Benchmark runs must prevent contamination between arms:

- use a fresh temporary workspace per run
- isolate host config and plugin directories
- record the effective Aegis installation path and activation mode
- preserve workspaces or transcripts for audit
- make model, host, seed, timeout, and tool restrictions explicit
- run scorer self-tests before trusting scorer output

If a contamination bug is found, the affected result must be marked superseded
or invalidated instead of silently retained.

## 6. Report Boundary

Benchmark reports may say:

- which arm did better on the defined metrics
- which scenarios improved or regressed
- which checks are environment-bound
- which claims are unsupported

Benchmark reports must not say:

- Aegis grants completion authority
- Aegis proves final evidence sufficiency
- a host adapter is fully compatible because one benchmark passed
- Aegis saves a fixed percentage of cost, time, or code on arbitrary projects

## 7. Fixture Owner

The machine-checkable benchmark fixture lives at:

`tests/e2e/fixtures/agentic-benchmark-matrix.json`

The fixture is a design contract for the benchmark harness. It is advisory
method-pack verification, not a runtime gate.

## 8. Controlled Replay Samples

Controlled replay samples are the first sample layer below the benchmark
contract. They use seeded fixture projects, the same prompt per arm, and
per-arm temporary workspaces so replay evidence is not taken from local user
projects.

The replay manifest lives at:

`tests/e2e/fixtures/replay-samples.json`

The replay runner:

- copies each seeded fixture project into a fresh temporary workspace per arm
- initializes an isolated git workspace for replay auditability
- analyzes captured transcripts through `tests/e2e/analyze-transcript.sh`
- checks that the Aegis arm satisfies the behavior contract and scores higher
  than the no-Aegis contrast arm

This layer is benchmark-ready evidence plumbing. It does not run a live host agent.
It does not prove host adapter compatibility, and it does not grant final
evidence sufficiency or completion authority.

## 9. Live Replay Capture

Live replay capture is an opt-in environment-bound path for running a host
against one controlled replay sample arm and then feeding the captured output
back through the transcript analyzer.

The entrypoint is:

`tests/e2e/live-replay-capture.sh`

The live capture path:

- requires `AEGIS_LIVE_REPLAY=1` before invoking a host CLI
- writes raw logs, normalized transcripts, summaries, and metadata under
  repo-local `.tmp/`
- reuses `tests/helpers/codex-cli.sh` and `tests/helpers/claude-cli.sh` for
  host invocation instead of defining a new host adapter
- normalizes raw host output through
  `tests/helpers/normalize_live_replay_log.py`
- currently captures only a single `aegis-auto` arm by default

The live capture path must not fabricate a no-Aegis baseline. A trustworthy
`baseline-no-aegis` live arm requires isolated host configuration and plugin
discovery boundaries, and should be added only when that isolation is explicit.

Live capture output is environment-bound benchmark evidence. It is not part of
the default Layer 1 offline gate, does not prove host compatibility on its own,
and does not grant final evidence sufficiency or completion authority.
