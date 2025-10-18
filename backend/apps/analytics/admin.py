"""
Admin configuration for analytics application.
"""

from django.contrib import admin
from .models import TeamStatistics, MatchAnalytics


@admin.register(TeamStatistics)
class TeamStatisticsAdmin(admin.ModelAdmin):
    """Admin interface for TeamStatistics model."""
    list_display = [
        'team',
        'season',
        'matches_played',
        'wins',
        'draws',
        'losses',
        'points',
        'goal_difference',
    ]
    list_filter = ['season', 'team__sport']
    search_fields = ['team__name', 'season']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MatchAnalytics)
class MatchAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for MatchAnalytics model."""
    list_display = [
        'match',
        'most_likely_outcome',
        'confidence_score',
        'model_version',
        'created_at',
    ]
    list_filter = ['model_version', 'created_at']
    search_fields = ['match__home_team__name', 'match__away_team__name']
    readonly_fields = ['created_at', 'updated_at']
