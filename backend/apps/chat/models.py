from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    """Represents a single chat conversation between user and AI."""
    CHANNEL_CHOICES = [('web', 'Web'), ('whatsapp', 'WhatsApp')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default='New Conversation')
    is_active = models.BooleanField(default=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='web')
    language = models.CharField(max_length=10, default='en')
    is_diagnosis_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'

    def __str__(self):
        return f"[{self.channel}] {self.user.username}: {self.title}"

    @property
    def message_count(self):
        return self.messages.count()

    @property
    def last_message_preview(self):
        last = self.messages.last()
        return last.content[:100] if last else None


class Message(models.Model):
    """Individual message in a chat session."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]
    INPUT_TYPE_CHOICES = [('text', 'Text'), ('voice', 'Voice'), ('image', 'Image')]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(help_text='Message content in English')
    input_type = models.CharField(max_length=10, choices=INPUT_TYPE_CHOICES, default='text')
    original_language = models.CharField(max_length=10, default='en')
    translated_content = models.TextField(blank=True, null=True, help_text='Original content if translated')
    audio_file = models.FileField(upload_to='chat_audio/', null=True, blank=True)
    image_file = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    image_analysis = models.TextField(blank=True, null=True, help_text='Vision AI analysis of uploaded image')
    metadata = models.JSONField(default=dict, blank=True, null=True, help_text='Additional message metadata')
    tts_audio_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}..."


class ExtractedSymptom(models.Model):
    """Symptoms extracted from conversation by LLM."""
    SEVERITY_CHOICES = [('mild','Mild'), ('moderate','Moderate'), ('severe','Severe')]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='extracted_symptoms')
    symptom_name = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True, help_text='e.g. 3 days, 1 week')
    body_location = models.CharField(max_length=100, blank=True, null=True, help_text='e.g. head, chest, left arm')
    additional_details = models.TextField(blank=True, null=True)
    extracted_from_message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.SET_NULL)
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'extracted_symptoms'
        ordering = ['-extracted_at']
        unique_together = ['session', 'symptom_name']  # Prevent duplicates

    def __str__(self):
        sev = f" ({self.severity})" if self.severity else ""
        dur = f" for {self.duration}" if self.duration else ""
        return f"{self.symptom_name}{sev}{dur}"
