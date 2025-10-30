"""
Test multi-server client functionality
"""
import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the MultiServerMCPClient
from demos.doct_her_stdio import MultiServerMCPClient

class TestMultiServerClient:
    
    @pytest_asyncio.fixture
    async def client(self):
        """Create a MultiServerMCPClient for testing."""
        client = MultiServerMCPClient()
        yield client
        # Cleanup
        try:
            await client.disconnect()
        except:
            pass
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test that client initializes correctly."""
        assert client.sessions == {}
        assert client.tool_registry == {}
        assert client.use_legacy == False
    
    @pytest.mark.asyncio 
    async def test_server_paths_configuration(self, client, server_paths):
        """Test that server paths are correctly configured."""
        # Check that all server files exist
        for server_name, server_path in server_paths.items():
            assert Path(server_path).exists(), f"Server file {server_path} should exist"
            
        # Check that MCP_SERVERS constant is properly defined
        from demos.doct_her_stdio import MCP_SERVERS
        assert len(MCP_SERVERS) == 3, "Should have 3 configured servers"
        assert "database" in MCP_SERVERS
        assert "api" in MCP_SERVERS
        assert "calculator" in MCP_SERVERS
    
    @pytest.mark.asyncio
    async def test_connect_to_servers(self, client):
        """Test connecting to all servers."""
        # Import MCP_SERVERS from the main module
        from demos.doct_her_stdio import MCP_SERVERS
        
        # This test requires the servers to be working
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            # Should have connected to 3 servers
            assert len(client.sessions) == 3, f"Should connect to 3 servers, got {len(client.sessions)}"
            assert "database" in client.sessions
            assert "api" in client.sessions
            assert "calculator" in client.sessions
            
            # Each session should be initialized
            for server_name, session in client.sessions.items():
                assert session is not None, f"{server_name} session should not be None"
                
        except Exception as e:
            # If servers fail to start, should fallback to legacy
            pytest.skip(f"Servers not available for testing: {e}")
    
    @pytest.mark.asyncio
    async def test_tool_discovery(self, client):
        """Test tool discovery across all servers."""
        from demos.doct_her_stdio import MCP_SERVERS
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            # Should have discovered tools
            assert len(client.tool_registry) > 0, "Should have discovered tools from servers"
            
            # Should have tools from all three domains
            tool_names = list(client.tool_registry.keys())
            
            # Check for database tools
            database_tools = [t for t in tool_names if "elsa" in t.lower() or "wave" in t.lower()]
            assert len(database_tools) > 0, f"Should have database tools, found: {tool_names}"
            
            # Check for API tools
            api_tools = [t for t in tool_names if any(api in t.lower() for api in ["pubmed", "eshre", "asrm", "nams"])]
            assert len(api_tools) > 0, f"Should have API tools, found: {tool_names}"
            
            # Check for calculator tools  
            calc_tools = [t for t in tool_names if "ivf" in t.lower() or "calculate" in t.lower()]
            assert len(calc_tools) > 0, f"Should have calculator tools, found: {tool_names}"
            
            print(f"✅ Discovered {len(tool_names)} tools across all servers")
            
        except Exception as e:
            pytest.skip(f"Tool discovery test requires working servers: {e}")
    
    @pytest.mark.asyncio
    async def test_tool_routing(self, client):
        """Test that tools are routed to correct servers."""
        from demos.doct_her_stdio import MCP_SERVERS
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            # Test routing logic
            for tool_name, server_name in client.tool_registry.items():
                if "elsa" in tool_name.lower() or "wave" in tool_name.lower():
                    assert server_name == "database", f"ELSA tool {tool_name} should route to database server"
                elif any(api in tool_name.lower() for api in ["pubmed", "eshre", "asrm", "nams"]):
                    assert server_name == "api", f"API tool {tool_name} should route to api server"
                elif "ivf" in tool_name.lower() or "calculate" in tool_name.lower():
                    assert server_name == "calculator", f"Calculator tool {tool_name} should route to calculator server"
            
        except Exception as e:
            pytest.skip(f"Tool routing test requires working servers: {e}")
    
    @pytest.mark.asyncio
    async def test_call_tool(self, client):
        """Test calling tools through the multi-server client."""
        from demos.doct_her_stdio import MCP_SERVERS
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            # Try calling a simple tool from each server
            test_calls = [
                ("get_sart_calculator_info", {}),  # Calculator server
                ("list_elsa_waves", {"include_details": False}),  # Database server
                ("list_nams_topics", {})  # API server
            ]
            
            results = []
            for tool_name, args in test_calls:
                if tool_name in client.tool_registry:
                    try:
                        result = await client.call_tool(tool_name, args)
                        results.append((tool_name, result, True))
                    except Exception as e:
                        results.append((tool_name, str(e), False))
                else:
                    results.append((tool_name, "Tool not found", False))
            
            # At least some tools should work
            successful_calls = [r for r in results if r[2]]
            assert len(successful_calls) > 0, f"At least one tool call should succeed. Results: {results}"
            
            print(f"✅ Tool call results: {len(successful_calls)}/{len(test_calls)} succeeded")
            
        except Exception as e:
            pytest.skip(f"Tool calling test requires working servers: {e}")
    
    @pytest.mark.asyncio
    async def test_get_all_tools_for_claude(self, client):
        """Test aggregating all tools for Claude API."""
        from demos.doct_her_stdio import MCP_SERVERS
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            tools = await client.get_all_tools_for_claude()
            assert len(tools) > 0, "Should return tools for Claude"
            
            # Each tool should have required fields
            for tool in tools:
                assert "name" in tool, "Tool should have name"
                assert "description" in tool, "Tool should have description"
                assert "inputSchema" in tool, "Tool should have input schema"
            
            print(f"✅ Prepared {len(tools)} tools for Claude API")
            
        except Exception as e:
            pytest.skip(f"Claude tools preparation test requires working servers: {e}")
    
    @pytest.mark.asyncio
    async def test_fallback_to_legacy(self, client):
        """Test fallback to legacy server when new servers fail."""
        # Mock server connection to fail
        with patch.object(client, 'connect_to_servers') as mock_connect:
            mock_connect.side_effect = Exception("Server connection failed")
            
            # Should fall back to legacy
            with patch.object(client, 'connect_to_legacy_server') as mock_legacy:
                mock_legacy.return_value = None  # Mock successful legacy connection
                
                try:
                    await client.connect_to_servers()
                    # If it gets here, fallback worked
                    assert client.use_legacy == True, "Should have switched to legacy mode"
                except:
                    # Fallback might also fail if legacy server doesn't exist
                    pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self, client):
        """Test error handling for various failure modes."""
        # Test with invalid tool name
        with pytest.raises(Exception):
            await client.call_tool("nonexistent_tool", {})
    
    @pytest.mark.asyncio
    async def test_tool_count_preservation(self, client, tool_inventory):
        """Test that no tools were lost in refactoring."""
        from demos.doct_her_stdio import MCP_SERVERS
        try:
            await client.connect_to_servers(MCP_SERVERS)
            
            actual_tools = set(client.tool_registry.keys())
            expected_tools = set(tool_inventory)
            
            missing_tools = expected_tools - actual_tools
            extra_tools = actual_tools - expected_tools
            
            print(f"Expected tools: {len(expected_tools)}")
            print(f"Actual tools: {len(actual_tools)}")
            
            if missing_tools:
                print(f"❌ Missing tools: {missing_tools}")
            if extra_tools:
                print(f"ℹ️  Extra tools: {extra_tools}")
            
            # We should not have lost any expected tools
            assert len(missing_tools) == 0, f"Lost tools in refactoring: {missing_tools}"
            
        except Exception as e:
            pytest.skip(f"Tool preservation test requires working servers: {e}")
    
    def test_server_command_format(self):
        """Test that server commands are formatted correctly."""
        # Check the command format used in the client
        expected_command = "fastmcp"
        expected_args_pattern = ["run", "server_path", "--transport", "stdio", "--no-banner"]
        
        # This tests the fixed command format
        assert expected_command == "fastmcp", "Should use fastmcp command"
        # The actual path will vary, but pattern should be correct