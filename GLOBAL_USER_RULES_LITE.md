# Aegis Lite Global Rules

Copy this block into your AI coding tool's global user rules when you want
lighter Aegis routing without importing the full advanced template.

```markdown
# Aegis Lite Global Rules

If Aegis is installed:

- At the start of each turn, check whether the task matches an installed Aegis
  skill. If it matches, load and follow that skill.
- Simple, local, low-risk tasks may use a fast path. Do not expand the full
  governance workflow just because Aegis exists.
- Complex, diagnostic, architecture, refactor, contract, cross-module, shared
  module, compatibility, or long-running tasks should use the relevant Aegis
  workflow by default.
- Before implementation, identify the goal, scope, impact surface, and
  verification method. Read project baseline or authority docs when relevant.
- Before claiming completion, provide fresh verification evidence. If
  verification is blocked, state the blocker and residual risk.
- Aegis is a method layer, not a final authority system. Do not claim final
  gate decisions or completion authority.
- The user's current instruction and the target project's rules take priority
  over Aegis guidance.
```

For stricter teams or governance-heavy projects, start from
[GLOBAL_USER_RULES_TEMPLATE.md](GLOBAL_USER_RULES_TEMPLATE.md) and merge only
the parts you need.
