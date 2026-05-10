# Aegis Current Docs

Status: `Approved`

## 1. Purpose

This directory contains the public current baseline for `Aegis Method Pack`.

It is intentionally small. Internal implementation records, migration plans,
private smoke notes, cutover checklists, and local-only audit trails do not
belong in this public current surface.

## 2. Repository Boundary

The current repository is:

> `Aegis Method Pack (runtime-ready)`

This repository owns:

- skills and workflow discipline
- host-installable method-pack distribution
- runtime-ready drafts, hints, and projections
- public docs needed by users and contributors

This repository does not own:

- authoritative runtime core
- authoritative `GateDecision`
- authoritative `PolicySnapshot`
- final `completion authority`

## 3. Authority Order

When public docs conflict, use this order:

1. `AGENTS.md`
2. `docs/current/README.md`
3. approved ADRs in `docs/adr/`
4. task-relevant docs in `docs/current/`
5. host-specific docs such as `docs/README.codex.md`,
   `docs/README.opencode.md`, `docs/README.claude-code.md`,
   `docs/README.codebuddy.md`, `docs/README.deepseek-tui.md`, and
   `docs/README.trae.md`
6. tests and fixtures

## 4. Public Current Baseline

The public current set is:

- `docs/current/AEGIS_TARGET_STATE.md`
- `docs/current/AEGIS_PRODUCT_BASELINE.md`
- `docs/current/AEGIS_PROCESS_BASELINE.md`
- `docs/current/AEGIS_ACTIVATION_MODE.md`
- `docs/current/AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`
- `docs/current/AEGIS_RULE_LAYERING.md`
- `docs/current/AEGIS_TRIGGER_HEALTH_BASELINE.md`
- `docs/current/AEGIS_DUAL_TRACK_GOVERNANCE.md`
- `docs/current/AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
- `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`
- `docs/current/AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
- `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
- `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
- `docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md`

## 5. Document Roles

`AEGIS_TARGET_STATE.md`
: One-page summary of what this repository is trying to become.

`AEGIS_PRODUCT_BASELINE.md`
: Product boundary, owned surfaces, and non-goals.

`AEGIS_PROCESS_BASELINE.md`
: Method-layer workflow baseline and evidence discipline.

`AEGIS_ACTIVATION_MODE.md`
: `auto` and `explicit` activation mode semantics.

`AEGIS_PROMPT_HYGIENE_AND_INJECTION_BOUNDARY.md`
: Bounded context intake, evidence indexing, and log/output hygiene.

`AEGIS_RULE_LAYERING.md`
: Method, host, and repo rule layering.

`AEGIS_TRIGGER_HEALTH_BASELINE.md`
: Trigger-chain diagnosis for "installed but not reliably invoking the right
skill", including install, discovery, activation, routing, execution-depth, and
false-positive layers.

`AEGIS_DUAL_TRACK_GOVERNANCE.md`
: Repair track plus retirement track governance.

`AEGIS_ARTIFACT_SCHEMA_BASELINE.md`
: Minimum runtime-ready artifact shapes.

`AEGIS_RUNTIME_READY_BOUNDARY.md`
: What the method pack may output, and what only a future runtime core may decide.

`AEGIS_METHOD_PACK_RELEASE_CHECKLIST.md`
: Minimum release gate and verification readback.

`AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
: Current host compatibility snapshot and evidence boundary.

`AEGIS_KNOWN_LIMITATIONS.md`
: Current limitations and retained compatibility boundaries.

## 6. Local Archive Rule

`docs/archive/` is local-only and ignored by git.

Use it for implementation history, internal migration records, private staging
notes, and old cutover material that should not ship as part of the public
repository.

Do not reference `docs/archive/` from public README files, host install docs, or
release instructions.

## 7. Update Rule

When a change affects public behavior, host installation, release gates,
runtime-ready artifacts, or the method-pack/runtime-core boundary, update the
smallest relevant current doc before changing implementation.

If a document is only useful as process evidence, keep it out of `docs/current`.
