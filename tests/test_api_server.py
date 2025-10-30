"""
Test API server tools (PubMed, ESHRE, ASRM, NAMS)
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

class TestAPIServer:
    
    @pytest_asyncio.fixture
    async def api_session(self):
        """Create a session connected to the API server."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "api_server.py"
        
        server_params = StdioServerParameters(
            command="fastmcp",
            args=["run", str(server_path), "--transport", "stdio", "--no-banner"]
        )
        
        async with stdio_client(server_params) as (stdio, write):
            session = ClientSession(stdio, write)
            await session.initialize()
            yield session
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, api_session):
        """Test that API server initializes successfully."""
        tools = await api_session.list_tools()
        assert len(tools.tools) > 0, "API server should have registered tools"
    
    @pytest.mark.asyncio
    async def test_search_pubmed(self, api_session):
        """Test search_pubmed tool."""
        result = await api_session.call_tool("search_pubmed", {
            "query": "endometriosis treatment",
            "max_results": 5
        })
        
        assert result.isError == False, f"search_pubmed should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "Found" in content_str and "articles" in content_str, "Should return search results"
        assert "endometriosis" in content_str.lower() or "treatment" in content_str.lower(), "Should contain query terms"
    
    @pytest.mark.asyncio
    async def test_get_article(self, api_session):
        """Test get_article tool with a known PMID."""
        # Use a well-known PMID for testing
        result = await api_session.call_tool("get_article", {"pmid": "34567890"})
        
        # Note: This might fail if the PMID doesn't exist, but should handle gracefully
        assert isinstance(result.content, list), "Result should be a list"
        
        if not result.isError:
            content_str = str(result.content[0].text) if result.content else ""
            assert "PMID" in content_str, "Should contain PMID information"
    
    @pytest.mark.asyncio
    async def test_list_eshre_guidelines(self, api_session):
        """Test list_eshre_guidelines tool."""
        result = await api_session.call_tool("list_eshre_guidelines", {})
        
        assert result.isError == False, f"list_eshre_guidelines should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "ESHRE" in content_str or "guidelines" in content_str.lower(), "Should contain ESHRE information"
    
    @pytest.mark.asyncio
    async def test_search_eshre_guidelines(self, api_session):
        """Test search_eshre_guidelines tool."""
        result = await api_session.call_tool("search_eshre_guidelines", {"query": "IVF"})
        
        assert result.isError == False, f"search_eshre_guidelines should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert len(content_str) > 10, "Should return meaningful content"
    
    @pytest.mark.asyncio
    async def test_list_asrm_practice_documents(self, api_session):
        """Test list_asrm_practice_documents tool."""
        result = await api_session.call_tool("list_asrm_practice_documents", {})
        
        assert result.isError == False, f"list_asrm_practice_documents should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "ASRM" in content_str or "practice" in content_str.lower(), "Should contain ASRM information"
    
    @pytest.mark.asyncio
    async def test_list_nams_position_statements(self, api_session):
        """Test list_nams_position_statements tool."""
        result = await api_session.call_tool("list_nams_position_statements", {})
        
        assert result.isError == False, f"list_nams_position_statements should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "NAMS" in content_str or "position" in content_str.lower() or "menopause" in content_str.lower(), "Should contain NAMS information"
    
    @pytest.mark.asyncio
    async def test_all_api_tools_registered(self, api_session):
        """Test that all expected API tools are registered."""
        tools = await api_session.list_tools()
        tool_names = [tool.name for tool in tools.tools]
        
        expected_api_tools = [
            "search_pubmed", "get_article", "get_multiple_articles",
            "list_eshre_guidelines", "search_eshre_guidelines", "get_eshre_guideline",
            "list_asrm_practice_documents", "list_asrm_ethics_opinions", 
            "search_asrm_guidelines", "get_asrm_guideline",
            "list_nams_position_statements", "search_nams_protocols", 
            "get_nams_protocol", "list_nams_topics"
        ]
        
        missing_tools = [tool for tool in expected_api_tools if tool not in tool_names]
        extra_tools = [tool for tool in tool_names if tool not in expected_api_tools]
        
        print(f"✅ API server registered {len(tool_names)} tools: {tool_names}")
        if missing_tools:
            print(f"❌ Missing API tools: {missing_tools}")
        if extra_tools:
            print(f"ℹ️  Extra API tools: {extra_tools}")
        
        # We expect all tools to be registered
        assert len(missing_tools) == 0, f"Missing API tools: {missing_tools}"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, api_session):
        """Test API error handling for invalid requests."""
        # Test with invalid PMID
        result = await api_session.call_tool("get_article", {"pmid": "invalid_pmid"})
        
        # Should handle gracefully (either return error or empty result)
        assert isinstance(result.content, list), "Should return a list even for errors"
    
    @pytest.mark.asyncio
    async def test_pubmed_rate_limiting(self, api_session):
        """Test that PubMed rate limiting is respected."""
        # Make multiple quick requests
        results = []
        for i in range(3):
            result = await api_session.call_tool("search_pubmed", {
                "query": f"test query {i}",
                "max_results": 1
            })
            results.append(result)
            # Small delay to respect rate limits
            await asyncio.sleep(0.5)
        
        # All requests should complete without rate limit errors
        for result in results:
            assert isinstance(result.content, list), "All requests should return results"
    
    def test_server_can_start_independently(self):
        """Test that the server can start as a standalone process."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "api_server.py"
        
        # Test that fastmcp can inspect the server
        result = subprocess.run([
            "fastmcp", "inspect", str(server_path)
        ], capture_output=True, text=True, timeout=15)
        
        assert result.returncode == 0, f"Server inspection failed: {result.stderr}"
        assert "Tools:" in result.stdout, "Server should have tools"
        assert "women-health-api" in result.stdout, "Server should have correct name"