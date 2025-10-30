#!/usr/bin/env python3
"""
DoctHER: AI-Powered Women's Health Assistant
Sophisticated medical journal aesthetic with unique typography and atmospheric design
"""

import streamlit as st
import sys
import os
import asyncio
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Add project root to path - go up one level from demos/ to the actual project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Import MCP client
sys.path.insert(0, str(project_root))
try:
    from mcp_client import MCPClient
except ImportError as e:
    st.error(f"Could not import mcp_client. Please run from project root directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="DoctHER - Women's Health Intelligence",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        padding-top: 15vh;
        padding-bottom: 4rem;
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
        margin-bottom: 3rem;
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
        max-width: 750px;
        margin: 0 auto 2rem auto;
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

    /* Button Styling */
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

    /* Responsive Design */
    @media (max-width: 768px) {
        .logo { font-size: 3.5rem; }
        .tagline { font-size: 1.2rem; }
        .chat-container { padding: 0 1.5rem 120px 1.5rem; }
        .user-message, .assistant-message { padding: 1.2rem 1.5rem; }
        .debug-logs, .error-details { font-size: 0.75rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_message_sent" not in st.session_state:
    st.session_state.first_message_sent = False

async def query_with_mcp_standalone(user_input: str) -> str:
    """Query Claude with MCP context using standalone client connections with detailed logging"""
    debug_log = []
    debug_log.append(f"📝 Processing query: '{user_input}'")

    try:
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return "❌ Please set your ANTHROPIC_API_KEY in the environment variables."

        # Define the individual MCP servers to connect to
        server_scripts = [
            str(project_root / "servers/pubmed_server.py"),
            str(project_root / "servers/eshre_server.py"),
            str(project_root / "servers/nams_server.py"),
            str(project_root / "servers/elsa_server.py"),
            str(project_root / "servers/asrm_server.py"),
            str(project_root / "servers/sart_ivf_server.py"),
            str(project_root / "servers/menopause_server.py")
        ]

        debug_log.append(f"🔗 Connecting to {len(server_scripts)} MCP servers...")

        # Create fresh clients for this query
        clients = {}
        all_tools = []
        tool_client_map = {}
        connected_count = 0

        # Connect to all servers with detailed logging
        for server_script in server_scripts:
            server_name = Path(server_script).stem.replace('_server', '')

            try:
                client = MCPClient(command="python", args=[server_script])
                await client.connect()
                clients[server_name] = client

                # Get tools from this client
                client_tools = await client.list_tools()
                all_tools.extend(client_tools)

                # Map tools to their client
                for tool in client_tools:
                    tool_client_map[tool.name] = client

                connected_count += 1
                debug_log.append(f"  ✅ {server_name}: {len(client_tools)} tools")

            except Exception as e:
                debug_log.append(f"  ❌ {server_name}: failed ({str(e)[:50]}...)")
                continue

        if not clients:
            error_msg = "❌ Could not connect to any MCP servers."
            debug_log.append(error_msg)
            return "\n".join(debug_log)

        debug_log.append(f"\n📊 Total: {connected_count} servers, {len(all_tools)} tools")

        # Create Anthropic client
        anthropic = Anthropic(api_key=api_key)

        # Prepare messages
        messages = [{
            "role": "user",
            "content": f"{user_input}\n\nPlease use the available medical research tools to provide evidence-based insights when relevant."
        }]

        # Convert MCP tools to Anthropic format
        anthropic_tools = []
        for tool in all_tools:
            try:
                anthropic_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                })
            except Exception as e:
                debug_log.append(f"⚠️  Failed to convert tool {tool.name}: {str(e)}")
                continue

        debug_log.append(f"\n🤖 Sending to Claude with {len(anthropic_tools)} tools available...")

        # Call Claude with or without tools
        if anthropic_tools:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=messages,
                tools=anthropic_tools,
                temperature=0.1,
            )
        else:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                messages=messages,
                temperature=0.1,
            )

        debug_log.append("✅ Claude response received!")

        # Process response and handle tool calls with detailed logging
        result_parts = []
        tool_results = []

        for content_block in response.content:
            if content_block.type == "text":
                result_parts.append(content_block.text)
                debug_log.append("💬 Claude provided text response")
            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_args = content_block.input
                tool_id = content_block.id

                debug_log.append(f"\n🛠  Claude wants to use tool: {tool_name}")
                import json
                debug_log.append(f"   📄 Arguments: {json.dumps(tool_args, indent=2)}")

                try:
                    # Find the correct client for this tool
                    client_for_tool = tool_client_map.get(tool_name)
                    if client_for_tool:
                        debug_log.append(f"   ⚡ Executing {tool_name}...")
                        mcp_result = await client_for_tool.call_tool(tool_name, tool_args)
                        tool_output = ""

                        if mcp_result.content:
                            for content in mcp_result.content:
                                if hasattr(content, 'text'):
                                    tool_output += content.text

                        debug_log.append(f"   ✅ Tool executed! Response length: {len(tool_output)} chars")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": tool_output
                        })
                    else:
                        debug_log.append(f"   ❌ Tool not available")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": "Tool not available"
                        })

                except Exception as e:
                    debug_log.append(f"   ❌ Tool execution failed: {str(e)}")
                    # Don't gracefully fallback - show the error
                    error_msg = f"Tool execution failed: {str(e)}\n\nFull error details: {repr(e)}"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": error_msg
                    })

        # Get final response if tools were used
        final_text = "\n".join(result_parts)
        if tool_results:
            try:
                debug_log.append(f"\n🔄 Sending tool results back to Claude for synthesis...")

                follow_up_messages = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results}
                ]

                final_response = anthropic.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=4000,
                    messages=follow_up_messages,
                    temperature=0.1,
                )

                debug_log.append("✅ Final synthesis complete!")

                final_text = ""
                for content_block in final_response.content:
                    if content_block.type == "text":
                        final_text += content_block.text

            except Exception as e:
                # Don't gracefully fallback - show the error
                debug_log.append(f"⚠️  Synthesis failed: {str(e)}")
                error_details = f"Synthesis error: {str(e)}\n\nFull error: {repr(e)}"
                final_text = "\n".join(result_parts) + "\n\n" + error_details

        # Cleanup connections with logging
        debug_log.append(f"\n🧹 Cleaning up {len(clients)} connections...")
        for server_name, client in clients.items():
            try:
                await client.cleanup()
                debug_log.append(f"  ✅ {server_name} cleaned up")
            except asyncio.CancelledError:
                # Expected when Streamlit reruns - suppress
                debug_log.append(f"  ⚠️  {server_name} cleanup cancelled (Streamlit rerun)")
                pass
            except Exception as e:
                debug_log.append(f"  ⚠️  {server_name} cleanup warning: {str(e)[:50]}")
                pass

        # Combine debug log with final response
        full_response = "\n".join(debug_log) + "\n\n" + "=" * 60 + "\n📄 FINAL DOCTHER RESPONSE:\n" + "=" * 60 + "\n" + final_text
        return full_response

    except Exception as e:
        # Don't gracefully fallback - show detailed error
        import traceback
        error_details = f"❌ Critical Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        if 'debug_log' in locals():
            return "\n".join(debug_log) + "\n\n" + error_details
        return error_details

