# Refactor Women's Health MCP: Single Router → Multi-Server FastMCP Architecture

## Current Architecture (Actual State)

Based on @query_flow_ascii.txt and existing codebase:

**Current Structure:**
```
Frontend (Streamlit)
    ↓
MCP Client (single connection)
    ↓
scripts/mcp_stdio_server.py (FastMCP Router)
    ↓
├── servers/sart_ivf_server.py      (calculate_ivf_success, generate_recommendations)
├── servers/pubmed_server.py        (search_pubmed, get_article, fetch_abstract)
├── servers/eshre_server.py         (get_eshre_guideline, search_guidelines)
├── servers/asrm_server.py          (search_asrm_guidelines, list_practice_documents)
├── servers/nams_server.py          (search_nams_protocols, list_position_statements)
└── servers/elsa_server.py          (search_elsa_data, list_waves)
    ↓
External APIs (SART, NCBI, ESHRE, ASRM, NAMS, ELSA)
```

**Current behavior:**
- Single FastMCP server at `scripts/mcp_stdio_server.py` acts as a wrapper/router
- Modular server architecture already exists in `servers/` directory (6 separate modules)
- Each server module has tools for specific medical domains
- Client connects to one entry point, which dispatches to appropriate server module

## Critical Requirement: Tool Preservation

⚠️ **IMPORTANT: Preserve ALL tools from BOTH locations:**

1. **Tools in individual server files** (`servers/*.py`):
   - `servers/sart_ivf_server.py` → All IVF calculation tools
   - `servers/pubmed_server.py` → All PubMed search tools
   - `servers/eshre_server.py` → All ESHRE guideline tools
   - `servers/asrm_server.py` → All ASRM guideline tools
   - `servers/nams_server.py` → All NAMS protocol tools
   - `servers/elsa_server.py` → All ELSA dataset tools

2. **Tools in the router** (`scripts/mcp_stdio_server.py`):
   - May contain additional tools not in individual servers
   - May contain wrapper tools or aggregate functions
   - May contain utility tools

**Task: Create comprehensive tool inventory**
- [ ] List ALL tools from each `servers/*.py` file
- [ ] List ALL tools from `scripts/mcp_stdio_server.py`
- [ ] Identify duplicates (same tool in multiple places)
- [ ] Identify unique tools (only in one location)
- [ ] Flag any tools that need to be migrated/preserved

**Tool Inventory Template:**
```markdown
| Tool Name | Location(s) | Description | Target Server |
|-----------|------------|-------------|---------------|
| calculate_ivf_success | servers/sart_ivf_server.py | IVF success calc | Calculator |
| search_pubmed | servers/pubmed_server.py, scripts/mcp_stdio_server.py | PubMed search | API |
| custom_tool_xyz | scripts/mcp_stdio_server.py ONLY | Custom utility | ??? |
```

**No duplicates in final architecture:**
- Each tool should appear in exactly ONE of the 3 new FastMCP servers
- If a tool exists in multiple places, choose the most complete implementation
- Document any discrepancies between implementations

## Desired Architecture

Transform to **three FastMCP servers** grouping existing 6 modules by domain:
```
Frontend (Streamlit)
    ↓
Multi-Server MCP Client
    ├────────────────┬────────────────┬────────────────┐
    ↓                ↓                ↓                ↓
DATABASE         API              CALCULATOR       [Router?]
SERVER           SERVER           SERVER

servers/elsa_    servers/pubmed_  servers/sart_    scripts/
server.py        server.py        ivf_server.py    mcp_stdio_
(FastMCP)        servers/eshre_   (FastMCP)        server.py
                 server.py                         [evaluate]
                 servers/asrm_
                 server.py
                 servers/nams_
                 server.py
                 (FastMCP)
```

**New grouping strategy:**

**Database Server** (1 module):
- `servers/elsa_server.py` → Convert to FastMCP
- Tools: search_elsa_data, list_waves, [+ any others found]
- Domain: Local longitudinal aging datasets

