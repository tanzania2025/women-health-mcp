# Women's Health MCP Server Guide

## 🎯 Overview

The Women's Health MCP Server provides a **production-ready Model Context Protocol (MCP) implementation** using stdio (Standard Input/Output) that enables AI agents to access standardized reproductive health data, clinical calculators, and evidence-based recommendations.

## 🏗️ Architecture

```
/women-health-mcp/
├── scripts/
│   └── mcp_stdio_server.py   # FastMCP stdio server implementation
├── app/
│   └── doct_her_stdio.py     # DoctHER chat interface (uses MCP server)
├── servers/                   # Individual MCP tool servers
│   ├── pubmed_server.py       # PubMed research integration
│   ├── eshre_server.py        # ESHRE guidelines
│   ├── nams_server.py         # NAMS protocols
│   └── elsa_server.py         # ELSA data integration
└── core/                      # Core components
    ├── clinical_calculators.py
    ├── research_database_integration.py
    └── fhir_integration.py
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### 2. Start DoctHER
```bash
streamlit run app/doct_her_stdio.py
```

The MCP server (`scripts/mcp_stdio_server.py`) runs automatically as a subprocess when DoctHER starts.

### 3. Example Usage

Ask DoctHER questions and it will automatically use the appropriate MCP tools:
- "I'm 38 with AMH 0.8, what are my IVF chances?"
- "Find recent PubMed articles about fertility after 35"
- "What are the ESHRE guidelines for IVF?"

## 📡 MCP Protocol Endpoints

### Standard MCP Methods
- **`initialize`** - Establish connection and capabilities
- **`resources/list`** - List available data resources
- **`resources/read`** - Read specific resource data
- **`tools/list`** - List available clinical tools
- **`tools/call`** - Execute clinical calculations
- **`prompts/list`** - List AI prompt templates
- **`prompts/get`** - Get formatted prompts

### Communication Protocol
The MCP server uses **stdio** (Standard Input/Output) for communication:
- Runs as a subprocess of the DoctHER application
- Communicates via stdin/stdout using JSON-RPC messages
- Automatically managed by the MCP client library

## 🔧 Available Tools

### Clinical Calculators
1. **`assess-ovarian-reserve`**
   - Input: age, amh, fsh (optional), afc (optional)
   - Output: ASRM category, percentile, recommendations

2. **`predict-ivf-success`**  
   - Input: age, amh, cycle_type, prior_pregnancies
   - Output: Live birth rate, confidence intervals

3. **`predict-menopause`**
   - Input: age, amh, lifestyle factors
   - Output: Predicted timing, current stage

4. **`query-research-database`**
   - Input: database (swan/sart/pubmed), query_type, condition
   - Output: Population statistics, research data

5. **`create-fhir-resource`**
   - Input: resource_type, patient_id, data
   - Output: FHIR R4 compliant resource

## 📊 Available Resources

### Data Sources
- **`patient-data`** - Standardized patient profiles
- **`clinical-calculators`** - Calculator metadata
- **`research-data`** - SWAN, SART database info
- **`fhir-resources`** - FHIR resource templates

## 🤖 AI Integration Examples

### Using with Anthropic Claude
```python
import httpx

async def claude_with_mcp(question):
    # Get MCP context
    async with httpx.AsyncClient() as client:
        tools_response = await client.get(
            "http://localhost:8000/mcp/tools",
            headers={"Authorization": "Bearer your-api-key"}
        )
        
        # Call clinical tool
        assessment = await client.post(
            "http://localhost:8000/mcp/tools/assess-ovarian-reserve",
            json={"age": 38, "amh": 0.8},
            headers={"Authorization": "Bearer your-api-key"}
        )
        
        # Get formatted prompt
        prompt_response = await client.post(
            "http://localhost:8000/mcp/prompts/fertility-consultation",
            json={
                "patient_age": 38,
                "amh_level": 0.8,
                "clinical_question": question
            },
            headers={"Authorization": "Bearer your-api-key"}
        )
    
    # Send to Claude with context
    # claude_response = anthropic.messages.create(...)
```

### Direct MCP Protocol Usage
```python
import json

mcp_request = {
    "jsonrpc": "2.0",
    "id": "request_1",
    "method": "tools/call",
    "params": {
        "name": "assess-ovarian-reserve",
        "arguments": {
            "age": 38,
            "amh": 0.8
        }
    }
}

# Send to http://localhost:8000/mcp
```

## 🔒 Security Configuration

### API Authentication
```bash
# Set in .env file
API_KEY=your-secure-api-key-here

# Use in requests
Authorization: Bearer your-secure-api-key-here
```

### HIPAA Compliance Mode
```bash
# Enable in .env
HIPAA_COMPLIANCE_MODE=true
ENABLE_AUDIT_LOGGING=true
```

## 📈 Production Deployment

### Environment Variables
```bash
# Production settings
DEBUG=false
ENABLE_REAL_APIS=true
DATABASE_URL=postgresql://user:pass@host:5432/db

# External APIs
SWAN_API_KEY=your-swan-key
SART_API_KEY=your-sart-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run_server.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: womens-health-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: womens-health-mcp
  template:
    spec:
      containers:
      - name: mcp-server
        image: womens-health-mcp:latest
        ports:
        - containerPort: 8000
```

## 🔍 Monitoring & Logging

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
- Server logs: Console output
- Audit logs: Enabled with `ENABLE_AUDIT_LOGGING=true`
- Performance metrics: Available at `/metrics` (if enabled)

## 🧪 Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
python demo/mcp_client_demo.py
```

### Load Testing
```bash
# Install wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## 📞 Support

### Troubleshooting
1. **Import errors**: Run `python setup_mcp.py`
2. **Server won't start**: Check `.env` file exists
3. **Tool calls fail**: Verify API key in headers
4. **WebSocket issues**: Check firewall settings

### Development
- MCP Protocol Spec: https://modelcontextprotocol.io/
- FastAPI Docs: http://localhost:8000/docs (when server running)
- OpenAPI Schema: http://localhost:8000/openapi.json

This MCP server provides the **infrastructure foundation** for the $50B women's health AI market, enabling standardized, secure, and evidence-based AI agents for reproductive health.