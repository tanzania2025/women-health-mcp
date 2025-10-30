#!/usr/bin/env python3
"""
Women's Health Database Server - FastMCP Implementation
Provides access to ELSA (English Longitudinal Study of Ageing) datasets and metadata
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
import json

# Import ELSA server module
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
from servers import elsa_server

# Create FastMCP server
mcp = FastMCP("women-health-database")


@mcp.tool()
async def list_elsa_waves(include_details: bool = False) -> str:
    """
    List all available ELSA waves with basic information.
    
    ELSA (English Longitudinal Study of Ageing) is a longitudinal panel study
    following adults aged 50+ in England since 1998. Contains rich multidimensional
    data on health, economic circumstances, and social participation.
    
    Args:
        include_details: Include detailed information about each wave
    """
    if include_details:
        result = {
            "study": elsa_server.ELSA_FULL_NAME,
            "study_number": elsa_server.ELSA_STUDY_NUMBER,
            "total_waves": len(elsa_server.ELSA_WAVES),
            "waves": elsa_server.ELSA_WAVES
        }
    else:
        result = {
            "study": elsa_server.ELSA_FULL_NAME,
            "total_waves": len(elsa_server.ELSA_WAVES),
            "waves": [
                {
                    "wave": v["wave"],
                    "name": v["name"],
                    "year": v["year"]
                }
                for v in elsa_server.ELSA_WAVES.values()
            ]
        }

    return json.dumps(result, indent=2)


@mcp.tool()
async def get_wave_details(wave: str) -> str:
    """
    Get detailed information about a specific ELSA wave.
    
    Args:
        wave: Wave number (0-11) or 'latest' for most recent wave
    """
    if wave == "latest":
        wave = "11"

    if wave not in elsa_server.ELSA_WAVES:
        return json.dumps({
            "error": f"Wave {wave} not found. Available waves: 0-11"
        }, indent=2)

    wave_info = elsa_server.ELSA_WAVES[wave].copy()
    wave_info["ukds_url"] = f"{elsa_server.UKDS_BASE_URL}/datacatalogue/studies/study?id={elsa_server.ELSA_STUDY_NUMBER}"
    wave_info["project_url"] = f"{elsa_server.ELSA_PROJECT_URL}/data-and-documentation"

    return json.dumps(wave_info, indent=2)


@mcp.tool()
async def search_data_modules(query: str, module: Optional[str] = None) -> str:
    """
    Search ELSA data modules and variables by topic or keyword.
    
    ELSA contains multiple data modules covering different aspects of aging:
    health, cognitive function, mental health, biomarkers, economic circumstances,
    work/retirement, social networks, family relationships, and health behaviors.
    
    Args:
        query: Search term (e.g., 'cognitive', 'depression', 'wealth', 'menopause')
        module: Specific module to search (optional)
    """
    query_lower = query.lower()
    results = []

    modules_to_search = {module: elsa_server.ELSA_DATA_MODULES[module]} if module else elsa_server.ELSA_DATA_MODULES

    for mod_id, mod_data in modules_to_search.items():
        # Search in name, description, and variables
        searchable_text = f"{mod_data['name']} {mod_data['description']} {' '.join(mod_data['variables'])}".lower()

        if query_lower in searchable_text:
            results.append({
                "module_id": mod_id,
                "module_name": mod_data["name"],
                "description": mod_data["description"],
                "relevant_variables": [v for v in mod_data["variables"] if query_lower in v.lower()]
            })

    return json.dumps({
        "query": query,
        "results_found": len(results),
        "modules": results
    }, indent=2)


@mcp.tool()
async def get_data_module_info(module: str) -> str:
    """
    Get detailed information about a specific ELSA data module.
    
    Available modules: health, cognitive, mental_health, biomarkers, economic,
    work, social, family, lifestyle, expectations
    
    Args:
        module: Module identifier
    """
    if module not in elsa_server.ELSA_DATA_MODULES:
        return json.dumps({
            "error": f"Module '{module}' not found. Available modules: {list(elsa_server.ELSA_DATA_MODULES.keys())}"
        }, indent=2)

    module_info = elsa_server.ELSA_DATA_MODULES[module].copy()
    module_info["module_id"] = module

    return json.dumps(module_info, indent=2)


@mcp.tool()
async def get_access_information(detailed: bool = True) -> str:
    """
    Get information on how to access ELSA data from UK Data Service.
    
    ELSA data is freely available to researchers through the UK Data Service
    after registration. Includes step-by-step access instructions and
    programmatic access options.
    
    Args:
        detailed: Include detailed step-by-step access instructions
    """
    access_info = {
        "study": elsa_server.ELSA_FULL_NAME,
        "study_number": elsa_server.ELSA_STUDY_NUMBER,
        "data_provider": "UK Data Service (UKDS)",
        "access_url": f"{elsa_server.UKDS_BASE_URL}/datacatalogue/studies/study?id={elsa_server.ELSA_STUDY_NUMBER}",
        "contact_email": elsa_server.ELSA_DATA_EMAIL,
        "registration_required": True,
        "access_levels": {
            "open": "Some datasets available without registration",
            "safeguarded": "Most ELSA data - requires UKDS registration",
            "controlled": "Sensitive data - requires SecureLab access"
        }
    }

    if detailed:
        access_info["access_steps"] = [
            {
                "step": 1,
                "action": "Register with UK Data Service",
                "url": "https://ukdataservice.ac.uk/",
                "notes": "UK academics can use institutional login (UKAMF). Others can create free account."
            },
            {
                "step": 2,
                "action": "Search for ELSA data",
                "url": f"{elsa_server.UKDS_BASE_URL}/datacatalogue/studies/study?id={elsa_server.ELSA_STUDY_NUMBER}",
                "notes": f"Study Number: SN {elsa_server.ELSA_STUDY_NUMBER} - English Longitudinal Study of Ageing: Waves 0-11"
            },
            {
                "step": 3,
                "action": "Review data documentation",
                "notes": "Check questionnaires, user guides, and data dictionaries"
            },
            {
                "step": 4,
                "action": "Accept End User License",
                "notes": "Agree to terms of use for data access"
            },
            {
                "step": 5,
                "action": "Download data",
                "notes": "Available formats: SPSS, Stata, tab-delimited"
            }
        ]

        access_info["programmatic_access"] = {
            "r_package": {
                "name": "ukds",
                "description": "R package for downloading UKDS datasets programmatically",
                "repository": "CRAN"
            },
            "python_package": {
                "name": "ukds",
                "description": "Python package for working with UKDS datasets",
                "repository": "PyPI"
            }
        }

        access_info["controlled_data_access"] = {
            "method": "UK Data Service SecureLab",
            "description": "Remote access safe environment for sensitive data",
            "requirements": "Separate application required",
            "url": "https://ukdataservice.ac.uk/help/secure-lab/"
        }

    return json.dumps(access_info, indent=2)


@mcp.tool()
async def get_study_metadata() -> str:
    """
    Get comprehensive metadata about the ELSA study.
    
    Returns complete study information including principal investigators,
    funding, design, data collection methods, and citation information.
    """
    metadata = {
        "study_name": elsa_server.ELSA_FULL_NAME,
        "study_number": elsa_server.ELSA_STUDY_NUMBER,
        "principal_investigators": [
            "Professor Andrew Steptoe (University College London)",
            "Dr. Daisy Fancourt (University College London)"
        ],
        "funding": "National Institute on Aging (NIA), UK Government departments",
        "study_design": "Longitudinal panel study",
        "target_population": "Adults aged 50 and over living in England",
        "baseline_year": 1998,
        "total_waves": len(elsa_server.ELSA_WAVES),
        "latest_wave": 11,
        "latest_fieldwork": "2023-2024",
        "data_collection_modes": [
            "Face-to-face computer-assisted interviews",
            "Self-completion questionnaires",
            "Nurse visits (selected waves)",
            "Biomarker collection"
        ],
        "key_domains": list(elsa_server.ELSA_DATA_MODULES.keys()),
        "geographic_coverage": "England (representative sample)",
        "data_formats": ["SPSS", "Stata", "Tab-delimited"],
        "citation": f"NatCen Social Research, University College London, Institute for Fiscal Studies. (2024). English Longitudinal Study of Ageing. [data collection]. UK Data Service. SN: {elsa_server.ELSA_STUDY_NUMBER}, DOI: 10.5255/UKDA-SN-{elsa_server.ELSA_STUDY_NUMBER}-25",
        "project_website": elsa_server.ELSA_PROJECT_URL,
        "documentation_url": f"{elsa_server.ELSA_PROJECT_URL}/data-and-documentation",
        "ukds_url": f"{elsa_server.UKDS_BASE_URL}/datacatalogue/studies/study?id={elsa_server.ELSA_STUDY_NUMBER}"
    }

    return json.dumps(metadata, indent=2)


@mcp.tool()
async def get_documentation_links(wave: Optional[str] = None, doc_type: str = "all") -> str:
    """
    Get links to ELSA documentation, questionnaires, and user guides.
    
    Args:
        wave: Specific wave number (optional, returns all if not specified)
        doc_type: Type of documentation (questionnaire, user_guide, technical, data_dictionary, all)
    """
    base_docs = {
        "main_project_site": elsa_server.ELSA_PROJECT_URL,
        "data_documentation": f"{elsa_server.ELSA_PROJECT_URL}/data-and-documentation",
        "ukds_catalogue": f"{elsa_server.UKDS_BASE_URL}/datacatalogue/studies/study?id={elsa_server.ELSA_STUDY_NUMBER}",
        "user_guides": f"{elsa_server.ELSA_PROJECT_URL}/data-and-documentation",
        "questionnaires": f"{elsa_server.ELSA_PROJECT_URL}/data-and-documentation",
        "technical_reports": f"{elsa_server.ELSA_PROJECT_URL}/publications",
        "data_dictionaries": "Available via UKDS download",
        "faqs": f"{elsa_server.ELSA_PROJECT_URL}/frequently-asked-questions"
    }

    result = {
        "study": elsa_server.ELSA_FULL_NAME,
        "documentation_links": base_docs,
        "contact": {
            "data_queries": elsa_server.ELSA_DATA_EMAIL,
            "general_enquiries": f"{elsa_server.ELSA_PROJECT_URL}/contact"
        },
        "notes": [
            "Detailed wave-specific documentation available after UKDS registration",
            "User guides include variable derivations and technical details",
            "Questionnaires show exact wording of questions asked"
        ]
    }

    if wave:
        result["wave"] = wave
        result["note"] = f"Wave {wave} specific documentation available via UKDS after registration"

    return json.dumps(result, indent=2)


@mcp.tool()
async def compare_waves(waves: list[str], focus: str = "all") -> str:
    """
    Compare variables and topics across multiple ELSA waves.
    
    Args:
        waves: List of wave numbers to compare (e.g., ['1', '5', '9'])
        focus: Specific aspect to focus comparison on (topics, sample_size, all)
    """
    if not waves:
        return json.dumps({"error": "No waves specified for comparison"}, indent=2)

    comparison = {
        "waves_compared": waves,
        "comparison": {}
    }

    for wave in waves:
        if wave not in elsa_server.ELSA_WAVES:
            comparison["comparison"][wave] = {"error": "Wave not found"}
            continue

        wave_data = elsa_server.ELSA_WAVES[wave]

        if focus == "all" or focus == "topics":
            comparison["comparison"][wave] = {
                "name": wave_data["name"],
                "year": wave_data["year"],
                "key_topics": wave_data["key_topics"]
            }

        if focus == "all" or focus == "sample_size":
            if wave not in comparison["comparison"]:
                comparison["comparison"][wave] = {}
            comparison["comparison"][wave]["sample_size"] = wave_data["sample_size"]
            comparison["comparison"][wave]["fieldwork_period"] = wave_data["fieldwork_period"]

    return json.dumps(comparison, indent=2)


@mcp.tool()
async def get_research_examples(topic: str = "general") -> str:
    """
    Get examples of research questions that can be answered with ELSA data.
    
    Provides research question examples and analysis possibilities for different
    topic areas including health, economics, mental health, COVID-19, and biomarkers.
    
    Args:
        topic: Research topic area (general, health, economic, mental_health, covid, biomarkers)
    """
    research_examples = {
        "general": [
            "How does health change with age in the English population?",
            "What are the predictors of successful aging?",
            "How do social determinants affect health outcomes in older adults?"
        ],
        "health": [
            "What is the trajectory of cognitive decline in aging?",
            "How do chronic conditions cluster in older adults?",
            "What factors predict disability-free life expectancy?"
        ],
        "economic": [
            "How does wealth accumulation vary across cohorts?",
            "What is the relationship between pension adequacy and well-being?",
            "How does retirement affect health and cognitive function?"
        ],
        "mental_health": [
            "What are the prevalence and predictors of depression in older age?",
            "How does social isolation affect mental health trajectories?",
            "What role does social support play in resilience to life stressors?"
        ],
        "covid": [
            "How did COVID-19 affect mental health in older adults?",
            "What were the health behavior changes during the pandemic?",
            "How did social isolation during lockdowns affect cognitive function?"
        ],
        "biomarkers": [
            "How do biological markers relate to subjective health ratings?",
            "What is the relationship between inflammation and cognitive aging?",
            "How do health behaviors affect biomarker profiles?"
        ]
    }

    examples = research_examples.get(topic.lower(), research_examples["general"])

    result = {
        "topic": topic,
        "research_questions": examples,
        "data_strengths": [
            "Longitudinal design allows for causal inference",
            "Rich multidimensional data (health, economic, social)",
            "Biomarker data in selected waves",
            "Large representative sample of English adults 50+",
            "Long follow-up period (1998-2024)"
        ],
        "analysis_possibilities": [
            "Longitudinal modeling of change over time",
            "Cross-sectional comparisons across age groups",
            "Life course epidemiology",
            "Health inequality research",
            "Policy evaluation studies"
        ]
    }

    return json.dumps(result, indent=2)


# Run the server
if __name__ == "__main__":
    mcp.run()