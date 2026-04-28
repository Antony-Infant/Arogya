"""
Ollama LLM Service - Interface to LLaMA 3 running locally via Ollama.
All AI reasoning flows through this service.
"""
import ollama
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, model=None):
        self.model = model or settings.OLLAMA_MODEL
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> str:
        """Generate a response from LLaMA 3."""
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={'temperature': temperature, 'num_predict': 2048}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"I'm having trouble processing your request. Please try again. (Error: {str(e)[:100]})"

    def chat(self, messages: list, temperature: float = 0.3) -> str:
        """Multi-turn chat with conversation history."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={'temperature': temperature, 'num_predict': 2048}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return f"Error: {str(e)[:100]}"

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            self.client.list()
            return True
        except Exception:
            return False
