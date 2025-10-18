"""
Views for matches application.
"""

from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Sport, League, Team, Match, Prediction
from .serializers import (
    SportSerializer,
    LeagueSerializer,
    TeamSerializer,
    MatchSerializer,
    PredictionSerializer,
    PredictionCreateSerializer,
)


class SportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Sport model.
    
    GET /api/matches/sports/ - List all sports
    GET /api/matches/sports/{id}/ - Get sport detail
    """
    
    queryset = Sport.objects.filter(is_active=True)
    serializer_class = SportSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for League model.
    
    GET /api/matches/leagues/ - List all leagues
    GET /api/matches/leagues/{id}/ - Get league detail
    GET /api/matches/leagues/{id}/matches/ - Get matches for league
    """
    
    queryset = League.objects.filter(is_active=True).select_related('sport')
    serializer_class = LeagueSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sport', 'country', 'season']
    search_fields = ['name', 'country']
    ordering_fields = ['name', 'country', 'created_at']
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Get all matches for a specific league.
        
        GET /api/matches/leagues/{id}/matches/
        """
        league = self.get_object()
        matches = Match.objects.filter(league=league).select_related(
            'home_team', 'away_team'
        ).order_by('-match_date')
        
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Team model.
    
    GET /api/matches/teams/ - List all teams
    GET /api/matches/teams/{id}/ - Get team detail
    GET /api/matches/teams/{id}/matches/ - Get team matches
    """
    
    queryset = Team.objects.filter(is_active=True).select_related('sport')
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sport', 'country']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'country', 'created_at']
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Get all matches for a specific team.
        
        GET /api/matches/teams/{id}/matches/
        """
        team = self.get_object()
        
        # Get both home and away matches
        matches = Match.objects.filter(
            models.Q(home_team=team) | models.Q(away_team=team)
        ).select_related(
            'league', 'home_team', 'away_team'
        ).order_by('-match_date')
        
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Match model.
    
    GET /api/matches/matches/ - List all matches
    GET /api/matches/matches/{id}/ - Get match detail
    GET /api/matches/matches/upcoming/ - Get upcoming matches
    GET /api/matches/matches/live/ - Get live matches
    GET /api/matches/matches/finished/ - Get finished matches
    """
    
    queryset = Match.objects.select_related(
        'league', 'home_team', 'away_team'
    ).all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['league', 'status', 'home_team', 'away_team']
    search_fields = ['home_team__name', 'away_team__name', 'venue']
    ordering_fields = ['match_date', 'created_at']
    ordering = ['-match_date']
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming matches.
        
        GET /api/matches/matches/upcoming/
        """
        matches = self.queryset.filter(
            status=Match.Status.SCHEDULED,
            match_date__gte=timezone.now()
        ).order_by('match_date')[:20]
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        """
        Get live matches.
        
        GET /api/matches/matches/live/
        """
        matches = self.queryset.filter(
            status=Match.Status.LIVE
        ).order_by('match_date')
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def finished(self, request):
        """
        Get finished matches.
        
        GET /api/matches/matches/finished/
        """
        matches = self.queryset.filter(
            status=Match.Status.FINISHED
        ).order_by('-match_date')[:50]
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """
        Get all predictions for a specific match.
        
        GET /api/matches/matches/{id}/predictions/
        """
        match = self.get_object()
        predictions = Prediction.objects.filter(match=match).select_related('user')
        
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Prediction model.
    
    GET /api/matches/predictions/ - List user's predictions
    POST /api/matches/predictions/ - Create new prediction
    GET /api/matches/predictions/{id}/ - Get prediction detail
    PUT/PATCH /api/matches/predictions/{id}/ - Update prediction
    DELETE /api/matches/predictions/{id}/ - Delete prediction
    """
    
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['match', 'prediction_type', 'is_correct']
    ordering_fields = ['created_at', 'confidence']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return predictions for current user only.
        
        Returns:
            QuerySet: Filtered predictions
        """
        return Prediction.objects.filter(
            user=self.request.user
        ).select_related('match', 'match__home_team', 'match__away_team')
    
    def get_serializer_class(self):
        """
        Use different serializer for create operation.
        
        Returns:
            Serializer: Appropriate serializer class
        """
        if self.action == 'create':
            return PredictionCreateSerializer
        return PredictionSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get user's prediction statistics.
        
        GET /api/matches/predictions/stats/
        """
        predictions = self.get_queryset()
        
        total = predictions.count()
        correct = predictions.filter(is_correct=True).count()
        pending = predictions.filter(is_correct__isnull=True).count()
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return Response({
            'total_predictions': total,
            'correct_predictions': correct,
            'pending_predictions': pending,
            'accuracy': round(accuracy, 2)
        })
