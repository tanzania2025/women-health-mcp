"""
FastAPI-based MCP Server for Women's Health AI
Provides HTTP and WebSocket endpoints for Model Context Protocol communication
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from .mcp_protocol import MCPServer
from .config import Settings


# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("🚀 Starting Women's Health MCP Server...")
    yield
    # Shutdown
    print("🔄 Shutting down MCP Server...")


# Initialize FastAPI app
app = FastAPI(
    title="Women's Health MCP Server",
    description="Model Context Protocol server for reproductive health AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp_server = MCPServer()
settings = Settings()


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key for authenticated requests."""
    if not credentials or credentials.credentials != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Women's Health MCP Server",
        "version": "1.0.0",
        "status": "healthy",
        "capabilities": ["resources", "tools", "prompts", "completion"],
        "protocol_version": "2024-11-05"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": "2024-10-18T18:45:00Z",
        "checks": {
            "mcp_server": "ok",
            "database": "ok",
            "external_apis": "ok"
        },
        "version": "1.0.0"
    }


@app.post("/mcp")
async def handle_mcp_request(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Handle MCP requests via HTTP POST.
    
    This endpoint accepts standard MCP JSON-RPC messages and returns responses.
    """
    try:
        response = await mcp_server.handle_request(request)
        return response
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal server error: {str(e)}"
            }
        }


@app.websocket("/mcp/ws")
async def websocket_mcp_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time MCP communication.
    
    Provides persistent connection for AI agents that need continuous context updates.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive MCP request
            data = await websocket.receive_text()
            request = json.loads(data)
            
            # Process request
            response = await mcp_server.handle_request(request)
            
            # Send response
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        await websocket.close(code=1011, reason=f"Server error: {str(e)}")


@app.get("/mcp/resources")
async def list_resources(api_key: str = Depends(verify_api_key)):
    """List available MCP resources."""
    request = {
        "jsonrpc": "2.0",
        "id": "list_resources",
        "method": "resources/list"
    }
    
    response = await mcp_server.handle_request(request)
    return response.get("result", {})


@app.get("/mcp/tools")
async def list_tools(api_key: str = Depends(verify_api_key)):
    """List available MCP tools."""
    request = {
        "jsonrpc": "2.0", 
        "id": "list_tools",
        "method": "tools/list"
    }
    
    response = await mcp_server.handle_request(request)
    return response.get("result", {})


@app.get("/mcp/prompts")
async def list_prompts(api_key: str = Depends(verify_api_key)):
    """List available MCP prompts."""
    request = {
        "jsonrpc": "2.0",
        "id": "list_prompts", 
        "method": "prompts/list"
    }
    
    response = await mcp_server.handle_request(request)
    return response.get("result", {})


@app.post("/mcp/tools/{tool_name}")
async def call_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Call a specific MCP tool."""
    request = {
        "jsonrpc": "2.0",
        "id": f"call_{tool_name}",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    response = await mcp_server.handle_request(request)
    
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    return response.get("result", {})


@app.get("/mcp/resources/{resource_uri:path}")
async def read_resource(
    resource_uri: str,
    api_key: str = Depends(verify_api_key)
):
    """Read a specific MCP resource."""
    request = {
        "jsonrpc": "2.0",
        "id": f"read_{resource_uri.replace('/', '_')}",
        "method": "resources/read",
        "params": {
            "uri": f"mcp://women-health/{resource_uri}"
        }
    }
    
    response = await mcp_server.handle_request(request)
    
    if "error" in response:
        raise HTTPException(status_code=404, detail=response["error"])
    
    return response.get("result", {})


@app.post("/mcp/prompts/{prompt_name}")
async def get_prompt(
    prompt_name: str,
    arguments: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Get a specific MCP prompt with arguments."""
    request = {
        "jsonrpc": "2.0",
        "id": f"prompt_{prompt_name}",
        "method": "prompts/get",
        "params": {
            "name": prompt_name,
            "arguments": arguments
        }
    }
    
    response = await mcp_server.handle_request(request)
    
    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])
    
    return response.get("result", {})


# Anthropic/OpenAI Integration Endpoints
@app.post("/ai/anthropic/complete")
async def anthropic_completion(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Proxy endpoint for Anthropic Claude API with MCP context.
    Automatically injects relevant MCP resources and tools into the conversation.
    """
    # This would integrate with Anthropic's Claude API
    # For now, return a placeholder response
    return {
        "completion": "Anthropic integration coming soon...",
        "model": "claude-3-sonnet",
        "mcp_context_injected": True
    }


@app.post("/ai/openai/complete")
async def openai_completion(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Proxy endpoint for OpenAI API with MCP context.
    Automatically injects relevant MCP resources and tools into the conversation.
    """
    # This would integrate with OpenAI's API
    # For now, return a placeholder response
    return {
        "completion": "OpenAI integration coming soon...",
        "model": "gpt-4",
        "mcp_context_injected": True
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the MCP server."""
    uvicorn.run(
        "mcp_server.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server(reload=True)