"""
URL configuration for matches application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SportViewSet,
    LeagueViewSet,
    TeamViewSet,
    MatchViewSet,
    PredictionViewSet,
)

app_name = 'matches'

router = DefaultRouter()
router.register(r'sports', SportViewSet, basename='sport')
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'predictions', PredictionViewSet, basename='prediction')

urlpatterns = [
    path('', include(router.urls)),
]
