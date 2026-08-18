# Aegis Global Routing Prefix

Add the block below at the very beginning of the existing global user rules;
there is no need to change the existing content.

This optional, manually copied host/profile prefix does not install Aegis or
prove that its skills are discoverable. It is not updated by `aegis:update`;
re-copy or merge it when release notes announce a routing-prefix change.

```markdown
# Aegis Global Routing Prefix

If Aegis is installed:

- Follow the Aegis Activation Mode provided by the host or current session; if none is declared, use the default `auto`.
- `auto`: At the start of each turn, determine whether the current task matches an installed Aegis skill. When it does, load and follow the smallest necessary relevant skill before responding or acting.
- `explicit`: Load Aegis only when the user explicitly invokes Aegis or names an Aegis skill; do not activate it from task semantics alone.
- When no Aegis skill matches, use the normal fast path. When one matches, let that skill decide whether its fast path applies; do not expand the full governance workflow merely because Aegis is installed.
- After long-task continuation, session resume, context compaction, or a clear task change, re-check Aegis routing against the current task.
- Let the currently loaded Aegis skill determine the task-specific analysis, planning, debugging, TDD, verification, governance, and output requirements.
- TDD Mode is independent of Activation Mode. Follow the current Aegis configuration (`off` by default, optionally `auto`) and explicit user or project requirements.
```
