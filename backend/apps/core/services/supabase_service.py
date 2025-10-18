"""
Supabase service layer.

This module provides high-level business logic methods
for interacting with Supabase database.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from apps.core.services.supabase_client import get_supabase_client
from apps.core.exceptions import (
    SupabaseQueryError,
    ResourceNotFoundError,
)
from apps.core.decorators import handle_supabase_errors

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    High-level service for Supabase operations.
    
    This service provides clean, business-logic focused methods
    for common database operations with proper error handling.
    
    Usage:
        service = SupabaseService()
        sports = service.get_all_sports()
    """
    
    def __init__(self):
        """
        Initialize the service with Supabase client.
        """
        self.client = get_supabase_client()
    
    # ==================== SPORTS ====================
    
    @handle_supabase_errors
    def get_all_sports(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all sports from database.
        
        Args:
            active_only: If True, return only active sports
            
        Returns:
            List of sport dictionaries
            
        Example:
            >>> service = SupabaseService()
            >>> sports = service.get_all_sports()
            >>> for sport in sports:
            ...     print(sport['name'])
        """
        query = self.client.table('sports').select('*')
        
        if active_only:
            query = query.eq('is_active', True)
        
        response = query.order('name').execute()
        logger.info(f"Retrieved {len(response.data)} sports")
        return response.data
    
    @handle_supabase_errors
    def get_sport_by_id(self, sport_id: int) -> Dict[str, Any]:
        """
        Get a specific sport by ID.
        
        Args:
            sport_id: ID of the sport
            
        Returns:
            Sport dictionary
            
        Raises:
            ResourceNotFoundError: If sport not found
        """
        response = self.client.table('sports').select('*').eq('id', sport_id).execute()
        
        if not response.data:
            raise ResourceNotFoundError(f"Sport with id {sport_id} not found")
        
        return response.data[0]
    
    # ==================== LEAGUES ====================
    
    @handle_supabase_errors
    def get_leagues_by_sport(self, sport_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all leagues for a specific sport.
        
        Args:
            sport_id: ID of the sport
            active_only: If True, return only active leagues
            
        Returns:
            List of league dictionaries
        """
        query = self.client.table('leagues').select('*').eq('sport_id', sport_id)
        
        if active_only:
            query = query.eq('is_active', True)
        
        response = query.order('name').execute()
        logger.info(f"Retrieved {len(response.data)} leagues for sport {sport_id}")
        return response.data
    
    @handle_supabase_errors
    def get_league_by_id(self, league_id: int) -> Dict[str, Any]:
        """
        Get a specific league by ID.
        
        Args:
            league_id: ID of the league
            
        Returns:
            League dictionary
            
        Raises:
            ResourceNotFoundError: If league not found
        """
        response = self.client.table('leagues').select('*').eq('id', league_id).execute()
        
        if not response.data:
            raise ResourceNotFoundError(f"League with id {league_id} not found")
        
        return response.data[0]
    
    # ==================== TEAMS ====================
    
    @handle_supabase_errors
    def get_teams_by_league(self, league_id: int) -> List[Dict[str, Any]]:
        """
        Get all teams in a specific league.
        
        Args:
            league_id: ID of the league
            
        Returns:
            List of team dictionaries
        """
        response = (
            self.client.table('teams')
            .select('*')
            .eq('league_id', league_id)
            .order('name')
            .execute()
        )
        logger.info(f"Retrieved {len(response.data)} teams for league {league_id}")
        return response.data
    
    @handle_supabase_errors
    def get_team_by_id(self, team_id: int) -> Dict[str, Any]:
        """
        Get a specific team by ID.
        
        Args:
            team_id: ID of the team
            
        Returns:
            Team dictionary with related data
            
        Raises:
            ResourceNotFoundError: If team not found
        """
        response = (
            self.client.table('teams')
            .select('*, league:leagues(*), sport:sports(*)')
            .eq('id', team_id)
            .execute()
        )
        
        if not response.data:
            raise ResourceNotFoundError(f"Team with id {team_id} not found")
        
        return response.data[0]
    
    @handle_supabase_errors
    def search_teams(self, query: str, league_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search teams by name.
        
        Args:
            query: Search query string
            league_id: Optional league ID to filter by
            
        Returns:
            List of matching team dictionaries
        """
        supabase_query = (
            self.client.table('teams')
            .select('*')
            .ilike('name', f'%{query}%')
        )
        
        if league_id:
            supabase_query = supabase_query.eq('league_id', league_id)
        
        response = supabase_query.order('name').limit(20).execute()
        logger.info(f"Found {len(response.data)} teams matching '{query}'")
        return response.data
    
    # ==================== MATCHES ====================
    
    @handle_supabase_errors
    def get_upcoming_matches(
        self,
        sport_id: Optional[int] = None,
        league_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming matches.
        
        Args:
            sport_id: Optional sport ID to filter by
            league_id: Optional league ID to filter by
            limit: Maximum number of matches to return
            
        Returns:
            List of match dictionaries with team data
        """
        query = (
            self.client.table('matches')
            .select('*, home_team:teams!matches_home_team_id_fkey(*), away_team:teams!matches_away_team_id_fkey(*), league:leagues(*)')
            .gte('match_date', datetime.now().isoformat())
            .eq('status', 'scheduled')
        )
        
        if sport_id:
            query = query.eq('sport_id', sport_id)
        
        if league_id:
            query = query.eq('league_id', league_id)
        
        response = query.order('match_date').limit(limit).execute()
        logger.info(f"Retrieved {len(response.data)} upcoming matches")
        return response.data
    
    @handle_supabase_errors
    def get_match_by_id(self, match_id: int) -> Dict[str, Any]:
        """
        Get a specific match by ID with all related data.
        
        Args:
            match_id: ID of the match
            
        Returns:
            Match dictionary with teams, league, and sport data
            
        Raises:
            ResourceNotFoundError: If match not found
        """
        response = (
            self.client.table('matches')
            .select(
                '*, '
                'home_team:teams!matches_home_team_id_fkey(*, league:leagues(*, sport:sports(*))), '
                'away_team:teams!matches_away_team_id_fkey(*, league:leagues(*, sport:sports(*))), '
                'league:leagues(*, sport:sports(*))'
            )
            .eq('id', match_id)
            .execute()
        )
        
        if not response.data:
            raise ResourceNotFoundError(f"Match with id {match_id} not found")
        
        return response.data[0]
    
    @handle_supabase_errors
    def get_team_matches(
        self,
        team_id: int,
        status: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get matches for a specific team.
        
        Args:
            team_id: ID of the team
            status: Optional status filter (scheduled, live, finished)
            limit: Maximum number of matches to return
            
        Returns:
            List of match dictionaries
        """
        # Supabase doesn't support OR directly, so we need to use RPC or multiple queries
        # For now, we'll do two queries and merge
        home_query = (
            self.client.table('matches')
            .select('*, home_team:teams!matches_home_team_id_fkey(*), away_team:teams!matches_away_team_id_fkey(*)')
            .eq('home_team_id', team_id)
        )
        
        away_query = (
            self.client.table('matches')
            .select('*, home_team:teams!matches_home_team_id_fkey(*), away_team:teams!matches_away_team_id_fkey(*)')
            .eq('away_team_id', team_id)
        )
        
        if status:
            home_query = home_query.eq('status', status)
            away_query = away_query.eq('status', status)
        
        home_response = home_query.order('match_date', desc=True).limit(limit).execute()
        away_response = away_query.order('match_date', desc=True).limit(limit).execute()
        
        # Merge and sort by date
        all_matches = home_response.data + away_response.data
        all_matches.sort(key=lambda x: x['match_date'], reverse=True)
        
        logger.info(f"Retrieved {len(all_matches)} matches for team {team_id}")
        return all_matches[:limit]
    
    # ==================== PREDICTIONS ====================
    
    @handle_supabase_errors
    def create_prediction(
        self,
        user_id: str,
        match_id: int,
        predicted_winner: str,
        confidence_score: float,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new prediction.
        
        Args:
            user_id: ID of the user making the prediction
            match_id: ID of the match
            predicted_winner: 'home', 'away', or 'draw'
            confidence_score: Confidence score (0-1)
            notes: Optional notes about the prediction
            
        Returns:
            Created prediction dictionary
        """
        prediction_data = {
            'user_id': user_id,
            'match_id': match_id,
            'predicted_winner': predicted_winner,
            'confidence_score': confidence_score,
            'notes': notes,
        }
        
        response = self.client.table('predictions').insert(prediction_data).execute()
        logger.info(f"Created prediction for match {match_id} by user {user_id}")
        return response.data[0]
    
    @handle_supabase_errors
    def get_user_predictions(
        self,
        user_id: str,
        match_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get predictions made by a user.
        
        Args:
            user_id: ID of the user
            match_id: Optional match ID to filter by
            
        Returns:
            List of prediction dictionaries
        """
        query = (
            self.client.table('predictions')
            .select('*, match:matches(*, home_team:teams(*), away_team:teams(*))')
            .eq('user_id', user_id)
        )
        
        if match_id:
            query = query.eq('match_id', match_id)
        
        response = query.order('created_at', desc=True).execute()
        logger.info(f"Retrieved {len(response.data)} predictions for user {user_id}")
        return response.data
    
    # ==================== UTILITY METHODS ====================
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health.
        
        Returns:
            Health status dictionary
        """
        is_healthy = self.client.health_check()
        
        return {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'service': 'supabase',
            'timestamp': datetime.now().isoformat(),
        }
