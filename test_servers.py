#!/usr/bin/env python3
"""
Test Individual MCP Servers
Shows each server working independently
"""

import asyncio
from mcp_client import MCPClient
import json

async def test_server(server_script: str, server_name: str, test_calls: list):
    """Test a single MCP server"""
    print(f"\n{'='*20} {server_name.upper()} SERVER {'='*20}")
    
    try:
        # Connect to server
        print(f"🔗 Connecting to {server_script}...")
        client = MCPClient(command="python", args=[server_script])
        await client.connect()
        print("✅ Connected!")
        
        # List available tools
        tools = await client.list_tools()
        print(f"\n📋 Available tools ({len(tools)}):")
        for tool in tools:
            print(f"  • {tool.name}: {tool.description}")
        
        # Test tool calls
        for tool_name, args in test_calls:
            print(f"\n🛠  Testing {tool_name}...")
            print(f"   📄 Args: {json.dumps(args, indent=2)}")
            
            try:
                result = await client.call_tool(tool_name, args)
                
                if result.content:
                    output = ""
                    for content in result.content:
                        if hasattr(content, 'text'):
                            output += content.text
                    
                    print(f"   ✅ Success! Response length: {len(output)} chars")
                    print(f"   📄 Preview: {output[:200]}...")
                else:
                    print("   ⚠️  No content returned")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Cleanup
        await client.cleanup()
        print(f"✅ {server_name} server test complete!")
        
    except Exception as e:
        print(f"❌ Failed to test {server_name} server: {e}")

async def main():
    """Test all servers individually"""
    print("🧪 TESTING INDIVIDUAL MCP SERVERS")
    print("=" * 60)
    
    # Define server tests
    server_tests = [
        {
            "script": "servers/pubmed_server.py",
            "name": "PubMed",
            "tests": [
                ("search_pubmed_articles", {"query": "PCOS", "max_results": 2}),
                ("get_article", {"pmid": "12345678"})  # This might fail but shows the process
            ]
        },
        {
            "script": "servers/sart_ivf_server.py", 
            "name": "SART IVF",
            "tests": [
                ("calculate_ivf_success_rates", {
                    "age": 32,
                    "height_cm": 165,
                    "weight_kg": 60,
                    "amh_available": True,
                    "amh_value": 2.5
                })
            ]
        },
        {
            "script": "servers/menopause_server.py",
            "name": "Menopause", 
            "tests": [
                ("calculate_menopause_age_estimate", {
                    "current_age": 45,
                    "mothers_menopause_age": 52,
                    "smoking_status": "never"
                })
            ]
        },
        {
            "script": "servers/elsa_server.py",
            "name": "ELSA",
            "tests": [
                ("list_elsa_waves", {"include_details": False}),
                ("search_data_modules", {"query": "cognitive"})
            ]
        },
        {
            "script": "servers/eshre_server.py",
            "name": "ESHRE", 
            "tests": [
                ("search_eshre_guidelines", {"query": "endometriosis"})
            ]
        },
        {
            "script": "servers/nams_server.py",
            "name": "NAMS",
            "tests": [
                ("search_nams_protocols", {"query": "hormone therapy"})
            ]
        },
        {
            "script": "servers/asrm_server.py",
            "name": "ASRM",
            "tests": [
                ("search_asrm_guidelines", {"query": "IVF"})
            ]
        }
    ]
    
    # Test each server
    for server_test in server_tests:
        await test_server(
            server_test["script"],
            server_test["name"], 
            server_test["tests"]
        )
    
    print(f"\n{'='*60}")
    print("🎉 ALL SERVER TESTS COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()