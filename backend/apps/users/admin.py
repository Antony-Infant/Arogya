from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone_number', 'preferred_language', 'gender', 'is_whatsapp_user', 'date_joined']
    list_filter = ['is_whatsapp_user', 'preferred_language', 'gender', 'is_active']
    search_fields = ['username', 'email', 'phone_number']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Medical Profile', {
            'fields': ('phone_number', 'date_of_birth', 'gender', 'blood_group',
                       'existing_conditions', 'allergies', 'current_medications')
        }),
        ('Chatbot Settings', {
            'fields': ('preferred_language', 'location_lat', 'location_lng',
                       'is_whatsapp_user', 'whatsapp_number', 'profile_image')
        }),
    )
