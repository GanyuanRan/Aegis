---
name: writing-plans
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

This skill is the canonical planning workflow for multi-step implementation work. Use it to convert approved specs or requirements into plans that are executable, testable, impact-aware, and bounded by compatibility and authority constraints.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/aegis/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)
- For task-specific plans that do not need to become reusable project
  references, save the plan in
  `docs/aegis/work/YYYY-MM-DD-<task-slug>/30-plan.md` and record atomic tasks in
  `docs/aegis/work/YYYY-MM-DD-<task-slug>/40-atomic-tasks.md`.
- Promote a plan to `docs/aegis/plans/` only when future tasks should reuse it
  as a stable implementation reference.

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

Before writing tasks, explicitly check:

- what is fact vs assumption vs unknown
- what baseline docs or contracts the plan must respect
- what compatibility boundary the implementation cannot break
- whether this plan includes bugfix / refactor / contract work that must carry repair track + retirement track expectations

If authority or scope is unclear, say so before drafting the plan.

## Aegis Project Workspace

Use a lazy, task-scoped workspace. Do not create directories or files just in
case.

Default minimum when project records are needed:

```text
docs/aegis/
  README.md
  INDEX.md
```

For medium-complexity implementation tasks:

```text
docs/aegis/work/YYYY-MM-DD-<task-slug>/
  00-intent.md
  10-baseline-readset.md
  30-plan.md
  40-atomic-tasks.md
  50-evidence.md
```

For high-complexity or reusable work, add only the directories that are
actually justified:

- `baseline/` when the project lacks a baseline and the user agrees to create
  one, or when project facts must be maintained here.
- `adr/` when the task creates a durable architecture decision.
- `specs/` when a design/spec should be reused across tasks.
- `plans/` when an implementation plan should be reused across tasks.

If the project already has `docs/adr/`, architecture docs, README/AGENTS
authority, or another baseline owner, link to those from `INDEX.md` or the
baseline read-set instead of duplicating them under `docs/aegis/`.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Required Planning Outputs

Before you leave this workflow, the written plan must make these items answerable:

1. **What problem or approved scope this plan is implementing**
2. **Which baseline docs, ADRs, or requirements shaped the plan**
3. **What files own the change**
4. **What compatibility boundary must hold**
5. **What verification proves each major slice**
6. **What risks, rollback surface, or unknowns remain**
7. **What old owner / fallback / patch stays, shrinks, or retires when applicable**

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use aegis:subagent-driven-development (recommended) or aegis:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Baseline / Authority Refs:** [Exact docs, ADRs, requirements, or contracts that constrain this plan]

**Compatibility Boundary:** [What existing behavior or interfaces must remain stable]

**Verification:** [What commands, tests, or checks will prove this work]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Why this task exists:**
- [Which user/business value, requirement, invariant, or risk this task addresses]
- [For user-visible work: the main journey or experience floor this task protects]

**Impact / Compatibility:**
- [Affected layers, owners, contracts, and what must not break]

**Verification:**
- [Exact command(s) or check(s) that prove this task is done]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

For bug fixes, refactors, contract changes, or governance cleanup, add two short subsections inside the relevant task:

- **Repair Track**
  - root cause being addressed
  - canonical owner being changed
  - smallest necessary change
  - compatibility boundary
  - task-level verification

- **Retirement Track**
  - old owner / fallback / patch / duplicate branch
  - whether it is still active
  - only reason to keep it, if any
  - trigger for deletion or convergence
  - verification before removal

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits
- Call out impact, compatibility, and verification explicitly
- Tie each task to user/business value or a concrete risk; do not justify work
  with technical motion alone
- For user-visible work, include main-journey verification or explicitly mark the
  unverified journey as residual risk
- If the work alters old logic, say what retires and what remains

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

**4. Compatibility check:** Did you clearly mark invariants, non-goals, and interfaces that must stay stable?

**5. Verification check:** Does every major task say exactly how it will be proven?

**6. Dual-track check:** If the work changes old logic, did you state what retires, what stays, and why?

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `docs/aegis/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use aegis:subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use aegis:executing-plans
- Batch execution with checkpoints for review

## Planning Boundaries

- A plan can define implementation slices, verification, rollback surface, and retirement expectations
- A plan cannot grant authoritative completion
- A plan should prepare runtime-ready execution, not pretend to be runtime authority
