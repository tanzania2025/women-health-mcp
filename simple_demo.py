#!/usr/bin/env python3
"""
Simple MCP Demo - Just Client-Server Communication
Shows the raw MCP protocol working without AI
"""

import asyncio
from mcp_client import MCPClient
import json

async def simple_demo():
    """Simple demonstration of MCP client-server communication"""
    print("🔧 Simple MCP Client-Server Demo")
    print("=" * 40)
    
    print("🔗 Starting PubMed server...")
    
    try:
        # Connect to PubMed server
        client = MCPClient(command="python", args=["servers/pubmed_server.py"])
        await client.connect()
        print("✅ Connected to PubMed server!")
        
        # List available tools
        print("\n📋 Listing available tools...")
        tools = await client.list_tools()
        
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool.name}")
            print(f"    Description: {tool.description}")
            print(f"    Schema: {json.dumps(tool.inputSchema, indent=4)}")
            print()
        
        # Call a tool directly
        print("🛠  Calling search_pubmed_articles tool...")
        result = await client.call_tool("search_pubmed_articles", {
            "query": "PCOS polycystic ovary syndrome treatment",
            "max_results": 3
        })
        
        print("📄 Raw MCP Response:")
        print(f"  Is Error: {result.isError if hasattr(result, 'isError') else 'N/A'}")
        print(f"  Content blocks: {len(result.content) if result.content else 0}")
        
        if result.content:
            for i, content in enumerate(result.content):
                print(f"\n  Content Block {i+1}:")
                if hasattr(content, 'text'):
                    text = content.text
                    print(f"    Type: text")
                    print(f"    Length: {len(text)} characters")
                    print(f"    Preview: {text[:200]}...")
                else:
                    print(f"    Type: {type(content)}")
                    print(f"    Content: {content}")
        
        # Test another tool
        print("\n🛠  Trying to get a specific article (this might fail, but shows the process)...")
        try:
            result2 = await client.call_tool("get_article", {
                "pmid": "38123456"  # Random PMID that might not exist
            })
            
            if result2.content and result2.content[0].text:
                print("✅ Article retrieved successfully!")
                print(f"📄 Preview: {result2.content[0].text[:300]}...")
            else:
                print("⚠️  No content returned (expected for invalid PMID)")
                
        except Exception as e:
            print(f"❌ Article retrieval failed (expected): {e}")
        
        # Clean up
        print("\n🧹 Cleaning up connection...")
        await client.cleanup()
        print("✅ Connection closed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

async def multi_server_demo():
    """Demonstrate connecting to multiple servers"""
    print("\n\n🔧 Multi-Server Demo")
    print("=" * 40)
    
    servers = [
        ("PubMed", "servers/pubmed_server.py"),
        ("Menopause", "servers/menopause_server.py"),
        ("ELSA", "servers/elsa_server.py")
    ]
    
    for server_name, server_script in servers:
        print(f"\n🔗 Testing {server_name} server...")
        
        try:
            client = MCPClient(command="python", args=[server_script])
            await client.connect()
            
            tools = await client.list_tools()
            print(f"  ✅ Connected! Found {len(tools)} tools:")
            for tool in tools:
                print(f"    • {tool.name}")
            
            await client.cleanup()
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting MCP Demo Suite\n")
    
    try:
        # Run simple demo
        asyncio.run(simple_demo())
        
        # Run multi-server demo
        asyncio.run(multi_server_demo())
        
        print("\n🎉 All demos complete!")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo suite failed: {e}")