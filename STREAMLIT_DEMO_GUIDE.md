# 🌊 Women's Health MCP Streamlit Demo

## 🎯 **Interactive Web Demo Showcasing Real SWAN Data Integration**

This Streamlit demo provides a **comprehensive interactive interface** to explore the complete Women's Health MCP system with real SWAN dataset integration.

## 🚀 **Quick Start**

### Launch the Demo
```bash
# Navigate to project directory
cd /Users/sunaina/code/women-health-mcp

# Launch Streamlit demo
streamlit run streamlit_demo.py

# Demo will be available at: http://localhost:8501
```

### Test Components First
```bash
# Verify everything is working
python test_streamlit_demo.py
```

## 📊 **Demo Features Overview**

### 1. **📊 SWAN Dataset Explorer**
**Purpose**: Explore the real SWAN research dataset
- **Participants**: 2,413 women from Visit 07 (2003-2005)
- **Variables**: 1,018 clinical and demographic variables
- **Demographics**: 5 ethnic groups (African American, Caucasian, Chinese, Hispanic, Japanese)
- **Variable Search**: Find specific variables by keyword (e.g., "ESTR", "MENO", "AGE")

**What You Can Do**:
- View dataset overview and statistics
- Browse sample variables 
- Search for specific hormone or clinical variables
- Explore demographic breakdown

### 2. **🧮 Clinical Calculator**
**Purpose**: Evidence-based reproductive health calculations
- **ASRM/ESHRE Guidelines**: Ovarian reserve assessment
- **SART Database**: IVF success rate predictions
- **Interactive Inputs**: Age, AMH, FSH, antral follicle count

**What You Can Do**:
- Input patient data (age 18-55, AMH levels, optional FSH/AFC)
- Get real-time ovarian reserve classification
- View IVF success rate gauge with confidence intervals
- See evidence-based clinical recommendations

**Sample Inputs**:
- **Age**: 38 years
- **AMH**: 0.8 ng/mL
- **FSH**: 12.5 mIU/mL
- **AFC**: 8 follicles

### 3. **🤖 AI Fertility Consultation**
**Purpose**: Complete AI-powered clinical consultation pipeline
- **MCP Context Gathering**: Real-time clinical assessments
- **Evidence Synthesis**: ASRM guidelines + SART data + SWAN population context
- **Urgency Assessment**: Time-sensitive fertility window analysis

**What You Can Do**:
- Enter patient scenario and clinical question
- Watch AI processing steps with progress bar
- Receive comprehensive evidence-based consultation
- View clinical context visualizations (success rates by age, AMH percentiles)

**Demo Scenario**:
```
Patient: 38-year-old with AMH 0.8 ng/mL
Question: "Should I start IVF immediately or wait?"
Result: Evidence-based recommendation with urgency assessment
```

### 4. **📈 Population Analysis**
**Purpose**: SWAN population-level statistical analysis
- **Age Filtering**: Analyze specific age ranges
- **Ethnicity Filtering**: Multi-ethnic population breakdowns
- **Condition Analysis**: Menopause timing, hormone levels, demographics

**What You Can Do**:
- Filter SWAN data by age range (40-70 years)
- Select specific conditions to analyze
- Generate age distribution histograms
- View ethnicity breakdowns with pie charts and bar graphs

### 5. **🔬 Hormone Variables**
**Purpose**: Detailed hormone variable exploration
- **8 Estrogen Variables**: ESTROG17, ESTRTW17, etc.
- **Statistical Analysis**: Count, mean, median, standard deviation
- **Value Distribution**: Top value frequency charts

**What You Can Do**:
- Search by hormone type (Estrogen, FSH, AMH, Progesterone)
- Select specific variables for detailed analysis
- View statistical summaries and distributions
- Explore value frequency charts

## 🎮 **Interactive Demo Walkthrough**

### **Getting Started**
1. **Launch Demo**: `streamlit run streamlit_demo.py`
2. **Check Sidebar**: SWAN dataset status should show "✅ 2413 participants loaded"
3. **Navigate Modes**: Use sidebar dropdown to switch between demo modes

### **Recommended Demo Flow**

#### **Step 1: Explore SWAN Dataset** 📊
- Select "📊 SWAN Dataset Explorer"
- View dataset overview metrics
- Try searching for "ESTR" to find estrogen variables
- Browse the demographic breakdown

#### **Step 2: Use Clinical Calculator** 🧮
- Select "🧮 Clinical Calculator"
- Input: Age 38, AMH 0.8, FSH 12.5
- Click "🧮 Calculate Clinical Assessment"
- Observe ovarian reserve classification and IVF success gauge