**API Server** (4 modules combined):
- `servers/pubmed_server.py` → Convert to FastMCP
- `servers/eshre_server.py` → Convert to FastMCP
- `servers/asrm_server.py` → Convert to FastMCP
- `servers/nams_server.py` → Convert to FastMCP
- Tools:
  - PubMed: search_pubmed, get_article, fetch_abstract
  - ESHRE: get_eshre_guideline, search_guidelines
  - ASRM: search_asrm_guidelines, list_practice_documents
  - NAMS: search_nams_protocols, list_position_statements
  - [+ any others found in servers/ or scripts/]
- Domain: External medical APIs and clinical guidelines

**Calculator Server** (1 module):
- `servers/sart_ivf_server.py` → Convert to FastMCP
- Tools: calculate_ivf_success, generate_recommendations, [+ any others found]
- Domain: Clinical calculations and predictions

## Refactoring Tasks

### Task 1: Comprehensive Tool Audit & Inventory

**Step 1: Analyze ALL server modules in `servers/` directory**

For each file:
- [ ] `servers/sart_ivf_server.py`
- [ ] `servers/pubmed_server.py`
- [ ] `servers/eshre_server.py`
- [ ] `servers/asrm_server.py`
- [ ] `servers/nams_server.py`
- [ ] `servers/elsa_server.py`

Document for each:
```markdown
### servers/[name]_server.py

**Tools found:**
1. tool_name_1(param1, param2) → description
2. tool_name_2(param1) → description
...

**Current implementation:**
- [ ] Traditional MCP
- [ ] FastMCP
- [ ] Plain Python functions

**External dependencies:**
- API: [name, credentials needed]
- Libraries: [list]

**Shared utilities:**
- [list any helper functions used]
```

**Step 2: Analyze router in `scripts/mcp_stdio_server.py`**

Document:
```markdown
### scripts/mcp_stdio_server.py

**Tools registered (all tools available to Claude):**
1. tool_name → routes to servers/X.py
2. tool_name → defined locally in router
...

**Routing logic:**
- How does it import server modules?
- How does it register tools?
- Any custom tools defined here only?

**Initialization:**
- Connection management
- Shared resources
- Environment variables
```

**Step 3: Create consolidated tool inventory**

Create `TOOL_INVENTORY.md`:
```markdown
# Complete Tool Inventory

## All Unique Tools (No Duplicates)

| Tool Name | Primary Location | Also Found In | Description | Target Server | Status |
|-----------|-----------------|---------------|-------------|---------------|--------|
| calculate_ivf_success | servers/sart_ivf_server.py | - | SART IVF calculator | Calculator | ✓ Migrate |
| search_pubmed | servers/pubmed_server.py | scripts/mcp_stdio_server.py | PubMed search | API | ⚠ Choose impl |
| ... | ... | ... | ... | ... | ... |

## Tools by Target Server

### Database Server (ELSA)
- search_elsa_data
- list_waves
- [any others]

### API Server (PubMed, ESHRE, ASRM, NAMS)
**PubMed:**
- search_pubmed
- get_article
- fetch_abstract
- [any others]

**ESHRE:**
- get_eshre_guideline
- search_guidelines
- [any others]

**ASRM:**
- search_asrm_guidelines
- list_practice_documents
- [any others]

**NAMS:**
- search_nams_protocols
- list_position_statements
- [any others]

### Calculator Server (SART IVF)
- calculate_ivf_success
- generate_recommendations
- [any others]

### Orphaned Tools (Not clearly belonging to above categories)
- tool_xyz → [decide where it goes]

## Duplicate Resolution

| Tool Name | Implementation 1 | Implementation 2 | Chosen | Reason |
|-----------|-----------------|------------------|--------|---------|
| example_tool | servers/X.py (v1) | scripts/mcp_stdio_server.py (v2) | servers/X.py | More complete |
```

**Deliverable:** Complete `TOOL_INVENTORY.md` before proceeding to Task 2

### Task 2: Group Modules into Three FastMCP Servers

**Important: Use the tool inventory from Task 1 as the source of truth**

**Option A: Consolidate into single files**
```
mcp_servers/
├── database_server.py      # All ELSA tools from inventory
├── api_server.py           # All PubMed/ESHRE/ASRM/NAMS tools from inventory
└── calculator_server.py    # All SART IVF tools from inventory
```

