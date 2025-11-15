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
import warnings
import numpy as np
from pathlib import Path
from contextlib import AsyncExitStack
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Suppress numpy warnings from faster_whisper before any imports
warnings.filterwarnings('ignore', category=RuntimeWarning, module='faster_whisper')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*divide by zero.*')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*overflow.*')
warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*invalid value.*')

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import database and auth modules
from database import init_db, get_session_maker, crud
from auth import Authenticator
from components import (
    show_login_signup_page,
    show_sidebar,
    init_chat_session,
    show_symptom_recording_form,
    show_symptom_dashboard,
    show_symptom_recorder,
)

# Page configuration
st.set_page_config(
    page_title="DoctHER - Your AI Women's Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"  # Enable sidebar for navigation
)

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./womens_health_mcp.db")

# Lazy database initialization - only connects when needed
@st.cache_resource
def get_database_engine():
    """Initialize database engine (cached, runs once per app instance)."""
    return init_db(DATABASE_URL)

@st.cache_resource
def get_database_session_maker():
    """Get database session maker (cached, runs once per app instance)."""
    engine = get_database_engine()
    return get_session_maker(engine)

def get_db_session():
    """Get or create database session for current user (lazy initialization)."""
    if 'db_session' not in st.session_state:
        SessionLocal = get_database_session_maker()
        st.session_state.db_session = SessionLocal()
    return st.session_state.db_session

# MCP Server Paths - New Multi-Server Architecture
MCP_SERVERS = {
    "database": str(Path(__file__).parent.parent / "mcp_servers" / "database_server.py"),
    "api": str(Path(__file__).parent.parent / "mcp_servers" / "api_server.py"),
    "calculator": str(Path(__file__).parent.parent / "mcp_servers" / "calculator_server.py")
}

# Fallback to legacy router if new servers don't exist
LEGACY_MCP_SERVER = str(Path(__file__).parent.parent / "scripts" / "mcp_stdio_server.py")

