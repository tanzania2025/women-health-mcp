#!/usr/bin/env python3
"""
ASRM Practice Guidance MCP Server

This MCP server provides tools to search and access ASRM (American Society for
Reproductive Medicine) practice guidance documents, committee opinions, ethics
opinions, and other clinical resources.
"""

import os
import asyncio
from typing import Any, Optional
import httpx
from bs4 import BeautifulSoup
import re
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# ASRM URLs
ASRM_BASE_URL = "https://www.asrm.org"
PRACTICE_GUIDANCE_URL = f"{ASRM_BASE_URL}/practice-guidance/"
PRACTICE_DOCUMENTS_URL = f"{ASRM_BASE_URL}/practice-guidance/practice-committee-documents/"
ETHICS_OPINIONS_URL = f"{ASRM_BASE_URL}/practice-guidance/ethics-opinions/"

# Create server instance
server = Server("asrm-server")


async def fetch_page(url: str) -> str:
    """
    Fetch a webpage and return its HTML content.

    Args:
        url: The URL to fetch

    Returns:
        HTML content as string
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.text


async def parse_practice_documents() -> list[dict[str, Any]]:
    """
    Parse the practice guidance page to extract available documents.

    Returns:
        List of documents with title, URL, and description
    """
    html = await fetch_page(PRACTICE_GUIDANCE_URL)
    soup = BeautifulSoup(html, 'html.parser')

    documents = []

    # Find all document listings
    # Look for links to actual practice documents (they have longer paths)
    main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))

    if main_content:
        # Look for article links - these are typically practice documents
        links = main_content.find_all('a', href=re.compile(r'/practice-guidance/practice-committee-documents/[a-z0-9-]+'))

        for link in links:
            href = link.get('href', '')

            # Skip the category page itself and filter links
            if href.endswith('/practice-committee-documents/') or '?s=' in href:
                continue

            # Skip navigation links, patient resources, etc.
            if any(skip in href for skip in ['patient-education', 'coding', 'covid', 'emr']):
                continue

            # Get full URL
            if href.startswith('/'):
                full_url = f"{ASRM_BASE_URL}{href}"
            else:
                full_url = href

            # Get title
            title = link.get_text(strip=True)

            # Try to find description (usually in nearby text)
            description = ""
            parent = link.find_parent(['div', 'article', 'section'])
            if parent:
                # Look for paragraph or description text near the link
                paragraphs = parent.find_all('p')
                for p in paragraphs:
                    p_text = p.get_text(strip=True)
                    # Skip empty or very short paragraphs
                    if p_text and len(p_text) > 20 and p_text != title:
                        description = p_text
                        break

            # Only add if we have a meaningful title (not just navigation)
            if title and len(title) > 15 and 'filter' not in title.lower():
                documents.append({
                    'title': title,
                    'url': full_url,
                    'description': description,
                    'type': 'practice_document'
                })

    # Remove duplicates based on URL
    seen_urls = set()
    unique_documents = []
    for doc in documents:
        if doc['url'] not in seen_urls:
            seen_urls.add(doc['url'])
            unique_documents.append(doc)

    return unique_documents


async def parse_ethics_opinions() -> list[dict[str, Any]]:
    """
    Parse the ethics opinions page to extract available opinions.

    Returns:
        List of ethics opinions with title, URL, and description
    """
    html = await fetch_page(PRACTICE_GUIDANCE_URL)
    soup = BeautifulSoup(html, 'html.parser')

    opinions = []

    main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))

    if main_content:
        # Look for links to actual ethics opinions (they have longer paths)
        links = main_content.find_all('a', href=re.compile(r'/practice-guidance/ethics-opinions/[a-z0-9-]+'))

        for link in links:
            href = link.get('href', '')

            # Skip the category page itself and filter links
            if href.endswith('/ethics-opinions/') or '?s=' in href:
                continue

            if href.startswith('/'):
                full_url = f"{ASRM_BASE_URL}{href}"
            else:
                full_url = href

            title = link.get_text(strip=True)

            description = ""
            parent = link.find_parent(['div', 'article', 'section'])
            if parent:
                paragraphs = parent.find_all('p')
                for p in paragraphs:
                    p_text = p.get_text(strip=True)
                    if p_text and len(p_text) > 20 and p_text != title:
                        description = p_text
                        break

            if title and len(title) > 15 and 'filter' not in title.lower():
                opinions.append({
                    'title': title,
                    'url': full_url,
                    'description': description,
                    'type': 'ethics_opinion'
                })

    # Remove duplicates
    seen_urls = set()
    unique_opinions = []
    for op in opinions:
        if op['url'] not in seen_urls:
            seen_urls.add(op['url'])
            unique_opinions.append(op)

    return unique_opinions


async def search_guidelines(query: str, category: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Search ASRM guidelines by keyword.

    Args:
        query: Search term
        category: Optional category filter ('practice', 'ethics', or None for all)

    Returns:
        List of matching documents
    """
    all_docs = []

    # Fetch based on category
    if category is None or category.lower() == 'practice':
        practice_docs = await parse_practice_documents()
        all_docs.extend(practice_docs)

    if category is None or category.lower() == 'ethics':
        ethics_docs = await parse_ethics_opinions()
        all_docs.extend(ethics_docs)

    # Filter by query
    query_lower = query.lower()
    matching_docs = [
        doc for doc in all_docs
        if query_lower in doc['title'].lower() or
           (doc['description'] and query_lower in doc['description'].lower())
    ]

    return matching_docs


