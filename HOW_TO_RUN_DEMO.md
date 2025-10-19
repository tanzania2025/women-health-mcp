# 🚀 How to Run the Women's Health MCP Demo

## 📋 **Quick Reference**

| Demo Type | Command | URL | Purpose |
|-----------|---------|-----|---------|
| **🌐 Streamlit Web Demo** | `streamlit run streamlit_demo.py` | http://localhost:8501 | Interactive web interface |
| **🤖 Complete SWAN Integration** | `python swan_mcp_demo.py` | Terminal | End-to-end pipeline demo |
| **⚡ Quick Claude Integration** | `python claude_mcp_integration.py` | Terminal | AI consultation workflow |
| **🖥️ MCP Server** | `python run_server.py` | http://localhost:8000 | Production server |
| **🧪 Component Testing** | `python test_streamlit_demo.py` | Terminal | Verify all components work |

---

## 🎯 **Recommended Demo Sequence**

### **1. Start with Streamlit Web Demo** (Most Interactive)
### **2. Run SWAN Integration Demo** (Complete Pipeline) 
### **3. Test Claude Integration** (AI Workflow)
### **4. Optional: MCP Server** (Production Ready)

---

## 🌐 **1. Streamlit Web Demo** (Recommended First)

### **🎯 Best For**: Interactive exploration, visual demonstrations, non-technical users

### **Setup & Launch**
```bash
# Navigate to project directory
cd /Users/sunaina/code/women-health-mcp

# Install dependencies (if not already done)
pip install streamlit plotly

# Launch interactive web demo
streamlit run streamlit_demo.py
```

### **📱 Access the Demo**
- **URL**: http://localhost:8501
- **Interface**: Full web application with sidebar navigation
- **Features**: 5 interactive demo modes

### **🎮 How to Use**
1. **Check SWAN Status**: Sidebar should show "✅ 2413 participants loaded"
2. **Choose Demo Mode**: Use sidebar dropdown
3. **Explore Features**: Each mode has different interactive capabilities

### **📊 Demo Modes Available**

#### **📊 SWAN Dataset Explorer**
- View real SWAN dataset overview (2,413 participants, 1,018 variables)
- Search variables by keyword (try "ESTR", "MENO", "AGE")
- Browse demographic breakdown by ethnicity

#### **🧮 Clinical Calculator**
- **Input**: Age (18-55), AMH level, optional FSH/AFC
- **Try**: Age 38, AMH 0.8, FSH 12.5
- **Output**: Ovarian reserve classification + IVF success gauge

#### **🤖 AI Fertility Consultation**
- **Input**: Patient scenario and clinical question
- **Default**: "38-year-old with AMH 0.8, should I do IVF?"
- **Output**: Complete evidence-based consultation with visualizations

#### **📈 Population Analysis**
- **Input**: Condition, age range, ethnicity filters
- **Try**: "menopause timing", ages 45-55
- **Output**: Population statistics with interactive charts

#### **🔬 Hormone Variables**
- **Input**: Hormone type selection (Estrogen, FSH, AMH, etc.)
- **Try**: "Estrogen" → Select "ESTROG17" for analysis
- **Output**: Statistical summary and distribution charts

### **⚠️ Troubleshooting**
```bash
# If port 8501 is busy
streamlit run streamlit_demo.py --server.port 8502

# If dependencies missing
pip install streamlit plotly pandas numpy

# If SWAN data not loading
# Check that raw_data/ICPSR_31901 directory exists
ls /Users/sunaina/code/women-health-mcp/raw_data/ICPSR_31901/
```

---

## 🤖 **2. SWAN Integration Demo** (Complete Pipeline)

### **🎯 Best For**: Understanding the complete data flow, technical demonstrations

### **Launch**
```bash
# Navigate to project directory  
cd /Users/sunaina/code/women-health-mcp

# Run complete SWAN integration demo
python swan_mcp_demo.py
```

### **📋 What You'll See**
```
🌊 ============================================================
   SWAN Data Integration with Women's Health MCP
   Real Research Data → AI Clinical Recommendations
================================================================

🚀 Initializing MCP Server...
   ✅ MCP Server ready with 9 clinical tools

📊 Checking SWAN Dataset Status...
   ✅ SWAN Dataset: 2413 participants, 1018 variables

🤖 AI Agent Query Example:
   Patient Question: "I'm 38 with AMH 0.8 ng/mL. Should I do IVF now?"

📈 Step 1: Query SWAN Population Data...
   ✅ SWAN context retrieved

🧮 Step 2: Clinical Ovarian Reserve Assessment...
   🔬 Ovarian Reserve: low
   📊 Population Percentile: 30th
   ✅ ASRM assessment completed

🎯 Step 3: IVF Success Rate Prediction...
   📈 Live Birth Rate: 23.1%
   📊 Confidence Interval: [15.1, 31.1]
   ✅ SART-based prediction completed

🔬 Step 4: SWAN Hormone Variable Analysis...
   🧪 Found 8 estrogen-related variables
   ✅ Hormone data available for analysis

🎯 AI-Powered Clinical Recommendation:
================================================================
📊 POPULATION CONTEXT (SWAN DATA):
   Your AMH level (0.8 ng/mL) places you in the 30th percentile.
   
🧮 CLINICAL ASSESSMENT:
   • Ovarian Reserve: Low (ASRM criteria)
   • IVF Success Rate: 23.1% per fresh cycle (SART data)
   
⚡ URGENCY ASSESSMENT: HIGH
   Age 38 with AMH 0.8 indicates time-sensitive fertility window.
   
💡 RECOMMENDATION:
   Schedule fertility consultation within 1-2 months.
   
📚 EVIDENCE BASIS:
   • SWAN Study: 2413 participants, longitudinal data
   • SART Database: >50,000 IVF cycles for age-adjusted rates
================================================================
```

