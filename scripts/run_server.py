#!/usr/bin/env python3
"""
Women's Health MCP Server Runner
Quick start script for development and testing
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import httpx
        print("✓ Core dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)

def setup_environment():
    """Setup environment variables if .env file doesn't exist."""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("⚠️  .env file not found, using defaults...")
        # Set minimal environment variables
        os.environ.setdefault("API_KEY", "demo-api-key-change-in-production")
        os.environ.setdefault("DEBUG", "true")
        os.environ.setdefault("ENABLE_REAL_APIS", "false")
    else:
        print("✓ .env file found")

def main():
    """Main entry point."""
    print("🚀 Starting Women's Health MCP Server...")
    print("="*50)
    
    # Check dependencies
    check_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Import after path setup
    from demos.mcp_server.server import start_server
    
    print("\n📡 MCP Server Configuration:")
    print(f"  Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"  Port: {os.getenv('PORT', '8000')}")
    print(f"  Debug: {os.getenv('DEBUG', 'true')}")
    print(f"  API Key: {os.getenv('API_KEY', 'demo-api-key')[:-10]}...")
    
    print("\n🔗 Available Endpoints:")
    print("  Health Check: http://localhost:8000/health")
    print("  MCP Resources: http://localhost:8000/mcp/resources")
    print("  MCP Tools: http://localhost:8000/mcp/tools")
    print("  WebSocket: ws://localhost:8000/mcp/ws")
    
    print("\n🧪 To test the server:")
    print("  streamlit run demos/doct_her_stdio.py")
    
    print("\n⭐ Features Available:")
    print("  ✓ Model Context Protocol (MCP) compliance")
    print("  ✓ Clinical calculators (ovarian reserve, IVF success)")
    print("  ✓ Research database integration (SWAN, SART)")
    print("  ✓ FHIR R4 compliant resources")
    print("  ✓ AI prompt templates")
    print("  ✓ WebSocket real-time communication")
    
    print("\n" + "="*50)
    print("Starting server... (Press Ctrl+C to stop)")
    
    try:
        # Start the server
        start_server(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            reload=os.getenv("DEBUG", "true").lower() == "true"
        )
    except KeyboardInterrupt:
        print("\n🔄 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()