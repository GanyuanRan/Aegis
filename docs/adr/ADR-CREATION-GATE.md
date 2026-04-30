# ADR Creation Gate

An Architecture Decision Record is a permanent document. Before creating one, confirm ALL THREE conditions hold. If any is missing, capture the decision in a lighter form (CONTEXT.md term, code comment, or commit message).

## The Three Conditions

### 1. Hard to Reverse

Changing your mind later would be costly in time, data migration, or cross-team coordination.

**Qualifies**: "We chose PostgreSQL over MongoDB because ACID transactions are required for payment processing." — migrating payment data between database paradigms is expensive.

**Does not qualify**: "We'll use tabs for indentation." — trivial to reformat later.

### 2. Surprising Without Context

A future reader (including your future self) would wonder "why did they do it this way?" without the decision record.

**Qualifies**: "We're using polling instead of WebSockets because the target deployment environment blocks persistent connections." — without this context, a future developer would assume it's a mistake and "fix" it.

**Does not qualify**: "We're using Express because it's the standard choice for Node.js HTTP servers." — any Node.js developer would assume this.

### 3. Result of a Real Trade-off

Genuine alternatives existed, were evaluated, and one was chosen for specific, articulated reasons.

**Qualifies**: "Evaluated three caching strategies (in-memory LRU, Redis, CDN-edge). Redis chosen because sub-ms latency requirement rules out CDN, and multi-process access rules out in-memory."

**Does not qualify**: "We chose React." — if no alternatives were seriously considered, there's no trade-off to record.

## Self-Check

Before creating an ADR:

- [ ] If we reversed this decision in 6 months, would it be expensive?
- [ ] If a new team member read the code without this ADR, would they be confused?
- [ ] Did we genuinely compare alternatives and choose for specific reasons?

All three must be YES. Otherwise, use a lighter format.

## Example: A Qualified ADR

`ADR-0001-aegis-method-pack-is-not-runtime-core.md` meets all three:

1. **Hard to reverse** — once method-pack code ships as runtime-core, untangling the two layers is expensive
2. **Surprising** — future contributors would wonder why the method-pack stops short of making authoritative runtime decisions
3. **Real trade-off** — "deliverable now" vs "future capability boundary" was an explicit choice

## Example: Something That Should NOT Be an ADR

"We decided to use 2-space indentation." → Fails condition 1 (trivial to change) and condition 3 (no real alternatives evaluated — it's a style preference). Capture this in `.editorconfig` instead.
