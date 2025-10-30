# Debugging & Testing MCP Refactoring: Fix FastMCP Execution & Add Comprehensive Tests

## Current Problem

The refactored MCP architecture is failing with:
````
/Users/sunaina/.pyenv/versions/3.12.9/envs/lewagon/bin/python: No module named fastmcp.__main__; 'fastmcp' is a package and cannot be directly executed
````

This means our FastMCP servers aren't being executed correctly.

## Your Tasks

### Task 1: Fix FastMCP Server Execution

**Problem:** The command `python -m fastmcp run mcp_servers/database_server.py` doesn't work.

**Investigation needed:**
1. Check how FastMCP servers should actually be run
2. Look at @mcp_servers/database_server.py, @mcp_servers/api_server.py, @mcp_servers/calculator_server.py
3. Check FastMCP documentation or examples for correct execution method
4. Verify if servers need a `if __name__ == "__main__"` block

**Expected fixes:**
- Update server files to be directly executable: `python mcp_servers/database_server.py`
- OR find correct FastMCP CLI command
- OR create a run script that properly executes FastMCP servers
- Update @demos/doct_her_stdio.py client connection to use correct command

**Test the fix:**
````bash
# This should work after your fix
python mcp_servers/database_server.py  # Should start the server

# OR
fastmcp run mcp_servers/database_server.py  # If there's a CLI tool

# OR whatever the correct method is
````

### Task 2: Write Comprehensive Tests for MCP Architecture

Create tests in `tests/` directory to evaluate:

#### 2.1 Individual Server Tests

**Test each FastMCP server independently:**

`tests/test_database_server.py`:
````python
"""
Test database server tools:
- search_elsa_data returns correct data structure
- list_waves returns available waves
- All tools from TOOL_INVENTORY.md are registered
- Error handling for invalid queries
"""
````

`tests/test_api_server.py`:
````python
"""
Test API server tools:
- search_pubmed returns PubMed articles
- get_article retrieves correct article
- fetch_abstract returns abstract
- get_eshre_guideline returns guidelines
- search_asrm_guidelines works
- search_nams_protocols works
- All API tools from TOOL_INVENTORY.md are registered
- Handles API errors gracefully (network, rate limits, auth)
"""
````

`tests/test_calculator_server.py`:
````python
"""
Test calculator server tools:
- calculate_ivf_success returns predictions
- generate_recommendations returns advice
- All calculator tools from TOOL_INVENTORY.md are registered
- Input validation works
"""
````

#### 2.2 Multi-Server Client Tests

`tests/test_multi_server_client.py`:
````python
"""
Test client connecting to all servers:
- Client connects to all 3 servers successfully
- Client discovers tools from all servers
- Tool registry correctly maps tool names to servers
- Total tool count matches TOOL_INVENTORY.md
- call_tool() correctly routes to appropriate server
- get_all_tools_for_claude() aggregates all tools
- Handles server connection failures gracefully
"""
````

#### 2.3 Integration Tests

`tests/test_integration.py`:
````python
"""
Test complete query flow:
- User query → Client → Multiple servers → Response
- Agentic loop works (multiple tool calls)
- Tools from different servers can be used in same query
- Example: "Calculate IVF success then search PubMed"
  Should call calculator server, then API server
"""
````

#### 2.4 Tool Preservation Tests

`tests/test_tool_preservation.py`:
````python
"""
Verify no tools were lost in refactoring:
- Load TOOL_INVENTORY.md
- Compare expected tools vs actual registered tools
- Flag any missing tools
- Flag any unexpected new tools
- Verify tool descriptions are present and meaningful
"""
````

### Task 3: Implement Test Fixtures & Mocks

**Create test utilities:**

`tests/conftest.py`:
````python
"""
Pytest fixtures for all tests:
- Mock FastMCP servers for testing
- Mock external APIs (PubMed, ESHRE, ASRM, NAMS)
- Sample medical queries
- Sample tool responses
"""
````

`tests/mocks/`:
````
mocks/
├── mock_pubmed_responses.json
├── mock_elsa_data.json
├── mock_ivf_calculations.json
└── mock_api_responses.py
````

### Task 4: Run Tests & Identify Failures

**Execute all tests and report:**

1. Run each test file independently
2. Document which tests pass ✅ and which fail ❌
3. For each failure, identify:
   - What component is broken (server, client, tool, routing)
   - Error message and stack trace
   - Root cause hypothesis
   - Suggested fix

**Output format:**
````markdown
## Test Results

### test_database_server.py
- ✅ test_search_elsa_data_structure
- ❌ test_list_waves_returns_data
  - Error: ConnectionError - Cannot connect to server
  - Root cause: Server not starting correctly (FastMCP execution issue)
  - Fix: Update server execution method

