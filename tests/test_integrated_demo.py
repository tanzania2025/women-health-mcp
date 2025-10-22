#!/usr/bin/env python3
"""
Quick test script for the integrated Streamlit demo
Tests that all imports work and basic functionality is available
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
    
    try:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Data visualization libraries imported successfully")
    except ImportError as e:
        print(f"❌ Visualization libraries import failed: {e}")
    
    try:
        from mcp_server.mcp_protocol import MCPServer
        from mcp_server.swan_data_integration import swan_integration
        print("✅ MCP server components imported successfully")
    except ImportError as e:
        print(f"❌ MCP server import failed: {e}")
    
    # Test optional dependencies
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"⚠️ BeautifulSoup not available: {e}")
    
    try:
        import httpx
        print("✅ HTTPX imported successfully")
    except ImportError as e:
        print(f"❌ HTTPX import failed: {e}")

def test_menopause_calculator():
    """Test the menopause calculator function."""
    print("\nTesting menopause calculator...")
    
    try:
        # Import the function from the demo file
        from streamlit_demo import calculate_menopause_age_simple
        
        # Test calculation
        result = calculate_menopause_age_simple(
            age=45,
            race="white", 
            bmi=24.0,
            smoking=False,
            pregnancies=2,
            breastfeeding=True,
            family_history="average"
        )
        
        print(f"✅ Menopause calculator test: {result:.1f} years")
        
        if 45 <= result <= 58:
            print("✅ Result is within expected range")
        else:
            print("⚠️ Result outside expected range")
            
    except Exception as e:
        print(f"❌ Menopause calculator test failed: {e}")

def test_swan_integration():
    """Test SWAN data integration."""
    print("\nTesting SWAN integration...")
    
    try:
        from mcp_server.swan_data_integration import swan_integration
        
        # Test dataset info
        info = swan_integration.get_dataset_info()
        print(f"✅ SWAN dataset status: {info.get('status', 'unknown')}")
        
        if info.get('status') == 'loaded':
            print(f"   Participants: {info.get('participants', 'N/A')}")
            print(f"   Variables: {info.get('variables', 'N/A')}")
        
    except Exception as e:
        print(f"❌ SWAN integration test failed: {e}")

def test_copied_servers():
    """Test that Dan's servers were copied successfully."""
    print("\nTesting copied MCP servers...")
    
    server_files = [
        "menopause_server.py",
        "sart_ivf_server.py", 
        "asrm_server.py",
        "nams_server.py",
        "pubmed_server.py"
    ]
    
    for server_file in server_files:
        file_path = Path(__file__).parent / server_file
        if file_path.exists():
            print(f"✅ {server_file} copied successfully")
        else:
            print(f"❌ {server_file} not found")

def main():
    """Run all tests."""
    print("🧪 Testing Integrated Streamlit Demo")
    print("=" * 40)
    
    test_imports()
    test_menopause_calculator()
    test_swan_integration()
    test_copied_servers()
    
    print("\n" + "=" * 40)
    print("✨ Integration test complete!")
    print("\nTo run the demo:")
    print("streamlit run streamlit_demo.py")

if __name__ == "__main__":
    main()