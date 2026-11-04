#!/usr/bin/env bash
# Guard the per-skill instruction surface against compaction loss.
#
# Claude Code re-attaches each skill after a compaction only up to 20,000
# characters of its SKILL.md; anything past that point is gone for the rest of
# the session. A skill that crosses the limit therefore loses rules mid-session
# without any error, which is why this is a hard failure rather than a warning.
#
# The limit applies to the always-resident instruction surface, not to the
# on-demand references a skill reads for one activated section.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

HARD_LIMIT=20000
WARN_AT=18000

failures=0
warnings=0

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

warn() {
    echo "  [WARN] $1"
    warnings=$((warnings + 1))
}

echo "=== Skill Instruction Surface Budget Check ==="
echo "Hard limit: ${HARD_LIMIT} bytes per skills/*/SKILL.md"

shopt -s nullglob
skill_files=(skills/*/SKILL.md)
shopt -u nullglob

if [[ ${#skill_files[@]} -eq 0 ]]; then
    fail "at least one skills/*/SKILL.md is discovered"
else
    echo "  [PASS] discovered ${#skill_files[@]} skill instruction surfaces"
fi

for skill_file in "${skill_files[@]}"; do
    bytes=$(wc -c <"$skill_file" | tr -d '[:space:]')
    if (( bytes >= HARD_LIMIT )); then
        fail "$skill_file is ${bytes} bytes and would be truncated after compaction (limit ${HARD_LIMIT}); move evidence-conditional detail into a reference the skill reads on demand"
    elif (( bytes >= WARN_AT )); then
        warn "$skill_file is ${bytes} bytes, within $((${HARD_LIMIT} - bytes)) bytes of the compaction limit"
    fi
done

# The comparison has to be able to fail: prove it triggers on an oversize file
# instead of trusting a green run that never exercises the branch.
tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/aegis-skill-size.XXXXXX")"
trap 'rm -rf -- "$tmp_dir"' EXIT
python - "$tmp_dir/oversize.md" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_text("x" * 20001, encoding="utf-8")
PY
synthetic_bytes=$(wc -c <"$tmp_dir/oversize.md" | tr -d '[:space:]')
if (( synthetic_bytes >= HARD_LIMIT )); then
    echo "  [PASS] limit comparison triggers on a ${synthetic_bytes}-byte control file"
else
    fail "limit comparison does not trigger on an oversize control file"
fi

if (( failures > 0 )); then
    echo
    echo "Skill instruction surface budget check failed: $failures"
    exit 1
fi

if (( warnings > 0 )); then
    echo
    echo "Skill instruction surface budget check passed with ${warnings} warning(s)."
    exit 0
fi

echo
echo "Skill instruction surface budget check passed."
