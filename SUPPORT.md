# Support

## What this repository is

This repository currently publishes:

> `Aegis Method Pack (runtime-ready)`

It provides method-pack skills, distribution skeletons, host installation guidance, and verification assets.

It does **not** currently provide the full `Aegis Platform`.

## Where to start

Before asking for help, read:

1. `docs/current/README.md`
2. `docs/current/AEGIS_KNOWN_LIMITATIONS.md`
3. `docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md`
4. the relevant host guide, such as `docs/README.codex.md`,
   `docs/README.opencode.md`, `docs/README.codebuddy.md`,
   `docs/README.deepseek-tui.md`, or `docs/README.trae.md`
5. `docs/testing.md`

## How to get help

Use the path that best matches your problem:

### 1. Bug reports

Open a GitHub issue using the bug report template when:

- behavior regressed
- installation no longer works as documented
- a supported check now fails unexpectedly

Include:

- host
- version
- reproduction steps
- logs or transcript evidence

### 2. Feature requests

Open a GitHub issue using the feature request template when:

- you can describe a real problem
- the proposed change still belongs in method-pack scope

### 3. Security-sensitive issues

Do not file those publicly.

Follow `SECURITY.md`.

## Before filing an issue

Please check:

1. whether the issue reproduces without Aegis installed
2. whether the host is currently in the fresh-evidence compatibility set
3. whether the behavior is already covered by known limitations

## Current support boundary

Current fresh-evidence host coverage is centered on:

- `Codex`
- `OpenCode`

Other hosts may still be product targets, but are not automatically current release-level verdicts.

## What maintainers may ask for

To reduce guesswork, maintainers may ask you for:

- exact command used
- full error output
- a minimal reproduction
- transcript excerpts
- host version and model/provider details

## Response boundary

Support help in this repository is best-effort and bounded by the current method-pack scope.

If the real issue belongs to a host platform, marketplace, or future runtime layer, you may be redirected to the correct owner.