#### **Step 3: AI Consultation** 🤖
- Select "🤖 AI Fertility Consultation"
- Keep default patient data or modify
- Click "🤖 Generate AI Consultation"
- Watch progress bar as MCP context is gathered
- Review comprehensive evidence-based response

#### **Step 4: Population Analysis** 📈
- Select "📈 Population Analysis"
- Choose "menopause timing" condition
- Set age range 45-55
- Click "📊 Run Population Analysis"
- Explore age distribution and ethnicity breakdowns

#### **Step 5: Hormone Deep Dive** 🔬
- Select "🔬 Hormone Variables"
- Choose "Estrogen" hormone type
- Click "🔬 Search Hormone Variables"
- Select "ESTROG17" for detailed analysis
- View statistical summary and distribution

## 📈 **Demo Highlights**

### **Real Data Integration** ✅
- **Live SWAN Data**: 2,413 real participants, not mock data
- **1,018 Variables**: Comprehensive reproductive health dataset
- **Multi-Ethnic**: 5 population groups for diverse insights

### **Clinical Accuracy** ✅
- **ASRM Guidelines**: Evidence-based ovarian reserve classification
- **SART Success Rates**: Real IVF outcome predictions
- **Population Context**: How patient compares to research cohorts

### **Interactive Visualizations** ✅
- **Success Rate Gauges**: Real-time IVF probability meters
- **Age Distribution Charts**: Population-level statistical analysis
- **AMH Percentile Plots**: Where patients fall in population distributions
- **Ethnicity Breakdowns**: Demographic analysis with pie/bar charts

### **AI Integration Ready** ✅
- **MCP Protocol**: Standardized context gathering for AI agents
- **Evidence Synthesis**: Combines multiple data sources seamlessly
- **Clinical Reasoning**: Step-by-step diagnostic logic display

## 🔧 **Technical Details**

### **Architecture**
```
Streamlit UI → MCP Server → SWAN Data Integration → Clinical Calculators
     ↓              ↓               ↓                      ↓
Interactive    JSON-RPC 2.0    Real TSV Data        ASRM/ESHRE
 Web App       Protocol         2,413 Records        Guidelines
```

### **Performance**
- **Caching**: Streamlit `@st.cache_resource` for MCP server initialization
- **Data Loading**: One-time SWAN dataset loading with pandas
- **Real-time**: Live calculations without pre-computed results

### **Dependencies**
- **Streamlit**: Web interface framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: SWAN data processing
- **AsyncIO**: MCP server communication

## 🎯 **Use Cases Demonstrated**

### **For Healthcare Providers**
- **Clinical Decision Support**: Evidence-based fertility consultation
- **Population Context**: How patients compare to research data
- **Risk Stratification**: Urgency assessment based on age/biomarkers

### **For AI Developers**
- **MCP Integration**: How AI agents gather clinical context
- **Data Pipeline**: Real research data → standardized protocol → AI insights
- **Evidence Synthesis**: Combining guidelines, databases, and population data

### **For Researchers**
- **SWAN Data Exploration**: Interactive analysis of longitudinal study
- **Variable Discovery**: Search and analyze specific clinical measures
- **Population Statistics**: Age, ethnicity, and condition breakdowns

### **For Patients/Advocates**
- **Transparency**: See exactly how recommendations are generated
- **Population Context**: Understand where they fit in research data
- **Evidence Basis**: Clear sources for all clinical insights

## 🚀 **Production Extensions**

### **Real Claude Integration**
```python
# Add to demo with ANTHROPIC_API_KEY
import anthropic

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
response = await client.messages.create(
    model="claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": mcp_context + patient_question}]
)
```

### **Enhanced Visualizations**
- **3D Population Plots**: Age × AMH × Success Rate surfaces
- **Time Series**: Longitudinal SWAN data over multiple visits
- **Risk Heatmaps**: Population-level outcome predictions

### **Additional Data Sources**
- **SART Real-time API**: Live IVF success rate updates
- **PubMed Integration**: Latest research paper context
- **EHR Connectivity**: Real patient data input

## 📊 **Demo Success Metrics**

The demo successfully demonstrates:

✅ **Real SWAN Data**: 2,413 participants, 1,018 variables loaded
✅ **Clinical Tools**: 8 MCP tools operational
✅ **Interactive UI**: 5 demo modes with rich visualizations  
✅ **Evidence Integration**: ASRM + SART + SWAN synthesis
✅ **AI Ready**: Complete MCP protocol implementation

**🎉 This demo showcases the complete infrastructure needed for the $50B women's health AI market with real research-grade data backing every recommendation.**

---

## 🖱️ **Try It Now**

```bash
streamlit run streamlit_demo.py
```

**Open:** http://localhost:8501

**Experience the future of evidence-based women's health AI!** 🌊✨