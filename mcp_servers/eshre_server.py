#!/usr/bin/env python3
"""
ESHRE Guidelines MCP Server

This MCP server provides tools to search and access ESHRE (European Society
for Human Reproduction and Embryology) clinical guidelines and recommendations.
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

# ESHRE URLs
ESHRE_BASE_URL = "https://www.eshre.eu"
GUIDELINES_URL = f"{ESHRE_BASE_URL}/Guidelines-and-Legal"

# Create server instance
server = Server("eshre-server")


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


async def parse_guidelines_list() -> list[dict[str, Any]]:
    """
    Parse the guidelines page to extract available guidelines.

    Returns:
        List of guidelines with title, URL, and description
    """
    html = await fetch_page(GUIDELINES_URL)
    soup = BeautifulSoup(html, 'html.parser')

    guidelines = []

    # Find all guideline links
    main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))

    # Look for all links to guidelines pages - search the whole soup for better results
    links = soup.find_all('a', href=re.compile(r'/Guidelines-and-Legal/Guidelines/[^/]+$'))

    for link in links:
        href = link.get('href', '')

        # Skip category pages and filter links
        if href in ['/Guidelines-and-Legal/Guidelines', '/en/Guidelines-and-Legal', '/Guidelines-and-Legal']:
            continue

        # Skip development process and guidelines-in-development pages
        if any(skip in href for skip in ['Guideline-development-process', 'Guidelines-in-development']):
            continue

        # Get full URL
        if href.startswith('/'):
            full_url = f"{ESHRE_BASE_URL}{href}"
        else:
            full_url = href

        # Get title from the link or nearby h4
        title = ""
        parent = link.find_parent(['div', 'article', 'section'])

        # Look for h4 or title in the link structure
        h4 = parent.find('h4') if parent else None
        if h4:
            title = h4.get_text(strip=True)
        else:
            title = link.get_text(strip=True)

        # Try to find description
        description = ""
        if parent:
            # Look for paragraph or description text near the link
            paragraphs = parent.find_all('p')
            for p in paragraphs:
                p_text = p.get_text(strip=True)
                # Skip empty or very short paragraphs
                if p_text and len(p_text) > 20 and p_text != title:
                    description = p_text
                    break

        # Extract the guideline ID from URL
        guideline_id = href.split('/')[-1]

        # Only add if we have a meaningful title
        if title and len(title) > 2:
            guidelines.append({
                'id': guideline_id,
                'title': title,
                'url': full_url,
                'description': description
            })

    # Remove duplicates based on URL
    seen_urls = set()
    unique_guidelines = []
    for guideline in guidelines:
        if guideline['url'] not in seen_urls:
            seen_urls.add(guideline['url'])
            unique_guidelines.append(guideline)

    return unique_guidelines


async def search_guidelines(query: str) -> list[dict[str, Any]]:
    """
    Search ESHRE guidelines by keyword.

    Args:
        query: Search term

    Returns:
        List of matching guidelines
    """
    all_guidelines = await parse_guidelines_list()

    # Filter by query
    query_lower = query.lower()
    matching_guidelines = [
        guideline for guideline in all_guidelines
        if query_lower in guideline['title'].lower() or
           (guideline['description'] and query_lower in guideline['description'].lower())
    ]

    return matching_guidelines


async def get_guideline_content(url: str) -> dict[str, Any]:
    """
    Fetch the full content of a specific guideline document.

    Args:
        url: URL of the guideline

    Returns:
        Dictionary with title, content, metadata, and download links
    """
    html = await fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Extract title
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"

    # Extract publication date
    date = ""
    # Look for "Issued:" or date patterns
    for p in soup.find_all('p'):
        p_text = p.get_text(strip=True)
        if p_text.startswith('Issued:'):
            date = p_text.replace('Issued:', '').strip()
            break

    # Extract main content
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

    # Extract download links
    download_links = []
    download_section = soup.find_all('a', href=re.compile(r'\.pdf$'))

    for link in download_section:
        href = link.get('href', '')
        if href:
            # Get full URL
            if href.startswith('/'):
                pdf_url = f"{ESHRE_BASE_URL}{href}"
            else:
                pdf_url = href

            # Get link text or parent text
            link_text = link.get_text(strip=True)
            if not link_text or link_text == "":
                # Try to find text in parent or sibling elements
                parent = link.find_parent(['div', 'p', 'li'])
                if parent:
                    link_text = parent.get_text(strip=True)

            # Clean up link text
            if link_text and "Download" in link_text:
                link_text = link_text.replace("Download", "").strip()

            if pdf_url not in [dl['url'] for dl in download_links]:
                download_links.append({
                    'title': link_text or 'PDF Document',
                    'url': pdf_url
                })

    return {
        'title': title,
        'url': url,
        'date': date,
        'content': content_text,
        'downloads': download_links,
        'word_count': len(content_text.split())
    }


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="list_eshre_guidelines",
            description="List all available ESHRE clinical guidelines and recommendations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
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
        types.Tool(
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
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    """
    try:
        if name == "list_eshre_guidelines":
            guidelines = await parse_guidelines_list()

            result = "# ESHRE Clinical Guidelines\n\n"
            result += f"Found {len(guidelines)} clinical guidelines:\n\n"

            for i, guideline in enumerate(guidelines, 1):
                result += f"{i}. **{guideline['title']}**\n"
                if guideline['description']:
                    result += f"   {guideline['description']}\n"
                result += f"   URL: {guideline['url']}\n\n"

            return [types.TextContent(type="text", text=result)]

        elif name == "search_eshre_guidelines":
            if not arguments or "query" not in arguments:
                raise ValueError("query parameter is required")

            query = arguments["query"]
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

            return [types.TextContent(type="text", text=result)]

        elif name == "get_eshre_guideline":
            if not arguments or "url" not in arguments:
                raise ValueError("url parameter is required")

            url = arguments["url"]
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
    Main entry point for the ESHRE MCP server.
    """
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eshre-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