### **🔍 What This Demonstrates**
- Real SWAN dataset loading (2,413 participants)
- MCP protocol tool execution
- Clinical calculator integration
- Evidence-based AI recommendation synthesis
- Complete data pipeline from research → clinical insights

---

## ⚡ **3. Claude Integration Demo** (AI Workflow)

### **🎯 Best For**: Understanding AI agent integration, Claude API workflow

### **Launch**
```bash
# Navigate to project directory
cd /Users/sunaina/code/women-health-mcp

# Run Claude integration demo
python claude_mcp_integration.py
```

### **📋 What You'll See**
```
🔗 ============================================================
   Claude AI + Women's Health MCP Integration Demo
   Evidence-Based Fertility Consultation
================================================================

👤 Patient Profile:
   Age: 38 years
   AMH: 0.8 ng/mL
   Question: I'm 38 years old with AMH 0.8 ng/mL. Should I start IVF immediately or wait?

🤖 Claude AI Processing with MCP Context...

🧮 Gathering ovarian reserve assessment...
   ✅ Ovarian reserve: low

📈 Gathering IVF success prediction...
   ✅ IVF success rate: 23.1%

📊 Gathering SWAN population context...
   ✅ SWAN context: Population data retrieved

📋 Getting consultation prompt template...
   ✅ Consultation prompt template retrieved

🧠 Claude AI generating evidence-based response...
   🔑 Anthropic API Key configured: sk-ant-api03-CVK49rK...
   ⚠️  Actual Claude API call would happen here
   ✅ Evidence-based response generated

[Complete evidence-based consultation response with clinical reasoning]
```

### **🔍 What This Demonstrates**
- How Claude AI would integrate with MCP server
- Context gathering from multiple clinical tools
- Prompt template generation
- Evidence synthesis workflow
- Ready for real Anthropic API integration

---

## 🖥️ **4. MCP Server** (Production Ready)

### **🎯 Best For**: API integration, production deployment, external AI agents

### **Setup Environment**
```bash
# Ensure .env file exists with your API keys
cat .env

# Should contain:
# ANTHROPIC_API_KEY=your-anthropic-api-key
# API_KEY=your-server-api-key
```

### **Launch Server**
```bash
# Navigate to project directory
cd /Users/sunaina/code/women-health-mcp

# Start MCP server
python run_server.py
```

### **📋 Expected Output**
```
🚀 Starting Women's Health MCP Server...
==================================================
✓ Core dependencies found
✓ .env file found

📡 MCP Server Configuration:
  Host: 0.0.0.0
  Port: 8000
  Debug: true

🔗 Available Endpoints:
  Health Check: http://localhost:8000/health
  MCP Resources: http://localhost:8000/mcp/resources
  MCP Tools: http://localhost:8000/mcp/tools
  WebSocket: ws://localhost:8000/mcp/ws

⭐ Features Available:
  ✓ Model Context Protocol (MCP) compliance
  ✓ Clinical calculators (ovarian reserve, IVF success)
  ✓ Research database integration (SWAN, SART)
  ✓ FHIR R4 compliant resources
  ✓ AI prompt templates
  ✓ WebSocket real-time communication

Starting server... (Press Ctrl+C to stop)
```

### **🧪 Test the Server**
```bash
# Health check
curl http://localhost:8000/health

# List available tools (requires API key)
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/mcp/tools

# Call ovarian reserve tool
curl -X POST http://localhost:8000/mcp/tools/assess-ovarian-reserve \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"age": 38, "amh": 0.8}'
```

---

## 🧪 **5. Component Testing** (Verification)

### **🎯 Best For**: Troubleshooting, verifying setup, CI/CD

### **Launch**
```bash
# Navigate to project directory
cd /Users/sunaina/code/women-health-mcp

# Test all components
python test_streamlit_demo.py
```

