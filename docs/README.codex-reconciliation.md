# Optional Codex record reconciliation

Status: experimental opt-in advisory profile; current-build diagnostic gate passed.
Operator review is required. This profile is not part of the published v2.11.0 release.

This optional Codex CLI profile checks inherited task records against selected
before-work evidence, then checks whether the active records and final reply
correct real contradictions. It targets the record/disclosure behavior in
[issue #67](https://github.com/GanyuanRan/Aegis/issues/67) for the explicitly
enabled profile. Ordinary Aegis skill-only sessions retain the known limitation.

## Scope

- The operator selects complete record files and bounded evidence files or line
  windows. No recursive source discovery or transcript parsing is performed.
- `UserPromptSubmit` captures the selected before-state and obtains a separate
  advisory assessment. Missing or inconclusive evidence stops the prompt and
  reports that the check needs verification.
- `Stop` reviews the selected records and latest reply. It may request at most
  two correction passes of its own. Accurate inherited claims must not be called
  false. The profile layers onto existing config, so other hooks may also run;
  this extension never vetoes their continuations.
- Each selected record must itself explain the accurate resume-time state and
  correct the old false claim. The final reply must independently describe that
  claim and why it was wrong. A new completion entry or generic change list does
  not provide the missing explanation on either surface.
- Reviewers use read-only model invocations. Enabling the profile adds model
  usage and latency: one initial assessment and up to three final reviews,
  plus any host correction turns. Running Codex without this profile adds no
  reconciliation calls.
- Unresolved, failed or exhausted checks emit `systemMessage` and write a private
  `needs-verification` receipt when storage is usable. A Stop
  hook cannot retract a reply already streamed by the host. Consumers must
  inspect the terminal status rather than treating the first draft as final.

This is an advisory record-consistency check. It does not establish task
correctness, historical test execution, evidence completeness, governance
truth, an authoritative `GateDecision`, or completion authority. Code tests
and requirement acceptance remain separate.

## Install and enable

Use Python 3.10+ and the Codex CLI. From the Aegis checkout, choose the project,
its full task record, and enough source evidence to assess that record:

```bash
python3 extensions/codex-reconciliation/profile.py \
  --workspace /path/to/project \
  --record HANDOFF.md \
  --evidence src/worker.py:1:120 \
  --model YOUR_MODEL --effort xhigh
```

Repeat `--record` and `--evidence` as needed. Paths are relative to the selected
workspace. Installer `--model` and `--effort` select the read-only assessors;
choose the worker's model in Codex itself. Evidence accepts a whole file or
`path:first-line:last-line`; records
must be complete files. Inputs must be UTF-8, with no symlinks: at most 32
selections, 16 KiB per excerpt and 64 KiB of selected text in total. A source file
must be at most 2 MiB before selecting its line window. Incomplete evidence is
reported as inconclusive, not guessed.

The installer prints `profile`, `profileFile` and `config`. Start Codex with the
printed name, review the displayed hook commands, and explicitly trust them:

```bash
codex -p PRINTED_PROFILE_NAME -C /path/to/project
```

In the Codex hook review screen, both `UserPromptSubmit` and `Stop` must be active.
Use `/hooks` to inspect them. The installer never writes host trust decisions.
Automated validation may use the host trust override in an isolated environment;
that does not replace the interactive trust step for an ordinary installation.

`--codex-home` selects a different Codex home. Set the same `CODEX_HOME` when
launching Codex. `--codex` selects the executable used by assessors; Windows
requires the native executable, not a `.cmd` or PowerShell shim. Assessors reuse
the selected Codex home's authentication but ignore user configuration and rules.
Shell/unified execution, apps, plugins, multi-agent, browser/computer use, image
generation and web search are disabled for assessors; any observed tool event
invalidates the check. This is not proof that every possible host capability is
unavailable. Custom provider configuration is outside the verified scope.

## Trust and lifecycle boundary

The installer generates a distinct named Codex profile for an explicit workspace
and selected inputs. It preserves the normal user configuration and existing
host/plugin distribution. Users choose the profile and review and trust its hook
definitions; installation alone does not authorize execution.

Code is copied outside the workspace into a versioned installation. Profile names
and hook commands bind the selected configuration and code fingerprints. Reinstall
after code or selector changes, select the new profile, and review its new hook
definitions. Existing sessions continue using their installed version. Hook trust
is not a sandbox against another process with the same user's filesystem access.

The initial live target is Codex CLI 0.146.0 on Linux. Other versions, live Windows
use, Codex Desktop and other hosts require separate evidence. Source snapshots, model
judgments and candidate replies remain private in the generated profile's data
directory outside the working project. Do not publish that directory.

Use only one active task in the selected workspace, including other Codex sessions
or agents. The operator must enforce this restriction: the extension does not
prevent a second session. Before/after hashes detect source changes during the
assessment windows; they do not prove exclusive access throughout task execution.

The default assessor deadline is 300 seconds; the outer hook deadline is 330
seconds. A killed host/hook, unavailable Python, denied trust or unwritable storage
can prevent a terminal receipt. Missing, stale, `capturing`, `active`, or `repair-requested`
receipts are unverified. Check the receipt's session/turn identity, configuration
fingerprint and timestamp. A CLI exit code of zero is not evidence of reconciliation.
Do not reuse a prior turn's success after interruption or a changed configuration.
An interrupted turn stays unverified even if a later turn passes against a new
capture; this extension does not merge task history across user turns or sessions.

Codex CLI 0.146.0's interactive UI displays the hook warning. In the tested
`exec --json` surface, that warning is absent from JSONL and stderr even though
the failure receipt is written. Automation must consume the matching private
receipt; neither the JSONL completion event nor the `-o` reply file establishes
that reconciliation succeeded.

Each turn's `result.json` is under `runs/` next to the printed private `config`
file. `reconciled` means only that the selected active records and latest reply
passed this advisory check. The evidence may still be incomplete or the model's
interpretation wrong. Read the accompanying assessment/review when accepting the
result; code tests and requirement verification remain necessary.

The extension allows two corrective continuations and at most three final
reviews per turn. Unclear record supersession or disclosure may be clarified
within that budget; uncertainty never counts as reconciliation. Missing or
uncertain before-work evidence still blocks preflight. An interrupted preflight
cannot be reused as a valid capture.
The initial assessment is contestable. A review that detects an adopted dispute
of that assessment in the active record or reply retains its exact quote and
ends this check as `needs-verification` without another correction request.
This does not decide that the dispute is right; the selected evidence and
interpretation need operator review. Dispute recognition is still model-mediated.
Corrections may cover related claims together when subject, scope and time are
clear. Review the complete record and reply for later denial or re-scoping;
quotation matching alone proves text presence, not semantic adoption.
A normal new user turn receives a new capture. Stop-generated corrections on the
verified CLI retain the original turn and frozen evidence. Missing or unrecognized
turn identity is unverified; no transcript heuristics are used to infer it.

Selected records must remain readable through closeout. Evidence files may be
retired after capture. A new user turn captures current state afresh, so update
the evidence selection and install a new profile if retired files were selected.

To disable the extension, start Codex without this named profile. To uninstall,
close sessions using it and remove only the printed profile file and its matching
private data directory after retaining any evidence you need. Reinstalling identical
inputs is idempotent; the installer refuses to overwrite an altered existing
installation. Changed code/configuration produces a new profile requiring review.

## Evidence and lifecycle

Installation and native lifecycle checks passed in the stated environment.
The current frozen skills and extension then passed S1–S4 three times each:
all twelve attempts met independent record/reply review and original code tests,
including accurate-record and three-short-bullets controls. No attempt in this
batch was invalid or replaced. This meets the selected-case diagnostic gate;
it does not establish general automatic-fix reliability.

Earlier evidence remains relevant: independent review rejected two model success
receipts in the first twelve-run candidate. A later policy clarification produced
differing judgments on an ambiguous-record control; its stricter oracle was
subsequently qualified as described in the evidence notes. Deterministic quote
matching and successful code tests do not establish semantic interpretation.
Operator review of the original evidence, active record and final reply remains
required. Default skill-only #67 is unresolved; no frozen matrix-v7 improvement
follows from these non-blind development diagnostics.

See [diagnostic preparation and evidence](../tests/codex-reconciliation/README.md)
for the deterministic command and repeatable native inputs.

Re-evaluate this optional path when a verified native host/skill flow meets
the same correction, disclosure and false-accusation checks with less cost.

## Host contracts

- [Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Plugin hook trust](https://developers.openai.com/plugins/build/plugins)
