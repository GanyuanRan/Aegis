# Aegis Domain Language

Canonical language for the Aegis product layers and their authority boundary.
This glossary summarizes terminology; current docs and approved ADRs remain
authoritative.

## Language

**Aegis Method Pack**:
The portable, host-installable method layer that owns skills, workflow
discipline, and advisory runtime-ready outputs.
_Avoid_: Aegis Platform, Runtime Core
_Authority_: docs/current/AEGIS_TARGET_STATE.md; docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md

**Host Adapter**:
A host-specific integration layer that maps host context into governance input
and projects results back without becoming the authority owner.
_Avoid_: Method Pack, Runtime Core
_Authority_: docs/current/AEGIS_TARGET_STATE.md

**Runtime Core**:
The future independent authority layer for baseline truth, policy snapshots,
gate decisions, evidence sufficiency, and completion authority.
_Avoid_: Method Pack, host plugin
_Authority_: docs/current/AEGIS_TARGET_STATE.md; docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md

**runtime-ready artifact**:
An advisory draft, hint, projection, or evidence bundle shaped for possible
future runtime consumption without carrying authoritative decision power.
_Avoid_: final decision, approval, completion grant
_Authority_: docs/current/AEGIS_TARGET_STATE.md; docs/adr/ADR-0001-aegis-method-pack-is-not-runtime-core.md

## Relationships

- The **Aegis Method Pack** can run across hosts without a **Runtime Core**.
- A **Host Adapter** may connect the **Aegis Method Pack** to a future
  **Runtime Core**.
- The **Aegis Method Pack** produces a **runtime-ready artifact**; only an
  authorized future **Runtime Core** may turn suitable input into an
  authoritative runtime decision.
