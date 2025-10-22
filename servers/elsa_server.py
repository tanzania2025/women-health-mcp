#!/usr/bin/env python3
"""
ELSA (English Longitudinal Study of Ageing) MCP Server

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

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

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

# Initialize MCP server
app = Server("elsa-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available ELSA data tools."""
    return [
        types.Tool(
            name="list_elsa_waves",
            description="List all available ELSA waves with basic information",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_details": {
                        "type": "boolean",
                        "description": "Include detailed information about each wave",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="get_wave_details",
            description="Get detailed information about a specific ELSA wave",
            inputSchema={
                "type": "object",
                "properties": {
                    "wave": {
                        "type": "string",
                        "description": "Wave number (0-11) or 'latest' for most recent wave"
                    }
                },
                "required": ["wave"]
            }
        ),
        types.Tool(
            name="search_data_modules",
            description="Search ELSA data modules and variables by topic or keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'cognitive', 'depression', 'wealth')"
                    },
                    "module": {
                        "type": "string",
                        "description": "Specific module to search (optional)",
                        "enum": list(ELSA_DATA_MODULES.keys())
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_data_module_info",
            description="Get detailed information about a specific ELSA data module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module": {
                        "type": "string",
                        "description": "Module identifier",
                        "enum": list(ELSA_DATA_MODULES.keys())
                    }
                },
                "required": ["module"]
            }
        ),
        types.Tool(
            name="get_access_information",
            description="Get information on how to access ELSA data from UK Data Service",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed step-by-step access instructions",
                        "default": True
                    }
                }
            }
        ),
        types.Tool(
            name="get_study_metadata",
            description="Get comprehensive metadata about the ELSA study",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_documentation_links",
            description="Get links to ELSA documentation, questionnaires, and user guides",
            inputSchema={
                "type": "object",
                "properties": {
                    "wave": {
                        "type": "string",
                        "description": "Specific wave number (optional, returns all if not specified)"
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "Type of documentation",
                        "enum": ["questionnaire", "user_guide", "technical", "data_dictionary", "all"]
                    }
                }
            }
        ),
        types.Tool(
            name="compare_waves",
            description="Compare variables and topics across multiple ELSA waves",
            inputSchema={
                "type": "object",
                "properties": {
                    "waves": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of wave numbers to compare (e.g., ['1', '5', '9'])"
                    },
                    "focus": {
                        "type": "string",
                        "description": "Specific aspect to focus comparison on",
                        "enum": ["topics", "sample_size", "all"]
                    }
                },
                "required": ["waves"]
            }
        ),
        types.Tool(
            name="get_research_examples",
            description="Get examples of research questions that can be answered with ELSA data",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Research topic area (optional)"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
    """Handle tool calls for ELSA data access."""

    if name == "list_elsa_waves":
        include_details = arguments.get("include_details", False)

        if include_details:
            result = {
                "study": ELSA_FULL_NAME,
                "study_number": ELSA_STUDY_NUMBER,
                "total_waves": len(ELSA_WAVES),
                "waves": ELSA_WAVES
            }
        else:
            result = {
                "study": ELSA_FULL_NAME,
                "total_waves": len(ELSA_WAVES),
                "waves": [
                    {
                        "wave": v["wave"],
                        "name": v["name"],
                        "year": v["year"]
                    }
                    for v in ELSA_WAVES.values()
                ]
            }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "get_wave_details":
        wave = arguments.get("wave")

        if wave == "latest":
            wave = "11"

        if wave not in ELSA_WAVES:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Wave {wave} not found. Available waves: 0-11"
                }, indent=2)
            )]

        wave_info = ELSA_WAVES[wave].copy()
        wave_info["ukds_url"] = f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}"
        wave_info["project_url"] = f"{ELSA_PROJECT_URL}/data-and-documentation"

        return [types.TextContent(
            type="text",
            text=json.dumps(wave_info, indent=2)
        )]

    elif name == "search_data_modules":
        query = arguments.get("query", "").lower()
        module_filter = arguments.get("module")

        results = []

        modules_to_search = {module_filter: ELSA_DATA_MODULES[module_filter]} if module_filter else ELSA_DATA_MODULES

        for mod_id, mod_data in modules_to_search.items():
            # Search in name, description, and variables
            searchable_text = f"{mod_data['name']} {mod_data['description']} {' '.join(mod_data['variables'])}".lower()

            if query in searchable_text:
                results.append({
                    "module_id": mod_id,
                    "module_name": mod_data["name"],
                    "description": mod_data["description"],
                    "relevant_variables": [v for v in mod_data["variables"] if query in v.lower()]
                })

        return [types.TextContent(
            type="text",
            text=json.dumps({
                "query": query,
                "results_found": len(results),
                "modules": results
            }, indent=2)
        )]

    elif name == "get_data_module_info":
        module = arguments.get("module")

        if module not in ELSA_DATA_MODULES:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Module '{module}' not found. Available modules: {list(ELSA_DATA_MODULES.keys())}"
                }, indent=2)
            )]

        module_info = ELSA_DATA_MODULES[module].copy()
        module_info["module_id"] = module

        return [types.TextContent(
            type="text",
            text=json.dumps(module_info, indent=2)
        )]

    elif name == "get_access_information":
        detailed = arguments.get("detailed", True)

        access_info = {
            "study": ELSA_FULL_NAME,
            "study_number": ELSA_STUDY_NUMBER,
            "data_provider": "UK Data Service (UKDS)",
            "access_url": f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}",
            "contact_email": ELSA_DATA_EMAIL,
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
                    "url": f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}",
                    "notes": "Study Number: SN 5050 - English Longitudinal Study of Ageing: Waves 0-11"
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

        return [types.TextContent(
            type="text",
            text=json.dumps(access_info, indent=2)
        )]

    elif name == "get_study_metadata":
        metadata = {
            "study_name": ELSA_FULL_NAME,
            "study_number": ELSA_STUDY_NUMBER,
            "principal_investigators": [
                "Professor Andrew Steptoe (University College London)",
                "Dr. Daisy Fancourt (University College London)"
            ],
            "funding": "National Institute on Aging (NIA), UK Government departments",
            "study_design": "Longitudinal panel study",
            "target_population": "Adults aged 50 and over living in England",
            "baseline_year": 1998,
            "total_waves": len(ELSA_WAVES),
            "latest_wave": 11,
            "latest_fieldwork": "2023-2024",
            "data_collection_modes": [
                "Face-to-face computer-assisted interviews",
                "Self-completion questionnaires",
                "Nurse visits (selected waves)",
                "Biomarker collection"
            ],
            "key_domains": list(ELSA_DATA_MODULES.keys()),
            "geographic_coverage": "England (representative sample)",
            "data_formats": ["SPSS", "Stata", "Tab-delimited"],
            "citation": "NatCen Social Research, University College London, Institute for Fiscal Studies. (2024). English Longitudinal Study of Ageing. [data collection]. UK Data Service. SN: 5050, DOI: 10.5255/UKDA-SN-5050-25",
            "project_website": ELSA_PROJECT_URL,
            "documentation_url": f"{ELSA_PROJECT_URL}/data-and-documentation",
            "ukds_url": f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(metadata, indent=2)
        )]

    elif name == "get_documentation_links":
        wave = arguments.get("wave")
        doc_type = arguments.get("doc_type", "all")

        base_docs = {
            "main_project_site": ELSA_PROJECT_URL,
            "data_documentation": f"{ELSA_PROJECT_URL}/data-and-documentation",
            "ukds_catalogue": f"{UKDS_BASE_URL}/datacatalogue/studies/study?id={ELSA_STUDY_NUMBER}",
            "user_guides": f"{ELSA_PROJECT_URL}/data-and-documentation",
            "questionnaires": f"{ELSA_PROJECT_URL}/data-and-documentation",
            "technical_reports": f"{ELSA_PROJECT_URL}/publications",
            "data_dictionaries": "Available via UKDS download",
            "faqs": f"{ELSA_PROJECT_URL}/frequently-asked-questions"
        }

        result = {
            "study": ELSA_FULL_NAME,
            "documentation_links": base_docs,
            "contact": {
                "data_queries": ELSA_DATA_EMAIL,
                "general_enquiries": f"{ELSA_PROJECT_URL}/contact"
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

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "compare_waves":
        waves = arguments.get("waves", [])
        focus = arguments.get("focus", "all")

        if not waves:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": "No waves specified for comparison"}, indent=2)
            )]

        comparison = {
            "waves_compared": waves,
            "comparison": {}
        }

        for wave in waves:
            if wave not in ELSA_WAVES:
                comparison["comparison"][wave] = {"error": "Wave not found"}
                continue

            wave_data = ELSA_WAVES[wave]

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

        return [types.TextContent(
            type="text",
            text=json.dumps(comparison, indent=2)
        )]

    elif name == "get_research_examples":
        topic = arguments.get("topic", "general")

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

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        )]


async def main():
    """Run the ELSA MCP server."""
    logger.info("Starting ELSA MCP server")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