# Removed fallback function - we want detailed error reporting instead

def display_landing_page():
    """Display the sophisticated landing page"""
    st.markdown("""
    <div class="landing-container">
        <div class="logo">DoctHER</div>
        <div class="tagline">Intelligence in Women's Health</div>
    </div>
    """, unsafe_allow_html=True)

def display_chat_interface():
    """Display the chat messages"""
    if st.session_state.messages:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>You:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>DoctHER:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""

    # Show landing page if no messages
    if not st.session_state.first_message_sent:
        display_landing_page()
        input_container_class = "input-container centered"
    else:
        display_chat_interface()
        input_container_class = "input-container-bottom"

    # New conversation button (positioned above input when chat exists)
    if st.session_state.messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:  # Center the button
            if st.button("🔄 New Conversation", key="new_conv"):
                st.session_state.messages = []
                st.session_state.first_message_sent = False
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing

    # Input area using form to prevent infinite loops
    st.markdown(f'<div class="{input_container_class}">', unsafe_allow_html=True)

    with st.form(key="input_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])

        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask about fertility, hormones, reproductive health, or request research..." if not st.session_state.first_message_sent
                          else "Continue your health consultation...",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button("Ask")

    st.markdown('</div>', unsafe_allow_html=True)

    # Process user input when form is submitted
    if submitted and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.first_message_sent = True

        # Get AI response with detailed technical logging
        with st.spinner("🔬 Analyzing with medical intelligence..."):
            try:
                response = asyncio.run(query_with_mcp_standalone(user_input))
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                # Show detailed error instead of fallback
                import traceback
                error_response = f"❌ **System Error:**\n\nError: {str(e)}\n\nFull traceback:\n```\n{traceback.format_exc()}\n```"
                st.session_state.messages.append({"role": "assistant", "content": error_response})

        # Rerun to refresh
        st.rerun()

if __name__ == "__main__":
    main()
