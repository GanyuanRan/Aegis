---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Execute

→ Bug? Test failure? Unexpected behavior? → **Find root cause first. No fixes without evidence.**
  1. Isolate: read error → reproduce → check git diff → cover 4 layers (symptom / logic / system / architecture)
  2. Identify owner: compare with working code → locate canonical owner → flag duplicate owners as a finding
  3. Prove: one hypothesis → minimal test → iterate. 3+ failed hypotheses = question architecture, do not attempt #4.
  4. Fix: failing test → minimal code at canonical owner → verify → repair track + retirement track
→ Done when: confidence ≥ B, both tracks explicit, DeeperCause answered "no" with evidence.

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Symptom fixes are failure.

This skill is the canonical debugging workflow. Use it to move from symptom to root cause, then to the smallest justified fix and retirement plan.

## When to Use

Any technical issue: test failures, bugs, unexpected behavior, performance problems, build/integration failures.

Especially under time pressure, when "just one quick fix" seems obvious, after multiple failed fixes, or when duplicate owners / fallback chains may be involved.

Simple bugs have root causes too. Rushing guarantees rework.

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → consult `feedback-loop-construction.md` to build an automated reproduction loop before proceeding; don't guess
   - Record the current baseline: inputs, environment, version, logs, and success/failure criteria

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   When the system has multiple components (CI → build → signing, API → service → database):
   - Instrument each component boundary: log what enters and exits
   - Run once to see where data breaks, then focus investigation there

5. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
    - Where does bad value originate?
    - What called this with bad value?
    - Keep tracing up until you find the source
    - Fix at source, not at symptom

6. **Cover the Four Diagnostic Layers**
   - **Symptom layer**: what visibly failed, where, and under what reproduction steps?
   - **Logic layer**: which branch, contract, invariant, or state transition is wrong?
   - **System layer**: which component boundary, dependency, config, or ownership seam allowed it?
   - **Architecture layer**: what design choice, duplicated owner, fallback, or compatibility layer made the issue possible?

   If you have not checked all four layers, you are not done diagnosing.

### Phase 2: Pattern Analysis

1. **Find working examples** in the same codebase — what works that's similar?
2. **Compare against references** — read completely, don't skim
3. **Identify differences** between working and broken — list every difference
4. **Understand dependencies** — config, environment, assumptions
5. **Locate the canonical owner** — which file/module should own this? Multiple owners = a finding, not normality

### Phase 3: Hypothesis and Testing

1. **Form single hypothesis**: "I think X is the root cause because Y" — be specific
2. **Test minimally**: smallest possible change, one variable at a time. Prefer instrumentation over code edits while still proving the cause.
3. **Verify**: worked? → Phase 4. Didn't? → Form NEW hypothesis. Don't stack fixes.
4. **When you don't know**: say "I don't understand X", don't pretend
5. **Run Reflection** at the end of each loop:
   - **Goal** | **DeeperCause** (yes/no/uncertain) | **Evidence** | **Risk/Unknown** | **Decision** (exit/iterate/escalate)
   - If DeeperCause = uncertain → continue or escalate. Only exit when root cause is deep enough and evidence is sufficient.

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Use the `aegis:test-driven-development` skill for writing proper failing tests

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring
   - Prefer changing the canonical owner instead of stacking more logic into a fallback path

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?
   - Verify the intended compatibility boundary still holds
   - Verify you did not silently move authority to the wrong layer

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with your human partner before attempting more fixes**

   This is NOT a failed hypothesis - this is a wrong architecture.

6. **Deliver Dual-Track Closure**

   For bug fixes, refactors, contract changes, or governance cleanup, always produce:

   **Fix track**
   - Root cause
   - Canonical owner
   - Smallest necessary change
   - Compatibility boundary
   - Verification method

   **Retirement track**
   - Old owner / fallback / patch / duplicate branch
   - Whether it is still active on the main path
   - The only reason to keep it, if any
   - Trigger for deletion or convergence
   - Verification needed before removal

   Never add a new owner, fallback, prompt branch, or adapter path without stating what happens to the old one.

## Quality Gate

Before you claim debugging is complete:

1. Re-run the latest Reflection checklist
2. Confirm the fix addressed the source, not just the sample
3. Confirm whether the retirement surface shrank, stayed, or grew
4. State confidence:
   - `A` = direct evidence and regression coverage support the root-cause conclusion
   - `B` = strong evidence, limited coverage or some bounded unknowns remain
   - `C` = partial evidence only; do not present as fully resolved

If confidence is not at least `B`, do not speak as if the issue is fully closed.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**
- **"Let's just add another fallback"**
- **"We can keep both owners for now" without a retirement condition**

**ALL of these mean: STOP. Return to Phase 1.**

**If 3+ fixes failed:** Question the architecture (see Phase 4.5)

## Human Partner Signals

If you hear "Is that not happening?", "Will it show us...?", "Stop guessing", "Ultrathink this" → STOP. Return to Phase 1.

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
 | **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, cover symptom/logic/system/architecture | Understand WHAT, WHY, and WHERE the true owner is |
 | **2. Pattern** | Find working examples, compare, identify canonical owner | Identify differences and duplicated ownership |
 | **3. Hypothesis** | Form theory, test minimally, run Reflection | Confirmed or new hypothesis with explicit evidence |
 | **4. Implementation** | Create test, fix, verify, close fix+retirement tracks | Bug resolved, tests pass, and retirement surface is explicit |

## When Process Reveals "No Root Cause"

If investigation reveals the issue is truly environmental, timing-dependent, or external:
document what you investigated, implement appropriate handling (retry, timeout, error message),
add monitoring. But: 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

See `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`, `feedback-loop-construction.md` in this directory.

Related skills: `aegis:test-driven-development`, `aegis:verification-before-completion`.
