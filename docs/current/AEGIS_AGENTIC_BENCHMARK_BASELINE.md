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

The version 4 matrix maps every minimum scenario class to three distinct
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
3. `opt-in-live-held-out` is implemented and remains explicit opt-in outside
   default CI. It contains matrix-owned development, standard held-out, and
   extended held-out profiles. This status describes the offline-verified
   harness, not live result evidence.
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

### 7.3 P1 Case Portfolio And Fair-Scoring Contract

Matrix version 4 reserves one concrete portfolio manifest at:

`tests/e2e/fixtures/agentic-benchmark-cases.json`

The target portfolio contains exactly 30 cases: one development, one held-out
normal, and one held-out boundary case for each of the ten required scenario
classes. The manifest owns only that concrete portfolio. It does not own
repetitions, attempt ceilings, concurrency, or time budgets.

The matrix is the only exact run-shape owner. It defines these profiles:

| Profile | Cases | Repetitions | Valid target | Attempt ceiling | Workers | Wall budget | Publication |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `development-pilot` | 1 development | 1 | 2 | 2 | 2 | 300 seconds | disabled |
| `standard-held-out` | all 20 held-out | 1 | 40 | 44 | 8 | 2700 seconds | advisory; `repeated-run-evidence` unsupported |
| `extended-held-out` | all 20 held-out | 3 | 120 | 132 | 8 | 2700 seconds | advisory repeated-run evidence |

Every profile uses both live comparison arms, a 30-second provider preflight,
a 240-second per-attempt timeout, and an infrastructure failure limit of two
completed attempts in a wave. The maximum supported worker count is 12. An
incomplete batch must not feed public benchmark claims.

The profile wall-clock budget is an end-to-end active-run ceiling. It includes
isolation and setup, provider preflight, paired canary and fan-out, plus each
attempt's Codex execution, parsing, scoring and artifact cleanup. Reservations
are persisted before work starts, resume cannot reset consumed time, and no
ledger may record cumulative wall time above the selected profile ceiling.
The same ceiling also includes bounded control-file bootstrap, validation,
authentication freeze, report persistence, summary output and authentication
close. Before active child work starts, `activeInvocation` fsyncs a reservation
for all remaining time. An interrupted active invocation consumes that complete
reservation on the next start and requires a new batch; restart is not a way to
regain wall-clock budget. The active child may checkpoint total elapsed time
after authentication close and summary output, but it cannot delete the
reservation. Only the outer supervisor may settle it after a zero exit and a
clean reap of the whole child tree. Timeout or any nonzero exit retains the
reservation while a remaining-budget cleanup attempts to purge untrusted
attempt artifacts.

The preflight proves only that Codex returned a sanitized, non-empty catalog,
that the requested model was present, and that no visible refresh failure was
reported. It does not independently prove provider reachability when an
upstream client silently serves cached metadata. The paired real-attempt canary
is the transport truth before wider fan-out.

The standard profile preserves held-out case coverage while bounding normal
user wait, but one observation per case cannot support repeated-run stability,
within-case variance, or `repeated-run-evidence` claims. The extended profile
adds three repetitions per case and may provide advisory repeated-run evidence,
but it still cannot prove universal quality, external causality, candidate
promotion, runtime authority, or completion authority.

Held-out scoring must be arm-neutral and observable-outcome based. The same
contract applies to both arms. Source-edit cases inspect the resulting
workspace, git diff, fixture-owned tests and response/event evidence. Advisory
or no-edit cases inspect worktree preservation, forbidden actions, response
claims and event order. Aegis skill names, routes, artifact names, or semantic
aliases may be diagnostic attribution only; they cannot make a task pass and
must not be required from the no-Aegis arm.

Verification commands may optionally declare `immutableArgPaths`. Each
declared path must be a normalized, project-relative regular seed file, appear
exactly once as a complete `argv` token, and not overlap
`forbiddenChangedPaths`. Contract validation must reject missing, duplicate,
escaping, symlinked, hard-linked, special-file, or otherwise ambiguous inputs.
Commands without `immutableArgPaths` retain their existing behavior.

