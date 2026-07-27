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
- `trace-digest-coverage`
- `rule-effect-attribution`
- `skill-call-stability`

Cost, time, token count, and diff size may be collected as supporting metrics.
They are not primary success claims for Aegis.

Trace Digest quality is measured only when the scenario asks for auditability or
when release/debug/long-task review requires it. The benchmark should check
whether the trace names execution trace, evidence chain, retrieval chain, rule
effects, skill routing stability, verification coverage, confidence labels,
host capability gaps, and redaction without exposing raw chain-of-thought.

## 4. Required Scenario Classes

The minimum benchmark suite should include:

- ambiguous feature shaping before implementation
- quick bug repair that must surface Change Necessity before source edits
- tiny helper or small guard addition that must surface Change Necessity before
  adding a new source-code path
- shared-owner bug repair instead of caller-side fallback
- completion claim with missing evidence
- fallback or compatibility cleanup with retirement trigger
- fast-path tiny task that must stay cheap
- requested white-box Trace Digest for a non-trivial task
- negative fast-path sample that must not emit Trace Digest ceremony
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

### 7.1 Scenario Coverage Contract

The version 2 matrix maps every minimum scenario class to three distinct
coverage signals:

- `workflowQualityFixtureRefs` names one or more existing deterministic
  workflow-quality fixtures
- `controlledReplaySampleRefs` names zero or more samples in the controlled
  replay manifest
- `liveReplayEligible` states whether the current live replay entrypoint can
  prepare that scenario through a controlled replay sample

These fields describe available verification paths. A fixture reference is not
evidence that a benchmark run passed, an empty controlled replay list is an
explicit coverage gap, and live eligibility is not live execution evidence.

All ten minimum scenario classes have deterministic workflow-quality fixture
references. Current controlled replay and live eligibility are limited to these
exact mappings:

- `quick-bug-change-necessity` -> `change-necessity-before-edit`
- `shared-owner-bug-repair` -> `shared-owner-bug-repair`
- `completion-claim-with-missing-evidence` ->
  `completion-evidence-boundary`

The other seven minimum scenario classes intentionally use empty
`controlledReplaySampleRefs` and set `liveReplayEligible` to `false`. The matrix
and replay manifest must agree bidirectionally on sample ID and scenario class;
validation must reject missing, extra, or mismatched mappings.

### 7.2 Evaluation Tiers And Candidate Comparison

The benchmark contract separates four evidence tiers:

1. `deterministic-static` is implemented and is the default CI tier.
2. `controlled-replay` is implemented for the checked-in captured transcripts.
3. `opt-in-live-repeated-held-out` is contract-only and remains outside default
   CI.
4. `sampled-blind-human-review` is contract-only and is reserved for sampled
   escalation with arm identity hidden from reviewers.

The matrix also defines a conditional `previous-aegis` arm. It is used only
when evaluating a candidate skill or workflow revision against the immediately
previous revision. Current development controlled replay samples must not carry
this arm. It becomes eligible only after a separate candidate-revision metadata
and comparison design is defined.

Candidate promotion remains advisory. It requires held-out evidence, repeated
run evidence, no regression in a primary metric, and review of high-variance
results or non-discriminating assertions. Benchmark output must not
automatically promote a candidate or modify a skill, workflow, or baseline.

## 8. Controlled Replay Samples

Controlled replay samples are the first sample layer below the benchmark
contract. They use seeded fixture projects, the same prompt per arm, and
per-arm temporary workspaces so replay evidence is not taken from local user
projects.

Each current sample declares `evaluationTier=controlled-replay` and
`datasetPartition=development`. A single replay of a checked-in static
transcript does not provide variance, held-out, blind-review, or candidate
promotion evidence.

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

The runner may write a versioned structured advisory report under repo-local
`.tmp/`. That report records contract results and comparison scores from the
static transcript analyzer. Unknown token, cost, variance, held-out, and blind
review evidence must remain explicitly unknown rather than being inferred.

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

The current single-arm live capture is not the contract-only repeated/held-out
tier. It does not provide repeated-run, variance, held-out, or promotion
evidence.

Live capture output is environment-bound benchmark evidence. It is not part of
the default Layer 1 offline gate, does not prove host compatibility on its own,
and does not grant final evidence sufficiency or completion authority.
