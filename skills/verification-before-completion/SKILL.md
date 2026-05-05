---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

This skill is the canonical completion gate for method-pack work. Use it to turn raw verification output into bounded, reviewable evidence without crossing into authoritative runtime completion.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Required Outputs

Before you leave this workflow, you must be able to state:

1. **What exact claim was being checked**
2. **What fresh command or verification step was run**
3. **What the output actually proved**
4. **What remains unverified or unknown**
5. **Whether Remove/Restore checks found side effects**
6. **What confidence grade the evidence supports**
7. **Whether this is verified evidence only, or also an authoritative completion signal**
8. **Which target test and related regression tests were run, or why they could not run**
9. **What manual verification steps reproduce the check when automation is blocked**
10. **For user-visible work, whether the main user journey was verified and what experience or operational floor remains unverified**
11. **For long tasks, what latest `TodoCheckpointDraft` and `DriftCheckDraft` say about remaining work, blockers, and drift risk**
12. **For governance, cleanup, migration, compatibility, namespace cutover, public release, deprecation, policy boundary, or retirement work, whether the final response preserved the governance closure contract**
13. **When prompt hygiene affected the work, which evidence was summarized, which raw payloads were not loaded, and what readback remains available**

Method-pack default: you provide verified evidence and advisory judgment. Do not imply that verification alone grants authoritative completion unless the governing runtime explicitly says so.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| Work is done | Fresh QA bundle + residual risk statement | "Looks good to me" |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Target test and related regression:**
```
✅ Target test: npm test path/to/changed.test.ts
✅ Related regression: npm test path/to/consumer.test.ts
❌ "Ran the easiest test only" when shared modules or contracts changed
```

**Automation blocked:**
```
✅ Blocker: local DB schema unavailable
✅ Manual verification steps: start service, POST payload X, expect response Y
✅ Follow-up: add automated regression when test DB is available
❌ "Could not run tests" without manual steps or follow-up
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**User-visible work:**
```
✅ Verify main journey (E2E, integration, Playwright, screenshot, or reproducible manual steps) → state what was proven
✅ If main journey was not verified → claim only the narrower verified scope and report the journey as residual risk
❌ "Unit tests pass, feature complete"
```

**QA closure:**
```
✅ Verify command(s) → Read output → Check side effects / rollback surface → State confidence and unknowns
❌ "Verified" without saying what was actually proven
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents
- Marking a slice, wave, or milestone as complete

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## QA Closure

After the raw verification step passes, perform a short QA pass:

1. **Remove/Restore**
   - Did this change introduce side effects elsewhere?
   - If you temporarily changed instrumentation, guards, or fixtures, were they restored or intentionally kept?

2. **Evidence Bundle**
   - Capture the exact command, scope, exit status, and key output
   - State what the evidence covers and what it does not cover
   - For user-visible work, state whether the main journey and applicable
     experience or operational floor were verified
   - Prefer compact, runtime-ready reporting over vague success language

3. **Prompt Hygiene Boundary**
   - Apply this when external tool output, logs, memories, search results,
     transcripts, screenshots, OCR/document extraction, or large command output
     shaped the judgment.
   - Report whether the work used summaries, raw excerpts, or fresh
     verification.
   - Name any large raw payloads intentionally not loaded into prompt context.
   - If the summary was insufficient, either read back the smallest relevant
     excerpt or lower the claim to `unknown`, `partial`, or
     `needs-verification`.
   - When relevant, include this compact evidence boundary:

   ```text
   Evidence Used:
   - summary: ...
   - raw excerpt: ...

   Not Loaded:
   - full log / full transcript / full search results / full tool output

   Confidence:
   - A / B / C, with why

   Next Evidence:
   - ...
   ```

4. **Confidence Grade**
   - `A` = direct evidence plus meaningful regression coverage; no material unknowns remain
   - `B` = direct evidence for the core claim, with bounded residual risk
   - `C` = partial or indirect evidence only; do not present as fully closed

5. **Authority Boundary**
   - `verified evidence` means the claimed check passed
   - `authoritative completion` requires whatever higher-level owner, runtime, or governance process defines final completion
   - Never collapse those two ideas into one sentence unless the authority chain is explicit

6. **Long-Task Checkpoint Review**
   - If the task used long-task-continuation, re-read the latest checkpoint.
   - Confirm every todo has a status.
   - Confirm no drift check is still `blocked`, `pause-for-user`, `needs-baseline-readback`, or `needs-verification`.
   - If any checkpoint item is unresolved, report partial status instead of completion.

7. **Governance Closure Contract**
   - Apply this for governance, cleanup, migration, compatibility, namespace
     cutover, public release, deprecation, policy boundary, or retirement work.
   - Do not skip this structure just because the implementation was small. If
     the task belongs to a governance or retirement category, compress the
     content, but preserve the tracks.
   - Localize section labels and prose to the user's language. Keep stable
     internal concepts in English only when they are product terms or
     file/path identifiers.

   Required final-response shape:

   ```text
   Repair Track:
   - repaired object
   - action taken
   - impact scope
   - verification evidence

   Retirement Track:
   - retired object
   - retirement action
   - retained boundary
   - future retirement trigger

   Residual Risk:
   - unverified items
   - intentionally deferred items
   ```

## Red Flags - QA Drift

- Reporting "done" when only one layer was checked
- Treating agent success as equivalent to independent verification
- Forgetting to mention residual risk or uncovered scope
- Saying "verified" when the command was narrow but the claim is broad
- Presenting method-pack verification as if it grants final authority
- Adding new verification branches without saying what old check or fallback now retires
- Closing governance or retirement work without Repair Track, Retirement Track,
  and Residual Risk, even when the change was small

## Minimal Reporting Shape

Use this shape when closing a task:

- **Claim checked**
- **Evidence**
- **Result**
- **Unknown / residual risk**
- **Confidence**
- **Authority note**

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