**Option B: Keep modules, create FastMCP wrappers**
```
servers/                    # Keep existing modules (convert to FastMCP)
├── elsa_server.py         # Convert to FastMCP standalone
├── pubmed_server.py       # Convert to FastMCP standalone
├── eshre_server.py        # Convert to FastMCP standalone
├── asrm_server.py         # Convert to FastMCP standalone
├── nams_server.py         # Convert to FastMCP standalone
└── sart_ivf_server.py     # Convert to FastMCP standalone

mcp_servers/               # New FastMCP aggregators
├── database_server.py     # FastMCP server that imports elsa_server tools
├── api_server.py          # FastMCP server that imports pubmed/eshre/asrm/nams tools
└── calculator_server.py   # FastMCP server that imports sart_ivf tools
```

**Decide which option based on:**
- Code reusability (are server modules used elsewhere?)
- Testing complexity (easier to test individual modules?)
- Deployment flexibility (need to deploy servers separately?)
- Tool count (consolidation makes sense if <5 tools per domain)

### Task 3: Convert to FastMCP Implementation

For each existing server module, convert to FastMCP pattern:

**Before (Traditional MCP or plain Python):**
```python
# servers/pubmed_server.py (current - analyze actual implementation)
def search_pubmed(query: str, max_results: int = 10):
    # Implementation
    pass

def get_article(pmid: str):
    # Implementation
    pass
```

**After (FastMCP):**
```python
# servers/pubmed_server.py (new)
from fastmcp import FastMCP
from typing import Optional

mcp = FastMCP("women-health-pubmed")

@mcp.tool()
async def search_pubmed(
    query: str,
    max_results: int = 10,
    publication_year: Optional[str] = None
) -> dict:
    """
    Search PubMed for peer-reviewed medical literature using NCBI E-utilities API.

    Searches 35M+ biomedical articles. Useful for finding evidence-based research
    on fertility, women's health, and clinical guidelines.

    Args:
        query: Medical search terms (e.g., "PCOS treatment protocols")
        max_results: Number of articles to return (1-100, default 10)
        publication_year: Filter by year (e.g., "2024" or "2020:2024")

    Returns:
        Dict containing PubMed articles with titles, abstracts, DOIs, authors
    """
    # Implementation with proper async/await
    pass

@mcp.tool()
async def get_article(pmid: str) -> dict:
    """
    Retrieve full PubMed article details by PMID.

    Args:
        pmid: PubMed ID (e.g., "12345678")

    Returns:
        Dict with full article metadata, abstract, authors, citations
    """
    pass

@mcp.lifespan
async def lifespan():
    """Initialize NCBI API client"""
    api_client = await init_ncbi_client()
    yield {"ncbi_client": api_client}
    await api_client.close()
```

**Requirements for each converted tool:**
- Medical-grade descriptions (explain clinical use case)
- Type hints for all parameters
- Proper async/await (if making I/O calls)
- Error handling with medical context
- Input validation
- HIPAA-aware logging (no sensitive data)
- **ALL tools from inventory must be included**

### Task 4: Create Three Aggregated FastMCP Servers

**Database Server** (`mcp_servers/database_server.py`):
```python
from fastmcp import FastMCP
from servers.elsa_server import search_elsa_data, list_waves  # + any others from inventory

mcp = FastMCP("women-health-database")

# Register ALL ELSA tools from inventory
@mcp.tool()
async def search_elsa_data(*args, **kwargs):
    """
    Search ELSA (English Longitudinal Study of Ageing) datasets.

    Provides access to longitudinal data on aging, health, and socioeconomic
    factors in the UK population aged 50+. Useful for research on women's
    health in aging populations.
    """
    return await search_elsa_data(*args, **kwargs)

@mcp.tool()
async def list_waves(*args, **kwargs):
    """List available ELSA data collection waves (Wave 1-9, 2002-present)"""
    return await list_waves(*args, **kwargs)

# + Add any other ELSA tools found in inventory

# Add lifespan management if needed
```

