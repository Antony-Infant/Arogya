from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'preferred_language', 'location_lat', 'location_lng', 'date_of_birth',
                  'gender', 'blood_group', 'existing_conditions', 'allergies',
                  'current_medications', 'is_whatsapp_user', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_whatsapp_user']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'phone_number',
                  'first_name', 'last_name', 'preferred_language', 'date_of_birth', 'gender']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UpdateLocationSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()

class MedicalProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating medical profile info."""
    class Meta:
        model = User
        fields = ['date_of_birth', 'gender', 'blood_group', 'existing_conditions',
                  'allergies', 'current_medications']
