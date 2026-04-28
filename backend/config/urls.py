from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT Auth
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # App endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/diagnosis/', include('apps.diagnosis.urls')),
    path('api/feedback/', include('apps.feedback.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/whatsapp/', include('apps.whatsapp.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