**API Server** (`mcp_servers/api_server.py`):
```python
from fastmcp import FastMCP
from servers.pubmed_server import search_pubmed, get_article, fetch_abstract  # + others
from servers.eshre_server import get_eshre_guideline, search_guidelines  # + others
from servers.asrm_server import search_asrm_guidelines, list_practice_documents  # + others
from servers.nams_server import search_nams_protocols, list_position_statements  # + others

mcp = FastMCP("women-health-api")

# Register ALL PubMed tools from inventory
@mcp.tool()
async def search_pubmed(*args, **kwargs):
    """
    Search PubMed for peer-reviewed medical literature (35M+ articles).

    Uses NCBI E-utilities API to search biomedical literature. Essential for
    evidence-based clinical decision support and research validation.
    """
    return await search_pubmed(*args, **kwargs)

@mcp.tool()
async def get_article(*args, **kwargs):
    """Retrieve full PubMed article details by PMID"""
    return await get_article(*args, **kwargs)

@mcp.tool()
async def fetch_abstract(*args, **kwargs):
    """Fetch article abstract from PubMed"""
    return await fetch_abstract(*args, **kwargs)

# Register ALL ESHRE tools from inventory
@mcp.tool()
async def get_eshre_guideline(*args, **kwargs):
    """
    Retrieve European Society of Human Reproduction and Embryology (ESHRE) guidelines.

    Access evidence-based fertility treatment guidelines used across Europe.
    """
    return await get_eshre_guideline(*args, **kwargs)

@mcp.tool()
async def search_guidelines(*args, **kwargs):
    """Search ESHRE clinical practice guidelines"""
    return await search_guidelines(*args, **kwargs)

# Register ALL ASRM tools from inventory
@mcp.tool()
async def search_asrm_guidelines(*args, **kwargs):
    """
    Search American Society for Reproductive Medicine (ASRM) guidelines.

    Access US-based reproductive medicine practice guidelines and committee opinions.
    """
    return await search_asrm_guidelines(*args, **kwargs)

@mcp.tool()
async def list_practice_documents(*args, **kwargs):
    """List ASRM practice committee documents"""
    return await list_practice_documents(*args, **kwargs)

# Register ALL NAMS tools from inventory
@mcp.tool()
async def search_nams_protocols(*args, **kwargs):
    """
    Search North American Menopause Society (NAMS) clinical protocols.

    Access menopause management guidelines and hormone therapy recommendations.
    """
    return await search_nams_protocols(*args, **kwargs)

@mcp.tool()
async def list_position_statements(*args, **kwargs):
    """List NAMS position statements on menopause management"""
    return await list_position_statements(*args, **kwargs)

# + Add ANY other API tools found in inventory (from servers/ OR scripts/)

# Add combined lifespan management for all API connections
@mcp.lifespan
async def lifespan():
    """Initialize all external API clients"""
    pubmed_client = await init_pubmed_client()
    # ... other API clients
    yield {
        "pubmed": pubmed_client,
        # ... other clients
    }
    await pubmed_client.close()
    # ... close other clients
```

**Calculator Server** (`mcp_servers/calculator_server.py`):
```python
from fastmcp import FastMCP
from servers.sart_ivf_server import calculate_ivf_success, generate_recommendations  # + others

mcp = FastMCP("women-health-calculator")

# Register ALL SART IVF tools from inventory
@mcp.tool()
async def calculate_ivf_success(*args, **kwargs):
    """
    Calculate IVF success rates using SART (Society for Assisted Reproductive Technology) data.

    Predicts live birth probability based on patient demographics, medical history,
    and treatment parameters. Uses validated SART prediction model from Aberdeen University.
    """
    return await calculate_ivf_success(*args, **kwargs)

@mcp.tool()
async def generate_recommendations(*args, **kwargs):
    """
    Generate personalized IVF treatment recommendations based on success predictions.

    Provides clinical guidance on treatment optimization, timing, and alternatives.
    """
    return await generate_recommendations(*args, **kwargs)

# + Add ANY other calculator tools found in inventory
```

**Critical: No tools should be missing from the final servers!**

### Task 5: Update MCP Client in Streamlit App

**Current client code in `demos/doct_her_stdio.py`:**
- Single connection to `scripts/mcp_stdio_server.py`
- Single `session.list_tools()` call
- Simple tool routing

