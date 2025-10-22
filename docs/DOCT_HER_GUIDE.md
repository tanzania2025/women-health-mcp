# Doct-Her: AI-Powered Women's Health Assistant

## Overview

Doct-Her is a modern chat interface that acts as a wrapper around Claude AI, connected to local MCP (Model Context Protocol) servers for evidence-based reproductive health consultations.

## Features

- 🩺 **Claude AI Integration** - Powered by Anthropic's Claude 3.5 Sonnet
- 🧮 **Clinical Calculators** - Ovarian Reserve Assessment, IVF Success Prediction, Menopause Timing
- 📊 **Evidence-Based** - Uses ASRM guidelines and SART database
- 💬 **Natural Language** - Automatically extracts age, AMH, FSH from your questions
- 🔒 **Privacy-Focused** - Your data is processed securely and never stored

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

# MCP Server Configuration (optional, defaults shown)
MCP_SERVER_URL=http://localhost:8000
API_KEY=demo-api-key-change-in-production
```

**Get your Anthropic API key:**
1. Go to https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key

### 3. Start the MCP Server

In one terminal, start the MCP server:

```bash
python scripts/run_server.py
```

This will start the MCP server at `http://localhost:8000` with the clinical calculators.

### 4. Start Doct-Her

In another terminal, start the Doct-Her interface:

```bash
streamlit run demos/doct_her_app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Example Questions

The app automatically extracts clinical data from natural language. Try questions like:

**Fertility Assessment:**
- "I'm 38 with AMH 0.8, should I consider IVF?"
- "38 years old, AMH is 1.2 ng/ml, what are my options?"
- "I'm 35, AMH 2.5, FSH 8.5, should I freeze my eggs?"

**IVF Success Rates:**
- "What are my IVF success rates at age 40 with AMH 0.5?"
- "I'm 33 with AMH 3.2, what are my chances with IVF?"

**General Questions:**
- "What does a low AMH mean?"
- "At what age should I consider fertility preservation?"
- "How does age affect egg quality?"

### How It Works

1. **Extract Patient Data** - The app uses regex patterns to extract:
   - Age (e.g., "38 years old", "38 y/o")
   - AMH level (e.g., "AMH 0.8", "AMH is 1.2 ng/ml")
   - FSH level (e.g., "FSH 12.5")

2. **Gather MCP Context** - Calls local MCP server tools:
   - `assess-ovarian-reserve` - ASRM-based ovarian reserve assessment
   - `predict-ivf-success` - SART database IVF success prediction

3. **Build System Prompt** - Creates a comprehensive system prompt with:
   - Clinical context from MCP tools
   - Evidence-based guidelines
   - Your role as an AI assistant

4. **Call Claude API** - Sends to Claude 3.5 Sonnet with MCP context

5. **Stream Response** - Returns evidence-based, compassionate guidance

## Available MCP Tools

When you provide age and AMH data, the app automatically calls:

### 1. Ovarian Reserve Assessment
- **Based on:** ASRM guidelines
- **Inputs:** Age, AMH, FSH (optional)
- **Outputs:** Category, percentile, interpretation

### 2. IVF Success Prediction
- **Based on:** SART database (>50,000 cycles)
- **Inputs:** Age, AMH, cycle type
- **Outputs:** Live birth rate, confidence intervals

### 3. Menopause Prediction
- **Based on:** SWAN longitudinal study
- **Inputs:** Age, AMH, lifestyle factors
- **Outputs:** Predicted menopause timing, current stage

## Troubleshooting

### "Anthropic API key not configured"
Add your `ANTHROPIC_API_KEY` to the `.env` file and restart the app.

### "MCP server not running"
Start the MCP server first:
```bash
python scripts/run_server.py
```

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
Extract Patient Data (Regex)
    ↓
Gather MCP Context (HTTP → MCP Server)
    ├─ assess-ovarian-reserve
    └─ predict-ivf-success
    ↓
Build System Prompt (MCP Context)
    ↓
Call Claude API (Anthropic SDK)
    ↓
Display Response (Streamlit)
```

## Privacy & Security

- ✅ **Local Processing** - MCP servers run locally on your machine
- ✅ **Secure Communication** - API calls use HTTPS
- ✅ **No Data Storage** - Chat history only in browser session
- ✅ **HIPAA-Ready** - MCP server supports audit logging and encryption

## Next Steps

### For Users
1. Add your Anthropic API key to `.env`
2. Start asking questions about fertility and reproductive health
3. Share the app with friends who might benefit

### For Developers
1. Add new MCP tools (e.g., menopause prediction, PCOS assessment)
2. Implement streaming responses from Claude
3. Add conversation history persistence
4. Deploy to production with proper security

## Support

For questions or issues:
- Check the main README: `/README.md`
- Review MCP Server Guide: `/docs/MCP_SERVER_GUIDE.md`
- File an issue on GitHub

## License

This project is part of the Women's Health MCP initiative to provide evidence-based AI infrastructure for reproductive health.
