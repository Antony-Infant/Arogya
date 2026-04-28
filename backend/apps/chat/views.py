"""Chat API Views - All endpoints return consistent response format."""
import logging
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import ChatSession, Message
from .serializers import (ChatSessionDetailSerializer, ChatSessionListSerializer, SendMessageSerializer)

logger = logging.getLogger(__name__)


def _process_and_respond(session, content, input_type, user, request):
    """Shared processing for all input types. Returns consistent dict."""
    try:
        from services.chat_engine import ChatEngine
        result = ChatEngine().process_message(session, content, input_type, user)
    except Exception as e:
        logger.error(f"ChatEngine: {e}", exc_info=True)
        result = {'message': 'Something went wrong. Please try again.', 'diagnosis': None,
                  'symptoms': [], 'follow_up_needed': False, 'hospitals': [], 'tts_url': None}

    Message.objects.create(session=session, role='assistant', content=result['message'],
                           metadata=result.get('diagnosis') or {})

    if session.messages.filter(role='user').count() == 1:
        session.title = content[:80]
        session.save(update_fields=['title'])

    return result


class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        return ChatSessionListSerializer if self.action == 'list' else ChatSessionDetailSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        session = self.get_object()
        ser = SendMessageSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        content = ser.validated_data['content']

        # Update user location if provided
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        if lat and lng:
            request.user.location_lat = float(lat)
            request.user.location_lng = float(lng)
            request.user.save(update_fields=['location_lat', 'location_lng'])

        Message.objects.create(session=session, role='user', content=content, input_type='text')
        result = _process_and_respond(session, content, 'text', request.user, request)

        return Response({
            'message': result['message'],
            'diagnosis': result.get('diagnosis'),
            'symptoms_extracted': result.get('symptoms', []),
            'follow_up_needed': result.get('follow_up_needed', False),
            'hospitals': result.get('hospitals', []),
            'tts_url': result.get('tts_url'),
        })

    @action(detail=True, methods=['post'], url_path='send-voice', parser_classes=[MultiPartParser])
    def send_voice(self, request, pk=None):
        session = self.get_object()
        audio = request.FILES.get('audio')
        if not audio:
            return Response({'error': 'No audio file'}, status=400)

        try:
            from services.whisper_service import WhisperService
            transcription = WhisperService().transcribe(audio)
        except Exception as e:
            logger.error(f"Whisper: {e}", exc_info=True)
            return Response({'error': 'Transcription failed'}, status=500)

        Message.objects.create(session=session, role='user', content=transcription,
                               input_type='voice', audio_file=audio)
        result = _process_and_respond(session, transcription, 'voice', request.user, request)

        return Response({
            'transcription': transcription,
            'message': result['message'],
            'diagnosis': result.get('diagnosis'),
            'hospitals': result.get('hospitals', []),
            'tts_url': result.get('tts_url'),
        })

    @action(detail=True, methods=['post'], url_path='send-image', parser_classes=[MultiPartParser])
    def send_image(self, request, pk=None):
        session = self.get_object()
        img = request.FILES.get('image')
        if not img:
            return Response({'error': 'No image'}, status=400)

        try:
            from services.vision_service import VisionService
            analysis = VisionService().analyze_medical_image(img)
        except Exception as e:
            analysis = f"Image analysis unavailable: {e}"

        Message.objects.create(session=session, role='user',
                               content=f"[Image: {img.name}]\n{analysis}",
                               input_type='image', image_file=img, image_analysis=analysis)
        result = _process_and_respond(session, analysis, 'image', request.user, request)

        return Response({
            'image_analysis': analysis,
            'message': result['message'],
            'diagnosis': result.get('diagnosis'),
            'hospitals': result.get('hospitals', []),
            'tts_url': result.get('tts_url'),
        })

    @action(detail=True, methods=['post'], url_path='send-pdf', parser_classes=[MultiPartParser])
    def send_pdf(self, request, pk=None):
        session = self.get_object()
        pdf = request.FILES.get('pdf')
        if not pdf:
            return Response({'error': 'No PDF file'}, status=400)

        try:
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                for chunk in pdf.chunks():
                    tmp.write(chunk)
                path = tmp.name
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
                text = "\n".join(page.extract_text() or '' for page in reader.pages)[:3000]
            except ImportError:
                text = "[Install pypdf: pip install pypdf]"
            finally:
                os.unlink(path)
        except Exception as e:
            text = f"PDF reading failed: {e}"

        content = f"[PDF: {pdf.name}]\n{text}" if text.strip() else "[Empty PDF]"
        Message.objects.create(session=session, role='user', content=content, input_type='text')
        result = _process_and_respond(session,
            f"Patient uploaded a medical document:\n{text[:2000]}", 'text', request.user, request)

        return Response({
            'pdf_text': text[:500],
            'message': result['message'],
            'diagnosis': result.get('diagnosis'),
            'hospitals': result.get('hospitals', []),
        })
