"""WhatsApp webhook - full feature parity with web: text, voice, image, hospitals, antifragile."""
import logging, requests, tempfile, os, base64
from rest_framework.views import APIView
from rest_framework import permissions
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.chat.models import ChatSession, Message

logger = logging.getLogger(__name__)
User = get_user_model()


class WhatsAppWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        body = request.data.get('Body', '').strip()
        from_number = request.data.get('From', '')
        num_media = int(request.data.get('NumMedia', 0))
        media_type = request.data.get('MediaContentType0', '')
        media_url = request.data.get('MediaUrl0', '')

        if not from_number:
            return HttpResponse(status=400)

        logger.info(f"WA from {from_number}: body={body[:50]} media={num_media}")

        # Get/create user
        clean = from_number.replace('whatsapp:', '').replace('+', '')
        user, _ = User.objects.get_or_create(
            whatsapp_number=from_number,
            defaults={'username': f'wa_{clean}', 'is_whatsapp_user': True})

        # Get/create session
        session = ChatSession.objects.filter(user=user, channel='whatsapp', is_active=True).first()
        if not session:
            session = ChatSession.objects.create(user=user, channel='whatsapp', title='WhatsApp')

        # Handle different input types
        try:
            from services.chat_engine import ChatEngine
            engine = ChatEngine()

            if num_media > 0 and media_url:
                if 'image' in media_type:
                    # IMAGE: Download and analyze with Vision
                    content = self._handle_image(media_url, body, session, engine, user)
                elif 'audio' in media_type or 'ogg' in media_type:
                    # VOICE: Download, transcribe, process
                    content = self._handle_voice(media_url, body, session, engine, user)
                elif 'pdf' in media_type:
                    # PDF: Download, extract text, process
                    content = self._handle_pdf(media_url, session, engine, user)
                else:
                    content = body or "I sent a file"
                    Message.objects.create(session=session, role='user', content=content)
                    result = engine.process_message(session, content, 'text', user)
                    content = result['message']
            else:
                # TEXT
                if not body:
                    return HttpResponse(status=200)
                Message.objects.create(session=session, role='user', content=body)
                result = engine.process_message(session, body, 'text', user)
                content = result['message']

                # Add hospitals if diagnosis was generated
                if result.get('hospitals'):
                    hosp_text = "\n\nNearby Hospitals:"
                    for h in result['hospitals'][:5]:
                        hosp_text += f"\n- {h['name']}"
                        if h.get('lat') and h.get('lng'):
                            hosp_text += f" (https://maps.google.com/?q={h['lat']},{h['lng']})"
                    content += hosp_text

                # Add feedback prompt after diagnosis
                if result.get('diagnosis'):
                    content += "\n\nWas this diagnosis helpful? Reply 'correct' or 'incorrect [disease name]'"

            Message.objects.create(session=session, role='assistant', content=content[:1500])

        except Exception as e:
            logger.error(f"WA error: {e}", exc_info=True)
            content = "I apologize, something went wrong. Please try again."

        self._send(from_number, content)

        # Handle feedback responses
        if body and session.is_diagnosis_complete:
            self._check_feedback(body, session, user)

        return HttpResponse(status=200)

    def _handle_image(self, url, caption, session, engine, user):
        try:
            img_data = self._download_media(url)
            if img_data:
                import ollama
                b64 = base64.b64encode(img_data).decode('utf-8')
                client = ollama.Client(host=settings.OLLAMA_BASE_URL)
                r = client.chat(model=settings.OLLAMA_VISION_MODEL,
                    messages=[{'role':'user','content':
                        'Analyze this medical image. Extract medicines, lab values, or describe conditions.',
                        'images':[b64]}])
                analysis = r['message']['content']
            else:
                analysis = "Could not download image."
        except Exception as e:
            analysis = f"Image analysis unavailable: {e}"

        msg_content = f"[Image] {caption}\nAnalysis: {analysis}" if caption else f"[Image]\n{analysis}"
        Message.objects.create(session=session, role='user', content=msg_content, input_type='image')
        result = engine.process_message(session, analysis, 'image', user)
        return result['message']

    def _handle_voice(self, url, caption, session, engine, user):
        try:
            audio_data = self._download_media(url)
            if audio_data:
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
                    f.write(audio_data)
                    path = f.name
                import whisper
                model = whisper.load_model('base')
                text = model.transcribe(path).get('text', '').strip()
                os.unlink(path)
            else:
                text = caption or "Voice message"
        except Exception as e:
            text = caption or f"Voice transcription failed: {e}"

        Message.objects.create(session=session, role='user', content=text, input_type='voice')
        result = engine.process_message(session, text, 'voice', user)
        return f"(Voice: {text[:100]})\n\n{result['message']}"

    def _handle_pdf(self, url, session, engine, user):
        try:
            pdf_data = self._download_media(url)
            if pdf_data:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    f.write(pdf_data)
                    path = f.name
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(p.extract_text() or '' for p in reader.pages)[:3000]
                os.unlink(path)
            else:
                text = "Could not download PDF."
        except Exception as e:
            text = f"PDF reading failed: {e}"

        Message.objects.create(session=session, role='user', content=f"[PDF]\n{text[:2000]}")
        result = engine.process_message(session, f"Patient uploaded medical document:\n{text}", 'text', user)
        return result['message']

    def _download_media(self, url):
        try:
            r = requests.get(url, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN), timeout=30)
            return r.content if r.ok else None
        except: return None

    def _check_feedback(self, body, session, user):
        """Handle 'correct' or 'incorrect [disease]' replies for antifragile system."""
        lower = body.lower().strip()
        if lower in ('correct', 'yes correct', 'accurate', 'right'):
            try:
                pred = session.predictions.order_by('-created_at').first()
                if pred:
                    from apps.feedback.models import UserFeedback
                    UserFeedback.objects.create(user=user, prediction=pred, is_correct=True)
                    logger.info(f"WA feedback: CORRECT for {pred.disease_name}")
            except: pass
        elif lower.startswith('incorrect') or lower.startswith('wrong'):
            try:
                correct_disease = body.split(' ', 1)[1].strip() if ' ' in body else ''
                pred = session.predictions.order_by('-created_at').first()
                if pred:
                    from apps.feedback.models import UserFeedback
                    UserFeedback.objects.create(
                        user=user, prediction=pred, is_correct=False,
                        correct_disease=correct_disease or 'Not specified')
                    logger.info(f"WA feedback: INCORRECT for {pred.disease_name}, correct={correct_disease}")
            except: pass

    def _send(self, to, message):
        if not settings.TWILIO_ACCOUNT_SID or 'your_sid' in settings.TWILIO_ACCOUNT_SID:
            return
        try:
            from twilio.rest import Client
            msg = message[:1590] if len(message) > 1600 else message
            Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN).messages.create(
                body=msg, from_=settings.TWILIO_WHATSAPP_NUMBER, to=to)
        except Exception as e:
            logger.error(f"Twilio: {e}")
