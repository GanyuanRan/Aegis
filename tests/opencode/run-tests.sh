#!/usr/bin/env bash
# Main test runner for OpenCode plugin test suite
# Runs all tests and reports results
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " OpenCode Plugin Test Suite"
echo "========================================"
echo ""
echo "Repository: $(cd ../.. && pwd)"
echo "Test time: $(date)"
echo ""

# Parse command line arguments
RUN_INTEGRATION=false
VERBOSE=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
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
            echo "  --integration, -i  Run integration tests (requires OpenCode)"
            echo "  --verbose, -v      Show verbose output"
            echo "  --test, -t NAME    Run only the specified test"
            echo "  --help, -h         Show this help"
            echo ""
            echo "Tests:"
            echo "  test-plugin-loading.sh  Verify plugin installation and structure"
            echo "  test-tools.sh           Test native skill discovery/loading behavior (integration)"
            echo "  test-priority.sh        Test skill priority resolution (integration)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# List of tests to run (no external dependencies)
tests=(
    "test-plugin-loading.sh"
)

# Exit code used by integration tests when the local OpenCode CLI is unavailable
# or unusable for the current platform.
OPENCODE_INTEGRATION_SKIP_EXIT=80

# Integration tests (require OpenCode)
integration_tests=(
    "test-tools.sh"
    "test-priority.sh"
)

# Add integration tests if requested
if [ "$RUN_INTEGRATION" = true ]; then
    tests+=("${integration_tests[@]}")
fi

# Filter to specific test if requested
if [ -n "$SPECIFIC_TEST" ]; then
    tests=("$SPECIFIC_TEST")
fi

# Track results
passed=0
failed=0
skipped=0

# Run each test
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
        echo "  Making $test executable..."
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
            if [ $exit_code -eq $OPENCODE_INTEGRATION_SKIP_EXIT ]; then
                echo "  [SKIP] $test (${duration}s)"
                skipped=$((skipped + 1))
            else
                echo "  [FAIL] $test (${duration}s)"
                failed=$((failed + 1))
            fi
        fi
    else
        # Capture output for non-verbose mode
        if output=$(bash "$test_path" 2>&1); then
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            echo "  [PASS] (${duration}s)"
            passed=$((passed + 1))
        else
            exit_code=$?
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            if [ $exit_code -eq $OPENCODE_INTEGRATION_SKIP_EXIT ]; then
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

# Print summary
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
    echo "Use --integration flag to run tests that require OpenCode."
    echo ""
fi

if [ $skipped -gt 0 ]; then
    echo "Note: One or more integration tests were skipped because the local OpenCode CLI"
    echo "is unavailable or not runnable for this platform."
    echo ""
fi

if [ $failed -gt 0 ]; then
    echo "STATUS: FAILED"
    exit 1
else
    echo "STATUS: PASSED"
    exit 0
fi