### **📋 Expected Output**
```
🌊 Women's Health MCP Streamlit Demo Test
Testing integration with real SWAN data

🧪 Testing Streamlit Demo Components
==================================================

1️⃣ Testing MCP Server Initialization...
   ✅ MCP Server initialized successfully

2️⃣ Testing SWAN Dataset Status...
   ✅ SWAN Dataset loaded: 2413 participants
   📊 Variables available: 1018

3️⃣ Testing Clinical Calculators...
   ✅ Ovarian reserve calculator working
   ✅ IVF success predictor working

4️⃣ Testing SWAN Data Queries...
   ✅ SWAN population queries working

5️⃣ Testing Variable Search...
   ✅ Variable search working: Found 8 estrogen variables

6️⃣ Testing Variable Summary...
   ✅ Variable summary working for ESTROG17

🎉 All Streamlit Demo Components Working!

📋 Demo Features Available:
   ✅ 📊 SWAN Dataset Explorer
   ✅ 🧮 Clinical Calculator
   ✅ 🤖 AI Fertility Consultation
   ✅ 📈 Population Analysis
   ✅ 🔬 Hormone Variables
```

---

## ⚙️ **System Requirements**

### **Dependencies**
```bash
# Core requirements
pip install pandas numpy asyncio

# Streamlit demo
pip install streamlit plotly

# MCP server (optional)
pip install fastapi uvicorn pydantic-settings

# Claude integration (optional)
pip install anthropic
```

### **Data Requirements**
- **SWAN Dataset**: `/Users/sunaina/code/women-health-mcp/raw_data/ICPSR_31901/`
- **File**: `DS0001/31901-0001-Data.tsv` (2,413 participants, 1,018 variables)

### **Environment Variables** (Optional)
```bash
# Create .env file
ANTHROPIC_API_KEY=your-anthropic-api-key
API_KEY=your-server-api-key
DEBUG=true
```

---

## 🔧 **Troubleshooting**

### **SWAN Data Not Loading**
```bash
# Check data file exists
ls /Users/sunaina/code/women-health-mcp/raw_data/ICPSR_31901/DS0001/

# Should show: 31901-0001-Data.tsv
# If missing, verify download location
```

### **Port Already in Use**
```bash
# For Streamlit (default 8501)
streamlit run streamlit_demo.py --server.port 8502

# For MCP Server (default 8000)
# Edit run_server.py to change port
```

### **Import Errors**
```bash
# Ensure project root in Python path
export PYTHONPATH="/Users/sunaina/code/women-health-mcp:$PYTHONPATH"

# Or run from project directory
cd /Users/sunaina/code/women-health-mcp
python swan_mcp_demo.py
```

### **Module Not Found**
```bash
# Install missing dependencies
pip install streamlit plotly pandas numpy asyncio fastapi

# Or install all at once
pip install -r requirements.txt  # if requirements.txt exists
```

---

## 🎯 **Demo Objectives**

### **Technical Demonstration**
- ✅ Real SWAN dataset integration (2,413 participants)
- ✅ MCP protocol implementation (JSON-RPC 2.0)
- ✅ Clinical calculator validation (ASRM/ESHRE)
- ✅ AI agent context gathering
- ✅ Evidence-based recommendation synthesis

### **Clinical Validation**
- ✅ Ovarian reserve assessment (age + AMH → percentile)
- ✅ IVF success prediction (SART database integration)
- ✅ Population context (SWAN longitudinal study)
- ✅ Urgency assessment (time-sensitive fertility decisions)

### **Infrastructure Readiness**
- ✅ Production MCP server (FastAPI + WebSocket)
- ✅ Interactive web interface (Streamlit)
- ✅ API authentication and security
- ✅ Real-time clinical tool execution
- ✅ Standardized protocol for AI agents

---

## 🏆 **Success Metrics**

After running any demo, you should see:

### **Data Integration** ✅
- SWAN dataset: 2,413 participants loaded
- Variables: 1,018 clinical measures available
- Hormone variables: 8 estrogen variables found

### **Clinical Tools** ✅
- Ovarian reserve: Classification + percentile
- IVF success: Age-adjusted rates with confidence intervals
- Population context: SWAN study comparisons

### **AI Readiness** ✅
- MCP protocol: JSON-RPC 2.0 compliance
- Context gathering: Multi-tool orchestration
- Evidence synthesis: Guidelines + data + population context

**🎉 This demonstrates the complete infrastructure needed for the $50B women's health AI market with real research-grade evidence backing every recommendation!**

---

## 🚀 **Quick Start Commands**

```bash
# 1. Interactive Web Demo (Recommended)
streamlit run streamlit_demo.py
# → Open http://localhost:8501

# 2. Complete Pipeline Demo
python swan_mcp_demo.py

# 3. Claude AI Integration Demo  
python claude_mcp_integration.py

# 4. Verify Everything Works
python test_streamlit_demo.py

# 5. Production MCP Server (Optional)
python run_server.py
```

**Choose your demo based on your needs and enjoy exploring the future of evidence-based women's health AI!** 🌊✨