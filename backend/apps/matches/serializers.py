"""
Serializers for matches application.
"""

from rest_framework import serializers
from .models import Sport, League, Team, Match, Prediction


class SportSerializer(serializers.ModelSerializer):
    """Serializer for Sport model."""
    
    class Meta:
        model = Sport
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for League model."""
    
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    
    class Meta:
        model = League
        fields = [
            'id',
            'sport',
            'sport_name',
            'external_id',
            'name',
            'country',
            'season',
            'logo',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model."""
    
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id',
            'sport',
            'sport_name',
            'external_id',
            'name',
            'code',
            'country',
            'logo',
            'founded',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for Match model."""
    
    league_name = serializers.CharField(source='league.name', read_only=True)
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    is_finished = serializers.BooleanField(read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Match
        fields = [
            'id',
            'league',
            'league_name',
            'external_id',
            'home_team',
            'home_team_name',
            'away_team',
            'away_team_name',
            'match_date',
            'status',
            'home_score',
            'away_score',
            'venue',
            'referee',
            'statistics',
            'is_finished',
            'is_live',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for Prediction model."""
    
    match_info = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    predicted_winner = serializers.CharField(read_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'id',
            'match',
            'match_info',
            'user',
            'user_email',
            'prediction_type',
            'predicted_home_score',
            'predicted_away_score',
            'predicted_winner',
            'confidence',
            'reasoning',
            'is_correct',
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


class PredictionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating predictions."""
    
    class Meta:
        model = Prediction
        fields = [
            'match',
            'predicted_home_score',
            'predicted_away_score',
            'confidence',
            'reasoning',
        ]
    
    def validate(self, attrs):
        """Validate prediction data."""
        match = attrs.get('match')
        
        # Check if match has already started
        if match.is_live or match.is_finished:
            raise serializers.ValidationError(
                'Cannot create prediction for started or finished match.'
            )
        
        # Check if user already has a prediction for this match
        user = self.context['request'].user
        if Prediction.objects.filter(
            match=match,
            user=user,
            prediction_type=Prediction.PredictionType.USER
        ).exists():
            raise serializers.ValidationError(
                'You already have a prediction for this match.'
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create prediction with user and type."""
        validated_data['user'] = self.context['request'].user
        validated_data['prediction_type'] = Prediction.PredictionType.USER
        return super().create(validated_data)
