from django.db import models
from django.conf import settings

class DiseasePrediction(models.Model):
    """Stores each diagnosis prediction made by the system."""
    session = models.ForeignKey('chat.ChatSession', on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='predictions')

    # Core prediction
    disease_name = models.CharField(max_length=255)
    disease_id = models.CharField(max_length=20, blank=True)
    confidence_score = models.FloatField(help_text='0.0 to 1.0')
    causal_explanation = models.TextField(help_text='Why this disease was predicted')
    symptoms_matched = models.TextField(help_text='Pipe-separated symptoms that matched')
    causal_weights_used = models.TextField(blank=True, help_text='Causal weights applied')

    # Diagnosis details
    urgency_level = models.CharField(max_length=100, default='Routine')
    specialist_type = models.CharField(max_length=255, default='General Practitioner')
    recommended_medicines = models.TextField(blank=True)
    diet_recommendations = models.TextField(blank=True)
    home_remedies = models.TextField(blank=True)
    exercise_recommendations = models.TextField(blank=True)
    lifestyle_changes = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    when_to_see_doctor = models.TextField(blank=True)
    complications_if_untreated = models.TextField(blank=True)

    # Alternative predictions
    alternative_diseases = models.JSONField(default=list, blank=True,
        help_text='List of alternative diagnoses with confidence scores')

    # RAG context
    rag_context_used = models.TextField(blank=True)
    rag_relevance_score = models.FloatField(default=0.0)

    # LLM response
    full_llm_response = models.TextField(blank=True, help_text='Complete LLM generated response')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'disease_predictions'
        ordering = ['-created_at']
        verbose_name = 'Disease Prediction'
        verbose_name_plural = 'Disease Predictions'

    def __str__(self):
        return f"{self.disease_name} ({self.confidence_score:.0%}) for {self.user.username}"


class NearbyHospital(models.Model):
    """Stores nearby hospitals fetched for a prediction."""
    prediction = models.ForeignKey(DiseasePrediction, on_delete=models.CASCADE, related_name='hospitals')
    name = models.CharField(max_length=255)
    hospital_type = models.CharField(max_length=50, default='hospital')
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=500, blank=True)
    distance_km = models.FloatField(default=0.0)

    class Meta:
        db_table = 'nearby_hospitals'
        ordering = ['distance_km']

    def __str__(self):
        return f"{self.name} ({self.distance_km:.1f} km)"
