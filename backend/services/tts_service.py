"""
gTTS Service - Converts text to speech for voice output.
Supports multiple languages.
"""
from gtts import gTTS
import tempfile
import os
from django.conf import settings

class TTSService:
    def generate_audio(self, text: str, language: str = 'en') -> str:
        """Generate MP3 audio file from text."""
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tts_audio'), exist_ok=True)

        tts = gTTS(text=text, lang=language, slow=False)
        with tempfile.NamedTemporaryFile(
            suffix='.mp3', delete=False,
            dir=os.path.join(settings.MEDIA_ROOT, 'tts_audio')
        ) as tmp:
            tts.save(tmp.name)
            return tmp.name