An affected editable-test case is a current portfolio case whose editable
verification file is declared by a non-empty `immutableArgPaths`. Each
immutable command in such a case is paired with one ordinary final-workspace
command that preserves the original `argv` tokens, `expectedExit`, and
`timeoutSeconds` but omits `immutableArgPaths`. Immutable execution rewrites
only the declared exact `argv` token or tokens; ordinary execution does not.
The scorer derives immutable files from the outcome contract's sibling frozen
`project/`, mounts only the declared files read-only, and keeps the final
workspace as the implementation and import source. Verification preserves
network isolation and never mutates that workspace. The runner gains no
verification-policy responsibility.

Semantic intent tags are assistant-authored only. Command events may retain
structured objective evidence, such as a bounded `rg` or `grep` dependency
check, but arbitrary output, stderr, or file content cannot create semantic
intent. Fixed-key sandbox-failure classification remains a separate
infrastructure concern and cannot create a passing semantic tag.

The concrete portfolio, outcome scorer, isolated repeated runner, aggregation
and report projection are implemented and pass their focused offline gates.
Harness implementation is not live benchmark evidence: no result exists until
an explicitly authorized, complete held-out batch is executed and reviewed.

The repeated runner entrypoint is `tests/e2e/run-agentic-benchmark.sh`. The
profile contract requires its offline path to freeze the matrix-selected shape,
manifest, prompts, project trees, outcome contracts, evaluated method-pack
snapshot, harness code, model/tool policy and deterministic run order. Attempts
must execute batch-local frozen copies and revalidate them before each launch
and final aggregation. A dry-run must refuse to replace an existing batch, and
credential-shaped output must make an attempt invalid without entering
preserved logs. Real execution remains explicitly opt-in. It must preserve
every paid attempt, retry only infrastructure-invalid attempts within the
selected profile ceiling, aggregate by case cluster, and leave partial or
unresolved reports unknown. These runner capabilities do not change the tier
status or create public benchmark evidence before the separate report
projection gate passes.

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

## 10. Repeated Held-Out Isolation And Publication Boundary

The repeated held-out path must fail closed unless both arms receive the same
prompt, seeded project, host, model, timeout and tool policy in fresh workspaces.
The no-Aegis arm must prove that injected Aegis instructions, skills and plugins
are absent. The Aegis arm may mount only a distribution-shaped snapshot of the
evaluated method pack; benchmark prompts, scorers and expected outcomes must be
outside the agent-visible filesystem. Authentication may be made available
read-only through the host's supported path, but credentials must never enter
fixtures, logs, reports or public artifacts.
Every isolated client subprocess must derive its own offset-zero read-only
open-file description from the sealed authentication snapshot; concurrent or
sequential commands must never rewind or share the source offset. A direct
Codex client must execute the frozen native runtime directly and receive auth
only by opening a private `auth.json` link to the supervising worker's sealed
descriptor path. The descriptor itself must not be inherited by the client; a
package launcher that drops non-stdio descriptors before spawning the native
runtime is not a live client path. The descriptor must not reach agent tool
children. Commands that
still use the audit-only outer `bwrap` may inherit or rewrite only numeric
`--ro-bind-data` sources in the validated bwrap prefix; every payload argument
after the first `--` separator remains opaque to descriptor discovery.

The fixed `codex debug prompt-input` audit is a zero-inference prompt-rendering
check, not a Codex execution or provider preflight. It may use only the frozen,
validated benchmark network policy because supported Codex clients do not
guarantee that prompt rendering completes offline. Its report records only the
sanitized network-policy metadata and keeps `modelCalls` at zero. The separate
mount audit remains in an unshared network namespace, receives no proxy values,
and must be validated independently from the prompt-input transport. Raw proxy
values must not enter audit reports or failure diagnostics. Cross-arm prompt
comparison ignores only the volatile top-level response-item IDs generated by
each prompt-debug invocation and the random suffix of Codex's generated
`~/.codex/tmp/arg0/codex-arg0*` read grant. Role, other content, type and nested
fields remain part of the comparison contract.

