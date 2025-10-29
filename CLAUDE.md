# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a **Women's Health Model Context Protocol (MCP) server ecosystem** providing AI agents with standardized access to reproductive health data sources and clinical calculators. The project has been **fully refactored to use FastMCP** for simplified development.

### Core Components

- **`servers/`**: Individual FastMCP servers for different data sources (PubMed, ASRM, ESHRE, NAMS, ELSA, etc.)
- **`scripts/mcp_stdio_server.py`**: Main unified FastMCP server combining all tools
- **`core/`**: Clinical calculation engines and FHIR integration
- **`app.py`**: Main Streamlit frontend with sophisticated medical journal aesthetics
- **`tests/`**: Test suite for server functionality

### FastMCP Pattern

All servers use the modern FastMCP framework with:
```python
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("server-name")

@mcp.tool()
def tool_name(
    param: str = Field(description="Parameter description")
) -> str:
    return "result"

@mcp.resource("resource://uri", mime_type="application/json")
def resource_name() -> dict:
    return {"data": "value"}

if __name__ == "__main__":
    mcp.run()
```

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Running the Application
```bash
# Main DoctHER chat interface (recommended)
streamlit run app.py
# or 
python run_frontend.py

# CLI interface with multi-server architecture
python main.py

# Run unified MCP server directly
python scripts/mcp_stdio_server.py

# Run individual servers
python servers/pubmed_server.py
python servers/asrm_server.py
# etc.
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific server tests
python -m pytest tests/test_pubmed.py
python -m pytest tests/test_asrm.py

# Test individual components
python -m core.clinical_calculators
python -m servers.pubmed_server
```

## Key Architectural Patterns

### MCP Server Structure
Each server in `servers/` follows this pattern:
1. **Imports**: `fastmcp`, `pydantic`, `asyncio` for async operations
2. **Helper functions**: Async functions for data fetching/processing
3. **FastMCP tools**: `@mcp.tool()` decorated functions with Pydantic validation
4. **Resources**: `@mcp.resource()` for metadata endpoints
5. **Server execution**: `mcp.run()` at bottom

### Async Operations Integration
FastMCP servers wrap async operations with `asyncio.run()`:
```python
@mcp.tool()
def search_pubmed(query: str) -> str:
    # Call async helper function
    results = asyncio.run(fetch_pubmed_data(query))
    return format_results(results)
```

### Data Source Integration
- **PubMed**: NCBI E-utilities API for scientific literature
- **ASRM/ESHRE/NAMS**: Web scraping of medical guidelines with BeautifulSoup
- **ELSA**: UK Data Service integration for longitudinal aging study
- **SART**: IVF success calculator API integration
- **FHIR**: Healthcare interoperability standards

### Clinical Calculator Pattern
Core calculations in `core/clinical_calculators.py`:
- Uses real APIs (SART IVF calculator)
- Validates medical parameters (age ranges, hormone levels)
- Returns structured results with confidence intervals
- Handles both metric and imperial units

## Privacy and Security Considerations

- Patient data must be HIPAA compliant
- All external API calls include proper rate limiting
- Sensitive medical parameters validated before processing  
- Error handling returns empty results rather than fake data
- Audit logging enabled in production mode

## Development Workflow

1. **For new tools**: Add to appropriate server in `servers/` or main server in `scripts/`
2. **For new data sources**: Create new server file following FastMCP pattern
3. **For clinical calculations**: Extend `core/clinical_calculators.py`
4. **For testing**: Add tests to `tests/` directory

## File Relationships

- `scripts/mcp_stdio_server.py` imports and combines tools from individual servers
- `demos/doct_her_stdio.py` runs the main server as a subprocess
- `core/` modules provide shared functionality across servers
- Individual servers in `servers/` can run standalone or be imported

## External API Dependencies

- **NCBI E-utilities**: PubMed searches (optional API key for higher limits)
- **SART Calculator**: `https://w3.abdn.ac.uk/clsm/SARTIVF/tool/ivf1`
- **UK Data Service**: ELSA data access
- **Medical websites**: ASRM, ESHRE, NAMS for guideline scraping

## Common Debugging

- Import errors: Ensure all dependencies in `requirements.txt` are installed
- Server startup issues: Check `.env` file exists with required API keys
- Tool execution failures: Verify external APIs are accessible
- FastMCP migration: All servers converted from standard MCP to FastMCP pattern