---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Execute

→ Creative work (feature, component, behavior change)? → **Design first. No code until design approved.**
  1. Explore project context → read authority docs, check for existing patterns
  2. Ask clarifying questions one at a time (prefer multiple choice)
  3. Propose 2-3 approaches with trade-offs and your recommendation
  4. Present design sections → get user approval after each
  5. Write spec → self-review → user review → transition to writing-plans
→ HARD GATE: Do NOT write code, scaffold projects, or invoke implementation skills until design is approved.

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context and authority boundary, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits, authority docs, CONTEXT.md
2. **Choose the path and scope** — real design? diagnosis? route accordingly or decompose first
3. **Offer visual companion** (if visual questions ahead) — own message, no other content
4. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
5. **Draft working artifacts** — `TaskIntentDraft`, `BaselineReadSetHint`, `ImpactStatementDraft`
6. **Propose 2-3 approaches** — with trade-offs and your recommendation
7. **Present design** — in sections scaled to complexity, get user approval after each
8. **Write design doc** — save to `docs/aegis/specs/YYYY-MM-DD-<topic>-design.md` and commit
9. **Spec self-review** — check for placeholders, contradictions, ambiguity, scope, boundary
10. **User reviews written spec** — ask user to review before proceeding
11. **Transition to implementation** — invoke writing-plans skill (terminal state)

**The terminal state is invoking writing-plans.** Do NOT invoke any other implementation skill.

## The Process

**Understanding the idea:**
- Check current project state first (files, docs, recent commits)
- Read relevant authority docs before asking deep questions
- If the request is diagnosis/root-cause/follow-up to an approved plan → route to correct workflow
- If the request spans multiple independent subsystems → flag and decompose first
- Ask clarifying questions one at a time, prefer multiple choice
- Separate facts, assumptions, unknowns while exploring

**Working artifacts:** Keep three drafts: `TaskIntentDraft` (outcome, scope, risks), `BaselineReadSetHint` (candidate docs, authority gaps), `ImpactStatementDraft` (affected layers, owners, invariants, compat, non-goals). Refresh when scope changes.

**Exploring approaches:** Propose 2-3 approaches with trade-offs and recommendation. Make scope boundary explicit: what's in, what's deferred, what belongs elsewhere.

**Presenting the design:** Scale sections to complexity. Cover: architecture, components, data flow, error handling, testing, compatibility boundary. Get approval after each section.

**Design for isolation:** Each unit = one clear purpose, well-defined interface, testable independently. Can someone understand it without reading internals? Can you change internals without breaking consumers?

**Existing codebases:** Follow existing patterns. Include targeted improvements only when they serve the current goal. If the design touches contracts, compat, fallbacks, or duplicated owners → call it out directly.

## After the Design

**Documentation:**

- Before writing project artifacts, initialize the Aegis Project Workspace lazily:
  - If the project already has docs/ADR/baseline authority, reference it instead
    of duplicating it.
  - If no Aegis workspace exists and this task needs records, create only
    `docs/aegis/README.md` and `docs/aegis/INDEX.md` first.
  - For this task's process trail, create
    `docs/aegis/work/YYYY-MM-DD-<task-slug>/` only when the task is medium or
    high complexity.
- Write the validated design (spec) to `docs/aegis/specs/YYYY-MM-DD-<topic>-design.md`
  - (User preferences for spec location override this default)
  - If the design is task-specific and not reusable, it may live as
    `docs/aegis/work/YYYY-MM-DD-<task-slug>/20-spec.md` instead. Promote it to
    `specs/` only when future tasks should treat it as a reusable reference.
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git
- Include the latest `TaskIntentDraft`, `BaselineReadSetHint`, and `ImpactStatementDraft` inline or in an appendix when they materially shaped the design.
- Record explicit non-goals and compatibility boundaries so the later implementation plan does not drift.

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.
5. **Boundary check:** Did you clearly mark invariants, compatibility boundaries, owners, and non-goals?

Fix any issues inline. No need to re-review — just fix and move on.

**User Review Gate:**
After the spec review loop passes, ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response. If they request changes, make them and re-run the spec review loop. Only proceed once the user approves.

**Implementation:**

- Invoke the writing-plans skill to create a detailed implementation plan
- Do NOT invoke any other skill. writing-plans is the next step.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense

## Visual Companion

A browser-based companion for showing mockups, diagrams, and visual options during brainstorming. Available as a tool — not a mode. Accepting the companion means it's available for questions that benefit from visual treatment; it does NOT mean every question goes through the browser.

**Offering the companion:** When you anticipate that upcoming questions will involve visual content (mockups, layouts, diagrams), offer it once for consent:
> "Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)"

**This offer MUST be its own message.** Do not combine it with clarifying questions, context summaries, or any other content. The message should contain ONLY the offer above and nothing else. Wait for the user's response before continuing. If they decline, proceed with text-only brainstorming.

**Per-question decision:** Even after the user accepts, decide FOR EACH QUESTION whether to use the browser or the terminal. The test: **would the user understand this better by seeing it than reading it?**

- **Use the browser** for content that IS visual — mockups, wireframes, layout comparisons, architecture diagrams, side-by-side visual designs
- **Use the terminal** for content that is text — requirements questions, conceptual choices, tradeoff lists, A/B/C/D text options, scope decisions

A question about a UI topic is not automatically a visual question. "What does personality mean in this context?" is a conceptual question — use the terminal. "Which wizard layout works better?" is a visual question — use the browser.

If they agree to the companion, read the detailed guide before proceeding:
`skills/brainstorming/visual-companion.md`
