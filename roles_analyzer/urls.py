"""
URL routing for Roles Analyzer API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobRoleViewSet,
    EmployeeViewSet,
    AnalysisRunViewSet,
    MissingRoleViewSet,
    chatbot_message
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'job-roles', JobRoleViewSet, basename='jobrole')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'analysis-runs', AnalysisRunViewSet, basename='analysisrun')
router.register(r'missing-roles', MissingRoleViewSet, basename='missingrole')

urlpatterns = [
    path('', include(router.urls)),
    path('chatbot/', chatbot_message, name='chatbot'),
]

