# Aegis Target State

Status: `Approved`

## 1. Purpose of This Document

This document is a one-page summary of the current target state for `Aegis`.

It answers only three questions:

- What should this repository ultimately become
- What will the overall `Aegis` evolve into in the long term
- What is explicitly out of scope for the current phase

If you need details, refer to the corresponding authoritative docs:

- Product positioning: `docs/current/AEGIS_PRODUCT_BASELINE.md`
- Method process: `docs/current/AEGIS_PROCESS_BASELINE.md`
- Boundary constraints: `docs/current/AEGIS_RUNTIME_READY_BOUNDARY.md`

---

## 2. One-Sentence Conclusion

The target state of this repository is not a complete platform, but rather:

> `Aegis Method Pack (runtime-ready)`

In other words, this repository is ultimately meant to become:

- A method layer product that integrates `ADD + TLREF + Dual-Track Governance`
- Retaining the `superpowers` distribution skeleton and plugin-installable capability
- Capable of cross-host installation and operation
- Capable of stably producing runtime-ready drafts / hints / projections
- Without overstepping into runtime authority

---

## 3. Ultimate Target State of This Repository

When this repository reaches its target state, it should simultaneously satisfy the following conditions:

1. It is a clearly defined `Aegis Method Pack`
2. It retains from `superpowers`:
   - Skills distribution model
   - Workflow triggering skeleton
   - Multi-host installation skeleton
   - Plugin / marketplace / repo-install distribution capability
3. It builds in `Aegis` qualities:
   - Evidence-driven working style
   - Architecture-first impact analysis
   - TLREF / DIVE / Reflection / QA
   - Repair Track + Retirement Track dual-track governance
4. It can stably produce:
   - `TaskIntentDraft`
   - `BaselineReadSetHint`
   - `ImpactStatementDraft`
   - `EvidenceBundleDraft`
   - `GateInputPack`
   - `SubagentContextPacket`
   - `TodoCheckpointDraft`
   - `ResumeStateHint`
   - `DriftCheckDraft`
5. It remains only:
   - `runtime-ready`
   - `advisory-first`
   - `authority-constrained`

---

## 4. Long-Term Target State of Overall Aegis

The long-term shape of overall `Aegis` is not a single repository, but a three-layer system:

1. `Aegis Method Pack`
2. `Aegis Host Adapters`
3. `Aegis Runtime Core`

The division of responsibilities across the three layers is as follows:

- `Method Pack`
  - Responsible for skills, workflow discipline, runtime-ready artifacts
- `Host Adapters`
  - Responsible for mapping host context into unified governance input, then projecting results back to the host
- `Runtime Core`
  - Responsible for baseline truth, policy snapshot, authoritative impact analysis, gate decision, evidence sufficiency, completion authority

This repository corresponds only to the first layer, not the latter two.

---

## 5. Completion Criteria for the Current Phase

For this repository, "target state achieved" is not an empty phrase — at minimum the following must be observable:

1. Authority docs are complete
2. TLREF has formally entered the method layer baseline
3. Dual-track governance has entered current docs and workflow
4. Runtime-ready artifact schemas have been finalized
5. The first batch of high-leverage skills have completed process upgrade
6. Plugin-installable capability still holds
7. This repository still has not overstepped by claiming to be a runtime core

---

## 6. What Is Explicitly Out of Scope for the Current Phase

To avoid going off course, the following are explicitly out of scope for the current phase:

- Do not write this repository as a complete `Aegis Platform`
- Do not implement authoritative `GateDecision` in this repository
- Do not grant `completion authority` in this repository
- Do not break plugin-installable capability in pursuit of governance enhancements
- Do not elevate host-specific logic backward into the method-pack baseline
- Do not merge method pack, adapters, and runtime core back into a single-repo same-layer structure

---

## 7. Current Development Direction and Productization Sequence

The correct development direction at present is:

1. First strengthen this repository into a `Method Pack (runtime-ready)`
2. First finalize the baseline, process, and artifact contracts
3. Then progressively upgrade high-leverage skills
4. First complete the open-source release baseline for the method pack and non-live rollout strengthening work
5. Only then proceed to adapter-facing contracts
6. Only finally proceed to independent construction of runtime core / adapters

The recommended productization sequence is:

1. First make `Aegis Method Pack` a stable method pack that is open-sourceable, distributable, and cross-host installable
2. First use real user feedback, real task samples, and open-source reception to validate whether it is worth continuing to grow into a complete platform
3. If the method pack proves to have sustained value in real usage, then proceed to independent construction of the full `Aegis`
4. At that point, `OpenCode + installed Aegis Method Pack` can serve as one of the priority host shell candidates for carrying future host-side secondary development optimization

The key boundaries here are:

- `OpenCode` may be a host shell candidate in the future, but it is not the authority source for this repository
- `Aegis Method Pack` can stand independently first, without the runtime core being landed as a prerequisite
- Full platform construction must occur after the method pack's value has been validated, not the other way around by preemptively over-implementing

In one sentence:

> First enable different hosts to "work like Aegis," then let a future independent runtime core become the true authority.
