from django.contrib import admin
from .models import UserFeedback

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'prediction', 'is_correct', 'correct_disease', 'is_processed', 'created_at']
    list_filter = ['is_correct', 'is_processed']
    search_fields = ['correct_disease', 'feedback_text']
