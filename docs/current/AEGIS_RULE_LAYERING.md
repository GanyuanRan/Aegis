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

## 3. Layering Conclusion for the Current Master Draft

The root `AGENTS_RULES.md` should currently be regarded as:

> A rule master draft not yet fully de-layered

Subsequent migration principles:

- Methodology core migrates into `docs/current/` and skills
- Host preferences migrate into host-facing docs
- Repository constraints migrate into repo contribution docs

---

## 4. Design Constraints

Any subsequent rule addition must first answer:

1. Is it portable across hosts
2. Does it depend on specific tool capabilities
3. Does it only serve current repository contributions

Only the first category is permitted to enter the method-pack core.
