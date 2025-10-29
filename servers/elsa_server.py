#!/usr/bin/env python3
"""
ELSA (English Longitudinal Study of Ageing) MCP Server - FastMCP Implementation

Provides structured real-time access to ELSA data information, metadata, and documentation.
Data source: UK Data Service (UKDS) - Study Number SN 5050

Features:
- Browse available ELSA waves and datasets
- Search variables and documentation
- Access study metadata and questionnaires
- Get information on data access procedures
- Optional integration with UKDS download service
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastmcp import FastMCP
from pydantic import Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("elsa-server")

# ELSA Data Constants
ELSA_STUDY_NUMBER = "5050"
ELSA_FULL_NAME = "English Longitudinal Study of Ageing"
UKDS_BASE_URL = "https://beta.ukdataservice.ac.uk"
ELSA_PROJECT_URL = "https://www.elsa-project.ac.uk"
ELSA_DATA_EMAIL = "ELSAdata@natcen.ac.uk"

# ELSA Wave Information (based on available data as of 2024)
ELSA_WAVES = {
    "0": {
        "wave": 0,
        "year": "1998, 1999, 2001",
        "name": "Health Survey for England (HSE)",
        "description": "Baseline wave from Health Survey for England cohort",
        "sample_size": "~11,000 core members",
        "key_topics": ["Health status", "Disability", "Health behaviors", "Anthropometry"],
        "fieldwork_period": "1998-2001"
    },
    "1": {
        "wave": 1,
        "year": "2002-2003",
        "name": "Wave 1",
        "description": "First ELSA wave with detailed interviews",
        "sample_size": "~12,000 respondents",
        "key_topics": ["Health", "Economic circumstances", "Social participation", "Biomarkers"],
        "fieldwork_period": "2002-2003"
    },
    "2": {
        "wave": 2,
        "year": "2004-2005",
        "name": "Wave 2",
        "description": "Follow-up wave",
        "sample_size": "~9,400 respondents",
        "key_topics": ["Health trajectories", "Retirement", "Wealth", "Expectations"],
        "fieldwork_period": "2004-2005"
    },
    "3": {
        "wave": 3,
        "year": "2006-2007",
        "name": "Wave 3",
        "description": "Third wave with nurse visit",
        "sample_size": "~9,700 respondents",
        "key_topics": ["Cognitive function", "Biomarkers", "Physical function", "Mental health"],
        "fieldwork_period": "2006-2007"
    },
    "4": {
        "wave": 4,
        "year": "2008-2009",
        "name": "Wave 4",
        "description": "Fourth wave",
        "sample_size": "~11,000 respondents",
        "key_topics": ["Health", "Work", "Income", "Quality of life"],
        "fieldwork_period": "2008-2009"
    },
    "5": {
        "wave": 5,
        "year": "2010-2011",
        "name": "Wave 5",
        "description": "Fifth wave with refreshment sample",
        "sample_size": "~10,200 respondents",
        "key_topics": ["Ageing", "Health service use", "Social networks", "Biomarkers"],
        "fieldwork_period": "2010-2011"
    },
    "6": {
        "wave": 6,
        "year": "2012-2013",
        "name": "Wave 6",
        "description": "Sixth wave with nurse visit",
        "sample_size": "~10,600 respondents",
        "key_topics": ["Life course", "Health", "Cognitive ageing", "Physical measurements"],
        "fieldwork_period": "2012-2013"
    },
    "7": {
        "wave": 7,
        "year": "2014-2015",
        "name": "Wave 7",
        "description": "Seventh wave",
        "sample_size": "~9,600 respondents",
        "key_topics": ["Healthy ageing", "Employment", "Financial planning", "Well-being"],
        "fieldwork_period": "2014-2015"
    },
    "8": {
        "wave": 8,
        "year": "2016-2017",
        "name": "Wave 8",
        "description": "Eighth wave with nurse visit",
        "sample_size": "~9,600 respondents",
        "key_topics": ["Biological ageing", "Dementia", "Frailty", "Biomarkers"],
        "fieldwork_period": "2016-2017"
    },
    "9": {
        "wave": 9,
        "year": "2018-2019",
        "name": "Wave 9",
        "description": "Ninth wave",
        "sample_size": "~9,300 respondents",
        "key_topics": ["Health", "Social care", "Retirement", "Internet use"],
        "fieldwork_period": "2018-2019"
    },
    "10": {
        "wave": 10,
        "year": "2020-2021",
        "name": "Wave 10 (COVID-19)",
        "description": "Tenth wave conducted during COVID-19 pandemic",
        "sample_size": "~8,500 respondents",
        "key_topics": ["COVID-19 impact", "Mental health", "Social isolation", "Health behaviors"],
        "fieldwork_period": "2020-2021",
        "notes": "Modified data collection due to pandemic"
    },
    "11": {
        "wave": 11,
        "year": "2023-2024",
        "name": "Wave 11",
        "description": "Most recent wave (fieldwork started October 2023)",
        "sample_size": "TBD",
        "key_topics": ["Post-pandemic health", "Long COVID", "Economic recovery", "Well-being"],
        "fieldwork_period": "2023-2024",
        "notes": "Data available on UKDS (without survey weights)"
    }
}

# Key ELSA Data Modules
ELSA_DATA_MODULES = {
    "health": {
        "name": "Health and Disability",
        "variables": ["Self-rated health", "Chronic conditions", "Pain", "Vision", "Hearing", "ADL/IADL"],
        "description": "Physical health status, disabilities, and functional limitations"
    },
    "cognitive": {
        "name": "Cognitive Function",
        "variables": ["Memory tests", "Verbal fluency", "Processing speed", "Executive function"],
        "description": "Cognitive assessments including memory, reasoning, and processing"
    },
    "mental_health": {
        "name": "Mental Health",
        "variables": ["Depression (CES-D)", "Anxiety", "Life satisfaction", "Quality of life"],
        "description": "Mental health indicators and psychological well-being"
    },
    "biomarkers": {
        "name": "Biomarkers (Nurse Visit)",
        "variables": ["Blood pressure", "Blood samples", "Lung function", "Grip strength", "Anthropometry"],
        "description": "Objective health measures collected by nurses"
    },
    "economic": {
        "name": "Economic Circumstances",
        "variables": ["Income", "Wealth", "Pensions", "Benefits", "Debt", "Housing"],
        "description": "Financial resources, assets, and economic well-being"
    },
    "work": {
        "name": "Work and Retirement",
        "variables": ["Employment status", "Job characteristics", "Retirement planning", "Work history"],
        "description": "Employment patterns and retirement transitions"
    },
    "social": {
        "name": "Social Networks and Participation",
        "variables": ["Social contacts", "Social activities", "Loneliness", "Civic engagement"],
        "description": "Social relationships, activities, and community involvement"
    },
    "family": {
        "name": "Family and Relationships",
        "variables": ["Marital status", "Children", "Grandchildren", "Caregiving"],
        "description": "Family structure and intergenerational relationships"
    },
    "lifestyle": {
        "name": "Health Behaviors",
        "variables": ["Smoking", "Alcohol", "Physical activity", "Diet", "Sleep"],
        "description": "Health-related behaviors and lifestyle factors"
    },
    "expectations": {
        "name": "Expectations and Attitudes",
        "variables": ["Life expectancy", "Future health", "Economic expectations"],
        "description": "Subjective expectations about future outcomes"
    }
}

# Create FastMCP server
mcp = FastMCP("elsa-server")


# ==================== FastMCP Tools ====================

@mcp.tool()
def list_elsa_waves(
    include_details: bool = Field(False, description="Include detailed information about each wave")
) -> str:
    """
    List all available ELSA waves with basic information.
    """
    if include_details:
        result = f"# {ELSA_FULL_NAME}\n\n"
        result += f"**Study Number:** {ELSA_STUDY_NUMBER}\n"
        result += f"**Total Waves:** {len(ELSA_WAVES)}\n\n"
        
        for wave_id, wave_data in ELSA_WAVES.items():
            result += f"## Wave {wave_data['wave']}: {wave_data['name']}\n"
            result += f"**Year:** {wave_data['year']}\n"
            result += f"**Sample Size:** {wave_data['sample_size']}\n"
            result += f"**Fieldwork Period:** {wave_data['fieldwork_period']}\n"
            result += f"**Description:** {wave_data['description']}\n"
            result += f"**Key Topics:** {', '.join(wave_data['key_topics'])}\n"
            if 'notes' in wave_data:
                result += f"**Notes:** {wave_data['notes']}\n"
            result += "\n"
    else:
        result = f"# {ELSA_FULL_NAME}\n\n"
        result += f"**Total Waves:** {len(ELSA_WAVES)}\n\n"
        
        for wave_id, wave_data in ELSA_WAVES.items():
            result += f"- **Wave {wave_data['wave']}:** {wave_data['name']} ({wave_data['year']})\n"
    
    return result


@mcp.tool()
def get_wave_details(
    wave: str = Field(description="Wave number (0-11) or 'latest' for most recent wave")
) -> str:
    """
    Get detailed information about a specific ELSA wave.
    """
    if wave == "latest":
        wave = "11"
    
    if wave not in ELSA_WAVES:
        return f"**Error:** Wave {wave} not found. Available waves: 0-11"
    
    wave_data = ELSA_WAVES[wave]
    
    result = f"# {wave_data['name']}\n\n"
    result += f"**Wave:** {wave_data['wave']}\n"
    result += f"**Year:** {wave_data['year']}\n"
    result += f"**Sample Size:** {wave_data['sample_size']}\n"
    result += f"**Fieldwork Period:** {wave_data['fieldwork_period']}\n"
    result += f"**Description:** {wave_data['description']}\n\n"
    
    result += f"**Key Topics:**\n"
    for topic in wave_data['key_topics']:
        result += f"- {topic}\n"
    
    if 'notes' in wave_data:
        result += f"\n**Notes:** {wave_data['notes']}\n"
    
    result += f"\n**Data Access:**\n"
    result += f"- UKDS URL: {UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}\n"
    result += f"- Project URL: {ELSA_PROJECT_URL}/data-and-documentation\n"
    
    return result


@mcp.tool()
def search_data_modules(
    query: str = Field(description="Search term (e.g., 'cognitive', 'depression', 'wealth')"),
    module: Optional[str] = Field(None, description="Specific module to search (optional)")
) -> str:
    """
    Search ELSA data modules and variables by topic or keyword.
    """
    results = []
    modules_to_search = {module: ELSA_DATA_MODULES[module]} if module and module in ELSA_DATA_MODULES else ELSA_DATA_MODULES
    
    for mod_id, mod_data in modules_to_search.items():
        searchable_text = f"{mod_data['name']} {mod_data['description']} {' '.join(mod_data['variables'])}".lower()
        
        if query.lower() in searchable_text:
            relevant_vars = [v for v in mod_data['variables'] if query.lower() in v.lower()]
            results.append({
                'id': mod_id,
                'name': mod_data['name'],
                'description': mod_data['description'],
                'relevant_variables': relevant_vars
            })
    
    result = f"# Search Results for '{query}'\n\n"
    result += f"**Results Found:** {len(results)}\n\n"
    
    if not results:
        result += "No matching modules found. Try different keywords or browse all modules with get_data_module_info.\n"
        result += f"\n**Available modules:** {', '.join(ELSA_DATA_MODULES.keys())}\n"
        return result
    
    for i, res in enumerate(results, 1):
        result += f"## {i}. {res['name']} ({res['id']})\n"
        result += f"{res['description']}\n\n"
        
        if res['relevant_variables']:
            result += f"**Relevant Variables:**\n"
            for var in res['relevant_variables']:
                result += f"- {var}\n"
        result += "\n"
    
    return result


@mcp.tool()
def get_data_module_info(
    module: str = Field(description="Module identifier")
) -> str:
    """
    Get detailed information about a specific ELSA data module.
    """
    if module not in ELSA_DATA_MODULES:
        return f"**Error:** Module '{module}' not found. Available modules: {', '.join(ELSA_DATA_MODULES.keys())}"
    
    mod_data = ELSA_DATA_MODULES[module]
    
    result = f"# {mod_data['name']}\n\n"
    result += f"**Module ID:** {module}\n"
    result += f"**Description:** {mod_data['description']}\n\n"
    
    result += f"**Variables Include:**\n"
    for var in mod_data['variables']:
        result += f"- {var}\n"
    
    return result


@mcp.tool()
def get_access_information(
    detailed: bool = Field(True, description="Include detailed step-by-step access instructions")
) -> str:
    """
    Get information on how to access ELSA data from UK Data Service.
    """
    result = f"# {ELSA_FULL_NAME} Data Access\n\n"
    result += f"**Study Number:** {ELSA_STUDY_NUMBER}\n"
    result += f"**Data Provider:** UK Data Service (UKDS)\n"
    result += f"**Contact:** {ELSA_DATA_EMAIL}\n"
    result += f"**Access URL:** {UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}\n\n"
    
    result += f"**Access Levels:**\n"
    result += f"- **Open:** Some datasets available without registration\n"
    result += f"- **Safeguarded:** Most ELSA data - requires UKDS registration\n"
    result += f"- **Controlled:** Sensitive data - requires SecureLab access\n\n"
    
    if detailed:
        result += f"## Step-by-Step Access Instructions\n\n"
        
        steps = [
            ("Register with UK Data Service", "https://ukdataservice.ac.uk/", "UK academics can use institutional login (UKAMF). Others can create free account."),
            ("Search for ELSA data", f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}", "Study Number: SN 5050 - English Longitudinal Study of Ageing: Waves 0-11"),
            ("Review data documentation", None, "Check questionnaires, user guides, and data dictionaries"),
            ("Accept End User License", None, "Agree to terms of use for data access"),
            ("Download data", None, "Available formats: SPSS, Stata, tab-delimited")
        ]
        
        for i, (action, url, notes) in enumerate(steps, 1):
            result += f"**{i}. {action}**\n"
            if url:
                result += f"   - URL: {url}\n"
            result += f"   - {notes}\n\n"
        
        result += f"## Programmatic Access\n\n"
        result += f"**R Package:**\n"
        result += f"- Package: ukds (available on CRAN)\n"
        result += f"- Description: R package for downloading UKDS datasets programmatically\n\n"
        
        result += f"**Python Package:**\n"
        result += f"- Package: ukds (available on PyPI)\n"
        result += f"- Description: Python package for working with UKDS datasets\n\n"
        
        result += f"## Controlled Data Access\n\n"
        result += f"**Method:** UK Data Service SecureLab\n"
        result += f"**Description:** Remote access safe environment for sensitive data\n"
        result += f"**Requirements:** Separate application required\n"
        result += f"**URL:** https://ukdataservice.ac.uk/help/secure-lab/\n"
    
    return result


@mcp.tool()
def get_study_metadata() -> str:
    """
    Get comprehensive metadata about the ELSA study.
    """
    result = f"# {ELSA_FULL_NAME} Metadata\n\n"
    
    result += f"**Study Number:** {ELSA_STUDY_NUMBER}\n"
    result += f"**Principal Investigators:**\n"
    result += f"- Professor Andrew Steptoe (University College London)\n"
    result += f"- Dr. Daisy Fancourt (University College London)\n\n"
    
    result += f"**Study Design:** Longitudinal panel study\n"
    result += f"**Target Population:** Adults aged 50 and over living in England\n"
    result += f"**Geographic Coverage:** England (representative sample)\n"
    result += f"**Baseline Year:** 1998\n"
    result += f"**Total Waves:** {len(ELSA_WAVES)}\n"
    result += f"**Latest Wave:** 11\n"
    result += f"**Latest Fieldwork:** 2023-2024\n\n"
    
    result += f"**Funding:** National Institute on Aging (NIA), UK Government departments\n\n"
    
    result += f"**Data Collection Modes:**\n"
    modes = ["Face-to-face computer-assisted interviews", "Self-completion questionnaires", "Nurse visits (selected waves)", "Biomarker collection"]
    for mode in modes:
        result += f"- {mode}\n"
    result += "\n"
    
    result += f"**Key Data Domains:**\n"
    for domain in ELSA_DATA_MODULES.keys():
        result += f"- {domain}\n"
    result += "\n"
    
    result += f"**Data Formats:** SPSS, Stata, Tab-delimited\n\n"
    
    result += f"**Citation:**\n"
    result += f"NatCen Social Research, University College London, Institute for Fiscal Studies. (2024). English Longitudinal Study of Ageing. [data collection]. UK Data Service. SN: {ELSA_STUDY_NUMBER}, DOI: 10.5255/UKDA-SN-{ELSA_STUDY_NUMBER}-25\n\n"
    
    result += f"**Links:**\n"
    result += f"- Project Website: {ELSA_PROJECT_URL}\n"
    result += f"- Documentation: {ELSA_PROJECT_URL}/data-and-documentation\n"
    result += f"- UKDS Catalogue: {UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}\n"
    
    return result


@mcp.tool()
def get_documentation_links(
    wave: Optional[str] = Field(None, description="Specific wave number (optional, returns all if not specified)"),
    doc_type: Optional[str] = Field("all", description="Type of documentation")
) -> str:
    """
    Get links to ELSA documentation, questionnaires, and user guides.
    """
    result = f"# {ELSA_FULL_NAME} Documentation Links\n\n"
    
    if wave:
        result += f"**Wave {wave} Documentation**\n\n"
    
    result += f"**Main Documentation Links:**\n"
    result += f"- Main Project Site: {ELSA_PROJECT_URL}\n"
    result += f"- Data Documentation: {ELSA_PROJECT_URL}/data-and-documentation\n"
    result += f"- UKDS Catalogue: {UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}\n"
    result += f"- User Guides: {ELSA_PROJECT_URL}/data-and-documentation\n"
    result += f"- Questionnaires: {ELSA_PROJECT_URL}/data-and-documentation\n"
    result += f"- Technical Reports: {ELSA_PROJECT_URL}/publications\n"
    result += f"- Data Dictionaries: Available via UKDS download\n"
    result += f"- FAQs: {ELSA_PROJECT_URL}/frequently-asked-questions\n\n"
    
    result += f"**Contact Information:**\n"
    result += f"- Data Queries: {ELSA_DATA_EMAIL}\n"
    result += f"- General Enquiries: {ELSA_PROJECT_URL}/contact\n\n"
    
    result += f"**Important Notes:**\n"
    result += f"- Detailed wave-specific documentation available after UKDS registration\n"
    result += f"- User guides include variable derivations and technical details\n"
    result += f"- Questionnaires show exact wording of questions asked\n"
    
    if wave:
        result += f"\n**Note:** Wave {wave} specific documentation available via UKDS after registration\n"
    
    return result


@mcp.tool()
def compare_waves(
    waves: List[str] = Field(description="List of wave numbers to compare (e.g., ['1', '5', '9'])"),
    focus: str = Field("all", description="Specific aspect to focus comparison on (topics, sample_size, or all)")
) -> str:
    """
    Compare variables and topics across multiple ELSA waves.
    """
    if not waves:
        return "**Error:** No waves specified for comparison"
    
    result = f"# ELSA Wave Comparison\n\n"
    result += f"**Waves Compared:** {', '.join(waves)}\n"
    result += f"**Focus:** {focus}\n\n"
    
    for wave in waves:
        if wave not in ELSA_WAVES:
            result += f"## Wave {wave}\n**Error:** Wave not found\n\n"
            continue
        
        wave_data = ELSA_WAVES[wave]
        
        result += f"## Wave {wave}: {wave_data['name']}\n"
        result += f"**Year:** {wave_data['year']}\n"
        
        if focus in ["all", "sample_size"]:
            result += f"**Sample Size:** {wave_data['sample_size']}\n"
            result += f"**Fieldwork Period:** {wave_data['fieldwork_period']}\n"
        
        if focus in ["all", "topics"]:
            result += f"**Key Topics:**\n"
            for topic in wave_data['key_topics']:
                result += f"- {topic}\n"
        
        if 'notes' in wave_data:
            result += f"**Notes:** {wave_data['notes']}\n"
        
        result += "\n"
    
    return result


@mcp.tool()
def get_research_examples(
    topic: Optional[str] = Field(None, description="Research topic area (optional)")
) -> str:
    """
    Get examples of research questions that can be answered with ELSA data.
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
    
    topic = (topic or "general").lower()
    examples = research_examples.get(topic, research_examples["general"])
    
    result = f"# Research Examples - {topic.title()} Topic\n\n"
    
    result += f"**Example Research Questions:**\n"
    for i, question in enumerate(examples, 1):
        result += f"{i}. {question}\n"
    
    result += f"\n**ELSA Data Strengths:**\n"
    strengths = [
        "Longitudinal design allows for causal inference",
        "Rich multidimensional data (health, economic, social)",
        "Biomarker data in selected waves",
        "Large representative sample of English adults 50+",
        "Long follow-up period (1998-2024)"
    ]
    for strength in strengths:
        result += f"- {strength}\n"
    
    result += f"\n**Analysis Possibilities:**\n"
    analyses = [
        "Longitudinal modeling of change over time",
        "Cross-sectional comparisons across age groups",
        "Life course epidemiology",
        "Health inequality research",
        "Policy evaluation studies"
    ]
    for analysis in analyses:
        result += f"- {analysis}\n"
    
    return result


# ==================== Resources ====================

@mcp.resource("elsa://metadata", mime_type="application/json")
def list_elsa_resources() -> dict:
    """List all available ELSA resources."""
    return {
        "waves": f"{len(ELSA_WAVES)} waves available (0-11)",
        "data_modules": f"{len(ELSA_DATA_MODULES)} data modules",
        "study_period": "1998-2024",
        "data_access": "UK Data Service registration required",
        "capabilities": "Search, browse, compare waves and modules"
    }


# Run the server
if __name__ == "__main__":
    mcp.run()
