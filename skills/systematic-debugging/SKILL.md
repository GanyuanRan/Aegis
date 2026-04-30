---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

This skill is the canonical debugging workflow for diagnosis work. Use it to move from symptom to root cause, then from root cause to the smallest justified fix and retirement plan.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue
- The issue may involve duplicated owners, fallback chains, or historical compatibility layers

**Don't skip when:**
- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (systematic is faster than thrashing)

## Required Outputs

Before you leave this workflow, you must be able to state:

1. **What is fact vs assumption vs unknown**
2. **What the root cause is**
3. **What the canonical owner is**
4. **What the smallest necessary fix is**
5. **What older owner / fallback / patch must stay, shrink, or retire**
6. **What evidence proves your conclusion**
7. **Whether any deeper architectural cause still remains**

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

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

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

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

5. **Locate the Canonical Owner**
   - Which file, module, or contract should own this behavior?
   - Is the current failure happening in the owner, or in a stale mirror / fallback / compatibility path?
   - If multiple owners appear to exist, treat that as a debugging finding, not as normal complexity

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once
   - Prefer instrumentation, assertions, or a targeted reproduction before code edits when you are still proving the cause

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

5. **Run Reflection Before Moving On**

   Use this checklist at the end of each diagnostic loop:

   - **Goal:** Which acceptance points are satisfied? Which are not?
   - **DeeperCause:** Is there a deeper cause below the current finding? Answer `yes`, `no`, or `uncertain`.
   - **Evidence:** What logs, commands, tests, or file references support the conclusion?
   - **Risk/Unknown:** What architectural drift, residual risk, or unknowns remain?
   - **Decision:** `exit`, `iterate`, or `escalate`

   Rules:
   - If `DeeperCause = uncertain`, you must continue or escalate.
   - Only choose `exit` when you can justify why the root cause is deep enough and evidence is sufficient.

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

## your human partner's Signals You're Doing It Wrong

**Watch for these redirections:**
- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultrathink this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**When you see these:** STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |
| "We'll keep the fallback forever just in case" | Unbounded fallback retention is architecture drift. Set a retirement trigger or remove it. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
 | **1. Root Cause** | Read errors, reproduce, check changes, gather evidence, cover symptom/logic/system/architecture | Understand WHAT, WHY, and WHERE the true owner is |
 | **2. Pattern** | Find working examples, compare, identify canonical owner | Identify differences and duplicated ownership |
 | **3. Hypothesis** | Form theory, test minimally, run Reflection | Confirmed or new hypothesis with explicit evidence |
 | **4. Implementation** | Create test, fix, verify, close fix+retirement tracks | Bug resolved, tests pass, and retirement surface is explicit |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## Supporting Techniques

These techniques are part of systematic debugging and available in this directory:

- **`root-cause-tracing.md`** - Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** - Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** - Replace arbitrary timeouts with condition polling
- **`feedback-loop-construction.md`** - Build automated reproduction loops before forming hypotheses

**Related skills:**
- **aegis:test-driven-development** - For creating failing test case (Phase 4, Step 1)
- **aegis:verification-before-completion** - Verify fix worked before claiming success

## Real-World Impact

From debugging sessions:
- Systematic approach: 15-30 minutes to fix
- Random fixes approach: 2-3 hours of thrashing
- First-time fix rate: 95% vs 40%
- New bugs introduced: Near zero vs common
