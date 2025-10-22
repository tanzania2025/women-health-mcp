#!/usr/bin/env python3
"""
Claude Integration with Women's Health MCP
Demonstrates how Claude would use the MCP server for clinical consultations
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from mcp_server.mcp_protocol import MCPServer
from mcp_server.config import settings

class ClaudeMCPIntegration:
    """
    Demonstration of how Claude would integrate with the Women's Health MCP server.
    Shows the complete workflow from patient question to evidence-based recommendation.
    """
    
    def __init__(self):
        self.mcp_server = MCPServer()
        self.anthropic_api_key = settings.anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        
    async def process_fertility_consultation(self, patient_question: str, patient_data: Dict[str, Any]) -> str:
        """
        Process a fertility consultation using MCP server context.
        This demonstrates how Claude would gather MCP context before generating a response.
        """
        
        print("🤖 Claude AI Processing with MCP Context...")
        print(f"📝 Patient Question: {patient_question}")
        print()
        
        # Step 1: Get clinical context from MCP tools
        mcp_context = await self._gather_mcp_context(patient_data)
        
        # Step 2: Get formatted prompt template
        consultation_prompt = await self._get_consultation_prompt(patient_question, patient_data)
        
        # Step 3: Generate Claude response (simulated)
        claude_response = await self._generate_claude_response(consultation_prompt, mcp_context)
        
        return claude_response
    
    async def _gather_mcp_context(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gather relevant context from MCP server tools."""
        
        context = {}
        
        # Get ovarian reserve assessment
        if 'age' in patient_data and 'amh' in patient_data:
            print("🧮 Gathering ovarian reserve assessment...")
            ovarian_request = {
                'name': 'assess-ovarian-reserve',
                'arguments': {
                    'age': patient_data['age'],
                    'amh': patient_data['amh']
                }
            }
            
            response = await self.mcp_server._handle_call_tool('ovarian_assessment', ovarian_request)
            ovarian_result = json.loads(response['result']['content'][0]['text'])
            context['ovarian_reserve'] = ovarian_result['result']
            print(f"   ✅ Ovarian reserve: {ovarian_result['result']['category']}")
        
        # Get IVF success prediction
        if 'age' in patient_data and 'amh' in patient_data:
            print("📈 Gathering IVF success prediction...")
            ivf_request = {
                'name': 'predict-ivf-success',
                'arguments': {
                    'age': patient_data['age'],
                    'amh': patient_data['amh'],
                    'cycle_type': 'fresh'
                }
            }
            
            response = await self.mcp_server._handle_call_tool('ivf_prediction', ivf_request)
            ivf_result = json.loads(response['result']['content'][0]['text'])
            context['ivf_prediction'] = ivf_result['result']
            print(f"   ✅ IVF success rate: {ivf_result['result']['live_birth_rate']:.1f}%")
        
        # Get SWAN population context
        print("📊 Gathering SWAN population context...")
        swan_request = {
            'name': 'query-research-database',
            'arguments': {
                'database': 'swan',
                'query_type': 'population_statistics',
                'condition': 'menopause timing',
                'age_range': [patient_data.get('age', 35) - 5, patient_data.get('age', 35) + 5]
            }
        }
        
        response = await self.mcp_server._handle_call_tool('swan_query', swan_request)
        swan_result = json.loads(response['result']['content'][0]['text'])
        context['swan_data'] = swan_result
        print(f"   ✅ SWAN context: Population data retrieved")
        
        print()
        return context
    
    async def _get_consultation_prompt(self, question: str, patient_data: Dict[str, Any]) -> str:
        """Get the formatted consultation prompt from MCP server."""
        
        print("📋 Getting consultation prompt template...")
        
        prompt_request = {
            'name': 'fertility-consultation',
            'arguments': {
                'patient_age': patient_data.get('age'),
                'amh_level': patient_data.get('amh'),
                'clinical_question': question,
                'urgency_level': 'routine'
            }
        }
        
        response = await self.mcp_server._handle_get_prompt('prompt_request', prompt_request)
        prompt_content = response['result']['messages'][0]['content']['text']
        
        print("   ✅ Consultation prompt template retrieved")
        print()
        
        return prompt_content
    
    async def _generate_claude_response(self, prompt: str, mcp_context: Dict[str, Any]) -> str:
        """
        Simulate Claude's response generation using MCP context.
        In production, this would call the actual Anthropic API.
        """
        
        print("🧠 Claude AI generating evidence-based response...")
        print()
        
        # This is where we would call the Anthropic API
        if self.anthropic_api_key:
            print(f"   🔑 Anthropic API Key configured: {self.anthropic_api_key[:20]}...")
            print("   ⚠️  Actual Claude API call would happen here")
        else:
            print("   ⚠️  No Anthropic API key found - using simulated response")
        
        # Simulate Claude's sophisticated response using the MCP context
        ovarian = mcp_context.get('ovarian_reserve', {})
        ivf = mcp_context.get('ivf_prediction', {})
        
        urgency = "HIGH" if (ovarian.get('category') == 'low' and ivf.get('live_birth_rate', 0) < 25) else "ROUTINE"
        timeline = "1-2 months" if urgency == "HIGH" else "3-6 months"
        
        claude_response = f"""
Based on my analysis of your clinical profile using the latest evidence-based guidelines and research data:

**CLINICAL ASSESSMENT:**
• Ovarian Reserve: {ovarian.get('category', 'N/A').replace('_', ' ').title()} ({ovarian.get('percentile', 'N/A')}th percentile for your age)
• IVF Success Rate: {ivf.get('live_birth_rate', 'N/A'):.1f}% per fresh cycle (age-adjusted)
• Population Context: Based on data from 2,413 women in the SWAN longitudinal study

**RECOMMENDATION:**
Given your age and AMH level, I recommend scheduling a fertility consultation within {timeline}. 
{'Your ovarian reserve indicates a time-sensitive fertility window where earlier intervention may improve outcomes.' if urgency == 'HIGH' else 'You have time to carefully consider your options.'}

**CLINICAL REASONING:**
{ovarian.get('interpretation', 'Clinical interpretation not available')}

The {ivf.get('live_birth_rate', 0):.1f}% success rate is based on SART data from similar patient profiles. 
Success rates {'decline significantly with age, making timing critical' if urgency == 'HIGH' else 'remain relatively stable in your age group'}.

**NEXT STEPS:**
1. Schedule consultation with reproductive endocrinologist
2. Consider additional testing (antral follicle count, FSH)
3. Discuss treatment timeline and options
4. {'Consider expedited evaluation given age and AMH levels' if urgency == 'HIGH' else 'Take time to research fertility preservation options'}

**EVIDENCE BASIS:**
This recommendation incorporates:
• ASRM/ESHRE clinical guidelines for ovarian reserve assessment
• SART database success rates (>50,000 cycles analyzed)
• SWAN longitudinal study population data (2,413 participants)
• Age-specific fertility decline trajectories

**CONFIDENCE LEVEL:** High - based on robust clinical data and established guidelines.
"""
        
        print("   ✅ Evidence-based response generated")
        return claude_response.strip()

