from django.urls import path
from .views import RegisterView, ProfileView, UpdateLocationView, MedicalProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('location/', UpdateLocationView.as_view(), name='update-location'),
    path('medical-profile/', MedicalProfileView.as_view(), name='medical-profile'),
]
