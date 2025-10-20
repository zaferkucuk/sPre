"""
Views for matches application.

This module provides API views for sports, leagues, teams, matches, and predictions
using Supabase as the data backend through the service layer.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.services import SupabaseService
from apps.core.exceptions import ResourceNotFoundError, SupabaseQueryError

logger = logging.getLogger(__name__)


# ==================== SPORTS VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def sports_list(request):
    """
    List all active sports.
    
    GET /api/matches/sports/
    
    Query Parameters:
        - active_only (bool): Filter by active status (default: True)
    
    Returns:
        200: List of sports
        500: Server error
    
    Example:
        GET /api/matches/sports/
        Response: [{"id": 1, "name": "Football", "slug": "football", ...}]
    """
    try:
        service = SupabaseService()
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        sports = service.get_all_sports(active_only=active_only)
        
        return Response({
            'success': True,
            'count': len(sports),
            'data': sports
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching sports: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch sports'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def sport_detail(request, sport_id):
    """
    Get details of a specific sport.
    
    GET /api/matches/sports/{id}/
    
    Returns:
        200: Sport details
        404: Sport not found
        500: Server error
    """
    try:
        service = SupabaseService()
        sport = service.get_sport_by_id(sport_id)
        
        return Response({
            'success': True,
            'data': sport
        })
    
    except ResourceNotFoundError:
        return Response({
            'success': False,
            'error': f'Sport with id {sport_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching sport {sport_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch sport details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== LEAGUES VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def leagues_list(request):
    """
    List all leagues, optionally filtered by sport.
    
    GET /api/matches/leagues/
    
    Query Parameters:
        - sport_id (int): Filter by sport ID
        - active_only (bool): Filter by active status (default: True)
    
    Returns:
        200: List of leagues
        500: Server error
    
    Example:
        GET /api/matches/leagues/?sport_id=1
        Response: [{"id": 1, "name": "Premier League", ...}]
    """
    try:
        service = SupabaseService()
        sport_id = request.query_params.get('sport_id')
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        
        if sport_id:
            leagues = service.get_leagues_by_sport(int(sport_id), active_only=active_only)
        else:
            # If no sport specified, get all sports and their leagues
            sports = service.get_all_sports(active_only=active_only)
            leagues = []
            for sport in sports:
                sport_leagues = service.get_leagues_by_sport(sport['id'], active_only=active_only)
                leagues.extend(sport_leagues)
        
        return Response({
            'success': True,
            'count': len(leagues),
            'data': leagues
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching leagues: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch leagues'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def league_detail(request, league_id):
    """
    Get details of a specific league.
    
    GET /api/matches/leagues/{id}/
    
    Returns:
        200: League details
        404: League not found
        500: Server error
    """
    try:
        service = SupabaseService()
        league = service.get_league_by_id(league_id)
        
        return Response({
            'success': True,
            'data': league
        })
    
    except ResourceNotFoundError:
        return Response({
            'success': False,
            'error': f'League with id {league_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching league {league_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch league details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== TEAMS VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def teams_list(request):
    """
    List all teams, optionally filtered by league.
    
    GET /api/matches/teams/
    
    Query Parameters:
        - league_id (int): Filter by league ID
        - search (str): Search teams by name
    
    Returns:
        200: List of teams
        500: Server error
    """
    try:
        service = SupabaseService()
        league_id = request.query_params.get('league_id')
        search = request.query_params.get('search')
        
        if search:
            teams = service.search_teams(search, league_id=int(league_id) if league_id else None)
        elif league_id:
            teams = service.get_teams_by_league(int(league_id))
        else:
            return Response({
                'success': False,
                'error': 'Please provide either league_id or search parameter'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'count': len(teams),
            'data': teams
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching teams: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch teams'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def team_detail(request, team_id):
    """
    Get details of a specific team.
    
    GET /api/matches/teams/{id}/
    
    Returns:
        200: Team details with related data
        404: Team not found
        500: Server error
    """
    try:
        service = SupabaseService()
        team = service.get_team_by_id(team_id)
        
        return Response({
            'success': True,
            'data': team
        })
    
    except ResourceNotFoundError:
        return Response({
            'success': False,
            'error': f'Team with id {team_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching team {team_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch team details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def team_matches(request, team_id):
    """
    Get all matches for a specific team.
    
    GET /api/matches/teams/{id}/matches/
    
    Query Parameters:
        - status (str): Filter by match status (scheduled, live, finished)
        - limit (int): Number of matches to return (default: 20)
    
    Returns:
        200: List of team matches
        500: Server error
    """
    try:
        service = SupabaseService()
        match_status = request.query_params.get('status')
        limit = int(request.query_params.get('limit', 20))
        
        matches = service.get_team_matches(team_id, status=match_status, limit=limit)
        
        return Response({
            'success': True,
            'count': len(matches),
            'data': matches
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching matches for team {team_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch team matches'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== MATCHES VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def matches_list(request):
    """
    List upcoming matches with optional filters.
    
    GET /api/matches/matches/
    
    Query Parameters:
        - sport_id (int): Filter by sport
        - league_id (int): Filter by league
        - limit (int): Number of matches to return (default: 50)
    
    Returns:
        200: List of upcoming matches
        500: Server error
    """
    try:
        service = SupabaseService()
        sport_id = request.query_params.get('sport_id')
        league_id = request.query_params.get('league_id')
        limit = int(request.query_params.get('limit', 50))
        
        matches = service.get_upcoming_matches(
            sport_id=int(sport_id) if sport_id else None,
            league_id=int(league_id) if league_id else None,
            limit=limit
        )
        
        return Response({
            'success': True,
            'count': len(matches),
            'data': matches
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching matches: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch matches'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def match_detail(request, match_id):
    """
    Get details of a specific match.
    
    GET /api/matches/matches/{id}/
    
    Returns:
        200: Match details with teams and league data
        404: Match not found
        500: Server error
    """
    try:
        service = SupabaseService()
        match = service.get_match_by_id(match_id)
        
        return Response({
            'success': True,
            'data': match
        })
    
    except ResourceNotFoundError:
        return Response({
            'success': False,
            'error': f'Match with id {match_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching match {match_id}: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch match details'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== PREDICTIONS VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prediction_create(request):
    """
    Create a new prediction for a match.
    
    POST /api/matches/predictions/
    
    Request Body:
        {
            "match_id": 1,
            "predicted_winner": "home",  // "home", "away", or "draw"
            "confidence_score": 0.85,
            "notes": "Optional prediction notes"
        }
    
    Returns:
        201: Prediction created successfully
        400: Invalid input
        500: Server error
    """
    try:
        # Validate required fields
        required_fields = ['match_id', 'predicted_winner', 'confidence_score']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate predicted_winner
        if request.data['predicted_winner'] not in ['home', 'away', 'draw']:
            return Response({
                'success': False,
                'error': 'predicted_winner must be "home", "away", or "draw"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate confidence_score
        confidence = float(request.data['confidence_score'])
        if not 0 <= confidence <= 1:
            return Response({
                'success': False,
                'error': 'confidence_score must be between 0 and 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        service = SupabaseService()
        prediction = service.create_prediction(
            user_id=str(request.user.id),
            match_id=int(request.data['match_id']),
            predicted_winner=request.data['predicted_winner'],
            confidence_score=confidence,
            notes=request.data.get('notes')
        )
        
        return Response({
            'success': True,
            'data': prediction
        }, status=status.HTTP_201_CREATED)
    
    except SupabaseQueryError as e:
        logger.error(f"Error creating prediction: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to create prediction'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predictions_list(request):
    """
    Get all predictions made by the authenticated user.
    
    GET /api/matches/predictions/
    
    Query Parameters:
        - match_id (int): Filter by specific match
    
    Returns:
        200: List of user predictions
        500: Server error
    """
    try:
        service = SupabaseService()
        match_id = request.query_params.get('match_id')
        
        predictions = service.get_user_predictions(
            user_id=str(request.user.id),
            match_id=int(match_id) if match_id else None
        )
        
        return Response({
            'success': True,
            'count': len(predictions),
            'data': predictions
        })
    
    except SupabaseQueryError as e:
        logger.error(f"Error fetching predictions: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch predictions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== HEALTH CHECK ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Check API and Supabase service health.
    
    GET /api/matches/health/
    
    Returns:
        200: Service is healthy
        503: Service is unhealthy
    """
    try:
        service = SupabaseService()
        health_status = service.health_check()
        
        if health_status['status'] == 'healthy':
            return Response({
                'success': True,
                'data': health_status
            })
        else:
            return Response({
                'success': False,
                'data': health_status
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'success': False,
            'error': 'Service unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
