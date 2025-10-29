#!/usr/bin/env python3
"""
Single Query Test - Exact App.py Behavior
Tests one query to show complete app.py workflow
"""

import asyncio
import os
import sys
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
import json

# Load environment
load_dotenv()

# Import MCP client
from mcp_client import MCPClient

async def query_with_mcp_standalone(user_input: str) -> str:
    """
    EXACT replica of the query_with_mcp_standalone function from app.py
    """
    try:
        print(f"📝 Processing query: '{user_input}'")
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "Please set your ANTHROPIC_API_KEY in the environment variables."

        # List of server scripts (same as app.py)
        server_scripts = [
            "servers/pubmed_server.py",
            "servers/eshre_server.py", 
            "servers/nams_server.py",
            "servers/elsa_server.py",
            "servers/asrm_server.py",
            "servers/sart_ivf_server.py",
            "servers/menopause_server.py"
        ]

        print(f"🔗 Connecting to {len(server_scripts)} MCP servers...")

        # Connect to all servers and collect tools
        clients = {}
        tool_client_map = {}
        all_tools = []
        connected_count = 0

        for server_script in server_scripts:
            server_name = Path(server_script).stem.replace('_server', '')
            
            try:
                # Create and connect client
                client = MCPClient(command="python", args=[server_script])
                await client.connect()
                clients[server_name] = client
                
                # Get tools from this client
                client_tools = await client.list_tools()
                all_tools.extend(client_tools)
                
                # Map tools to their client
                for tool in client_tools:
                    tool_client_map[tool.name] = client
                    
                connected_count += 1
                print(f"  ✅ {server_name}: {len(client_tools)} tools")
                    
            except Exception as e:
                print(f"  ❌ {server_name}: failed ({str(e)[:50]}...)")
                continue

        if not clients:
            return "Could not connect to any MCP servers."

        print(f"\n📊 Total: {connected_count} servers, {len(all_tools)} tools")

        # Create Anthropic client
        anthropic = Anthropic(api_key=api_key)

        # Prepare messages (same as app.py)
        messages = [{
            "role": "user",
            "content": f"{user_input}\n\nPlease use the available medical research tools to provide evidence-based insights when relevant."
        }]

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

        print(f"\n🤖 Sending to Claude with {len(anthropic_tools)} tools available...")

        # Call Claude with or without tools (same logic as app.py)
        if anthropic_tools:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=messages,
                tools=anthropic_tools,
                temperature=0.1,
            )
        else:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=messages,
                temperature=0.1,
            )

        print("✅ Claude response received!")

        # Process response and handle tool calls (same as app.py)
        result_parts = []
        tool_results = []

        for content_block in response.content:
            if content_block.type == "text":
                result_parts.append(content_block.text)
                print(f"💬 Claude provided text response")
            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_args = content_block.input
                tool_id = content_block.id

                print(f"\n🛠  Claude wants to use tool: {tool_name}")
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
                        print(f"   ❌ Tool not available")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": "Tool not available"
                        })

                except Exception as e:
                    print(f"   ❌ Tool execution failed: {str(e)}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": f"Tool execution failed: {str(e)}"
                    })

        # Get final response if tools were used (same as app.py)
        final_text = "\n".join(result_parts)
        if tool_results:
            try:
                print(f"\n🔄 Sending tool results back to Claude for synthesis...")
                
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

                print("✅ Final synthesis complete!")

                final_text = ""
                for content_block in final_response.content:
                    if content_block.type == "text":
                        final_text += content_block.text
                        
            except Exception as e:
                print(f"⚠️  Synthesis failed, returning initial response: {str(e)}")

        # Cleanup connections
        print(f"\n🧹 Cleaning up {len(clients)} connections...")
        for client in clients.values():
            try:
                await client.cleanup()
            except:
                pass

        return final_text

    except Exception as e:
        return f"Error: {str(e)}"

async def main():
    """Single query test"""
    print("🔬 Single Query Test - Exact App.py Behavior")
    print("=" * 60)
    
    # Test with a typical medical query
    query = sys.argv[1] if len(sys.argv) > 1 else "What are current PCOS treatment options? Search recent research."
    
    print(f"Query: {query}")
    print("=" * 60)
    
    response = await query_with_mcp_standalone(query)
    
    print("\n" + "=" * 60)
    print("📄 FINAL DOCTHER RESPONSE:")
    print("=" * 60)
    print(response)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()