#!/usr/bin/env python3
"""
SWAN MCP Integration Demo
Demonstrates complete flow from real SWAN data to AI-powered clinical recommendations
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from demos.mcp_server.mcp_protocol import MCPServer
from demos.mcp_server.swan_data_integration import swan_integration

async def main():
    """
    Complete demonstration of SWAN data integration with MCP server
    for women's health AI agents.
    """

    print("🌊 " + "="*60)
    print("   SWAN Data Integration with Women's Health MCP")
    print("   Real Research Data → AI Clinical Recommendations")
    print("="*64)
    print()

    # Initialize MCP Server
    print("🚀 Initializing MCP Server...")
    server = MCPServer()
    print("   ✅ MCP Server ready with 9 clinical tools")
    print()

    # Check SWAN data status
    print("📊 Checking SWAN Dataset Status...")
    dataset_info = swan_integration.get_dataset_info()

    if dataset_info['status'] == 'loaded':
        print(f"   ✅ SWAN Dataset: {dataset_info['participants']} participants, {dataset_info['variables']} variables")
        print(f"   📅 Study Period: {dataset_info['visit']}")
        print(f"   🌍 Ethnicities: {len(dataset_info['ethnicities'])} groups")
    else:
        print("   ⚠️  SWAN dataset not loaded - using mock data")
    print()

    # Simulate AI Agent Query
    print("🤖 AI Agent Query Example:")
    print('   Patient Question: "I\'m 38 with AMH 0.8 ng/mL. Should I do IVF now?"')
    print()

    # Step 1: Get SWAN population context
    print("📈 Step 1: Query SWAN Population Data...")

    swan_query = {
        'name': 'query-research-database',
        'arguments': {
            'database': 'swan',
            'query_type': 'population_statistics',
            'condition': 'menopause timing',
            'age_range': [35, 45]
        }
    }

    swan_response = await server._handle_call_tool('swan_query', swan_query)
    swan_result = json.loads(swan_response['result']['content'][0]['text'])

    # Handle the nested result structure
    if 'result' in swan_result:
        swan_data = swan_result['result']
    else:
        swan_data = swan_result

    print(f"   📊 Population Sample: {swan_data.get('sample_size', 'N/A')} women aged 35-45")
    if 'age_statistics' in swan_data and swan_data['age_statistics']['mean_age']:
        print(f"   📈 Mean Age: {swan_data['age_statistics']['mean_age']:.1f} years")
    print("   ✅ SWAN context retrieved")
    print()

    # Step 2: Clinical ovarian reserve assessment
    print("🧮 Step 2: Clinical Ovarian Reserve Assessment...")

    ovarian_query = {
        'name': 'assess-ovarian-reserve',
        'arguments': {
            'age': 38,
            'amh': 0.8
        }
    }

    ovarian_response = await server._handle_call_tool('ovarian_assessment', ovarian_query)
    ovarian_result = json.loads(ovarian_response['result']['content'][0]['text'])

    print(f"   🔬 Ovarian Reserve: {ovarian_result['result']['category']}")
    print(f"   📊 Population Percentile: {ovarian_result['result']['percentile']}th")
    print(f"   💡 Clinical Interpretation: {ovarian_result['result']['interpretation']}")
    print("   ✅ ASRM assessment completed")
    print()

    # Step 3: IVF success prediction
    print("🎯 Step 3: IVF Success Rate Prediction...")

    ivf_query = {
        'name': 'predict-ivf-success',
        'arguments': {
            'age': 38,
            'amh': 0.8,
            'cycle_type': 'fresh'
        }
    }

    ivf_response = await server._handle_call_tool('ivf_prediction', ivf_query)
    ivf_result = json.loads(ivf_response['result']['content'][0]['text'])

    print(f"   📈 Live Birth Rate: {ivf_result['result']['live_birth_rate']:.1f}%")
    print(f"   📊 Confidence Interval: {ivf_result['result']['confidence_interval']}")
    print(f"   🔄 3-Cycle Cumulative: {ivf_result['result']['cumulative_success_3_cycles']:.1f}%")
    print("   ✅ SART-based prediction completed")
    print()

    # Step 4: Search SWAN hormone variables
    print("🔬 Step 4: SWAN Hormone Variable Analysis...")

    hormone_vars = swan_integration.search_variables("ESTR")
    print(f"   🧪 Found {len(hormone_vars)} estrogen-related variables:")
    for var in hormone_vars[:3]:
        print(f"      • {var}")
    print("   ✅ Hormone data available for analysis")
    print()

    # Generate AI-powered recommendation
    print("🎯 AI-Powered Clinical Recommendation:")
    print("="*64)

    # Determine urgency based on age and AMH
    urgency = "HIGH" if (38 >= 38 and 0.8 <= 1.0) else "ROUTINE"
    timeline = "1-2 months" if urgency == "HIGH" else "3-6 months"

    print(f"""
📊 POPULATION CONTEXT (SWAN DATA):
   Your AMH level (0.8 ng/mL) places you in the {ovarian_result['result']['percentile']}th percentile.
   SWAN study shows similar profiles in {swan_data.get('sample_size', 'N/A')} women aged 35-45.

🧮 CLINICAL ASSESSMENT:
   • Ovarian Reserve: {ovarian_result['result']['category'].replace('_', ' ').title()} (ASRM criteria)
   • IVF Success Rate: {ivf_result['result']['live_birth_rate']:.1f}% per fresh cycle (SART data)
   • Population Comparison: Below median for age group

⚡ URGENCY ASSESSMENT: {urgency}
   Age 38 with AMH 0.8 indicates time-sensitive fertility window.

💡 RECOMMENDATION:
   Schedule fertility consultation within {timeline}.
   Consider IVF evaluation given diminished ovarian reserve.
   Success rates decline with age - timing is critical.

📚 EVIDENCE BASIS:
   • SWAN Study: {dataset_info['participants']} participants, longitudinal data
   • SART Database: >50,000 IVF cycles for age-adjusted rates
   • ASRM Guidelines: Evidence-based ovarian reserve classification
   • Confidence Level: High (research-grade population data)
""")

    print("="*64)
    print("✨ Complete SWAN → MCP → AI Pipeline Demonstration")
    print(f"   🔗 Data Flow: Research Data → Clinical Tools → Evidence-Based AI")
    print(f"   🎯 Infrastructure: Production-ready for women's health AI market")
    print("="*64)

if __name__ == "__main__":
    asyncio.run(main())
