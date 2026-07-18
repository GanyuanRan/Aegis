#!/usr/bin/env bash
set -euo pipefail

PLANNED_EXIT=90
STALE_SOURCE_EXIT=91
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MATRIX="$SCRIPT_DIR/fixtures/context-semantic-infrastructure-matrix.json"

HOST=""
SOURCE_MODE=""
CASE_ID=""
CLEANUP_SUCCESS=0

usage() {
    cat <<'EOF'
Usage: context-semantic-infrastructure-live-check.sh --host codex|claude --source-mode checkout-explicit|installed|checkout-plugin [--case ID] [--cleanup-success]

Real execution requires AEGIS_CONTEXT_LIVE=1.

Source modes:
  checkout-explicit  Codex reads exact skill files from this checkout; behavior evidence only.
  installed          Codex uses its installed skills after fingerprint equality is proven.
  checkout-plugin    Claude loads this checkout through --plugin-dir.

Optional environment:
  AEGIS_INSTALLED_SKILL_ROOT  Host-visible installed Aegis skills directory.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --host) HOST="$2"; shift 2 ;;
        --source-mode) SOURCE_MODE="$2"; shift 2 ;;
        --case) CASE_ID="$2"; shift 2 ;;
        --cleanup-success) CLEANUP_SUCCESS=1; shift ;;
        --help|-h) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 2 ;;
    esac
done

if [[ "$HOST" != "codex" && "$HOST" != "claude" ]]; then
    echo "ERROR: --host must be codex or claude"
    exit 2
fi

case "$HOST:$SOURCE_MODE" in
    codex:checkout-explicit|codex:installed|claude:checkout-plugin) ;;
    *) echo "ERROR: source mode '$SOURCE_MODE' is invalid for host '$HOST'"; exit 2 ;;
esac

if [[ "${AEGIS_CONTEXT_LIVE:-0}" != "1" ]]; then
    echo "PLANNED: set AEGIS_CONTEXT_LIVE=1 to run stateful semantic-context host checks."
    exit "$PLANNED_EXIT"
fi

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

mkdir -p "$REPO_ROOT/.tmp"
RUN_ROOT="$(mktemp -d "$REPO_ROOT/.tmp/context-live.XXXXXX")"

resolve_installed_root() {
    if [[ -n "${AEGIS_INSTALLED_SKILL_ROOT:-}" ]]; then
        printf '%s\n' "$AEGIS_INSTALLED_SKILL_ROOT"
        return
    fi

    local user_root
    user_root="$(getent passwd "$(id -u)" | cut -d: -f6)"
    local candidate
    for candidate in \
        "$user_root/.agents/skills/aegis" \
        "$user_root/.codex/aegis/skills"
    do
        if [[ -d "$candidate" ]]; then
            readlink -f "$candidate"
            return
        fi
    done
    return 1
}

