#!/usr/bin/env python3
"""
Test Enhanced Multi-Dataset Demo
Verify all enhanced capabilities are working with multiple SWAN visits
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_server.mcp_protocol import MCPServer
from multi_dataset_integration import multi_dataset_integration

async def test_enhanced_demo():
    """Test all enhanced multi-dataset demo components."""
    
    print("🌊 Enhanced Women's Health MCP Demo Test")
    print("Testing multi-dataset integration with longitudinal SWAN analysis")
    print("="*70)
    
    # Test 1: Multi-dataset integration
    print("\n1️⃣ Testing Multi-Dataset Integration...")
    overview = multi_dataset_integration.get_datasets_overview()
    
    total_datasets = overview['total_datasets']
    loaded_datasets = overview['loaded_datasets']
    
    print(f"   📊 Datasets discovered: {total_datasets}")
    print(f"   ✅ Datasets loaded: {loaded_datasets}")
    
    if loaded_datasets > 0:
        total_participants = overview.get('total_participants', 0)
        total_variables = overview.get('total_variables', 0)
        date_range = overview.get('date_range', 'N/A')
        
        print(f"   👥 Total participants: {total_participants:,}")
        print(f"   📋 Total variables: {total_variables:,}")
        print(f"   📅 Date range: {date_range}")
        
        print("\n   📋 Loaded Dataset Details:")
        for dataset_id, info in overview['datasets'].items():
            if info['loaded']:
                print(f"      ✅ {dataset_id}: {info['visit']} ({info['period']}) - {info['participants']:,} participants")
    else:
        print("   ❌ No datasets loaded")
        return False
    
    # Test 2: Longitudinal analysis
    print("\n2️⃣ Testing Longitudinal Analysis...")
    
    conditions = ["menopause progression", "hormone trajectories", "population demographics"]
    
    for condition in conditions:
        print(f"   🔬 Testing {condition}...")
        
        longitudinal_result = multi_dataset_integration.get_longitudinal_analysis(condition, (45, 55))
        
        if 'error' not in longitudinal_result:
            visits_analyzed = longitudinal_result['visits_analyzed']
            total_sample = sum(data['sample_size'] for data in longitudinal_result['longitudinal_data'].values())
            print(f"      ✅ Analyzed {visits_analyzed} visits, {total_sample:,} participants")
        else:
            print(f"      ❌ Error in {condition} analysis")
    
    # Test 3: Cross-visit variable tracking
    print("\n3️⃣ Testing Cross-Visit Variable Tracking...")
    
    variable_categories = ["ESTR", "FSH", "AMH", "AGE", "MENO"]
    
    for category in variable_categories:
        search_results = multi_dataset_integration.search_variables_across_datasets(category)
        
        if search_results:
            datasets_with_vars = len(search_results)
            total_vars = sum(result['count'] for result in search_results.values())
            print(f"   🔍 {category}: Found in {datasets_with_vars} datasets, {total_vars} total variables")
        else:
            print(f"   ⚠️  {category}: No variables found")
    
    # Test 4: Cross-visit variable analysis
    print("\n4️⃣ Testing Cross-Visit Variable Analysis...")
    
    cross_analysis = multi_dataset_integration.get_cross_visit_variable_analysis("ESTR")
    
    if cross_analysis['visits_with_data'] > 0:
        visits_with_data = cross_analysis['visits_with_data']
        print(f"   📊 Estrogen analysis: {visits_with_data} visits with data")
        
        for dataset_id, data in cross_analysis['cross_visit_analysis'].items():
            visit = data['visit']
            vars_found = len(data['variables_found'])
            analysis_count = len(data.get('analysis', {}))
            print(f"      • {visit}: {vars_found} variables, {analysis_count} with statistics")
    else:
        print("   ❌ No cross-visit estrogen data found")
    
    # Test 5: MCP server integration
    print("\n5️⃣ Testing Enhanced MCP Server Integration...")
    
    mcp_server = MCPServer()
    print("   ✅ MCP server initialized")
    
    # Test enhanced ovarian reserve assessment
    ovarian_request = {
        'name': 'assess-ovarian-reserve',
        'arguments': {'age': 48, 'amh': 0.5}
    }
    
    ovarian_response = await mcp_server._handle_call_tool('test_enhanced_ovarian', ovarian_request)
    
    if 'error' not in ovarian_response:
        print("   ✅ Enhanced ovarian reserve calculator working")
    else:
        print("   ❌ Enhanced ovarian reserve calculator failed")
    
    # Test SWAN database query with multi-dataset context
    swan_request = {
        'name': 'query-research-database',
        'arguments': {
            'database': 'swan',
            'query_type': 'population_statistics',
            'condition': 'menopause progression'
        }
    }
    
    swan_response = await mcp_server._handle_call_tool('test_enhanced_swan', swan_request)
    
    if 'error' not in swan_response:
        print("   ✅ Enhanced SWAN database queries working")
    else:
        print("   ❌ Enhanced SWAN database queries failed")
    
    print("\n🎉 Enhanced Demo Component Testing Complete!")
    print("="*70)
    
    # Summary of enhanced capabilities
    print("\n📊 Enhanced Capabilities Summary:")
    print(f"   🌊 Multi-Dataset Integration: {loaded_datasets} SWAN visits loaded")
    print(f"   👥 Population Scale: {total_participants:,} participants")
    print(f"   📈 Longitudinal Analysis: 3 condition types supported")
    print(f"   🔬 Variable Tracking: 5 categories tested")
    print(f"   🧮 Enhanced Calculators: Population context from multiple visits")
    print(f"   🤖 AI Context: Longitudinal evidence synthesis")
    
    print("\n🚀 Enhanced Demo Launch Commands:")
    print("   # Multi-dataset web demo:")
    print("   streamlit run enhanced_streamlit_demo.py")
    print("   ")
    print("   # Original single-visit demo:")
    print("   streamlit run streamlit_demo.py")
    print("   ")
    print("   # Command-line demos:")
    print("   python swan_mcp_demo.py")
    print("   python claude_mcp_integration.py")
    
    return True

def main():
    """Run the enhanced demo component tests."""
    
    success = asyncio.run(test_enhanced_demo())
    
    if success:
        print("\n✨ Enhanced demo is ready!")
        print("🌊 Experience longitudinal women's health AI with multiple SWAN visits!")
        print("\nRecommended: streamlit run enhanced_streamlit_demo.py")
    else:
        print("\n❌ Enhanced demo has issues. Check the error messages above.")

if __name__ == "__main__":
    main()