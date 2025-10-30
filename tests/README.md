# MCP Testing Suite

This directory contains comprehensive tests for the Women's Health MCP multi-server architecture.

## Test Organization

### Individual Server Tests
- `test_database_server.py` - Tests ELSA longitudinal aging data server
- `test_api_server.py` - Tests PubMed, ESHRE, ASRM, NAMS API server  
- `test_calculator_server.py` - Tests SART IVF calculator server

### Integration Tests
- `test_multi_server_client.py` - Tests the MultiServerMCPClient
- `test_integration.py` - End-to-end integration tests
- `test_tool_preservation.py` - Verifies no tools were lost in refactoring

### Test Utilities
- `conftest.py` - Pytest fixtures and test configuration
- `mocks/` - Mock data and responses for testing
- `run_all_tests.sh` - Test runner script

## Running Tests

### Run All Tests
```bash
# From project root
./tests/run_all_tests.sh
```

### Run Specific Test Files
```bash
# Individual server tests
pytest tests/test_database_server.py -v
pytest tests/test_api_server.py -v
pytest tests/test_calculator_server.py -v

# Multi-server tests
pytest tests/test_multi_server_client.py -v
pytest tests/test_integration.py -v
pytest tests/test_tool_preservation.py -v
```

### Run with Different Options
```bash
# Verbose output
pytest tests/ -v

# Show only failing tests
pytest tests/ --tb=short

# Stop on first failure
pytest tests/ -x

# Run specific test method
pytest tests/test_database_server.py::TestDatabaseServer::test_list_elsa_waves -v
```

## Test Requirements

### Dependencies
- pytest
- pytest-asyncio
- mcp (Model Context Protocol)
- fastmcp

### Prerequisites
1. All three MCP servers must be executable:
   - `mcp_servers/database_server.py`
   - `mcp_servers/api_server.py` 
   - `mcp_servers/calculator_server.py`

2. FastMCP CLI must be available:
   ```bash
   fastmcp --version
   ```

3. Server inspection should work:
   ```bash
   fastmcp inspect mcp_servers/database_server.py
   ```

## Test Categories

### Unit Tests
- Individual server functionality
- Tool registration and discovery
- Input validation and error handling

### Integration Tests  
- Multi-server client connectivity
- Cross-server tool routing
- Agentic loop simulation (multiple tool calls)

### Preservation Tests
- Verify all expected tools are present
- Compare against TOOL_INVENTORY.md
- Check tool descriptions and schemas

### Performance Tests
- Basic response time validation
- Concurrent tool call handling

## Expected Outcomes

### Passing Tests Indicate
✅ All servers start successfully  
✅ All tools from TOOL_INVENTORY.md are registered  
✅ Multi-server client connects to all 3 servers  
✅ Tool routing works correctly  
✅ No tools were lost in refactoring  
✅ Error handling works properly  

### Common Failure Modes

#### FastMCP Execution Issues
- **Error**: `No module named fastmcp.__main__`
- **Fix**: Use `fastmcp run server.py` not `python -m fastmcp`

#### Server Connection Failures
- **Error**: Connection timeout or refused
- **Check**: Server can start independently with `fastmcp run server.py`

#### Missing Tools
- **Error**: Tool not found in registry
- **Check**: Tool has `@mcp.tool()` decorator in server file

#### Import/Path Issues  
- **Error**: Module not found
- **Check**: Python path includes project root

## Debugging Failed Tests

### 1. Check Server Status
```bash
# Test each server individually
fastmcp inspect mcp_servers/database_server.py
fastmcp inspect mcp_servers/api_server.py  
fastmcp inspect mcp_servers/calculator_server.py
```

### 2. Check Tool Registration
```bash
# Should show all tools for each server
fastmcp inspect mcp_servers/database_server.py --format mcp
```

### 3. Test Client Connection
```bash
# Run basic connection test
python -c "
import asyncio
from demos.doct_her_stdio import MultiServerMCPClient
async def test():
    client = MultiServerMCPClient()
    await client.connect_to_servers()
    print(f'Connected to {len(client.sessions)} servers')
    print(f'Discovered {len(client.tool_registry)} tools')
asyncio.run(test())
"
```

### 4. Verbose Test Output
```bash
pytest tests/test_database_server.py -v -s --tb=long
```

## Adding New Tests

When adding new tools or servers:

1. **Add unit tests** in appropriate server test file
2. **Update tool expectations** in test_tool_preservation.py
3. **Add integration scenarios** in test_integration.py  
4. **Update TOOL_INVENTORY.md** with new tools
5. **Run full test suite** to ensure no regressions

## Test Data

Mock data is provided in `mocks/` directory:
- `mock_pubmed_responses.json` - Sample PubMed API responses
- `mock_elsa_data.json` - Sample ELSA dataset information

## Continuous Testing

For development workflow:
1. Run tests before committing changes
2. Add new tests for new functionality  
3. Update tests when modifying existing tools
4. Use `./tests/run_all_tests.sh` for comprehensive validation

## Success Criteria

All tests should pass for:
- ✅ FastMCP servers execute correctly
- ✅ All 28+ expected tools are registered  
- ✅ Multi-server client routes tools properly
- ✅ Integration flows work end-to-end
- ✅ No tools lost during refactoring
- ✅ Error handling is robust