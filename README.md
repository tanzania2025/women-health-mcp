# Women's Health MCP - Complete Solution

🚀 **Comprehensive Women's Health AI Infrastructure** - Production MCP Servers + Research Framework

This repository provides two complementary approaches to women's health AI systems:
1. **Production MCP Servers** (`/mcp_servers/`) - Ready-to-use servers for Claude Desktop
2. **Research Framework** (`/framework/`) - Multi-modal context protocol demonstration

## 🎯 Quick Start

### Option 1: Production MCP Servers (Recommended for Claude Desktop)

The `/mcp_servers/` directory contains **production-ready MCP servers** using the official Anthropic Model Context Protocol. These servers work immediately with Claude Desktop.

**Available Servers:**
- 📚 **PubMed** - Search and retrieve scientific articles
- 📋 **ASRM Guidelines** - American Society for Reproductive Medicine practice guidelines
- 🧮 **SART IVF Calculator** - IVF success rate predictions (live calculator integration)
- 🌡️ **Menopause Predictor** - Menopause age estimation with SWAN data validation
- 📖 **NAMS Protocols** - North American Menopause Society clinical protocols
- 🔬 **ESHRE Guidelines** - European Society of Human Reproduction guidelines
- 📊 **ELSA Data Access** - English Longitudinal Study of Ageing data queries
- 🏥 **NHS API** - Direct access to NHS patient health records (UK)

**Installation:**
```bash
cd mcp_servers/
pip install -r requirements.txt

# For NHS API (TypeScript):
cd nhs_api/
npm install
npm run build
```

**Configuration for Claude Desktop:**

