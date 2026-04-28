"""
OpenAI Whisper Service - Converts speech to text locally.
Handles webm, ogg, wav, mp4, mp3 from browser recordings.
"""
import whisper
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

class WhisperService:
    _model = None

    def __init__(self, model_size='base'):
        if WhisperService._model is None:
            logger.info(f"Loading Whisper model: {model_size}")
            WhisperService._model = whisper.load_model(model_size)

    def transcribe(self, audio_file, language=None) -> str:
        """Transcribe audio file to text. Detects format from filename."""
        # Detect the actual extension from the uploaded filename
        name = getattr(audio_file, 'name', 'recording.webm') or 'recording.webm'
        ext = os.path.splitext(name)[-1].lower()
        if not ext or ext not in ['.wav', '.mp3', '.mp4', '.webm', '.ogg', '.m4a', '.flac']:
            ext = '.webm'  # Browser default

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            options = {'fp16': False}  # CPU-safe
            if language:
                options['language'] = language
            result = self._model.transcribe(tmp_path, **options)
            text = result['text'].strip()
            logger.info(f"Transcribed ({result.get('language','?')}): {text[:100]}")
            return text if text else "Could not understand the audio. Please try again."
        except Exception as e:
            logger.error(f"Whisper error: {e}", exc_info=True)
            return f"Transcription failed: {str(e)[:100]}"
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
