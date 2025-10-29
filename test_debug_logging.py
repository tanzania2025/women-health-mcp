#!/usr/bin/env python3
"""
Test Debug Logging Function Only
Tests just the debug logging functionality without full execution
"""

import asyncio
from app import query_with_mcp_standalone

async def test_debug_logging():
    """Test debug logging with a simple query"""
    print("🧪 Testing Debug Logging Functionality")
    print("=" * 50)
    
    # Test with invalid API key to see error handling
    import os
    original_key = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = ""  # Force error
    
    try:
        response = await query_with_mcp_standalone("Test query")
        print("Response:")
        print(response)
    except Exception as e:
        print(f"Exception (expected): {e}")
    finally:
        # Restore original key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key

if __name__ == "__main__":
    asyncio.run(test_debug_logging())