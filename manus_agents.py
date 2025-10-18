"""
Manus AI Agents - Data retrieval and clinical advisor agents for women's health
"""
import json
from typing import Dict, List, Any


# Mock research papers database
RESEARCH_PAPERS = [
    {
        "title": "AMH levels and reproductive outcomes: systematic review",
        "year": 2024,
        "key_findings": "AMH is a reliable marker for ovarian reserve but age remains the strongest predictor",
        "relevance_keywords": ["amh", "ovarian reserve", "ivf success", "systematic review"]
    },
    {
        "title": "IVF success in low AMH: what we learned",
        "year": 2023,
        "key_findings": "Low AMH alone should not exclude patients from IVF; personalized protocols improve outcomes",
        "relevance_keywords": ["low amh", "ivf", "success rates", "personalized treatment"]
    },
    {
        "title": "Age is more predictive than AMH",
        "year": 2024,
        "key_findings": "Chronological age outperforms AMH in predicting live birth rates in IVF",
        "relevance_keywords": ["age", "amh", "prediction", "live birth"]
    },
    {
        "title": "Optimizing IVF protocols for diminished ovarian reserve",
        "year": 2023,
        "key_findings": "Modified stimulation protocols can improve outcomes in low AMH patients",
        "relevance_keywords": ["diminished ovarian reserve", "ivf protocol", "low amh", "optimization"]
    },
    {
        "title": "Time to pregnancy and AMH levels: population study",
        "year": 2024,
        "key_findings": "AMH <1.0 associated with longer time to pregnancy but not absolute infertility",
        "relevance_keywords": ["amh", "time to pregnancy", "fertility", "population health"]
    }
]


