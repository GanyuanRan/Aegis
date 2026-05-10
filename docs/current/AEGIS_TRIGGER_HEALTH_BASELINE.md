# Aegis Trigger Health Baseline

Status: `Reviewed`

## 1. Document Scope

This document defines the trigger-health diagnostic loop for the
`Aegis Method Pack`.

It answers:

- how to diagnose "Aegis is installed but the right skill does not trigger"
- how to separate install/discovery failures from routing failures
- how to improve automatic skill invocation without making `using-aegis`
  heavier

It does not answer:

- authoritative runtime routing decisions
- host adapter implementation details
- final evidence sufficiency

---

## 2. Bottom Line

If a representative task does not reliably trigger the expected Aegis skill,
do not first add more keywords to a skill description.

Treat the failure as a trigger-chain diagnosis:

1. install and version visibility
2. host skill discovery
3. activation mode and bootstrap entry
4. `using-aegis` router entry
5. task-to-skill routing
6. skill execution depth
7. context pressure and re-entry
8. false positive over-triggering

Fix the layer that owns the failure. Do not move all responsibility into
`using-aegis`.

---

## 3. Trigger Health Layers

### L0 Install And Version

Question:

- Is the installed method-pack root the expected version?

Evidence:

- `python scripts/aegis-doctor.py --json`
- `bash scripts/bump-version.sh --check` in the method-pack checkout
- release tag / commit readback when testing a published install

Failure owner:

- install or update path

### L1 Discovery

Question:

- Can the host see the current `skills/` directory?

Evidence:

- `python scripts/aegis-doctor.py --discovery-root <host-skill-discovery-root>`
- host-specific `/skills`, plugin reload, or fresh-session smoke

Failure owner:

- host discovery directory, symlink/junction/copy path, reload/restart boundary

### L2 Activation

Question:

- Is automatic bootstrap expected in this host and this activation mode?

Evidence:

- `docs/current/AEGIS_ACTIVATION_MODE.md`
- user-local `activation_mode`
- host-specific install guide

Failure owner:

- activation mode, bootstrap hook, host profile, or explicit-only install

### L3 Router Entry

Question:

- Does `using-aegis` enter the decision path when it should?

Evidence:

- explicit call to `aegis:using-aegis`
- host transcript showing `using-aegis` was loaded
- global user rule / bootstrap prompt presence

Failure owner:

- global rule, bootstrap context, host startup injection, or skill discovery

### L4 Skill Routing

Question:

- Given the user task, does the router select the expected skill?

Evidence:

- trigger-health fixture matrix
- explicit skill request comparison
- skill description boundary review

Failure owner:

- skill description trigger wording, skill boundary overlap, or routing order

### L5 Execution Depth

Question:

- If the right skill loaded, did it execute deeply enough?

Evidence:

- required output markers, quality gates, and hard-signal fields
- scenario transcript analysis

Failure owner:

- skill body, quality gate, stop condition, or verification requirement

### L6 Context Pressure And Re-entry

Question:

- After a long session, heavy tool output, resume, or context compaction, does
  the agent re-enter Aegis routing before continuing non-trivial work?

Evidence:

- transcript shows a compact re-entry check after compaction or resume
- explicit call to `aegis:using-aegis` restores the expected route
- trigger-health fixture comparing clean context with context-pressure prompts

Failure owner:

- re-entry cue, host compaction boundary, or manual explicit invocation path

Re-entry rule:

- Do not assume the original startup route is still active under context
  pressure. Re-check: current task type, relevant Aegis skill, baseline/plan or
  debugging gate, and verification gate.
- If a task-specific skill applies, load it before continuing. If not, state the
  fast-path reason and continue.

### L7 False Positive Control

Question:

- Is Aegis triggering on simple tasks that should stay on the fast path?

Evidence:

- negative trigger-health samples
- compact `using-aegis` hot-path budget

Failure owner:

- overbroad description, overbroad global rule, or too-heavy hot path

---

## 4. Representative Trigger Matrix

Trigger health uses stable, representative prompts rather than ad hoc feelings.

Minimum samples:

| Sample | Expected Primary Skill | Allowed Secondary Skill | Must Not Do |
| --- | --- | --- | --- |
| Quick shared-module bug fix | `systematic-debugging` | `verification-before-completion` | Jump straight to code |
| Failing test diagnosis | `systematic-debugging` | `test-driven-development` | Modify tests before locating owner |
| New ambiguous feature | `brainstorming` | `writing-plans` | Start implementation immediately |
| Approved implementation plan | `writing-plans` or `executing-plans` | `test-driven-development` | Re-design without cause |
| Release or completion claim | `verification-before-completion` | `requesting-code-review` | Claim completion without evidence |
| Repeated fixes / fallback growth | `systematic-debugging` | `first-principles-review` | Add another local patch |
| Post-compaction bug continuation | `using-aegis` | `systematic-debugging`, `verification-before-completion` | Continue without re-entry |
| Simple factual Q&A | none or `using-aegis` only | none | Force full workflow |
| Tiny wording edit | none or fast path | none | Create project workspace records |

The matrix checks both false negatives and false positives.

---

## 5. Root Improvements For Automatic Invocation

The stable path is not to make every entry point louder. It is to keep each
owner narrow:

1. Keep `using-aegis` compact and route-only.
2. Keep skill descriptions trigger-oriented; do not summarize workflow in
   descriptions.
3. Keep detailed rules inside the owning skill body.
4. Add representative trigger-health fixtures before changing descriptions.
5. When a trigger fails, classify the failed layer before editing.
6. Prefer better boundary wording over broad keyword stuffing.
7. Preserve explicit invocation as the override path.
8. Keep simple tasks cheap so users do not disable Aegis due to over-triggering.
9. Under context pressure or after compaction/resume, run a compact re-entry
   check instead of assuming the initial route still holds.

---

## 6. Failure Report Shape

When trigger health fails, report:

```text
TriggerHealthLayer:
ObservedPrompt:
ExpectedSkill:
ActualSkill:
FailureType: install | discovery | activation | router-entry | routing | depth | context-pressure | false-positive
CanonicalOwner:
SmallestFix:
Verification:
```

If the failed layer is unknown, do not change skill text yet. First collect
install, discovery, activation, and explicit invocation evidence.

---

## 7. Boundary

Trigger health is advisory method-pack verification. It can show whether the
method-pack routing surface is likely healthy. It does not grant authoritative
runtime decisions, final gate decisions, or completion authority.