macOS: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "pubmed": {
      "command": "/Users/your-username/anaconda3/bin/python",
      "args": ["/path/to/women-health-mcp/mcp_servers/pubmed_server.py"]
    },
    "sart-ivf": {
      "command": "/Users/your-username/anaconda3/bin/python",
      "args": ["/path/to/women-health-mcp/mcp_servers/sart_ivf_server.py"]
    },
    "nhs-data": {
      "command": "node",
      "args": ["/path/to/women-health-mcp/mcp_servers/nhs_api/build/index.js"]
    }
  }
}
```

**Usage Examples:**
```
"Search PubMed for recent studies on AMH levels and ovarian reserve"
"Calculate IVF success rates for a 35-year-old with PCOS, AMH 2.5 ng/ml"
"Show me ASRM guidelines for diminished ovarian reserve"
"What does ESHRE recommend for endometriosis treatment?"
"Predict menopause age for 45-year-old, mother's menopause at 52"
```

📖 **Detailed Documentation:** See `/mcp_servers/docs/` for server-specific guides

---

### Option 2: Research Framework (For Development & Research)

The `/framework/` directory contains the **enhanced Multi-Modal Context Protocol framework** - a demonstration of standardized infrastructure for women's health AI systems.

**Features:**
- Custom WH-MCP protocol implementation
- Clinical calculators (ovarian reserve, IVF success, menopause prediction)
- Multi-platform data integration (cycle tracking apps, wearables)
- HIPAA-compliant privacy and security layer
- FHIR R4 data exchange
- Research database integration (SWAN, SART, PubMed)

**Running the Framework:**
```bash
cd framework/
python enhanced_mcp_demo.py
```

This demonstrates the conceptual MCP architecture and data flow patterns.

---

## 📊 Comparison: MCP Servers vs Framework

| Feature | Production MCP Servers | Research Framework |
|---------|----------------------|-------------------|
| **Integration** | Direct Claude Desktop integration | Demonstration/research code |
| **MCP Protocol** | Official Anthropic MCP | Custom WH-MCP protocol |
| **Data Sources** | Live API calls (PubMed, SART, NHS, ELSA) | Mock/simulated data |
| **Use Case** | Production clinical decision support | Research & development |
| **Setup** | Add to Claude config, ready to use | Run demos to explore concepts |
| **Documentation** | Per-server detailed guides | Architecture overview |

## 🏗️ Project Structure

```
women-health-mcp/
├── mcp_servers/           # Production MCP servers
│   ├── pubmed_server.py
│   ├── asrm_server.py
│   ├── sart_ivf_server.py
│   ├── menopause_server.py
│   ├── nams_server.py
│   ├── eshre_server.py
│   ├── elsa_server.py
│   ├── nhs_api/          # NHS API TypeScript server
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── test_*.py         # Test files for each server
│   ├── requirements.txt
│   └── docs/             # Server documentation
│       ├── PUBMED_MCP_README.md
│       ├── ASRM_MCP_README.md
│       ├── SART_IVF_README.md
│       ├── NAMS_MCP_README.md
│       ├── ESHRE_MCP_README.md
│       ├── ELSA_README.md
│       └── NHS_*.md      # NHS API setup guides
│
├── framework/            # Research framework (original code)
│   ├── womens_health_mcp.py
│   ├── clinical_calculators.py
│   ├── patient_data_integration.py
│   ├── privacy_security.py
│   ├── research_database_integration.py
│   ├── fhir_integration.py
│   ├── enhanced_mcp_demo.py
│   └── ...
│
├── docs/                 # General documentation
└── README.md            # This file
```

## 🔬 Featured MCP Servers

### SART IVF Calculator
Calculates IVF success probabilities using live data from the Society for Assisted Reproductive Technology calculator (Aberdeen University).

**Example:**
```
Calculate IVF success for 38-year-old, 165cm, 65kg, with PCOS
```
**Output:**
```
After 1 cycle: 45.2% live birth probability
After 2 cycles: 69.8%
After 3 cycles: 82.1%
```

### PubMed Integration
Real-time search and retrieval of scientific articles from the PubMed database.

**Example:**
```
Search PubMed for systematic reviews on AMH and egg freezing published after 2022
```

### ELSA Data Access
Query the English Longitudinal Study of Ageing database for population-level insights on women's health across the lifespan.

**Example:**
```
What does ELSA data show about menopause timing and cognitive function?
```

### NHS API
Secure OAuth2-authenticated access to NHS patient health records (UK only).

**Example:**
```
Show my current medications and upcoming appointments
```

## 🚀 Use Cases

### Clinical Decision Support
- **IVF Planning**: Calculate age-specific success rates with personalized factors
- **Fertility Assessment**: Evaluate ovarian reserve using validated calculators
- **Treatment Guidelines**: Access ASRM, ESHRE, NAMS clinical protocols

### Research & Education
- **Literature Review**: Search PubMed for latest studies and systematic reviews
- **Population Data**: Query ELSA for epidemiological insights
- **Protocol Development**: Reference evidence-based guidelines

### Patient Care
- **Personalized Predictions**: Menopause timing, fertility window estimation
- **Treatment Planning**: Evidence-based IVF protocol selection
- **Health Records**: Integrated NHS data access (UK)

## 🔒 Security & Privacy

- **NHS API**: OAuth2 authentication, FHIR-compliant, GDPR-ready
- **Data Handling**: No PHI stored by MCP servers
- **Credentials**: Use environment variables, never commit secrets
- **Audit**: All API calls logged for transparency

## 📖 Documentation

- **MCP Server Guides**: `/mcp_servers/docs/`
- **NHS API Setup**: `/mcp_servers/docs/NHS_*.md`
- **Framework Architecture**: `/framework/` (see original README)
- **Configuration Examples**: `/mcp_servers/docs/*_config.json`

## 🤝 Contributing

Contributions welcome! This project combines:
- Production MCP servers for real-world clinical use
- Research framework for exploring multi-modal AI architectures

Please ensure:
- MCP servers follow official Anthropic MCP specification
- Security and privacy are maintained
- Documentation is updated
- No sensitive data in commits

## 📚 References

- [Anthropic MCP Documentation](https://modelcontextprotocol.io/)
- [SART IVF Calculator](https://w3.abdn.ac.uk/clsm/SARTIVF/)
- [PubMed API](https://www.ncbi.nlm.nih.gov/home/develop/api/)
- [NHS FHIR API](https://digital.nhs.uk/developer/api-catalogue)
- [ELSA Study](https://www.elsa-project.ac.uk/)

## 📄 License

MIT

## ⚠️ Disclaimer

This software is for informational and research purposes. Not a substitute for professional medical advice. Always consult qualified healthcare professionals for clinical decisions.

The NHS API integration is for personal health record access only. Not affiliated with or endorsed by NHS Digital.