def data_retrieval_agent(patient_data: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Agent 1: Analyze patient profile and retrieve relevant research.
    
    Args:
        patient_data: Standardized patient data from Biomini
        query: Clinical question
        
    Returns:
        Structured context for clinical advisor agent
    """
    # Step 1: Analyze patient profile
    age = patient_data['demographics']['age']
    amh = patient_data['reproductive_labs']['amh']
    ovarian_status = patient_data['ovarian_reserve_status']
    years_trying = patient_data['demographics']['years_trying_to_conceive']
    prior_ivf = patient_data['clinical_context']['prior_ivf']
    
    patient_summary = {
        "age": age,
        "amh_level": amh,
        "ovarian_reserve_category": ovarian_status,
        "infertility_duration_years": years_trying,
        "prior_treatments": prior_ivf,
        "key_concern": "Low ovarian reserve" if amh < 1.0 else "Age-related fertility decline"
    }
    
    # Step 2: Retrieve relevant papers (mock - in real system would query vector DB)
    relevant_papers = []
    for paper in RESEARCH_PAPERS:
        # Simple relevance scoring based on keywords
        if (amh < 1.0 and "low amh" in ' '.join(paper['relevance_keywords'])) or \
           ("ivf" in query.lower() and "ivf" in ' '.join(paper['relevance_keywords'])):
            relevant_papers.append(paper)
    
    # Limit to top 3-5 papers
    relevant_papers = relevant_papers[:5]
    
    # Step 3: Format context
    research_summary = {
        "papers_found": len(relevant_papers),
        "papers": [{"title": p['title'], "year": p['year'], "findings": p['key_findings']} 
                   for p in relevant_papers],
        "consensus": "Low AMH indicates reduced ovarian reserve but does not preclude IVF success",
        "recent_findings": "2024 studies emphasize age over AMH as primary success predictor"
    }
    
    return {
        "agent": "data_retrieval_agent",
        "patient_summary": patient_summary,
        "research_summary": research_summary,
        "data_sources_accessed": ["biomini_patient_context", "research_database"]
    }


def clinical_advisor_agent(agent1_output: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Agent 2: Synthesize clinical recommendation based on guidelines and data.
    
    Args:
        agent1_output: Output from data retrieval agent
        query: Clinical question
        
    Returns:
        Clinical recommendation with reasoning
    """
    patient = agent1_output['patient_summary']
    research = agent1_output['research_summary']
    
    # Step 1: Match to ASRM guidelines
    guideline = ""
    if patient['amh_level'] < 1.0:
        guideline = "ASRM recommends expedited fertility evaluation for AMH <1.0 ng/mL"
    else:
        guideline = "ASRM recommends standard fertility workup based on age and duration of infertility"
    
    # Step 2: Look up SART success rates (mock data)
    success_data = calculate_sart_success(patient['age'], patient['amh_level'])
    
    # Step 3: Synthesize recommendation
    if patient['age'] >= 40 or patient['amh_level'] < 0.5:
        urgency = "immediate"
        recommendation = (
            f"Based on your age ({patient['age']}) and AMH level ({patient['amh_level']} ng/mL), "
            f"we strongly recommend immediate consultation with a reproductive endocrinologist. "
            f"SART data shows {success_data['rate']}% success rate for your profile. "
            f"Time is a critical factor - each month of delay may reduce success rates."
        )
    elif patient['amh_level'] < 1.0:
        urgency = "expedited"
        recommendation = (
            f"Your AMH level ({patient['amh_level']} ng/mL) indicates diminished ovarian reserve. "
            f"We recommend scheduling a fertility consultation within 1-2 months. "
            f"SART data shows {success_data['rate']}% success rate for your profile. "
            f"Recent research shows that with optimized protocols, low AMH patients can achieve good outcomes."
        )
    else:
        urgency = "standard"
        recommendation = (
            f"Based on your profile, standard fertility evaluation is appropriate. "
            f"SART data shows {success_data['rate']}% success rate for your age group. "
            f"Consider consultation after 6 months of trying if under 35, or immediately if over 35."
        )
    
    reasoning_steps = [
        f"Patient age ({patient['age']}) and AMH ({patient['amh_level']}) analyzed",
        f"Ovarian reserve classified as: {patient['ovarian_reserve_category']}",
        f"ASRM guideline applied: {guideline}",
        f"SART success rate calculated: {success_data['rate']}% (CI: {success_data['confidence_interval']})",
        f"Research consensus: {research['consensus']}",
        f"Urgency level determined: {urgency}"
    ]
    
    return {
        "agent": "clinical_advisor_agent",
        "clinical_question": query,
        "patient_profile": patient,
        "relevant_guideline": guideline,
        "success_data": success_data,
        "recommendation": recommendation,
        "urgency": urgency,
        "reasoning": reasoning_steps,
        "evidence_base": {
            "guidelines": "ASRM 2024",
            "success_rates": "SART 2023 National Summary",
            "research_papers": research['papers_found']
        }
    }


def calculate_sart_success(age: int, amh: float) -> Dict[str, Any]:
    """Calculate mock SART success rates based on age and AMH."""
    # Base rates by age (mock data based on SART trends)
    base_rates = {
        'under_35': 45,
        '35_37': 35,
        '38_40': 22,
        '41_42': 12,
        'over_42': 5
    }
    
    # Determine age category
    if age < 35:
        base_rate = base_rates['under_35']
    elif age <= 37:
        base_rate = base_rates['35_37']
    elif age <= 40:
        base_rate = base_rates['38_40']
    elif age <= 42:
        base_rate = base_rates['41_42']
    else:
        base_rate = base_rates['over_42']
    
    # Adjust for AMH (simplified model)
    if amh < 0.5:
        rate = int(base_rate * 0.7)  # 30% reduction for very low AMH
    elif amh < 1.0:
        rate = int(base_rate * 0.85)  # 15% reduction for low AMH
    else:
        rate = base_rate
    
    # Calculate confidence interval
    ci_lower = max(1, rate - 4)
    ci_upper = min(rate + 4, 100)
    
    return {
        "rate": rate,
        "confidence_interval": f"{ci_lower}-{ci_upper}%",
        "age_group": f"{age} years",
        "amh_category": "very low" if amh < 1.0 else "normal"
    }


if __name__ == "__main__":
    # Test agents
    print("=== MANUS AI AGENTS TEST ===\n")
    
    # Sample patient data (preprocessed by Biomini)
    test_patient = {
        "patient_id": "P001",
        "demographics": {"age": 38, "years_trying_to_conceive": 1.5},
        "reproductive_labs": {"amh": 0.8, "fsh": 12, "lh": 8, "estradiol": 45},
        "ovarian_reserve_status": "very_low",
        "clinical_context": {
            "cycle_history": "regular, 28 days",
            "prior_ivf": "none",
            "attempts_to_conceive_months": 18
        }
    }
    
    # Test Agent 1
    print("AGENT 1: Data Retrieval")
    agent1_result = data_retrieval_agent(test_patient, "Should I do IVF now?")
    print(json.dumps(agent1_result, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test Agent 2
    print("AGENT 2: Clinical Advisor")
    agent2_result = clinical_advisor_agent(agent1_result, "Should I do IVF now?")
    print(json.dumps(agent2_result, indent=2))