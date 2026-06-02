# Aegis for GitHub Copilot

This repository uses Aegis as method-pack workflow discipline.

Before risky implementation, prefer the smallest relevant Aegis skill from
`.github/skills/` or the linked Aegis skill directories. Keep detailed workflow
logic in the skill body rather than duplicating it here.

Key repository boundaries:

- treat Aegis as `Aegis Method Pack (runtime-ready)`, not a runtime core
- keep user instructions and target-project rules above Aegis guidance
- do not claim authoritative `GateDecision` or final completion authority
- require fresh verification evidence before completion claims
- keep repository instructions concise; do not replace skill bodies with a long
  fixed prompt
