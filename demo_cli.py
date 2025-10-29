#!/usr/bin/env python3
"""
Demo CLI - Women's Health MCP Architecture
Shows the complete process working without Streamlit interface
"""

import asyncio
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Import MCP client
from mcp_client import MCPClient

async def demo_mcp_workflow():
    """Demonstrate the complete MCP workflow"""
    print("🔬 DoctHER CLI Demo - Women's Health MCP Architecture")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set your ANTHROPIC_API_KEY in environment variables")
        return
    
    print("✅ Anthropic API key found")
    
    # Define servers to connect to
    server_scripts = [
        "servers/pubmed_server.py",
        "servers/eshre_server.py", 
        "servers/nams_server.py",
        "servers/elsa_server.py",
        "servers/asrm_server.py",
        "servers/sart_ivf_server.py",
        "servers/menopause_server.py"
    ]
    
    print(f"\n📡 Connecting to {len(server_scripts)} MCP servers...")
    
    # Connect to all servers
    clients = {}
    all_tools = []
    tool_client_map = {}
    
    for server_script in server_scripts:
        server_name = Path(server_script).stem.replace('_server', '')
        
        try:
            print(f"  🔗 Connecting to {server_name}...")
            client = MCPClient(command="python", args=[server_script])
            await client.connect()
            clients[server_name] = client
            
            # Get tools from this client
            client_tools = await client.list_tools()
            all_tools.extend(client_tools)
            
            # Map tools to their client
            for tool in client_tools:
                tool_client_map[tool.name] = client
                
            print(f"    ✅ Connected! Found {len(client_tools)} tools")
            
        except Exception as e:
            print(f"    ❌ Failed to connect to {server_name}: {e}")
            continue
    
    print(f"\n🛠  Total tools available: {len(all_tools)}")
    print("\n📋 Available Tools:")
    for tool in all_tools:
        print(f"  • {tool.name}: {tool.description[:80]}...")
    
    # Create Anthropic client
    print("\n🤖 Initializing Claude AI...")
    anthropic = Anthropic(api_key=api_key)
    
    # Convert MCP tools to Anthropic format
    anthropic_tools = []
    for tool in all_tools:
        try:
            anthropic_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })
        except Exception:
            continue
    
    print(f"✅ Claude initialized with {len(anthropic_tools)} tools")
    
    # Demo query
    user_query = "What are the latest treatments for PCOS? Please search recent research."
    print(f"\n❓ Demo Query: '{user_query}'")
    print("\n🔍 Sending to Claude with MCP tools...")
    
    # Send query to Claude
    messages = [{
        "role": "user",
        "content": f"{user_query}\n\nPlease use the available medical research tools to provide evidence-based insights."
    }]
    
    response = anthropic.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        messages=messages,
        tools=anthropic_tools,
        temperature=0.1,
    )
    
    print("📨 Claude's response received!")
    
    # Process response and handle tool calls
    result_parts = []
    tool_results = []
    
    print("\n🔧 Processing Claude's response...")
    
    for content_block in response.content:
        if content_block.type == "text":
            result_parts.append(content_block.text)
            print("💬 Claude provided text response")
            
        elif content_block.type == "tool_use":
            tool_name = content_block.name
            tool_args = content_block.input
            tool_id = content_block.id
            
            print(f"🛠  Claude wants to use tool: {tool_name}")
            print(f"   📄 Arguments: {json.dumps(tool_args, indent=2)}")
            
            try:
                # Find the correct client for this tool
                client_for_tool = tool_client_map.get(tool_name)
                if client_for_tool:
                    print(f"   ⚡ Executing {tool_name}...")
                    mcp_result = await client_for_tool.call_tool(tool_name, tool_args)
                    
                    tool_output = ""
                    if mcp_result.content:
                        for content in mcp_result.content:
                            if hasattr(content, 'text'):
                                tool_output += content.text
                    
                    print(f"   ✅ Tool executed! Response length: {len(tool_output)} chars")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": tool_output
                    })
                else:
                    print(f"   ❌ Tool {tool_name} not found")
                    tool_results.append({
                        "type": "tool_result", 
                        "tool_use_id": tool_id,
                        "content": "Tool not available"
                    })
                    
            except Exception as e:
                print(f"   ❌ Tool execution failed: {e}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"Tool execution failed: {str(e)}"
                })
    
    # Get final response if tools were used
    final_text = "\n".join(result_parts)
    
    if tool_results:
        print("\n🔄 Sending tool results back to Claude for synthesis...")
        
        follow_up_messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]
        
        final_response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            messages=follow_up_messages,
            temperature=0.1,
        )
        
        final_text = ""
        for content_block in final_response.content:
            if content_block.type == "text":
                final_text += content_block.text
        
        print("✅ Final synthesis complete!")
    
    # Display results
    print("\n" + "="*60)
    print("📄 FINAL RESPONSE:")
    print("="*60)
    print(final_text)
    print("="*60)
    
    # Cleanup
    print("\n🧹 Cleaning up connections...")
    for client in clients.values():
        try:
            await client.cleanup()
        except:
            pass
    
    print("✅ Demo complete!")

async def demo_individual_tool():
    """Demonstrate using a single tool directly"""
    print("\n🔧 BONUS: Direct Tool Demo")
    print("-" * 40)
    
    print("🔗 Connecting to PubMed server only...")
    
    try:
        client = MCPClient(command="python", args=["servers/pubmed_server.py"])
        await client.connect()
        
        # List tools
        tools = await client.list_tools()
        print(f"📋 Available tools: {[t.name for t in tools]}")
        
        # Call search tool directly
        print("\n🔍 Searching PubMed for 'PCOS treatment'...")
        result = await client.call_tool("search_pubmed_articles", {
            "query": "PCOS treatment",
            "max_results": 3
        })
        
        if result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    print("📄 Results:")
                    print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
        
        await client.cleanup()
        print("✅ Direct tool demo complete!")
        
    except Exception as e:
        print(f"❌ Direct tool demo failed: {e}")

if __name__ == "__main__":
    print("Starting Women's Health MCP CLI Demo...\n")
    
    try:
        # Run main demo
        asyncio.run(demo_mcp_workflow())
        
        # Run bonus demo
        asyncio.run(demo_individual_tool())
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()