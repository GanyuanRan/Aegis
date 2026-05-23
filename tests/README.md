# Aegis Test Surface

This directory is split into two test surfaces.

## Public Quality Verification

Tracked test suites under `tests/` are part of the public Aegis quality
verification surface. They should be reproducible from a clean checkout, or
clearly marked as optional host integration checks when they require a local
agent CLI, model access, or plugin installation.

Primary public entrypoints:

- `e2e/` - release and governance verification orchestration
- `opencode/` - OpenCode host compatibility checks
- `codex-plugin-sync/` - Codex plugin sync and publishable-set regression checks
- `helpers/` - shared parser and host bridge helpers

Optional or slower public suites:

- `claude-code/`
- `skill-triggering/`
- `explicit-skill-requests/`
- `subagent-driven-dev/`

These suites may require local host setup and should not be treated as the
default minimum verification path unless a release checklist says so.

## Local Development Tests

Use `tests/local/` for private or development-only test cases that are useful
on this machine but should not enter the public repository. Everything under
`tests/local/` is ignored by git except its README.

Local-only test cases must not become dependencies of public CI, release
checks, README commands, or current authority docs. If a local test becomes
generally useful and reproducible, move it out of `tests/local/` into the
appropriate public suite and document its entrypoint.
