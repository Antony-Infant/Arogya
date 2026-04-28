from django.contrib import admin
from .models import DiseasePrediction, NearbyHospital

@admin.register(DiseasePrediction)
class DiseasePredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'disease_name', 'confidence_score', 'urgency_level', 'created_at']
    list_filter = ['urgency_level', 'created_at']
    search_fields = ['disease_name', 'user__username']
    readonly_fields = ['created_at']

@admin.register(NearbyHospital)
class NearbyHospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'hospital_type', 'prediction', 'distance_km']
