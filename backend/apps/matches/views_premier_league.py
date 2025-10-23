"""
Premier League specific views using Django ORM.

This module provides API endpoints specifically for Premier League data
using Django ORM for better performance and control.
"""

import logging
from datetime import datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q

from .models import Match, Team, League
from .serializers import MatchSerializer, TeamSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def premier_league_fixtures(request):
    """
    Get Premier League fixtures using Django ORM.
    
    GET /api/matches/premier-league/fixtures/
    
    Query Parameters:
        - status (str): Filter by match status (scheduled, live, finished) 
        - limit (int): Number of fixtures to return (default: 50, max: 200)
        - date_from (str): Filter fixtures from date (YYYY-MM-DD)
        - date_to (str): Filter fixtures to date (YYYY-MM-DD)
        - upcoming (bool): Get only upcoming matches (default: false)
    
    Returns:
        200: List of Premier League fixtures
        400: Invalid parameters
        404: Premier League not found
        500: Server error
        
    Example:
        GET /api/matches/premier-league/fixtures/?status=scheduled&limit=20
        
        Response:
        {
            "success": true,
            "count": 20,
            "league": {
                "id": 1,
                "name": "Premier League",
                "country": "England",
                "logo_url": "https://..."
            },
            "data": [
                {
                    "id": 1,
                    "external_id": "12345",
                    "home_team": {
                        "id": 1,
                        "name": "Manchester United",
                        "logo_url": "https://..."
                    },
                    "away_team": {
                        "id": 2,
                        "name": "Liverpool",
                        "logo_url": "https://..."
                    },
                    "match_date": "2024-10-25T15:00:00Z",
                    "venue": "Old Trafford",
                    "status": "scheduled",
                    "home_score": null,
                    "away_score": null,
                    "round": "Matchweek 9"
                }
            ]
        }
    """
    try:
        # Get query parameters
        match_status = request.query_params.get('status')
        limit = int(request.query_params.get('limit', 50))
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        upcoming = request.query_params.get('upcoming', 'false').lower() == 'true'
        
        # Validate and cap limit
        if limit > 200:
            limit = 200
        if limit < 1:
            limit = 50
        
        # Get Premier League
        premier_league = League.objects.filter(
            Q(external_id='39') | Q(name__icontains='Premier League')
        ).first()
        
        if not premier_league:
            return Response({
                'success': False,
                'error': 'Premier League not found. Please run: python manage.py fetch_premier_league_fixtures',
                'help': 'Run the management command to fetch fixtures first'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build query
        matches_query = Match.objects.filter(
            league=premier_league
        ).select_related(
            'home_team',
            'away_team',
            'league'
        )
        
        # Apply filters
        if match_status:
            valid_statuses = ['scheduled', 'live', 'finished']
            if match_status not in valid_statuses:
                return Response({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            matches_query = matches_query.filter(status=match_status)
        
        if upcoming:
            # Get only upcoming matches (from now onwards)
            matches_query = matches_query.filter(
                match_date__gte=datetime.now()
            )
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                matches_query = matches_query.filter(match_date__gte=date_from_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Invalid date_from format. Use YYYY-MM-DD (e.g., 2024-10-25)'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                matches_query = matches_query.filter(match_date__lte=date_to_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Invalid date_to format. Use YYYY-MM-DD (e.g., 2024-10-25)'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Order by date
        matches_query = matches_query.order_by('match_date')
        
        # Get total count before limiting
        total_count = matches_query.count()
        
        # Apply limit
        matches = matches_query[:limit]
        
        # Serialize data
        serializer = MatchSerializer(matches, many=True)
        
        logger.info(
            f"Fetched {len(serializer.data)} Premier League fixtures "
            f"(total available: {total_count})"
        )
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'total_available': total_count,
            'league': {
                'id': premier_league.id,
                'name': premier_league.name,
                'country': premier_league.country,
                'logo_url': premier_league.logo_url,
                'season': premier_league.season,
            },
            'filters': {
                'status': match_status,
                'date_from': date_from,
                'date_to': date_to,
                'upcoming': upcoming,
            },
            'data': serializer.data
        })
    
    except ValueError as e:
        logger.error(f"Invalid parameter value: {str(e)}")
        return Response({
            'success': False,
            'error': f'Invalid parameter value: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.exception("Error fetching Premier League fixtures")
        return Response({
            'success': False,
            'error': f'Failed to fetch fixtures: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def premier_league_teams(request):
    """
    Get all Premier League teams.
    
    GET /api/matches/premier-league/teams/
    
    Query Parameters:
        - search (str): Search teams by name
    
    Returns:
        200: List of Premier League teams
        404: Premier League not found
        500: Server error
        
    Example:
        GET /api/matches/premier-league/teams/?search=Manchester
        
        Response:
        {
            "success": true,
            "count": 2,
            "data": [
                {
                    "id": 1,
                    "name": "Manchester United",
                    "code": "MUN",
                    "country": "England",
                    "logo_url": "https://...",
                    "founded_year": 1878
                },
                {
                    "id": 2,
                    "name": "Manchester City",
                    "code": "MCI",
                    "country": "England",
                    "logo_url": "https://...",
                    "founded_year": 1880
                }
            ]
        }
    """
    try:
        # Get Premier League
        premier_league = League.objects.filter(
            Q(external_id='39') | Q(name__icontains='Premier League')
        ).first()
        
        if not premier_league:
            return Response({
                'success': False,
                'error': 'Premier League not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get teams
        teams_query = Team.objects.filter(
            leagues=premier_league
        ).distinct()
        
        # Apply search filter
        search = request.query_params.get('search')
        if search:
            teams_query = teams_query.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        # Order by name
        teams = teams_query.order_by('name')
        
        # Serialize data
        serializer = TeamSerializer(teams, many=True)
        
        logger.info(f"Fetched {len(serializer.data)} Premier League teams")
        
        return Response({
            'success': True,
            'count': len(serializer.data),
            'league': {
                'id': premier_league.id,
                'name': premier_league.name,
            },
            'data': serializer.data
        })
    
    except Exception as e:
        logger.exception("Error fetching Premier League teams")
        return Response({
            'success': False,
            'error': f'Failed to fetch teams: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def premier_league_stats(request):
    """
    Get Premier League statistics summary.
    
    GET /api/matches/premier-league/stats/
    
    Returns:
        200: Premier League statistics
        404: Premier League not found
        500: Server error
        
    Example:
        GET /api/matches/premier-league/stats/
        
        Response:
        {
            "success": true,
            "data": {
                "total_teams": 20,
                "total_matches": 380,
                "scheduled_matches": 200,
                "finished_matches": 150,
                "live_matches": 0,
                "season": "2024/2025"
            }
        }
    """
    try:
        # Get Premier League
        premier_league = League.objects.filter(
            Q(external_id='39') | Q(name__icontains='Premier League')
        ).first()
        
        if not premier_league:
            return Response({
                'success': False,
                'error': 'Premier League not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get statistics
        total_teams = Team.objects.filter(leagues=premier_league).distinct().count()
        
        matches_query = Match.objects.filter(league=premier_league)
        total_matches = matches_query.count()
        scheduled_matches = matches_query.filter(status='scheduled').count()
        finished_matches = matches_query.filter(status='finished').count()
        live_matches = matches_query.filter(status='live').count()
        
        logger.info("Fetched Premier League statistics")
        
        return Response({
            'success': True,
            'data': {
                'league': {
                    'id': premier_league.id,
                    'name': premier_league.name,
                    'country': premier_league.country,
                    'season': premier_league.season,
                },
                'statistics': {
                    'total_teams': total_teams,
                    'total_matches': total_matches,
                    'scheduled_matches': scheduled_matches,
                    'finished_matches': finished_matches,
                    'live_matches': live_matches,
                }
            }
        })
    
    except Exception as e:
        logger.exception("Error fetching Premier League statistics")
        return Response({
            'success': False,
            'error': f'Failed to fetch statistics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
