"""
Test database server tools (ELSA longitudinal aging data)
"""
import pytest
import pytest_asyncio
import asyncio
import subprocess
import sys
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestDatabaseServer:
    
    @pytest_asyncio.fixture
    async def database_session(self):
        """Create a session connected to the database server."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "database_server.py"
        
        server_params = StdioServerParameters(
            command="fastmcp",
            args=["run", str(server_path), "--transport", "stdio", "--no-banner"]
        )
        
        async with stdio_client(server_params) as (stdio, write):
            session = ClientSession(stdio, write)
            await session.initialize()
            yield session
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, database_session):
        """Test that database server initializes successfully."""
        tools = await database_session.list_tools()
        assert len(tools.tools) > 0, "Database server should have registered tools"
    
    @pytest.mark.asyncio
    async def test_list_elsa_waves(self, database_session):
        """Test list_elsa_waves tool."""
        result = await database_session.call_tool("list_elsa_waves", {"include_details": False})
        
        assert result.isError == False, f"list_elsa_waves should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        assert len(result.content) > 0, "Should return at least one result"
        
        # Check if content contains wave information
        content_str = str(result.content[0].text) if result.content else ""
        assert "wave" in content_str.lower() or "ELSA" in content_str, "Should contain ELSA wave information"
    
    @pytest.mark.asyncio
    async def test_search_data_modules(self, database_session):
        """Test search_data_modules tool."""
        result = await database_session.call_tool("search_data_modules", {"query": "health"})
        
        assert result.isError == False, f"search_data_modules should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        # Should return some health-related modules
        content_str = str(result.content[0].text) if result.content else ""
        assert len(content_str) > 10, "Should return meaningful content"
    
    @pytest.mark.asyncio
    async def test_get_access_information(self, database_session):
        """Test get_access_information tool."""
        result = await database_session.call_tool("get_access_information", {})
        
        assert result.isError == False, f"get_access_information should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "access" in content_str.lower() or "data" in content_str.lower(), "Should contain access information"
    
    @pytest.mark.asyncio
    async def test_all_database_tools_registered(self, database_session, tool_inventory):
        """Test that all expected database tools are registered."""
        tools = await database_session.list_tools()
        tool_names = [tool.name for tool in tools.tools]
        
        expected_database_tools = [
            "list_elsa_waves", "get_wave_details", "search_data_modules",
            "get_data_module_info", "get_access_information", "get_study_metadata",
            "get_documentation_links", "compare_waves", "get_research_examples"
        ]
        
        missing_tools = [tool for tool in expected_database_tools if tool not in tool_names]
        assert len(missing_tools) == 0, f"Missing database tools: {missing_tools}"
        
        print(f"✅ Database server registered {len(tool_names)} tools: {tool_names}")
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self, database_session):
        """Test that invalid tool calls are handled gracefully."""
        # Test with invalid tool name
        with pytest.raises(Exception):  # Should raise an exception for unknown tool
            await database_session.call_tool("nonexistent_tool", {})
    
    def test_server_can_start_independently(self):
        """Test that the server can start as a standalone process."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "database_server.py"
        
        # Test that fastmcp can inspect the server
        result = subprocess.run([
            "fastmcp", "inspect", str(server_path)
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, f"Server inspection failed: {result.stderr}"
        assert "Tools:" in result.stdout, "Server should have tools"
        assert "women-health-database" in result.stdout, "Server should have correct name"