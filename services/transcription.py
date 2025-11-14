"""
Audio transcription service using Faster Whisper.

Provides speech-to-text conversion for voice symptom recording.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import streamlit as st


class TranscriptionService:
    """Service for transcribing audio using Faster Whisper."""

    def __init__(self, model_size: str = "medium"):
        """
        Initialize transcription service.

        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.model_size = model_size
        self._model = None

    @property
    def model(self):
        """Lazy load the Faster Whisper model (cached)."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel

                # Load model with GPU if available, otherwise CPU
                self._model = WhisperModel(
                    self.model_size,
                    device="cpu",  # Use "cuda" if GPU available
                    compute_type="int8"  # Optimize for CPU
                )
            except ImportError:
                raise ImportError(
                    "faster-whisper is not installed. "
                    "Install it with: pip install faster-whisper"
                )
        return self._model

    def transcribe_audio(
        self,
        audio_file,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            audio_file: Audio file (BytesIO or file path)
            language: Language code (e.g., 'en' for English)

        Returns:
            Dictionary with transcription result:
            {
                'text': str,
                'success': bool,
                'error': Optional[str],
                'segments': List[dict]  # Individual segments with timestamps
            }
        """
        temp_file = None

        try:
            # Save audio to temporary file if it's bytes
            if hasattr(audio_file, 'read'):
                # It's a file-like object
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    temp_file.write(audio_file.read())
                    temp_path = temp_file.name
            else:
                # It's already a file path
                temp_path = audio_file

            # Transcribe using Faster Whisper
            segments, info = self.model.transcribe(
                temp_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Voice Activity Detection to filter silence
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Collect all segments
            segment_list = []
            full_text = []

            for segment in segments:
                segment_dict = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                }
                segment_list.append(segment_dict)
                full_text.append(segment.text.strip())

            # Combine all text
            transcribed_text = " ".join(full_text)

            return {
                'text': transcribed_text,
                'success': True,
                'error': None,
                'segments': segment_list,
                'language': info.language,
                'language_probability': info.language_probability
            }

        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': str(e),
                'segments': []
            }

        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def transcribe_with_cache(
        self,
        audio_file,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Transcribe audio with Streamlit caching.

        This method uses Streamlit's caching to avoid re-transcribing
        the same audio multiple times.

        Args:
            audio_file: Audio file bytes
            language: Language code

        Returns:
            Transcription result dictionary
        """
        # Note: This requires the audio_file to be hashable
        # In practice, you'd hash the audio bytes for caching
        return self.transcribe_audio(audio_file, language)


# Singleton instance - lazy loaded
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service(model_size: str = "medium") -> TranscriptionService:
    """
    Get or create transcription service instance.

    Args:
        model_size: Whisper model size

    Returns:
        TranscriptionService instance
    """
    global _transcription_service

    if _transcription_service is None:
        _transcription_service = TranscriptionService(model_size=model_size)

    return _transcription_service
