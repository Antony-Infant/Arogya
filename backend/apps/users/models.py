from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model with medical chatbot specific fields."""
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text='User phone number')
    preferred_language = models.CharField(max_length=10, default='en', help_text='Preferred language code')
    location_lat = models.FloatField(null=True, blank=True, help_text='Last known latitude')
    location_lng = models.FloatField(null=True, blank=True, help_text='Last known longitude')
    is_whatsapp_user = models.BooleanField(default=False, help_text='Registered via WhatsApp')
    whatsapp_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male','Male'),('female','Female'),('other','Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True, help_text='e.g. A+, B-, O+')
    existing_conditions = models.TextField(blank=True, help_text='Pre-existing medical conditions')
    allergies = models.TextField(blank=True, help_text='Known allergies')
    current_medications = models.TextField(blank=True, help_text='Current medications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.email})"
