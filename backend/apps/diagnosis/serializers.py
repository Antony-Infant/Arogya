from rest_framework import serializers
from .models import DiseasePrediction, NearbyHospital

class NearbyHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbyHospital
        fields = ['id', 'name', 'hospital_type', 'latitude', 'longitude',
                  'phone', 'address', 'distance_km']

class DiseasePredictionSerializer(serializers.ModelSerializer):
    hospitals = NearbyHospitalSerializer(many=True, read_only=True)

    class Meta:
        model = DiseasePrediction
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']

class DiagnosisRequestSerializer(serializers.Serializer):
    symptoms = serializers.ListField(child=serializers.CharField(), min_length=1)
