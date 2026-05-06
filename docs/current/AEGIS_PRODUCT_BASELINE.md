# Aegis Product Baseline

Status: `Approved`

## 1. Document Scope

This document defines the product baseline for the current `Aegis` repository.

This document is only responsible for answering the following questions:

- What product is this repository
- What role does this repository play in the overall `Aegis` roadmap
- What role does this repository NOT play
- How should this repository evolve going forward without boundary drift

This document is NOT responsible for answering the following questions:

- How to write individual skills
- Node-level contracts of the runtime core
- Host-specific details of adapters

---

## 2. Bottom Line Up Front

The formal product definition of this repository is:

> `Aegis Method Pack (runtime-ready)`

The strengths this repository inherits from `superpowers` are:

- Skills distribution model
- Multi-host installation and instruction skeleton
- Workflow triggering mechanisms
- Methodology composability
- Distributable capability via plugin / marketplace / repo-install methods

The new core directions added by this repository are:

- Crystallizing `Aegis` governance-style processes into an installable method layer
- Converging the high-value concepts of ADD into runtime-ready artifacts and boundary contracts
- Enabling different hosts to first "work like Aegis," then later connect to an independent runtime core

---

## 3. What This Repository Is Responsible For

This repository is responsible for the following four categories:

### 3.1 Method Pack

- Skills
- Initial instructions
- Workflow packs
- Review / verification / planning discipline
- Evidence capture conventions

### 3.2 Distribution Layer

- Installation instructions for Codex / OpenCode / other hosts
- Plugin / marketplace / symlink or junction instructions
- File organization compatible with host discovery mechanisms
- Preserving installable properties for all AI coding tools that support plugins

### 3.3 Governance Projection Layer

- `TaskIntent` draft template
- `ImpactStatement` draft template
- `EvidenceBundle` checklist and naming conventions
- Minimal structured prompts for `Gate input`
- Risk summaries and next-step suggestions for host-facing output

### 3.4 Baseline Docs for Method Layer

- This repository's own authority docs
- Method layer baseline
- Boundary documentation with the future runtime core

---

## 4. What This Repository Is NOT Responsible For

This repository must NOT assume the following authoritative responsibilities:

- `Baseline Registry`
- Final resolution of `ADR / policy snapshot`
- Authoritative adjudication of `GateDecision`
- Final determination of `evidence sufficiency`
- Granting or withholding of `completion authority`
- Final classification of defect / drift / corrosion
- Cross-session governance archive / fact chain

These capabilities are only permitted to exist in a future independent `Aegis Runtime Core`.

---

## 5. Relationship With the Overall Aegis Roadmap

The currently recommended overall product shape is:

- `Aegis Method Pack`
- `Aegis Runtime Core`
- `Aegis Host Adapters`

This repository corresponds only to the first item.

This means:

- This repository can rapidly spread to multiple hosts first
- This repository can converge process discipline first
- This repository can reserve contracts for the future runtime core
- This repository must NOT claim to already possess full governance authority simply because it has more docs or stronger skills

---

## 6. Relationship With Upstream superpowers

The relationship between this repository and upstream is defined as follows:

- Inherited: skills distribution model, workflow skeleton, multi-host usage skeleton
- Inherited: plugin-installable method layer distribution capability
- Differentiated: governance-style processes, evidence-driven constraints, runtime-ready boundary, Aegis branding
- Not pursued: back-porting fork-specific product positioning and runtime-ready boundaries to upstream

This repository should be regarded as an independent product line, not "a superpowers mirror with a few rule tweaks."

---

## 7. Evolution Strategy for the Current Phase

The current phase adopts the following convergence order:

### Phase 1: Baseline First

- Establish the authority map first
- Establish the product baseline, process baseline, and boundary baseline first
- All subsequent skill modifications shall be guided by these documents

### Phase 2: Process Upgrade

- Enhance key skills without disrupting the existing distribution skeleton
- Focus on strengthening framing, debugging, verification, planning, and review

### Phase 3: Runtime-ready Projection

- Finalize artifact shapes for the future runtime core
- Form stable method-pack output contracts

### Phase 4: Repo Split

- After the single-repo method layer stabilizes, split out independent runtime core and adapters

---

## 8. Drift Signals

When any of the following phenomena appear, the product boundary should be considered as drifting:

- This repository begins directly claiming `completion authority` in docs or skills
- `GateDecision` is written as a local final adjudication logic within this repository
- Host-side output is misrepresented as authoritative truth
- In order to accommodate the runtime core, this repository begins merging method pack, adapter, and authority core back into a single monolithic structure
- This repository loses its plugin-installable property, or can only be installed and used on a single host

---

## 9. Current Constraints

All subsequent documentation and implementation in this repository must satisfy the following constraints:

- Build the method layer first; do not masquerade as the authority layer
- Finalize the baseline first, then change process implementations
- Converge artifact contracts first, then connect to the runtime core
- All "more powerful" enhancements must proceed under clear boundary conditions
