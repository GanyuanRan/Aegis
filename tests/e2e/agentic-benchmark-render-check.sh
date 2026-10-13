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

if rg -n '/home/|/Users/|[A-Za-z]:\\|session[_-]?id|rollout[_-]?id|(^|[^A-Za-z0-9])[sS][kK]-[A-Za-z0-9_-]{16,}' \
    "$projection_root/public.json" "$projection_root/result-a.svg" \
    "$projection_root/result-a.en.md" "$projection_root/result-a.zh.md" >/dev/null; then
    fail "generated projection excludes machine paths, IDs and credentials"
else
    pass "generated projection excludes machine paths, IDs and credentials"
fi

if rg -q '0%' "$projection_root/result-a.svg" \
    && rg -q '100%' "$projection_root/result-a.svg" \
    && rg -q 'standard-held-out.*n=44 runs / 22 cases' "$projection_root/result-a.svg" \
    && rg -q 'Repeated-run evidence is unsupported' "$projection_root/result-a.en.md" \
    && rg -q 'lower is better' "$projection_root/result-a.svg" \
    && ! rg -q 'Contract pass rate by scenario class|ambiguous-feature-shaping' "$projection_root/result-a.svg" \
    && [[ "$(rg -c '<text class="section"' "$projection_root/result-a.svg")" -eq 2 ]]; then
    pass "SVG uses a zero-based scale and only two overall metric panels"
else
    fail "SVG uses a zero-based scale and only two overall metric panels"
fi

if "${PYTHON_CMD[@]}" - <<'PY'
from pathlib import Path

# Keep the 75-line entry budget; test the reader flow rather than requiring
# the full benchmark or an independent runtime's promotion before installation.
def valid_layout(text, quick, detail, runtime, metrics, boundary, link):
    lines = text.splitlines()
    def position(heading):
        hits = [i for i, line in enumerate(lines) if line == heading]
        return hits[0] if len(hits) == 1 else None
    q, d, r = (position(h) for h in (quick, detail, runtime))
    if q is None or d is None or r is None or q + 1 > 75 or not q < d < r:
        return False
    prefix = "\n".join(lines[:q])
    return (
        all(term in prefix for term in (*metrics, *boundary, link))
        and "benchmarks/results/" not in prefix
        and not any(term in text for term in (
            "ambiguous-feature-shaping", "Contract pass rate by scenario class", "场景类别"
        ))
    )

configs = (
    ("README.md", "## Quick Install", "## Measured Agentic Benchmark",
     "## Try Aegis Methods in a Coding Runtime",
     ("pass rate **61.67% → 93.33%", "unsafe outcomes **13.33% → 0%**"),
     ("Aegis 2.7.6", "2026-08-11", "bounded advisory evidence",
      "not a measurement of this release", "completion authority"),
     "[the full benchmark and its limitations](#measured-agentic-benchmark)"),
    ("README.zh-CN.md", "## 极简安装", "## 实测 Agentic Benchmark",
     "## 体验 Aegis 方法在运行时中的应用",
     ("**61.67% → 93.33%**", "不安全结果 **13.33% → 0%**"),
     ("Aegis 2.7.6", "2026-08-11", "有界建议性证据",
      "不是对本次发布的测量", "不构成普遍质量或完成权威声明"),
     "[完整基准与证据限制](#实测-agentic-benchmark)"),
)
negative_count = 0
for name, *config in configs:
    text = Path(name).read_text(encoding="utf-8")
    assert valid_layout(text, *config), f"invalid reader flow: {name}"
    quick, detail, runtime, metrics, boundary, link = config
    prefix, rest = text.split(quick, 1)
    # Each malformed variant must fail the same validator used for real files.
    variants = {
        "late installation": "\n" * 75 + text,
        "missing installation": text.replace(quick, "## Missing install"),
        "duplicate installation": text + "\n" + quick,
        "summary after installation": quick + rest + prefix,
        "details before installation": detail + "\n" + text.replace(detail, ""),
        "runtime before installation": runtime + "\n" + text.replace(runtime, ""),
        "missing details": text.replace(detail, "## Missing details"),
        "full chart before installation": "![chart](benchmarks/results/result.svg)\n" + text,
        "scenario table": text + "\nContract pass rate by scenario class\n",
        "missing evidence link": text.replace(link, ""),
    }
    for i, term in enumerate((*metrics, *boundary)):
        variants[f"missing summary fact {i}"] = prefix.replace(term, "") + quick + rest
    for label, variant in variants.items():
        assert not valid_layout(variant, *config), f"negative control accepted: {name}: {label}"
        negative_count += 1
    print(f"  [PASS] {name}: quick install at line {len(prefix.splitlines()) + 1}")
print(f"  [PASS] README layout negative controls: {negative_count}")
PY
then
    pass "root READMEs keep bounded evidence before early install, with details and runtime after it"
else
    fail "root READMEs keep bounded evidence before early install, with details and runtime after it"
fi

if "${PYTHON_CMD[@]}" - <<'PY'
from pathlib import Path


def in_benchmark_section(text, heading, phrase):
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        return False
    start = starts[0] + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return phrase in "\n".join(lines[start:end])


