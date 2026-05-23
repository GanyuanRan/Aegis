# Aegis Prompt Hygiene and Injection Boundary

Status: `Approved`

## 1. Document Scope

This document defines the prompt hygiene and external evidence injection boundary for the `Aegis Method Pack`.

This document answers:

- Which external materials may enter the prompt
- Which external materials must first be summarized, indexed, or quarantined
- How to reduce persistent context without weakening Aegis's judgment capability
- How to escalate evidence gathering when information is insufficient, rather than lowering judgment standards

This document does NOT answer:

- Final evidence sufficiency adjudication by the future runtime core
- Context compression implementation in host adapters
- Security classifier details for specific models or platforms

---

## 2. Bottom Line Up Front

The current rule is:

> External tool output, logs, memories, and search results are evidence candidates by default — they should NOT be injected into the prompt in full. Summarize first, cite raw excerpts on demand; only bring in the smallest excerpt when verification requires the original text.

This rule applies to:

- shell / terminal output
- MCP tool output
- semantic retrieval tool output
- web / docs / search results
- memory / prior session summaries
- CI / test / runtime logs
- database / telemetry / structured log query results
- browser / screenshot / OCR / document extraction results

This rule is not about seeing less evidence — it is about not mistaking raw materials for persistent context.

---

## 3. Core Principles

### 3.1 Reduce Persistent Context, Not Available Information

Aegis's capability comes from:

- Correctly identifying authority sources
- Correctly establishing baseline read-sets
- Correctly judging impact scope and risk
- Correctly collecting and citing evidence
- Refusing over-conclusion when evidence is insufficient

These capabilities do not require all raw materials to be persistent in the prompt.

The governance goal is:

- Retain the minimum evidence summary needed for the current judgment in the prompt
- Keep raw materials in files, logs, command output, tool results, or artifact references
- Read back original excerpts by reference when re-verification is needed

### 3.2 Raw Input Quarantine

The following materials default to NOT entering the prompt in full:

- Long logs
- Historical sessions / transcripts
- Large tool output
- Full memory summaries
- Complete test / CI output
- Large search result pages
- Full large files
- Repeated error text

They should first be converted to:

- Source
- Time / scope / command
- Key facts
- Key line numbers or excerpt references
- Unverified points
- Whether original readback is needed

### 3.3 Summary First, Raw Excerpt Only When Needed

The default injection order is:

1. Inject the summary first
2. When the summary is insufficient, read the smallest original excerpt
3. When the excerpt is still insufficient, expand the read range
4. When expansion is still insufficient, downgrade status to `unknown` or `needs-verification`

It is forbidden to package an evidence-deficient judgment as a conclusion because context budget is insufficient.

### 3.4 Evidence Index Before Evidence Payload

For large materials, establish an evidence index first:

- `source`
- `commandOrTool`
- `timeOrVersion`
- `scope`
- `summary`
- `relevantRefs`
- `rawLocation`
- `readbackNeeded`

Only when `readbackNeeded = true`, bring the smallest original excerpt into the current prompt.

### 3.5 No Silent Pruning

If material is compressed or omitted, it must be answerable:

- What type of material was omitted
- Why the current judgment does not need its full text
- How to read it back if needed
- Whether the current conclusion is downgraded as a result

Do not present "did not read the full material" as "the material supports the conclusion."

### 3.6 Host Context Intake Discipline

`Host Context Intake Discipline` is the host-side context intake discipline. Its stable owner is `bounded evidence intake`:

> Large input: build index first, then read windows, finally bring in only the necessary excerpts.

The standard order is:

1. `index`: First locate source, pattern, match line, command scope, time, or version.
2. `window`: Only read the smallest line-number window around the hit location.
3. `excerpt`: Only bring the original excerpt that the current judgment must depend on into the prompt.
4. `expand`: Expand range with justification when the window is insufficient; downgrade to `unknown` or `needs-verification` if still insufficient after expansion.

This discipline applies to high-risk input surfaces in hosts such as Codex,
Claude Code, OpenCode, Copilot, Antigravity CLI, Antigravity IDE,
Antigravity App, and transitional Gemini CLI, including:

- `.codex/log`, `.codex/sessions`, `history.jsonl`
- `~/.claude/projects`, host transcripts, chat history
- Complete CI / pytest / build / server output
- Large `git diff`, continuous `apply_patch` output, long-running poll logs
- Search results, memory, MCP or semantic retrieval large candidate output

Broad directory searches for historical materials are forbidden by default — e.g., directly scanning entire `.codex`, `.claude`, or host projects directories. Only read when the user explicitly requests, a test requires it, or they are direct evidence sources, and always with:

- Specific file path or strict file set
- Keyword or time / request / thread scope
- Line number window or result count cap
- Output cap or explicit summary-first strategy

When any of the following triggers, prefer switching to a fresh session, compressing context, or writing state as a `ResumeStateHint` and continuing:

- A single request input is clearly approaching the host or model context limit
- Large logs, history, sessions, or transcripts have been read consecutively
- Large patches, diffs, or test output have been executed consecutively in the same session
- `PROMPT_POLICY_WARNING`, `Invalid prompt`, or equivalent host warning has appeared
- Current judgment is starting to depend on old error full text rather than the evidence index

