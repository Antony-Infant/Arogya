"""
LLaMA 3.2 Vision Service - Analyzes medical images locally via Ollama.
Handles: prescriptions, lab reports, medicine tablets, skin conditions, X-rays.
No training needed - uses vision model's built-in medical knowledge.
"""
import ollama
import base64
import tempfile
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.model = settings.OLLAMA_VISION_MODEL

    def analyze_medical_image(self, image_file) -> str:
        """Analyze any medical image and return text description."""
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            for chunk in image_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Read and encode
            with open(tmp_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            response = self.client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': (
                        'You are a medical AI assistant analyzing a medical image. '
                        'Identify what type of medical image this is and provide detailed analysis:\n'
                        '- If PRESCRIPTION: Extract all medicine names, dosages, frequency, and duration.\n'
                        '- If LAB REPORT: Extract all test names, values, reference ranges, and flag abnormals.\n'
                        '- If MEDICINE TABLET/PACKAGING: Identify the medicine, its uses, and dosage form.\n'
                        '- If SKIN CONDITION/WOUND: Describe appearance, color, size, possible condition.\n'
                        '- If X-RAY/SCAN: Describe visible findings and possible abnormalities.\n'
                        '- If ANYTHING ELSE: Describe what you see and its medical relevance.\n'
                        'Be thorough and accurate. This information will be used for patient consultation.'
                    ),
                    'images': [image_data],
                }]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return f"Unable to analyze image: {str(e)[:200]}"
        finally:
            os.unlink(tmp_path)
