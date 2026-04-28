"""
LibreTranslate Service - Multilingual support running locally.
Translates user messages to English and responses back to user's language.
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class TranslateService:
    def __init__(self):
        self.base_url = settings.LIBRETRANSLATE_URL

    def translate(self, text: str, source: str = 'auto', target: str = 'en') -> str:
        """Translate text between languages."""
        try:
            response = requests.post(
                f"{self.base_url}/translate",
                json={'q': text, 'source': source, 'target': target},
                timeout=30,
            )
            if response.status_code == 200:
                return response.json().get('translatedText', text)
            logger.warning(f"Translation failed: {response.status_code}")
            return text
        except requests.exceptions.ConnectionError:
            logger.warning("LibreTranslate not available. Returning original text.")
            return text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def detect_language(self, text: str) -> str:
        """Detect language of input text."""
        try:
            response = requests.post(
                f"{self.base_url}/detect",
                json={'q': text},
                timeout=10,
            )
            if response.status_code == 200:
                detections = response.json()
                return detections[0]['language'] if detections else 'en'
            return 'en'
        except Exception:
            return 'en'

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/languages", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
