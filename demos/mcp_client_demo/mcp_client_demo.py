#!/usr/bin/env python3
"""
MCP Client Demo - Demonstrates how AI agents interact with Women's Health MCP Server
"""

import asyncio
import json
import httpx
from typing import Dict, Any, Optional


class WomensHealthMCPClient:
    """
    Client for interacting with Women's Health MCP Server.
    Demonstrates how AI agents can leverage the MCP protocol.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "demo-api-key-change-in-production"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def initialize_connection(self) -> Dict[str, Any]:
        """Initialize MCP connection."""
        request = {
            "jsonrpc": "2.0",
            "id": "init_1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "women-health-ai-agent",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "resources": {"subscribe": True},
                    "tools": {"subscribe": True},
                    "prompts": {"subscribe": True}
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp",
                json=request,
                headers=self.headers
            )
            return response.json()
    
    async def list_available_resources(self) -> Dict[str, Any]:
        """List all available MCP resources."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/mcp/resources",
                headers=self.headers
            )
            return response.json()
    
    async def list_available_tools(self) -> Dict[str, Any]:
        """List all available MCP tools."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/mcp/tools",
                headers=self.headers
            )
            return response.json()
    
    async def assess_ovarian_reserve(self, age: int, amh: float, fsh: Optional[float] = None) -> Dict[str, Any]:
        """Call ovarian reserve assessment tool."""
        arguments = {"age": age, "amh": amh}
        if fsh:
            arguments["fsh"] = fsh
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/assess-ovarian-reserve",
                json=arguments,
                headers=self.headers
            )
            return response.json()
    
    async def predict_ivf_success(self, age: int, amh: float, cycle_type: str = "fresh") -> Dict[str, Any]:
        """Call IVF success prediction tool."""
        arguments = {
            "age": age,
            "amh": amh,
            "cycle_type": cycle_type
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/predict-ivf-success",
                json=arguments,
                headers=self.headers
            )
            return response.json()
    
    async def get_fertility_consultation_prompt(self, patient_age: int, amh_level: float, clinical_question: str) -> Dict[str, Any]:
        """Get fertility consultation prompt template."""
        arguments = {
            "patient_age": patient_age,
            "amh_level": amh_level,
            "clinical_question": clinical_question
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/prompts/fertility-consultation",
                json=arguments,
                headers=self.headers
            )
            return response.json()
    
    async def read_patient_data(self, patient_id: str = "demo_patient") -> Dict[str, Any]:
        """Read patient data resource."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/mcp/resources/patient-data",
                headers=self.headers
            )
            return response.json()


async def run_comprehensive_demo():
    """Run comprehensive MCP client demonstration."""
    
    print("🚀 Women's Health MCP Client Demo")
    print("="*50)
    
    client = WomensHealthMCPClient()
    
    try:
        # Step 1: Initialize connection
        print("\n1. Initializing MCP connection...")
        init_response = await client.initialize_connection()
        print(f"✓ Connected to: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Step 2: Discover available resources
        print("\n2. Discovering available resources...")
        resources = await client.list_available_resources()
        print("Available resources:")
        for resource in resources.get("resources", []):
            print(f"  • {resource['name']}: {resource['description']}")
        
        # Step 3: Discover available tools
        print("\n3. Discovering available tools...")
        tools = await client.list_available_tools()
        print("Available tools:")
        for tool in tools.get("tools", []):
            print(f"  • {tool['name']}: {tool['description']}")
        
        # Step 4: Demonstrate clinical assessment
        print("\n4. Performing clinical assessment...")
        print("Patient: 38-year-old woman, AMH 0.8 ng/mL, FSH 12.5 mIU/mL")
        
        # Assess ovarian reserve
        ovarian_result = await client.assess_ovarian_reserve(age=38, amh=0.8, fsh=12.5)
        if "content" in ovarian_result:
            assessment = json.loads(ovarian_result["content"][0]["text"])
            print(f"✓ Ovarian reserve: {assessment['result']['category']} ({assessment['result']['percentile']}th percentile)")
        
        # Predict IVF success
        ivf_result = await client.predict_ivf_success(age=38, amh=0.8, cycle_type="fresh")
        if "content" in ivf_result:
            prediction = json.loads(ivf_result["content"][0]["text"])
            print(f"✓ IVF success rate: {prediction['result']['live_birth_rate']}%")
        
        # Step 5: Generate clinical consultation prompt
        print("\n5. Generating AI consultation prompt...")
        prompt_result = await client.get_fertility_consultation_prompt(
            patient_age=38,
            amh_level=0.8,
            clinical_question="Should I start IVF now or try naturally for a few more months?"
        )
        
        if "messages" in prompt_result:
            prompt_text = prompt_result["messages"][0]["content"]["text"]
            print("✓ Generated comprehensive consultation prompt:")
            print("  " + prompt_text.replace("\n", "\n  ")[:300] + "...")
        
        # Step 6: Access patient data
        print("\n6. Accessing patient data resource...")
        patient_data = await client.read_patient_data()
        if "contents" in patient_data:
            data = json.loads(patient_data["contents"][0]["text"])
            print(f"✓ Retrieved data for patient: {data.get('patient_id', 'Unknown')}")
            print(f"  Age: {data.get('demographics', {}).get('age', 'Unknown')}")
            print(f"  AMH: {data.get('labs', {}).get('amh', 'Unknown')} ng/mL")
        
        print("\n✅ MCP Client Demo completed successfully!")
        print("\nThis demonstrates how AI agents can:")
        print("• Connect to MCP servers using standard protocols")
        print("• Discover and access reproductive health resources")
        print("• Execute clinical calculation tools")
        print("• Generate evidence-based consultation prompts")
        print("• Access standardized patient data")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("Make sure the MCP server is running: python -m mcp_server.server")


async def run_simple_demo():
    """Run simple demo for quick testing."""
    
    print("🔬 Simple MCP Client Test")
    print("="*30)
    
    client = WomensHealthMCPClient()
    
    try:
        # Test server health
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{client.base_url}/health")
            health = response.json()
            print(f"✓ Server status: {health['status']}")
        
        # Test ovarian reserve assessment
        result = await client.assess_ovarian_reserve(age=38, amh=0.8)
        print("✓ Ovarian reserve assessment completed")
        
        print("\n✅ Simple test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        asyncio.run(run_simple_demo())
    else:
        asyncio.run(run_comprehensive_demo())