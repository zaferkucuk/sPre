"""
URL configuration for analytics application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamStatisticsViewSet, MatchAnalyticsViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'team-statistics', TeamStatisticsViewSet, basename='team-statistics')
router.register(r'match-analytics', MatchAnalyticsViewSet, basename='match-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
