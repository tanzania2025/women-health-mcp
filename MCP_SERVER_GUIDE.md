# Women's Health MCP Server Guide

## 🎯 Overview

The Women's Health MCP Server provides a **production-ready Model Context Protocol (MCP) implementation** that enables AI agents to access standardized reproductive health data, clinical calculators, and evidence-based recommendations.

## 🏗️ Architecture

```
/women-health-mcp/
├── mcp_server/           # Core MCP server implementation
│   ├── mcp_protocol.py   # MCP spec compliance layer
│   ├── server.py         # FastAPI web server  
│   └── config.py         # Configuration management
├── demo/                 # Client demonstrations
│   └── mcp_client_demo.py # Example AI agent client
├── data/                 # Data storage directory
└── [enhanced components] # Clinical calculators, FHIR, etc.
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Setup directories and dependencies
python setup_mcp.py

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# ANTHROPIC_API_KEY=your-key
# OPENAI_API_KEY=your-key
```

### 2. Start MCP Server
```bash
python run_server.py
```

Server will start at `http://localhost:8000`

### 3. Test with Demo Client
```bash
# Full demonstration
python demo/mcp_client_demo.py

# Quick test
python demo/mcp_client_demo.py simple
```

## 📡 MCP Protocol Endpoints

### Standard MCP Methods
- **`initialize`** - Establish connection and capabilities
- **`resources/list`** - List available data resources
- **`resources/read`** - Read specific resource data
- **`tools/list`** - List available clinical tools
- **`tools/call`** - Execute clinical calculations
- **`prompts/list`** - List AI prompt templates
- **`prompts/get`** - Get formatted prompts

### HTTP API Endpoints
- **`GET /health`** - Server health check
- **`POST /mcp`** - Send MCP JSON-RPC requests
- **`WS /mcp/ws`** - WebSocket for real-time communication
- **`GET /mcp/resources`** - List resources (REST)
- **`GET /mcp/tools`** - List tools (REST)
- **`POST /mcp/tools/{tool_name}`** - Call tool (REST)

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
pytest mcp_server/
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