#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

echo "=== Agentic Benchmark Render Check ==="

mkdir -p "$REPO_ROOT/.tmp"
projection_root="$(mktemp -d "$REPO_ROOT/.tmp/agentic-render-check.XXXXXX")"
trap 'rm -rf -- "$projection_root"' EXIT

if "${PYTHON_CMD[@]}" -m py_compile tests/helpers/render_agentic_benchmark.py; then
    pass "renderer compiles"
else
    fail "renderer compiles"
fi

if "${PYTHON_CMD[@]}" tests/helpers/render_agentic_benchmark.py self-test; then
    pass "standard and extended positive, neutral and negative golden projections"
else
    fail "standard and extended positive, neutral and negative golden projections"
fi

"${PYTHON_CMD[@]}" - "$projection_root/private.json" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, "tests/helpers")
from render_agentic_benchmark import canonical_json, synthetic_private

Path(sys.argv[1]).write_text(canonical_json(synthetic_private("positive", "standard-held-out")), encoding="utf-8")
PY

if "${PYTHON_CMD[@]}" tests/helpers/render_agentic_benchmark.py sanitize \
    --private-report "$projection_root/private.json" \
    --output-json "$projection_root/public.json" \
    && "${PYTHON_CMD[@]}" tests/helpers/render_agentic_benchmark.py render \
        --report "$projection_root/public.json" \
        --svg "$projection_root/result-a.svg" \
        --markdown-en "$projection_root/result-a.en.md" \
        --markdown-zh "$projection_root/result-a.zh.md" \
    && "${PYTHON_CMD[@]}" tests/helpers/render_agentic_benchmark.py render \
        --report "$projection_root/public.json" \
        --svg "$projection_root/result-b.svg" \
        --markdown-en "$projection_root/result-b.en.md" \
        --markdown-zh "$projection_root/result-b.zh.md" \
    && cmp -s "$projection_root/result-a.svg" "$projection_root/result-b.svg" \
    && cmp -s "$projection_root/result-a.en.md" "$projection_root/result-b.en.md" \
    && cmp -s "$projection_root/result-a.zh.md" "$projection_root/result-b.zh.md"; then
    pass "sanitize/render CLI projection is byte-identical"
else
    fail "sanitize/render CLI projection is byte-identical"
fi

if rg -n '/home/|/Users/|[A-Za-z]:\\|session[_-]?id|rollout[_-]?id|sk-[A-Za-z0-9_-]{16,}' \
    "$projection_root/public.json" "$projection_root/result-a.svg" \
    "$projection_root/result-a.en.md" "$projection_root/result-a.zh.md" >/dev/null; then
    fail "generated projection excludes machine paths, IDs and credentials"
else
    pass "generated projection excludes machine paths, IDs and credentials"
fi

if rg -q '0%' "$projection_root/result-a.svg" \
    && rg -q '100%' "$projection_root/result-a.svg" \
    && rg -q 'standard-held-out.*n=40 runs / 20 cases' "$projection_root/result-a.svg" \
    && rg -q 'Repeated-run evidence is unsupported' "$projection_root/result-a.en.md" \
    && rg -q 'lower is better' "$projection_root/result-a.svg" \
    && [[ "$(rg -c '<text class="label" x="40"' "$projection_root/result-a.svg")" -eq 10 ]]; then
    pass "SVG uses a zero-based scale, ten class comparisons and unsafe panel"
else
    fail "SVG uses a zero-based scale, ten class comparisons and unsafe panel"
fi

if rg -n 'sanitized_report|SANITIZED_REPORT_TYPE|render-input|subparsers\.add_parser\("sanitize"' tests/helpers/run_agentic_benchmark.py >/dev/null; then
    fail "runner no longer owns public sanitization or rendering"
else
    pass "runner no longer owns public sanitization or rendering"
fi

if [[ -f benchmarks/README.md ]] \
    && rg -q '40 `standard-held-out`' benchmarks/README.md \
    && rg -q '120 `extended-held-out`' benchmarks/README.md \
    && rg -q 'No result is currently published' benchmarks/README.md \
    && rg -q 'advisory' benchmarks/README.md \
    && rg -qi 'raw logs' benchmarks/README.md; then
    pass "benchmark evidence boundary is documented"
else
    fail "benchmark evidence boundary is documented"
fi

if find benchmarks/results assets/benchmarks -type f \( -name '*.json' -o -name '*.svg' \) -print -quit 2>/dev/null | grep -q .; then
    fail "no real benchmark result or chart is published before authorization"
else
    pass "no real benchmark result or chart is published before authorization"
fi

if (( failures > 0 )); then
    echo
    echo "Agentic benchmark render check failed: $failures"
    exit 1
fi

echo
echo "Agentic benchmark render check passed."
