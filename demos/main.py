#!/usr/bin/env python3
"""
Women's Health MCP - Main Demo Entry Point
Demonstrates clinical decision support for fertility questions
"""

from core.biomini_intake import ingest_patient, SAMPLE_PATIENT_1, SAMPLE_PATIENT_2
from core.netmind_router import orchestrate_query
from core.manus_agents import data_retrieval_agent, clinical_advisor_agent
from core.huggingface_integration import rank_papers_by_relevance, load_biomedical_model
from demos.end_to_end_demo import run_full_pipeline


def main():
    """Run the Women's Health MCP demo."""
    
    # Display welcome message
    print("\n" + "="*70)
    print("     WOMEN'S HEALTH MCP - CLINICAL DECISION SUPPORT DEMO")
    print("     Hackathon Demo: AI-Powered Fertility Consultation")
    print("="*70)
    
    # Demo scenario 1: 38-year-old with low AMH considering IVF
    print("\n📋 DEMO SCENARIO 1: IVF Decision Support")
    print("Patient: 38-year-old woman, AMH 0.8 ng/mL, trying for 18 months")
    print("Question: 'I have AMH 0.8, should I do IVF now?'")
    
    input("\n➡️  Press Enter to run the clinical decision pipeline...")
    
    # Run the pipeline
    result = run_full_pipeline(
        SAMPLE_PATIENT_1,
        "I have AMH 0.8, should I do IVF now?"
    )
    
    # Optional: Show second demo
    print("\n" + "="*70)
    response = input("\n🔄 Would you like to see another patient scenario? (y/n): ")
    
    if response.lower() == 'y':
        print("\n📋 DEMO SCENARIO 2: Approaching Menopause")
        print("Patient: 45-year-old woman, AMH 0.3 ng/mL, irregular cycles")
        print("Question: 'Am I too late for IVF? What are my options?'")
        
        input("\n➡️  Press Enter to run the analysis...")
        
        result2 = run_full_pipeline(
            SAMPLE_PATIENT_2,
            "Am I too late for IVF? What are my options?"
        )
    
    print("\n✅ Demo completed successfully!")
    print("🏆 This MCP demonstrates:")
    print("   • Real-time patient data ingestion (Biomini)")
    print("   • Intelligent query routing (Netmind)")
    print("   • Multi-agent clinical reasoning (Manus AI)")
    print("   • Evidence-based recommendations with research ranking")
    print("   • Impact: Democratizing fertility expertise for women's longevity")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()


"""
EXPECTED OUTPUT EXAMPLE:
========================

╔════════════════════════════════════════════════════════════
  WOMEN'S HEALTH MCP - CLINICAL DECISION SUPPORT
╚════════════════════════════════════════════════════════════

Clinical Question: I have AMH 0.8, should I do IVF now?
Patient ID: P001

▶════════════════════════════════════════════════════════════
  [BIOMINI] Ingesting patient data...
▶════════════════════════════════════════════════════════════

✓ Patient Age: 38 years
✓ AMH Level: 0.8 ng/mL
✓ Ovarian Reserve Status: VERY_LOW
✓ Years Trying to Conceive: 1.5

▶════════════════════════════════════════════════════════════
  [NETMIND] Routing query...
▶════════════════════════════════════════════════════════════

Query Type: fertility_query
Priority: high

Data Sources to Query:
  → biomini_patient_context
  → huggingface_research
  → sart_database

Agents to Activate:
  → data_retrieval_agent
  → clinical_advisor_agent

▶════════════════════════════════════════════════════════════
  [MANUS AI] Orchestrating agents...
▶════════════════════════════════════════════════════════════

→ Activating Data Retrieval Agent...
  ✓ Patient profile analyzed
  ✓ Found 5 relevant research papers
  ✓ Key concern identified: Low ovarian reserve

▶════════════════════════════════════════════════════════════
  [HUGGING FACE] Ranking research by relevance...
▶════════════════════════════════════════════════════════════

Top relevant research:
  1. [0.80] IVF success in low AMH: what we learned (2023)
  2. [0.70] AMH levels and reproductive outcomes: systematic review (2024)
  3. [0.50] Optimizing IVF protocols for diminished ovarian reserve (2023)

★════════════════════════════════════════════════════════════
  [OUTPUT] Clinical Recommendation
★════════════════════════════════════════════════════════════

RECOMMENDATION:
--------------------------------------------------
Your AMH level (0.8 ng/mL) indicates diminished ovarian reserve. We recommend 
scheduling a fertility consultation within 1-2 months. SART data shows 19% 
success rate for your profile. Recent research shows that with optimized 
protocols, low AMH patients can achieve good outcomes.
--------------------------------------------------

CLINICAL REASONING:
  1. Patient age (38) and AMH (0.8) analyzed
  2. Ovarian reserve classified as: very_low
  3. ASRM guideline applied: ASRM recommends expedited fertility evaluation for AMH <1.0 ng/mL
  4. SART success rate calculated: 19% (CI: 15-23%)
  5. Research consensus: Low AMH indicates reduced ovarian reserve but does not preclude IVF success
  6. Urgency level determined: expedited

EVIDENCE BASE:
  • Guidelines: ASRM 2024
  • Success Rates: SART 2023 National Summary
  • Research Papers Reviewed: 5

╚════════════════════════════════════════════════════════════
  Pipeline execution complete!
╚════════════════════════════════════════════════════════════
"""