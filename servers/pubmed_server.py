#!/usr/bin/env python3
"""
PubMed MCP Server - FastMCP Implementation

This MCP server provides tools to search PubMed for scientific articles
and retrieve their content for analysis by Claude.
"""

import os
from typing import Any, List, Optional
import requests
from xml.etree import ElementTree as ET
from fastmcp import FastMCP
from pydantic import Field
import time

# NCBI E-utilities base URLs
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Get API key from environment (optional but recommended for higher rate limits)
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

# Create FastMCP server
mcp = FastMCP("pubmed-server")


def search_pubmed(query: str, max_results: int = 10) -> dict[str, Any]:
    """
    Search PubMed for articles matching the query.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 10)

    Returns:
        Dictionary containing search results with PMIDs and count
    """
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
    }

    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    response = requests.get(ESEARCH_URL, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    return {
        "count": int(data["esearchresult"]["count"]),
        "pmids": data["esearchresult"]["idlist"],
        "query": query
    }


def get_article_summaries(pmids: list[str]) -> list[dict[str, Any]]:
    """
    Get article summaries for a list of PMIDs.

    Args:
        pmids: List of PubMed IDs

    Returns:
        List of article summaries
    """
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    }

    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    response = requests.get(ESUMMARY_URL, params=params, timeout=30.0)
    response.raise_for_status()
    data = response.json()

    summaries = []
    for pmid in pmids:
        if pmid in data["result"]:
            article = data["result"][pmid]
            summaries.append({
                "pmid": pmid,
                "title": article.get("title", ""),
                "authors": [author.get("name", "") for author in article.get("authors", [])],
                "journal": article.get("fulljournalname", ""),
                "pubdate": article.get("pubdate", ""),
                "doi": article.get("elocationid", "").replace("doi: ", ""),
            })

    return summaries


def fetch_article_abstract(pmid: str) -> dict[str, Any]:
    """
    Fetch full article details including abstract from PubMed.

    Args:
        pmid: PubMed ID

    Returns:
        Dictionary containing article details
    """
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }

    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    response = requests.get(EFETCH_URL, params=params, timeout=30.0)
    response.raise_for_status()

    # Parse XML response
    root = ET.fromstring(response.text)

    # Extract article information
    article_data = {
            "pmid": pmid,
            "title": "",
            "abstract": "",
            "authors": [],
            "journal": "",
            "pubdate": "",
            "doi": "",
            "keywords": [],
        }

    # Find the article element
    article = root.find(".//PubmedArticle")
    if article is None:
        return article_data

    # Title
    title_elem = article.find(".//ArticleTitle")
    if title_elem is not None and title_elem.text:
        article_data["title"] = title_elem.text

    # Abstract
    abstract_texts = article.findall(".//AbstractText")
    if abstract_texts:
        abstract_parts = []
        for abstract_text in abstract_texts:
            label = abstract_text.get("Label", "")
            text = abstract_text.text or ""
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)
        article_data["abstract"] = "\n\n".join(abstract_parts)

    # Authors
    authors = article.findall(".//Author")
    for author in authors:
        last_name = author.find("LastName")
        fore_name = author.find("ForeName")
        if last_name is not None and fore_name is not None:
            article_data["authors"].append(f"{fore_name.text} {last_name.text}")

    # Journal
    journal = article.find(".//Journal/Title")
    if journal is not None and journal.text:
        article_data["journal"] = journal.text

    # Publication date
    pub_date = article.find(".//PubDate")
    if pub_date is not None:
        year = pub_date.find("Year")
        month = pub_date.find("Month")
        day = pub_date.find("Day")
        date_parts = []
        if year is not None and year.text:
            date_parts.append(year.text)
        if month is not None and month.text:
            date_parts.append(month.text)
        if day is not None and day.text:
            date_parts.append(day.text)
        article_data["pubdate"] = " ".join(date_parts)

    # DOI
    article_ids = article.findall(".//ArticleId")
    for article_id in article_ids:
        if article_id.get("IdType") == "doi":
            article_data["doi"] = article_id.text or ""

    # Keywords
    keywords = article.findall(".//Keyword")
    article_data["keywords"] = [kw.text for kw in keywords if kw.text]

    return article_data


# ==================== FastMCP Tools ====================

@mcp.tool(
    name="search_pubmed_articles",
    description="Search PubMed for scientific articles. Returns a list of article PMIDs and basic information matching the search query."
)
def search_pubmed_articles(
    query: str = Field(description="Search query (e.g., 'breast cancer treatment', 'PCOS polycystic ovary syndrome')"),
    max_results: int = Field(10, description="Maximum number of results to return (max: 100)", le=100)
) -> str:
    # Search PubMed
    search_results = search_pubmed(query, max_results)

    # Get summaries for the results
    summaries = get_article_summaries(search_results["pmids"])

    # Format the response
    response = f"# PubMed Search Results\n\n"
    response += f"Found {search_results['count']} articles for query: **'{query}'**\n\n"
    response += f"Showing top {len(summaries)} results:\n\n"

    for i, summary in enumerate(summaries, 1):
        response += f"## {i}. {summary['title']}\n\n"
        response += f"- **PMID:** {summary['pmid']}\n"
        response += f"- **Authors:** {', '.join(summary['authors'][:3])}"
        if len(summary['authors']) > 3:
            response += f" et al."
        response += f"\n- **Journal:** {summary['journal']}\n"
        response += f"- **Published:** {summary['pubdate']}\n"
        if summary['doi']:
            response += f"- **DOI:** {summary['doi']}\n"
        response += "\n"

    response += "💡 **Tip:** Use the 'get_article' tool with a PMID to retrieve the full abstract and details."

    return response


@mcp.tool(
    name="get_article",
    description="Retrieve full article details including title, abstract, authors, journal, publication date, DOI, and keywords for a specific PubMed article by PMID."
)
def get_article(
    pmid: str = Field(description="PubMed ID (PMID) of the article to retrieve")
) -> str:
    # Fetch article details
    article = fetch_article_abstract(pmid)

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
def get_multiple_articles(
    pmids: List[str] = Field(description="List of PubMed IDs to retrieve")
) -> str:
    # Fetch all articles
    articles = []
    for pmid in pmids:
        article = fetch_article_abstract(pmid)
        articles.append(article)
        # Be respectful of NCBI rate limits (3 requests/second without API key)
        if not NCBI_API_KEY:
            time.sleep(0.34)

    # Format the response
    response = f"# Multiple PubMed Articles\n\n"
    response += f"Retrieved {len(articles)} articles:\n\n"
    response += "---\n\n"

    for i, article in enumerate(articles, 1):
        response += f"## Article {i}: {article['title']}\n\n"
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
            response += f"### Abstract\n\n{article['abstract']}\n"
        else:
            response += "**Note:** Abstract not available for this article.\n"

        if i < len(articles):
            response += "\n---\n\n"

    return response


# ==================== Resources ====================

@mcp.resource("pubmed://search", mime_type="application/json")
def pubmed_search_info() -> dict:
    """Information about PubMed search capabilities."""
    return {
        "database": "PubMed (MEDLINE)",
        "search_capabilities": "Full-text search across scientific literature",
        "rate_limits": "3 requests/second without API key, 10/second with API key",
        "max_results": 100,
        "data_includes": ["abstracts", "authors", "journals", "publication_dates", "DOIs", "keywords"]
    }


# Run the server
if __name__ == "__main__":
    mcp.run()
