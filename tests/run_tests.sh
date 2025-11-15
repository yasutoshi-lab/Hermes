#!/bin/bash
# Test runner script for Hermes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Hermes Test Suite Runner${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-no}"

# Function to run dependency checks
run_dependency_checks() {
    echo -e "${YELLOW}[1/4] Checking dependencies...${NC}"
    python tests/test_dependencies.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ All dependencies are healthy${NC}"
    else
        echo -e "${RED}✗ Some dependencies failed${NC}"
        exit 1
    fi
    echo ""
}

# Function to run unit tests
run_unit_tests() {
    echo -e "${YELLOW}[2/4] Running unit tests...${NC}"
    if [ "$COVERAGE" == "cov" ]; then
        pytest tests/unit -v -m unit --cov=hermes_cli --cov-report=html --cov-report=term
    else
        pytest tests/unit -v -m unit
    fi
    echo ""
}

# Function to run integration tests
run_integration_tests() {
    echo -e "${YELLOW}[3/4] Running integration tests...${NC}"
    pytest tests/integration -v -m "integration and not slow"
    echo ""
}

# Function to run slow integration tests
run_slow_tests() {
    echo -e "${YELLOW}[4/4] Running slow integration tests...${NC}"
    pytest tests/integration -v -m "integration and slow"
    echo ""
}

# Main execution
case "$TEST_TYPE" in
    all)
        run_dependency_checks
        run_unit_tests
        run_integration_tests
        echo -e "${GREEN}✓ All fast tests passed${NC}"
        echo -e "${YELLOW}Note: Slow tests were skipped. Run with 'all-slow' to include them.${NC}"
        ;;
    all-slow)
        run_dependency_checks
        run_unit_tests
        run_integration_tests
        run_slow_tests
        echo -e "${GREEN}✓ All tests passed${NC}"
        ;;
    unit)
        run_unit_tests
        echo -e "${GREEN}✓ Unit tests passed${NC}"
        ;;
    integration)
        run_dependency_checks
        run_integration_tests
        echo -e "${GREEN}✓ Integration tests passed${NC}"
        ;;
    deps|dependencies)
        run_dependency_checks
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: $0 [all|all-slow|unit|integration|deps] [cov]"
        echo ""
        echo "Test types:"
        echo "  all           - Run dependency checks, unit, and fast integration tests (default)"
        echo "  all-slow      - Run all tests including slow integration tests"
        echo "  unit          - Run only unit tests"
        echo "  integration   - Run dependency checks and integration tests"
        echo "  deps          - Run only dependency checks"
        echo ""
        echo "Coverage:"
        echo "  cov           - Generate coverage report (only for unit tests)"
        echo ""
        echo "Examples:"
        echo "  $0 all"
        echo "  $0 unit cov"
        echo "  $0 integration"
        exit 1
        ;;
esac

if [ "$COVERAGE" == "cov" ]; then
    echo -e "${BLUE}Coverage report generated: htmlcov/index.html${NC}"
fi

echo ""
echo -e "${GREEN}✓ Test suite completed successfully${NC}"
