from django.contrib import admin
from .models import ChatSession, Message, ExtractedSymptom

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'channel', 'language', 'is_active', 'message_count', 'created_at']
    list_filter = ['channel', 'is_active', 'language', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'input_type', 'content_preview', 'created_at']
    list_filter = ['role', 'input_type', 'created_at']
    search_fields = ['content']

    def content_preview(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content'

@admin.register(ExtractedSymptom)
class ExtractedSymptomAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'symptom_name', 'severity', 'duration', 'extracted_at']
    list_filter = ['severity', 'extracted_at']
    search_fields = ['symptom_name']
