from rest_framework.views import APIView
from rest_framework import permissions
from django.http import HttpResponse
from apps.diagnosis.models import DiseasePrediction

class GeneratePDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, prediction_id):
        try:
            prediction = DiseasePrediction.objects.get(id=prediction_id, user=request.user)
        except DiseasePrediction.DoesNotExist:
            return HttpResponse('Prediction not found', status=404)

        from services.pdf_generator import generate_diagnosis_pdf
        pdf_buffer = generate_diagnosis_pdf(prediction, request.user)

        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        safe_name = prediction.disease_name.replace(' ', '_')
        response['Content-Disposition'] = f'attachment; filename="diagnosis_{safe_name}.pdf"'
        return response

class GenerateVoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        text = request.data.get('text', '')
        language = request.data.get('language', 'en')
        if not text:
            return HttpResponse('No text provided', status=400)

        from services.tts_service import TTSService
        tts = TTSService()
        audio_path = tts.generate_audio(text, language)

        with open(audio_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/mpeg')
            response['Content-Disposition'] = 'attachment; filename="response.mp3"'
            return response
