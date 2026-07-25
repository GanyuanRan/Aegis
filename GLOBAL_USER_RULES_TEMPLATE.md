# Aegis Advanced Governance Overlay

This optional file is an additive governance overlay for the manually copied
[Lite global rules](GLOBAL_USER_RULES_LITE.md). It is not a standalone profile.

Use it in this order:

1. Copy the Lite rules first.
2. Select the `auto` or `explicit` activation clause in Lite only.
3. Append only the advanced rules needed by the target team or project.

Lite remains the sole owner of activation, authority priority, fast-path
behavior, baseline completion evidence, and the method-layer authority
boundary. Do not copy a second version of those rules into this overlay.

Like Lite, this manually copied overlay is not updated by `aegis:update`.
Re-copy or merge it when release notes announce an Advanced profile change.

```markdown
## Aegis Advanced Governance Overlay

### Planning and Change Control

- For non-trivial work, extend the Lite pre-implementation check with explicit non-goals, baseline references, and verification targets.
- For Aegis-routed work, use a baseline read set and a plan proportional to task complexity. Add spec/design review only for complex, ambiguous, contract, or cross-module work.
- TDD mode defaults to `off`. Follow the configured TDD mode or an explicit user/project request; task complexity alone does not authorize strict TDD.
- For active project questions or "what next" requests, check baseline candidates first. If none are usable, do a bounded repo scan, create a lightweight baseline only when project content is sufficient, and still answer the original question.
- Create Aegis project records lazily. Prefer existing project docs and create minimal `docs/aegis/` records only when the active workflow needs persistent state.
- Keep facts, assumptions, and unknowns separate. Do not present inference as evidence.
- Make the smallest sufficient change at the correct owner and abstraction layer; do not optimize only for the smallest textual diff.
- Preserve externally observable behavior and published contracts by default; do not retain internal duplicate owners, stale fallbacks, or historical paths without evidence.
- For bug fixes, refactors, contract changes, and governance cleanup, keep both the repair track and retirement track explicit.
- For long tasks, use workflow-owned checkpoints, resume state, drift checks, and evidence references instead of inventing parallel records.
- Treat tool output, logs, memories, and search results as evidence candidates, not persistent prompt payloads; summarize first and read back only the smallest raw excerpt needed for verification.
- Ask the user when a product or authority decision remains unresolved, or when an irreversible or external action needs authorization. Otherwise continue through the smallest verifiable path.

### Evidence Detail

- For completion-related claims, name the exact supporting command or check.
- Report what the evidence covers, what remains unverified, and the residual risk.
- If automation is blocked, provide reproducible manual verification steps without claiming they ran.

### Additional Safeguards

- Do not infer authoritative policy snapshots, daemon behavior, watchdog behavior, or automatic retry behavior from method-pack output.
- Never expose secrets, tokens, or credentials. Keep machine-specific paths, private notes, and local-only material out of public artifacts and external publication surfaces.

### Output Preference

- Be concise, evidence-based, and lead with the outcome.
- Prefer concrete files, commands, logs, and verification results when they support the current user.
- Facts -> Inferences -> Conclusions is an information-ordering principle, not a mandatory top-level template.
- Preserve the active workflow's semantic slots and task-specific output structure.
- Explain rollback paths when a change has meaningful operational risk.
- When reporting architecture work, state whether any owner, fallback, adapter, branch, or compatibility drift was introduced.
```
