# ESHRE Guidelines MCP Server

An MCP (Model Context Protocol) server that provides access to ESHRE (European Society for Human Reproduction and Embryology) clinical guidelines and recommendations.

## Overview

The ESHRE Guidelines MCP Server enables AI assistants like Claude to search, retrieve, and provide information from official ESHRE clinical practice guidelines. These guidelines cover topics in reproductive medicine including:

- Endometriosis
- IVF/ICSI and ovarian stimulation
- PCOS (Polycystic Ovary Syndrome)
- Fertility preservation
- Recurrent pregnancy loss
- Premature ovarian insufficiency
- PGT (Preimplantation Genetic Testing)
- And many more reproductive health topics

## Features

The server provides three main tools:

1. **list_eshre_guidelines** - List all available ESHRE clinical guidelines
2. **search_eshre_guidelines** - Search guidelines by keyword or topic
3. **get_eshre_guideline** - Retrieve full guideline content and download links

## Installation

### Prerequisites

- Python 3.10 or higher
- Required Python packages (install via requirements.txt)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

The requirements include:
- `mcp` - Model Context Protocol SDK
- `httpx` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

2. Make the server executable:
```bash
chmod +x eshre_server.py
```

## Configuration

### Claude Desktop

Add the following to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "eshre-guidelines": {
      "command": "/path/to/your/python",
      "args": [
        "/path/to/womens_health_mcp/eshre_server.py"
      ]
    }
  }
}
```

Example with Anaconda Python:
```json
{
  "mcpServers": {
    "eshre-guidelines": {
      "command": "/Users/dgordon/anaconda3/bin/python",
      "args": [
        "/Users/dgordon/womens_health_mcp/eshre_server.py"
      ]
    }
  }
}
```

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Usage

Once configured, you can use the ESHRE server through Claude Desktop. Here are some example queries:

### List All Guidelines
```
Can you list all available ESHRE guidelines?
```

### Search for Specific Topics
```
Search ESHRE guidelines for endometriosis
```

```
Find ESHRE guidelines about fertility preservation
```

```
What ESHRE guidelines are available for PCOS?
```

### Get Guideline Content
```
Get the full ESHRE guideline on endometriosis
```

```
Show me the ESHRE guideline for ovarian stimulation in IVF
```

## Available Tools

### 1. list_eshre_guidelines

Lists all available ESHRE clinical guidelines.

**Parameters:** None

**Returns:** A formatted list of all guidelines with titles, descriptions, and URLs.

### 2. search_eshre_guidelines

Searches ESHRE guidelines by keyword or topic.

**Parameters:**
- `query` (string, required): Search term (e.g., "endometriosis", "IVF", "PCOS")

**Returns:** A list of matching guidelines with titles, descriptions, and URLs.

### 3. get_eshre_guideline

Retrieves the full content of a specific guideline.

**Parameters:**
- `url` (string, required): Full URL of the guideline document

**Returns:** Complete guideline information including:
- Title
- Publication date
- Full text content
- Download links (PDFs for full guidelines, patient versions, evidence tables, etc.)
- Word count

## Testing

Run the test suite to verify the server is working correctly:

```bash
python test_eshre.py
```

The test suite will:
1. List all available guidelines
2. Search for several common topics
3. Retrieve and display content from a sample guideline

## Examples

### Example 1: Finding Guidelines on Endometriosis

**User:** "What ESHRE guidelines are available for endometriosis?"

**Response:** The server will search for and return all guidelines related to endometriosis, including:
- ESHRE Guideline: Endometriosis
- Surgery in Endometriosis
- Classification for endometriosis

### Example 2: Getting Full Guideline Content

**User:** "Get the full ESHRE guideline on PCOS"

**Response:** The server will retrieve:
- Full guideline title and publication date
- Complete text content from the guideline webpage
- Download links for:
  - Full guideline PDF
  - Patient version
  - Evidence tables
  - Supporting documents

## Data Source

All data is retrieved from the official ESHRE website:
https://www.eshre.eu/Guidelines-and-Legal

The guidelines are developed by ESHRE guideline development groups following rigorous methodology and represent best practice recommendations in reproductive medicine.

## Limitations

- The server retrieves content from public ESHRE web pages
- Some guidelines may require downloading PDFs for complete content
- The server provides summaries and links; full clinical use should reference the official PDF documents
- Internet connection required for all operations

## Troubleshooting

### Server Not Appearing in Claude

1. Check that the configuration file path is correct
2. Verify Python path is correct (`which python` or `which python3`)
3. Ensure all dependencies are installed
4. Restart Claude Desktop after configuration changes

### Connection Errors

1. Verify internet connection
2. Check if ESHRE website is accessible
3. Look for firewall or proxy issues

### Import Errors

Ensure all required packages are installed:
```bash
pip install mcp httpx beautifulsoup4 lxml
```

## Version History

- **0.1.0** (2025) - Initial release
  - List all ESHRE guidelines
  - Search guidelines by keyword
  - Retrieve full guideline content and download links

## Related Servers

This server is part of the Women's Health MCP collection:
- **asrm_server.py** - ASRM (American Society for Reproductive Medicine) guidelines
- **eshre_server.py** - ESHRE guidelines (this server)

## License

This MCP server is provided as-is for educational and clinical reference purposes. The ESHRE guidelines themselves are copyright ESHRE and subject to their terms of use.

## Support

For issues or questions about this MCP server, please refer to the MCP documentation or create an issue in the project repository.

## Acknowledgments

- ESHRE for developing and publishing comprehensive clinical guidelines
- The MCP protocol team at Anthropic
- BeautifulSoup and httpx library developers
