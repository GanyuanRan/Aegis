#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FIXTURES="$SCRIPT_DIR/fixtures/trigger-cases.json"
EVALUATOR="$REPO_ROOT/tests/helpers/evaluate_kimi_trigger_smoke.py"
KIMI_BIN="${KIMI_CMD:-kimi}"

if ! command -v "$KIMI_BIN" >/dev/null 2>&1; then
    echo "[SKIP] environment-bound: Kimi Code CLI is not available as $KIMI_BIN"
    exit 0
fi

KIMI_DATA_ROOT="${KIMI_CODE_HOME:-$HOME/.kimi-code}"
PLUGIN_ROOT="$(python3 - "$KIMI_DATA_ROOT/plugins/installed.json" <<'PY'
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
python3 "$PLUGIN_ROOT/scripts/aegis-doctor.py" --json --host-profile kimi-code-auto >/dev/null

mkdir -p "$REPO_ROOT/.tmp/kimi-code-live"
RUN_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/kimi-code-live/run.XXXXXX")"
trap 'rm -rf "$RUN_ROOT"' EXIT
RESULTS="$RUN_ROOT/results"
mkdir -p "$RESULTS"

while IFS=$'\t' read -r case_id prompt; do
    case_root="$RUN_ROOT/$case_id"
    mkdir -p "$case_root"
    git -C "$case_root" init -q
    (
        cd "$case_root"
        "$KIMI_BIN" -p "$prompt" --output-format stream-json >"$RESULTS/$case_id.jsonl"
    )
done < <(python3 - "$FIXTURES" <<'PY'
import json
import pathlib
import sys

data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for case in data["cases"]:
    print(f'{case["id"]}\t{case["prompt"]}')
PY
)

resume_root="$RUN_ROOT/resume-bug"
mkdir -p "$resume_root"
git -C "$resume_root" init -q
bug_prompt="A cache change introduced an intermittent authentication regression. Diagnose the real cause before proposing a fix. Do not modify files."
(
    cd "$resume_root"
    "$KIMI_BIN" -p "$bug_prompt" --output-format stream-json >"$RUN_ROOT/resume-base.jsonl"
    "$KIMI_BIN" -c -p "Continue the same diagnosis from the existing evidence. Do not modify files." \
        --output-format stream-json >"$RUN_ROOT/resume.jsonl"
)

python3 "$EVALUATOR" \
    --fixtures "$FIXTURES" \
    --results-dir "$RESULTS" \
    --resume-result "$RUN_ROOT/resume.jsonl"

if find "$RUN_ROOT" -path '*/.git' -prune -o -type f ! -name '*.jsonl' -print | grep -q .; then
    echo "Kimi live smoke created unexpected project files" >&2
    exit 1
fi

echo "Kimi Code live automatic-routing smoke passed."
