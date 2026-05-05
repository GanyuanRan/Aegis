#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PLANNED_EXIT=90
MODE="bootstrap"
HOST_PROFILE="${AEGIS_E2E_HOST_PROFILE:-fast}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --bootstrap)
            MODE="bootstrap"
            shift
            ;;
        --full)
            MODE="full"
            shift
            ;;
        --host-profile)
            HOST_PROFILE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--bootstrap|--full] [--host-profile fast|matrix|none]"
            echo ""
            echo "  --bootstrap  Run the currently active bootstrap slice (default)"
            echo "  --full       Attempt every layer entrypoint; planned skeletons return as planned"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "========================================"
echo " Aegis E2E Verification"
echo "========================================"
echo ""
echo "Mode: $MODE"
echo "Host profile: $HOST_PROFILE"
echo "Directory: $SCRIPT_DIR"
echo ""

passed=0
planned=0
failed=0

run_step() {
    local label="$1"
    shift
    local output
    local exit_code

    echo "----------------------------------------"
    echo "Running: $label"
    echo "----------------------------------------"

    set +e
    output="$("$@" 2>&1)"
    exit_code=$?
    set -e

    if [[ $exit_code -eq 0 ]]; then
        echo "$output"
        echo ""
        echo "  [PASS] $label"
        passed=$((passed + 1))
        echo ""
        return 0
    fi

    echo "$output"
    echo ""
    if [[ $exit_code -eq $PLANNED_EXIT ]]; then
        echo "  [PLAN] $label"
        planned=$((planned + 1))
    else
        echo "  [FAIL] $label"
        failed=$((failed + 1))
    fi
    echo ""
    return 0
}

if [[ "$MODE" == "bootstrap" ]]; then
    run_step "Layer 1 Fast Check" bash "$SCRIPT_DIR/layer1-fast-check.sh" --host-profile none
    run_step "Governance Completion Contract Check" bash "$SCRIPT_DIR/governance-completion-contract-check.sh"
    run_step "Layer 2 Behavior Check Skeleton" bash "$SCRIPT_DIR/layer2-behavior-check.sh" --bootstrap-status
    run_step "Layer 3 Scenario Check Skeleton" bash "$SCRIPT_DIR/layer3-scenario-check.sh" --bootstrap-status
else
    run_step "Layer 1 Fast Check" bash "$SCRIPT_DIR/layer1-fast-check.sh" --host-profile "$HOST_PROFILE"
    run_step "Governance Completion Contract Check" bash "$SCRIPT_DIR/governance-completion-contract-check.sh"
    run_step "Layer 2 Behavior Check" bash "$SCRIPT_DIR/layer2-behavior-check.sh"
    run_step "Layer 3 Scenario Check" bash "$SCRIPT_DIR/layer3-scenario-check.sh"
fi

echo "========================================"
echo " E2E Verification Summary"
echo "========================================"
echo ""
echo "  Passed:  $passed"
echo "  Planned: $planned"
echo "  Failed:  $failed"
echo ""

if [[ $failed -gt 0 ]]; then
    echo "STATUS: FAILED"
    exit 1
fi

echo "STATUS: PASSED"
exit 0
