# Complete Tool Inventory

## All Unique Tools (No Duplicates)

| Tool Name | Primary Location | Also Found In | Description | Target Server | Status |
|-----------|-----------------|---------------|-------------|---------------|--------|
| **SART IVF Tools** |
| calculate_ivf_success | servers/sart_ivf_server.py | - | SART IVF success rate calculation | Calculator | ✓ Available |
| predict_ivf_success | scripts/mcp_stdio_server.py | - | FastMCP wrapper for SART calculation | Calculator | ✓ Wrapper only |
| **PubMed Tools** |
| search_pubmed | servers/pubmed_server.py | scripts/mcp_stdio_server.py | Search PubMed articles | API | ⚠ Choose impl |
| get_article | servers/pubmed_server.py | scripts/mcp_stdio_server.py | Get single article details | API | ⚠ Choose impl |
| get_multiple_articles | servers/pubmed_server.py | scripts/mcp_stdio_server.py | Get multiple article details | API | ⚠ Choose impl |
| **ESHRE Tools** |
| list_eshre_guidelines | servers/eshre_server.py | scripts/mcp_stdio_server.py | List ESHRE guidelines | API | ⚠ Choose impl |
| search_eshre_guidelines | servers/eshre_server.py | scripts/mcp_stdio_server.py | Search ESHRE guidelines | API | ⚠ Choose impl |
| get_eshre_guideline | servers/eshre_server.py | scripts/mcp_stdio_server.py | Get ESHRE guideline content | API | ⚠ Choose impl |
| **ASRM Tools** |
| list_practice_documents | servers/asrm_server.py | scripts/mcp_stdio_server.py | List ASRM practice docs | API | ⚠ Choose impl |
| list_ethics_opinions | servers/asrm_server.py | scripts/mcp_stdio_server.py | List ASRM ethics opinions | API | ⚠ Choose impl |
| search_asrm_guidelines | servers/asrm_server.py | scripts/mcp_stdio_server.py | Search ASRM guidelines | API | ⚠ Choose impl |
| get_guideline_content | servers/asrm_server.py | - | Get ASRM guideline content | API | ✓ Server only |
| list_asrm_practice_documents | scripts/mcp_stdio_server.py | - | FastMCP wrapper for practice docs | API | ✓ Wrapper only |
| list_asrm_ethics_opinions | scripts/mcp_stdio_server.py | - | FastMCP wrapper for ethics opinions | API | ✓ Wrapper only |
| get_asrm_guideline | scripts/mcp_stdio_server.py | - | FastMCP wrapper for guideline content | API | ✓ Wrapper only |
| **NAMS Tools** |
| list_nams_position_statements | servers/nams_server.py | scripts/mcp_stdio_server.py | List NAMS position statements | API | ⚠ Choose impl |
| search_nams_protocols | servers/nams_server.py | scripts/mcp_stdio_server.py | Search NAMS protocols | API | ⚠ Choose impl |
| get_protocol_content | servers/nams_server.py | - | Get NAMS protocol content | API | ✓ Server only |
| list_nams_topics | servers/nams_server.py | - | List common NAMS topics | API | ✓ Server only |
| get_nams_protocol | scripts/mcp_stdio_server.py | - | FastMCP wrapper for protocol content | API | ✓ Wrapper only |
| **ELSA Tools** |
| list_elsa_waves | servers/elsa_server.py | scripts/mcp_stdio_server.py | List ELSA waves | Database | ⚠ Choose impl |
| get_wave_details | servers/elsa_server.py | - | Get ELSA wave details | Database | ✓ Server only |
| search_data_modules | servers/elsa_server.py | - | Search ELSA data modules | Database | ✓ Server only |
| get_data_module_info | servers/elsa_server.py | - | Get ELSA module info | Database | ✓ Server only |
| get_access_information | servers/elsa_server.py | - | Get ELSA data access info | Database | ✓ Server only |
| get_study_metadata | servers/elsa_server.py | - | Get ELSA study metadata | Database | ✓ Server only |
| get_documentation_links | servers/elsa_server.py | - | Get ELSA documentation links | Database | ✓ Server only |
| compare_waves | servers/elsa_server.py | - | Compare ELSA waves | Database | ✓ Server only |
| get_research_examples | servers/elsa_server.py | - | Get ELSA research examples | Database | ✓ Server only |
| search_data_modules | mcp_servers/database_server.py | - | Search ELSA data modules by topic or keyword | Database | ✓ Available |

## Tools by Target Server

### Database Server (ELSA)
**From servers/elsa_server.py:**
- list_elsa_waves
- get_wave_details 
- search_data_modules
- get_data_module_info
- get_access_information
- get_study_metadata
- get_documentation_links
- compare_waves
- get_research_examples

**From mcp_servers/database_server.py (FastMCP):**
- list_elsa_waves
- search_data_modules

### API Server (PubMed, ESHRE, ASRM, NAMS)

**PubMed (servers/pubmed_server.py):**
- search_pubmed
- get_article
- get_multiple_articles

**ESHRE (servers/eshre_server.py):**
- list_eshre_guidelines
- search_eshre_guidelines
- get_eshre_guideline

**ASRM (servers/asrm_server.py):**
- list_practice_documents
- list_ethics_opinions
- search_asrm_guidelines
- get_guideline_content

**NAMS (servers/nams_server.py):**
- list_nams_position_statements
- search_nams_protocols
- get_protocol_content
- list_nams_topics

**FastMCP Wrappers (scripts/mcp_stdio_server.py):**
- All of the above as FastMCP wrapper functions

### Calculator Server (SART IVF)
**From servers/sart_ivf_server.py:**
- calculate_ivf_success
- generate_recommendations (helper function)

**From scripts/mcp_stdio_server.py:**
- predict_ivf_success (wrapper)

## Duplicate Resolution

| Tool Name | Implementation 1 | Implementation 2 | Chosen | Reason |
|-----------|-----------------|------------------|--------|------------|
| search_pubmed | servers/pubmed_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| get_article | servers/pubmed_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| get_multiple_articles | servers/pubmed_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| list_eshre_guidelines | servers/eshre_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| search_eshre_guidelines | servers/eshre_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| get_eshre_guideline | servers/eshre_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, direct API access |
| list_elsa_waves | servers/elsa_server.py (traditional MCP) | scripts/mcp_stdio_server.py (FastMCP wrapper) | servers/ version | More complete, richer data structure |

## Architecture Summary

### Current State:
- **Traditional MCP Servers**: All servers/ files use traditional MCP protocol
- **FastMCP Router**: scripts/mcp_stdio_server.py acts as FastMCP wrapper/aggregator
- **Duplicated Tools**: Most tools exist in both locations (server implementation + FastMCP wrapper)

### Total Tool Count:
- **Unique functionality**: ~25 distinct medical tools
- **Total implementations**: ~40+ (counting duplicates)
- **FastMCP wrappers**: ~15 wrapper functions in scripts/mcp_stdio_server.py

### External Dependencies:
- **PubMed**: NCBI E-utilities API (optional API key: NCBI_API_KEY)
- **ESHRE**: Web scraping eshre.eu
- **ASRM**: Web scraping asrm.org  
- **NAMS**: Web scraping menopause.org
- **SART**: Aberdeen University calculator API
- **ELSA**: Static data (no external API)