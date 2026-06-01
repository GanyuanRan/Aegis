# Scenario E: Local GREEN Is Not Final Completion

This scenario validates the TDD completion boundary after one strict TDD slice
reaches GREEN.

It checks that Aegis can represent:

- GREEN as proof of the current behavior slice only
- `Slice Card` scope versus parent acceptance scope
- `Goal Closure` downgrade to `needs-verification` when parent acceptance is
  still open
- visible covered and uncovered scope in the closeout
- continued task state through `TodoCheckpointDraft` and `EvidenceBundleDraft`

This is a fixture-backed Method Pack scenario. It does not simulate live host
execution and does not grant completion authority.
