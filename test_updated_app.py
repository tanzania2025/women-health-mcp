#!/usr/bin/env python3
"""
Test Updated App.py - Detailed Logging Version
Tests the new query_with_mcp_standalone function with detailed technical logs
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the updated function
from app import query_with_mcp_standalone

async def test_updated_app():
    """Test the updated app.py function with detailed logging"""
    print("🧪 Testing Updated App.py - Detailed Logging Version")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Please set your ANTHROPIC_API_KEY in environment variables")
        return
    
    print("✅ Anthropic API key found")
    
    # Test query
    query = "What are current PCOS treatments? Search recent research."
    print(f"\n🔍 Testing query: '{query}'")
    print("=" * 60)
    
    try:
        response = await query_with_mcp_standalone(query)
        print(response)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_updated_app())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")