# Custom CSS
css = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput > label {display: none !important;}

    /* Design System Colors */
    :root {
        --deep-teal: #0a4d4e;
        --warm-terracotta: #c85a3e;
        --neutral-ink: #1a1a1a;
        --soft-sage: #8ba888;
        --warm-sand: #e8ddd3;
        --clinical-blue: #4a7c8e;
        --research-red: #c14953;
        --analysis-amber: #d4a24c;
        --evidence-green: #6b8e7f;
        --canvas: #fdfcfb;
        --surface: #f5f3f0;
        --border-color: #d4cec6;
        --text-secondary: #5a5550;
    }

    /* Global Styles */
    html, body, .stApp {
        background: var(--canvas) !important;
        color: var(--neutral-ink) !important;
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .main {
        background: var(--canvas) !important;
        padding: 0 !important;
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
    }

    /* Landing Page Styles */
    .landing-container {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 15vh;
        padding-bottom: 4rem;
        text-align: center;
    }

    .logo {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 48px;
        font-weight: 600;
        color: var(--deep-teal);
        margin-bottom: 1rem;
        line-height: 56px;
    }

    .tagline {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 24px;
        font-weight: 500;
        color: var(--text-secondary);
        margin-bottom: 3rem;
        line-height: 32px;
    }

    /* Chat Messages */
    .chat-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px 140px 24px;
        min-height: 300px;
        overflow-y: visible;
    }

    .chat-message {
        padding: 24px;
        margin: 16px 0;
        border-radius: 12px;
        font-size: 16px;
        line-height: 24px;
        max-width: 100%;
        position: relative;
        background: var(--surface);
        border: 1px solid var(--border-color);
        color: var(--neutral-ink);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .user-message {
        background: white !important;
        border-left: 4px solid var(--deep-teal) !important;
    }

    .assistant-message {
        background: var(--surface) !important;
        border-left: 4px solid var(--warm-terracotta) !important;
    }

    .chat-message strong {
        color: var(--neutral-ink);
        font-weight: 600;
    }

    /* Input Styling */
    .input-container.centered {
        max-width: 700px;
        margin: 0 auto 2rem auto;
    }

    .input-container-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--canvas);
        padding: 24px;
        z-index: 1000;
        border-top: 1px solid var(--border-color);
    }

    .input-container-bottom > div {
        max-width: 1200px;
        margin: 0 auto;
    }

    .stTextInput > div > div > input {
        border-radius: 6px !important;
        border: 1.5px solid var(--border-color) !important;
        background: white !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--neutral-ink) !important;
        height: 52px !important;
        transition: all 0.15s ease !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary) !important;
        opacity: 0.7 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--deep-teal) !important;
        box-shadow: 0 0 0 3px rgba(10, 77, 78, 0.1) !important;
        outline: none !important;
    }

    /* Button Styling - Minimal outlined design */
    .stButton > button {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        transition: all 0.2s ease !important;
        height: 52px !important;
    }

    .stButton > button:hover {
        background: rgba(10, 77, 78, 0.08) !important;
        color: var(--deep-teal) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
        background: rgba(10, 77, 78, 0.12) !important;
    }

    /* Primary send button - outlined style */
    .stButton > button[kind="primary"],
    .stForm button[kind="formSubmit"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        width: 52px !important;
        height: 52px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 20px !important;
        line-height: 52px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stForm button[kind="formSubmit"]:hover {
        background: rgba(10, 77, 78, 0.1) !important;
        color: var(--deep-teal) !important;
        transform: scale(1.05) !important;
    }

    /* Plus button and other icon buttons - outlined style */
    .stButton > button:not([kind="primary"]):not([data-testid*="log_btn"]) {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        width: 52px !important;
        height: 52px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 20px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:not([kind="primary"]):not([data-testid*="log_btn"]):hover {
        background: rgba(10, 77, 78, 0.1) !important;
        color: var(--deep-teal) !important;
        transform: scale(1.05) !important;
    }

    /* Minimal Icon Styling */
    /* Using clean SVG icons with minimal design */

    /* Style for inline SVG icons */
    .icon-btn-svg {
        width: 20px;
        height: 20px;
        stroke: currentColor;
        fill: none;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    /* File uploader */
    .stFileUploader {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 8px !important;
    }

    .stFileUploader > div {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        min-height: 60px !important;
        padding: 16px !important;
        background: var(--surface) !important;
        border: 1px dashed var(--border-color) !important;
        border-radius: 6px !important;
        margin-top: 8px !important;
    }

    .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] {
        font-size: 14px !important;
        color: var(--text-secondary) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* Tool log button styling */
    button[data-testid*="log_btn"] {
        background: transparent !important;
        border: none !important;
        color: var(--text-secondary) !important;
        font-size: 13px !important;
        text-decoration: underline !important;
        padding: 4px 8px !important;
        cursor: pointer !important;
        transition: color 0.15s ease !important;
        height: auto !important;
        min-height: auto !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    button[data-testid*="log_btn"]:hover {
        color: var(--deep-teal) !important;
        background: transparent !important;
    }

    /* Form styling */
    .stForm {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    .stForm [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Capabilities hint */
    .capabilities-hint {
        text-align: center;
        margin-top: 2rem;
        padding: 24px;
        background: transparent;
        border: none;
        font-family: 'IBM Plex Sans', serif;
        color: var(--text-secondary);
        font-size: 16px;
        font-weight: 400;
        line-height: 24px;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
        opacity: 0.8;
    }

    .privacy-disclaimer {
        text-align: center;
        margin-top: 3rem;
        padding: 16px;
        background: transparent;
        border: none;
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 400;
        line-height: 20px;
        opacity: 0.6;
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Trust indicators styling */
    .trust-indicators {
        background: var(--surface);
        border-top: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        padding: 32px 24px;
        text-align: center;
        margin: 48px -24px;
    }

    .trust-stat {
        color: var(--deep-teal);
        font-size: 24px;
        font-weight: 600;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .trust-label {
        color: var(--text-secondary);
        font-size: 12px;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* Sidebar styling for icon-only mode */
    [data-testid="stSidebar"] {
        min-width: 60px !important;
        max-width: 120px !important;
        width: 70px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 0.75rem 0.25rem !important;
    }

    /* Icon buttons in sidebar - minimal outlined design */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: none !important;
        padding: 8px !important;
        font-size: 20px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        min-height: 40px !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(10, 77, 78, 0.1) !important;
        color: var(--deep-teal) !important;
        transform: scale(1.08) !important;
    }

    [data-testid="stSidebar"] .stButton > button:active {
        background: rgba(10, 77, 78, 0.15) !important;
        transform: scale(1.0) !important;
    }

    /* Disabled sidebar buttons */
    [data-testid="stSidebar"] .stButton > button:disabled {
        background: rgba(10, 77, 78, 0.15) !important;
        color: var(--deep-teal) !important;
        opacity: 0.7 !important;
    }

    /* Compact spacing for sidebar */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 0.25rem !important;
    }


    /* Export button icon */
    button:has(.stDownloadButton):not([kind="primary"]) {
        font-size: 0 !important;
    }

    /* Symptom form Save button - checkmark icon */
    button[kind="primary"]:not(.stForm button) {
        position: relative;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 16px !important;
            padding-right: 16px !important;
        }

        .logo {
            font-size: 32px;
            line-height: 40px;
        }

        .tagline {
            font-size: 18px;
            line-height: 28px;
        }

        .chat-container {
            padding: 0 16px 120px 16px;
        }

        .chat-message {
            padding: 16px;
        }

        .input-container-bottom {
            padding: 16px;
        }

        [data-testid="stSidebar"] {
            min-width: 60px !important;
        }
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)


class MultiServerMCPClient:
    """MCP Client for connecting to multiple FastMCP servers."""

    def __init__(self):
        self.sessions = {}  # server_name -> ClientSession
        self.tool_registry = {}  # tool_name -> server_name
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.use_legacy = False

    async def connect_to_servers(self, server_paths: dict, status_container=None):
        """Connect to multiple MCP servers."""

        # Check if new servers exist, otherwise fallback to legacy
        servers_exist = all(Path(path).exists() for path in server_paths.values())

        if not servers_exist:
            if status_container:
                status_container.warning("⚠️ New multi-server architecture not found, using legacy server")
            self.use_legacy = True
            await self.connect_to_legacy_server()
            return

        if status_container:
            status_container.info("🔄 Connecting to multi-server architecture...")

        # Connect to each server
        for server_name, server_path in server_paths.items():
            try:
                if status_container:
                    status_container.info(f"🔄 Connecting to {server_name} server...")

                server_params = StdioServerParameters(
                    command="fastmcp",
                    args=["run", server_path, "--transport", "stdio", "--no-banner"]
                )

                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                stdio, write = stdio_transport
                session = await self.exit_stack.enter_async_context(
                    ClientSession(stdio, write)
                )

                await session.initialize()
                self.sessions[server_name] = session

                if status_container:
                    status_container.success(f"✅ Connected to {server_name} server")

            except Exception as e:
                if status_container:
                    status_container.error(f"❌ Failed to connect to {server_name} server: {str(e)}")
                # Fall back to legacy if any server fails
                if not self.use_legacy:
                    self.use_legacy = True
                    await self.connect_to_legacy_server()
                    return

        # Build tool registry
        await self._discover_tools(status_container)

    async def connect_to_legacy_server(self):
        """Fallback to legacy single-server architecture."""
        if not Path(LEGACY_MCP_SERVER).exists():
            raise FileNotFoundError("Neither new multi-server nor legacy server found")

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[LEGACY_MCP_SERVER]
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        self.sessions["legacy"] = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        await self.sessions["legacy"].initialize()

    async def _discover_tools(self, status_container=None):
        """Build registry of which tool belongs to which server."""
        total_tools = 0

        for server_name, session in self.sessions.items():
            tools = await session.list_tools()
            server_tool_count = len(tools.tools)
            total_tools += server_tool_count

            for tool in tools.tools:
                self.tool_registry[tool.name] = server_name

            if status_container:
                tool_names = [tool.name for tool in tools.tools]
                status_container.info(f"📋 {server_name}: {server_tool_count} tools ({', '.join(tool_names[:3])}{'...' if len(tool_names) > 3 else ''})")

        if status_container:
            status_container.success(f"✅ Total: {total_tools} tools discovered across {len(self.sessions)} server(s)")

    async def call_tool(self, tool_name: str, arguments: dict):
        """Route tool call to appropriate server."""
        if self.use_legacy:
            session = self.sessions["legacy"]
        else:
            server_name = self.tool_registry.get(tool_name)
            if not server_name:
                raise ValueError(f"Unknown tool: {tool_name}")
            session = self.sessions[server_name]

        return await session.call_tool(tool_name, arguments)

    async def get_all_tools_for_claude(self):
        """Aggregate tools from all servers for Claude API."""
        all_tools = []
        for session in self.sessions.values():
            tools = await session.list_tools()
            all_tools.extend([{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools.tools])
        return all_tools

    async def process_query(self, query: str, status_container=None, tool_chain_container=None) -> str:
        """Process a query using Claude and available MCP tools."""

        if status_container:
            status_container.info("🔧 Loading MCP tools...")

        # Get available tools from all MCP servers (or legacy)
        if self.use_legacy and "legacy" in self.sessions:
            response = await self.sessions["legacy"].list_tools()
            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
        else:
            # Use multi-server approach
            available_tools = await self.get_all_tools_for_claude()

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

You have access to clinical research and calculator tools via MCP (Model Context Protocol) servers. Use these tools to provide evidence-based guidance.

**Your Role:**
You are an agent to give scientific answers to women's health questions.

**Your Approach:**
1. Use clinical guidelines first (ESHRE for fertility/IVF, ASRM for reproductive medicine, NAMS for menopause)
2. Search PubMed for latest scientific evidence to supplement guidelines
3. Use ELSA database for population health and aging data when relevant
4. Use clinical calculators when patients provide specific data (age, AMH, etc.)

**Available Tool Categories:**
- **Clinical Guidelines**: ESHRE, ASRM, NAMS position statements and protocols
- **Research Database**: PubMed search and article retrieval
- **Population Data**: ELSA (English Longitudinal Study of Ageing) datasets
- **Clinical Calculators**: SART IVF success predictions and recommendations

**IMPORTANT: Use tools efficiently**
- Make multiple tool calls in parallel when searching different sources
- Always check tool parameters carefully before calling
- Use the exact tool names and parameters as provided in the tool schemas

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
                return 'T'  # T for Tool

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
                        result = await self.call_tool(
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
    # Authentication state
    Authenticator.init_session_state()

    # Database session - NOT initialized here, only when needed
    # Call get_db_session() when you need database access

    # Chat state
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

    # Chat session tracking
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None

    # Symptom tracker state
    if 'show_symptom_tracker' not in st.session_state:
        st.session_state.show_symptom_tracker = False
    if 'show_symptom_form' not in st.session_state:
        st.session_state.show_symptom_form = False
    if 'show_chat_window' not in st.session_state:
        st.session_state.show_chat_window = False
    if 'current_input_text' not in st.session_state:
        st.session_state.current_input_text = ""
    if 'symptom_extraction_cache' not in st.session_state:
        st.session_state.symptom_extraction_cache = None
    if 'symptom_text_to_record' not in st.session_state:
        st.session_state.symptom_text_to_record = None


def render_landing_page():
    """Render the landing page with logo and tagline."""
    st.markdown("""
        <div class="landing-container">
            <div class="logo">DoctHER</div>
            <div class="tagline">Research-Grade AI for Women's Health Topics</div>
        </div>
    """, unsafe_allow_html=True)


def render_capabilities_hint():
    """Render capabilities hint."""
    st.markdown("""
        <div class="capabilities-hint">
            Access 35M+ peer-reviewed articles, clinical calculators, and evidence-based
            guidelines from ESHRE, ASRM, NAMS, and ELSA.
        </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    """Render the chat history."""
    if st.session_state.messages:
        for idx, message in enumerate(st.session_state.messages):
            message_class = "user-message" if message["role"] == "user" else "assistant-message"
            role_label = "You" if message["role"] == "user" else "DoctHER"

            # Use st.badge for role indicators with Material Symbols
            if message["role"] == "user":
                st.badge(role_label, icon=":material/person:")
            else:
                st.badge(role_label, icon=":material/medical_services:")

            st.markdown(f"""
                <div class="chat-message {message_class}" style="margin-top: -8px;">
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
                            f"View log ({len(tool_log)} tool{'s' if len(tool_log) > 1 else ''} used)",
                            icon=":material/search:",
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

    # Show AI thinking placeholder if processing
    if st.session_state.is_processing:
        st.badge("DoctHER", icon=":material/medical_services:")
        st.markdown("""
            <div class="chat-message assistant-message" style="opacity: 0.7; margin-top: -8px;">
                <em>Thinking...</em>
            </div>
        """, unsafe_allow_html=True)



async def handle_user_input_async(user_input: str, status_container, tool_chain_container):
    """Process user input asynchronously."""

    if not ANTHROPIC_API_KEY:
        return """⚠️ **Anthropic API key not configured**

To enable AI-powered consultations, please:
1. Add your ANTHROPIC_API_KEY to the `.env` file
2. Restart the application"""

    # Create a new MCP client for each request to avoid event loop issues
    client = MultiServerMCPClient()

    try:
        # Connect to MCP servers
        status_container.info("🔄 Connecting to MCP servers...")
        await client.connect_to_servers(MCP_SERVERS, status_container)
        if not client.use_legacy:
            status_container.success("✅ Connected to multi-server architecture")
        else:
            status_container.success("✅ Connected to legacy server")

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


def add_user_message(user_input: str):
    """Add user message immediately to UI and database."""
    # Get database session
    db = get_db_session()

    # Ensure we have a chat session
    session_id = st.session_state.get('current_session_id')
    if not session_id:
        user_id = st.session_state.get('user_id')
        if user_id:
            chat_session = crud.create_chat_session(db, user_id, title="New Chat")
            st.session_state.current_session_id = chat_session.id
            session_id = chat_session.id

    # Add user message to chat immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Save user message to database
    if session_id:
        crud.create_message(db, session_id, "user", user_input)

    # Add empty tool log for user message
    st.session_state.tool_logs.append([])

    # Set chat mode
    st.session_state.show_chat = True


def generate_chat_title(user_message: str) -> str:
    """
    Generate a concise chat title using LLM based on the first user message.

    Args:
        user_message: The first message from the user

    Returns:
        A concise title (3-6 words)
    """
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""Generate a very concise title (3-6 words maximum) for a chat conversation that starts with this user message:

"{user_message}"

The title should:
- Be 3-6 words maximum
- Capture the main topic or question
- Be clear and descriptive
- Use title case

Return ONLY the title, nothing else."""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )

        title = response.content[0].text.strip()
        # Limit to 60 chars just in case
        return title[:60] if len(title) > 60 else title
    except Exception as e:
        # Fallback to truncated message if LLM fails
        return user_message[:47] + "..." if len(user_message) > 50 else user_message


def process_assistant_response(user_input: str):
    """Process AI response after user message is displayed."""
    # Get database session
    db = get_db_session()
    session_id = st.session_state.get('current_session_id')

    # Use session state containers if they exist, otherwise create new ones
    if hasattr(st.session_state, 'tool_chain_container') and hasattr(st.session_state, 'status_container'):
        tool_chain_container = st.session_state.tool_chain_container
        status_container = st.session_state.status_container
    else:
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

    # Clean up session state containers
    if hasattr(st.session_state, 'tool_chain_container'):
        del st.session_state.tool_chain_container
    if hasattr(st.session_state, 'status_container'):
        del st.session_state.status_container

    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    # Save assistant message to database
    if session_id:
        assistant_message = crud.create_message(db, session_id, "assistant", assistant_response)

        # Save tool logs for this message
        if tool_log:
            for tool_name in tool_log:
                crud.create_tool_log(db, assistant_message.id, tool_name)

        # Generate chat title using LLM on first message
        chat_session = crud.get_chat_session(db, session_id)
        if chat_session and chat_session.title in ["New Chat", "First Chat", "Untitled"]:
            # Generate title using LLM
            title = generate_chat_title(user_input)
            crud.update_chat_session_title(db, session_id, title)

    # Store tool log for this response
    st.session_state.tool_logs.append(tool_log)


def main():
    """Main application."""
    initialize_session_state()

    # Check authentication
    if not Authenticator.is_authenticated():
        # Show login/signup page - lazy load DB only when needed
        show_login_signup_page(get_db_session())
        return

    # User is authenticated - initialize chat session if needed
    init_chat_session(get_db_session())

    # Show sidebar with chat history and navigation
    show_sidebar(get_db_session())

    # Check if user wants to view chat selection window
    if st.session_state.get('show_chat_window', False):
        from components.sidebar import show_chat_selection_window
        show_chat_selection_window(get_db_session())

    # Check if user wants to view symptom tracker
    if st.session_state.get('show_symptom_tracker', False):
        show_symptom_dashboard(get_db_session())
        return

    # Check if user wants to record a symptom
    if st.session_state.get('show_symptom_form', False):
        show_symptom_recording_form(get_db_session(), Anthropic(api_key=ANTHROPIC_API_KEY))
        return

    # Check if user wants to use symptom recorder (this is now the main page by default)
    if not st.session_state.get('show_symptom_tracker', False) and not st.session_state.get('show_symptom_form', False) and not st.session_state.get('show_chat_window', False) and len(st.session_state.messages) == 0:
        show_symptom_recorder(get_db_session(), Anthropic(api_key=ANTHROPIC_API_KEY))
        return

    # Initialize variables
    uploaded_file = None
    user_input = ""
    send_clicked = False
    attach_clicked = False
    record_clicked = False

    # Check if we should show chat mode (any messages exist OR currently processing)
    show_chat_mode = len(st.session_state.messages) > 0 or st.session_state.is_processing

    if not show_chat_mode:
        # Show centered landing page for first interaction
        render_landing_page()

        # Centered input container
        st.markdown('<div class="input-container centered">', unsafe_allow_html=True)

        # Form with text input and buttons below
        with st.form(key=f"input_form_{st.session_state.form_counter}", clear_on_submit=False):
            # Full-width text input
            default_value = st.session_state.pending_input if st.session_state.is_processing else ""
            user_input = st.text_input(
                "message",
                value=default_value,
                placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                key=f"user_input_{st.session_state.form_counter}",
                label_visibility="collapsed",
                disabled=st.session_state.is_processing
            )

            # Three buttons in a row below the input - much narrower than input box
            # Layout: [attach left] [large space] [record] [send right]
            col1, col2, col3, col4 = st.columns([1, 6, 1, 1])

            with col1:
                attach_clicked = st.form_submit_button("", icon=":material/attach_file:", help="Add attachments", disabled=st.session_state.is_processing, use_container_width=True)

            # col2 is empty space

            with col3:
                record_clicked = st.form_submit_button("", icon=":material/medical_services:", help="Record Symptom", disabled=st.session_state.is_processing, use_container_width=True)

            with col4:
                button_icon = ":material/refresh:" if st.session_state.is_processing else ":material/send:"
                send_clicked = st.form_submit_button("", icon=button_icon, type="primary", disabled=st.session_state.is_processing, use_container_width=True)

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
        # Show compact title at top of chat
        st.markdown("""
            <div style="text-align: center; padding: 0.25rem 0 0.5rem 0;">
                <div class="logo" style="font-size: 1.5rem; margin-bottom: 0;">DoctHER</div>
            </div>
        """, unsafe_allow_html=True)

        # Show chat history in scrollable container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        render_chat_history()

        # Show processing status if currently processing
        if st.session_state.is_processing:
            st.session_state.tool_chain_container = st.empty()
            st.session_state.status_container = st.empty()

        st.markdown('</div>', unsafe_allow_html=True)

        # Fixed bottom input
        st.markdown('<div class="input-container-bottom">', unsafe_allow_html=True)

        # Form with text input and buttons below
        with st.form(key=f"input_form_chat_{st.session_state.form_counter}", clear_on_submit=False):
            # Full-width text input
            default_value = st.session_state.pending_input if st.session_state.is_processing else ""
            user_input = st.text_input(
                "message",
                value=default_value,
                placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                key=f"user_input_chat_{st.session_state.form_counter}",
                label_visibility="collapsed",
                disabled=st.session_state.is_processing
            )

            # Three buttons in a row below the input - much narrower than input box
            # Layout: [attach left] [large space] [record] [send right]
            col1, col2, col3, col4 = st.columns([1, 6, 1, 1])

            with col1:
                attach_clicked = st.form_submit_button("", icon=":material/attach_file:", help="Add attachments", disabled=st.session_state.is_processing, use_container_width=True)

            # col2 is empty space

            with col3:
                record_clicked = st.form_submit_button("", icon=":material/medical_services:", help="Record Symptom", disabled=st.session_state.is_processing, use_container_width=True)

            with col4:
                button_icon = ":material/refresh:" if st.session_state.is_processing else ":material/send:"
                send_clicked = st.form_submit_button("", icon=button_icon, type="primary", disabled=st.session_state.is_processing, use_container_width=True)

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

    # Handle attach button click
    if attach_clicked:
        st.session_state.show_upload_menu = not st.session_state.show_upload_menu
        st.rerun()

    # Handle record symptom button click
    if record_clicked:
        if user_input and user_input.strip():
            st.session_state.symptom_text_to_record = user_input
            st.session_state.show_symptom_form = True
            st.session_state.show_chat_window = False
            st.rerun()
        else:
            st.warning("Please enter symptom description in the text box first")

    # Handle send button click
    if send_clicked and user_input and user_input.strip() and not st.session_state.is_processing:
        # Include file info in the message if there's an attachment
        message_content = user_input
        if uploaded_file is not None:
            message_content += f"\n\n[Attachment: {uploaded_file.name}]"

        # Store the input for processing
        st.session_state.pending_message = message_content

        # Add user message immediately (shows in UI right away)
        add_user_message(message_content)

        # Set processing state
        st.session_state.is_processing = True
        st.session_state.pending_input = ""

        # Reset upload menu state
        st.session_state.show_upload_menu = False

        # Rerun to show user message and processing state
        st.rerun()

    # Process the assistant response if we're in processing state
    if st.session_state.is_processing and st.session_state.pending_message:
        message_to_process = st.session_state.pending_message
        st.session_state.pending_message = ""  # Clear it immediately

        # Process the AI response
        process_assistant_response(message_to_process)

        # Clear processing state
        st.session_state.is_processing = False

        # Increment form counter to reset form with new key
        st.session_state.form_counter += 1

        st.rerun()


if __name__ == "__main__":
    main()
