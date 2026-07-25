# Aegis Rule Layering

Status: `Approved`

## 1. Document Scope

This document defines the layered boundaries of the current `Aegis` rule system.

This document is only responsible for answering the following questions:

- Which rules belong to the portable method layer core
- Which rules belong to host / profile preferences
- Which rules belong to the current repository's contribution constraints

---

## 2. Three-Layer Rule Model

### 2.1 Portable Method Rules

Rules suitable for entry into the `Aegis Method Pack` core include:

- TLREF
- DIVE
- Reflection
- QA
- Evidence-Driven
- Dual-Track Governance
- Output Contract

### 2.2 Host / Profile Rules

Rules that should not be directly written into the general method-pack baseline include:

- `sequential-thinking`
- Preferring `serena` / `context7`
- Host-specific tool routing
- Assembly methods unique to a particular plugin platform

These rules should enter:

- Host adapter docs
- Host-specific profile
- Install / usage guide

Bootstrap adapters must stay thin. A host adapter may decide activation mode,
TDD mode, JSON shape, skill discovery path, legacy warnings, and host tool
mapping, but it should source the portable hot path from
`skills/using-aegis/SKILL.md` or a host-native reference to that file. It should
not copy the full skill body into a separate prompt owner, replace
task-specific skills with one large fixed prompt, or grant runtime /
completion authority.

### 2.3 Repo Contribution Rules

Rules that only constrain current repository contributions and local implementation include:

- File length limits
- Naming conventions
- Repository security and commit constraints
- Document placement constraints

These rules should not be automatically elevated to cross-host general methodology.

---

## 3. Current Owners And Manual Projections

The current portable routing owner is `skills/using-aegis/SKILL.md`. Detailed
workflow behavior remains owned by the task-specific skills and approved
current docs. Activation and TDD mode semantics are owned by
`AEGIS_ACTIVATION_MODE.md` and `AEGIS_TDD_MODE.md` respectively.

The root `GLOBAL_USER_RULES_LITE*` and `GLOBAL_USER_RULES_TEMPLATE*` files are
manual host/profile projections. They are not method owners, host adapters, or
proof that Aegis is installed and discoverable. They are not updated by `aegis:update`;
users must re-copy or merge them when a release changes the projected profile
semantics.

These projections may retain stable user-selected preferences such as
authority priority, fast-path behavior, evidence discipline, workspace
laziness, and method-pack authority boundaries. They must not duplicate
volatile workflow protocols, exact skill output shapes, or host-specific tool
routing.

Projection maintenance follows these rules:

- Keep the Lite projection as the default compact option.
- Keep the Advanced projection as an optional stable governance overlay that
  is appended to Lite rather than used as a standalone profile.
- Keep activation, authority priority, fast-path behavior, baseline completion
  evidence, and the method-layer authority boundary owned by Lite. Advanced
  must reference those base rules instead of copying a second version.
- Preserve public filenames and links unless a documented compatibility
  decision authorizes retirement.
- Keep shared semantics aligned across English and Chinese without requiring
  byte-for-byte translation.
- When activation, TDD, routing, priority, verification, or authority semantics
  change, review all four projections and publish a manual-copy migration note.

---

## 4. Design Constraints

Any subsequent rule addition must first answer:

1. Is it portable across hosts
2. Does it depend on specific tool capabilities
3. Does it only serve current repository contributions

Only the first category is permitted to enter the method-pack core.