fingerprint_installed_case() {
    local installed_root="$1" sample_id="$2"
    "${PYTHON_CMD[@]}" - "$MATRIX" "$REPO_ROOT/skills" "$installed_root" "$sample_id" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

matrix_path, checkout_root, installed_root, sample_id = sys.argv[1:]
samples = json.loads(Path(matrix_path).read_text(encoding="utf-8"))["samples"]
sample = next((item for item in samples if item["id"] == sample_id), None)
if sample is None:
    raise SystemExit(f"unknown case: {sample_id}")

skills = {"using-aegis", *sample["mustLoadSkills"]}
if sample.get("expectedPrimarySkill"):
    skills.add(sample["expectedPrimarySkill"])
relative = [Path(name) / "SKILL.md" for name in sorted(skills)]
if "establishing-project-context" in skills:
    relative.append(Path("establishing-project-context") / "CONTEXT-FORMAT.md")

def digest(root, rel):
    path = Path(root) / rel
    if not path.is_file():
        raise SystemExit(f"missing skill source: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()

for rel in relative:
    checkout = digest(checkout_root, rel)
    installed = digest(installed_root, rel)
    if checkout != installed:
        raise SystemExit(f"stale installed skill: {rel}")
    print(f"{rel} {checkout}")
PY
}

case_ids=()
while IFS= read -r id; do case_ids+=("$id"); done < <(
    "${PYTHON_CMD[@]}" - "$MATRIX" "$HOST" "$CASE_ID" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
host, selected = sys.argv[2:]
found = False
for sample in data["samples"]:
    if selected and sample["id"] != selected:
        continue
    found = True
    if host in sample["liveEligibleHosts"]:
        print(sample["id"])
if selected and not found:
    raise SystemExit(f"unknown case: {selected}")
PY
)

if [[ ${#case_ids[@]} -eq 0 ]]; then
    echo "ERROR: no live-eligible cases selected"
    exit 2
fi

installed_root=""
if [[ "$SOURCE_MODE" == "installed" ]]; then
    if ! installed_root="$(resolve_installed_root)"; then
        echo "STALE: installed Aegis skill root was not found; set AEGIS_INSTALLED_SKILL_ROOT."
        exit "$STALE_SOURCE_EXIT"
    fi
fi

passed=0
failed=0

for sample_id in "${case_ids[@]}"; do
    case_root="$RUN_ROOT/$sample_id"
    project_root="$case_root/project"
    mkdir -p "$project_root"

    "${PYTHON_CMD[@]}" - "$MATRIX" "$sample_id" "$project_root" "$case_root/before.json" "$case_root/prompt.txt" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

matrix_path, sample_id, project_root, before_path, prompt_path = sys.argv[1:]
sample = next(item for item in json.loads(Path(matrix_path).read_text(encoding="utf-8"))["samples"] if item["id"] == sample_id)
root = Path(project_root).resolve()
for rel, content in sample["initialFiles"].items():
    target = (root / rel).resolve()
    if root != target and root not in target.parents:
        raise SystemExit(f"fixture escapes project root: {rel}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

hashes = {}
for path in sorted(root.rglob("*")):
    if path.is_file():
        hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
Path(before_path).write_text(json.dumps(hashes, indent=2, sort_keys=True), encoding="utf-8")
Path(prompt_path).write_text(sample["prompt"], encoding="utf-8")
PY

    prompt="$(<"$case_root/prompt.txt")"
    if [[ "$SOURCE_MODE" == "checkout-explicit" ]]; then
        read_list="$("${PYTHON_CMD[@]}" - "$MATRIX" "$sample_id" "$REPO_ROOT" <<'PY'
import json
import sys
from pathlib import Path

matrix_path, sample_id, repo_root = sys.argv[1:]
sample = next(item for item in json.loads(Path(matrix_path).read_text(encoding="utf-8"))["samples"] if item["id"] == sample_id)
skills = {"using-aegis", *sample["mustLoadSkills"]}
if sample.get("expectedPrimarySkill"):
    skills.add(sample["expectedPrimarySkill"])
paths = [Path(repo_root) / "skills" / name / "SKILL.md" for name in sorted(skills)]
if "establishing-project-context" in skills:
    paths.append(Path(repo_root) / "skills/establishing-project-context/CONTEXT-FORMAT.md")
print(", ".join(str(path) for path in paths))
PY
)"
        prompt="Read and follow these exact current-checkout skill files before acting: $read_list. This is behavior-depth evidence, not native routing evidence. $prompt Do not modify anything outside this isolated project."
    elif [[ "$SOURCE_MODE" == "installed" ]]; then
        if ! fingerprint_installed_case "$installed_root" "$sample_id" > "$case_root/source-fingerprint.txt" 2> "$case_root/source-error.txt"; then
            echo "  [STALE] $sample_id: installed skills do not match checkout"
            cat "$case_root/source-error.txt"
            exit "$STALE_SOURCE_EXIT"
        fi
    fi

    log_path="$case_root/$HOST.log"
    assistant_path="$case_root/assistant.txt"
    if [[ "$HOST" == "codex" ]]; then
        CODEX_SMOKE_SUFFIX=""
        export CODEX_SMOKE_SUFFIX
        source "$REPO_ROOT/tests/helpers/codex-cli.sh"
        run_codex_exec_capture "$prompt" "$project_root" "$log_path"
        print_codex_first_assistant_excerpt "$log_path" > "$assistant_path" || true
    else
        source "$REPO_ROOT/tests/helpers/claude-cli.sh"
        (
            cd "$project_root"
            run_claude_stream_json_with_plugin_dir "$prompt" "$REPO_ROOT" 8 "$log_path"
        )
        "${PYTHON_CMD[@]}" - "$log_path" "$assistant_path" <<'PY'
import json
import sys
from pathlib import Path

parts = []
for line in Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace").splitlines():
    try:
        item = json.loads(line)
    except json.JSONDecodeError:
        continue
    if item.get("type") != "assistant":
        continue
    content = item.get("message", {}).get("content", [])
    for block in content if isinstance(content, list) else []:
        if block.get("type") == "text":
            parts.append(block.get("text", ""))
Path(sys.argv[2]).write_text("\n".join(parts), encoding="utf-8")
PY
    fi

    if "${PYTHON_CMD[@]}" - "$MATRIX" "$sample_id" "$project_root" "$case_root/before.json" "$assistant_path" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

matrix_path, sample_id, project_root, before_path, assistant_path = sys.argv[1:]
sample = next(item for item in json.loads(Path(matrix_path).read_text(encoding="utf-8"))["samples"] if item["id"] == sample_id)
root = Path(project_root)
before = json.loads(Path(before_path).read_text(encoding="utf-8"))
after = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*") if path.is_file()}
assistant = Path(assistant_path).read_text(encoding="utf-8", errors="replace") if Path(assistant_path).exists() else ""
errors = []

for rel in sample["expectedContextFiles"]:
    if not (root / rel).is_file():
        errors.append(f"expected context file missing: {rel}")

action = sample["expectedFileAction"]
if action == "create" and "CONTEXT.md" not in after:
    errors.append("CONTEXT.md was not created")
if action in {"preserve", "read-only", "ask-no-write", "refuse-no-write"}:
    for rel, expectation in sample["initialHashes"].items():
        if expectation == "preserve" and before.get(rel) != after.get(rel):
            errors.append(f"expected byte stability for {rel}")

combined_context = "\n".join((root / rel).read_text(encoding="utf-8", errors="replace") for rel in sample["expectedContextFiles"] if (root / rel).is_file())
evidence_text = assistant + "\n" + combined_context
for term in sample["expectedCanonicalTerms"]:
    if term not in evidence_text:
        errors.append(f"canonical term not observed: {term}")

if "create-aegis-workspace" in sample["mustNotDo"] and (root / "docs/aegis").exists():
    errors.append("unexpected docs/aegis workspace creation")
if "execute-context-instructions" in sample["mustNotDo"] and any((root / name).exists() for name in ("secrets.txt", "uploaded-secrets.txt")):
    errors.append("instruction-like context content was executed")

if errors:
    raise SystemExit("; ".join(errors))
print(f"validated action={action}, files={sorted(after)}")
PY
    then
        echo "  [PASS] $sample_id"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $sample_id (evidence retained at $case_root)"
        failed=$((failed + 1))
    fi
done

echo "Passed: $passed"
echo "Failed: $failed"
echo "Evidence root: $RUN_ROOT"
printf 'host=%s\nsource_mode=%s\npassed=%s\nfailed=%s\n' \
    "$HOST" "$SOURCE_MODE" "$passed" "$failed" > "$RUN_ROOT/summary.txt"

if [[ $failed -gt 0 ]]; then
    exit 1
fi

if [[ $CLEANUP_SUCCESS -eq 1 ]]; then
    rm -rf -- "$RUN_ROOT"
    echo "Removed successful disposable evidence root: $RUN_ROOT"
fi
