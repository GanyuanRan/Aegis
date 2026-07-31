#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Live Replay Capture Check ==="

bash "$SCRIPT_DIR/live-replay-capture.sh" \
    --sample change-necessity-before-edit \
    --arm aegis-auto \
    --host codex \
    --workspace-root .tmp/e2e-live-replay-dry-run \
    --dry-run

if grep -q "AEGIS_LIVE_REPLAY=1" tests/e2e/live-replay-capture.sh; then
    echo "  [PASS] live replay requires explicit opt-in"
else
    echo "  [FAIL] live replay requires explicit opt-in"
    exit 1
fi

if grep -q "currently supports only aegis-auto" tests/e2e/live-replay-capture.sh; then
    echo "  [PASS] no-Aegis baseline is not fabricated by live capture"
else
    echo "  [FAIL] no-Aegis baseline guard is missing"
    exit 1
fi

if CODEX_SMOKE_SUFFIX="" bash -lc 'source tests/helpers/codex-cli.sh; [[ -z "$codex_smoke_suffix" ]]'; then
    echo "  [PASS] Codex live replay can preserve the original prompt"
else
    echo "  [FAIL] Codex empty smoke suffix override is not honored"
    exit 1
fi

benchmark_helper_log=".tmp/live-replay-capture-check/benchmark-helper.log"
mkdir -p "$(dirname "$benchmark_helper_log")"
CODEX_BENCHMARK_CMD='printf "%s\n"' \
CODEX_SMOKE_SUFFIX='must-not-appear-in-benchmark-prompt' \
bash -lc 'source tests/helpers/codex-cli.sh; run_codex_benchmark_capture "benchmark-prompt-sentinel" ".tmp" "$1"' \
    _ "$benchmark_helper_log"

if grep -Fxq -- '--json' "$benchmark_helper_log" \
    && grep -Fxq -- '--sandbox' "$benchmark_helper_log" \
    && grep -Fxq -- 'workspace-write' "$benchmark_helper_log" \
    && grep -Fxq -- 'benchmark-prompt-sentinel' "$benchmark_helper_log" \
    && ! grep -q -- 'must-not-appear-in-benchmark-prompt' "$benchmark_helper_log"; then
    echo "  [PASS] focused Codex benchmark capture preserves prompt and execution flags"
else
    echo "  [FAIL] focused Codex benchmark capture drifted"
    exit 1
fi

echo ""
echo "Live replay capture check passed."
