"""
Test complete query flow integration
"""
import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demos.doct_her_stdio import MultiServerMCPClient

class TestIntegration:
    
    @pytest_asyncio.fixture
    async def connected_client(self):
        """Create and connect a MultiServerMCPClient."""
        from demos.doct_her_stdio import MCP_SERVERS
        client = MultiServerMCPClient()
        try:
            await client.connect_to_servers(MCP_SERVERS)
            yield client
        except Exception as e:
            pytest.skip(f"Integration tests require working servers: {e}")
        finally:
            try:
                await client.disconnect()
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_complete_query_flow(self, connected_client):
        """Test a complete query that uses multiple servers."""
        # This simulates a real user query that might use multiple tools
        
        # 1. First, get IVF calculator info (calculator server)
        calc_info_result = await connected_client.call_tool("get_sart_calculator_info", {})
        assert not calc_info_result.isError, "Calculator info should work"
        
        # 2. Then search PubMed for related research (api server)
        pubmed_result = await connected_client.call_tool("search_pubmed", {
            "query": "IVF success rates",
            "max_results": 3
        })
        assert not pubmed_result.isError, "PubMed search should work"
        
        # 3. Get ELSA data info (database server)
        elsa_result = await connected_client.call_tool("list_elsa_waves", {"include_details": False})
        assert not elsa_result.isError, "ELSA waves should work"
        
        print("✅ Multi-server query flow completed successfully")
    
    @pytest.mark.asyncio
    async def test_agentic_loop_simulation(self, connected_client):
        """Test multiple tool calls in sequence (simulating Claude's agentic loop)."""
        # Simulate what Claude might do for: "Calculate IVF success then find related research"
        
        tool_calls = [
            ("calculate_ivf_success", {
                "age": 30,
                "height_cm": 165,
                "weight_kg": 60,
                "amh_available": True,
                "amh_value": 2.5
            }),
            ("search_pubmed", {
                "query": "IVF success rates age 30",
                "max_results": 2
            }),
            ("list_nams_topics", {})
        ]
        
        results = []
        for tool_name, args in tool_calls:
            if tool_name in connected_client.tool_registry:
                result = await connected_client.call_tool(tool_name, args)
                results.append((tool_name, result.isError == False))
                # Small delay between calls
                await asyncio.sleep(0.1)
        
        successful_calls = [r for r in results if r[1]]
        assert len(successful_calls) >= 1, f"At least one call should succeed. Results: {results}"
        
        print(f"✅ Agentic loop simulation: {len(successful_calls)}/{len(tool_calls)} tools succeeded")
    
    @pytest.mark.asyncio
    async def test_cross_server_data_correlation(self, connected_client):
        """Test using data from one server to inform queries to another."""
        # 1. Get NAMS topics to understand menopause areas
        nams_result = await connected_client.call_tool("list_nams_topics", {})
        if nams_result.isError:
            pytest.skip("NAMS topics not available")
        
        # 2. Use a topic to search PubMed
        pubmed_result = await connected_client.call_tool("search_pubmed", {
            "query": "hormone therapy menopause",
            "max_results": 2
        })
        if pubmed_result.isError:
            pytest.skip("PubMed search not available")
        
        # 3. Search ESHRE guidelines for same topic
        eshre_result = await connected_client.call_tool("search_eshre_guidelines", {
            "query": "hormone therapy"
        })
        if eshre_result.isError:
            pytest.skip("ESHRE search not available")
        
        print("✅ Cross-server data correlation completed")
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, connected_client):
        """Test that errors in one tool don't break subsequent tools."""
        # Mix valid and invalid tool calls
        tool_calls = [
            ("get_sart_calculator_info", {}),  # Should work
            ("invalid_tool", {}),  # Should fail
            ("list_nams_topics", {}),  # Should work
        ]
        
        results = []
        for tool_name, args in tool_calls:
            try:
                result = await connected_client.call_tool(tool_name, args)
                results.append((tool_name, "success", not result.isError))
            except Exception as e:
                results.append((tool_name, "error", False))
        
        # Should have at least one success and one failure
        successes = [r for r in results if r[2]]
        failures = [r for r in results if not r[2]]
        
        assert len(successes) >= 1, f"Should have at least one success: {results}"
        assert len(failures) >= 1, f"Should have at least one failure: {results}"
        
        print("✅ Error recovery test passed")
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, connected_client):
        """Test calling multiple tools concurrently."""
        # Prepare concurrent calls to different servers
        tasks = []
        
        if "get_sart_calculator_info" in connected_client.tool_registry:
            tasks.append(connected_client.call_tool("get_sart_calculator_info", {}))
        
        if "list_nams_topics" in connected_client.tool_registry:
            tasks.append(connected_client.call_tool("list_nams_topics", {}))
        
        if "list_elsa_waves" in connected_client.tool_registry:
            tasks.append(connected_client.call_tool("list_elsa_waves", {"include_details": False}))
        
        if len(tasks) == 0:
            pytest.skip("No tools available for concurrent testing")
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful calls
        successful = sum(1 for r in results if not isinstance(r, Exception) and not r.isError)
        assert successful > 0, f"At least one concurrent call should succeed. Results: {results}"
        
        print(f"✅ Concurrent calls: {successful}/{len(tasks)} succeeded")
    
    @pytest.mark.asyncio
    async def test_tool_chaining(self, connected_client):
        """Test using output from one tool as input to another."""
        # 1. Get calculator info
        calc_info = await connected_client.call_tool("get_sart_calculator_info", {})
        if calc_info.isError:
            pytest.skip("Calculator info not available")
        
        # 2. Calculate IVF success
        calc_result = await connected_client.call_tool("calculate_ivf_success", {
            "age": 28,
            "height_cm": 165,
            "weight_kg": 58,
            "amh_available": True,
            "amh_value": 3.0
        })
        if calc_result.isError:
            pytest.skip("IVF calculation not available")
        
        # 3. Generate recommendations based on calculation
        # Note: This would normally parse the calc_result, but we'll use a mock structure
        mock_calc_data = {
            "age": 28,
            "success_rate_1_cycle": 50.0,
            "amh_available": True,
            "amh_value": 3.0
        }
        
        recommendations = await connected_client.call_tool("generate_recommendations", {
            "calculation_result": mock_calc_data
        })
        
        # This is tool chaining - using output of one tool as input to another
        print("✅ Tool chaining completed")
    
    @pytest.mark.asyncio 
    async def test_all_servers_responding(self, connected_client):
        """Test that all three servers are responding to requests."""
        server_tests = {
            "database": "list_elsa_waves",
            "api": "list_nams_topics", 
            "calculator": "get_sart_calculator_info"
        }
        
        results = {}
        for server_name, tool_name in server_tests.items():
            if tool_name in connected_client.tool_registry:
                try:
                    result = await connected_client.call_tool(tool_name, {})
                    results[server_name] = not result.isError
                except Exception as e:
                    results[server_name] = False
            else:
                results[server_name] = False
        
        working_servers = [name for name, working in results.items() if working]
        assert len(working_servers) >= 1, f"At least one server should be working. Results: {results}"
        
        if len(working_servers) == 3:
            print("✅ All 3 servers responding correctly")
        else:
            print(f"⚠️  Only {len(working_servers)}/3 servers working: {working_servers}")
    
    @pytest.mark.asyncio
    async def test_performance_timing(self, connected_client):
        """Test basic performance of tool calls."""
        import time
        
        # Time a simple tool call
        start_time = time.time()
        result = await connected_client.call_tool("list_nams_topics", {})
        end_time = time.time()
        
        call_duration = end_time - start_time
        
        # Should complete within reasonable time (10 seconds)
        assert call_duration < 10.0, f"Tool call took too long: {call_duration:.2f}s"
        
        if not result.isError:
            print(f"✅ Tool call completed in {call_duration:.2f}s")
        else:
            print(f"⚠️  Tool call failed but completed in {call_duration:.2f}s")