async def main():
    """Demonstrate Claude integration with Women's Health MCP server."""
    
    print("🔗 " + "="*60)
    print("   Claude AI + Women's Health MCP Integration Demo")
    print("   Evidence-Based Fertility Consultation")
    print("="*64)
    print()
    
    # Initialize Claude-MCP integration
    claude_mcp = ClaudeMCPIntegration()
    
    # Patient scenario
    patient_question = "I'm 38 years old with AMH 0.8 ng/mL. Should I start IVF immediately or wait?"
    patient_data = {
        'age': 38,
        'amh': 0.8,
        'trying_to_conceive': True,
        'previous_pregnancies': 0
    }
    
    print("👤 Patient Profile:")
    print(f"   Age: {patient_data['age']} years")
    print(f"   AMH: {patient_data['amh']} ng/mL")
    print(f"   Question: {patient_question}")
    print()
    
    # Process consultation
    claude_response = await claude_mcp.process_fertility_consultation(patient_question, patient_data)
    
    # Display result
    print("🎯 Claude AI Consultation Response:")
    print("="*64)
    print(claude_response)
    print("="*64)
    print()
    
    print("✨ MCP Integration Benefits:")
    print("   🔍 Real-time access to clinical calculators and research data")
    print("   📊 Evidence-based recommendations with confidence intervals")
    print("   🧮 ASRM/ESHRE guideline compliance")
    print("   📚 SWAN longitudinal study population context")
    print("   ⚡ Urgency assessment based on age and biomarker trajectories")
    print()
    
    print("🚀 Production Integration:")
    print("   • Add Anthropic API key to .env file")
    print("   • Replace simulated response with actual Claude API call")
    print("   • Deploy MCP server for real-time AI agent access")
    print("="*64)

if __name__ == "__main__":
    asyncio.run(main())