### test_api_server.py
- ❌ test_pubmed_search_basic
  - Error: Tool not found in registry
  - Root cause: search_pubmed not registered in api_server.py
  - Fix: Add @mcp.tool() decorator to search_pubmed

[Continue for all tests...]
````

### Task 5: Propose & Implement Fixes

Based on test failures, systematically fix each issue:

**Priority 1: FastMCP Execution (Blocking)**
- Fix how servers are started
- Update client connection code
- Verify servers can run independently

**Priority 2: Tool Registration (Critical)**
- Ensure all tools from TOOL_INVENTORY.md are registered
- Add missing @mcp.tool() decorators
- Fix tool naming inconsistencies

**Priority 3: Client Routing (Critical)**
- Fix tool discovery across multiple servers
- Fix tool routing to correct server
- Handle connection errors

**Priority 4: Integration (High)**
- Fix agentic loop
- Fix cross-server tool calls
- Verify Claude can see and use all tools

**Priority 5: Error Handling (Medium)**
- API error handling
- Network timeouts
- Rate limiting

### Task 6: Continuous Testing Setup

**Create test automation:**

`tests/run_all_tests.sh`:
````bash
#!/bin/bash
# Run all tests and report results
pytest tests/ -v --tb=short
````

`tests/test_on_change.py`:
````python
"""
Monitor file changes and auto-run relevant tests:
- If mcp_servers/database_server.py changes → run test_database_server.py
- If mcp_servers/api_server.py changes → run test_api_server.py
- If demos/doct_her_stdio.py changes → run test_multi_server_client.py
"""
````

`.github/workflows/test.yml` (if using GitHub):
````yaml
# Run tests on every commit
````

### Task 7: Test Documentation

Create `tests/README.md`:
````markdown
# MCP Testing Suite

## Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database_server.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mcp_servers --cov=demos
```

## Test Organization

- `test_database_server.py` - ELSA database server
- `test_api_server.py` - PubMed/ESHRE/ASRM/NAMS API server
- `test_calculator_server.py` - SART IVF calculator server
- `test_multi_server_client.py` - Multi-server client
- `test_integration.py` - End-to-end tests
- `test_tool_preservation.py` - Verify no tools lost

## Adding New Tests

When adding new tools:
1. Add test to appropriate server test file
2. Update tool count expectations
3. Add integration test if tool interacts with other servers
````

## Execution Order

1. **First:** Fix FastMCP execution issue (Task 1)
   - This is blocking everything else
   - Test that servers can start independently

2. **Second:** Write tests (Task 2-3)
   - Write all test files
   - Create mocks and fixtures

3. **Third:** Run tests and document failures (Task 4)
   - Run each test suite
   - Create detailed failure report

4. **Fourth:** Fix issues based on test results (Task 5)
   - Start with Priority 1 (blocking issues)
   - Work through priorities systematically
   - Re-run tests after each fix

5. **Fifth:** Set up continuous testing (Task 6)
   - Create automation scripts
   - Document testing process

## Success Criteria

- [ ] All 3 FastMCP servers start successfully
- [ ] Client connects to all 3 servers
- [ ] All tools from TOOL_INVENTORY.md are registered and working
- [ ] All tests pass ✅
- [ ] Integration tests verify complete query flow works
- [ ] Tests run automatically on code changes
- [ ] Zero tools lost in refactoring (verified by tests)

## Critical Questions to Answer

1. **How should FastMCP servers be executed?**
   - Direct execution? CLI tool? Wrapper script?

2. **Which tests are failing and why?**
   - Server connection? Tool registration? Routing?

3. **Are all tools preserved?**
   - Compare TOOL_INVENTORY.md vs actual registered tools

4. **Does the multi-server architecture work end-to-end?**
   - Can Claude use tools from all 3 servers in one query?

## Output Format

Present your findings as:

### 1. FastMCP Execution Fix
````
Problem: [description]
Investigation: [what you found]
Solution: [code changes]
Verification: [how to test it works]
````

### 2. Test Results Summary
````
Total Tests: X
Passing: Y ✅
Failing: Z ❌

Critical Failures:
- [test name]: [root cause] → [proposed fix]
- ...

Minor Failures:
- [test name]: [root cause] → [proposed fix]
- ...
````

### 3. Proposed Fixes
````
Priority 1 Fixes (Blocking):
- Fix #1: [description] → [implementation]
- Fix #2: [description] → [implementation]

Priority 2 Fixes (Critical):
- ...
````

### 4. Implementation Plan
````
Step 1: [what to do]
Step 2: [what to do]
...
````

---

**Start by:**
1. Investigating the FastMCP execution error
2. Fixing how servers are started
3. Writing comprehensive tests
4. Running tests to identify all failures
5. Systematically fixing issues

**Think through the problem before coding.** Show me your analysis of what's broken and your plan to fix it.
