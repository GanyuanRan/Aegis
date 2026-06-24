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
