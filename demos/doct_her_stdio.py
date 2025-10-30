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

# MCP Server Paths - FastMCP unified servers
MCP_SERVERS = {
    "api": str(Path(__file__).parent.parent / "mcp_servers" / "api_server.py"),
    "database": str(Path(__file__).parent.parent / "mcp_servers" / "database_server.py"),
    "calculator": str(Path(__file__).parent.parent / "mcp_servers" / "calculator_server.py")
}

# Sophisticated Medical Journal Aesthetic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Fira+Code:wght@300;400;500;600&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

    /* Root Variables - Medical Journal Palette */
    :root {
        --primary-forest: #1B3B36;
        --secondary-sage: #4A6741;
        --accent-amber: #D4AF37;
        --accent-copper: #B87333;
        --text-charcoal: #2C2C2C;
        --text-sage: #5A6B57;
        --bg-parchment: #FAF7F2;
        --bg-cream: #F7F4EF;
        --bg-ivory: #FEFCF8;
        --border-sepia: #E5D5B7;
        --shadow-warm: rgba(180, 115, 51, 0.15);
        --shadow-cool: rgba(27, 59, 54, 0.12);
    }

    /* Force consistent theming */
    html, body, .stApp {
        color-scheme: light only !important;
        background: var(--bg-parchment) !important;
        font-family: 'Crimson Text', Georgia, serif;
    }

    /* Hide Streamlit defaults */
    #MainMenu, footer, header { visibility: hidden; }
    .stTextInput > label { display: none !important; }

    /* Atmospheric Background Layers */
    .main {
        background:
            /* Paper texture overlay */
            url("data:image/svg+xml,%3Csvg width='200' height='200' viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3CfeComponentTransfer%3E%3CfeFuncA type='discrete' tableValues='0 0.01 0.02 0.01 0'/%3E%3C/feComponentTransfer%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E"),
            /* Gradient foundation */
            linear-gradient(135deg, var(--bg-ivory) 0%, var(--bg-parchment) 30%, var(--bg-cream) 70%, var(--bg-parchment) 100%);
        position: relative;
        padding: 0;
    }

    /* Landing Page Styling */
    .landing-container {
        max-width: 820px;
        margin: 0 auto;
        padding-top: 8vh;
        padding-bottom: 2rem;
        text-align: center;
    }

    /* Logo - Sophisticated Medical Typography */
    .logo {
        font-family: 'Cormorant Garamond', 'Crimson Text', Georgia, serif;
        font-size: 4.5rem;
        font-weight: 600;
        color: var(--primary-forest);
        margin-bottom: 1.8rem;
        letter-spacing: -0.5px;
        position: relative;
        display: inline-block;
        text-shadow:
            0 2px 4px rgba(27, 59, 54, 0.1),
            0 8px 16px rgba(27, 59, 54, 0.06);
    }

    /* Tagline - Editorial styling */
    .tagline {
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 1.4rem;
        font-style: italic;
        color: var(--text-sage);
        margin-bottom: 1.5rem;
        font-weight: 400;
        letter-spacing: 0.3px;
        line-height: 1.6;
        opacity: 0.9;
    }

    /* Chat Container */
    .chat-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2.5rem 140px 2.5rem;
        min-height: auto;
        overflow-y: auto;
    }

    /* Input Styling */
    .input-container.centered {
        max-width: 350px;
        margin: 0 auto 2rem auto;
        padding: 0 1rem;
    }

    .input-container-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background:
            linear-gradient(to bottom,
                rgba(250, 247, 242, 0) 0%,
                rgba(250, 247, 242, 0.8) 15%,
                rgba(250, 247, 242, 0.95) 35%,
                rgba(250, 247, 242, 1) 50%);
        padding: 2rem 1rem 2rem 1rem;
        z-index: 1000;
        backdrop-filter: blur(12px);
        border-top: 1px solid var(--border-sepia);
        box-shadow:
            0 -8px 32px var(--shadow-warm),
            0 -2px 8px var(--shadow-cool);
    }

    .input-container-bottom > div {
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Sophisticated Input Field */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 2px solid var(--border-sepia) !important;
        background: var(--bg-ivory) !important;
        padding: 1.4rem 2rem !important;
        font-family: 'Crimson Text', Georgia, serif !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        color: var(--text-charcoal) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        box-shadow:
            inset 0 2px 4px rgba(27, 59, 54, 0.05),
            0 4px 12px var(--shadow-warm),
            0 0 0 0 rgba(212, 175, 55, 0) !important;
        letter-spacing: 0.2px !important;
        line-height: 1.5 !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: var(--text-sage) !important;
        opacity: 0.6 !important;
        font-style: italic !important;
        font-weight: 400 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--accent-amber) !important;
        background: var(--bg-ivory) !important;
        box-shadow:
            inset 0 2px 4px rgba(27, 59, 54, 0.05),
            0 8px 24px var(--shadow-warm),
            0 0 0 3px rgba(212, 175, 55, 0.15) !important;
        outline: none !important;
    }

    /* Message Styling */
    .user-message {
        background: linear-gradient(135deg, var(--bg-ivory) 0%, var(--bg-cream) 100%);
        border-left: 4px solid var(--accent-amber);
        border-radius: 8px;
        padding: 1.5rem 2rem;
        margin: 1.5rem 0;
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 1.05rem;
        line-height: 1.6;
        color: var(--text-charcoal);
        box-shadow:
            0 4px 12px var(--shadow-warm),
            inset 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    .assistant-message {
        background: linear-gradient(135deg, var(--bg-cream) 0%, var(--bg-parchment) 100%);
        border-left: 4px solid var(--primary-forest);
        border-radius: 8px;
        padding: 1.8rem 2rem;
        margin: 1.5rem 0;
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 1.05rem;
        line-height: 1.7;
        color: var(--text-charcoal);
        box-shadow:
            0 6px 18px var(--shadow-cool),
            inset 0 1px 2px rgba(255, 255, 255, 0.7);
    }

    /* Button Styling - Default */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-forest) 0%, var(--secondary-sage) 100%) !important;
        color: var(--bg-ivory) !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Crimson Text', Georgia, serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        padding: 0.8rem 2rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        box-shadow:
            0 4px 12px var(--shadow-cool),
            inset 0 1px 2px rgba(255, 255, 255, 0.1) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--secondary-sage) 0%, var(--primary-forest) 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow:
            0 6px 18px var(--shadow-cool),
            inset 0 1px 2px rgba(255, 255, 255, 0.15) !important;
    }

    /* Plus Button (Attachment) - Circular, subtle */
    .stButton > button:first-child {
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: var(--bg-cream) !important;
        border: 1px solid var(--border-sepia) !important;
        color: var(--text-sage) !important;
        font-size: 1.2rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        box-shadow: 0 2px 4px var(--shadow-warm) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .stButton > button:first-child:hover {
        background: var(--bg-ivory) !important;
        border-color: var(--accent-amber) !important;
        transform: none !important;
        box-shadow: 0 2px 8px var(--shadow-warm) !important;
    }

    /* Send Button (Form Submit) - Circular, prominent */
    button[kind="primary"],
    button[type="submit"] {
        width: 48px !important;
        height: 48px !important;
        min-height: 48px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, var(--accent-amber) 0%, var(--accent-copper) 100%) !important;
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        border: none !important;
        box-shadow:
            0 4px 12px rgba(212, 175, 55, 0.3),
            inset 0 1px 2px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    button[kind="primary"]:hover,
    button[type="submit"]:hover {
        background: linear-gradient(135deg, var(--accent-copper) 0%, var(--accent-amber) 100%) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow:
            0 6px 16px rgba(212, 175, 55, 0.4),
            inset 0 1px 2px rgba(255, 255, 255, 0.4) !important;
    }

    /* Technical Logs Styling */
    .debug-logs {
        font-family: 'Fira Code', 'Monaco', 'Courier New', monospace !important;
        background: #f8f9fa !important;
        border-left: 4px solid var(--secondary-sage) !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
        white-space: pre-wrap !important;
    }

    .error-details {
        font-family: 'Fira Code', 'Monaco', 'Courier New', monospace !important;
        background: #fff5f5 !important;
        border-left: 4px solid #e53e3e !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
    }

    /* Capabilities Hint */
    .capabilities-hint {
        text-align: center;
        margin-top: 1.5rem;
        padding: 1rem 2rem;
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 1rem;
        font-style: italic;
        color: var(--text-sage);
        line-height: 1.6;
        opacity: 0.85;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
        border-top: 1px solid var(--border-sepia);
        border-bottom: 1px solid var(--border-sepia);
    }

    /* Privacy Disclaimer */
    .privacy-disclaimer {
        text-align: center;
        margin-top: 1rem;
        padding: 0.75rem 2rem;
        font-family: 'Crimson Text', Georgia, serif;
        font-size: 0.8rem;
        color: var(--text-sage);
        line-height: 1.6;
        opacity: 0.6;
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Prevent column stacking - keep buttons side-by-side */
    div[data-testid="column"] {
        flex: 0 0 auto !important;
        min-width: fit-content !important;
    }

    /* Button container layout */
    div[data-testid="column"]:has(button) {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .landing-container {
            padding-top: 5vh;
            padding-bottom: 1rem;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .tagline {
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        .chat-container { padding: 0 1.5rem 120px 1.5rem; }
        .user-message, .assistant-message { padding: 1.2rem 1.5rem; }
        .debug-logs, .error-details { font-size: 0.75rem !important; }
        .capabilities-hint {
            font-size: 0.9rem;
            padding: 0.75rem 1.5rem;
            margin-top: 1rem;
        }
        .privacy-disclaimer {
            font-size: 0.75rem;
            margin-top: 0.75rem;
        }

        /* Keep columns inline on mobile */
        div[data-testid="column"] {
            flex-shrink: 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)


class MultiServerMCPClient:
    """MCP Client for connecting to multiple FastMCP servers."""

    def __init__(self):
        self.sessions = {}  # server_name -> ClientSession
        self.tool_registry = {}  # tool_name -> server_name
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

    async def connect_to_servers(self, server_paths: dict, status_container=None):
        """Connect to multiple FastMCP servers."""
        if status_container:
            status_container.info("🔄 Connecting to FastMCP servers...")

        # Connect to each server
        for server_name, server_path in server_paths.items():
            try:
                if status_container:
                    status_container.info(f"🔄 Connecting to {server_name} server...")

                server_params = StdioServerParameters(
                    command="fastmcp",
                    args=["run", server_path]
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
                raise

        # Build tool registry
        await self._discover_tools(status_container)

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

        # Get available tools from all FastMCP servers
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
    """Render the landing page with logo."""
    st.markdown("""
        <div class="landing-container">
            <div class="logo">DoctHER</div>
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
    client = MultiServerMCPClient()

    try:
        # Connect to MCP servers
        status_container.info("🔄 Connecting to MCP servers...")
        await client.connect_to_servers(MCP_SERVERS, status_container)
        status_container.success("✅ Connected to FastMCP servers")

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
    # User message already added before processing started
    # Just add empty tool log for user message
    st.session_state.tool_logs.append([])

    # Use persistent containers from session state (created in chat layout)
    status_container = st.session_state.get('status_container', st.empty())
    tool_chain_container = st.session_state.get('tool_chain_container', st.empty())

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

        # Form with input on top, buttons below
        with st.form(key=f"input_form_{st.session_state.form_counter}", clear_on_submit=False):
            # Text input takes full width
            default_value = st.session_state.pending_input if st.session_state.is_processing else ""
            user_input = st.text_input(
                "message",
                value=default_value,
                placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                key=f"user_input_{st.session_state.form_counter}",
                label_visibility="collapsed",
                disabled=st.session_state.is_processing
            )

            # Buttons below input
            col_plus, col_spacer, col_send = st.columns([0.1, 0.8, 0.1])

            with col_plus:
                plus_clicked = st.form_submit_button("➕", help="Add attachments")
                if plus_clicked:
                    st.session_state.show_upload_menu = not st.session_state.show_upload_menu
                    st.rerun()

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

        # Create persistent status containers at top (for processing state)
        if 'status_container' not in st.session_state:
            st.session_state.status_container = st.empty()
        if 'tool_chain_container' not in st.session_state:
            st.session_state.tool_chain_container = st.empty()

        # Display status containers
        st.session_state.status_container.empty()
        st.session_state.tool_chain_container.empty()

        # Show chat history in scrollable container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        render_chat_history()
        st.markdown('</div>', unsafe_allow_html=True)

        # Fixed bottom input
        st.markdown('<div class="input-container-bottom">', unsafe_allow_html=True)

        # Form with input on top, buttons below
        with st.form(key=f"input_form_chat_{st.session_state.form_counter}", clear_on_submit=False):
            # Text input takes full width
            default_value = st.session_state.pending_input if st.session_state.is_processing else ""
            user_input = st.text_input(
                "message",
                value=default_value,
                placeholder="e.g. I'm 38 with AMH 0.8, should I consider IVF?",
                key=f"user_input_chat_{st.session_state.form_counter}",
                label_visibility="collapsed",
                disabled=st.session_state.is_processing
            )

            # Buttons below input
            col_plus, col_spacer, col_send = st.columns([0.1, 0.8, 0.1])

            with col_plus:
                plus_clicked = st.form_submit_button("➕", help="Add attachments")
                if plus_clicked:
                    st.session_state.show_upload_menu = not st.session_state.show_upload_menu
                    st.rerun()

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

        # Add user message immediately to switch layout to chat mode
        st.session_state.messages.append({
            "role": "user",
            "content": message_content
        })

        # Store the input and set processing state
        st.session_state.pending_input = user_input
        st.session_state.pending_message = message_content
        st.session_state.is_processing = True

        # Reset upload menu state
        st.session_state.show_upload_menu = False

        # Rerun to show processing state (now in chat mode with logo at top)
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
