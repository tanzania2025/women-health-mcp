#!/usr/bin/env python3
"""
PubMed MCP Server

This MCP server provides tools to search PubMed for scientific articles
and retrieve their content for analysis by Claude.
"""

import os
import asyncio
from typing import Any, Optional
import httpx
from xml.etree import ElementTree as ET
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# NCBI E-utilities base URLs
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Get API key from environment (optional but recommended for higher rate limits)
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

# Create server instance
server = Server("pubmed-server")


async def search_pubmed(query: str, max_results: int = 10) -> dict[str, Any]:
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

    async with httpx.AsyncClient() as client:
        response = await client.get(ESEARCH_URL, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        return {
            "count": int(data["esearchresult"]["count"]),
            "pmids": data["esearchresult"]["idlist"],
            "query": query
        }


async def get_article_summaries(pmids: list[str]) -> list[dict[str, Any]]:
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

    async with httpx.AsyncClient() as client:
        response = await client.get(ESUMMARY_URL, params=params, timeout=30.0)
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


async def fetch_article_abstract(pmid: str) -> dict[str, Any]:
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

    async with httpx.AsyncClient() as client:
        response = await client.get(EFETCH_URL, params=params, timeout=30.0)
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


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for PubMed search and retrieval.
    """
    return [
        types.Tool(
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
        types.Tool(
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
        types.Tool(
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
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "search_pubmed":
        query = arguments.get("query")
        if not query:
            raise ValueError("Missing required argument: query")

        max_results = min(int(arguments.get("max_results", 10)), 100)

        # Search PubMed
        search_results = await search_pubmed(query, max_results)

        # Get summaries for the results
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

        return [types.TextContent(type="text", text=response)]

    elif name == "get_article":
        pmid = arguments.get("pmid")
        if not pmid:
            raise ValueError("Missing required argument: pmid")

        # Fetch article details
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

        return [types.TextContent(type="text", text=response)]

    elif name == "get_multiple_articles":
        pmids = arguments.get("pmids")
        if not pmids:
            raise ValueError("Missing required argument: pmids")

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

        return [types.TextContent(type="text", text=response)]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the PubMed MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pubmed-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
