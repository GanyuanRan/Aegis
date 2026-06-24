#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Minimality Reference Check ==="

doc="docs/current/AEGIS_MINIMALITY_REFERENCE.md"

if [[ ! -f "$doc" ]]; then
    echo "missing $doc"
    exit 1
fi

grep -q "AEGIS_MINIMALITY_REFERENCE.md" docs/current/README.md
grep -q "Existence Check" "$doc"
grep -q "Before Adding A Skill" "$doc"
grep -q "Before Adding An Artifact" "$doc"
grep -q "Before Adding A Host Adapter" "$doc"
grep -q "Before Adding A Fallback Or Compatibility Path" "$doc"
grep -q "Before Adding A Benchmark Metric" "$doc"
grep -q "not override user instructions" "$doc"
grep -q "Existence Check" skills/brainstorming/SKILL.md
grep -q "Existence Check" skills/writing-plans/SKILL.md
grep -q "Minimality Check" skills/systematic-debugging/SKILL.md
grep -q "AEGIS_MINIMALITY_REFERENCE.md" docs/current/AEGIS_PROCESS_BASELINE.md

echo "  [PASS] minimality reference covers existence, skill, artifact, adapter, fallback, benchmark, and workflow integration boundaries"
echo ""
echo "Minimality reference check passed."
