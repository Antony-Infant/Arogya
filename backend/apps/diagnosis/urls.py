from django.urls import path
from .views import DiagnosisView, DiseaseInfoView, PredictionHistoryView

urlpatterns = [
    path('predict/', DiagnosisView.as_view(), name='diagnosis-predict'),
    path('disease/<str:disease_id>/', DiseaseInfoView.as_view(), name='disease-info'),
    path('history/', PredictionHistoryView.as_view(), name='prediction-history'),
]
