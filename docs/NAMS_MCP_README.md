# NAMS Position Statements MCP Server

An MCP (Model Context Protocol) server that provides access to NAMS (North American Menopause Society, now The Menopause Society) position statements, clinical guidelines, and treatment protocols for menopause management.

## Overview

The NAMS MCP server allows AI assistants to search, retrieve, and reference evidence-based clinical guidelines from The Menopause Society. This includes position statements on hormone therapy, symptom management, bone health, cardiovascular care, and other menopause-related topics.

## Features

- **List Position Statements**: Browse all available NAMS position statements and clinical guidelines
- **Search by Keyword**: Find relevant protocols using keywords or medical terms
- **Topic Filtering**: Filter results by specific topics (hormone therapy, cardiovascular, etc.)
- **Retrieve Full Content**: Access complete position statement content
- **Fallback Data**: Includes curated list of known position statements when web access is limited

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages (install via requirements.txt):
  - `mcp`
  - `httpx`
  - `beautifulsoup4`

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add to Claude Desktop configuration:

Edit `/Users/dgordon/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nams-protocols": {
      "command": "/Users/dgordon/anaconda3/bin/python",
      "args": [
        "/Users/dgordon/womens_health_mcp/nams_server.py"
      ]
    }
  }
}
```

3. Restart Claude Desktop to load the server.

## Available Tools

### 1. list_nams_position_statements

Lists all available NAMS position statements and clinical guidelines.

**Usage:**
```
Use the list_nams_position_statements tool
```

**Returns:** Complete list of position statements with titles, URLs, topics, and descriptions.

### 2. search_nams_protocols

Search position statements by keyword or topic.

**Parameters:**
- `query` (required): Search term (e.g., "hormone therapy", "hot flashes", "bone health")
- `topic` (optional): Topic filter (e.g., "hormone therapy", "cardiovascular", "genitourinary")

**Usage:**
```
Search NAMS protocols for "vasomotor symptoms"
Search NAMS protocols for "management" with topic "hormone therapy"
```

**Returns:** Matching position statements with relevance to the search query.

### 3. get_protocol_content

Retrieve the full content of a specific position statement.

**Parameters:**
- `url` (required): Full URL of the position statement

**Usage:**
```
Get the content from https://menopause.org/wp-content/uploads/professional/nams-2022-hormone-therapy-position-statement.pdf
```

**Returns:** Full text content, metadata, and document information.

**Note:** PDF documents return metadata and download information rather than full text extraction.

### 4. list_nams_topics

Lists common topics covered by NAMS position statements.

**Usage:**
```
List NAMS topics
```

**Returns:** Organized list of clinical topics with coverage in NAMS guidelines.

## Common Topics

NAMS position statements cover these key areas:

- **Hormone Therapy**: Indications, risks, benefits, and management
- **Vasomotor Symptoms**: Hot flashes, night sweats
- **Genitourinary Syndrome**: Vaginal atrophy, urinary symptoms
- **Osteoporosis**: Bone health and fracture prevention
- **Cardiovascular Health**: Heart disease risk and management
- **Sexual Health**: Libido, sexual function
- **Mood and Cognition**: Depression, memory, cognitive function
- **Sleep Disorders**: Insomnia and sleep quality
- **Nonhormonal Therapies**: Alternative treatment options
- **Bioidentical Hormones**: Compounded hormone therapy
- **Premature Menopause**: Early menopause management

## Example Queries

### Finding Hormone Therapy Guidelines
```
Search NAMS protocols for "hormone therapy"
```

### Managing Vasomotor Symptoms
```
Search NAMS protocols for "hot flashes"
Search NAMS protocols for "night sweats"
```

### Bone Health
```
Search NAMS protocols for "osteoporosis"
Search NAMS protocols for "bone density"
```

### Cardiovascular Care
```
Search NAMS protocols for "cardiovascular" with topic "cardiovascular"
```

### Genitourinary Symptoms
```
Search NAMS protocols for "vaginal atrophy"
Search NAMS protocols for "genitourinary syndrome"
```

## Key Position Statements

The server includes access to major NAMS position statements:

1. **2022 Hormone Therapy Position Statement** - Comprehensive guidance on hormone therapy use
2. **Nonhormonal Management of Vasomotor Symptoms** - Evidence-based nonhormonal approaches
3. **Genitourinary Syndrome of Menopause** - Diagnosis and treatment guidelines
4. **Management of Osteoporosis** - Bone health in postmenopausal women
5. **Cardiovascular Disease and Menopause** - Heart health guidance
6. **Bioidentical Hormone Therapy** - Position on compounded hormones
7. **Treatment of Menopausal Symptoms** - General symptom management

## Technical Details

### Web Scraping

The server attempts to scrape the NAMS website for the most current position statements. If web access is blocked or unavailable, it falls back to a curated list of known position statements.

### Rate Limiting

The server uses appropriate user-agent headers and follows web scraping best practices. However, the NAMS website may block automated access. The fallback mechanism ensures continued functionality.

### Content Handling

- **HTML Pages**: Full text extraction with structure preservation
- **PDF Documents**: Metadata and download information (PDFs require manual download)
- **Dynamic Content**: May have limited access depending on website structure

## Testing

Run the test suite:

```bash
python test_nams.py
```

The test suite verifies:
- Position statement parsing
- Search functionality
- Topic filtering
- Content retrieval
- Fallback mechanisms
- End-to-end workflows

## Troubleshooting

### Server Not Appearing in Claude

1. Check that the path in `claude_desktop_config.json` is correct
2. Verify Python executable path: `which python`
3. Restart Claude Desktop completely
4. Check logs in Claude Desktop developer tools

### Search Returns No Results

- Try broader search terms
- Use the `list_nams_position_statements` tool to browse all available content
- Check the `list_nams_topics` tool for valid topic names

### Web Scraping Blocked

The server includes a fallback list of known position statements. If web scraping fails, the server will automatically use this curated list to provide core functionality.

## Data Sources

- **Primary Source**: https://www.menopause.org/publications/professional-publications/position-statements-other-reports
- **Position Statements**: Official NAMS/Menopause Society publications
- **Clinical Guidelines**: Evidence-based recommendations from expert panels

## Updates

NAMS position statements are updated periodically as new evidence emerges. The most current versions are available on the NAMS website. The fallback list in this server may need periodic updates to reflect new publications.

## Limitations

- PDF content extraction is limited (direct download recommended)
- Some content may require NAMS membership or subscription
- Web scraping may be blocked by site protection mechanisms
- Content depends on NAMS website structure (subject to change)

## Clinical Use

This tool is designed to help healthcare providers access evidence-based guidelines. It should be used as a reference tool alongside clinical judgment and patient-specific considerations.

**Note**: Always verify information with the primary source and use current clinical guidelines in practice.

## License

This MCP server is provided for educational and clinical reference purposes. NAMS position statements remain the intellectual property of The Menopause Society.

## Support

For issues with:
- **Server functionality**: Check test results and configuration
- **NAMS guidelines**: Visit https://www.menopause.org
- **MCP protocol**: See https://modelcontextprotocol.io

## Version

Current version: 0.1.0

## Author

Created as part of the Women's Health MCP project for integrating clinical guidelines into AI-assisted healthcare workflows.
