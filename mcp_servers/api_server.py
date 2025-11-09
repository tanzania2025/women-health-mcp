#!/usr/bin/env python3
"""
Women's Health API Server - FastMCP Implementation
Provides access to external medical APIs and clinical guidelines:
- PubMed (NCBI E-utilities)
- ESHRE (European Society of Human Reproduction and Embryology)
- ASRM (American Society for Reproductive Medicine)
- NAMS (North American Menopause Society)
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

# Import server modules
sys.path.insert(0, str(Path(__file__).parent.parent / "servers"))
from servers import pubmed_server, eshre_server, asrm_server, nams_server

# Create FastMCP server
mcp = FastMCP("women-health-api")


# ==================== PubMed Tools ====================

@mcp.tool()
async def search_pubmed(query: str, max_results: int = 10) -> str:
    """
    Search PubMed for peer-reviewed medical literature (35M+ articles).

    Uses NCBI E-utilities API to search biomedical literature. Essential for
    evidence-based clinical decision support and research validation.

    Args:
        query: Search query (e.g., 'breast cancer treatment', 'PCOS polycystic ovary syndrome')
        max_results: Maximum number of results to return (default: 10, max: 100)
    """
    try:
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
    except Exception as e:
        return f"Error searching PubMed: {str(e)}\n\nPlease try again or check your query."


@mcp.tool()
async def get_article(pmid: str) -> str:
    """
    Retrieve full PubMed article details by PMID.

    Returns complete article metadata including title, abstract, authors,
    journal, publication date, DOI, and keywords.

    Args:
        pmid: PubMed ID (PMID) of the article to retrieve
    """
    try:
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
    except Exception as e:
        return f"Error retrieving article {pmid}: {str(e)}\n\nPlease verify the PMID is correct."


@mcp.tool()
async def get_multiple_articles(pmids: list[str]) -> str:
    """
    Retrieve full details for multiple PubMed articles at once.

    Returns abstracts, titles, authors, and metadata for all specified PMIDs.
    Useful for batch processing of search results.

    Args:
        pmids: List of PubMed IDs to retrieve
    """
    try:
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
    except Exception as e:
        return f"Error retrieving articles: {str(e)}\n\nPlease verify the PMIDs are correct."


# ==================== ESHRE Guidelines Tools ====================

@mcp.tool()
async def list_eshre_guidelines() -> str:
    """
    List all available ESHRE clinical guidelines and recommendations.
    
    ESHRE (European Society of Human Reproduction and Embryology) provides
    evidence-based fertility treatment guidelines used across Europe.
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
async def search_eshre_guidelines(query: str) -> str:
    """
    Search ESHRE clinical practice guidelines by keyword or topic.
    
    Args:
        query: Search query (e.g., 'endometriosis', 'IVF', 'PCOS', 'fertility preservation')
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
async def get_eshre_guideline(url: str) -> str:
    """
    Retrieve the full content and download links for a specific ESHRE guideline.
    
    Args:
        url: Full URL of the guideline document
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


# ==================== ASRM Guidelines Tools ====================

@mcp.tool()
async def list_asrm_practice_documents() -> str:
    """
    List available ASRM practice committee documents and guidelines.
    
    ASRM (American Society for Reproductive Medicine) provides US-based
    reproductive medicine practice guidelines and committee opinions.
    """
    documents = await asrm_server.parse_practice_documents()

    result = "# ASRM Practice Documents\n\n"
    result += f"Found {len(documents)} practice documents:\n\n"

    for i, doc in enumerate(documents[:15], 1):  # Limit for readability
        result += f"{i}. **{doc['title']}**\n"
        if doc['description']:
            result += f"   {doc['description']}\n"
        result += f"   URL: {doc['url']}\n\n"

    if len(documents) > 15:
        result += f"\n...and {len(documents) - 15} more documents.\n"

    return result


@mcp.tool()
async def list_asrm_ethics_opinions() -> str:
    """
    List available ASRM ethics committee opinions.
    
    Provides bioethical guidance on reproductive medicine practices
    and emerging technologies.
    """
    opinions = await asrm_server.parse_ethics_opinions()

    result = "# ASRM Ethics Opinions\n\n"
    result += f"Found {len(opinions)} ethics opinions:\n\n"

    for i, op in enumerate(opinions[:15], 1):
        result += f"{i}. **{op['title']}**\n"
        if op['description']:
            result += f"   {op['description']}\n"
        result += f"   URL: {op['url']}\n\n"

    if len(opinions) > 15:
        result += f"\n...and {len(opinions) - 15} more opinions.\n"

    return result