configs = (
    ("README.md", "## Measured Agentic Benchmark", "requested the same"),
    ("README.zh-CN.md", "## 实测 Agentic Benchmark", "请求相同的"),
)
negative_count = 0
for name, heading, phrase in configs:
    text = Path(name).read_text(encoding="utf-8")
    assert in_benchmark_section(text, heading, phrase), f"missing comparison qualification: {name}"
    without_phrase = text.replace(phrase, "")
    variants = {
        "missing qualification": without_phrase,
        "qualification before benchmark": phrase + "\n" + without_phrase,
        "qualification after benchmark": without_phrase + "\n" + phrase,
        "qualification in another section": text.replace(phrase, "\n## Another section\n" + phrase),
        "missing benchmark heading": text.replace(heading, "## Missing benchmark"),
        "duplicate benchmark heading": text + "\n" + heading,
    }
    for label, variant in variants.items():
        assert not in_benchmark_section(variant, heading, phrase), f"negative control accepted: {name}: {label}"
        negative_count += 1
print(f"  [PASS] benchmark comparison section negative controls: {negative_count}")
PY
then
    pass "full benchmark section retains the same-request comparison boundary"
else
    fail "full benchmark section retains the same-request comparison boundary"
fi

if rg -n 'sanitized_report|SANITIZED_REPORT_TYPE|render-input|subparsers\.add_parser\("sanitize"' tests/helpers/run_agentic_benchmark.py >/dev/null; then
    fail "runner no longer owns public sanitization or rendering"
else
    pass "runner no longer owns public sanitization or rendering"
fi

if [[ -f benchmarks/README.md ]] \
    && rg -q '44 `standard-held-out`' benchmarks/README.md \
    && rg -q '132 `extended-held-out`' benchmarks/README.md \
    && rg -q 'latest published extended-held-out \(pre-v7\) snapshot' benchmarks/README.md \
    && rg -q 'first published matrix-v7 snapshot' benchmarks/README.md \
    && rg -q 'advisory' benchmarks/README.md \
    && rg -qi 'raw logs' benchmarks/README.md; then
    pass "benchmark evidence boundary is documented"
else
    fail "benchmark evidence boundary is documented"
fi

published_result="benchmarks/results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6"
published_name="gpt-5-6-sol-xhigh-extended-20260811-v2-7-6"
current_links_ok=true
for readme in README.md README.zh-CN.md benchmarks/README.md; do
    for suffix in json svg en.md zh-CN.md; do
        if ! rg -Fq "${published_name}.${suffix}" "$readme"; then
            current_links_ok=false
        fi
    done
    if ! rg -Fq 'Aegis 2.7.6' "$readme" \
        || ! rg -Fq '2026-08-11' "$readme"; then
        current_links_ok=false
    fi
done

if [[ "$current_links_ok" == true ]]; then
    pass "README current pointers match the Aegis 2.7.6 snapshot"
else
    fail "README current pointers match the Aegis 2.7.6 snapshot"
fi

bundle_projection_root="$projection_root/bundles"
mkdir -p "$bundle_projection_root"
# The three pre-v7 historical bundles (validated through the renderer's
# allowlist) and the committed matrix-v7 bundles listed below. The renderer
# decides which contract applies; this loop only proves that each listed bundle
# re-renders byte-identically and carries no private material.
bundle_bases=(
    "benchmarks/results/gpt-5-6-sol-xhigh-extended-20260731"
    "benchmarks/results/gpt-5-6-sol-xhigh-extended-20260811"
    "benchmarks/results/gpt-5-6-sol-xhigh-extended-20260811-v2-7-6"
    "benchmarks/results/gpt-5-6-sol-xhigh-standard-20260913-v2-10-1"
    "benchmarks/results/gpt-5-6-sol-xhigh-standard-20260925-v2-10-8"
    "benchmarks/results/gpt-5-6-sol-xhigh-standard-20261011-v2-13-0"
)
bundle_ok=true
for bundle_base in "${bundle_bases[@]}"; do
    bundle_name="${bundle_base##*/}"
    bundle_output_root="$bundle_projection_root/$bundle_name"
    mkdir -p "$bundle_output_root"
    if [[ -f "${bundle_base}.json" && -f "${bundle_base}.svg" \
        && -f "${bundle_base}.en.md" && -f "${bundle_base}.zh-CN.md" ]] \
        && "${PYTHON_CMD[@]}" tests/helpers/render_agentic_benchmark.py render \
            --report "${bundle_base}.json" \
            --svg "$bundle_output_root/result.svg" \
            --markdown-en "$bundle_output_root/result.en.md" \
            --markdown-zh "$bundle_output_root/result.zh-CN.md" \
        && cmp -s "${bundle_base}.svg" "$bundle_output_root/result.svg" \
        && cmp -s "${bundle_base}.en.md" "$bundle_output_root/result.en.md" \
        && cmp -s "${bundle_base}.zh-CN.md" "$bundle_output_root/result.zh-CN.md" \
        && ! rg -n '/home/|/Users/|[A-Za-z]:\\|session[_-]?id|rollout[_-]?id|(^|[^A-Za-z0-9])[sS][kK]-[A-Za-z0-9_-]{16,}' \
            "${bundle_base}.json" "${bundle_base}.svg" \
            "${bundle_base}.en.md" "${bundle_base}.zh-CN.md" >/dev/null; then
        continue
    fi
    bundle_ok=false
    echo "  [FAIL DETAIL] committed bundle: $bundle_base"
done

if [[ "$bundle_ok" == true ]]; then
    pass "all ${#bundle_bases[@]} authorized committed bundles validate and match canonical rendering"
else
    fail "all ${#bundle_bases[@]} authorized committed bundles validate and match canonical rendering"
fi

if (( failures > 0 )); then
    echo
    echo "Agentic benchmark render check failed: $failures"
    exit 1
fi

echo
echo "Agentic benchmark render check passed."
