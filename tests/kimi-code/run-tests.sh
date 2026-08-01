#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
elif command -v python >/dev/null 2>&1 && python -V >/dev/null 2>&1; then
    PYTHON_CMD=(python)
else
    echo "Python 3 is required (tried python3, py -3, and python)." >&2
    exit 1
fi

integration=0
if [[ "${1:-}" == "--integration" ]]; then
    integration=1
elif [[ $# -gt 0 ]]; then
    echo "Usage: $0 [--integration]" >&2
    exit 1
fi

echo "=== Kimi Code Deterministic Checks ==="
"${PYTHON_CMD[@]}" tests/helpers/validate_kimi_skills.py .
"${PYTHON_CMD[@]}" tests/helpers/validate_host_adapter_smoke.py .
"${PYTHON_CMD[@]}" -m unittest tests.helpers.test_aegis_doctor
"${PYTHON_CMD[@]}" -m unittest tests.helpers.test_evaluate_kimi_trigger_smoke
bash tests/e2e/aegis-doctor-check.sh
bash tests/e2e/kimi-code-host-boundary-check.sh

if [[ $integration -eq 0 ]]; then
    echo ""
    echo "Kimi Code deterministic checks passed."
    exit 0
fi

KIMI_BIN="${KIMI_CMD:-kimi}"
if ! command -v "$KIMI_BIN" >/dev/null 2>&1; then
    echo "[SKIP] environment-bound: Kimi Code CLI is not available as $KIMI_BIN"
    exit 0
fi

echo ""
echo "=== Kimi Code Environment-Bound Integration ==="
"$KIMI_BIN" --version
KIMI_DATA_ROOT="${KIMI_CODE_HOME:-$HOME/.kimi-code}"
PLUGIN_ROOT="$("${PYTHON_CMD[@]}" - "$KIMI_DATA_ROOT/plugins/installed.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
if not path.is_file():
    raise SystemExit("Kimi plugin registry is missing; install Aegis with /plugins first")
data = json.loads(path.read_text(encoding="utf-8"))
records = [item for item in data.get("plugins", []) if item.get("id") == "aegis" and item.get("enabled") is True]
if len(records) != 1:
    raise SystemExit("exactly one enabled Aegis plugin is required")
print(records[0]["root"])
PY
)"
"${PYTHON_CMD[@]}" "$PLUGIN_ROOT/scripts/aegis-doctor.py" --json --host-profile kimi-code-auto
echo "Kimi Code plugin contract integration passed; model routing still requires run-live-smoke.sh."
