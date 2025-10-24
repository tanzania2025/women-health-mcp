#!/usr/bin/env python3
"""
DoctHER: AI-Powered Women's Health Assistant
Modern chat interface using Claude with stdio MCP servers
"""

import streamlit as st
import sys
import os
import re
import asyncio
from pathlib import Path
from contextlib import AsyncExitStack
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DoctHER - Your AI Women's Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# MCP Server Script Path
MCP_SERVER_SCRIPT = str(Path(__file__).parent.parent / "scripts" / "mcp_stdio_server.py")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput > label {display: none !important;}

    /* Force light mode only - no dark mode support */
    :root {
        color-scheme: light only !important;
        --primary-rose: #ff6b9d;
        --secondary-coral: #ff8e72;
        --accent-gold: #ffd89b;
        --bg-cream: #fef8f4;
        --bg-rose: #fff5f8;
    }

    html, body, .stApp {
        color-scheme: light only !important;
        background: var(--bg-cream) !important;
    }

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }

    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    .main {
        background:
            radial-gradient(ellipse at 10% 20%, rgba(255, 107, 157, 0.08) 0%, transparent 45%),
            radial-gradient(ellipse at 90% 70%, rgba(255, 142, 114, 0.08) 0%, transparent 45%),
            radial-gradient(ellipse at 50% 50%, rgba(255, 216, 155, 0.06) 0%, transparent 50%),
            linear-gradient(180deg, #fef8f4 0%, #fff5f8 50%, #fef8f4 100%);
        padding: 0;
        position: relative;
        overflow: hidden;
    }

    .main::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background:
            radial-gradient(circle at 20% 80%, rgba(255, 107, 157, 0.03) 0%, transparent 25%),
            radial-gradient(circle at 80% 20%, rgba(255, 142, 114, 0.03) 0%, transparent 25%),
            radial-gradient(circle at 40% 40%, rgba(255, 216, 155, 0.02) 0%, transparent 25%);
        animation: float 20s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    .main::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ff6b9d' fill-opacity='0.02'%3E%3Ccircle cx='50' cy='50' r='1'/%3E%3Ccircle cx='25' cy='25' r='1'/%3E%3Ccircle cx='75' cy='75' r='1'/%3E%3Ccircle cx='25' cy='75' r='1'/%3E%3Ccircle cx='75' cy='25' r='1'/%3E%3C/g%3E%3C/svg%3E");
        pointer-events: none;
        opacity: 0.5;
        z-index: 0;
    }

    .block-container {
        padding-top: 3rem;
        max-width: 900px;
    }

    .landing-container {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 20vh;
        padding-bottom: 3rem;
        text-align: center;
    }

    /* Hide streamlit default elements for cleaner UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Ensure body has proper height */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* Remove default streamlit padding when chat is active */
    .stApp {
        margin: 0;
        padding: 0;
    }

    .logo {
        font-family: 'Playfair Display', serif;
        font-size: 5.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #c2185b 0%, #ff6b9d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
        position: relative;
        display: inline-block;
        filter: drop-shadow(0 8px 32px rgba(255, 107, 157, 0.15));
    }

    .logo::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 110%;
        height: 110%;
        background: radial-gradient(circle, rgba(255, 107, 157, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        z-index: -1;
        filter: blur(40px);
    }

    .tagline {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        background: linear-gradient(135deg, #c2185b 0%, #ff6b9d 50%, #ff8e72 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2.5rem;
        font-weight: 500;
        font-style: italic;
        letter-spacing: 0.5px;
        opacity: 0.9;
    }

    .powered-by {
        font-size: 0.75rem;
        color: #94a3b8;
        opacity: 0.6;
        margin-top: -1rem;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    /* Chat container - scrollable area */
    .chat-container {
        max-width: 1680px;
        margin: 0 auto;
        padding: 0 2rem 120px 2rem;
        min-height: auto;
        overflow-y: auto;
    }

    /* Input container - centered on landing page */
    .input-container.centered {
        max-width: 700px;
        margin: 0 auto 1.5rem auto;
    }

    /* Input container - fixed at bottom after first message */
    .input-container-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to bottom, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 20%, rgba(255,255,255,1) 100%);
        padding: 1.5rem 1rem 1.5rem 1rem;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }

    .input-container-bottom > div {
        max-width: 1680px;
        margin: 0 auto;
    }

    .stTextInput > div > div > input {
        border-radius: 28px !important;
        border: 2px solid transparent !important;
        background:
            linear-gradient(#ffffff, #ffffff) padding-box,
            linear-gradient(135deg, #ff6b9d20 0%, #ff8e7220 50%, #ffd89b20 100%) border-box !important;
        padding: 1.2rem 1.8rem !important;
        font-size: 1.05rem !important;
        font-weight: 400 !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow:
            0 8px 32px rgba(255, 107, 157, 0.06),
            0 2px 8px rgba(255, 142, 114, 0.04),
            inset 0 2px 4px rgba(255, 255, 255, 0.9),
            inset 0 -1px 2px rgba(255, 107, 157, 0.05) !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        -webkit-appearance: none !important;
        letter-spacing: 0.3px !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #000000 !important;
        opacity: 0.35 !important;
        font-style: italic !important;
        font-weight: 400 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: transparent !important;
        background:
            linear-gradient(#ffffff, #ffffff) padding-box,
            linear-gradient(135deg, #ff6b9d 0%, #ff8e72 50%, #ffd89b 100%) border-box !important;
        box-shadow:
            0 12px 48px rgba(255, 107, 157, 0.12),
            0 4px 16px rgba(255, 142, 114, 0.08),
            0 0 0 6px rgba(255, 107, 157, 0.08),
            inset 0 2px 4px rgba(255, 255, 255, 0.95),
            inset 0 -1px 2px rgba(255, 107, 157, 0.08) !important;
        outline: none !important;
    }

    /* Plus button styling */
    .stButton > button:not([kind="primary"]) {
        background: transparent !important;
        color: #64748b !important;
        font-size: 20px !important;
        border: none !important;
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 !important;
        line-height: 36px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:not([kind="primary"]):hover {
        background: #f1f5f9 !important;
        color: #475569 !important;
    }

    /* Primary button (send button) styling */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg,
            #ff6b9d 0%,
            #ff8e72 25%,
            #ffd89b 50%,
            #ff8e72 75%,
            #ff6b9d 100%) !important;
        background-size: 200% auto !important;
        color: white !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        min-height: 60px !important;
        padding: 0 !important;
        line-height: 60px !important;
        box-shadow:
            0 8px 32px rgba(255, 107, 157, 0.35),
            0 4px 16px rgba(255, 142, 114, 0.25),
            inset 0 2px 4px rgba(255, 255, 255, 0.3),
            inset 0 -2px 4px rgba(194, 24, 91, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        animation: gradient-shift 6s ease infinite !important;
    }

    .stButton > button[kind="primary"]::before,
    .stButton > button[data-testid="baseButton-primary"]::before {
        content: '' !important;
        position: absolute !important;
        top: -3px !important;
        left: -3px !important;
        right: -3px !important;
        bottom: -3px !important;
        background: linear-gradient(135deg, #ff6b9d, #ff8e72, #ffd89b, #ff8e72, #ff6b9d) !important;
        background-size: 200% auto !important;
        border-radius: 50% !important;
        z-index: -1 !important;
        opacity: 0 !important;
        transition: opacity 0.4s !important;
        filter: blur(16px) !important;
        animation: gradient-shift 6s ease infinite !important;
    }

    .stButton > button[kind="primary"]::after,
    .stButton > button[data-testid="baseButton-primary"]::after {
        content: '' !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        width: 0 !important;
        height: 0 !important;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 70%) !important;
        border-radius: 50% !important;
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: scale(1.12) translateY(-3px) rotate(5deg) !important;
        box-shadow:
            0 16px 48px rgba(255, 107, 157, 0.4),
            0 8px 24px rgba(255, 142, 114, 0.3),
            0 0 0 8px rgba(255, 107, 157, 0.1),
            inset 0 2px 4px rgba(255, 255, 255, 0.4),
            inset 0 -2px 4px rgba(194, 24, 91, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover::before,
    .stButton > button[data-testid="baseButton-primary"]:hover::before {
        opacity: 1 !important;
    }

    .stButton > button[kind="primary"]:hover::after,
    .stButton > button[data-testid="baseButton-primary"]:hover::after {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
    }

    /* Simple file uploader - hide all verbose elements */
    .stFileUploader {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stFileUploader > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stFileUploader label {
        display: none !important;
    }

    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        min-height: 50px !important;
        padding: 0.75rem 1rem !important;
        background: #f8fafc !important;
        border: 1px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        margin-top: 0.5rem !important;
    }

    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        font-size: 0.9rem !important;
        color: #64748b !important;
    }

    .stFileUploader section {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    .stFileUploader section > div {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    .stFileUploader small {
        display: none !important;
    }

    .chat-message {
        padding: 2rem 2.5rem;
        margin: 1.5rem 0;
        border-radius: 24px;
        font-size: 1.02rem;
        line-height: 1.8;
        max-width: 100%;
        position: relative;
        backdrop-filter: blur(20px);
        border: 1px solid transparent;
        color: #000000;
    }

    .chat-message::before {
        content: '';
        position: absolute;
        top: -1px;
        left: -1px;
        right: -1px;
        bottom: -1px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(255, 107, 157, 0.1), rgba(255, 142, 114, 0.1), rgba(255, 216, 155, 0.1));
        z-index: -1;
        opacity: 0;
    }

    .chat-message::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        border-radius: 24px 0 0 24px;
    }

    .chat-message:first-of-type {
        margin-top: 0;
    }

    .user-message {
        background:
            linear-gradient(135deg,
                rgba(255, 255, 255, 0.95) 0%,
                rgba(255, 245, 248, 0.9) 100%);
        border: 1px solid rgba(255, 107, 157, 0.12);
        box-shadow:
            0 8px 32px rgba(255, 107, 157, 0.08),
            0 2px 8px rgba(255, 142, 114, 0.06),
            inset 0 2px 0 rgba(255, 255, 255, 0.8),
            inset 0 -1px 0 rgba(255, 107, 157, 0.06);
    }

    .user-message::after {
        background: linear-gradient(180deg, #ff6b9d 0%, #ff8e72 100%);
    }

    .assistant-message {
        background:
            linear-gradient(135deg,
                rgba(255, 255, 255, 0.98) 0%,
                rgba(254, 252, 252, 0.95) 100%);
        border: 1px solid rgba(255, 142, 114, 0.12);
        box-shadow:
            0 8px 32px rgba(255, 142, 114, 0.08),
            0 2px 8px rgba(255, 216, 155, 0.06),
            inset 0 2px 0 rgba(255, 255, 255, 0.9),
            inset 0 -1px 0 rgba(255, 142, 114, 0.06);
    }

    .assistant-message::after {
        background: linear-gradient(180deg, #ff8e72 0%, #ffd89b 100%);
    }

    .chat-message strong {
        color: #000000;
        font-weight: 600;
        letter-spacing: 0.2px;
    }

    /* Log link button styling */
    button[data-testid*="log_btn"] {
        background: transparent !important;
        border: none !important;
        color: #64748b !important;
        font-size: 0.85rem !important;
        text-decoration: underline !important;
        padding: 0.25rem 0.5rem !important;
        cursor: pointer !important;
        transition: color 0.2s ease !important;
        height: auto !important;
        min-height: auto !important;
    }

    button[data-testid*="log_btn"]:hover {
        color: #475569 !important;
        background: transparent !important;
    }

    /* Form styling - remove default borders and padding */
    .stForm {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    /* Hide "Press Enter to submit form" text */
    .stForm [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Form submit button styling (for Enter key support) */
    .stForm button[kind="formSubmit"] {
        background: linear-gradient(135deg,
            #ff6b9d 0%,
            #ff8e72 25%,
            #ffd89b 50%,
            #ff8e72 75%,
            #ff6b9d 100%) !important;
        background-size: 200% auto !important;
        color: white !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        min-height: 60px !important;
        padding: 0 !important;
        line-height: 60px !important;
        display: block !important;
        box-shadow:
            0 8px 32px rgba(255, 107, 157, 0.35),
            0 4px 16px rgba(255, 142, 114, 0.25),
            inset 0 2px 4px rgba(255, 255, 255, 0.3),
            inset 0 -2px 4px rgba(194, 24, 91, 0.2) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        animation: gradient-shift 6s ease infinite !important;
    }

    .stForm button[kind="formSubmit"]:hover {
        transform: scale(1.12) translateY(-3px) rotate(5deg) !important;
        box-shadow:
            0 16px 48px rgba(255, 107, 157, 0.4),
            0 8px 24px rgba(255, 142, 114, 0.3),
            0 0 0 8px rgba(255, 107, 157, 0.1),
            inset 0 2px 4px rgba(255, 255, 255, 0.4),
            inset 0 -2px 4px rgba(194, 24, 91, 0.25) !important;
    }

    /* Spinner animation for processing state */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .stForm button[kind="formSubmit"].processing {
        animation: spin 1s linear infinite !important;
    }

    .capabilities-hint {
        text-align: center;
        margin-top: 2rem;
        padding: 1.5rem 2.5rem;
        background: transparent;
        border: none;
        font-family: 'Playfair Display', serif;
        background: linear-gradient(135deg, #c2185b 0%, #ff6b9d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1rem;
        font-weight: 500;
        font-style: italic;
        letter-spacing: 0.3px;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
        opacity: 1;
    }

    .privacy-disclaimer {
        text-align: center;
        margin-top: 3rem;
        padding: 0.75rem 2rem;
        background: transparent;
        border: none;
        color: #000000;
        font-size: 0.75rem;
        font-weight: 400;
        line-height: 1.7;
        opacity: 0.5;
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)


class MCPClient:
    """MCP Client for connecting to stdio-based MCP servers."""

    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server via stdio."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path]
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

    async def process_query(self, query: str, status_container=None, tool_chain_container=None) -> str:
        """Process a query using Claude and available MCP tools."""

        if status_container:
            status_container.info("🔧 Loading MCP tools...")

        # Get available tools from MCP server
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        if status_container:
            tool_names = [t["name"] for t in available_tools]
            status_container.success(f"✅ Loaded {len(available_tools)} tools: {', '.join(tool_names)}")

        # Load Agent Skills from SKILLS.md
        skills_path = Path(__file__).parent.parent / "SKILLS.md"
        agent_skills = ""
        if skills_path.exists():
            agent_skills = skills_path.read_text()

        # System prompt
        system_prompt = f"""You are DoctHER, an AI-powered women's health assistant specializing in reproductive health and fertility.

You have access to clinical calculator tools from MCP (Model Context Protocol) servers. Use these tools to provide evidence-based guidance.

**Your Role:**

You are an agent to give scientific answers to women's health questions.

Use ESHRE, ASRM, NAMS guidelines first if they are relevant, then look in PubMed or ELSA for relevant papers. Use the IVF calculator or other clinical tools if they are relevant.

**IMPORTANT: You have access to comprehensive research tools:**

**Clinical Guidelines:**
- `list_eshre_guidelines` - List all ESHRE (European Society of Human Reproduction) clinical guidelines
- `search_eshre_guidelines` - Search ESHRE guidelines by keyword (IVF, PCOS, endometriosis, etc.)
- `get_eshre_guideline` - Get full ESHRE guideline content
- `list_nams_position_statements` - List NAMS (Menopause Society) position statements
- `search_nams_protocols` - Search NAMS protocols (hormone therapy, vasomotor symptoms, etc.)
- `get_nams_protocol` - Get full NAMS protocol content

**Research Databases:**
- `search_pubmed` - Search PubMed for scientific articles on any topic
- `get_article` - Retrieve full abstract for a specific PMID
- `get_multiple_articles` - Fetch multiple PubMed articles at once
- `list_elsa_waves` - List ELSA (English Longitudinal Study of Ageing) waves
- `search_elsa_data` - Search ELSA data on aging, menopause, cognitive health, biomarkers

**Clinical Calculators:**
- `predict-ivf-success` - Calculate IVF success rates using real SART data

**How to use these tools:**
1. Start with clinical guidelines (ESHRE for fertility/IVF, NAMS for menopause)
2. Supplement with PubMed research for latest scientific evidence
3. Use ELSA database for population health and aging data
4. Use calculators when patient provides specific clinical data (age, AMH, etc.)

**IMPORTANT: Use tools in parallel whenever possible**
- When multiple searches are needed, make tool calls in parallel for efficiency
- Example: If searching both ESHRE guidelines AND PubMed, call both tools simultaneously
- This significantly speeds up response time and provides comprehensive answers faster

---

## AGENT SKILLS

{agent_skills}

---

Give a summarised result with references to guidelines and papers.

Oftentimes women feel their symptoms/pain is overlooked and dismissed by doctors. We want to make sure that women feel as though they have someone believing them. We want them empowered in their appointments.

- Provide evidence-based fertility and reproductive health guidance
- Use the available tools to search guidelines and scientific evidence
- Be deeply friendly and supportive.
- Help patients understand their options and next steps
- Always clarify that you're an AI assistant and recommend consulting healthcare providers

**Guidelines:**
1. When you receive a question, USE THE TOOLS to search relevant guidelines first
2. Search PubMed for recent scientific evidence to support your guidance
3. Use clinical calculators when patient data is available (age, AMH, etc.)
4. Be compassionate and supportive - validate their concerns
5. Explain medical terms clearly and avoid jargon
6. Always recommend consulting with healthcare providers for medical decisions
7. If age and clinical data indicate time-sensitive concerns, gently emphasize urgency
8. Provide clear next steps with scientific references and guideline citations
9. Ask questions to clarify patient concerns when needed or to get more clinical data to solve their problem if needed

Remember: You're providing educational information, not medical advice. Always cite your sources (ESHRE guidelines, NAMS protocols, PubMed articles, ELSA data)."""

        # Call Claude with tools
        messages = [{"role": "user", "content": query}]
        tool_calls_made = []
        tool_summaries = {}  # Store result summaries for each tool by index

        # Helper function to get tool icon
        def get_tool_icon(tool_name):
            """Get icon for tool based on name."""
            name_lower = tool_name.lower()
            if 'pubmed' in name_lower or 'article' in name_lower:
                return 'P'
            elif 'nams' in name_lower:
                return 'N'
            elif 'eshre' in name_lower:
                return 'E'
            elif 'elsa' in name_lower:
                return 'L'
            elif 'ivf' in name_lower or 'predict' in name_lower:
                return 'C'
            else:
                return '🔧'

        # Agentic loop
        for iteration in range(15):
            # Update status message
            if status_container:
                status_container.info(f"🤖 DoctHER thinking...")

            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=available_tools
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "end_turn":
                # Extract final response
                final_text = ""
                for content in response.content:
                    if hasattr(content, 'text'):
                        final_text += content.text

                if status_container:
                    status_container.success("✅ Response complete!")

                # Return response and tool log separately
                return (final_text, tool_calls_made)

            elif response.stop_reason == "tool_use":
                # Add assistant's response to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute tool calls
                tool_results = []
                for content in response.content:
                    if content.type == 'tool_use':
                        # Track which tool is being used
                        tool_calls_made.append(content.name)

                        # Add to tool chain display (without result details yet)
                        icon = get_tool_icon(content.name)
                        tool_display_name = content.name.replace('_', ' ').replace('-', ' ').title()

                        # Update tool chain container with current tool
                        def update_tool_chain():
                            """Helper to rebuild and update tool chain display."""
                            if tool_chain_container:
                                tools_html = ""
                                for i, tool_name in enumerate(tool_calls_made):
                                    tool_icon = get_tool_icon(tool_name)
                                    tool_label = tool_name.replace('_', ' ').replace('-', ' ').title()
                                    summary = tool_summaries.get(i, "")
                                    tools_html += f'<div style="display: flex; align-items: center; padding: 8px 0;"><div style="width: 32px; height: 32px; border-radius: 6px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #475569; margin-right: 12px; font-size: 14px;">{tool_icon}</div><div style="color: #334155; font-size: 14px;">{tool_label}<span style="color: #64748b; font-size: 12px;">{summary}</span></div></div>'

                                tool_chain_container.markdown(
                                    f'<div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin: 8px 0;"><div style="color: #64748b; font-size: 13px; margin-bottom: 8px;">{len(tool_calls_made)} step{"s" if len(tool_calls_made) > 1 else ""}</div>{tools_html}</div>',
                                    unsafe_allow_html=True
                                )

                        update_tool_chain()

                        # Execute tool via MCP
                        result = await self.session.call_tool(
                            content.name,
                            content.input
                        )

                        # Parse result to extract details for display
                        result_text = result.content[0].text if result.content else ""
                        result_summary = ""

                        # Extract useful info from result
                        if 'search_pubmed' in content.name.lower() or 'article' in content.name.lower():
                            # Try to find result count in response
                            if 'found' in result_text.lower():
                                match = re.search(r'found (\d+)', result_text.lower())
                                if match:
                                    result_summary = f" • Found {match.group(1)} results"
                            elif 'retrieved' in result_text.lower():
                                match = re.search(r'retrieved (\d+)', result_text.lower())
                                if match:
                                    result_summary = f" • Retrieved {match.group(1)} articles"

                        # Store the summary for this tool
                        if result_summary:
                            tool_summaries[len(tool_calls_made) - 1] = result_summary
                            # Update display with result details
                            update_tool_chain()

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content[0].text
                        })

                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                return (f"Unexpected stop reason: {response.stop_reason}", tool_calls_made)

        return ("Maximum iterations reached", tool_calls_made)

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'tool_logs' not in st.session_state:
        st.session_state.tool_logs = []  # Store tool usage logs for each message
    if 'show_upload_menu' not in st.session_state:
        st.session_state.show_upload_menu = False
    if 'form_counter' not in st.session_state:
        st.session_state.form_counter = 0  # Counter to reset form
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'pending_input' not in st.session_state:
        st.session_state.pending_input = ""
    if 'pending_message' not in st.session_state:
        st.session_state.pending_message = ""


def render_landing_page():
    """Render the landing page with logo and tagline."""
    st.markdown("""
        <div class="landing-container">
            <div class="logo">DoctHER</div>
            <div class="tagline">How can I help?</div>
        </div>
    """, unsafe_allow_html=True)


def render_capabilities_hint():
    """Render capabilities hint."""
    st.markdown("""
        <div class="capabilities-hint">
            Some of the things I can do: Search ESHRE & NAMS guidelines, PubMed research, ELSA aging data, and calculate IVF success rates
        </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    """Render the chat history."""
    if st.session_state.messages:
        for idx, message in enumerate(st.session_state.messages):
            message_class = "user-message" if message["role"] == "user" else "assistant-message"
            role_icon = "👤" if message["role"] == "user" else "🩺"
            role_label = "You" if message["role"] == "user" else "DoctHER"

            st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>{role_icon} {role_label}</strong><br>
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)

            # Show tool log as a clickable link (only for assistant messages)
            if message["role"] == "assistant" and idx < len(st.session_state.tool_logs):
                tool_log = st.session_state.tool_logs[idx]
                if tool_log:
                    # Create unique key for this log
                    log_key = f"show_log_{idx}"
                    if log_key not in st.session_state:
                        st.session_state[log_key] = False

                    # Show clickable link
                    col1, col2 = st.columns([0.3, 0.7])
                    with col1:
                        if st.button(
                            f"🔍 View log ({len(tool_log)} tool{'s' if len(tool_log) > 1 else ''} used)",
                            key=f"log_btn_{idx}",
                            help="Click to view tool usage"
                        ):
                            st.session_state[log_key] = not st.session_state[log_key]

                    # Show log details if toggled
                    if st.session_state[log_key]:
                        st.markdown("""
                            <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px;
                                 border-left: 3px solid #94a3b8; margin: 0.5rem 0 1rem 0;">
                                <strong style="color: #64748b; font-size: 0.85rem;">Tool Usage Log:</strong>
                            </div>
                        """, unsafe_allow_html=True)
                        for i, tool_name in enumerate(tool_log, 1):
                            st.markdown(f"<div style='padding: 0.25rem 0 0.25rem 1rem; color: #475569; font-size: 0.9rem;'><strong>{i}.</strong> {tool_name}</div>", unsafe_allow_html=True)



async def handle_user_input_async(user_input: str, status_container, tool_chain_container):
    """Process user input asynchronously."""

    if not ANTHROPIC_API_KEY:
        return """⚠️ **Anthropic API key not configured**

To enable AI-powered consultations, please:
1. Add your ANTHROPIC_API_KEY to the `.env` file
2. Restart the application"""

    # Create a new MCP client for each request to avoid event loop issues
    client = MCPClient()

    try:
        # Connect to MCP server
        status_container.info("🔄 Connecting to MCP server...")
        await client.connect_to_server(MCP_SERVER_SCRIPT)
        status_container.success("✅ Connected to MCP server")

        # Process query - returns (response, tool_log)
        result = await client.process_query(user_input, status_container, tool_chain_container)

        # Unpack result
        if isinstance(result, tuple):
            response, tool_log = result
        else:
            response = result
            tool_log = []

        # Clean up
        await client.cleanup()

        return (response, tool_log)

    except Exception as e:
        try:
            await client.cleanup()
        except:
            pass
        return (f"❌ Error: {str(e)}", [])


def handle_user_input(user_input: str):
    """Handle user input."""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Add empty tool log for user message
    st.session_state.tool_logs.append([])

    # Create containers for status and tool chain
    tool_chain_container = st.empty()
    status_container = st.empty()

    # Process with MCP - returns (response, tool_log)
    result = asyncio.run(handle_user_input_async(user_input, status_container, tool_chain_container))

    if isinstance(result, tuple):
        assistant_response, tool_log = result
    else:
        assistant_response = result
        tool_log = []

    # Clear status and tool chain containers
    status_container.empty()
    tool_chain_container.empty()

    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    # Store tool log for this response
    st.session_state.tool_logs.append(tool_log)

    st.session_state.show_chat = True


def main():
    """Main application."""
    initialize_session_state()

    # Initialize variables
    uploaded_file = None
    user_input = ""
    send_clicked = False

    # Check if this is the first interaction
    is_first_interaction = len(st.session_state.messages) == 0

    if is_first_interaction:
        # Show centered landing page for first interaction
        render_landing_page()

        # Centered input container
        st.markdown('<div class="input-container centered">', unsafe_allow_html=True)

        # Plus button outside form
        col_plus, col_rest = st.columns([0.07, 0.93])

        with col_plus:
            plus_clicked = st.button("➕", key="plus_button", help="Add attachments")
            if plus_clicked:
                st.session_state.show_upload_menu = not st.session_state.show_upload_menu
                st.rerun()

        with col_rest:
            # Form for input and send button (enables Enter key submission)
            with st.form(key=f"input_form_{st.session_state.form_counter}", clear_on_submit=False):
                col_input, col_send = st.columns([0.92, 0.08])

                with col_input:
                    # Use pending_input if processing, otherwise empty
                    default_value = st.session_state.pending_input if st.session_state.is_processing else ""
                    user_input = st.text_input(
                        "message",
                        value=default_value,
                        placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                        key=f"user_input_{st.session_state.form_counter}",
                        label_visibility="collapsed",
                        disabled=st.session_state.is_processing
                    )

                with col_send:
                    button_text = "⟳" if st.session_state.is_processing else "↑"
                    send_clicked = st.form_submit_button(button_text, type="primary", disabled=st.session_state.is_processing)

        # Show compact file uploader if toggled
        if st.session_state.show_upload_menu:
            uploaded_file = st.file_uploader(
                "Upload a file",
                type=["png", "jpg", "jpeg", "pdf", "txt"],
                key="file_upload",
                label_visibility="collapsed"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # Capabilities hint
        render_capabilities_hint()

        # Privacy disclaimer
        st.markdown("""
            <div class="privacy-disclaimer">
                None of the text or data used in the prompts is saved or used to train any models. All data is in your browser and deleted as soon as you refresh or move away from the page.
            </div>
        """, unsafe_allow_html=True)

    else:
        # Show title at top of chat
        st.markdown("""
            <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
                <div class="logo" style="font-size: 2rem; margin-bottom: 0.25rem;">DoctHER</div>
            </div>
        """, unsafe_allow_html=True)

        # Show chat history in scrollable container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        render_chat_history()
        st.markdown('</div>', unsafe_allow_html=True)

        # Fixed bottom input
        st.markdown('<div class="input-container-bottom">', unsafe_allow_html=True)

        # Plus button outside form
        col_plus, col_rest = st.columns([0.07, 0.93])

        with col_plus:
            plus_clicked = st.button("➕", key="plus_button_chat", help="Add attachments")
            if plus_clicked:
                st.session_state.show_upload_menu = not st.session_state.show_upload_menu
                st.rerun()

        with col_rest:
            # Form for input and send button (enables Enter key submission)
            with st.form(key=f"input_form_chat_{st.session_state.form_counter}", clear_on_submit=False):
                col_input, col_send = st.columns([0.92, 0.08])

                with col_input:
                    # Use pending_input if processing, otherwise empty
                    default_value = st.session_state.pending_input if st.session_state.is_processing else ""
                    user_input = st.text_input(
                        "message",
                        value=default_value,
                        placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                        key=f"user_input_chat_{st.session_state.form_counter}",
                        label_visibility="collapsed",
                        disabled=st.session_state.is_processing
                    )

                with col_send:
                    button_text = "⟳" if st.session_state.is_processing else "↑"
                    send_clicked = st.form_submit_button(button_text, type="primary", disabled=st.session_state.is_processing)

        # Show compact file uploader if toggled (for chat mode)
        if st.session_state.show_upload_menu:
            uploaded_file = st.file_uploader(
                "Upload a file",
                type=["png", "jpg", "jpeg", "pdf", "txt"],
                key="file_upload_chat",
                label_visibility="collapsed"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # Display uploaded file info if present
    if uploaded_file is not None:
        st.markdown(
            f'<div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">'
            f'📎 Attached: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)'
            f'</div>',
            unsafe_allow_html=True
        )

    # Handle send button click
    if send_clicked and user_input and user_input.strip() and not st.session_state.is_processing:
        # Include file info in the message if there's an attachment
        message_content = user_input
        if uploaded_file is not None:
            message_content += f"\n\n[Attachment: {uploaded_file.name}]"

        # Store the input and set processing state
        st.session_state.pending_input = user_input
        st.session_state.pending_message = message_content
        st.session_state.is_processing = True

        # Reset upload menu state
        st.session_state.show_upload_menu = False

        # Rerun to show processing state
        st.rerun()

    # Process the pending input if we're in processing state
    if st.session_state.is_processing and st.session_state.pending_message:
        message_to_process = st.session_state.pending_message
        st.session_state.pending_message = ""  # Clear it immediately

        # Process the input
        handle_user_input(message_to_process)

        # Clear processing state and input after completion
        st.session_state.is_processing = False
        st.session_state.pending_input = ""

        # Increment form counter to reset form with new key
        st.session_state.form_counter += 1

        st.rerun()


if __name__ == "__main__":
    main()
