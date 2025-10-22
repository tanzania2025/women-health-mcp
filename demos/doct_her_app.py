#!/usr/bin/env python3
"""
Doct-Her: AI-Powered Women's Health Assistant
A modern chat interface powered by Claude and local MCP servers
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Doct-Her - Your AI Women's Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Claude-inspired design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0;
    }

    /* Landing page container */
    .landing-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 4rem 2rem;
        text-align: center;
    }

    /* Logo styling */
    .logo {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -2px;
    }

    /* Tagline */
    .tagline {
        font-size: 2rem;
        color: #4a5568;
        margin-bottom: 3rem;
        font-weight: 300;
    }

    /* Chat container */
    .chat-container {
        max-width: 900px;
        margin: 2rem auto;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        padding: 2rem;
    }

    /* Chat input area */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Capabilities hint text */
    .capabilities-hint {
        text-align: center;
        margin-top: 1rem;
        color: #718096;
        font-size: 0.9rem;
        cursor: pointer;
        position: relative;
        display: inline-block;
        padding: 0.5rem;
    }

    .capabilities-hint:hover {
        color: #667eea;
    }

    /* Calculator list tooltip */
    .calculator-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        color: #2d3748;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-size: 0.9rem;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        margin-bottom: 0.75rem;
        z-index: 1000;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 2px solid #667eea;
        white-space: nowrap;
    }

    .capabilities-hint:hover .calculator-tooltip {
        opacity: 1;
    }

    .calculator-list {
        text-align: left;
        line-height: 1.8;
    }

    .calculator-item {
        display: block;
        color: #2d3748;
        font-weight: 500;
    }

    /* Chat messages */
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 12px;
    }

    .user-message {
        background: #f7fafc;
        border-left: 4px solid #667eea;
    }

    .assistant-message {
        background: #fff;
        border-left: 4px solid #48bb78;
    }


    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* Info cards */
    .info-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Available calculators (tools)
AVAILABLE_CALCULATORS = {
    "Menopause Calculator": {
        "description": "Predict menopause timing based on age, AMH, and risk factors",
        "endpoint": "menopause_prediction",
        "server": "servers.menopause_server"
    },
    "Ovarian Reserve Assessment": {
        "description": "Assess ovarian reserve using AMH, FSH, and age",
        "endpoint": "ovarian_reserve",
        "server": "servers.asrm_server"
    },
    "IVF Success Calculator": {
        "description": "Calculate IVF success rates based on age and biomarkers",
        "endpoint": "ivf_success",
        "server": "servers.sart_ivf_server"
    }
}

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False

def render_landing_page():
    """Render the landing page with logo and tagline."""
    st.markdown("""
        <div class="landing-container">
            <div class="logo">Doct-Her</div>
            <div class="tagline">How can I help you today?</div>
        </div>
    """, unsafe_allow_html=True)

def render_capabilities_hint():
    """Render simple capabilities hint with hover tooltip."""
    # Build calculator list for tooltip
    calculator_list = "<div class='calculator-list'>"
    for calc_name in AVAILABLE_CALCULATORS.keys():
        calculator_list += f"<span class='calculator-item'>• {calc_name}</span>"
    calculator_list += "</div>"

    st.markdown(f"""
        <div style="text-align: center;">
            <div class="capabilities-hint">
                some of the things I can do
                <div class="calculator-tooltip">
                    {calculator_list}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    """Render the chat interface."""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.messages:
        message_class = "user-message" if message["role"] == "user" else "assistant-message"
        role_icon = "👤" if message["role"] == "user" else "🩺"
        st.markdown(f"""
            <div class="chat-message {message_class}">
                <strong>{role_icon} {message["role"].title()}:</strong><br>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def handle_user_input(user_input: str):
    """Process user input and get response from Claude via MCP."""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # TODO: Integrate with Anthropic API and local MCP servers
    # For now, provide a placeholder response
    calculator_names = "\n    - ".join(AVAILABLE_CALCULATORS.keys())

    assistant_response = f"""
    Thank you for your question. I'm Doct-Her, your AI women's health assistant.

    I have access to several specialized calculators:
    - {calculator_names}

    To provide you with the most accurate information, I'll connect to the
    local MCP servers and use the appropriate calculator for your question.

    Your question: "{user_input}"

    (Integration with Anthropic Claude API and local MCP servers is currently being configured)
    """

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

    # Chat input centered
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    user_input = st.text_input(
        "Ask me anything about women's health...",
        placeholder="e.g., I'm 38 with AMH 0.8, should I consider IVF?",
        key="user_input",
        label_visibility="collapsed"
    )

    # Render capabilities hint below input
    render_capabilities_hint()

    if user_input and user_input.strip():
        handle_user_input(user_input)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Display chat history if exists
    if st.session_state.show_chat and st.session_state.messages:
        st.markdown("---")
        render_chat_interface()

    # Footer info
    if not st.session_state.show_chat:
        st.markdown("""
            <div class="info-card">
                <strong>🔒 Privacy First</strong><br>
                Your health data is processed securely using local MCP servers
                and HIPAA-compliant encryption. No data is stored permanently.
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
