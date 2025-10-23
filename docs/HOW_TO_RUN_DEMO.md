# 🚀 How to Run Doct-Her

## 📋 Quick Start

**Doct-Her** is an AI-powered women's health consultation application using Claude Sonnet 4 via the Model Context Protocol (MCP).

### Launch Command
```bash
streamlit run demos/doct_her_stdio.py
```

### Access
- **URL**: http://localhost:8501
- **Interface**: Modern chat interface similar to Claude

---

## ✨ Features

### 🔬 Research Tools (12 Tools Available)
- **PubMed**: Search scientific articles, retrieve full article details
- **ESHRE Guidelines**: Access European fertility treatment guidelines
- **NAMS Protocols**: Menopause treatment protocols and position statements
- **ELSA Data**: English Longitudinal Study of Ageing research data

### 🧮 Clinical Calculators
- **IVF Success Prediction**: SART-based live birth probability calculator
- **FHIR Resources**: Create standardized healthcare data resources

### 🎯 AI-Powered
- **Claude Sonnet 4**: Latest Claude model for high-quality responses
- **Parallel Tool Usage**: Efficient multi-tool queries for comprehensive answers
- **Streaming Responses**: Real-time response generation
- **Tool Transparency**: View which tools Claude uses and why

---

## 🎮 How to Use

1. **Start the Application**
   ```bash
   streamlit run demos/doct_her_stdio.py
   ```

2. **Enter Your Question**
   - Type your women's health question in the input box
   - Click the ↑ button or press Enter to send

3. **View Results**
   - Watch as Claude uses relevant tools in real-time
   - See the comprehensive response with citations
   - Click "🔍 View log" to see which tools were used

### Example Questions

**IVF Success Prediction:**
```
I'm 38 years old with AMH of 0.8 ng/mL. What are my chances with IVF?
```

**Research Queries:**
```
What does recent research say about AMH levels and fertility after 35?
```

**Guidelines:**
```
What are the ESHRE guidelines for IVF in women over 40?
```

**Menopause:**
```
What are the NAMS recommendations for hormone replacement therapy?
```

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Required: Anthropic API Key for Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional: Enable real API calls for research tools
ENABLE_REAL_APIS=true
```

### MCP Server
The MCP server (`scripts/mcp_stdio_server.py`) runs automatically when you start Doct-Her. It provides:
- 12 research and clinical tools
- JSON-RPC communication via stdio
- Automatic tool schema generation

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Use a different port
streamlit run demos/doct_her_stdio.py --server.port 8502
```

### Missing Dependencies
```bash
# Install all requirements
pip install -r requirements.txt
```

### API Key Issues
```bash
# Verify your .env file exists and contains ANTHROPIC_API_KEY
cat .env | grep ANTHROPIC_API_KEY
```

### MCP Server Not Responding
The MCP server runs as a subprocess. If you see errors:
1. Check that `scripts/mcp_stdio_server.py` exists
2. Ensure the `mcp` package is installed: `pip install mcp`
3. Restart the Streamlit application

---

## 📊 Technical Details

### Architecture
```
User Input → Doct-Her UI → Claude (Sonnet 4) → MCP Server → Tools
                                ↓
                        Streaming Response ← Tool Results
```

### MCP Tools Available
1. `predict-ivf-success` - SART IVF calculator
2. `search_pubmed` - Search PubMed articles
3. `get_article` - Get full PubMed article
4. `get_multiple_articles` - Batch retrieve articles
5. `list_eshre_guidelines` - List ESHRE guidelines
6. `search_eshre_guidelines` - Search ESHRE guidelines
7. `get_eshre_guideline` - Get specific guideline
8. `list_nams_position_statements` - List NAMS statements
9. `search_nams_protocols` - Search NAMS protocols
10. `get_nams_protocol` - Get specific protocol
11. `list_elsa_waves` - List ELSA study waves
12. `search_elsa_data` - Search ELSA data
13. `create-fhir-resource` - Create FHIR resources
14. `query-research-database` - Generic research queries

### System Prompt
Doct-Her is configured to:
- Use tools in parallel when possible
- Provide evidence-based recommendations
- Include proper citations and confidence levels
- Explain reasoning transparently

---

## 🚀 Next Steps

1. **Explore**: Try different questions to see how Claude uses tools
2. **Customize**: Modify the system prompt in `doct_her_stdio.py` (line 298)
3. **Add Tools**: Extend `scripts/mcp_stdio_server.py` with new MCP tools
4. **Deploy**: Consider containerizing with Docker for production use

For more information on the MCP protocol, see [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md).
