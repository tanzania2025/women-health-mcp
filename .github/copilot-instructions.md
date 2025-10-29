# Women's Health MCP - AI Agent Guidelines

## 🏗️ Architecture Overview

This project implements a Model Context Protocol (MCP) server ecosystem for women's health data integration, focusing on:

- Core MCP protocol implementation (`mcp_server/mcp_protocol.py`)
- Multiple specialized data servers for different sources
- AI-powered clinical decision support
- Privacy-first data handling

Key components:
```
/mcp_server/          # Core MCP implementation
/data/                # Data storage & schemas
/demo/                # Example MCP clients
[individual servers]  # Specialized data providers
```

## 🔄 Data Flow Architecture

1. Patient data enters through privacy layer
2. MCP protocol routes requests (`mcp_protocol.py`)
3. Specialized servers process domain data:
   - SWAN research database (`swan_data_integration.py`)
   - SART IVF statistics (`sart_ivf_server.py`)
   - ASRM guidelines (`asrm_server.py`)
   - NAMS protocols (`nams_server.py`)
   - PubMed literature (`pubmed_server.py`)
4. Clinical calculators apply validated algorithms
5. AI agents synthesize evidence-based recommendations

## 🚀 Development Workflow

1. Start the MCP server:
   ```bash
   python run_server.py  # WebSocket endpoint: ws://localhost:8000/mcp/ws
   ```

2. Test with demo client:
   ```bash
   python demo/mcp_client_demo.py [simple]  # Optional simple mode
   ```

3. Run Streamlit demo:
   ```bash
   streamlit run complete_hackathon_demo.py
   ```

## 💡 Project Conventions

1. All MCP servers follow JSON-RPC 2.0 spec
2. Server classes inherit from `MCPServer` base class
3. Tool methods use `@app.list_tools()` and `@app.call_tool()` decorators
4. Patient data requires HIPAA-compliant handling
5. Async/await pattern used throughout codebase

## 🔌 Integration Points

1. MCP Protocol
   - WebSocket/HTTP endpoints in `server.py`
   - JSON-RPC 2.0 message format
   - Tool registration pattern in `mcp_protocol.py`

2. External Systems
   - FHIR R4 for EHR integration
   - OAuth2 for NHS API authentication
   - RESTful APIs for research databases

3. Data Processing Pipeline
   - `Biomini` agent for standardization
   - `Netmind` router for query distribution
   - `Manus` multi-agent orchestration

## ⚠️ Critical Considerations

1. Privacy & Security
   - All patient data must be HIPAA compliant
   - Use audit logging for data access
   - Verify consent management

2. Data Validation
   - Clinical calculator inputs require validation
   - Research data requires age/demographic filtering
   - Statistics need proper population subsetting

3. Error Handling
   - Handle connection issues gracefully
   - Validate SWAN queries return results
   - Check age range handling in statistics

## 🧪 Testing Approach

1. Unit tests in `test_*.py` files
2. Integration tests in `test_complete_demo.py`
3. Use `runTests` for test execution
4. Verify MCP protocol compliance
5. Validate clinical calculator accuracy

## 📚 Key Files

- `SWAN_MCP_Flow_Diagram.md`: Complete system architecture
- `MCP_SERVER_GUIDE.md`: Server implementation details
- `clinical_calculators.py`: Validated medical algorithms
- `privacy_security.py`: HIPAA compliance layer