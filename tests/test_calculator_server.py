"""
Test calculator server tools (SART IVF calculations)
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

class TestCalculatorServer:
    
    @pytest_asyncio.fixture
    async def calculator_session(self):
        """Create a session connected to the calculator server."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "calculator_server.py"
        
        server_params = StdioServerParameters(
            command="fastmcp",
            args=["run", str(server_path), "--transport", "stdio", "--no-banner"]
        )
        
        async with stdio_client(server_params) as (stdio, write):
            session = ClientSession(stdio, write)
            await session.initialize()
            yield session
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, calculator_session):
        """Test that calculator server initializes successfully."""
        tools = await calculator_session.list_tools()
        assert len(tools.tools) > 0, "Calculator server should have registered tools"
    
    @pytest.mark.asyncio
    async def test_calculate_ivf_success(self, calculator_session):
        """Test calculate_ivf_success tool with valid parameters."""
        result = await calculator_session.call_tool("calculate_ivf_success", {
            "age": 32,
            "height_cm": 165,
            "weight_kg": 65,
            "previous_full_term": False,
            "male_factor": False,
            "polycystic": False,
            "uterine_problems": False,
            "unexplained_infertility": False,
            "low_ovarian_reserve": False,
            "amh_available": True,
            "amh_value": 2.5
        })
        
        assert result.isError == False, f"calculate_ivf_success should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        
        # Should contain success rate information
        assert "success" in content_str.lower(), "Should contain success rate information"
        
        # Try to parse as JSON to check structure
        try:
            # Extract JSON from the content
            json_start = content_str.find('{')
            if json_start >= 0:
                json_content = content_str[json_start:]
                parsed = json.loads(json_content)
                
                # Check for expected fields
                assert "success_rate_1_cycle" in parsed or "age" in parsed, "Should contain calculation results"
        except json.JSONDecodeError:
            # If not JSON, should still contain meaningful text
            assert len(content_str) > 50, "Should return substantial content about IVF success rates"
    
    @pytest.mark.asyncio
    async def test_predict_ivf_success(self, calculator_session):
        """Test predict_ivf_success tool."""
        result = await calculator_session.call_tool("predict_ivf_success", {
            "age": 30,
            "amh": 3.0,
            "height_cm": 170,
            "weight_kg": 60,
            "prior_pregnancies": 0,
            "male_factor": False,
            "polycystic": False
        })
        
        assert result.isError == False, f"predict_ivf_success should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "predict" in content_str.lower() or "success" in content_str.lower(), "Should contain prediction information"
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, calculator_session):
        """Test generate_recommendations tool."""
        # First get a calculation result
        calc_result = {
            "age": 28,
            "success_rate_1_cycle": 50.0,
            "amh_available": True,
            "amh_value": 3.2,
            "polycystic": False,
            "low_ovarian_reserve": False
        }
        
        result = await calculator_session.call_tool("generate_recommendations", {
            "calculation_result": calc_result
        })
        
        assert result.isError == False, f"generate_recommendations should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "recommendation" in content_str.lower(), "Should contain recommendations"
    
    @pytest.mark.asyncio
    async def test_get_sart_calculator_info(self, calculator_session):
        """Test get_sart_calculator_info tool."""
        result = await calculator_session.call_tool("get_sart_calculator_info", {})
        
        assert result.isError == False, f"get_sart_calculator_info should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "SART" in content_str, "Should contain SART information"
        assert "calculator" in content_str.lower(), "Should mention calculator"
    
    @pytest.mark.asyncio
    async def test_compare_success_rates(self, calculator_session):
        """Test compare_success_rates tool."""
        scenarios = [
            {
                "age": 28,
                "height_cm": 165,
                "weight_kg": 60,
                "amh_available": True,
                "amh_value": 3.0
            },
            {
                "age": 35,
                "height_cm": 170,
                "weight_kg": 65,
                "amh_available": True,
                "amh_value": 2.0
            }
        ]
        
        result = await calculator_session.call_tool("compare_success_rates", {
            "scenarios": scenarios
        })
        
        assert result.isError == False, f"compare_success_rates should not error: {result.content}"
        assert isinstance(result.content, list), "Result should be a list"
        
        content_str = str(result.content[0].text) if result.content else ""
        assert "compare" in content_str.lower() or "scenario" in content_str.lower(), "Should contain comparison information"
    
    @pytest.mark.asyncio
    async def test_input_validation(self, calculator_session):
        """Test input validation for invalid parameters."""
        # Test with invalid age (too young)
        result = await calculator_session.call_tool("calculate_ivf_success", {
            "age": 15,  # Invalid age
            "height_cm": 165,
            "weight_kg": 65
        })
        
        # Should handle invalid input gracefully
        if result.isError:
            # Error is expected for invalid input
            pass
        else:
            # If not error, should contain error message in content
            content_str = str(result.content[0].text) if result.content else ""
            assert "error" in content_str.lower() or "age" in content_str.lower(), "Should indicate age validation issue"
    
    @pytest.mark.asyncio
    async def test_all_calculator_tools_registered(self, calculator_session):
        """Test that all expected calculator tools are registered."""
        tools = await calculator_session.list_tools()
        tool_names = [tool.name for tool in tools.tools]
        
        expected_calculator_tools = [
            "calculate_ivf_success", "predict_ivf_success", "generate_recommendations",
            "get_sart_calculator_info", "compare_success_rates"
        ]
        
        missing_tools = [tool for tool in expected_calculator_tools if tool not in tool_names]
        extra_tools = [tool for tool in tool_names if tool not in expected_calculator_tools]
        
        print(f"✅ Calculator server registered {len(tool_names)} tools: {tool_names}")
        if missing_tools:
            print(f"❌ Missing calculator tools: {missing_tools}")
        if extra_tools:
            print(f"ℹ️  Extra calculator tools: {extra_tools}")
        
        assert len(missing_tools) == 0, f"Missing calculator tools: {missing_tools}"
    
    @pytest.mark.asyncio
    async def test_calculation_accuracy(self, calculator_session):
        """Test that calculations return reasonable values."""
        result = await calculator_session.call_tool("calculate_ivf_success", {
            "age": 30,
            "height_cm": 165,
            "weight_kg": 65,
            "amh_available": True,
            "amh_value": 2.8
        })
        
        assert result.isError == False, "Calculation should not error"
        content_str = str(result.content[0].text) if result.content else ""
        
        # Success rates should be reasonable percentages (0-100)
        # This is a basic sanity check
        if "%" in content_str:
            # Extract percentage values and check they're reasonable
            import re
            percentages = re.findall(r'(\d+\.?\d*)%', content_str)
            for pct in percentages:
                pct_val = float(pct)
                assert 0 <= pct_val <= 100, f"Success rate {pct_val}% should be between 0-100%"
    
    def test_server_can_start_independently(self):
        """Test that the server can start as a standalone process."""
        server_path = Path(__file__).parent.parent / "mcp_servers" / "calculator_server.py"
        
        # Test that fastmcp can inspect the server
        result = subprocess.run([
            "fastmcp", "inspect", str(server_path)
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0, f"Server inspection failed: {result.stderr}"
        assert "Tools:" in result.stdout, "Server should have tools"
        assert "women-health-calculator" in result.stdout, "Server should have correct name"