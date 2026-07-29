#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Agentic Benchmark Isolation Check ==="

test_root=".tmp/agentic-benchmark-isolation-check"
auth_file="$test_root/auth.json"
report_file="$test_root/audit/report.json"
rm -rf "$test_root"
mkdir -p "$test_root"
umask 077
printf '%s\n' '{"auth_mode":"test-only-placeholder"}' > "$auth_file"

python3 tests/helpers/run_agentic_benchmark.py isolation-audit \
    --case change-necessity-before-edit \
    --output-root "$test_root/audit" \
    --report-json "$report_file" \
    --auth-file "$auth_file"

python3 - "$report_file" <<'PY'
import json
import os
import sys
from pathlib import Path

report_path = Path(sys.argv[1])
report = json.loads(report_path.read_text(encoding="utf-8"))
baseline = report["arms"]["baseline-no-aegis"]
aegis = report["arms"]["aegis-auto"]

assert report["modelCalls"] == 0
assert report["authorityBoundary"] == "advisory-method-pack-evidence-not-completion-authority"
assert report["auditNetworkPolicy"]["promptInput"]["mode"] in {"direct", "proxy"}
assert report["auditNetworkPolicy"]["mountAudit"] == {"mode": "network-disabled"}
assert baseline["evaluatedSkillMatchCount"] == 0
assert aegis["evaluatedSkillMatchCount"] == report["distributionSnapshot"]["skillCount"]
assert baseline["methodPackMarkerCount"] == 0
assert aegis["methodPackMarkerCount"] > 0
assert baseline["nonSkillInputHash"] == aegis["nonSkillInputHash"]
assert baseline["authReadOnly"] is True and aegis["authReadOnly"] is True
assert baseline["benchmarkRepoVisible"] is False and aegis["benchmarkRepoVisible"] is False
assert baseline["peerWorkspaceVisible"] is False and aegis["peerWorkspaceVisible"] is False
assert baseline["scorerVisible"] is False and aegis["scorerVisible"] is False
assert baseline["visibleProcessCount"] <= 3 and aegis["visibleProcessCount"] <= 3
assert baseline["snapshotVisible"] is False and aegis["snapshotVisible"] is True
assert report["distributionSnapshot"]["version"]
assert len(report["distributionSnapshot"]["treeHash"]) == 64

serialized = report_path.read_text(encoding="utf-8")
for forbidden in ("/home/", "/workspace", "auth.json", "The settings page sometimes shows"):
    assert forbidden not in serialized, forbidden
for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
    if os.environ.get(key):
        assert os.environ[key] not in serialized
print("  [PASS] live no-model prompt and mount audit")
PY

python3 - "$REPO_ROOT" "$auth_file" <<'PY'
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "tests/helpers"))
from agentic_benchmark_isolation import (
    build_bwrap_command,
    hash_tree,
    prepare_arm_layout,
    resolve_proxy_policy,
    run_isolation_audit,
    validate_arm_pair,
    validate_bwrap_command,
)

root = Path(sys.argv[1]).resolve()
auth = Path(sys.argv[2]).resolve()
scratch = root / ".tmp/agentic-benchmark-isolation-check/refusals"
if scratch.exists():
    shutil.rmtree(scratch)
scratch.mkdir(parents=True)
seed = root / "tests/e2e/fixtures/replay-projects/change-necessity-before-edit"
layout = prepare_arm_layout(scratch / "arm", seed, auth, None)
bwrap = Path(shutil.which("bwrap") or "/missing/bwrap")
codex = Path(shutil.which("codex") or "/missing/codex").resolve()
proxy_policy = resolve_proxy_policy(__import__("os").environ)
command = build_bwrap_command(
    bwrap=bwrap,
    codex=codex,
    layout=layout,
    prompt="refusal-test",
    debug_prompt=True,
    isolate_network=False,
    proxy_policy=proxy_policy,
)

def refused(label, callback):
    try:
        callback()
    except SystemExit:
        print(f"  [PASS] refuses {label}")
        return
    raise AssertionError(f"did not refuse {label}")

missing_auth = scratch / "missing-auth.json"
case = {"id": "refusal-case", "seedProjectPath": str(seed.relative_to(root)), "promptPath": "tests/e2e/replay-samples/change-necessity-before-edit/prompt.txt"}
refused(
    "missing bwrap",
    lambda: run_isolation_audit(
        root=root,
        case=case,
        output_root=scratch / "missing-bwrap-output",
        auth_file=auth,
        bwrap=scratch / "missing-bwrap",
        codex=codex,
        proxy_policy=proxy_policy,
    ),
)
refused(
    "missing auth",
    lambda: run_isolation_audit(
        root=root,
        case=case,
        output_root=scratch / "missing-auth-output",
        auth_file=missing_auth,
        bwrap=bwrap,
        codex=codex,
        proxy_policy=proxy_policy,
    ),
)

writable_auth = command.copy()
writable_auth[writable_auth.index("--ro-bind")] = "--bind"
refused(
    "writable auth mount",
    lambda: validate_bwrap_command(
        writable_auth, root=root, output_root=scratch, layout=layout,
        client_network=True, proxy_policy=proxy_policy,
    ),
)

repo_visible = command.copy()
separator = repo_visible.index("--")
repo_visible[separator:separator] = ["--ro-bind", str(root), "/benchmark-repo"]
refused(
    "benchmark repository visibility",
    lambda: validate_bwrap_command(
        repo_visible, root=root, output_root=scratch, layout=layout,
        client_network=True, proxy_policy=proxy_policy,
    ),
)

unhashable = scratch / "unhashable-snapshot"
unhashable.mkdir()
(unhashable / "payload.txt").write_text("payload\n", encoding="utf-8")
(unhashable / "escape").symlink_to(root / "skills")
refused("unhashable snapshot", lambda: hash_tree(unhashable))

peer_layout = prepare_arm_layout(scratch / "peer", seed, auth, None)
(peer_layout["home"] / ".codex/config.toml").write_text("project_doc_max_bytes = 1\n", encoding="utf-8")
refused(
    "arm config drift",
    lambda: validate_arm_pair({"baseline-no-aegis": layout, "aegis-auto": peer_layout}, "same-prompt"),
)
PY

echo ""
echo "Agentic benchmark isolation check passed."