This discipline does not require less evidence gathering. It requires less persistent raw text and more retained re-readable references. The future runtime core can build true budget enforcement on top of this; the current method pack only provides workflow discipline, helper scripts, and runtime-ready hints.

---

## 4. Capability Protection Rules

Prompt hygiene must not weaken the following Aegis behaviors:

- baseline-first
- evidence-before-claims
- facts / assumptions / unknowns separation
- impact-aware judgment
- compatibility boundary review
- dual-track repair + retirement
- root-cause-first debugging
- verification-before-completion
- long-task checkpoint / resume / drift checks
- no authoritative completion from method-pack output

If these behaviors cannot be performed after context reduction, the correct action is not to skip governance — it is to escalate evidence gathering.

---

## 5. Escalation Ladder When Information Is Insufficient

When a summary is insufficient to support judgment, escalate in the following order:

1. Re-read the relevant section of authority docs
2. Re-read the smallest excerpt of the specific file or symbol
3. Query key lines of specific logs, test output, or command output
4. Run the smallest verification command
5. Expand the evidence read-set
6. Mark as `needs-verification`
7. Request the user to supplement authority or acceptance criteria that cannot be obtained autonomously

This ladder guarantees that Aegis does not become "less judgment after less context", but rather "less persistent context while maintaining on-demand evidence gathering capability."

---

## 6. External Material Injection Rules

### 6.1 Tool Output

Tool output defaults to injecting only:

- Tool name
- Input scope
- Key results
- Failures or anomalies
- References needed for later readback

Only when tool output itself is acceptance evidence, inject the smallest original excerpt.

### 6.1.1 MCP / Semantic Retrieval Tools

MCP tools, Serena, Context7, code indexes, semantic retrieval, and similar tools are not contamination sources by default.

The risk comes from:

- Treating full retrieval results as persistent prompt payload
- Stuffing excessive candidate symbols, file summaries, or historical indexes into context at once
- Treating tool output as current authority rather than evidence candidate

Correct usage:

- First record query scope, hit owner, relevant line numbers or symbols
- Only inject summary / refs / unknowns needed for the current judgment
- Re-read the smallest code excerpt or authority section when precise judgment is needed
- Do not substitute current repo source of truth with tool summaries

### 6.2 Logs

Logs default to injecting only:

- Time window
- Thread / request / trace ID
- Command or query
- Key lines
- Counts or status codes
- Missing observability

Do not paste complete logs as persistent context.

### 6.3 Memories and Prior Sessions

Memories and historical sessions default to hints only.

Current facts must come first from:

- Current repo files
- Approved current docs / ADRs
- Fresh command output
- User-provided current materials
- Official documentation

When using historical memory, label it as a historical clue, and re-verify against the current source of truth before key judgments whenever possible.

### 6.4 Search Results and Web Docs

Search results default to injecting only:

- Source
- Publishing or access time
- Summary directly relevant to the problem
- Links needing citation

Technical judgments prefer primary sources.

### 6.5 Repeated Error Text

Repeated error text should first be normalized into symbol names or short labels.

For example:

- `PROMPT_POLICY_WARNING`
- `HOST_PERMISSION_DENIED`
- `TEST_TIMEOUT`
- `MISSING_AUTHORITY_SOURCE`

Only retain the smallest original excerpt during initial location or precise troubleshooting.

For repeated errors like `PROMPT_POLICY_WARNING`, use short labels in subsequent discussion. Full error text is only retained when:

- Initial location
- An upstream request ID / trace ID is needed for server-side tracing
- Confirming whether the error text has changed

Do not recirculate complete error text repeatedly in long sessions.

---

## 7. Output Contract

When prompt hygiene affects the current judgment, the output must state at minimum:

- Whether the current judgment uses summarized or original evidence
- Which raw materials were not loaded in full
- Whether information is insufficient
- What should be read back next for higher confidence

Recommended format:

```text
Facts:
- ...

Evidence Used:
- summary: ...
- raw excerpt: ...

Not Loaded:
- full log / full transcript / full search results

Confidence:
- A / B / C, with why

Next Evidence:
- ...
```

---

## 8. Drift Signals

The following indicate prompt hygiene is weakening Aegis:

- Skipping baseline reading for brevity
- Skipping evidence to reduce context
- Substituting current authority with memory
- Claiming verification without original evidence
- Not marking unknowns
- Only giving suggestions for high-risk tasks, without impact scope and verification boundaries
- Packaging context budget problems as business conclusions

The following indicate prompt hygiene governance is insufficient:

- Injecting complete skills / docs / logs every round
- Repeatedly carrying old error text
- Large tool output persistent in prompt
- Historical diagnostic materials continuously recirculating in long sessions
- Multiple workflow skills simultaneously persistent without exit mechanisms

---

## 9. Relationship with Runtime-Ready Artifacts

This document reinforces the following artifacts:

- `BaselineReadSetHint`
- `EvidenceBundleDraft`
- `SubagentContextPacket`
- `TodoCheckpointDraft`
- `ResumeStateHint`
- `DriftCheckDraft`

Among them, `EvidenceBundleDraft` should preferentially save the evidence
index, not the full raw material text. `SubagentContextPacket` should carry
bounded task context and must-read excerpts, not a full conversation dump.

The future runtime core can read back original evidence based on these indexes and make authoritative sufficiency judgments; the current method pack only provides draft / hint / projection.
