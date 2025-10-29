#!/usr/bin/env python
"""
NAMS Position Statements MCP Server - FastMCP Implementation

This MCP server provides tools to search and access NAMS (North American Menopause Society,
now The Menopause Society) position statements, clinical guidelines, and treatment protocols.
"""

from typing import Any, Optional
import requests
from bs4 import BeautifulSoup
import re
from fastmcp import FastMCP
from pydantic import Field

# NAMS URLs
NAMS_BASE_URL = "https://www.menopause.org"
POSITION_STATEMENTS_URL = f"{NAMS_BASE_URL}/publications/professional-publications/position-statements-other-reports"
PROFESSIONAL_RESOURCES_URL = f"{NAMS_BASE_URL}/professional-resources"

# Create FastMCP server
mcp = FastMCP("nams-server")

# Common headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def fetch_page(url: str) -> str:
    """
    Fetch a webpage and return its HTML content.

    Args:
        url: The URL to fetch

    Returns:
        HTML content as string
    """
    response = requests.get(url, headers=HEADERS, timeout=30.0, allow_redirects=True)
    response.raise_for_status()
    return response.text


def parse_position_statements() -> list[dict[str, Any]]:
    """
    Parse the position statements page to extract available documents.

    Returns:
        List of position statements with title, URL, and description
    """
    try:
        html = fetch_page(POSITION_STATEMENTS_URL)
        soup = BeautifulSoup(html, 'html.parser')

        statements = []

        # Find main content area
        main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))

        if main_content:
            # Look for position statement links
            # These typically have specific patterns in NAMS site
            links = main_content.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                # Skip navigation and empty links
                if not text or len(text) < 15:
                    continue

                # Look for PDF links and position statement pages
                if '.pdf' in href.lower() or 'position' in href.lower() or 'statement' in text.lower():
                    # Get full URL
                    if href.startswith('/'):
                        full_url = f"{NAMS_BASE_URL}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue

                    # Try to find description
                    description = ""
                    parent = link.find_parent(['div', 'article', 'section', 'p'])
                    if parent:
                        # Get surrounding text
                        parent_text = parent.get_text(strip=True)
                        # Extract meaningful description (not just the title)
                        if len(parent_text) > len(text) + 20:
                            description = parent_text[:300]

                    statements.append({
                        'title': text,
                        'url': full_url,
                        'description': description,
                        'type': 'position_statement' if 'position' in text.lower() else 'clinical_guideline'
                    })

        # Remove duplicates based on URL
        seen_urls = set()
        unique_statements = []
        for stmt in statements:
            if stmt['url'] not in seen_urls:
                seen_urls.add(stmt['url'])
                unique_statements.append(stmt)

        return unique_statements

    except Exception as e:
        # Return fallback list of known position statements
        return get_known_position_statements()


def get_known_position_statements() -> list[dict[str, Any]]:
    """
    Return a curated list of known NAMS position statements.
    This serves as a fallback when web scraping is blocked.
    """
    return [
        {
            'title': '2022 Hormone Therapy Position Statement',
            'url': 'https://menopause.org/wp-content/uploads/professional/nams-2022-hormone-therapy-position-statement.pdf',
            'description': 'The 2022 Hormone Therapy Position Statement provides the most up-to-date, scientifically based information on hormone therapy for menopausal symptoms.',
            'type': 'position_statement',
            'year': '2022',
            'topic': 'hormone therapy'
        },
        {
            'title': 'Recommendations for Clinical Care of Midlife Women',
            'url': 'https://www.menopause.org/docs/default-source/2014/nams-recomm-for-clinical-care.pdf',
            'description': 'Clinical care recommendations for midlife women covering various aspects of menopause management.',
            'type': 'clinical_guideline',
            'topic': 'general care'
        },
        {
            'title': 'Nonhormonal Management of Menopause-Associated Vasomotor Symptoms',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/nonhormonal-management',
            'description': 'Position statement on nonhormonal approaches to managing hot flashes and night sweats.',
            'type': 'position_statement',
            'topic': 'vasomotor symptoms'
        },
        {
            'title': 'Management of Osteoporosis in Postmenopausal Women',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/osteoporosis',
            'description': 'Guidelines for prevention and treatment of osteoporosis in postmenopausal women.',
            'type': 'position_statement',
            'topic': 'osteoporosis'
        },
        {
            'title': 'Genitourinary Syndrome of Menopause',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/genitourinary-syndrome',
            'description': 'Position statement on diagnosis and treatment of genitourinary symptoms of menopause.',
            'type': 'position_statement',
            'topic': 'genitourinary'
        },
        {
            'title': 'Treatment of Symptoms of the Menopause',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/treatment-symptoms',
            'description': 'Comprehensive position statement on evidence-based treatment approaches for menopausal symptoms.',
            'type': 'position_statement',
            'topic': 'symptom management'
        },
        {
            'title': 'Cardiovascular Disease and Menopause',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/cardiovascular-disease',
            'description': 'Position statement on cardiovascular health in menopausal women.',
            'type': 'position_statement',
            'topic': 'cardiovascular'
        },
        {
            'title': 'Role of Progestogen in Hormone Therapy',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/progestogen-hormone-therapy',
            'description': 'Clinical guidance on the use of progestogens in hormone therapy.',
            'type': 'clinical_guideline',
            'topic': 'hormone therapy'
        },
        {
            'title': 'Bioidentical Hormone Therapy',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/bioidentical-hormone-therapy',
            'description': 'Position statement on bioidentical hormones and compounded hormone therapy.',
            'type': 'position_statement',
            'topic': 'hormone therapy'
        },
        {
            'title': 'Management of Symptomatic Vulvovaginal Atrophy',
            'url': f'{NAMS_BASE_URL}/publications/clinical-practice-materials/vulvovaginal-atrophy',
            'description': 'Clinical recommendations for managing vulvovaginal atrophy in postmenopausal women.',
            'type': 'clinical_guideline',
            'topic': 'genitourinary'
        },
    ]