@mcp.tool()
async def search_asrm_guidelines(query: str, category: Optional[str] = None) -> str:
    """
    Search ASRM guidelines by keyword.
    
    Args:
        query: Search query (e.g., 'IVF', 'endometriosis', 'genetic testing')
        category: Optional category filter ('practice' or 'ethics')
    """
    results = await asrm_server.search_guidelines(query, category)

    result = f"# Search Results for '{query}'\n\n"

    if category:
        result += f"Category: {category}\n\n"

    result += f"Found {len(results)} matching documents:\n\n"

    for i, doc in enumerate(results, 1):
        result += f"{i}. **{doc['title']}**\n"
        result += f"   Type: {doc['type']}\n"
        if doc['description']:
            result += f"   {doc['description']}\n"
        result += f"   URL: {doc['url']}\n\n"

    if not results:
        result += "No documents found matching your query.\n"
        result += "Try different keywords or browse all documents using list_asrm_practice_documents or list_asrm_ethics_opinions.\n"

    return result


@mcp.tool()
async def get_asrm_guideline(url: str) -> str:
    """
    Retrieve the full content of a specific ASRM guideline document.
    
    Args:
        url: Full URL of the guideline document
    """
    content = await asrm_server.get_guideline_content(url)

    result = f"# {content['title']}\n\n"
    result += f"**URL:** {content['url']}\n"
    if content['date']:
        result += f"**Date:** {content['date']}\n"
    result += f"**Word Count:** {content['word_count']}\n\n"
    result += "---\n\n"
    result += content['content']

    return result


# ==================== NAMS Position Statements Tools ====================

@mcp.tool()
async def list_nams_position_statements() -> str:
    """
    List available NAMS position statements and clinical guidelines on menopause management.
    
    NAMS (The Menopause Society, formerly North American Menopause Society) provides
    evidence-based menopause management guidelines and hormone therapy recommendations.
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
async def search_nams_protocols(query: str, topic: Optional[str] = None) -> str:
    """
    Search NAMS position statements and protocols by keyword or topic.
    
    Args:
        query: Search query (e.g., 'hormone therapy', 'hot flashes', 'bone health')
        topic: Optional topic filter (e.g., 'hormone therapy', 'cardiovascular', 'genitourinary')
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
async def get_nams_protocol(url: str) -> str:
    """
    Retrieve the full content of a specific NAMS protocol or position statement.
    
    Args:
        url: Full URL of the protocol or position statement
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


@mcp.tool()
async def list_nams_topics() -> str:
    """
    List common topics covered by NAMS position statements.
    
    Helps users discover relevant position statements for specific menopause-related topics.
    """
    topics = [
        "Hormone Therapy",
        "Vasomotor Symptoms (hot flashes, night sweats)",
        "Genitourinary Syndrome of Menopause",
        "Osteoporosis and Bone Health",
        "Cardiovascular Health",
        "Sexual Health",
        "Mood and Cognitive Function",
        "Sleep Disorders",
        "Weight Management",
        "Breast Health",
        "Nonhormonal Therapies",
        "Bioidentical Hormones",
        "Premature Menopause",
        "Complementary and Alternative Medicine"
    ]

    result = "# Common Topics in NAMS Position Statements\n\n"
    result += "The following topics are commonly addressed in NAMS position statements:\n\n"

    for i, topic in enumerate(topics, 1):
        result += f"{i}. {topic}\n"

    result += "\nUse these topics to search for specific position statements with the search_nams_protocols tool.\n"

    return result


# Environment variables for API connections
import os

# Environment variables that may be needed
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
ESHRE_CREDENTIALS = os.getenv("ESHRE_CREDENTIALS", "")  
ASRM_TOKEN = os.getenv("ASRM_TOKEN", "")
NAMS_TOKEN = os.getenv("NAMS_TOKEN", "")


# Run the server
if __name__ == "__main__":
    mcp.run()