"""
CLI chat interface for DoctHER.
"""

import asyncio
from typing import Dict, Any, List
from anthropic import Anthropic

from mcp_client import MCPClient
from .claude import Claude


class CliChat:
    """CLI chat interface for interacting with DoctHER."""
    
    def __init__(self, doc_client: MCPClient, clients: Dict[str, MCPClient], claude_service: Claude):
        self.doc_client = doc_client
        self.clients = clients
        self.claude_service = claude_service
        self.conversation_history = []
    
    async def process_message(self, user_message: str) -> str:
        """Process a user message and return the response."""
        try:
            # Get available tools from all connected clients
            all_tools = []
            tool_client_map = {}  # Map tool names to their client
            
            for client_name, client in self.clients.items():
                try:
                    client_tools = await client.list_tools()
                    all_tools.extend(client_tools)
                    
                    # Map each tool to its client for later execution
                    for tool in client_tools:
                        tool_client_map[tool.name] = client
                        
                except Exception as e:
                    print(f"⚠️  Could not get tools from {client_name}: {e}")
            
            # Convert MCP tools to Anthropic format
            anthropic_tools = []
            for tool in all_tools:
                anthropic_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
            
            # Prepare messages with system prompt and conversation history
            messages = []
            
            # Add conversation history
            for msg in self.conversation_history[-6:]:  # Keep last 6 messages for context
                messages.append(msg)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": f"{user_message}\n\nPlease use the available medical research tools to provide evidence-based insights when relevant."
            })
            
            # Call Claude with tools
            response = await self.claude_service.generate_response(
                messages=messages,
                tools=anthropic_tools if anthropic_tools else None
            )
            
            # Process response and handle tool calls
            result_parts = []
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    result_parts.append(content_block.text)
                elif content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_args = content_block.input
                    tool_id = content_block.id
                    
                    print(f"🔍 Using {tool_name}...")
                    
                    # Execute tool via the appropriate MCP client
                    try:
                        # Find the correct client for this tool
                        client_for_tool = tool_client_map.get(tool_name, self.doc_client)
                        
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
                        
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result", 
                            "tool_use_id": tool_id,
                            "content": f"Tool execution failed: {str(e)}"
                        })
            
            # If we used tools, get Claude's final response
            if tool_results:
                follow_up_messages = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results}
                ]
                
                final_response = await self.claude_service.generate_response(
                    messages=follow_up_messages
                )
                
                final_text = ""
                for content_block in final_response.content:
                    if content_block.type == "text":
                        final_text += content_block.text
                
                # Update conversation history
                self.conversation_history.extend([
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": final_text}
                ])
                
                return final_text
            
            assistant_response = "\n".join(result_parts)
            
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response}
            ])
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.conversation_history.extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": error_msg}
            ])
            return error_msg
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []