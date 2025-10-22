#!/usr/bin/env python3
"""
Doct-Her: AI-Powered Women's Health Assistant
A modern chat interface powered by Claude and local MCP servers
"""

import streamlit as st
import sys
import os
import asyncio
import httpx
import re
from pathlib import Path
from anthropic import Anthropic
from typing import Optional, Dict, Any

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

# Custom CSS - Clinical & Professional design with feminine touches
st.markdown("""
<style>
    /* Import softer, professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* Hide Streamlit branding and default labels */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stTextInput > label {display: none !important;}

    /* Global font and colors */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container - soft clinical colors with feminine touch */
    .main {
        background: linear-gradient(135deg, #faf5f9 0%, #f0f4f8 100%);
        padding: 0;
    }

    .block-container {
        padding-top: 3rem;
        max-width: 900px;
    }

    /* Landing page container */
    .landing-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 3rem 2rem 1.5rem 2rem;
        text-align: center;
    }

    /* Logo styling - soft professional lavender */
    .logo {
        font-size: 3.2rem;
        font-weight: 500;
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
        letter-spacing: -0.5px;
    }

    /* Tagline - softer, more clinical */
    .tagline {
        font-size: 1.35rem;
        color: #64748b;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Input container */
    .input-container {
        max-width: 700px;
        margin: 0 auto 1.5rem auto;
    }

    /* Chat input area - softer borders, clinical feel */
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

    .stTextInput > div > div > input::placeholder {
        color: #a0aec0;
        font-weight: 300;
    }

    /* Capabilities hint text */
    .capabilities-hint {
        text-align: center;
        margin-top: 1rem;
        color: #94a3b8;
        font-size: 0.85rem;
        cursor: pointer;
        position: relative;
        display: inline-block;
        padding: 0.5rem;
        font-weight: 400;
    }

    .capabilities-hint:hover {
        color: #a78bfa;
    }

    /* Calculator list tooltip - softer colors */
    .calculator-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: white;
        color: #475569;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-size: 0.875rem;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s ease;
        margin-bottom: 0.75rem;
        z-index: 1000;
        box-shadow: 0 10px 40px rgba(167, 139, 250, 0.15);
        border: 1.5px solid #e9d5ff;
        white-space: nowrap;
    }

    .capabilities-hint:hover .calculator-tooltip {
        opacity: 1;
    }

    .calculator-list {
        text-align: left;
        line-height: 1.9;
    }

    .calculator-item {
        display: block;
        color: #475569;
        font-weight: 400;
    }

    /* Chat messages */
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

    /* Chat history container */
    .chat-history {
        max-width: 700px;
        margin: 2rem auto;
    }

    /* Privacy link - subtle footer */
    .privacy-link {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
    }

    .privacy-link a {
        color: #94a3b8;
        font-size: 0.8rem;
        text-decoration: none;
        font-weight: 400;
        transition: color 0.2s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }

    .privacy-link a:hover {
        color: #a78bfa;
    }

    .privacy-icon {
        font-size: 0.75rem;
    }

    /* Button styling - softer clinical colors */
    .stButton > button {
        background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.7rem 1.8rem;
        font-weight: 500;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
    }

    /* Hide form submit button but keep Enter key functionality */
    .stForm button[kind="formSubmit"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
MCP_API_KEY = os.getenv("API_KEY", "demo-api-key-change-in-production")

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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
            <div class="tagline">How can I help?</div>
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

def render_privacy_link():
    """Render subtle privacy information link."""
    st.markdown("""
        <div class="privacy-link">
            <a href="#" onclick="return false;">
                <span class="privacy-icon">🔒</span>
                <span>Your data is processed securely and never stored</span>
            </a>
        </div>
    """, unsafe_allow_html=True)

def render_chat_history():
    """Render the chat history."""
    if st.session_state.messages:
        st.markdown('<div class="chat-history">', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)

def extract_patient_data(user_input: str) -> Dict[str, Any]:
    """Extract patient data from user input using regex patterns."""
    patient_data = {}

    # Extract age
    age_match = re.search(r'\b(\d{2})\s*(?:years?\s*old|y/?o)\b', user_input, re.IGNORECASE)
    if age_match:
        patient_data['age'] = int(age_match.group(1))

    # Extract AMH level
    amh_match = re.search(r'AMH\s*(?:is\s*|of\s*)?(\d+\.?\d*)\s*(?:ng/ml)?', user_input, re.IGNORECASE)
    if amh_match:
        patient_data['amh'] = float(amh_match.group(1))

    # Extract FSH level
    fsh_match = re.search(r'FSH\s*(?:is\s*|of\s*)?(\d+\.?\d*)', user_input, re.IGNORECASE)
    if fsh_match:
        patient_data['fsh'] = float(fsh_match.group(1))

    return patient_data


async def gather_mcp_context(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Gather clinical context from MCP server tools."""
    context = {}
    headers = {
        "Authorization": f"Bearer {MCP_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check if MCP server is available
            try:
                health = await client.get(f"{MCP_SERVER_URL}/health")
                if health.status_code != 200:
                    return {"error": "MCP server not available"}
            except:
                return {"error": "MCP server not running. Please start it with: python scripts/run_server.py"}

            # Get ovarian reserve assessment if we have age and AMH
            if 'age' in patient_data and 'amh' in patient_data:
                try:
                    response = await client.post(
                        f"{MCP_SERVER_URL}/mcp/tools/assess-ovarian-reserve",
                        json={
                            "age": patient_data['age'],
                            "amh": patient_data['amh'],
                            "fsh": patient_data.get('fsh')
                        },
                        headers=headers
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if "content" in result:
                            import json
                            context['ovarian_reserve'] = json.loads(result["content"][0]["text"])
                except Exception as e:
                    context['ovarian_reserve_error'] = str(e)

            # Get IVF success prediction if we have age and AMH
            if 'age' in patient_data and 'amh' in patient_data:
                try:
                    response = await client.post(
                        f"{MCP_SERVER_URL}/mcp/tools/predict-ivf-success",
                        json={
                            "age": patient_data['age'],
                            "amh": patient_data['amh'],
                            "cycle_type": "fresh"
                        },
                        headers=headers
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if "content" in result:
                            import json
                            context['ivf_prediction'] = json.loads(result["content"][0]["text"])
                except Exception as e:
                    context['ivf_prediction_error'] = str(e)

    except Exception as e:
        context['error'] = f"Error connecting to MCP server: {str(e)}"

    return context


def call_claude_with_context(user_input: str, mcp_context: Dict[str, Any]) -> str:
    """Call Claude API with MCP context."""

    if not ANTHROPIC_API_KEY:
        return """⚠️ **Anthropic API key not configured**

To enable AI-powered consultations, please:
1. Add your ANTHROPIC_API_KEY to the `.env` file
2. Restart the application

For now, here's what I can tell you based on the MCP servers:
""" + format_mcp_context(mcp_context)

    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Build system prompt with MCP context
        system_prompt = build_system_prompt_with_context(mcp_context)

        # Call Claude API
        message = client.messages.create(
            model="claude-4-5-haiku-20250110",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        return message.content[0].text

    except Exception as e:
        return f"❌ Error calling Claude API: {str(e)}\n\nMCP Context:\n{format_mcp_context(mcp_context)}"


def build_system_prompt_with_context(mcp_context: Dict[str, Any]) -> str:
    """Build system prompt with MCP clinical context."""

    prompt = """You are Doct-Her, an AI-powered women's health assistant specializing in reproductive health and fertility.

You have access to evidence-based clinical calculators and the latest research data through MCP (Model Context Protocol) servers.

**Your Role:**
- Provide evidence-based fertility and reproductive health guidance
- Explain clinical assessments in clear, compassionate language
- Help patients understand their options and next steps
- Always clarify that you're an AI assistant and recommend consulting healthcare providers

**Clinical Context from MCP Servers:**
"""

    if 'error' in mcp_context:
        prompt += f"\n⚠️ MCP Server Status: {mcp_context['error']}\n"
    else:
        if 'ovarian_reserve' in mcp_context:
            or_data = mcp_context['ovarian_reserve'].get('result', {})
            prompt += f"""
**Ovarian Reserve Assessment (ASRM Guidelines):**
- Category: {or_data.get('category', 'N/A').replace('_', ' ').title()}
- Percentile: {or_data.get('percentile', 'N/A')}th for age
- Interpretation: {or_data.get('interpretation', 'N/A')}
"""

        if 'ivf_prediction' in mcp_context:
            ivf_data = mcp_context['ivf_prediction'].get('result', {})
            prompt += f"""
**IVF Success Prediction (SART Database):**
- Live Birth Rate: {ivf_data.get('live_birth_rate', 'N/A')}% per fresh cycle
- Confidence: {ivf_data.get('confidence', {}).get('level', 'N/A')}
- Data Source: SART database with {ivf_data.get('evidence_basis', {}).get('sample_size', 'N/A')} cycles
"""

    prompt += """
**Guidelines:**
1. Use the clinical context above to inform your response
2. Be compassionate and supportive
3. Explain medical terms clearly
4. Always recommend consulting with healthcare providers for medical decisions
5. If age and AMH indicate time-sensitive concerns, gently emphasize urgency
6. Provide clear next steps

Remember: You're providing educational information, not medical advice.
"""

    return prompt


def format_mcp_context(mcp_context: Dict[str, Any]) -> str:
    """Format MCP context for display."""
    if 'error' in mcp_context:
        return f"❌ {mcp_context['error']}"

    output = []

    if 'ovarian_reserve' in mcp_context:
        or_data = mcp_context['ovarian_reserve'].get('result', {})
        output.append(f"**Ovarian Reserve:** {or_data.get('category', 'N/A').replace('_', ' ').title()}")
        output.append(f"**Percentile:** {or_data.get('percentile', 'N/A')}th")

    if 'ivf_prediction' in mcp_context:
        ivf_data = mcp_context['ivf_prediction'].get('result', {})
        output.append(f"**IVF Success Rate:** {ivf_data.get('live_birth_rate', 'N/A')}%")

    return "\n".join(output) if output else "No clinical context available"


def handle_user_input(user_input: str):
    """Process user input and get response from Claude via MCP."""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Show thinking indicator
    with st.spinner("🧠 Doct-Her is thinking..."):
        # Extract patient data from input
        patient_data = extract_patient_data(user_input)

        # Gather MCP context
        mcp_context = asyncio.run(gather_mcp_context(patient_data))

        # Call Claude API with context
        assistant_response = call_claude_with_context(user_input, mcp_context)

    # Add assistant response to chat
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
    st.markdown('<div class="input-container">', unsafe_allow_html=True)

    # Use a form to handle Enter key submission (Claude-style)
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input(
            "Ask your question",
            placeholder="e.g., I'm 38 with AMH 0.8, should I consider IVF?",
            key="user_input",
            label_visibility="collapsed"
        )
        # Submit button is hidden via CSS but enables Enter key submission
        submitted = st.form_submit_button("Send")

        if submitted and user_input and user_input.strip():
            handle_user_input(user_input)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Render capabilities hint below input
    render_capabilities_hint()

    # Display chat history if exists
    if st.session_state.show_chat:
        render_chat_history()

    # Privacy link at bottom
    if not st.session_state.show_chat:
        render_privacy_link()

if __name__ == "__main__":
    main()
