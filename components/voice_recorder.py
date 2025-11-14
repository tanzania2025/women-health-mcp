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
    st.markdown("# 🎤 Voice Symptom Recorder")
    st.markdown("Record your symptoms by voice and we'll transcribe and analyze them for you.")

    st.markdown("---")

    # Initialize session state for transcription
    if 'transcribed_text' not in st.session_state:
        st.session_state.transcribed_text = None
    if 'is_transcribing' not in st.session_state:
        st.session_state.is_transcribing = False

    # Back button
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("←", help="Back to Chat"):
            st.session_state.show_voice_recorder = False
            st.session_state.transcribed_text = None
            st.rerun()

    st.markdown("### Record Your Symptoms")

    # Audio input widget
    audio_value = st.audio_input("Click to start recording", key="voice_input")

    if audio_value is not None:
        st.markdown("---")

        # Show audio player
        st.audio(audio_value)

        # Transcribe button
        if not st.session_state.is_transcribing and st.session_state.transcribed_text is None:
            if st.button("📝 Transcribe Recording", type="primary", use_container_width=True):
                st.session_state.is_transcribing = True
                st.rerun()

        # Perform transcription
        if st.session_state.is_transcribing:
            with st.spinner("Transcribing your recording..."):
                # Get transcription service
                transcription_service = get_transcription_service(model_size="medium")

                # Reset audio file pointer
                audio_value.seek(0)

                # Transcribe
                result = transcription_service.transcribe_audio(audio_value, language="en")

                if result['success']:
                    st.session_state.transcribed_text = result['text']
                    st.session_state.is_transcribing = False
                    st.success("✅ Transcription complete!")
                    st.rerun()
                else:
                    st.error(f"❌ Transcription failed: {result['error']}")
                    st.session_state.is_transcribing = False

        # Show transcribed text with edit option
        if st.session_state.transcribed_text:
            st.markdown("### Transcribed Text")

            # Editable text area
            edited_text = st.text_area(
                "Review and edit if needed:",
                value=st.session_state.transcribed_text,
                height=150,
                help="You can edit the transcribed text before submitting"
            )

            st.markdown("---")

            # Action buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑️ Clear & Re-record", use_container_width=True):
                    st.session_state.transcribed_text = None
                    st.session_state.is_transcribing = False
                    st.rerun()

            with col2:
                if st.button("🩺 Record Symptom", type="primary", use_container_width=True):
                    # Save transcribed text to session state for symptom form
                    st.session_state.symptom_text_to_record = edited_text
                    st.session_state.symptom_extraction_cache = None

                    # Navigate to symptom form
                    st.session_state.show_voice_recorder = False
                    st.session_state.show_symptom_form = True
                    st.session_state.transcribed_text = None
                    st.rerun()

    else:
        # Instructions when no audio recorded
        st.info("""
        **How to use:**
        1. Click the microphone button above to start recording
        2. Describe your symptoms naturally (e.g., "I have a severe headache that started this morning")
        3. Click stop when done
        4. Review the transcription and edit if needed
        5. Click "Record Symptom" to save

        **Tips:**
        - Speak clearly and at a normal pace
        - Include details like: symptom type, location, severity, duration, and when it started
        - You can re-record if you're not satisfied
        """)

    st.markdown("---")
    st.markdown("**Privacy Note:** Your voice recording is transcribed locally and not stored permanently.")
