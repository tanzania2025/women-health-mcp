#!/usr/bin/env python3
"""
Doct-Her: AI-Powered Women's Health Assistant
Modern chat interface using Claude with stdio MCP servers
"""

import streamlit as st
import sys
import os
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
    page_title="Doct-Her - Your AI Women's Health Assistant",
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput > label {display: none !important;}

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #faf5f9 0%, #f0f4f8 100%);
        padding: 0;
    }

    .block-container {
        padding-top: 3rem;
        max-width: 900px;
    }

    .landing-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 3rem 2rem 1.5rem 2rem;
        text-align: center;
    }

    .logo {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
        letter-spacing: -0.5px;
    }

    .tagline {
        font-size: 1.35rem;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .input-container {
        max-width: 700px;
        margin: 0 auto 1.5rem auto;
    }

    .stTextInput > div > div > input {
        border-radius: 16px !important;
        border: 1.5px solid #e9d5ff !important;
        padding: 0.9rem 1.3rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        background: #fefeff !important;
        box-shadow: 0 2px 8px rgba(167, 139, 250, 0.04) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #c084fc !important;
        box-shadow: 0 0 0 3px rgba(192, 132, 252, 0.1) !important;
        outline: none !important;
    }

    .chat-message {
        padding: 1rem 1.25rem;
        margin: 1rem 0;
        border-radius: 12px;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .user-message {
        background: #faf5f9;
        border-left: 3px solid #c084fc;
    }

    .assistant-message {
        background: #ffffff;
        border-left: 3px solid #a78bfa;
        box-shadow: 0 2px 8px rgba(167, 139, 250, 0.04);
    }

    .stForm button[kind="formSubmit"] {
        display: none;
    }

    .capabilities-hint {
        text-align: center;
        margin-top: 1rem;
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 400;
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
            command="python",
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

    async def process_query(self, query: str, status_container=None) -> str:
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

        # System prompt
        system_prompt = """You are Doct-Her, an AI-powered women's health assistant specializing in reproductive health and fertility.

You have access to clinical calculator tools. Use these tools to provide evidence-based guidance.

**Your Role:**
- Provide evidence-based fertility and reproductive health guidance
- Use the available tools to calculate ovarian reserve, IVF success rates, etc.
- Explain clinical assessments in clear, compassionate language
- Help patients understand their options and next steps
- Always clarify that you're an AI assistant and recommend consulting healthcare providers

**Guidelines:**
1. When you receive a question with age and AMH data, USE THE TOOLS to get clinical assessments
2. Be compassionate and supportive
3. Explain medical terms clearly
4. Always recommend consulting with healthcare providers for medical decisions
5. If age and AMH indicate time-sensitive concerns, gently emphasize urgency
6. Provide clear next steps

Remember: You're providing educational information, not medical advice."""

        # Call Claude with tools
        messages = [{"role": "user", "content": query}]
        tool_calls_made = []

        # Agentic loop
        for iteration in range(5):
            if status_container:
                status_container.info(f"🤖 Claude thinking... (iteration {iteration + 1}/5)")

            response = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=2048,
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

                # Add tool usage summary
                if tool_calls_made:
                    tools_used = "\n".join([f"• **{call}**" for call in tool_calls_made])
                    final_text = f"**🔧 MCP Tools Used:**\n{tools_used}\n\n---\n\n{final_text}"

                if status_container:
                    status_container.success("✅ Response complete!")

                return final_text

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
                        tool_calls_made.append(content.name)

                        if status_container:
                            status_container.warning(f"🔧 Calling tool: **{content.name}**")

                        # Execute tool via MCP
                        result = await self.session.call_tool(
                            content.name,
                            content.input
                        )

                        if status_container:
                            status_container.success(f"✅ Tool **{content.name}** completed")

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
                return f"Unexpected stop reason: {response.stop_reason}"

        return "Maximum iterations reached"

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = None


def render_landing_page():
    """Render the landing page with logo and tagline."""
    st.markdown("""
        <div class="landing-container">
            <div class="logo">Doct-Her</div>
            <div class="tagline">How can I help?</div>
        </div>
    """, unsafe_allow_html=True)


def render_capabilities_hint():
    """Render capabilities hint."""
    st.markdown("""
        <div class="capabilities-hint">
            some of the things I can do: assess ovarian reserve, predict IVF success, estimate menopause timing
        </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    """Render the chat history."""
    if st.session_state.messages:
        for message in st.session_state.messages:
            message_class = "user-message" if message["role"] == "user" else "assistant-message"
            role_icon = "👤" if message["role"] == "user" else "🩺"
            role_label = "You" if message["role"] == "user" else "Doct-Her"

            st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>{role_icon} {role_label}</strong><br>
                    {message["content"]}
                </div>
            """, unsafe_allow_html=True)


async def handle_user_input_async(user_input: str, status_container):
    """Process user input asynchronously."""

    if not ANTHROPIC_API_KEY:
        return """⚠️ **Anthropic API key not configured**

To enable AI-powered consultations, please:
1. Add your ANTHROPIC_API_KEY to the `.env` file
2. Restart the application"""

    try:
        # Initialize MCP client if not already done
        if st.session_state.mcp_client is None:
            status_container.info("🔄 Connecting to MCP server...")
            st.session_state.mcp_client = MCPClient()
            await st.session_state.mcp_client.connect_to_server(MCP_SERVER_SCRIPT)
            status_container.success("✅ Connected to MCP server")

        # Process query
        response = await st.session_state.mcp_client.process_query(user_input, status_container)
        return response

    except Exception as e:
        return f"❌ Error: {str(e)}"


def handle_user_input(user_input: str):
    """Handle user input."""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Create status container
    status_container = st.empty()

    # Process with MCP
    assistant_response = asyncio.run(handle_user_input_async(user_input, status_container))

    # Clear status
    status_container.empty()

    # Add assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_response
    })

    st.session_state.show_chat = True


def main():
    """Main application."""
    initialize_session_state()

    # Render landing page
    render_landing_page()

    # Chat input
    st.markdown('<div class="input-container">', unsafe_allow_html=True)

    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "Ask your question",
            placeholder="e.g., I'm 38 with AMH 0.8, should I consider IVF?",
            key="user_input",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("Send")

        if submitted and user_input and user_input.strip():
            handle_user_input(user_input)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Capabilities hint
    render_capabilities_hint()

    # Display chat history
    if st.session_state.show_chat:
        render_chat_history()


if __name__ == "__main__":
    main()
