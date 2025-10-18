"""
Admin configuration for matches application.
"""

from django.contrib import admin
from .models import Sport, League, Team, Match, Prediction


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    """Admin interface for Sport model."""
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin interface for League model."""
    list_display = ['name', 'sport', 'country', 'season', 'is_active']
    list_filter = ['sport', 'country', 'is_active', 'created_at']
    search_fields = ['name', 'country', 'external_id']
    autocomplete_fields = ['sport']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model."""
    list_display = ['name', 'sport', 'country', 'code', 'is_active']
    list_filter = ['sport', 'country', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'external_id']
    autocomplete_fields = ['sport']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Admin interface for Match model."""
    list_display = [
        'home_team',
        'away_team',
        'league',
        'match_date',
        'status',
        'score_display',
    ]
    list_filter = ['status', 'league', 'match_date']
    search_fields = [
        'home_team__name',
        'away_team__name',
        'external_id',
    ]
    autocomplete_fields = ['league', 'home_team', 'away_team']
    date_hierarchy = 'match_date'
    
    def score_display(self, obj):
        """Display match score."""
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.home_score} - {obj.away_score}"
        return "-"
    score_display.short_description = 'Score'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Admin interface for Prediction model."""
    list_display = [
        'match',
        'user',
        'prediction_type',
        'predicted_score',
        'confidence',
        'is_correct',
        'created_at',
    ]
    list_filter = ['prediction_type', 'is_correct', 'created_at']
    search_fields = ['match__home_team__name', 'match__away_team__name', 'user__email']
    autocomplete_fields = ['match', 'user']
    
    def predicted_score(self, obj):
        """Display predicted score."""
        return f"{obj.predicted_home_score} - {obj.predicted_away_score}"
    predicted_score.short_description = 'Predicted Score'
