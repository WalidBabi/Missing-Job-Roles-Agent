"""
URL configuration for Missing Job Roles AI Agent project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('roles_analyzer.urls')),
]

