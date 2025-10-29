import sys
import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

import json
from pydantic import AnyUrl


class MCPClient:
    """MCP Client for connecting to stdio-based MCP servers."""

    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        """Connect to the MCP server via stdio."""
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write)
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        """Get the client session, raising error if not connected."""
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized. Call connect first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        """List all available tools from the MCP server."""
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Call a specific tool with the given input."""
        return await self.session().call_tool(tool_name, tool_input)

    async def list_prompts(self) -> list[types.Prompt]:
        """List all available prompts from the MCP server."""
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, args: dict[str, str]):
        """Get a specific prompt with the given arguments."""
        result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text

    async def cleanup(self):
        """Clean up the client connection and resources."""
        try:
            await self._exit_stack.aclose()
        except asyncio.CancelledError:
            # Suppress cancellation during cleanup - this is expected when Streamlit reruns
            pass
        except Exception as e:
            # Log other exceptions but don't raise them
            print(f"Warning during cleanup: {e}")
        finally:
            self._session = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# For testing
async def main():
    """Test the MCP client with the women's health server."""
    async with MCPClient(
        command="python",
        args=["mcp_server.py"],
    ) as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Test a simple tool call
        if tools:
            result = await client.call_tool(
                "predict_ivf_success",
                {"age": 35, "amh": 2.5}
            )
            print(f"Tool result: {result}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
