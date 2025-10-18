"""
Views for datasources application.

This module provides API endpoints for data synchronization operations.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .sync_service import DataSyncService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_leagues(request):
    """
    Trigger league synchronization.
    
    POST /api/datasources/sync/leagues/
    
    Request Body:
        {
            "sport_id": 1
        }
    
    Returns:
        200: Sync completed successfully
        500: Sync failed
    """
    try:
        sport_id = request.data.get('sport_id', 1)
        
        sync_service = DataSyncService()
        result = sync_service.sync_leagues(sport_id=sport_id)
        sync_service.cleanup()
        
        return Response({
            'success': result['success'],
            'message': 'League sync completed',
            'data': result
        })
    
    except Exception as e:
        logger.error(f"League sync failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_teams(request):
    """
    Trigger team synchronization for a league.
    
    POST /api/datasources/sync/teams/
    
    Request Body:
        {
            "league_external_id": "39",
            "sport_id": 1
        }
    """
    try:
        league_id = request.data.get('league_external_id')
        sport_id = request.data.get('sport_id', 1)
        
        if not league_id:
            return Response({
                'success': False,
                'error': 'league_external_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sync_service = DataSyncService()
        result = sync_service.sync_teams(
            league_external_id=league_id,
            sport_id=sport_id
        )
        sync_service.cleanup()
        
        return Response({
            'success': result['success'],
            'message': 'Team sync completed',
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Team sync failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_matches(request):
    """
    Trigger match synchronization for a league.
    
    POST /api/datasources/sync/matches/
    
    Request Body:
        {
            "league_external_id": "39",
            "days_ahead": 30,
            "sport_id": 1
        }
    """
    try:
        league_id = request.data.get('league_external_id')
        days_ahead = request.data.get('days_ahead', 30)
        sport_id = request.data.get('sport_id', 1)
        
        if not league_id:
            return Response({
                'success': False,
                'error': 'league_external_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sync_service = DataSyncService()
        result = sync_service.sync_matches(
            league_external_id=league_id,
            days_ahead=days_ahead,
            sport_id=sport_id
        )
        sync_service.cleanup()
        
        return Response({
            'success': result['success'],
            'message': 'Match sync completed',
            'data': result
        })
    
    except Exception as e:
        logger.error(f"Match sync failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def sync_full(request):
    """
    Trigger full synchronization (teams + matches) for a league.
    
    POST /api/datasources/sync/full/
    
    Request Body:
        {
            "league_external_id": "39"
        }
    """
    try:
        league_id = request.data.get('league_external_id')
        
        if not league_id:
            return Response({
                'success': False,
                'error': 'league_external_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        sync_service = DataSyncService()
        results = sync_service.full_sync(league_external_id=league_id)
        sync_service.cleanup()
        
        return Response({
            'success': results['success'],
            'message': 'Full sync completed',
            'data': results
        })
    
    except Exception as e:
        logger.error(f"Full sync failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_status(request):
    """
    Get synchronization status and history.
    
    GET /api/datasources/sync/status/
    
    Query Parameters:
        - data_type (optional): Filter by data type (leagues, teams, matches)
    
    Returns:
        200: List of sync logs
    """
    try:
        data_type = request.query_params.get('data_type')
        
        sync_service = DataSyncService()
        logs = sync_service.get_sync_status(data_type=data_type)
        sync_service.cleanup()
        
        return Response({
            'success': True,
            'count': len(logs),
            'data': logs
        })
    
    except Exception as e:
        logger.error(f"Failed to get sync status: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
