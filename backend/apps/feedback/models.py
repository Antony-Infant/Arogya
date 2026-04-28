from django.db import models
from django.conf import settings


class UserFeedback(models.Model):
    """Antifragile feedback - stores correct/incorrect with optional disease correction."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    prediction = models.ForeignKey('diagnosis.DiseasePrediction', on_delete=models.CASCADE, related_name='feedbacks')
    is_correct = models.BooleanField(help_text='Was the diagnosis correct?')
    correct_disease = models.CharField(max_length=255, blank=True, null=True,
        help_text='If wrong, what was the actual disease?')
    feedback_text = models.TextField(blank=True, null=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_feedback'
        ordering = ['-created_at']

    def __str__(self):
        status = "Correct" if self.is_correct else f"Wrong (actual: {self.correct_disease})"
        return f"Feedback #{self.id}: {self.prediction.disease_name} - {status}"
