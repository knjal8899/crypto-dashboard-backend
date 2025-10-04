"""
URL configuration for crypto_dashboard_backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/crypto/', include('apps.crypto.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
]
