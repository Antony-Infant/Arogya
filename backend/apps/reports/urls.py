from django.urls import path
from .views import GeneratePDFView, GenerateVoiceView

urlpatterns = [
    path('pdf/<int:prediction_id>/', GeneratePDFView.as_view(), name='generate-pdf'),
    path('voice/', GenerateVoiceView.as_view(), name='generate-voice'),
]
