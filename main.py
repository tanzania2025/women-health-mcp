#!/usr/bin/env python3
"""
DoctHER: AI-Powered Women's Health Assistant
Main entry point for the CLI application using FastMCP architecture
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

from mcp_client import MCPClient
from core.claude import Claude
from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Anthropic Config
claude_model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

assert anthropic_api_key, (
    "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


async def main():
    """Main entry point for DoctHER CLI application."""
    claude_service = Claude(model=claude_model)

    # Define the individual MCP servers to connect to
    server_scripts = [
        "mcp_server.py",  # Core tools (IVF calculator, etc.)
        "servers/pubmed_server.py",
        "servers/eshre_server.py", 
        "servers/nams_server.py",
        "servers/elsa_server.py",
        "servers/asrm_server.py",
        "servers/sart_ivf_server.py"
    ]
    
    # Add any additional server scripts from command line
    if len(sys.argv) > 1:
        server_scripts.extend(sys.argv[1:])

    clients = {}

    async with AsyncExitStack() as stack:
        # Connect to each individual MCP server
        primary_client = None
        
        for server_script in server_scripts:
            server_name = server_script.split('/')[-1].replace('.py', '').replace('_server', '')
            client_id = f"{server_name}_client"
            
            try:
                client = await stack.enter_async_context(
                    MCPClient(command="python", args=[server_script])
                )
                clients[client_id] = client
                
                # Use the first successfully connected client as primary
                if primary_client is None:
                    primary_client = client
                    
                print(f"✅ Connected to {server_name} server")
                
            except Exception as e:
                print(f"⚠️  Failed to connect to {server_name} server: {e}")

        if not primary_client:
            print("❌ Could not connect to any MCP servers")
            return

        chat = CliChat(
            doc_client=primary_client,  # Use first available client as primary
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()
        await cli.run()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())