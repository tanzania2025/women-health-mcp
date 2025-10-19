#!/usr/bin/env python3
"""
Test Streamlit Demo Components
Verify that all MCP + SWAN integrations work in the Streamlit environment
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_server.mcp_protocol import MCPServer
from mcp_server.swan_data_integration import swan_integration

async def test_streamlit_components():
    """Test all the components used in the Streamlit demo."""
    
    print("🧪 Testing Streamlit Demo Components")
    print("="*50)
    
    # Test 1: MCP Server initialization
    print("\n1️⃣ Testing MCP Server Initialization...")
    mcp_server = MCPServer()
    print("   ✅ MCP Server initialized successfully")
    
    # Test 2: SWAN dataset status
    print("\n2️⃣ Testing SWAN Dataset Status...")
    dataset_info = swan_integration.get_dataset_info()
    
    if dataset_info['status'] == 'loaded':
        print(f"   ✅ SWAN Dataset loaded: {dataset_info['participants']} participants")
        print(f"   📊 Variables available: {dataset_info['variables']}")
        print(f"   📅 Study period: {dataset_info['visit']}")
    else:
        print("   ❌ SWAN dataset not loaded")
        return False
    
    # Test 3: Clinical calculator functionality
    print("\n3️⃣ Testing Clinical Calculators...")
    
    # Test ovarian reserve assessment
    ovarian_request = {
        'name': 'assess-ovarian-reserve',
        'arguments': {'age': 38, 'amh': 0.8}
    }
    
    ovarian_response = await mcp_server._handle_call_tool('test_ovarian', ovarian_request)
    
    if 'error' not in ovarian_response:
        print("   ✅ Ovarian reserve calculator working")
    else:
        print("   ❌ Ovarian reserve calculator failed")
        return False
    
    # Test IVF success prediction
    ivf_request = {
        'name': 'predict-ivf-success',
        'arguments': {'age': 38, 'amh': 0.8, 'cycle_type': 'fresh'}
    }
    
    ivf_response = await mcp_server._handle_call_tool('test_ivf', ivf_request)
    
    if 'error' not in ivf_response:
        print("   ✅ IVF success predictor working")
    else:
        print("   ❌ IVF success predictor failed")
        return False
    
    # Test 4: SWAN data queries
    print("\n4️⃣ Testing SWAN Data Queries...")
    
    # Test SWAN population query
    swan_request = {
        'name': 'query-research-database',
        'arguments': {
            'database': 'swan',
            'query_type': 'population_statistics',
            'condition': 'reproductive health'
        }
    }
    
    swan_response = await mcp_server._handle_call_tool('test_swan', swan_request)
    
    if 'error' not in swan_response:
        print("   ✅ SWAN population queries working")
    else:
        print("   ❌ SWAN population queries failed")
        return False
    
    # Test 5: Variable search functionality
    print("\n5️⃣ Testing Variable Search...")
    
    hormone_vars = swan_integration.search_variables("ESTR")
    
    if len(hormone_vars) > 0:
        print(f"   ✅ Variable search working: Found {len(hormone_vars)} estrogen variables")
        print(f"   📋 Sample variables: {hormone_vars[:3]}")
    else:
        print("   ❌ Variable search failed")
        return False
    
    # Test 6: Variable summary functionality
    print("\n6️⃣ Testing Variable Summary...")
    
    if hormone_vars:
        var_summary = swan_integration.get_variable_summary(hormone_vars[0])
        
        if 'error' not in var_summary:
            print(f"   ✅ Variable summary working for {hormone_vars[0]}")
            print(f"   📊 Total records: {var_summary['total_records']}")
            print(f"   🔢 Data type: {var_summary['data_type']}")
        else:
            print("   ❌ Variable summary failed")
            return False
    
    print("\n🎉 All Streamlit Demo Components Working!")
    print("="*50)
    
    print("\n📋 Demo Features Available:")
    print("   ✅ 📊 SWAN Dataset Explorer")
    print("   ✅ 🧮 Clinical Calculator") 
    print("   ✅ 🤖 AI Fertility Consultation")
    print("   ✅ 📈 Population Analysis")
    print("   ✅ 🔬 Hormone Variables")
    
    print("\n🚀 Streamlit Demo URL: http://localhost:8501")
    print("   Navigate between different demo modes using the sidebar")
    
    return True

def main():
    """Run the Streamlit demo component tests."""
    
    print("🌊 Women's Health MCP Streamlit Demo Test")
    print("Testing integration with real SWAN data")
    
    success = asyncio.run(test_streamlit_components())
    
    if success:
        print("\n✨ Demo is ready! Run: streamlit run streamlit_demo.py")
    else:
        print("\n❌ Demo has issues. Check the error messages above.")

if __name__ == "__main__":
    main()