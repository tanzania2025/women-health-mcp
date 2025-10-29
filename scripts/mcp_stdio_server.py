#!/usr/bin/env python3
"""
Women's Health MCP Server - FastMCP Implementation
Provides clinical calculator and research tools via Model Context Protocol over stdio
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from pydantic import Field
from fastmcp.prompts import Message
from core.clinical_calculators import ClinicalCalculators
from core.research_database_integration import ResearchDatabaseIntegration
from core.fhir_integration import ReproductiveHealthFHIR

# Import research server modules
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
from servers import pubmed_server, eshre_server, nams_server, elsa_server

# Initialize calculators and services
calc = ClinicalCalculators()
research = ResearchDatabaseIntegration()
fhir = ReproductiveHealthFHIR()

# Create FastMCP server
mcp = FastMCP("women-health-mcp")


# ==================== Clinical Calculator Tools ====================

@mcp.tool()
async def predict_ivf_success(
    age: int = Field(description="Patient age in years (18-45)"),
    amh: float = Field(description="Anti-Müllerian Hormone level in ng/mL"),
    height_cm: Optional[float] = Field(None, description="Height in centimeters (120-220)"),
    weight_kg: Optional[float] = Field(None, description="Weight in kilograms (30-160)"),
    height_ft: Optional[int] = Field(None, description="Height in feet (4-7)"),
    height_in: Optional[int] = Field(None, description="Height in inches (0-11)"),
    weight_lbs: Optional[float] = Field(None, description="Weight in pounds (70-350)"),
    prior_pregnancies: int = Field(0, description="Number of prior full-term pregnancies"),
    male_factor: bool = Field(False, description="Partner has sperm problems"),
    polycystic: bool = Field(False, description="Patient has PCOS"),
    uterine_problems: bool = Field(False, description="Patient has uterine problems"),
    unexplained_infertility: bool = Field(False, description="Diagnosed with unexplained infertility"),
    low_ovarian_reserve: bool = Field(False, description="Diagnosed with low ovarian reserve"),
    bmi: Optional[float] = Field(None, description="Body Mass Index (optional)")
) -> str:
    """
    Predict IVF success rates using SART Calculator API.
    Calculates live birth probability for 1, 2, and 3 complete IVF cycles based on patient characteristics.
    """
    # Build parameters for SART calculator
    calc_params = {
        "age": age,
        "amh_available": True,
        "amh_value": amh,
        "previous_full_term": prior_pregnancies > 0,
        "male_factor": male_factor,
        "polycystic": polycystic,
        "uterine_problems": uterine_problems,
        "unexplained_infertility": unexplained_infertility,
        "low_ovarian_reserve": low_ovarian_reserve,
    }

    # Add height/weight if provided
    if height_cm:
        calc_params["height_cm"] = height_cm
    if weight_kg:
        calc_params["weight_kg"] = weight_kg
    if height_ft:
        calc_params["height_ft"] = height_ft
    if height_in:
        calc_params["height_in"] = height_in
    if weight_lbs:
        calc_params["weight_lbs"] = weight_lbs

    # Calculate BMI-based weight if only BMI provided
    if bmi and not weight_kg and not weight_lbs:
        height_m = 1.65  # Assume average height
        calc_params["weight_kg"] = bmi * (height_m ** 2)

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

    return json.dumps(response, indent=2)


# ==================== PubMed Tools ====================

@mcp.tool()
async def search_pubmed(
    query: str = Field(description="Search query (e.g., 'breast cancer treatment', 'PCOS polycystic ovary syndrome')"),
    max_results: int = Field(10, description="Maximum number of results to return (default: 10, max: 100)")
) -> str:
    """
    Search PubMed for scientific articles.
    Returns a list of article PMIDs and basic information matching the search query.
    """
    max_results = min(max_results, 100)

    # Search PubMed
    search_results = await pubmed_server.search_pubmed(query, max_results)
    summaries = await pubmed_server.get_article_summaries(search_results["pmids"])

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

    return response


@mcp.tool()
async def get_article(pmid: str = Field(description="PubMed ID (PMID) of the article to retrieve")) -> str:
    """
    Retrieve full article details including title, abstract, authors, journal, publication date, DOI, and keywords.
    """
    article = await pubmed_server.fetch_article_abstract(pmid)

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

    return response


@mcp.tool()
async def get_multiple_articles(pmids: list[str] = Field(description="List of PubMed IDs to retrieve")) -> str:
    """
    Retrieve full details for multiple PubMed articles at once.
    Returns abstracts, titles, authors, and metadata for all specified PMIDs.
    """
    articles = []
    for pmid in pmids:
        article = await pubmed_server.fetch_article_abstract(pmid)
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

    return response


# ==================== ESHRE Guidelines Tools ====================

@mcp.tool()
async def list_eshre_guidelines() -> str:
    """
    List all available ESHRE clinical guidelines and recommendations.
    """
    guidelines = await eshre_server.parse_guidelines_list()

    result = "# ESHRE Clinical Guidelines\n\n"
    result += f"Found {len(guidelines)} clinical guidelines:\n\n"

    for i, guideline in enumerate(guidelines, 1):
        result += f"{i}. **{guideline['title']}**\n"
        if guideline['description']:
            result += f"   {guideline['description']}\n"
        result += f"   URL: {guideline['url']}\n\n"

    return result


@mcp.tool()
async def search_eshre_guidelines(
    query: str = Field(description="Search query (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility preservation')")
) -> str:
    """
    Search ESHRE guidelines by keyword or topic.
    """
    results = await eshre_server.search_guidelines(query)

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

    return result


@mcp.tool()
async def get_eshre_guideline(url: str = Field(description="Full URL of the guideline document")) -> str:
    """
    Retrieve the full content and download links for a specific ESHRE guideline.
    """
    content = await eshre_server.get_guideline_content(url)

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

    return result


# ==================== NAMS Tools ====================

@mcp.tool()
async def list_nams_position_statements() -> str:
    """
    List available NAMS position statements and clinical guidelines on menopause management.
    """
    statements = await nams_server.parse_position_statements()

    # Supplement with known statements if needed
    if len(statements) < 5:
        known = nams_server.get_known_position_statements()
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

    return result


@mcp.tool()
async def search_nams_protocols(
    query: str = Field(description="Search query (e.g., 'hormone therapy', 'hot flashes', 'bone health')"),
    topic: Optional[str] = Field(None, description="Optional topic filter (e.g., 'hormone therapy', 'cardiovascular', 'genitourinary')")
) -> str:
    """
    Search NAMS position statements and protocols by keyword or topic.
    """
    results = await nams_server.search_protocols(query, topic)

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

    return result


@mcp.tool()
async def get_nams_protocol(url: str = Field(description="Full URL of the protocol or position statement")) -> str:
    """
    Retrieve the full content of a specific NAMS protocol or position statement.
    """
    content = await nams_server.get_protocol_content(url)

    result = f"# {content['title']}\n\n"
    result += f"**URL:** {content['url']}\n"
    result += f"**Content Type:** {content['content_type']}\n"
    if content.get('date'):
        result += f"**Date:** {content['date']}\n"
    if content['word_count'] > 0:
        result += f"**Word Count:** {content['word_count']}\n"
    result += "\n---\n\n"
    result += content['content']

    return result


# ==================== ELSA Tools ====================

@mcp.tool()
def list_elsa_waves(include_details: bool = Field(False, description="Include detailed information about each wave")) -> str:
    """
    List all available ELSA waves with basic information.
    """
    if include_details:
        result = {
            "study": "English Longitudinal Study of Ageing",
            "study_number": "5050",
            "total_waves": len(elsa_server.ELSA_WAVES),
            "waves": elsa_server.ELSA_WAVES
        }
    else:
        result = {
            "study": "English Longitudinal Study of Ageing",
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
def search_elsa_data(
    query: str = Field(description="Search term (e.g., 'cognitive', 'depression', 'wealth', 'menopause')"),
    module: Optional[str] = Field(None, description="Specific module to search (optional)")
) -> str:
    """
    Search ELSA data modules and variables by topic or keyword.
    """
    query_lower = query.lower()
    results = []

    modules_to_search = {module: elsa_server.ELSA_DATA_MODULES[module]} if module else elsa_server.ELSA_DATA_MODULES

    for mod_id, mod_data in modules_to_search.items():
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


# ==================== Resources ====================

@mcp.resource("health://guidelines", mime_type="application/json")
def list_all_guidelines() -> dict:
    """List all available clinical guidelines and resources."""
    return {
        "eshre_guidelines": "European Society of Human Reproduction and Embryology guidelines",
        "nams_statements": "North American Menopause Society position statements",
        "asrm_documents": "American Society for Reproductive Medicine practice documents",
        "pubmed_search": "PubMed scientific literature search",
        "elsa_data": "English Longitudinal Study of Ageing research data"
    }


# ==================== Prompts ====================

@mcp.prompt(
    name="analyze_research",
    description="Analyze research findings and provide clinical recommendations"
)
def analyze_research_prompt(
    topic: str = Field(description="Research topic to analyze"),
    patient_context: Optional[str] = Field(None, description="Patient context for personalized recommendations")
) -> list[Message]:
    """Generate a prompt for analyzing research findings in clinical context."""
    
    prompt = f"""
    You are a clinical research analyst specializing in women's health. Your task is to analyze research findings on the topic: "{topic}"
    
    Please follow these steps:
    
    1. **Search for relevant research**: Use the search_pubmed tool to find recent high-quality studies on this topic.
    
    2. **Review clinical guidelines**: Check relevant guidelines using:
       - search_eshre_guidelines for reproductive health topics
       - search_nams_protocols for menopause-related topics
    
    3. **Synthesize findings**: Combine evidence from multiple sources and identify:
       - Key findings and their clinical significance
       - Quality of evidence (study types, sample sizes, limitations)
       - Consensus or disagreements in the literature
       
    4. **Provide recommendations**: Based on the evidence, provide:
       - Evidence-based clinical recommendations
       - Areas where more research is needed
       - Practical implementation considerations
    """
    
    if patient_context:
        prompt += f"""
        
    5. **Patient-specific considerations**: Given this patient context: "{patient_context}"
       - Tailor recommendations to this specific scenario
       - Consider contraindications or special considerations
       - Suggest appropriate monitoring or follow-up
        """
    
    prompt += """
    
    Present your analysis in a structured format with clear sections and cite specific studies where appropriate.
    """
    
    return [Message(role="user", content=prompt)]


# Run the server
if __name__ == "__main__":
    mcp.run()