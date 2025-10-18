"""
Views for analytics application.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import TeamStatistics, MatchAnalytics
from .serializers import TeamStatisticsSerializer, MatchAnalyticsSerializer


class TeamStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for TeamStatistics model.
    
    GET /api/analytics/team-statistics/ - List team statistics
    GET /api/analytics/team-statistics/{id}/ - Get statistics detail
    """
    
    queryset = TeamStatistics.objects.select_related('team').all()
    serializer_class = TeamStatisticsSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['team', 'season']
    ordering_fields = ['matches_played', 'wins', 'goals_scored', 'updated_at']
    ordering = ['-updated_at']


class MatchAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for MatchAnalytics model.
    
    GET /api/analytics/match-analytics/ - List match analytics
    GET /api/analytics/match-analytics/{id}/ - Get analytics detail
    """
    
    queryset = MatchAnalytics.objects.select_related(
        'match',
        'match__home_team',
        'match__away_team'
    ).all()
    serializer_class = MatchAnalyticsSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['match']
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-created_at']
