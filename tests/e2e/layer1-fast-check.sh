#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

HOST_PROFILE="${AEGIS_E2E_HOST_PROFILE:-fast}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-host-smoke)
            HOST_PROFILE="none"
            shift
            ;;
        --host-profile)
            HOST_PROFILE="$2"
            shift 2
            ;;
        --fast)
            HOST_PROFILE="fast"
            shift
            ;;
        --full-matrix)
            HOST_PROFILE="matrix"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--skip-host-smoke|--host-profile fast|matrix|none]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ "${AEGIS_E2E_SKIP_HOST_SMOKE:-0}" == "1" ]]; then
    HOST_PROFILE="none"
fi

echo "========================================"
echo " Layer 1 Fast Check"
echo "========================================"
echo ""
echo "Host profile: $HOST_PROFILE"
echo ""

passed=0
failed=0

if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
elif command -v py >/dev/null 2>&1 && py -3 -V >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
else
    PYTHON_CMD=(python)
fi

run_check() {
    local label="$1"
    shift

    echo "Running: $label"
    if output="$("$@" 2>&1)"; then
        echo "  [PASS] $label"
        passed=$((passed + 1))
    else
        echo "  [FAIL] $label"
        echo "$output" | sed 's/^/    /'
        failed=$((failed + 1))
    fi
    echo ""
}

run_host_smoke_fast_profile() {
    run_check "codex representative skill-triggering smoke" \
        env AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-test.sh \
        brainstorming \
        tests/skill-triggering/prompts/brainstorming.txt

    run_check "codex representative explicit-skill smoke" \
        env AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-test.sh \
        brainstorming \
        tests/explicit-skill-requests/prompts/please-use-brainstorming.txt

    run_check "opencode base suite" bash tests/opencode/run-tests.sh
    run_check "codex plugin sync regression" bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
}

run_host_smoke_full_matrix() {
    run_check "codex skill-triggering matrix" \
        bash -lc "env AEGIS_TEST_CLI=codex bash tests/skill-triggering/run-all.sh"

    run_check "codex explicit-skill matrix" \
        bash -lc "env AEGIS_TEST_CLI=codex bash tests/explicit-skill-requests/run-all.sh"

    run_check "opencode base suite" bash tests/opencode/run-tests.sh
    run_check "codex plugin sync regression" bash tests/codex-plugin-sync/test-sync-to-codex-plugin.sh
}

run_check "boundary compliance" bash "$SCRIPT_DIR/boundary-compliance-check.sh"
run_check "artifact schema fixtures" bash "$SCRIPT_DIR/artifact-schema-check.sh"
run_check "aegis project workspace helper" bash "$SCRIPT_DIR/aegis-workspace-check.sh"
run_check "aegis doctor" bash "$SCRIPT_DIR/aegis-doctor-check.sh"
run_check "install verification policy" bash "$SCRIPT_DIR/install-verification-policy-check.sh"
run_check "claude hook permissions" bash "$SCRIPT_DIR/claude-hook-permissions-check.sh"
run_check "workspace text write compatibility" "${PYTHON_CMD[@]}" tests/helpers/test_workspace_text_write_compat.py
run_check "workspace helper skill wiring" bash "$SCRIPT_DIR/workspace-helper-wiring-check.sh"
run_check "workspace helper resolution" bash "$SCRIPT_DIR/workspace-helper-resolution-check.sh"
run_check "project bootstrap policy" bash "$SCRIPT_DIR/project-bootstrap-policy-check.sh"
run_check "trigger health policy" bash "$SCRIPT_DIR/trigger-health-check.sh"
run_check "Antigravity host boundary" bash "$SCRIPT_DIR/antigravity-host-boundary-check.sh"
run_check "CC GUI host boundary" bash "$SCRIPT_DIR/cc-gui-host-boundary-check.sh"
run_check "Pi host boundary" bash "$SCRIPT_DIR/pi-host-boundary-check.sh"
run_check "popular agent host boundary" bash "$SCRIPT_DIR/popular-agent-host-boundary-check.sh"
run_check "workflow quality policy" bash "$SCRIPT_DIR/workflow-quality-check.sh"
run_check "goal framing policy" bash "$SCRIPT_DIR/goal-framing-check.sh"
run_check "first-principles review policy" bash "$SCRIPT_DIR/first-principles-review-check.sh"
run_check "debugging patch-shape gate policy" bash "$SCRIPT_DIR/debugging-patch-shape-gate-check.sh"
run_check "long-task continuation scenario fixtures" bash "$SCRIPT_DIR/long-task-continuation-check.sh"
run_check "context budget guardrails" bash "$SCRIPT_DIR/context-budget-check.sh"
run_check "activation mode guardrails" bash "$SCRIPT_DIR/activation-mode-check.sh"
run_check "TDD policy guardrails" bash "$SCRIPT_DIR/tdd-policy-check.sh"

case "$HOST_PROFILE" in
    none)
        echo "Skipping host smoke suites for this run."
        echo ""
        ;;
    fast)
        run_host_smoke_fast_profile
        ;;
    matrix)
        run_host_smoke_full_matrix
        ;;
    *)
        echo "Unknown host profile: $HOST_PROFILE"
        exit 1
        ;;
esac

if [[ "$HOST_PROFILE" == "matrix" ]]; then
    echo "Note: matrix profile reuses the full Codex compatibility matrices and can take significantly longer."
    echo ""
fi

echo "Passed: $passed"
echo "Failed: $failed"

if [[ $failed -gt 0 ]]; then
    exit 1
fi

exit 0
