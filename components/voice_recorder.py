"""
Voice symptom recorder component for DoctHER application.

Provides voice recording interface with automatic transcription and symptom extraction.
"""

import streamlit as st
from sqlalchemy.orm import Session
from services.transcription import get_transcription_service


def show_voice_symptom_recorder(db_session: Session, client):
    """
    Display voice symptom recording interface.

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

    # Back button in top left corner
    if st.button("←", help="Back to Chat"):
        st.session_state.show_voice_recorder = False
        st.session_state.transcribed_text = None
        st.session_state.symptom_text_input = ""
        st.rerun()

    # Add vertical spacing
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Large microphone icon with audio input
        audio_value = st.audio_input("🎤", key="voice_input", label_visibility="hidden")

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Message
        st.markdown(
            "<p style='text-align: center; font-size: 18px; color: #666;'>Record your voice or type your symptoms below</p>",
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

        # Handle voice transcription
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
                        st.rerun()
                    else:
                        st.error(f"Transcription failed: {result['error']}")
                        st.session_state.is_transcribing = False

        # Text input box
        symptom_text = st.text_area(
            "Symptoms",
            value=st.session_state.symptom_text_input,
            height=200,
            placeholder="Describe your symptoms here...",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Submit button
        if st.button("Submit", type="primary", use_container_width=True, disabled=not symptom_text.strip()):
            # Save text to session state for symptom form
            st.session_state.symptom_text_to_record = symptom_text
            st.session_state.symptom_extraction_cache = None

            # Navigate to symptom form
            st.session_state.show_voice_recorder = False
            st.session_state.show_symptom_form = True
            st.session_state.transcribed_text = None
            st.session_state.symptom_text_input = ""
            st.rerun()
