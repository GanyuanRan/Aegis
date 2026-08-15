#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

integration=0
if [[ "${1:-}" == "--integration" ]]; then
    integration=1
elif [[ $# -gt 0 ]]; then
    echo "Usage: $0 [--integration]" >&2
    exit 1
fi

echo "=== DeepSeek Harness Deterministic Checks ==="
bash tests/e2e/deepseek-harness-host-boundary-check.sh

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    python3 tests/helpers/validate_host_adapter_smoke.py .
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    py -3 tests/helpers/validate_host_adapter_smoke.py .
else
    python tests/helpers/validate_host_adapter_smoke.py .
fi

if [[ $integration -eq 0 ]]; then
    echo "DeepSeek Harness deterministic checks passed."
    exit 0
fi

DSH_BIN="${DSH_CMD:-dsh}"
if ! command -v "$DSH_BIN" >/dev/null 2>&1; then
    echo "[SKIP] environment-bound: DeepSeek Harness CLI is not available as $DSH_BIN"
    exit 0
fi
if ! command -v pnpm >/dev/null 2>&1; then
    echo "[SKIP] environment-bound: pnpm is required by dsh plugin management"
    exit 0
fi

echo "=== DeepSeek Harness Isolated Bundle Integration ==="
tmp_root="$(mktemp -d)"
case "$tmp_root" in
    /tmp/*|/var/tmp/*|"${TMPDIR:-/tmp}"/*) ;;
    *) echo "Refusing unsafe temporary path: $tmp_root" >&2; exit 1 ;;
esac
trap 'rm -rf -- "$tmp_root"' EXIT

export DSH_HOME="$tmp_root/dsh-home"
"$DSH_BIN" plugin --profile web add "$REPO_ROOT"
"$DSH_BIN" plugin --profile web list --depth 0 >/dev/null

dump="$($DSH_BIN --profile web --dump-config)"
[[ "$(grep -c 'id: aegis-method-pack' <<<"$dump")" -eq 1 ]]
grep -q 'name: aegis/extensions/dsh/index.js' <<<"$dump"
"$DSH_BIN" --profile web --help >/dev/null

node - "$DSH_HOME/profiles/web/package.json" <<'NODE'
const fs = require('node:fs')
const manifest = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))
if (manifest.dependencies?.aegis === undefined) throw new Error('profile dependency aegis is missing')
const bundles = manifest.dsh?.profile?.bundles ?? []
if (bundles.filter(name => name === 'aegis').length !== 1) {
  throw new Error('profile must contain exactly one aegis bundle')
}
NODE

"$DSH_BIN" plugin --profile web remove aegis
dump="$($DSH_BIN --profile web --dump-config)"
if grep -q 'aegis-method-pack' <<<"$dump"; then
    echo "Aegis bundle row remained after profile removal" >&2
    exit 1
fi

echo "DeepSeek Harness isolated bundle integration passed."
