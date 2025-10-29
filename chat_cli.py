#!/usr/bin/env python3
"""
Interactive CLI Chat - Women's Health Assistant
Chat with DoctHER through command line
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

class DoctHERCLI:
    def __init__(self):
        self.clients = {}
        self.tool_client_map = {}
        self.anthropic_tools = []
        self.anthropic = None
        self.connected = False
        
    async def setup(self):
        """Initialize all MCP servers and Claude"""
        print("🔬 DoctHER - Women's Health AI Assistant")
        print("=" * 50)
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ Please set your ANTHROPIC_API_KEY in environment variables")
            return False
            
        # Connect to servers
        server_scripts = [
            "servers/pubmed_server.py",
            "servers/eshre_server.py", 
            "servers/nams_server.py",
            "servers/elsa_server.py",
            "servers/asrm_server.py",
            "servers/sart_ivf_server.py",
            "servers/menopause_server.py"
        ]
        
        print(f"📡 Connecting to {len(server_scripts)} medical data servers...")
        
        all_tools = []
        connected_count = 0
        
        for server_script in server_scripts:
            server_name = Path(server_script).stem.replace('_server', '')
            
            try:
                client = MCPClient(command="python", args=[server_script])
                await client.connect()
                self.clients[server_name] = client
                
                # Get tools from this client
                client_tools = await client.list_tools()
                all_tools.extend(client_tools)
                
                # Map tools to their client
                for tool in client_tools:
                    self.tool_client_map[tool.name] = client
                    
                connected_count += 1
                
            except Exception:
                continue
        
        if connected_count == 0:
            print("❌ Could not connect to any servers")
            return False
            
        print(f"✅ Connected to {connected_count} servers with {len(all_tools)} tools")
        
        # Setup Claude
        self.anthropic = Anthropic(api_key=api_key)
        
        # Convert tools for Claude
        for tool in all_tools:
            try:
                self.anthropic_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
            except Exception:
                continue
                
        print(f"🤖 Claude AI ready with {len(self.anthropic_tools)} medical research tools")
        print("\n💡 Available capabilities:")
        print("  • Search PubMed for latest research")
        print("  • Access ESHRE, NAMS, ASRM clinical guidelines")
        print("  • Calculate IVF success rates")
        print("  • Estimate menopause timing")
        print("  • Access ELSA longitudinal health data")
        
        self.connected = True
        return True
        
    async def chat(self, user_input: str) -> str:
        """Process a chat message"""
        if not self.connected:
            return "❌ System not properly initialized"
            
        try:
            # Send to Claude with tools
            messages = [{
                "role": "user",
                "content": f"{user_input}\n\nPlease use the available medical research tools when relevant to provide evidence-based insights."
            }]
            
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=messages,
                tools=self.anthropic_tools,
                temperature=0.1,
            )
            
            # Process tool calls
            result_parts = []
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    result_parts.append(content_block.text)
                elif content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_args = content_block.input
                    tool_id = content_block.id
                    
                    print(f"🛠  Using {tool_name}...")
                    
                    try:
                        client_for_tool = self.tool_client_map.get(tool_name)
                        if client_for_tool:
                            mcp_result = await client_for_tool.call_tool(tool_name, tool_args)
                            
                            tool_output = ""
                            if mcp_result.content:
                                for content in mcp_result.content:
                                    if hasattr(content, 'text'):
                                        tool_output += content.text
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": tool_output
                            })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": "Tool not available"
                            })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Tool execution failed: {str(e)}"
                        })
            
            # Get final response
            final_text = "\n".join(result_parts)
            
            if tool_results:
                follow_up_messages = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results}
                ]
                
                final_response = self.anthropic.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=4000,
                    messages=follow_up_messages,
                    temperature=0.1,
                )
                
                final_text = ""
                for content_block in final_response.content:
                    if content_block.type == "text":
                        final_text += content_block.text
            
            return final_text
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    async def cleanup(self):
        """Clean up connections"""
        for client in self.clients.values():
            try:
                await client.cleanup()
            except:
                pass

async def main():
    """Main interactive loop"""
    docther = DoctHERCLI()
    
    if not await docther.setup():
        return
    
    print("\n" + "="*50)
    print("💬 CHAT MODE - Type your questions below")
    print("💡 Example questions:")
    print("  • What are the latest PCOS treatments?")
    print("  • Calculate IVF success for a 35-year-old")  
    print("  • When might I expect menopause?")
    print("  • Show me ESHRE guidelines on endometriosis")
    print("  • What does research say about hormone therapy?")
    print("\n🚪 Type 'quit', 'exit' or press Ctrl+C to end")
    print("="*50)
    
    try:
        while True:
            print("\n" + "-"*30)
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            print("\n🤖 DoctHER: Thinking...")
            response = await docther.chat(user_input)
            
            print(f"\n🤖 DoctHER:\n{response}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Chat error: {e}")
    finally:
        print("\n🧹 Cleaning up...")
        await docther.cleanup()
        print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())