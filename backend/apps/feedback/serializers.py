from rest_framework import serializers
from .models import UserFeedback


class UserFeedbackSerializer(serializers.ModelSerializer):
    # user is set automatically from request in the view - read only in responses
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserFeedback
        fields = [
            'id', 'user', 'prediction', 'is_correct',
            'correct_disease', 'feedback_text', 'is_processed', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'is_processed', 'created_at']

    def validate_prediction(self, value):
        """Give a clear error if prediction doesn't exist instead of a cryptic 400."""
        if value is None:
            raise serializers.ValidationError(
                "A valid prediction is required. The diagnosis may not have been saved yet."
            )
        return value