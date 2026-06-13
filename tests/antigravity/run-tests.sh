#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " Antigravity CLI Test Suite"
echo "========================================"
echo ""
echo "Repository: $(cd ../.. && pwd)"
echo "Test time: $(date)"
echo ""

RUN_INTEGRATION=false
VERBOSE=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --integration|-i)
            RUN_INTEGRATION=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --test|-t)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --integration, -i  Run integration tests (requires Antigravity CLI)"
            echo "  --verbose, -v      Show verbose output"
            echo "  --test, -t NAME    Run only the specified test"
            echo "  --help, -h         Show this help"
            echo ""
            echo "Tests:"
            echo "  test-doc-surface.sh  Verify Aegis-side Antigravity docs and registry contract"
            echo "  test-cli-surface.sh  Probe local Antigravity CLI host surface (integration)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

tests=(
    "test-doc-surface.sh"
)

ANTIGRAVITY_INTEGRATION_SKIP_EXIT=80

integration_tests=(
    "test-cli-surface.sh"
)

if [ "$RUN_INTEGRATION" = true ]; then
    tests+=("${integration_tests[@]}")
fi

if [ -n "$SPECIFIC_TEST" ]; then
    tests=("$SPECIFIC_TEST")
fi

passed=0
failed=0
skipped=0

for test in "${tests[@]}"; do
    echo "----------------------------------------"
    echo "Running: $test"
    echo "----------------------------------------"

    test_path="$SCRIPT_DIR/$test"

    if [ ! -f "$test_path" ]; then
        echo "  [SKIP] Test file not found: $test"
        skipped=$((skipped + 1))
        continue
    fi

    if [ ! -x "$test_path" ]; then
        chmod +x "$test_path"
    fi

    start_time=$(date +%s)

    if [ "$VERBOSE" = true ]; then
        if bash "$test_path"; then
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            echo ""
            echo "  [PASS] $test (${duration}s)"
            passed=$((passed + 1))
        else
            exit_code=$?
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            echo ""
            if [ $exit_code -eq $ANTIGRAVITY_INTEGRATION_SKIP_EXIT ]; then
                echo "  [SKIP] $test (${duration}s)"
                skipped=$((skipped + 1))
            else
                echo "  [FAIL] $test (${duration}s)"
                failed=$((failed + 1))
            fi
        fi
    else
        if output=$(bash "$test_path" 2>&1); then
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            echo "  [PASS] (${duration}s)"
            passed=$((passed + 1))
        else
            exit_code=$?
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            if [ $exit_code -eq $ANTIGRAVITY_INTEGRATION_SKIP_EXIT ]; then
                echo "  [SKIP] (${duration}s)"
                skipped=$((skipped + 1))
            else
                echo "  [FAIL] (${duration}s)"
                failed=$((failed + 1))
            fi
            echo ""
            echo "  Output:"
            echo "$output" | sed 's/^/    /'
        fi
    fi

    echo ""
done

echo "========================================"
echo " Test Results Summary"
echo "========================================"
echo ""
echo "  Passed:  $passed"
echo "  Failed:  $failed"
echo "  Skipped: $skipped"
echo ""

if [ "$RUN_INTEGRATION" = false ] && [ ${#integration_tests[@]} -gt 0 ]; then
    echo "Note: Integration tests were not run."
    echo "Use --integration to probe the local Antigravity CLI surface."
    echo ""
fi

if [ $skipped -gt 0 ]; then
    echo "Note: One or more Antigravity integration tests were skipped because the local CLI"
    echo "is unavailable or blocked by local runtime/auth conditions."
    echo ""
fi

if [ $failed -gt 0 ]; then
    echo "STATUS: FAILED"
    exit 1
else
    echo "STATUS: PASSED"
    exit 0
fi