async def get_guideline_content(url: str) -> dict[str, Any]:
    """
    Fetch the full content of a specific guideline document.

    Args:
        url: URL of the guideline

    Returns:
        Dictionary with title, content, and metadata
    """
    html = await fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Extract title
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"

    # Extract main content
    # ASRM uses various content containers
    content_elem = (
        soup.find('main') or
        soup.find('article') or
        soup.find('div', class_=re.compile(r'content|article|body'))
    )

    content_text = ""
    if content_elem:
        # Remove navigation, headers, footers
        for unwanted in content_elem.find_all(['nav', 'header', 'footer', 'script', 'style']):
            unwanted.decompose()

        # Get text with preserved structure
        paragraphs = content_elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
        content_parts = []

        for para in paragraphs:
            text = para.get_text(strip=True)
            if text:
                # Add formatting for headings
                if para.name in ['h1', 'h2', 'h3', 'h4']:
                    content_parts.append(f"\n## {text}\n")
                else:
                    content_parts.append(text)

        content_text = "\n\n".join(content_parts)

    # Extract metadata
    meta_date = soup.find('meta', {'name': 'date'}) or soup.find('time')
    date = meta_date.get('content', '') if meta_date and meta_date.has_attr('content') else (
        meta_date.get_text(strip=True) if meta_date else ""
    )

    return {
        'title': title,
        'url': url,
        'content': content_text,
        'date': date,
        'word_count': len(content_text.split())
    }


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="list_practice_documents",
            description="List available ASRM practice committee documents and guidelines",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="list_ethics_opinions",
            description="List available ASRM ethics committee opinions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="search_asrm_guidelines",
            description="Search ASRM guidelines by keyword. Can filter by category (practice or ethics).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'IVF', 'endometriosis', 'genetic testing')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: 'practice' or 'ethics'",
                        "enum": ["practice", "ethics"]
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="get_guideline_content",
            description="Retrieve the full content of a specific ASRM guideline document by URL",
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
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    try:
        if name == "list_practice_documents":
            documents = await parse_practice_documents()

            result = "# ASRM Practice Documents\n\n"
            result += f"Found {len(documents)} practice documents:\n\n"

            for i, doc in enumerate(documents[:20], 1):  # Limit to 20 for readability
                result += f"{i}. **{doc['title']}**\n"
                if doc['description']:
                    result += f"   {doc['description']}\n"
                result += f"   URL: {doc['url']}\n\n"

            if len(documents) > 20:
                result += f"\n...and {len(documents) - 20} more documents.\n"

            return [types.TextContent(type="text", text=result)]

        elif name == "list_ethics_opinions":
            opinions = await parse_ethics_opinions()

            result = "# ASRM Ethics Opinions\n\n"
            result += f"Found {len(opinions)} ethics opinions:\n\n"

            for i, op in enumerate(opinions[:20], 1):
                result += f"{i}. **{op['title']}**\n"
                if op['description']:
                    result += f"   {op['description']}\n"
                result += f"   URL: {op['url']}\n\n"

            if len(opinions) > 20:
                result += f"\n...and {len(opinions) - 20} more opinions.\n"

            return [types.TextContent(type="text", text=result)]

        elif name == "search_asrm_guidelines":
            if not arguments or "query" not in arguments:
                raise ValueError("query parameter is required")

            query = arguments["query"]
            category = arguments.get("category")

            results = await search_guidelines(query, category)

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
                result += "Try different keywords or browse all documents using list_practice_documents or list_ethics_opinions.\n"

            return [types.TextContent(type="text", text=result)]

        elif name == "get_guideline_content":
            if not arguments or "url" not in arguments:
                raise ValueError("url parameter is required")

            url = arguments["url"]
            content = await get_guideline_content(url)

            result = f"# {content['title']}\n\n"
            result += f"**URL:** {content['url']}\n"
            if content['date']:
                result += f"**Date:** {content['date']}\n"
            result += f"**Word Count:** {content['word_count']}\n\n"
            result += "---\n\n"
            result += content['content']

            return [types.TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """
    Main entry point for the ASRM MCP server.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="asrm-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
