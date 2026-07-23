#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

failures=0

pass() {
    echo "  [PASS] $1"
}

fail() {
    echo "  [FAIL] $1"
    failures=$((failures + 1))
}

assert_contains() {
    local file="$1"
    local pattern="$2"
    local label="$3"

    if grep -qE -- "$pattern" "$file"; then
        pass "$label"
    else
        fail "$label"
    fi
}

echo "=== Install Verification Policy Check ==="

root_docs=(
    "README.md"
)

host_docs=(
    "docs/README.codex.md"
    "docs/README.opencode.md"
    "docs/README.claude-code.md"
    "docs/README.cc-gui.md"
    "docs/README.codebuddy.md"
    "docs/README.deepseek-tui.md"
    "docs/README.trae.md"
    "docs/README.copilot.md"
    "docs/README.qoder.md"
    "docs/README.kimi-code.md"
    "docs/README.antigravity.md"
    "docs/README.pi.md"
    "docs/README.openclaw.md"
    "docs/README.hermes-agent.md"
    "docs/README.zcode.md"
    "docs/README.grok-build.md"
)

for file in "${root_docs[@]}"; do
    assert_contains "$file" "aegis-doctor\\.py --write-config --json" \
        "$file requires doctor write-config JSON verification"
    assert_contains "$file" "aegis:update" \
        "$file documents explicit host-scoped Aegis update trigger"
    assert_contains "$file" "cd <aegis-method-pack-root>" \
        "$file anchors doctor verification to the method-pack root"
    assert_contains "$file" "target project directory|目标项目目录" \
        "$file warns not to run doctor from the target project directory"
    assert_contains "$file" '"workspaceSupport": "available"' \
        "$file names workspaceSupport install success field"
    assert_contains "$file" '"configStatus": "configured"' \
        "$file names configStatus install success field"
done

assert_contains "docs/README.codex.md" "aegis-update\\.py register" \
    "Codex guide registers host-scoped update metadata"
assert_contains "docs/README.codex.md" "aegis-update\\.py update --host codex --json" \
    "Codex guide uses explicit host-scoped update command"

for file in "${host_docs[@]}"; do
    assert_contains "$file" "aegis-doctor\\.py --write-config --json" \
        "$file uses hardened complete-install doctor command"
    assert_contains "$file" "cd <aegis-method-pack-root>" \
        "$file anchors complete-install doctor command to the method-pack root"
    assert_contains "$file" "target project directory" \
        "$file warns not to run doctor from the target project directory"
done

assert_contains "docs/current/AEGIS_KNOWN_LIMITATIONS.md" "aegis-doctor\\.py --write-config --json" \
    "known limitations tracks hardened install verification command"
assert_contains "docs/current/AEGIS_KNOWN_LIMITATIONS.md" "aegis-update\\.py update --host <host> --json" \
    "known limitations tracks host-scoped update command"
assert_contains "docs/current/AEGIS_KNOWN_LIMITATIONS.md" "cd <aegis-method-pack-root>" \
    "known limitations anchors hardened install verification command"
assert_contains "docs/current/AEGIS_KNOWN_LIMITATIONS.md" '"configStatus": "configured"' \
    "known limitations tracks configured status readback"
assert_contains "docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md" "aegis-doctor\\.py --write-config --json" \
    "compatibility snapshot requires hardened install verification"
assert_contains "docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md" "aegis-update\\.py update --host <host> --json" \
    "compatibility snapshot tracks host-scoped update registration"
assert_contains "docs/current/AEGIS_HOST_COMPATIBILITY_MATRIX_SNAPSHOT.md" "cd <aegis-method-pack-root>" \
    "compatibility snapshot anchors complete-install verification command"
assert_contains "docs/current/AEGIS_KNOWN_LIMITATIONS.md" "discovery shape|discovery-root structural readback" \
    "known limitations records updater discovery-shape structural verification"
assert_contains "docs/current/AEGIS_FAST_TRACK_PLAYBOOK.md" "native activation and automatic-entry checks" \
    "English universal prompt requires native activation verification"
assert_contains "docs/current/AEGIS_FAST_TRACK_PLAYBOOK_ZH.md" "原生活化与自动入口验证" \
    "Chinese universal prompt requires native activation verification"

if (( failures > 0 )); then
    echo ""
    echo "Install verification policy check failed with $failures issue(s)."
    exit 1
fi

echo ""
echo "Install verification policy check passed."
