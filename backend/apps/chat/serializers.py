from rest_framework import serializers
from .models import ChatSession, Message, ExtractedSymptom

class ExtractedSymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedSymptom
        fields = ['id', 'symptom_name', 'severity', 'duration', 'body_location',
                  'additional_details', 'extracted_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'input_type', 'original_language',
                  'translated_content', 'image_analysis', 'created_at']
        read_only_fields = ['id', 'created_at']

class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Full session with messages and symptoms."""
    messages = MessageSerializer(many=True, read_only=True)
    extracted_symptoms = ExtractedSymptomSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(source='messages.count', read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'is_active', 'channel', 'language',
                  'is_diagnosis_complete', 'message_count', 'messages', 'extracted_symptoms',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatSessionListSerializer(serializers.ModelSerializer):
    """Compact session for list view."""
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'is_active', 'channel', 'language',
                  'is_diagnosis_complete', 'message_count', 'last_message', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last = obj.messages.last()
        if last:
            return {'role': last.role, 'content': last.content[:100], 'created_at': last.created_at}
        return None

class SendMessageSerializer(serializers.Serializer):
    """Validates incoming chat message."""
    content = serializers.CharField(max_length=10000)
    input_type = serializers.ChoiceField(choices=['text', 'voice', 'image'], default='text')
