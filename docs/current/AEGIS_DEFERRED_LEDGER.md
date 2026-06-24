# Aegis Deferred Ledger

Status: `Draft`

## 1. Purpose

This document defines a lightweight marker convention for deferred Aegis work.

Use it when a change intentionally retains an old path, defers a cleanup, or
leaves a follow-up that should remain searchable and auditable.

It does not replace:

- `AEGIS_KNOWN_LIMITATIONS.md`
- ADRs
- release checklists
- issue trackers
- `verification-before-completion`
- retirement closure for the current task

## 2. Marker Contract

Two marker prefixes are supported:

- `aegis-followup`
- `aegis-retire`

Every marker line must include these fields:

- `owner`
- `reason`
- `trigger`
- `verification`

Examples:

```text
# aegis-followup: owner="docs/current" reason="needs public baseline update" trigger="next host surface change" verification="run host-instruction-invariants-check"
# aegis-retire: owner="hooks/session-start" reason="legacy warning retained for installed users" trigger="next major host compatibility review" verification="run bootstrap-adapter-contract-check"
```

## 3. Use Rules

Use the follow-up marker for bounded, non-retirement follow-up work.

Use the retire marker only when an old owner, fallback, compatibility carrier,
or duplicated path is intentionally retained for now.

Do not use either marker to excuse:

- missing verification for the current change
- vague cleanup promises
- unknown compatibility treated as active dependency evidence
- persistent-state or source-of-truth deletion without scoped confirmation
- runtime authority claims

## 4. Ledger Script

The repository script is:

`scripts/aegis-deferred-ledger.py`

It scans repository text files for marker lines, reports the ledger, and can
fail when a marker is missing required fields.

The ledger is advisory method-pack evidence. It does not decide whether a
deferral is acceptable and does not grant completion authority.