**New multi-server client:**
```python
# demos/doct_her_stdio.py (refactored section)

import asyncio
from mcp import ClientSession, StdioServerParameters
from typing import Dict, Any
import os

class MultiServerMCPClient:
    """Connect to multiple domain-specific MCP servers"""

    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.tool_registry: Dict[str, str] = {}

    async def connect_all_servers(self):
        """Connect to database, API, and calculator servers"""

        # Database Server
        db_session = ClientSession(
            StdioServerParameters(
                command="python",
                args=["-m", "fastmcp", "run", "mcp_servers/database_server.py"]
            )
        )
        await db_session.__aenter__()
        self.sessions["database"] = db_session

        # API Server
        api_session = ClientSession(
            StdioServerParameters(
                command="python",
                args=["-m", "fastmcp", "run", "mcp_servers/api_server.py"],
                env={
                    "PUBMED_API_KEY": os.getenv("NCBI_API_KEY"),
                    "ESHRE_CREDENTIALS": os.getenv("ESHRE_AUTH"),
                    "ASRM_TOKEN": os.getenv("ASRM_API_TOKEN"),
                    "NAMS_TOKEN": os.getenv("NAMS_API_TOKEN"),
                }
            )
        )
        await api_session.__aenter__()
        self.sessions["api"] = api_session

        # Calculator Server
        calc_session = ClientSession(
            StdioServerParameters(
                command="python",
                args=["-m", "fastmcp", "run", "mcp_servers/calculator_server.py"]
            )
        )
        await calc_session.__aenter__()
        self.sessions["calculator"] = calc_session

        # Build tool registry
        await self._discover_tools()

    async def _discover_tools(self):
        """Build registry of which tool belongs to which server"""
        total_tools = 0
        for server_name, session in self.sessions.items():
            tools = await session.list_tools()
            server_tool_count = len(tools.tools)
            total_tools += server_tool_count

            for tool in tools.tools:
                self.tool_registry[tool.name] = server_name
                st.sidebar.write(f"✓ {tool.name} → {server_name}")

            st.sidebar.info(f"{server_name}: {server_tool_count} tools")

        st.sidebar.success(f"Total: {total_tools} tools discovered")

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Route tool call to appropriate server"""
        server_name = self.tool_registry.get(tool_name)
        if not server_name:
            raise ValueError(f"Unknown tool: {tool_name}")

        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def get_all_tools_for_claude(self):
        """Aggregate tools from all servers for Claude API"""
        all_tools = []
        for session in self.sessions.values():
            tools = await session.list_tools()
            all_tools.extend(tools.tools)
        return all_tools

# Usage in Streamlit app
client = MultiServerMCPClient()
await client.connect_all_servers()

# In Claude API call
tools_for_claude = await client.get_all_tools_for_claude()
response = anthropic.messages.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": query}],
    tools=tools_for_claude,
    max_tokens=4096
)
```

**Preserve:**
- Agentic loop (15 iterations)
- Progressive UI feedback
- Tool chain display
- Error handling

### Task 6: Evaluate `scripts/mcp_stdio_server.py`

**Current role:** FastMCP wrapper/router that dispatches to `servers/` modules

**Decision Options:**

**Option A: Remove Entirely** ⭐ **Recommended**
- Pros: Cleaner architecture, direct connections, no intermediary, no confusion
- Cons: Breaking change, need to update all deployment configs
- When: If router only wraps existing server modules with no unique tools

**Option B: Keep as Backward Compatibility Layer**
- Pros: Existing integrations still work, gradual migration
- Cons: Maintains technical debt, confusing to have two paths
- When: If external systems depend on current endpoint

**Option C: Migrate Unique Tools**
- Pros: Preserves any custom tools defined only in router
- Cons: Need to categorize orphaned tools into appropriate servers
- When: If `scripts/mcp_stdio_server.py` has tools not in `servers/`

**Decision Criteria:**
```markdown
Check scripts/mcp_stdio_server.py:

1. Does it contain unique tools not in servers/?
   - YES → Option C (migrate those tools first)
   - NO → Proceed to #2

2. Do external systems connect directly to it?
   - YES → Option B (keep for compatibility, deprecated)
   - NO → Option A (remove entirely)
```

**Recommendation Process:**
- [ ] Analyze `scripts/mcp_stdio_server.py` for unique tools
- [ ] Document any tools that need migration
- [ ] Choose option based on criteria above
- [ ] Create migration plan

### Task 7: Configuration & Deployment

