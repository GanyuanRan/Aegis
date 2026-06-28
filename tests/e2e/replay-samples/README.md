# Controlled Replay Samples

This directory contains prompts and expected behavior contracts for controlled
agentic replay samples.

The samples use small fixture projects from
`tests/e2e/fixtures/replay-projects/`. They are replay inputs for captured
transcripts by default.

Live host capture is opt-in through `tests/e2e/live-replay-capture.sh` and
requires `AEGIS_LIVE_REPLAY=1`. The live capture path currently prepares only a
single `aegis-auto` arm; it does not fabricate a trustworthy no-Aegis baseline.
