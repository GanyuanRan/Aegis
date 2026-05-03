---
name: using-aegis
description: Use when starting any conversation - establishes compact Aegis skill-use discipline before any response, clarification, or action
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
You have Aegis.

Before any response or action, check whether a skill is relevant or explicitly
requested. If yes, load and follow that skill. If no skill applies, proceed
normally.
</EXTREMELY-IMPORTANT>

## Hot Path Rules

1. User instructions are highest priority. Aegis skills guide how to work, but
   never override explicit user or project instructions.
2. Process skills come before implementation skills. Before implementation,
   classify task complexity. Low-complexity work may enter TDD after concise
   intent and baseline checks; medium/high-complexity work needs planning,
   atomic tasks, and sometimes spec/design review before TDD.
   Contract, cross-module, shared module, and core logic changes are not
   low-complexity unless local evidence proves otherwise.
3. Use the Aegis Project Workspace lazily. Never write project files during
   global install. When records are needed, prefer existing project docs and
   create only minimal `docs/aegis/` task-scoped artifacts.
4. Load only the skills and references needed for the current task. Do not
   preload broad reference trees.
5. Do not search or read historical sessions, transcripts, `history.jsonl`,
   `.codex/sessions`, `~/.claude/projects`, or large log files by default.
   Search them only when the user asks, a test explicitly requires it, or they
   are the direct evidence source. Always bound such searches by scope, time,
   filename, or result limit.
6. If unsure how to map Aegis skill tool names to the current host, read the
   smallest relevant mapping in `references/`.

## Need More Detail?

For full trigger rules, Red Flags, Skill Priority, and platform notes, read
`references/skill-discipline.md`. Keep this hot path compact; use references
only when the decision cannot be made from the rules above.