**Create `config/mcp_servers.json`:**
```json
{
  "mcpServers": {
    "women-health-database": {
      "command": "python",
      "args": ["-m", "fastmcp", "run", "mcp_servers/database_server.py"],
      "description": "ELSA longitudinal aging datasets"
    },
    "women-health-api": {
      "command": "python",
      "args": ["-m", "fastmcp", "run", "mcp_servers/api_server.py"],
      "env": {
        "PUBMED_API_KEY": "${NCBI_API_KEY}",
        "ESHRE_CREDENTIALS": "${ESHRE_AUTH}",
        "ASRM_TOKEN": "${ASRM_API_TOKEN}",
        "NAMS_TOKEN": "${NAMS_API_TOKEN}"
      },
      "description": "PubMed, ESHRE, ASRM, NAMS external medical APIs"
    },
    "women-health-calculator": {
      "command": "python",
      "args": ["-m", "fastmcp", "run", "mcp_servers/calculator_server.py"],
      "description": "SART IVF success predictions and clinical calculators"
    }
  }
}
```

**Update `requirements.txt`:**
```txt
fastmcp>=0.1.0
mcp>=0.9.0
anthropic>=0.40.0
streamlit>=1.28.0
# ... existing dependencies
```

**Streamlit Cloud Consideration:**
⚠️ **Critical:** Streamlit Cloud cannot run multiple MCP servers as separate processes.

**Deployment Options:**
1. **Local Development:** Multi-server works perfectly
2. **Streamlit Cloud:** Need to deploy MCP servers remotely (Railway, Fly.io, Render)
3. **Hybrid:** Streamlit UI on Cloud, MCP servers on separate infrastructure

### Task 8: Testing Strategy

**Test each server independently:**
```python
# tests/test_api_server.py
import pytest
from fastmcp.testing import MCPTestClient
from mcp_servers.api_server import mcp

@pytest.fixture
async def api_client():
    async with MCPTestClient(mcp) as client:
        yield client

async def test_pubmed_search(api_client):
    """Verify PubMed search returns medical literature"""
    result = await api_client.call_tool(
        "search_pubmed",
        {"query": "PCOS treatment", "max_results": 5}
    )
    assert result.isError == False
    data = json.loads(result.content[0].text)
    assert "articles" in data
    assert len(data["articles"]) <= 5
    # Verify structure
    assert "title" in data["articles"][0]
    assert "pmid" in data["articles"][0]

async def test_all_tools_present(api_client):
    """Verify ALL tools from inventory are registered"""
    tools = await api_client.list_tools()
    tool_names = [t.name for t in tools.tools]

    # Check all expected tools are present (from inventory)
    expected_tools = [
        "search_pubmed", "get_article", "fetch_abstract",  # PubMed
        "get_eshre_guideline", "search_guidelines",  # ESHRE
        "search_asrm_guidelines", "list_practice_documents",  # ASRM
        "search_nams_protocols", "list_position_statements",  # NAMS
        # + any others from inventory
    ]

    for tool in expected_tools:
        assert tool in tool_names, f"Tool {tool} missing from API server"
```

**Test multi-server client:**
```python
# tests/test_multi_server_client.py
async def test_client_connects_to_all_servers():
    """Verify client discovers tools from all 3 servers"""
    client = MultiServerMCPClient()
    await client.connect_all_servers()

    # Should have tools from all servers
    assert "search_pubmed" in client.tool_registry  # API server
    assert "calculate_ivf_success" in client.tool_registry  # Calculator
    assert "search_elsa_data" in client.tool_registry  # Database

    # Verify routing
    assert client.tool_registry["search_pubmed"] == "api"
    assert client.tool_registry["calculate_ivf_success"] == "calculator"

async def test_tool_count_matches_inventory():
    """Verify total tool count matches inventory"""
    client = MultiServerMCPClient()
    await client.connect_all_servers()

    # Should match total from TOOL_INVENTORY.md
    total_tools = len(client.tool_registry)
    expected_total = 15  # Update based on actual inventory

    assert total_tools == expected_total, \
        f"Expected {expected_total} tools, found {total_tools}"
```

### Task 9: Documentation Updates

**Update README.md:**
```markdown
# Women's Health MCP Architecture

## Multi-Server Architecture
```
Streamlit Frontend
    ↓
Multi-Server MCP Client
    ├──→ Database Server (ELSA data)
    ├──→ API Server (PubMed, ESHRE, ASRM, NAMS)
    └──→ Calculator Server (IVF predictions)
