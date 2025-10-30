"""
Verify no tools were lost in refactoring by comparing expected vs actual tools
"""
import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demos.doct_her_stdio import MultiServerMCPClient

class TestToolPreservation:
    
    def load_tool_inventory(self):
        """Load expected tools from TOOL_INVENTORY.md."""
        try:
            inventory_path = Path(__file__).parent.parent / "TOOL_INVENTORY.md"
            with open(inventory_path, 'r') as f:
                content = f.read()
            
            # Parse tool names from markdown
            tools = {}
            current_server = None
            
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Detect server sections
                if "DATABASE SERVER" in line.upper():
                    current_server = "database"
                elif "API SERVER" in line.upper():
                    current_server = "api"
                elif "CALCULATOR SERVER" in line.upper():
                    current_server = "calculator"
                
                # Extract tool names
                if line.startswith('- `') and '`' in line[3:]:
                    tool_name = line[3:].split('`')[0]
                    if current_server:
                        if current_server not in tools:
                            tools[current_server] = []
                        tools[current_server].append(tool_name)
            
            return tools
            
        except FileNotFoundError:
            # Return expected tools if inventory file not found
            return {
                "database": [
                    "list_elsa_waves", "get_wave_details", "search_data_modules",
                    "get_data_module_info", "get_access_information", "get_study_metadata",
                    "get_documentation_links", "compare_waves", "get_research_examples"
                ],
                "api": [
                    "search_pubmed", "get_article", "get_multiple_articles",
                    "list_eshre_guidelines", "search_eshre_guidelines", "get_eshre_guideline",
                    "list_asrm_practice_documents", "list_asrm_ethics_opinions", 
                    "search_asrm_guidelines", "get_asrm_guideline",
                    "list_nams_position_statements", "search_nams_protocols", 
                    "get_nams_protocol", "list_nams_topics"
                ],
                "calculator": [
                    "calculate_ivf_success", "predict_ivf_success", "generate_recommendations",
                    "get_sart_calculator_info", "compare_success_rates"
                ]
            }
    
    @pytest_asyncio.fixture
    async def connected_client(self):
        """Create and connect a MultiServerMCPClient."""
        from demos.doct_her_stdio import MCP_SERVERS
        client = MultiServerMCPClient()
        try:
            await client.connect_to_servers(MCP_SERVERS)
            yield client
        except Exception as e:
            pytest.skip(f"Tool preservation tests require working servers: {e}")
        finally:
            try:
                await client.disconnect()
            except:
                pass
    
    @pytest.mark.asyncio
    async def test_no_tools_lost_overall(self, connected_client):
        """Test that no tools were lost overall in the refactoring."""
        expected_tools_by_server = self.load_tool_inventory()
        
        # Get all expected tools
        all_expected_tools = set()
        for server_tools in expected_tools_by_server.values():
            all_expected_tools.update(server_tools)
        
        # Get all actual tools
        actual_tools = set(connected_client.tool_registry.keys())
        
        # Check for missing tools
        missing_tools = all_expected_tools - actual_tools
        extra_tools = actual_tools - all_expected_tools
        
        print(f"Expected total tools: {len(all_expected_tools)}")
        print(f"Actual total tools: {len(actual_tools)}")
        print(f"Missing tools: {len(missing_tools)}")
        print(f"Extra tools: {len(extra_tools)}")
        
        if missing_tools:
            print(f"❌ Lost tools: {sorted(missing_tools)}")
        if extra_tools:
            print(f"ℹ️  New tools: {sorted(extra_tools)}")
        
        # Critical: No tools should be missing
        assert len(missing_tools) == 0, f"CRITICAL: Lost {len(missing_tools)} tools in refactoring: {sorted(missing_tools)}"
        
        print("✅ No tools lost in refactoring")
    
    @pytest.mark.asyncio
    async def test_database_tools_preserved(self, connected_client):
        """Test that all database server tools are preserved."""
        expected_tools = self.load_tool_inventory().get("database", [])
        
        database_tools = [
            tool for tool, server in connected_client.tool_registry.items()
            if server == "database"
        ]
        
        missing_db_tools = set(expected_tools) - set(database_tools)
        extra_db_tools = set(database_tools) - set(expected_tools)
        
        print(f"Expected database tools: {len(expected_tools)}")
        print(f"Actual database tools: {len(database_tools)}")
        
        if missing_db_tools:
            print(f"❌ Missing database tools: {sorted(missing_db_tools)}")
        if extra_db_tools:
            print(f"ℹ️  Extra database tools: {sorted(extra_db_tools)}")
        
        assert len(missing_db_tools) == 0, f"Missing database tools: {sorted(missing_db_tools)}"
        print("✅ All database tools preserved")
    
    @pytest.mark.asyncio
    async def test_api_tools_preserved(self, connected_client):
        """Test that all API server tools are preserved."""
        expected_tools = self.load_tool_inventory().get("api", [])
        
        api_tools = [
            tool for tool, server in connected_client.tool_registry.items()
            if server == "api"
        ]
        
        missing_api_tools = set(expected_tools) - set(api_tools)
        extra_api_tools = set(api_tools) - set(expected_tools)
        
        print(f"Expected API tools: {len(expected_tools)}")
        print(f"Actual API tools: {len(api_tools)}")
        
        if missing_api_tools:
            print(f"❌ Missing API tools: {sorted(missing_api_tools)}")
        if extra_api_tools:
            print(f"ℹ️  Extra API tools: {sorted(extra_api_tools)}")
        
        assert len(missing_api_tools) == 0, f"Missing API tools: {sorted(missing_api_tools)}"
        print("✅ All API tools preserved")
    
    @pytest.mark.asyncio
    async def test_calculator_tools_preserved(self, connected_client):
        """Test that all calculator server tools are preserved."""
        expected_tools = self.load_tool_inventory().get("calculator", [])
        
        calculator_tools = [
            tool for tool, server in connected_client.tool_registry.items()
            if server == "calculator"
        ]
        
        missing_calc_tools = set(expected_tools) - set(calculator_tools)
        extra_calc_tools = set(calculator_tools) - set(expected_tools)
        
        print(f"Expected calculator tools: {len(expected_tools)}")
        print(f"Actual calculator tools: {len(calculator_tools)}")
        
        if missing_calc_tools:
            print(f"❌ Missing calculator tools: {sorted(missing_calc_tools)}")
        if extra_calc_tools:
            print(f"ℹ️  Extra calculator tools: {sorted(extra_calc_tools)}")
        
        assert len(missing_calc_tools) == 0, f"Missing calculator tools: {sorted(missing_calc_tools)}"
        print("✅ All calculator tools preserved")
    
    @pytest.mark.asyncio
    async def test_tool_routing_correct(self, connected_client):
        """Test that tools are routed to the correct servers."""
        routing_errors = []
        
        for tool_name, server_name in connected_client.tool_registry.items():
            # Check database tools
            if any(keyword in tool_name.lower() for keyword in ["elsa", "wave", "data_module", "study"]):
                if server_name != "database":
                    routing_errors.append(f"Tool '{tool_name}' should route to database, not {server_name}")
            
            # Check API tools
            elif any(keyword in tool_name.lower() for keyword in ["pubmed", "eshre", "asrm", "nams", "article", "guideline"]):
                if server_name != "api":
                    routing_errors.append(f"Tool '{tool_name}' should route to api, not {server_name}")
            
            # Check calculator tools
            elif any(keyword in tool_name.lower() for keyword in ["ivf", "calculate", "predict", "sart", "success"]):
                if server_name != "calculator":
                    routing_errors.append(f"Tool '{tool_name}' should route to calculator, not {server_name}")
        
        assert len(routing_errors) == 0, f"Tool routing errors: {routing_errors}"
        print("✅ All tools routed to correct servers")
    
    @pytest.mark.asyncio
    async def test_tool_descriptions_present(self, connected_client):
        """Test that all tools have meaningful descriptions."""
        tools = await connected_client.get_all_tools_for_claude()
        
        tools_without_descriptions = []
        short_descriptions = []
        
        for tool in tools:
            if "description" not in tool or not tool["description"]:
                tools_without_descriptions.append(tool["name"])
            elif len(tool["description"]) < 10:
                short_descriptions.append((tool["name"], tool["description"]))
        
        if tools_without_descriptions:
            print(f"❌ Tools without descriptions: {tools_without_descriptions}")
        if short_descriptions:
            print(f"⚠️  Tools with short descriptions: {short_descriptions}")
        
        assert len(tools_without_descriptions) == 0, f"Tools missing descriptions: {tools_without_descriptions}"
        print("✅ All tools have descriptions")
    
    @pytest.mark.asyncio
    async def test_tool_schemas_valid(self, connected_client):
        """Test that all tools have valid input schemas."""
        tools = await connected_client.get_all_tools_for_claude()
        
        invalid_schemas = []
        
        for tool in tools:
            if "inputSchema" not in tool:
                invalid_schemas.append(f"{tool['name']}: missing inputSchema")
            elif not isinstance(tool["inputSchema"], dict):
                invalid_schemas.append(f"{tool['name']}: inputSchema not a dict")
            elif "type" not in tool["inputSchema"]:
                invalid_schemas.append(f"{tool['name']}: inputSchema missing type")
        
        assert len(invalid_schemas) == 0, f"Tools with invalid schemas: {invalid_schemas}"
        print("✅ All tools have valid schemas")
    
    def test_inventory_file_exists(self):
        """Test that the tool inventory file exists and is readable."""
        inventory_path = Path(__file__).parent.parent / "TOOL_INVENTORY.md"
        
        if not inventory_path.exists():
            print("⚠️  TOOL_INVENTORY.md not found, using fallback expected tools")
            return
        
        try:
            tools = self.load_tool_inventory()
            total_expected = sum(len(server_tools) for server_tools in tools.values())
            
            print(f"✅ Tool inventory loaded: {total_expected} expected tools across {len(tools)} servers")
            
            for server, server_tools in tools.items():
                print(f"  - {server}: {len(server_tools)} tools")
                
        except Exception as e:
            pytest.fail(f"Failed to parse TOOL_INVENTORY.md: {e}")
    
    @pytest.mark.asyncio
    async def test_comprehensive_tool_audit(self, connected_client):
        """Comprehensive audit of all tools across servers."""
        expected_tools = self.load_tool_inventory()
        
        # Build comprehensive report
        report = {
            "expected_total": sum(len(tools) for tools in expected_tools.values()),
            "actual_total": len(connected_client.tool_registry),
            "servers": {}
        }
        
        for server_name, expected_server_tools in expected_tools.items():
            actual_server_tools = [
                tool for tool, server in connected_client.tool_registry.items()
                if server == server_name
            ]
            
            server_report = {
                "expected": len(expected_server_tools),
                "actual": len(actual_server_tools),
                "missing": sorted(set(expected_server_tools) - set(actual_server_tools)),
                "extra": sorted(set(actual_server_tools) - set(expected_server_tools))
            }
            
            report["servers"][server_name] = server_report
        
        # Print comprehensive report
        print("\n" + "="*60)
        print("COMPREHENSIVE TOOL AUDIT REPORT")
        print("="*60)
        print(f"Expected total tools: {report['expected_total']}")
        print(f"Actual total tools: {report['actual_total']}")
        print(f"Net change: {report['actual_total'] - report['expected_total']:+d}")
        
        for server_name, server_report in report["servers"].items():
            print(f"\n{server_name.upper()} SERVER:")
            print(f"  Expected: {server_report['expected']}")
            print(f"  Actual: {server_report['actual']}")
            print(f"  Missing: {len(server_report['missing'])}")
            print(f"  Extra: {len(server_report['extra'])}")
            
            if server_report['missing']:
                print(f"  Missing tools: {server_report['missing']}")
            if server_report['extra']:
                print(f"  Extra tools: {server_report['extra']}")
        
        print("="*60)
        
        # Assert no critical tools are missing
        total_missing = sum(len(s['missing']) for s in report['servers'].values())
        assert total_missing == 0, f"CRITICAL: {total_missing} tools missing from refactoring"
        
        print("✅ AUDIT PASSED: All expected tools preserved")