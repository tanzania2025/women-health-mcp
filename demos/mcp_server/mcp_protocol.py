"""
Model Context Protocol (MCP) Implementation using FastMCP
Following the official MCP specification for AI agent context exchange
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP

# Create FastMCP server instance
mcp = FastMCP("women-health-mcp")


# ============================================================================
# IVF & Fertility Tools
# ============================================================================

@mcp.tool(
    name="predict-ivf-success",
    description="Predict IVF success rates using SART Calculator API. Calculates live birth probability for 1, 2, and 3 complete IVF cycles based on patient characteristics."
)
async def predict_ivf_success(
    age: int,
    amh: float,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    height_ft: Optional[int] = None,
    height_in: Optional[int] = None,
    weight_lbs: Optional[float] = None,
    prior_pregnancies: int = 0,
    male_factor: bool = False,
    polycystic: bool = False,
    uterine_problems: bool = False,
    unexplained_infertility: bool = False,
    low_ovarian_reserve: bool = False,
    bmi: Optional[float] = None
) -> dict:
    """
    Predict IVF success rates using SART Calculator API.

    Calculates live birth probability for 1, 2, and 3 complete IVF cycles based on
    patient characteristics. Uses real-time data from University of Aberdeen SART Calculator.

    Args:
        age: Patient age in years (18-45)
        amh: Anti-Müllerian Hormone level in ng/mL
        height_cm: Height in centimeters (120-220)
        weight_kg: Weight in kilograms (30-160)
        height_ft: Height in feet (4-7)
        height_in: Height in inches (0-11)
        weight_lbs: Weight in pounds (70-350)
        prior_pregnancies: Number of prior full-term pregnancies (>37 weeks)
        male_factor: Does partner have sperm problems?
        polycystic: Does patient have PCOS?
        uterine_problems: Does patient have uterine problems?
        unexplained_infertility: Diagnosed with unexplained infertility?
        low_ovarian_reserve: Diagnosed with low ovarian reserve?
        bmi: Body Mass Index (optional)

    Returns:
        Dictionary with success rates and recommendations
    """
    from core.clinical_calculators import ClinicalCalculators

    calc = ClinicalCalculators()

    # Build parameters
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

    return {
        "success_rate_1_cycle": result.success_rate_1_cycle,
        "success_rate_2_cycles": result.success_rate_2_cycles,
        "success_rate_3_cycles": result.success_rate_3_cycles,
        "patient_info": {
            "age": result.age,
            "amh_value": result.amh_value,
        },
        "recommendations": calc._generate_recommendations(result),
        "data_source": "SART IVF Calculator API (University of Aberdeen)"
    }


# ============================================================================
# PubMed Research Tools
# ============================================================================

@mcp.tool(
    name="search_pubmed",
    description="Search PubMed for scientific articles. Returns a list of article PMIDs and basic information matching the search query."
)
async def search_pubmed(query: str, max_results: int = 10) -> str:
    """
    Search PubMed for scientific articles.

    Returns a list of article PMIDs and basic information matching the search query.

    Args:
        query: Search query (e.g., 'breast cancer treatment', 'PCOS polycystic ovary syndrome')
        max_results: Maximum number of results to return (default: 10, max: 100)

    Returns:
        Formatted string with search results
    """
    from servers.pubmed_server import search_pubmed as pubmed_search, get_article_summaries

    max_results = min(int(max_results), 100)

    # Search PubMed
    search_results = await pubmed_search(query, max_results)
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

    return response


@mcp.tool(
    name="get_article",
    description="Retrieve full article details including title, abstract, authors, journal, publication date, DOI, and keywords for a specific PubMed article by PMID."
)
async def get_article(pmid: str) -> str:
    """
    Retrieve full article details for a specific PubMed article.

    Includes title, abstract, authors, journal, publication date, DOI, and keywords.

    Args:
        pmid: PubMed ID (PMID) of the article to retrieve

    Returns:
        Formatted string with full article details
    """
    from servers.pubmed_server import fetch_article_abstract

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

    return response


@mcp.tool(
    name="get_multiple_articles",
    description="Retrieve full details for multiple PubMed articles at once. Returns abstracts, titles, authors, and metadata for all specified PMIDs."
)
async def get_multiple_articles(pmids: List[str]) -> str:
    """
    Retrieve full details for multiple PubMed articles at once.

    Returns abstracts, titles, authors, and metadata for all specified PMIDs.

    Args:
        pmids: List of PubMed IDs to retrieve

    Returns:
        Formatted string with all article details
    """
    from servers.pubmed_server import fetch_article_abstract
    import os

    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

    # Fetch all articles
    articles = []
    for pmid in pmids:
        article = await fetch_article_abstract(pmid)
        articles.append(article)
        # Be respectful of NCBI rate limits (3 requests/second without API key)
        if not NCBI_API_KEY:
            await asyncio.sleep(0.34)

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


# ============================================================================
# ESHRE (European Society of Human Reproduction) Guidelines
# ============================================================================

@mcp.tool(
    name="list_eshre_guidelines",
    description="List all available ESHRE clinical guidelines and recommendations for reproductive health and fertility treatment."
)
async def list_eshre_guidelines() -> str:
    """
    List all available ESHRE clinical guidelines and recommendations.

    ESHRE provides evidence-based guidelines for reproductive health and fertility treatment.

    Returns:
        Formatted list of all ESHRE guidelines
    """
    from servers.eshre_server import parse_guidelines_list

    guidelines = await parse_guidelines_list()

    result = f"# ESHRE Clinical Guidelines\n\nFound {len(guidelines)} clinical guidelines:\n\n"

    for i, guideline in enumerate(guidelines, 1):
        result += f"{i}. **{guideline['title']}**\n"
        if guideline['description']:
            result += f"   {guideline['description']}\n"
        result += f"   URL: {guideline['url']}\n\n"

    return result


@mcp.tool(
    name="search_eshre_guidelines",
    description="Search ESHRE guidelines by keyword or topic (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility preservation')."
)
async def search_eshre_guidelines(query: str) -> str:
    """
    Search ESHRE guidelines by keyword or topic.

    Args:
        query: Search query (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility preservation')

    Returns:
        Formatted list of matching guidelines
    """
    from servers.eshre_server import search_guidelines

    results = await search_guidelines(query)

    result = f"# Search Results for '{query}'\n\nFound {len(results)} matching guidelines:\n\n"

    for i, guideline in enumerate(results, 1):
        result += f"{i}. **{guideline['title']}**\n"
        if guideline['description']:
            result += f"   {guideline['description']}\n"
        result += f"   URL: {guideline['url']}\n\n"

    if not results:
        result += "No guidelines found matching your query.\n"

    return result


@mcp.tool(
    name="get_eshre_guideline",
    description="Retrieve the full content and download links for a specific ESHRE guideline by URL."
)
async def get_eshre_guideline(url: str) -> str:
    """
    Retrieve the full content and download links for a specific ESHRE guideline.

    Args:
        url: Full URL of the guideline document

    Returns:
        Full guideline content with metadata
    """
    from servers.eshre_server import get_guideline_content

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

    return result


# ============================================================================
# NAMS (North American Menopause Society) Tools
# ============================================================================

@mcp.tool(
    name="list_nams_position_statements",
    description="List available NAMS position statements and clinical guidelines on menopause management."
)
async def list_nams_position_statements() -> str:
    """
    List available NAMS position statements and clinical guidelines on menopause management.

    Returns:
        Formatted list of NAMS position statements
    """
    from servers.nams_server import parse_position_statements, get_known_position_statements

    statements = await parse_position_statements()

    # Supplement with known statements if needed
    if len(statements) < 5:
        known = get_known_position_statements()
        seen_urls = {s['url'] for s in statements}
        for stmt in known:
            if stmt['url'] not in seen_urls:
                statements.append(stmt)

    result = f"# NAMS Position Statements & Clinical Guidelines\n\nFound {len(statements)} position statements and guidelines:\n\n"

    for i, stmt in enumerate(statements, 1):
        result += f"{i}. **{stmt['title']}**\n"
        if stmt.get('topic'):
            result += f"   Topic: {stmt['topic']}\n"
        if stmt.get('description'):
            result += f"   {stmt['description']}\n"
        result += f"   Type: {stmt['type']}\n"
        result += f"   URL: {stmt['url']}\n\n"

    return result


@mcp.tool(
    name="search_nams_protocols",
    description="Search NAMS position statements and protocols by keyword or topic (e.g., 'hormone therapy', 'osteoporosis', 'vasomotor symptoms')."
)
async def search_nams_protocols(query: str, topic: Optional[str] = None) -> str:
    """
    Search NAMS position statements and protocols by keyword or topic.

    Args:
        query: Search query (e.g., 'hormone therapy', 'osteoporosis', 'vasomotor symptoms')
        topic: Optional topic filter (e.g., 'hormone therapy', 'cardiovascular', 'genitourinary')

    Returns:
        Formatted list of matching protocols
    """
    from servers.nams_server import search_protocols

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

    return result


@mcp.tool(
    name="get_nams_protocol",
    description="Retrieve the full content of a specific NAMS protocol or position statement by URL."
)
async def get_nams_protocol(url: str) -> str:
    """
    Retrieve the full content of a specific NAMS protocol or position statement.

    Args:
        url: Full URL of the protocol or position statement

    Returns:
        Full protocol content with metadata
    """
    from servers.nams_server import get_protocol_content

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

    return result


# ============================================================================
# ELSA (English Longitudinal Study of Ageing) Tools
# ============================================================================

@mcp.tool(
    name="list_elsa_waves",
    description="List all available ELSA (English Longitudinal Study of Ageing) study waves with basic information."
)
async def list_elsa_waves(include_details: bool = False) -> dict:
    """
    List all available ELSA study waves.

    ELSA is a longitudinal study on aging in England (1998-2024).

    Args:
        include_details: Include detailed information about each wave

    Returns:
        Dictionary with ELSA wave information
    """
    from servers.elsa_server import ELSA_WAVES, ELSA_FULL_NAME, ELSA_STUDY_NUMBER

    if include_details:
        result_data = {
            "study": ELSA_FULL_NAME,
            "study_number": ELSA_STUDY_NUMBER,
            "total_waves": len(ELSA_WAVES),
            "waves": ELSA_WAVES
        }
    else:
        result_data = {
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

    return result_data


@mcp.tool(
    name="search_elsa_data",
    description="Search ELSA data modules and variables by topic or keyword (e.g., 'cognitive', 'depression', 'menopause', 'biomarkers')."
)
async def search_elsa_data(query: str, module: Optional[str] = None) -> dict:
    """
    Search ELSA data modules and variables by topic or keyword.

    Args:
        query: Search term (e.g., 'cognitive', 'depression', 'menopause', 'biomarkers')
        module: Specific module to search (optional)

    Returns:
        Dictionary with search results
    """
    from servers.elsa_server import ELSA_DATA_MODULES

    query_lower = query.lower()
    results = []

    modules_to_search = {module: ELSA_DATA_MODULES[module]} if module and module in ELSA_DATA_MODULES else ELSA_DATA_MODULES

    for mod_id, mod_data in modules_to_search.items():
        searchable_text = f"{mod_data['name']} {mod_data['description']} {' '.join(mod_data['variables'])}".lower()

        if query_lower in searchable_text:
            results.append({
                "module_id": mod_id,
                "module_name": mod_data["name"],
                "description": mod_data["description"],
                "relevant_variables": [v for v in mod_data["variables"] if query_lower in v.lower()]
            })

    return {
        "query": query,
        "results_found": len(results),
        "modules": results
    }


# ============================================================================
# Research Database Query Tool (Legacy - consider deprecating)
# ============================================================================

@mcp.tool(
    name="query-research-database",
    description="Query SWAN, SART, or PubMed databases (Legacy - use specific database tools like search_pubmed instead)."
)
async def query_research_database(
    database: str,
    query_type: str,
    condition: str,
    age_range: Optional[List[int]] = None
) -> dict:
    """
    Query SWAN, SART, or PubMed databases.

    Legacy tool - consider using specific database tools instead.

    Args:
        database: Database to query ('swan', 'sart', or 'pubmed')
        query_type: Type of query ('population_statistics', 'clinical_trials', 'publications')
        condition: Medical condition to query
        age_range: Optional age range as [min_age, max_age]

    Returns:
        Query results
    """
    from .swan_data_integration import swan_integration

    if database == "swan":
        result = swan_integration.get_population_statistics(
            condition=condition,
            age_range=tuple(age_range) if age_range else None
        )
        return {
            "database": database,
            "result": result
        }
    else:
        return {
            "database": database,
            "result": "Non-SWAN databases not implemented. Use specific tools like search_pubmed instead."
        }


# ============================================================================
# FHIR Resource Creation (Placeholder)
# ============================================================================

@mcp.tool(
    name="create-fhir-resource",
    description="Create FHIR R4 compliant reproductive health resources (Patient, Observation, DiagnosticReport, Condition)."
)
async def create_fhir_resource(
    resource_type: str,
    patient_id: str,
    data: dict
) -> dict:
    """
    Create FHIR R4 compliant reproductive health resources.

    Args:
        resource_type: FHIR resource type ('Patient', 'Observation', 'DiagnosticReport', 'Condition')
        patient_id: Patient identifier
        data: Resource-specific data

    Returns:
        Created FHIR resource
    """
    from core.fhir_integration import ReproductiveHealthFHIR

    fhir = ReproductiveHealthFHIR()

    return {
        "resource_type": resource_type,
        "patient_id": patient_id,
        "note": "FHIR resource creation is a placeholder in this demo",
        "data": data
    }