def search_protocols(query: str, topic: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Search NAMS protocols and position statements by keyword.

    Args:
        query: Search term
        topic: Optional topic filter

    Returns:
        List of matching documents
    """
    # Get all statements (try web scraping first, fall back to known list)
    all_docs = parse_position_statements()

    # If web scraping failed or returned few results, supplement with known statements
    if len(all_docs) < 5:
        known_docs = get_known_position_statements()
        # Merge, avoiding duplicates
        seen_urls = {doc['url'] for doc in all_docs}
        for doc in known_docs:
            if doc['url'] not in seen_urls:
                all_docs.append(doc)

    # Filter by query
    query_lower = query.lower()
    matching_docs = [
        doc for doc in all_docs
        if query_lower in doc['title'].lower() or
           (doc.get('description') and query_lower in doc['description'].lower()) or
           (doc.get('topic') and query_lower in doc['topic'].lower())
    ]

    # Filter by topic if provided
    if topic:
        topic_lower = topic.lower()
        matching_docs = [
            doc for doc in matching_docs
            if doc.get('topic') and topic_lower in doc['topic'].lower()
        ]

    return matching_docs


def get_protocol_content(url: str) -> dict[str, Any]:
    """
    Fetch the full content of a specific NAMS protocol or position statement.

    Args:
        url: URL of the document

    Returns:
        Dictionary with title, content, and metadata
    """
    # Handle PDFs differently
    if url.endswith('.pdf'):
        return {
            'title': 'PDF Document',
            'url': url,
            'content': 'This is a PDF document. Please download it directly from the URL to view the full content.',
            'content_type': 'pdf',
            'word_count': 0
        }

    html = fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Extract title
    title_elem = soup.find('h1')
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"

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

    # Extract metadata
    meta_date = soup.find('meta', {'name': 'date'}) or soup.find('time')
    date = meta_date.get('content', '') if meta_date and meta_date.has_attr('content') else (
        meta_date.get_text(strip=True) if meta_date else ""
    )

    return {
        'title': title,
        'url': url,
        'content': content_text,
        'content_type': 'html',
        'date': date,
        'word_count': len(content_text.split())
    }


# ==================== FastMCP Tools ====================

@mcp.tool(
    name="list_nams_position_statements",
    description="List available NAMS position statements and clinical guidelines on menopause management."
)
def list_nams_position_statements() -> str:
    statements = parse_position_statements()

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

    return result


@mcp.tool(
    name="search_nams_protocols",
    description="Search NAMS position statements and protocols by keyword or topic (e.g., 'hormone therapy', 'osteoporosis', 'vasomotor symptoms')."
)
def search_nams_protocols(
    query: str = Field(description="Search query (e.g., 'hormone therapy', 'hot flashes', 'bone health')"),
    topic: Optional[str] = Field(None, description="Optional topic filter (e.g., 'hormone therapy', 'cardiovascular', 'genitourinary')")
) -> str:
    results = search_protocols(query, topic)

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


@mcp.tool(
    name="get_protocol_content",
    description="Retrieve the full content of a specific NAMS protocol or position statement by URL."
)
def get_protocol_content_tool(
    url: str = Field(description="Full URL of the protocol or position statement")
) -> str:
    content = get_protocol_content(url)

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
def list_nams_topics() -> str:
    """
    List common topics covered by NAMS position statements.
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


# ==================== Resources ====================

@mcp.resource("nams://statements", mime_type="application/json")
def list_nams_resources() -> dict:
    """List all available NAMS resources."""
    return {
        "position_statements": "NAMS position statements and clinical guidelines",
        "topics": ["hormone therapy", "vasomotor symptoms", "osteoporosis", "cardiovascular", "genitourinary"],
        "search_capabilities": "Keyword and topic-based search across statements",
        "content_access": "Full text extraction with fallback mechanisms",
        "base_url": NAMS_BASE_URL
    }


# Run the server
if __name__ == "__main__":
    mcp.run()
