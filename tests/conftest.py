"""
Pytest fixtures for MCP testing suite
"""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def event_loop():
    """Create an event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_medical_queries():
    """Sample medical queries for testing."""
    return [
        "Calculate IVF success rates for a 32-year-old patient",
        "Search PubMed for endometriosis treatments",
        "Find ESHRE guidelines for PCOS management",
        "Get NAMS recommendations for hormone therapy",
        "Search ELSA data for cardiovascular outcomes"
    ]

@pytest.fixture
def mock_pubmed_response():
    """Mock PubMed API response."""
    return {
        "pmids": ["12345", "67890"],
        "count": 2,
        "articles": [
            {
                "pmid": "12345",
                "title": "Endometriosis Treatment Options",
                "authors": ["Smith J", "Johnson A"],
                "journal": "Fertility and Sterility",
                "pubdate": "2024",
                "abstract": "This study examines endometriosis treatment options...",
                "doi": "10.1016/j.fertnstert.2024.001"
            }
        ]
    }

@pytest.fixture
def mock_ivf_calculation_response():
    """Mock SART IVF calculation response."""
    return {
        "age": 32,
        "height_cm": 165,
        "weight_kg": 65,
        "success_rate_1_cycle": 45.2,
        "success_rate_2_cycles": 62.8,
        "success_rate_3_cycles": 74.1,
        "amh_value": 2.5,
        "recommendations": [
            "Consider preconception counseling",
            "Optimize lifestyle factors before treatment"
        ]
    }

@pytest.fixture
def mock_elsa_data_response():
    """Mock ELSA dataset response."""
    return {
        "waves": ["Wave 1", "Wave 2", "Wave 3"],
        "data_modules": ["Demographics", "Health", "Lifestyle"],
        "sample_size": 12000,
        "years": "1998-2023"
    }

@pytest.fixture
async def mock_mcp_session():
    """Mock MCP session for testing."""
    session = AsyncMock()
    session.initialize = AsyncMock()
    session.list_tools = AsyncMock()
    session.call_tool = AsyncMock()
    return session

@pytest.fixture
def tool_inventory():
    """Load expected tools from TOOL_INVENTORY.md."""
    try:
        inventory_path = Path(__file__).parent.parent / "TOOL_INVENTORY.md"
        with open(inventory_path, 'r') as f:
            content = f.read()
        # Parse the inventory to extract tool names
        # This is a simplified parser - could be enhanced
        tools = []
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('- `') and '`' in line[3:]:
                tool_name = line.strip()[3:].split('`')[0]
                tools.append(tool_name)
        return tools
    except FileNotFoundError:
        # Return expected tools if inventory file not found
        return [
            "list_elsa_waves", "get_wave_details", "search_data_modules",
            "search_pubmed", "get_article", "get_multiple_articles",
            "list_eshre_guidelines", "search_eshre_guidelines",
            "calculate_ivf_success", "predict_ivf_success"
        ]

@pytest.fixture
def server_paths():
    """MCP server paths for testing."""
    base_path = Path(__file__).parent.parent
    return {
        "database": str(base_path / "mcp_servers" / "database_server.py"),
        "api": str(base_path / "mcp_servers" / "api_server.py"),
        "calculator": str(base_path / "mcp_servers" / "calculator_server.py")
    }