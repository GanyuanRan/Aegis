#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if ! command -v rg >/dev/null 2>&1; then
    echo "ERROR: rg is required for benchmark render assertions." >&2
    exit 2
fi

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
    && ! rg -q 'Contract pass rate by scenario class|ambiguous-feature-shaping' "$projection_root/result-a.svg" \
    && [[ "$(rg -c '<text class="section"' "$projection_root/result-a.svg")" -eq 2 ]]; then
    pass "SVG uses a zero-based scale and only two overall metric panels"
else
    fail "SVG uses a zero-based scale and only two overall metric panels"
fi

en_quick_line="$(rg -n '^## Quick Install$' README.md | cut -d: -f1 || true)"
zh_quick_line="$(rg -n '^## 极简安装$' README.zh-CN.md | cut -d: -f1 || true)"
if [[ -n "$en_quick_line" && -n "$zh_quick_line" \
    && "$en_quick_line" -le 75 && "$zh_quick_line" -le 75 ]] \
    && rg -q '60%' README.md && rg -q '90%' README.md \
    && rg -q '11\.67%' README.md && rg -q '5%' README.md \
    && rg -q '60%' README.zh-CN.md && rg -q '90%' README.zh-CN.md \
    && rg -q '11\.67%' README.zh-CN.md && rg -q '5%' README.zh-CN.md \
    && rg -q 'gpt-5-6-sol-xhigh-extended-20260731\.svg' README.md README.zh-CN.md \
    && ! rg -q 'ambiguous-feature-shaping|Contract pass rate by scenario class|场景类别' README.md README.zh-CN.md; then
    pass "root READMEs keep a compact two-metric benchmark before quick install"
else
    fail "root READMEs keep a compact two-metric benchmark before quick install"
fi

if rg -n 'sanitized_report|SANITIZED_REPORT_TYPE|render-input|subparsers\.add_parser\("sanitize"' tests/helpers/run_agentic_benchmark.py >/dev/null; then
    fail "runner no longer owns public sanitization or rendering"
else
    pass "runner no longer owns public sanitization or rendering"
fi

if [[ -f benchmarks/README.md ]] \
    && rg -q '40 `standard-held-out`' benchmarks/README.md \
    && rg -q '120 `extended-held-out`' benchmarks/README.md \
    && rg -q 'current public snapshot' benchmarks/README.md \
    && rg -q 'advisory' benchmarks/README.md \
    && rg -qi 'raw logs' benchmarks/README.md; then
    pass "benchmark evidence boundary is documented"
else
    fail "benchmark evidence boundary is documented"
fi

published_result="benchmarks/results/gpt-5-6-sol-xhigh-extended-20260731"
if [[ -f "${published_result}.json" && -f "${published_result}.svg" \
    && -f "${published_result}.en.md" && -f "${published_result}.zh-CN.md" ]]; then
    pass "authorized public benchmark bundle remains complete"
else
    fail "authorized public benchmark bundle remains complete"
fi

if (( failures > 0 )); then
    echo
    echo "Agentic benchmark render check failed: $failures"
    exit 1
fi

echo
echo "Agentic benchmark render check passed."
