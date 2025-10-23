#!/usr/bin/env python3
"""
Women's Health MCP Server - Stdio Implementation
Provides clinical calculator and research tools via Model Context Protocol over stdio
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from core.clinical_calculators import ClinicalCalculators
from core.research_database_integration import ResearchDatabaseIntegration
from core.fhir_integration import ReproductiveHealthFHIR
import json

# Import research server functions
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
from pubmed_server import search_pubmed, get_article_summaries, fetch_article_abstract
from eshre_server import parse_guidelines_list, search_guidelines, get_guideline_content
from nams_server import parse_position_statements, search_protocols, get_protocol_content, get_known_position_statements
from elsa_server import ELSA_WAVES, ELSA_DATA_MODULES

# Initialize calculators
calc = ClinicalCalculators()
research = ResearchDatabaseIntegration()
fhir = ReproductiveHealthFHIR()

# Create MCP server
app = Server("women-health-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available clinical calculator and research tools."""
    return [
        # Clinical Calculator
        Tool(
            name="predict-ivf-success",
            description="Predict IVF success rates using SART Calculator API. Calculates live birth probability for 1, 2, and 3 complete IVF cycles based on patient characteristics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "Patient age in years",
                        "minimum": 18,
                        "maximum": 45
                    },
                    "amh": {
                        "type": "number",
                        "description": "Anti-Müllerian Hormone level in ng/mL",
                        "minimum": 0
                    },
                    "height_cm": {
                        "type": "number",
                        "description": "Height in centimeters (120-220). Use this OR height_ft/height_in."
                    },
                    "weight_kg": {
                        "type": "number",
                        "description": "Weight in kilograms (30-160). Use this OR weight_lbs."
                    },
                    "height_ft": {
                        "type": "integer",
                        "description": "Height in feet (4-7). Use with height_in if not using height_cm."
                    },
                    "height_in": {
                        "type": "integer",
                        "description": "Height in inches (0-11). Use with height_ft if not using height_cm."
                    },
                    "weight_lbs": {
                        "type": "number",
                        "description": "Weight in pounds (70-350). Use if not using weight_kg."
                    },
                    "prior_pregnancies": {
                        "type": "integer",
                        "description": "Number of prior full-term pregnancies (>37 weeks)",
                        "minimum": 0
                    },
                    "male_factor": {
                        "type": "boolean",
                        "description": "Does partner have sperm problems?",
                        "default": False
                    },
                    "polycystic": {
                        "type": "boolean",
                        "description": "Does patient have PCOS?",
                        "default": False
                    },
                    "uterine_problems": {
                        "type": "boolean",
                        "description": "Does patient have uterine problems?",
                        "default": False
                    },
                    "unexplained_infertility": {
                        "type": "boolean",
                        "description": "Diagnosed with unexplained infertility?",
                        "default": False
                    },
                    "low_ovarian_reserve": {
                        "type": "boolean",
                        "description": "Diagnosed with low ovarian reserve?",
                        "default": False
                    },
                    "bmi": {
                        "type": "number",
                        "description": "Body Mass Index (optional, for internal calculations)",
                        "minimum": 10,
                        "maximum": 60
                    }
                },
                "required": ["age", "amh"]
            }
        ),

        # PubMed Tools
        Tool(
            name="search_pubmed",
            description="Search PubMed for scientific articles. Returns a list of article PMIDs and basic information matching the search query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'breast cancer treatment', 'PCOS polycystic ovary syndrome')",
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10, max: 100)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_article",
            description="Retrieve full article details including title, abstract, authors, journal, publication date, DOI, and keywords for a specific PubMed article by PMID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pmid": {
                        "type": "string",
                        "description": "PubMed ID (PMID) of the article to retrieve",
                    },
                },
                "required": ["pmid"],
            },
        ),
        Tool(
            name="get_multiple_articles",
            description="Retrieve full details for multiple PubMed articles at once. Returns abstracts, titles, authors, and metadata for all specified PMIDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pmids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of PubMed IDs to retrieve",
                    },
                },
                "required": ["pmids"],
            },
        ),

        # ESHRE Tools
        Tool(
            name="list_eshre_guidelines",
            description="List all available ESHRE clinical guidelines and recommendations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="search_eshre_guidelines",
            description="Search ESHRE guidelines by keyword or topic (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility preservation')",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility')"
                    }
                },
                "required": ["query"]
            },
        ),
        Tool(
            name="get_eshre_guideline",
            description="Retrieve the full content and download links for a specific ESHRE guideline by URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the guideline document"
                    }
                },
                "required": ["url"]
            },
        ),

        # NAMS Tools
        Tool(
            name="list_nams_position_statements",
            description="List available NAMS position statements and clinical guidelines on menopause management",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="search_nams_protocols",
            description="Search NAMS position statements and protocols by keyword or topic (e.g., 'hormone therapy', 'osteoporosis', 'vasomotor symptoms')",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'hormone therapy', 'hot flashes', 'bone health')"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Optional topic filter (e.g., 'hormone therapy', 'cardiovascular', 'genitourinary')"
                    }
                },
                "required": ["query"]
            },
        ),
        Tool(
            name="get_nams_protocol",
            description="Retrieve the full content of a specific NAMS protocol or position statement by URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Full URL of the protocol or position statement"
                    }
                },
                "required": ["url"]
            },
        ),

        # ELSA Tools
        Tool(
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
        Tool(
            name="search_elsa_data",
            description="Search ELSA data modules and variables by topic or keyword (e.g., 'cognitive', 'depression', 'menopause', 'biomarkers')",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'cognitive', 'depression', 'wealth', 'menopause')"
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a clinical calculator or research tool."""

    try:
        # Clinical Calculator Tools
        if name == "predict-ivf-success":
            # Build parameters for SART calculator
            calc_params = {
                "age": arguments["age"],
                "amh_available": True,
                "amh_value": arguments["amh"],
                "previous_full_term": arguments.get("prior_pregnancies", 0) > 0,
                "male_factor": arguments.get("male_factor", False),
                "polycystic": arguments.get("polycystic", False),
                "uterine_problems": arguments.get("uterine_problems", False),
                "unexplained_infertility": arguments.get("unexplained_infertility", False),
                "low_ovarian_reserve": arguments.get("low_ovarian_reserve", False),
            }

            # Add height/weight if provided
            if arguments.get("height_cm"):
                calc_params["height_cm"] = arguments["height_cm"]
            if arguments.get("weight_kg"):
                calc_params["weight_kg"] = arguments["weight_kg"]
            if arguments.get("height_ft"):
                calc_params["height_ft"] = arguments["height_ft"]
            if arguments.get("height_in"):
                calc_params["height_in"] = arguments["height_in"]
            if arguments.get("weight_lbs"):
                calc_params["weight_lbs"] = arguments["weight_lbs"]

            # Calculate BMI-based weight if only BMI provided
            if arguments.get("bmi") and not arguments.get("weight_kg") and not arguments.get("weight_lbs"):
                height_m = 1.65  # Assume average height
                calc_params["weight_kg"] = arguments["bmi"] * (height_m ** 2)

            result = await calc.calculate_ivf_success(**calc_params)

            # Format response
            response = {
                "tool": "predict-ivf-success",
                "patient_info": {
                    "age": result.age,
                    "height_cm": result.height_cm,
                    "weight_kg": result.weight_kg,
                    "height_ft": result.height_ft,
                    "height_in": result.height_in,
                    "weight_lbs": result.weight_lbs,
                },
                "clinical_factors": {
                    "previous_full_term": result.previous_full_term,
                    "male_factor": result.male_factor,
                    "polycystic": result.polycystic,
                    "uterine_problems": result.uterine_problems,
                    "unexplained_infertility": result.unexplained_infertility,
                    "low_ovarian_reserve": result.low_ovarian_reserve,
                    "amh_value": result.amh_value,
                },
                "success_rates": {
                    "1_cycle": result.success_rate_1_cycle,
                    "2_cycles": result.success_rate_2_cycles,
                    "3_cycles": result.success_rate_3_cycles,
                },
                "recommendations": calc._generate_recommendations(result),
                "data_source": "SART IVF Calculator API (University of Aberdeen)",
            }

            return [TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]

        # PubMed Tools
        elif name == "search_pubmed":
            query = arguments.get("query")
            if not query:
                raise ValueError("Missing required argument: query")

            max_results = min(int(arguments.get("max_results", 10)), 100)

            # Search PubMed
            search_results = await search_pubmed(query, max_results)
            summaries = await get_article_summaries(search_results["pmids"])

            # Format the response
            response = f"Found {search_results['count']} articles for query: '{query}'\n\n"
            response += f"Showing top {len(summaries)} results:\n\n"

            for i, summary in enumerate(summaries, 1):
                response += f"{i}. **{summary['title']}**\n"
                response += f"   - PMID: {summary['pmid']}\n"
                response += f"   - Authors: {', '.join(summary['authors'][:3])}"
                if len(summary['authors']) > 3:
                    response += f" et al."
                response += f"\n   - Journal: {summary['journal']}\n"
                response += f"   - Published: {summary['pubdate']}\n"
                if summary['doi']:
                    response += f"   - DOI: {summary['doi']}\n"
                response += "\n"

            response += "\nUse the 'get_article' tool with a PMID to retrieve the full abstract and details."

            return [TextContent(type="text", text=response)]

        elif name == "get_article":
            pmid = arguments.get("pmid")
            if not pmid:
                raise ValueError("Missing required argument: pmid")

            article = await fetch_article_abstract(pmid)

            # Format the response
            response = f"# {article['title']}\n\n"
            response += f"**PMID:** {article['pmid']}\n"
            if article['doi']:
                response += f"**DOI:** {article['doi']}\n"
            response += f"**Journal:** {article['journal']}\n"
            response += f"**Published:** {article['pubdate']}\n\n"

            if article['authors']:
                response += f"**Authors:** {', '.join(article['authors'])}\n\n"

            if article['keywords']:
                response += f"**Keywords:** {', '.join(article['keywords'])}\n\n"

            if article['abstract']:
                response += f"## Abstract\n\n{article['abstract']}\n"
            else:
                response += "**Note:** Abstract not available for this article.\n"

            return [TextContent(type="text", text=response)]

        elif name == "get_multiple_articles":
            pmids = arguments.get("pmids")
            if not pmids:
                raise ValueError("Missing required argument: pmids")

            articles = []
            for pmid in pmids:
                article = await fetch_article_abstract(pmid)
                articles.append(article)
                await asyncio.sleep(0.34)  # Rate limiting

            # Format the response
            response = f"Retrieved {len(articles)} articles:\n\n"
            response += "=" * 80 + "\n\n"

            for article in articles:
                response += f"# {article['title']}\n\n"
                response += f"**PMID:** {article['pmid']}\n"
                if article['doi']:
                    response += f"**DOI:** {article['doi']}\n"
                response += f"**Journal:** {article['journal']}\n"
                response += f"**Published:** {article['pubdate']}\n\n"

                if article['authors']:
                    response += f"**Authors:** {', '.join(article['authors'])}\n\n"

                if article['keywords']:
                    response += f"**Keywords:** {', '.join(article['keywords'])}\n\n"

                if article['abstract']:
                    response += f"## Abstract\n\n{article['abstract']}\n"
                else:
                    response += "**Note:** Abstract not available for this article.\n"

                response += "\n" + "=" * 80 + "\n\n"

            return [TextContent(type="text", text=response)]

        # ESHRE Tools
        elif name == "list_eshre_guidelines":
            guidelines = await parse_guidelines_list()

            result = "# ESHRE Clinical Guidelines\n\n"
            result += f"Found {len(guidelines)} clinical guidelines:\n\n"

            for i, guideline in enumerate(guidelines, 1):
                result += f"{i}. **{guideline['title']}**\n"
                if guideline['description']:
                    result += f"   {guideline['description']}\n"
                result += f"   URL: {guideline['url']}\n\n"

            return [TextContent(type="text", text=result)]

        elif name == "search_eshre_guidelines":
            query = arguments.get("query")
            if not query:
                raise ValueError("query parameter is required")

            results = await search_guidelines(query)

            result = f"# Search Results for '{query}'\n\n"
            result += f"Found {len(results)} matching guidelines:\n\n"

            for i, guideline in enumerate(results, 1):
                result += f"{i}. **{guideline['title']}**\n"
                if guideline['description']:
                    result += f"   {guideline['description']}\n"
                result += f"   URL: {guideline['url']}\n\n"

            if not results:
                result += "No guidelines found matching your query.\n"
                result += "Try different keywords or browse all guidelines using list_eshre_guidelines.\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_eshre_guideline":
            url = arguments.get("url")
            if not url:
                raise ValueError("url parameter is required")

            content = await get_guideline_content(url)

            result = f"# {content['title']}\n\n"
            result += f"**URL:** {content['url']}\n"
            if content['date']:
                result += f"**Published:** {content['date']}\n"
            result += f"**Word Count:** {content['word_count']}\n\n"

            if content['downloads']:
                result += "## Downloads\n\n"
                for dl in content['downloads']:
                    result += f"- [{dl['title']}]({dl['url']})\n"
                result += "\n"

            result += "---\n\n"
            result += content['content']

            return [TextContent(type="text", text=result)]

        # NAMS Tools
        elif name == "list_nams_position_statements":
            statements = await parse_position_statements()

            # Supplement with known statements if needed
            if len(statements) < 5:
                known = get_known_position_statements()
                seen_urls = {s['url'] for s in statements}
                for stmt in known:
                    if stmt['url'] not in seen_urls:
                        statements.append(stmt)

            result = "# NAMS Position Statements & Clinical Guidelines\n\n"
            result += f"Found {len(statements)} position statements and guidelines:\n\n"

            for i, stmt in enumerate(statements, 1):
                result += f"{i}. **{stmt['title']}**\n"
                if stmt.get('topic'):
                    result += f"   Topic: {stmt['topic']}\n"
                if stmt.get('description'):
                    result += f"   {stmt['description']}\n"
                result += f"   Type: {stmt['type']}\n"
                result += f"   URL: {stmt['url']}\n\n"

            return [TextContent(type="text", text=result)]

        elif name == "search_nams_protocols":
            query = arguments.get("query")
            if not query:
                raise ValueError("query parameter is required")

            topic = arguments.get("topic")
            results = await search_protocols(query, topic)

            result = f"# Search Results for '{query}'\n\n"

            if topic:
                result += f"Topic filter: {topic}\n\n"

            result += f"Found {len(results)} matching documents:\n\n"

            for i, doc in enumerate(results, 1):
                result += f"{i}. **{doc['title']}**\n"
                result += f"   Type: {doc['type']}\n"
                if doc.get('topic'):
                    result += f"   Topic: {doc['topic']}\n"
                if doc.get('description'):
                    result += f"   {doc['description']}\n"
                result += f"   URL: {doc['url']}\n\n"

            if not results:
                result += "No documents found matching your query.\n"
                result += "Try different keywords or browse all documents using list_nams_position_statements.\n"
                result += "\nCommon topics: hormone therapy, vasomotor symptoms, osteoporosis, cardiovascular, genitourinary\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_nams_protocol":
            url = arguments.get("url")
            if not url:
                raise ValueError("url parameter is required")

            content = await get_protocol_content(url)

            result = f"# {content['title']}\n\n"
            result += f"**URL:** {content['url']}\n"
            result += f"**Content Type:** {content['content_type']}\n"
            if content.get('date'):
                result += f"**Date:** {content['date']}\n"
            if content['word_count'] > 0:
                result += f"**Word Count:** {content['word_count']}\n"
            result += "\n---\n\n"
            result += content['content']

            return [TextContent(type="text", text=result)]

        # ELSA Tools
        elif name == "list_elsa_waves":
            include_details = arguments.get("include_details", False)

            if include_details:
                result = {
                    "study": "English Longitudinal Study of Ageing",
                    "study_number": "5050",
                    "total_waves": len(ELSA_WAVES),
                    "waves": ELSA_WAVES
                }
            else:
                result = {
                    "study": "English Longitudinal Study of Ageing",
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

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "search_elsa_data":
            query = arguments.get("query", "").lower()
            module_filter = arguments.get("module")

            results = []
            modules_to_search = {module_filter: ELSA_DATA_MODULES[module_filter]} if module_filter else ELSA_DATA_MODULES

            for mod_id, mod_data in modules_to_search.items():
                searchable_text = f"{mod_data['name']} {mod_data['description']} {' '.join(mod_data['variables'])}".lower()

                if query in searchable_text:
                    results.append({
                        "module_id": mod_id,
                        "module_name": mod_data["name"],
                        "description": mod_data["description"],
                        "relevant_variables": [v for v in mod_data["variables"] if query in v.lower()]
                    })

            return [TextContent(
                type="text",
                text=json.dumps({
                    "query": query,
                    "results_found": len(results),
                    "modules": results
                }, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
