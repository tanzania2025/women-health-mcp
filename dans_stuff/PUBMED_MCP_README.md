# PubMed MCP Server

A Model Context Protocol (MCP) server that enables Claude to search PubMed for scientific articles and retrieve their full content including abstracts, metadata, and bibliographic information.

## Features

- **Search PubMed**: Search for scientific articles using natural language queries
- **Retrieve Articles**: Get full article details including abstracts, authors, journal info, DOIs, and keywords
- **Batch Retrieval**: Fetch multiple articles at once for comprehensive literature reviews
- **Rich Metadata**: Access publication dates, author lists, journal names, and more

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. Install the required dependencies:

```bash
# Use the same Python that Claude Desktop will use
/usr/local/bin/python3 -m pip install -r requirements.txt

# Or if python3 is in your PATH:
python3 -m pip install -r requirements.txt
```

2. (Optional but recommended) Get a free NCBI API key for higher rate limits:
   - Visit https://www.ncbi.nlm.nih.gov/account/
   - Register for a free account
   - Go to Settings → API Key Management
   - Generate an API key

3. If you have an API key, create or update your `.env` file:

```bash
NCBI_API_KEY=your_api_key_here
```

## Configuration for Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "/usr/local/bin/python3",
      "args": ["/Users/dgordon/womens_health_mcp/pubmed_server.py"],
      "env": {
        "NCBI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

If you don't have an API key, you can omit the `env` section:

```json
{
  "mcpServers": {
    "pubmed": {
      "command": "/usr/local/bin/python3",
      "args": ["/Users/dgordon/womens_health_mcp/pubmed_server.py"]
    }
  }
}
```

**Important**: Update the path in `args` to match the actual location of `pubmed_server.py` on your system.

After adding this configuration, restart Claude Desktop for the changes to take effect.

## Available Tools

### 1. search_pubmed

Search PubMed for articles matching a query.

**Parameters:**
- `query` (required): Search query string (e.g., "breast cancer treatment", "PCOS polycystic ovary syndrome")
- `max_results` (optional): Maximum number of results to return (default: 10, max: 100)

**Example usage in Claude:**
```
Search PubMed for recent articles on endometriosis treatment
```

### 2. get_article

Retrieve full details for a specific article by PMID.

**Parameters:**
- `pmid` (required): PubMed ID of the article

**Example usage in Claude:**
```
Get the full abstract for PubMed article 38765432
```

### 3. get_multiple_articles

Retrieve details for multiple articles at once.

**Parameters:**
- `pmids` (required): Array of PubMed IDs

**Example usage in Claude:**
```
Get the full details for articles 38765432, 38654321, and 38543210
```

## Usage Examples

### Basic Search

```
Search PubMed for articles about "women's health and reproductive outcomes"
```

This will return up to 10 articles with titles, authors, journal names, and PMIDs.

### Targeted Search with Retrieval

```
Search PubMed for the 5 most recent articles on "polycystic ovary syndrome PCOS" and then retrieve the full abstracts for the top 3 results
```

This will first search, then automatically retrieve the detailed information including abstracts.

### Literature Review

```
I'm researching endometriosis. Can you search PubMed for recent review articles and then get the full abstracts for the most relevant ones?
```

Claude will search, evaluate the results, and retrieve the most relevant articles for your review.

## Rate Limits

- **Without API Key**: 3 requests per second
- **With API Key**: 10 requests per second

The server automatically respects these limits to avoid being blocked by NCBI.

## Data Available

For each article, you can access:

- **Title**: Full article title
- **PMID**: PubMed unique identifier
- **DOI**: Digital Object Identifier (when available)
- **Abstract**: Full structured abstract
- **Authors**: Complete author list
- **Journal**: Full journal name
- **Publication Date**: Date of publication
- **Keywords**: Article keywords/MeSH terms

## Notes

- **Full Text**: This server retrieves abstracts and metadata. Full-text PDFs are not available through PubMed's API (they're usually behind publisher paywalls).
- **Open Access**: For open-access articles, you can use the DOI to find free full-text versions via PubMed Central or publisher websites.
- **Rate Limiting**: The server includes automatic rate limiting to comply with NCBI usage policies.

## Troubleshooting

### Server Not Appearing in Claude

1. Check that the path in `claude_desktop_config.json` is correct
2. Ensure Python is installed and accessible via the `python` command
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for error messages

### API Rate Limiting

If you're hitting rate limits:
1. Get a free NCBI API key (see Setup section)
2. Add it to your configuration
3. Restart Claude Desktop

### No Results Found

- Try broader search terms
- Use MeSH terms for more precise medical searches
- Check spelling and terminology

## Advanced Search Tips

PubMed supports advanced search syntax:

- **Phrase search**: Use quotes: `"ovarian cancer"`
- **Field-specific**: `Smith J[Author]`, `Cancer[Title]`
- **Date range**: `2020:2024[pdat]`
- **Boolean operators**: `AND`, `OR`, `NOT`

Example: `"breast cancer"[Title] AND "machine learning"[Title/Abstract] AND 2023:2024[pdat]`

## License

This MCP server uses NCBI's E-utilities API. Please follow NCBI's usage guidelines:
https://www.ncbi.nlm.nih.gov/books/NBK25497/

## Support

For issues specific to this MCP server, please check:
- Claude Desktop configuration
- Python installation and dependencies
- NCBI API key configuration (if using)

For questions about PubMed search syntax and capabilities, refer to:
https://pubmed.ncbi.nlm.nih.gov/help/
