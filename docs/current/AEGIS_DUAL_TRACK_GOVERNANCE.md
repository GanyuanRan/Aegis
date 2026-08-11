# Aegis Dual-Track Governance

Status: `Approved`

## 1. Document Scope

This document defines the currently effective "Repair Track + Retirement Track" dual-track governance rules for `Aegis`.

Ripple Signal Triage uses this document whenever the signal involves an old
owner, duplicate owner, fallback, adapter, legacy path, or retirement boundary.

---

## 2. Applicability Scope

The following types of tasks must be executed under dual-track governance by default:

- Bug fixes
- Architecture refactoring
- Chain governance
- Contract adjustments

---

## 3. Dual-Track Definition

### 3.1 Repair Track

Must answer:

1. True root cause
2. Unique canonical owner
3. Minimum necessary change
4. Compatibility boundary
5. Verification method

### 3.2 Retirement Track

The default behavior of the Retirement Track is to delete old logic; retention requires explicit justification.

Execution order:

1. **Locate**: Where is the current duplicate owner / old fallback / historical patch
2. **Effectiveness Check**: Is it still active on the main chain
   - If already inactive → record that local fact, then continue to step 3
   - If still active → continue to step 3
3. **Boundary Check**: Classify internal code, proven active external
   dependencies, and proven distribution whose consumers cannot be observed
4. **Default Operation**: For internal code or a resolved safe boundary, delete
5. **Exception** (only when verified dependency blockage prevents deletion):
   - Record: retained object, retention reason, observation metrics, retirement timing
   - Re-evaluate during the current slice's Pre-Delivery Review
6. **External-Unknown Hold**: Proven distribution with unobservable consumers
   is neither dependency proof nor safe-deletion proof; inventory read-only and
   require scoped post-disclosure confirmation before editing
7. **Verification**: After deletion, old logic is no longer active and no lingering references remain

---

## 4. Hard Constraints

- It is strictly forbidden to add new code without accounting for the disposition of old logic
- It is strictly forbidden to add new providers / fallbacks / prompt branches / adapters without a corresponding retirement plan
- Redundant code, dead code, inactive fallbacks, and obsolete compatibility layers shall be deleted within the same slice by default unless a stronger external or persistent-state boundary blocks deletion
- Only under verified dependency blockage is retention+recording permitted, and it must be re-evaluated in the Pre-Delivery Review
- Pre-disclosure delete requests do not confirm a later external-unknown risk
- If deletion cannot be performed yet, the following must be recorded: `Retained Object`, `Retention Reason`, `Observation Metrics`, `Retirement Timing`
- When adding a new canonical owner, prefer migrating old logic first, then downgrading the old logic to a compatibility layer

---

## 5. Pre-Delivery Review

Before each slice delivery, the following must be completed:

- Repair Review
  - Whether the root cause was truly eliminated, rather than patching against samples
- Retirement Review
  - Whether branches, duplicate owners, obsolete fallbacks, and invalid contracts were reduced

---

## 6. Method-Layer Positioning

Dual-track governance belongs to:

- The core governance process of `Aegis Method Pack`

It can:

- Organize analysis and delivery structure
- Require explicit retirement plans

It cannot:

- Overstep to replace the authoritative decision of a future runtime core
