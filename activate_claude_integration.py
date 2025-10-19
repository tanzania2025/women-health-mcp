#!/usr/bin/env python3
"""
Activate Full Claude Integration with MCP Server
Replace the placeholder endpoints with real Anthropic API calls
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def create_real_claude_integration():
    """Create the real Claude API integration code."""
    
    claude_integration_code = '''
import anthropic
from mcp_server.config import settings

async def real_anthropic_completion(request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """
    Real Anthropic Claude API integration with MCP context.
    Automatically injects relevant MCP resources and tools into the conversation.
    """
    
    # Initialize Anthropic client
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")
    
    anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    # Extract patient question and data
    message = request.get("message", "")
    include_mcp_context = request.get("include_mcp_context", True)
    patient_data = request.get("patient_data", {})
    
    # Gather MCP context if requested
    mcp_context = ""
    if include_mcp_context:
        # Get clinical assessment
        if patient_data.get("age") and patient_data.get("amh"):
            ovarian_request = {
                "jsonrpc": "2.0",
                "id": "ovarian_assessment",
                "method": "tools/call",
                "params": {
                    "name": "assess-ovarian-reserve",
                    "arguments": {
                        "age": patient_data["age"],
                        "amh": patient_data["amh"]
                    }
                }
            }
            ovarian_response = await mcp_server.handle_request(ovarian_request)
            
            # Get SWAN population context
            swan_request = {
                "jsonrpc": "2.0",
                "id": "swan_context",
                "method": "tools/call",
                "params": {
                    "name": "query-research-database",
                    "arguments": {
                        "database": "swan",
                        "query_type": "population_statistics",
                        "condition": "reproductive health"
                    }
                }
            }
            swan_response = await mcp_server.handle_request(swan_request)
            
            mcp_context = f"""
MCP CLINICAL CONTEXT:
- Ovarian Reserve Assessment: {ovarian_response.get('result', 'N/A')}
- SWAN Population Data: {swan_response.get('result', 'N/A')}
- Guidelines: ASRM/ESHRE evidence-based protocols applied
"""
    
    # Create Claude prompt with MCP context
    full_prompt = f"""
You are an expert reproductive endocrinologist providing evidence-based fertility consultation.

{mcp_context}

PATIENT QUESTION: {message}

Provide a comprehensive, evidence-based response that incorporates the MCP clinical context above.
Include specific recommendations, success rates, and clinical reasoning.
"""
    
    # Call Claude API
    response = await anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    )
    
    return {
        "completion": response.content[0].text,
        "model": "claude-3-sonnet",
        "mcp_context_injected": include_mcp_context,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    }
'''
    
    print("🔧 Creating real Claude integration code...")
    print("📋 To activate, replace the placeholder in mcp_server/server.py:")
    print()
    print("1️⃣ Install Anthropic SDK:")
    print("   pip install anthropic")
    print()
    print("2️⃣ Replace the anthropic_completion function at line 252 with:")
    print(claude_integration_code)
    print()
    print("3️⃣ Test with:")
    print("   curl -X POST http://localhost:8000/ai/anthropic/complete \\")
    print("     -H 'Authorization: Bearer your-api-key' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print("       \"message\": \"38-year-old with AMH 0.8, should I do IVF?\",")
    print("       \"include_mcp_context\": true,")
    print("       \"patient_data\": {\"age\": 38, \"amh\": 0.8}")
    print("     }'")

def show_current_usage():
    """Show where the API key is currently used."""
    
    print("🔍 Current ANTHROPIC_API_KEY Usage:")
    print()
    
    print("✅ LOADED IN CONFIGURATION:")
    print("   File: mcp_server/config.py")
    print("   Line: 23 - anthropic_api_key: Optional[str] = None")
    print("   Source: .env file")
    print()
    
    print("✅ AVAILABLE IN SERVER:")
    print("   File: mcp_server/server.py") 
    print("   Line: 252 - @app.post('/ai/anthropic/complete')")
    print("   Status: Placeholder endpoint ready for activation")
    print()
    
    print("✅ DEMONSTRATED IN:")
    print("   File: claude_mcp_integration.py")
    print("   Line: 12 - self.anthropic_api_key = settings.anthropic_api_key")
    print("   Function: Shows MCP context gathering for Claude")
    print()
    
    print("📚 DOCUMENTED IN:")
    print("   File: README.md - Integration examples")
    print("   File: MCP_SERVER_GUIDE.md - Production deployment")
    print()

def main():
    """Show API key usage and activation instructions."""
    
    print("🔑 " + "="*50)
    print("   ANTHROPIC_API_KEY Integration Status")
    print("="*54)
    print()
    
    # Check if API key is configured
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"✅ API Key Found: {api_key[:20]}...")
        print(f"   Length: {len(api_key)} characters")
        print("   Status: Ready for integration")
    else:
        print("❌ API Key Not Found")
        print("   Please add ANTHROPIC_API_KEY to .env file")
    print()
    
    show_current_usage()
    create_real_claude_integration()
    
    print("="*54)
    print("🚀 Your MCP server is ready for full Claude integration!")
    print("   The infrastructure is built - just activate the API calls")
    print("="*54)

if __name__ == "__main__":
    main()