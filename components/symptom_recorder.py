"""
Symptom recorder component for DoctHER application.

Provides voice recording or text input interface with automatic transcription and symptom extraction.
"""

import streamlit as st
from sqlalchemy.orm import Session
from services.transcription import get_transcription_service


def show_symptom_recorder(db_session: Session, client):
    """
    Display symptom recording interface with voice or text input.

    Args:
        db_session: SQLAlchemy database session
        client: Anthropic client instance
    """
    # Initialize session state for transcription
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = None
    if 'is_transcribing' not in st.session_state:
        st.session_state.is_transcribing = False
    if 'symptom_text_input' not in st.session_state:
        st.session_state.symptom_text_input = ""

    # DoctHER branding at top (same as chat mode)
    st.markdown("""
        <div style="text-align: center; padding: 0.25rem 0 0.5rem 0;">
            <div class="logo" style="font-size: 1.5rem; margin-bottom: 0;">DoctHER</div>
        </div>
    """, unsafe_allow_html=True)

    # Voice Agent UI styling
    st.markdown("""
        <style>
        /* Make audio input button larger */
        [data-testid="stAudioInput"] button {
            width: 120px !important;
            height: 120px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stAudioInput"] button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6) !important;
        }
        [data-testid="stAudioInput"] button svg {
            width: 60px !important;
            height: 60px !important;
        }
        /* Center the audio input */
        [data-testid="stAudioInput"] {
            display: flex;
            justify-content: center;
            margin: 2rem 0;
        }
        .voice-prompt {
            font-size: 1.2rem;
            color: var(--text-color);
            text-align: center;
            opacity: 0.9;
            margin: 1.5rem 0 2rem 0;
        }
        .or-divider {
            font-size: 1rem;
            color: var(--text-color);
            opacity: 0.6;
            margin: 2rem 0 1.5rem 0;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Voice prompt
    st.markdown('<div class="voice-prompt">Tell me about your symptoms</div>', unsafe_allow_html=True)

    # Handle voice transcription
    audio_value = st.audio_input("", key="voice_input", label_visibility="collapsed")

    if audio_value is not None:
        # Automatically transcribe if not already done
        if st.session_state.transcribed_text is None and not st.session_state.is_transcribing:
            st.session_state.is_transcribing = True

        # Perform transcription automatically
        if st.session_state.is_transcribing:
            with st.spinner("Transcribing..."):
                # Get transcription service
                transcription_service = get_transcription_service(model_size="medium")

                # Reset audio file pointer
                audio_value.seek(0)

                # Transcribe
                result = transcription_service.transcribe_audio(audio_value, language="en")

                if result['success']:
                    st.session_state.symptom_text_input = result['text']
                    st.session_state.transcribed_text = result['text']
                    st.session_state.is_transcribing = False

                    # Auto-submit after showing transcribed text
                    import time
                    st.success(f"✅ Transcribed: {result['text']}")
                    time.sleep(1.5)  # Show text for 1.5 seconds

                    # Navigate to symptom form automatically
                    st.session_state.symptom_text_to_record = result['text']
                    st.session_state.symptom_extraction_cache = None
                    st.session_state.show_symptom_form = True
                    st.session_state.transcribed_text = None
                    st.session_state.symptom_text_input = ""
                    st.rerun()
                else:
                    st.error(f"Transcription failed: {result['error']}")
                    st.session_state.is_transcribing = False

    # Add "or type" divider
    st.markdown('<div class="or-divider">or type your symptoms</div>', unsafe_allow_html=True)

    # Form for text input
    with st.form(key="symptom_voice_form", clear_on_submit=False):
        # Text input
        user_input = st.text_input(
            "message",
            value=st.session_state.symptom_text_input,
            placeholder="e.g. I have a severe headache that started this morning",
            key="symptom_voice_input",
            label_visibility="collapsed"
        )

        # Buttons layout: [← left] [large space] [Submit right]
        btn_col1, btn_col2, btn_col3 = st.columns([1, 6, 1])

        with btn_col1:
            back_clicked = st.form_submit_button("←", help="Back to Chat", use_container_width=True)

        # btn_col2 is empty space

        with btn_col3:
            submit_clicked = st.form_submit_button("➤", help="Submit", type="primary", use_container_width=True)

    # Handle form submission
    if back_clicked:
        st.session_state.transcribed_text = None
        st.session_state.symptom_text_input = ""
        st.rerun()

    if submit_clicked and user_input.strip():
        # Save text to session state for symptom form
        st.session_state.symptom_text_to_record = user_input
        st.session_state.symptom_extraction_cache = None

        # Navigate to symptom form
        st.session_state.show_symptom_form = True
        st.session_state.transcribed_text = None
        st.session_state.symptom_text_input = ""
        st.rerun()
