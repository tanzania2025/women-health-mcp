#!/bin/bash
# Run all MCP tests and report results

echo "=================================="
echo "Women's Health MCP Test Suite"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest not found. Installing...${NC}"
    pip install pytest pytest-asyncio
fi

# Navigate to project root
cd "$(dirname "$0")/.."

echo -e "${YELLOW}🔍 Starting test execution...${NC}"
echo ""

# Run individual server tests
echo "Testing individual servers..."
echo "=============================="

echo -e "${YELLOW}Testing Database Server...${NC}"
pytest tests/test_database_server.py -v --tb=short
DB_RESULT=$?

echo -e "${YELLOW}Testing API Server...${NC}"
pytest tests/test_api_server.py -v --tb=short  
API_RESULT=$?

echo -e "${YELLOW}Testing Calculator Server...${NC}"
pytest tests/test_calculator_server.py -v --tb=short
CALC_RESULT=$?

# Run multi-server client tests
echo ""
echo "Testing multi-server client..."
echo "=============================="
pytest tests/test_multi_server_client.py -v --tb=short
CLIENT_RESULT=$?

# Run integration tests
echo ""
echo "Testing integration..."
echo "====================="
pytest tests/test_integration.py -v --tb=short
INTEGRATION_RESULT=$?

# Run tool preservation tests
echo ""
echo "Testing tool preservation..."
echo "============================"
pytest tests/test_tool_preservation.py -v --tb=short
PRESERVATION_RESULT=$?

# Summary
echo ""
echo "=================================="
echo "TEST RESULTS SUMMARY"
echo "=================================="

declare -A results=(
    ["Database Server"]=$DB_RESULT
    ["API Server"]=$API_RESULT  
    ["Calculator Server"]=$CALC_RESULT
    ["Multi-Server Client"]=$CLIENT_RESULT
    ["Integration Tests"]=$INTEGRATION_RESULT
    ["Tool Preservation"]=$PRESERVATION_RESULT
)

passed=0
failed=0

for test_name in "${!results[@]}"; do
    if [ ${results[$test_name]} -eq 0 ]; then
        echo -e "${GREEN}✅ $test_name: PASSED${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ $test_name: FAILED${NC}"
        ((failed++))
    fi
done

echo ""
echo "Summary: $passed passed, $failed failed"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above for details.${NC}"
    exit 1
fi