Live attempts must not nest Codex's tool sandbox inside the audit-only outer
`bwrap`, because the outer namespace prevents the inner Linux sandbox from
starting. The trusted Codex provider client instead runs with an arm-private
home, workspace and temp directory, while one frozen Codex permission profile
is the canonical agent-tool boundary. That profile must allow reads and writes
only in the case workspace and private temp directory, deny benchmark, scorer,
peer-workspace and authentication reads, deny agent-tool network access, and be
enforced by Codex's native `bwrap`/seccomp backend. The Aegis arm receives a
read-only, distribution-shaped skill projection under its private
`~/.agents/skills`; the baseline arm receives the same profile with no Aegis
projection. Direct projections must use independent regular files rather than
symlinks or hard links: file write bits are removed, directories remain
parent-cleanup-safe, and the permission profile remains the agent write-denial
owner. The original distribution snapshot remains agent-invisible. Both arms
must pass the same zero-inference read/write/denied-read/denied-network probe
before provider inference. The frozen shell-environment policy must also prove that provider
proxy variables are absent from tool children even while the trusted client
uses the validated provider transport. The tool probe must invoke the same
frozen native Codex runtime as live attempts so descriptor hiding cannot pass
merely because a package launcher dropped the FD first.
Legacy Landlock, `danger-full-access`, sandbox bypass and dual-path fallbacks
are not compatibility paths. An attempt with a sandbox failure or no
machine-observed command/edit event is infrastructure-invalid and must never be
scored as an agent outcome.

Batch preparation must freeze content identities for the resolved Codex
launcher, its packaged native runtime, the audit `bwrap`, and the permission
backend `bwrap` resolved from the direct client's frozen `PATH`, then re-check
those identities before execution or resume. Version strings alone are
descriptive metadata, not sufficient evidence that the audited sandbox
implementation is the one used by the live batch. Stored identities contain
only role, digest and size; host paths are not reportable benchmark evidence.

Artifact entry-count and aggregate-size enforcement uses sampled artifact
monitoring plus a terminal confidentiality scrub. A stable over-limit tree is
terminated when observed, but sampling does not guarantee detection of a
transient peak that is created and deleted between polls. The per-file
`RLIMIT_FSIZE` remains a hard kernel-enforced ceiling; the sampled aggregate
monitor and terminal scrub must not be described as hard historical peak
measurement.

Before the first held-out attempt, the matrix, selected profile, portfolio,
prompts, projects, outcome contracts, evaluated method-pack snapshot and run
policy must be frozen and hashed. Semantic changes invalidate the batch.
Infrastructure-invalid attempts remain in an immutable ledger and consume the
selected profile's 44- or 132-attempt ceiling.
An infrastructure-invalid ledger entry must retain exactly one fixed, public-safe
`errorType` from the scheduler-owned allowlist. The code identifies the failed
boundary, such as supervisor output/result handling, host execution/events,
scoring, executor failure or interrupted recovery; it must never contain raw
exceptions, stderr, model output, credentials, proxy values, local paths or
provider text. Unsupported or dynamically derived error types fail closed.

Held-out results aggregate by case. The extended profile must not treat its
three repetitions as three independent tasks. Percentage-point deltas and
confidence intervals must use a deterministic case-cluster method with its seed
recorded. Mixed within-case outcomes, non-discriminating arm results and scorer
unknowns require blinded review or remain explicitly unknown.

Raw logs and workspaces stay under repo-local `.tmp/`. A README publication may
commit only a sanitized, path-independent advisory report plus a deterministic
SVG and exact table projection. The public snapshot must exclude credentials,
absolute local paths, session identifiers, raw reasoning, raw host logs and
unpublished prompt content. A neutral or negative valid result remains
publishable; incomplete, contaminated or hand-selected results do not.

Evidence produced under prior defective outcome or attribution semantics is
frozen diagnostic history and superseded for candidate scoring. It must never
be re-labeled, re-aggregated, or published as repaired evidence.

`tests/helpers/render_agentic_benchmark.py` is the single public projection
owner. It must derive the accepted shape from the frozen profile identifier,
recompute every displayed score from the complete 40-row standard or 120-row
extended held-out result set, validate the corresponding 30/20/40/44 or
30/20/120/132 design and case-cluster interval, then produce a zero-based SVG
and English/Chinese tables from the same sanitized JSON. Standard reports must
display the unsupported `repeated-run-evidence` limitation. The repeated runner
owns private execution and aggregation only; it does not expose a second
sanitizer or renderer path.
