# Aegis Lite Global Rules

This optional file is a manually copied host/profile projection. It does not
install Aegis or prove that skills are discoverable. It is not updated by
`aegis:update`; re-copy or merge it manually when release notes announce a
profile change.

The copyable block below uses the default `auto` activation profile. If the
installed Aegis configuration uses `explicit`, replace the activation bullet
with the explicit-mode version below. Keep exactly one activation profile.

```markdown
# Aegis Lite Global Rules

If Aegis is installed:

- Activation profile: `auto`. At the start of each turn, check whether the task matches an installed Aegis skill. If it matches, load and follow that skill.
- Simple, local, low-risk tasks may use a fast path. Do not expand the full governance workflow just because Aegis exists.
- Once Aegis is active for the turn, complex, diagnostic, architecture, refactor, contract, cross-module, shared-module, compatibility, or long-running tasks should use the relevant Aegis workflow by default.
- Before implementation, identify the goal, scope, impact surface, and verification method. Read project baseline or authority docs when relevant.
- Before claiming completion, provide fresh verification evidence. If verification is blocked, state the blocker and residual risk.
- Aegis is a method layer, not a final authority system. Do not claim final gate decisions or completion authority.
- The user's current instruction and the target project's rules take priority over Aegis guidance.
```

## Explicit-mode replacement

Replace only the activation bullet above with:

```markdown
- Activation profile: `explicit`. Use Aegis only when the user explicitly invokes Aegis or a specific Aegis skill; do not auto-route from task semantics under this profile.
```

This replacement aligns the copied profile; it cannot guarantee that a
host-native skill matcher will not independently match an installed skill.

For stricter teams or governance-heavy projects, keep this Lite block as the
base, then append only the parts you need from the
[Advanced governance overlay](GLOBAL_USER_RULES_TEMPLATE.md).
