"""
End-to-End Demo - Orchestrates the full women's health MCP pipeline
"""
import json
from typing import Dict, Any

from biomini_intake import ingest_patient
from netmind_router import orchestrate_query, display_routing_info
from manus_agents import data_retrieval_agent, clinical_advisor_agent
from huggingface_integration import rank_papers_by_relevance, display_ranked_papers


def print_section(title: str, icon: str = "═"):
    """Print a formatted section header."""
    print(f"\n{icon * 60}")
    print(f"  {title}")
    print(f"{icon * 60}\n")


def run_full_pipeline(patient_json: Dict[str, Any], clinical_question: str) -> Dict[str, Any]:
    """
    Execute the full pipeline from patient data to clinical recommendation.
    
    Args:
        patient_json: Raw patient data
        clinical_question: Clinical question to answer
        
    Returns:
        Complete pipeline output
    """
    print_section("WOMEN'S HEALTH MCP - CLINICAL DECISION SUPPORT", "╔")
    print(f"Clinical Question: {clinical_question}")
    print(f"Patient ID: {patient_json.get('patient_id', 'Unknown')}")
    
    # Step 1: Biomini Data Intake
    print_section("[BIOMINI] Ingesting patient data...", "▶")
    patient_data = ingest_patient(patient_json)
    
    print(f"✓ Patient Age: {patient_data['demographics']['age']} years")
    print(f"✓ AMH Level: {patient_data['reproductive_labs']['amh']} ng/mL")
    print(f"✓ Ovarian Reserve Status: {patient_data['ovarian_reserve_status'].upper()}")
    print(f"✓ Years Trying to Conceive: {patient_data['demographics']['years_trying_to_conceive']:.1f}")
    
    # Step 2: Netmind Routing
    print_section("[NETMIND] Routing query...", "▶")
    routing_result = orchestrate_query(patient_data, clinical_question)
    display_routing_info(routing_result)
    
    # Step 3: Manus AI Orchestration
    print_section("[MANUS AI] Orchestrating agents...", "▶")
    
    # Agent 1: Data Retrieval
    print("→ Activating Data Retrieval Agent...")
    agent1_output = data_retrieval_agent(patient_data, clinical_question)
    
    print(f"  ✓ Patient profile analyzed")
    print(f"  ✓ Found {agent1_output['research_summary']['papers_found']} relevant research papers")
    print(f"  ✓ Key concern identified: {agent1_output['patient_summary']['key_concern']}")
    
    # Step 4: Hugging Face Paper Ranking
    print_section("[HUGGING FACE] Ranking research by relevance...", "▶")
    papers = agent1_output['research_summary']['papers']
    ranked_papers = rank_papers_by_relevance(clinical_question, papers)
    
    print("Top relevant research:")
    display_ranked_papers(ranked_papers[:3])  # Show top 3
    
    # Update agent1 output with ranked papers
    agent1_output['research_summary']['papers'] = ranked_papers
    
    # Agent 2: Clinical Advisor
    print_section("[MANUS AI] Generating clinical recommendation...", "▶")
    print("→ Activating Clinical Advisor Agent...")
    
    agent2_output = clinical_advisor_agent(agent1_output, clinical_question)
    
    print(f"  ✓ ASRM guidelines applied")
    print(f"  ✓ SART success rate calculated: {agent2_output['success_data']['rate']}%")
    print(f"  ✓ Recommendation urgency: {agent2_output['urgency'].upper()}")
    
    # Final Output
    print_section("[OUTPUT] Clinical Recommendation", "★")
    
    print("RECOMMENDATION:")
    print("-" * 50)
    print(agent2_output['recommendation'])
    print("-" * 50)
    
    print("\nCLINICAL REASONING:")
    for i, step in enumerate(agent2_output['reasoning'], 1):
        print(f"  {i}. {step}")
    
    print("\nEVIDENCE BASE:")
    evidence = agent2_output['evidence_base']
    print(f"  • Guidelines: {evidence['guidelines']}")
    print(f"  • Success Rates: {evidence['success_rates']}")
    print(f"  • Research Papers Reviewed: {evidence['research_papers']}")
    
    # Compile complete output
    complete_output = {
        "patient_data": patient_data,
        "routing": routing_result,
        "data_retrieval": agent1_output,
        "clinical_advisor": agent2_output,
        "ranked_research": ranked_papers[:3]
    }
    
    print_section("Pipeline execution complete!", "╚")
    
    return complete_output


if __name__ == "__main__":
    # Test with sample patient
    from biomini_intake import SAMPLE_PATIENT_1
    
    # Run the full pipeline
    result = run_full_pipeline(
        SAMPLE_PATIENT_1,
        "I have AMH 0.8, should I do IVF now?"
    )
    
    # Optional: Save output to file
    with open("pipeline_output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n💾 Full output saved to pipeline_output.json")