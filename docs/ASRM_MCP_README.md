# ASRM Practice Guidance MCP Server

An MCP (Model Context Protocol) server that provides access to ASRM (American Society for Reproductive Medicine) practice guidance documents, committee opinions, ethics opinions, and clinical resources.

## Features

This server enables Claude to:

1. **List Practice Documents** - Browse available ASRM practice committee documents and clinical guidelines
2. **List Ethics Opinions** - Browse ASRM ethics committee opinions
3. **Search Guidelines** - Search for specific topics across all ASRM guidance documents
4. **Retrieve Full Content** - Fetch and read the complete text of any guideline document

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `mcp>=0.9.0` - Model Context Protocol
- `httpx>=0.27.0` - HTTP client for fetching web pages
- `beautifulsoup4>=4.12.0` - HTML parsing

### 2. Configure Claude Desktop

Add the ASRM server to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "asrm-practice-guidance": {
      "command": "python",
      "args": [
        "/FULL/PATH/TO/womens_health_mcp/asrm_server.py"
      ]
    }
  }
}
```

**Important**: Replace `/FULL/PATH/TO/` with the actual path to your `womens_health_mcp` directory.

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Available Tools

### 1. list_practice_documents

Lists all available ASRM practice committee documents and guidelines.

**Example usage in Claude:**
```
Can you list the available ASRM practice documents?
```

### 2. list_ethics_opinions

Lists all available ASRM ethics committee opinions.

**Example usage in Claude:**
```
Show me the ASRM ethics opinions
```

### 3. search_asrm_guidelines

Search for guidelines by keyword, optionally filtered by category (practice or ethics).

**Parameters:**
- `query` (required): Search term (e.g., "IVF", "endometriosis", "genetic testing")
- `category` (optional): Filter by "practice" or "ethics"

**Example usage in Claude:**
```
Search ASRM guidelines for "premature ovarian insufficiency"
Find ASRM ethics opinions about "egg donation"
```

### 4. get_guideline_content

Retrieve the full content of a specific guideline document by URL.

**Parameters:**
- `url` (required): Full URL of the guideline document

**Example usage in Claude:**
```
Get the full content of the ASRM guideline at https://www.asrm.org/practice-guidance/practice-committee-documents/...
```

## Example Workflows

### Finding Guidelines on a Specific Topic

```
User: I need information about IVF success rates for women over 40
Claude: [Uses search_asrm_guidelines with query "IVF age 40"]
Claude: [Presents relevant documents found]
Claude: [Uses get_guideline_content to retrieve full text of most relevant guideline]
Claude: [Provides evidence-based summary from the guideline]
```

### Reviewing Ethics Guidance

```
User: What are the ethical considerations for posthumous reproduction?
Claude: [Uses list_ethics_opinions or search_asrm_guidelines with category="ethics"]
Claude: [Retrieves relevant ethics opinion content]
Claude: [Summarizes the ethical framework and recommendations]
```

## Document Types Available

- **Practice Committee Documents**: Evidence-based clinical guidelines and committee opinions
- **Ethics Committee Opinions**: Ethical guidance on reproductive medicine practices
- **COVID-19 Resources**: Pandemic-specific guidance (via practice guidance section)
- **Coding Resources**: Clinical coding guidance and documentation

## Technical Details

### How It Works

1. **Web Scraping**: The server fetches ASRM web pages using `httpx`
2. **HTML Parsing**: Uses BeautifulSoup to extract document listings and content
3. **Content Extraction**: Intelligently parses guideline documents to extract:
   - Titles and headings
   - Full text content
   - Publication dates
   - Descriptions and metadata

### Rate Limiting

The server makes direct HTTP requests to ASRM's public website. Be mindful of:
- Not making excessive requests in short time periods
- Caching results when possible
- ASRM's website terms of service

## Troubleshooting

### Server Not Appearing in Claude

1. Check that the path in `claude_desktop_config.json` is absolute and correct
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for error messages

### No Results When Searching

1. Try different search terms (ASRM uses medical terminology)
2. Try browsing with `list_practice_documents` or `list_ethics_opinions` first
3. Check that the ASRM website is accessible from your network

### Content Not Fully Retrieved

Some ASRM documents may require authentication or have access restrictions. The server can only access publicly available content.

## Use Cases in Women's Health

This server is particularly useful for:

- **Clinical Decision Support**: Access evidence-based guidelines during patient consultations
- **Research & Literature Review**: Find ASRM position statements and committee opinions
- **Medical Education**: Reference authoritative reproductive medicine guidance
- **Protocol Development**: Use ASRM guidelines to inform clinical protocols
- **Ethics Consultation**: Reference ethics opinions for complex cases

## Limitations

- Only accesses publicly available ASRM content
- Some documents may require ASRM membership to view in full
- Content freshness depends on ASRM website updates
- Web scraping is dependent on ASRM's website structure (may need updates if their site changes)

## Related MCP Servers

This server works well alongside:
- **PubMed MCP Server**: For searching scientific literature
- **SART IVF Calculator MCP Server**: For IVF success rate calculations

## Contributing

If you find issues or want to enhance the server:
1. ASRM website structure changes may require parser updates
2. Additional document types could be added (coding resources, patient education)
3. Caching could improve performance

## License

This server is for educational and clinical research purposes. Always verify information with original ASRM sources and consult the ASRM website terms of service.

## Resources

- ASRM Website: https://www.asrm.org
- ASRM Practice Guidance: https://www.asrm.org/practice-guidance/
- Model Context Protocol: https://modelcontextprotocol.io
