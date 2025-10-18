"""
Serializers for analytics application.
"""

from rest_framework import serializers
from .models import TeamStatistics, MatchAnalytics


class TeamStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for TeamStatistics model."""
    
    team_name = serializers.CharField(source='team.name', read_only=True)
    points = serializers.IntegerField(read_only=True)
    goal_difference = serializers.IntegerField(read_only=True)
    win_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = TeamStatistics
        fields = [
            'id',
            'team',
            'team_name',
            'season',
            'matches_played',
            'wins',
            'draws',
            'losses',
            'points',
            'goals_scored',
            'goals_conceded',
            'goal_difference',
            'clean_sheets',
            'win_rate',
            'form',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MatchAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for MatchAnalytics model."""
    
    match_info = serializers.SerializerMethodField()
    most_likely_outcome = serializers.CharField(read_only=True)
    
    class Meta:
        model = MatchAnalytics
        fields = [
            'id',
            'match',
            'match_info',
            'home_win_probability',
            'draw_probability',
            'away_win_probability',
            'expected_goals_home',
            'expected_goals_away',
            'confidence_score',
            'most_likely_outcome',
            'factors',
            'model_version',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_match_info(self, obj):
        """Get basic match information."""
        return {
            'home_team': obj.match.home_team.name,
            'away_team': obj.match.away_team.name,
            'match_date': obj.match.match_date,
            'status': obj.match.status,
        }
