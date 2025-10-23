# DoctHER: AI-Powered Women's Health Assistant

## Overview

DoctHER is a modern chat interface powered by Claude Sonnet 4, connected to an MCP (Model Context Protocol) server via stdio for evidence-based reproductive health consultations.

## Features

- 🩺 **Claude AI Integration** - Powered by Anthropic's Claude Sonnet 4
- 🧮 **Clinical Calculators** - IVF Success Prediction via SART database
- 📚 **Research Tools** - PubMed, ESHRE guidelines, NAMS protocols, ELSA data
- 📊 **Evidence-Based** - Real-time access to research databases and clinical guidelines
- 💬 **Intelligent Tool Usage** - Claude automatically selects and uses relevant tools
- 🔄 **Parallel Execution** - Multiple tools used simultaneously for efficient responses
- 🔒 **Privacy-Focused** - All processing happens locally, no external data storage

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required for AI-powered consultations
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Enable real API calls for research tools
ENABLE_REAL_APIS=true
```

**Get your Anthropic API key:**
1. Go to https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key

### 3. Start DoctHER

The MCP server runs automatically as a subprocess. Simply start DoctHER:

```bash
streamlit run demos/doct_her_stdio.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Example Questions

Claude automatically uses relevant tools based on your question:

**IVF Success Prediction:**
- "I'm 38 with AMH 0.8, what are my chances with IVF?"
- "Calculate IVF success rates for a 40-year-old with AMH 0.5"

**Research Queries:**
- "What does recent research say about AMH levels and fertility after 35?"
- "Find PubMed articles about IVF success rates in women over 40"

**Guidelines:**
- "What are the ESHRE guidelines for IVF in women over 40?"
- "Show me NAMS recommendations for hormone replacement therapy"

**Data Analysis:**
- "What does ELSA data show about menopause timing?"
- "Search for research on ovarian reserve markers"

### How It Works

1. **User Input** - You type your question in the chat interface

2. **Claude Processing** - Claude Sonnet 4 analyzes your question and determines which tools to use

3. **MCP Tool Calls** - Claude calls relevant tools via the stdio MCP server:
   - Can use multiple tools in parallel for efficiency
   - Automatically selects appropriate tools based on context
   - Tools communicate via JSON-RPC over stdio

4. **Tool Execution** - The MCP server executes the requested tools:
   - Clinical calculators run locally
   - Research tools query databases and APIs
   - Results are returned to Claude

5. **Response Generation** - Claude synthesizes tool results into a comprehensive, evidence-based response

6. **Streaming Display** - Response streams to the UI in real-time with tool usage transparency

## Available MCP Tools

Claude can automatically use any of these 14 tools:

### Clinical Calculators
1. **predict-ivf-success** - SART-based IVF success prediction
   - Inputs: Age, AMH, height, weight, BMI, egg source, cycle number
   - Outputs: Live birth probability for 1, 2, 3 cycles

### Research Tools
2. **search_pubmed** - Search PubMed for scientific articles
3. **get_article** - Retrieve full PubMed article details
4. **get_multiple_articles** - Batch retrieve multiple articles

### Guidelines & Protocols
5. **list_eshre_guidelines** - List available ESHRE guidelines
6. **search_eshre_guidelines** - Search ESHRE guidelines by topic
7. **get_eshre_guideline** - Get specific ESHRE guideline details
8. **list_nams_position_statements** - List NAMS position statements
9. **search_nams_protocols** - Search NAMS protocols
10. **get_nams_protocol** - Get specific NAMS protocol

### Research Data
11. **list_elsa_waves** - List ELSA study waves
12. **search_elsa_data** - Search ELSA longitudinal data

### Healthcare Integration
13. **create-fhir-resource** - Create FHIR-compliant healthcare resources
14. **query-research-database** - Generic research database queries

## Troubleshooting

### "Anthropic API key not configured"
Add your `ANTHROPIC_API_KEY` to the `.env` file and restart the app.

### "MCP server not responding"
The MCP server runs automatically as a subprocess. If you see errors:
1. Check that `scripts/mcp_stdio_server.py` exists
2. Ensure the `mcp` package is installed: `pip install mcp`
3. Restart the Streamlit application

### Import errors
Run the setup script:
```bash
python scripts/setup_mcp.py
```

### Port already in use
Kill existing processes:
```bash
# Find and kill Streamlit
pkill -f streamlit

# Find and kill MCP server
pkill -f run_server
```

## Technical Architecture

```
User Input (Streamlit)
    ↓
Claude Sonnet 4 (Anthropic SDK)
    ↓
Tool Selection & Execution
    ↓
MCP Server (stdio subprocess)
    ├─ predict-ivf-success
    ├─ search_pubmed
    ├─ search_eshre_guidelines
    ├─ search_nams_protocols
    └─ [11 other tools]
    ↓
Tool Results → Claude
    ↓
Synthesized Response (streaming)
    ↓
Display in Chat UI (Streamlit)
```

### MCP Communication
- **Protocol**: JSON-RPC 2.0
- **Transport**: stdio (stdin/stdout)
- **Format**: Newline-delimited JSON
- **Tool Discovery**: Automatic via MCP spec
- **Parallel Execution**: Supported when tools are independent

## Privacy & Security

- ✅ **Local Processing** - MCP server runs as a local subprocess
- ✅ **Stdio Communication** - No network exposure for MCP tools
- ✅ **No Data Storage** - Chat history only in browser session
- ✅ **API Security** - Only Anthropic API called for Claude access
- ✅ **Audit Trail** - Tool usage logged and visible to users

## Next Steps

### For Users
1. Add your Anthropic API key to `.env`
2. Start asking questions about fertility and reproductive health
3. Share the app with friends who might benefit

### For Developers
1. Add new MCP tools to `scripts/mcp_stdio_server.py`
2. Customize system prompt in `doct_her_stdio.py` (line 298)
3. Add conversation history persistence
4. Deploy to production with Docker containerization

## Support

For questions or issues:
- Check the main README: `/README.md`
- Review MCP Server Guide: `/docs/MCP_SERVER_GUIDE.md`
- File an issue on GitHub

## License

This project is part of the Women's Health MCP initiative to provide evidence-based AI infrastructure for reproductive health.
