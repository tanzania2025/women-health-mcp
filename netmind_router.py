"""
Netmind Routing Logic - Routes queries to appropriate data sources and agents
"""
from typing import Dict, Any


# Routing configuration for different query types
ROUTING_CONFIG = {
    "fertility_query": {
        "data_sources": [
            "biomini_patient_context",
            "huggingface_research",
            "sart_database"
        ],
        "agents": [
            "data_retrieval_agent",
            "clinical_advisor_agent"
        ],
        "priority": "high"
    },
    "menopause_query": {
        "data_sources": [
            "biomini_patient_context",
            "swan_biomarkers",
            "huggingface_research"
        ],
        "agents": [
            "data_retrieval_agent",
            "menopause_advisor_agent"
        ],
        "priority": "medium"
    },
    "general_reproductive_health": {
        "data_sources": [
            "biomini_patient_context",
            "clinical_guidelines"
        ],
        "agents": [
            "general_health_agent"
        ],
        "priority": "medium"
    }
}


def route_query(query_type: str) -> Dict[str, Any]:
    """
    Return routing configuration for a given query type.
    
    Args:
        query_type: Type of clinical query
        
    Returns:
        Routing configuration dict
    """
    return ROUTING_CONFIG.get(query_type, ROUTING_CONFIG["general_reproductive_health"])


def orchestrate_query(patient_data: Dict[str, Any], clinical_question: str) -> Dict[str, Any]:
    """
    Orchestrate the query through the routing system.
    
    Args:
        patient_data: Standardized patient data from Biomini
        clinical_question: The clinical question to answer
        
    Returns:
        Orchestration result with activated components
    """
    # Determine query type based on keywords
    query_type = "fertility_query"  # Default for IVF-related questions
    
    if "menopause" in clinical_question.lower():
        query_type = "menopause_query"
    elif "ivf" not in clinical_question.lower() and "fertility" not in clinical_question.lower():
        query_type = "general_reproductive_health"
    
    # Get routing configuration
    route = route_query(query_type)
    
    # Build orchestration result
    orchestration_result = {
        "query_type": query_type,
        "patient_id": patient_data.get("patient_id"),
        "routing": route,
        "execution_plan": {
            "step_1": f"Retrieve data from: {', '.join(route['data_sources'])}",
            "step_2": f"Activate agents: {', '.join(route['agents'])}",
            "step_3": "Synthesize recommendations"
        },
        "status": "ready"
    }
    
    return orchestration_result


def display_routing_info(orchestration_result: Dict[str, Any]) -> None:
    """Display routing information in a formatted way."""
    print(f"Query Type: {orchestration_result['query_type']}")
    print(f"Priority: {orchestration_result['routing']['priority']}")
    print(f"\nData Sources to Query:")
    for source in orchestration_result['routing']['data_sources']:
        print(f"  → {source}")
    print(f"\nAgents to Activate:")
    for agent in orchestration_result['routing']['agents']:
        print(f"  → {agent}")


if __name__ == "__main__":
    # Test routing logic
    print("=== NETMIND ROUTER TEST ===\n")
    
    # Test fertility query routing
    test_patient = {"patient_id": "P001"}
    result = orchestrate_query(test_patient, "Should I do IVF now?")
    
    print("Routing for 'Should I do IVF now?':")
    display_routing_info(result)
    
    print("\n" + "="*50 + "\n")
    
    # Test menopause query routing
    result2 = orchestrate_query(test_patient, "Am I approaching menopause?")
    print("Routing for 'Am I approaching menopause?':")
    display_routing_info(result2)