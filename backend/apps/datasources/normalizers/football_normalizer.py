"""
Football data normalizer.

This module normalizes data from Football API to our database schema.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base_normalizer import BaseNormalizer
from apps.core.exceptions import DataParsingError

logger = logging.getLogger(__name__)


class FootballNormalizer(BaseNormalizer):
    """
    Normalizer for Football API data.
    
    Converts API-Football data format to our Supabase schema.
    
    Usage:
        normalizer = FootballNormalizer()
        league_data = normalizer.normalize_league(raw_api_data)
    """
    
    def __init__(self):
        """
        Initialize Football normalizer.
        """
        super().__init__(source_name="FootballAPI")
    
    def normalize_league(
        self,
        raw_data: Dict[str, Any],
        sport_id: int = 1
    ) -> Dict[str, Any]:
        """
        Normalize league data from Football API.
        
        Args:
            raw_data: Raw league data from Football API
            sport_id: Sport ID (default: 1 for football)
            
        Returns:
            Normalized league data for database
            
        Example:
            >>> raw = {'external_id': '39', 'name': 'Premier League', ...}
            >>> normalized = normalizer.normalize_league(raw)
            >>> print(normalized['name'])
            'Premier League'
        """
        try:
            # Validate required fields
            self.validate_required_fields(raw_data, ['external_id', 'name'])
            
            # Create slug from name
            slug = raw_data['name'].lower().replace(' ', '-').replace('/', '-')
            
            normalized = {
                'sport_id': sport_id,
                'name': self.safe_str(raw_data['name']),
                'slug': slug,
                'country': self.safe_str(raw_data.get('country')),
                'logo_url': self.safe_str(raw_data.get('logo_url')),
                'season': self.safe_str(raw_data.get('season')),
                'external_id': self.safe_str(raw_data['external_id']),
                'data_source': self.source_name,
                'is_active': True,
            }
            
            logger.debug(f"Normalized league: {normalized['name']}")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing league data: {str(e)}")
            raise DataParsingError(f"Failed to normalize league: {str(e)}") from e
    
    def normalize_team(
        self,
        raw_data: Dict[str, Any],
        sport_id: int = 1,
        league_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Normalize team data from Football API.
        
        Args:
            raw_data: Raw team data from Football API
            sport_id: Sport ID
            league_id: League ID in our database
            
        Returns:
            Normalized team data for database
        """
        try:
            # Validate required fields
            self.validate_required_fields(raw_data, ['external_id', 'name'])
            
            normalized = {
                'sport_id': sport_id,
                'league_id': league_id,
                'name': self.safe_str(raw_data['name']),
                'code': self.safe_str(raw_data.get('code')),
                'country': self.safe_str(raw_data.get('country')),
                'founded_year': self.safe_int(raw_data.get('founded_year')),
                'logo_url': self.safe_str(raw_data.get('logo_url')),
                'venue': self.safe_str(raw_data.get('venue')),
                'venue_city': self.safe_str(raw_data.get('venue_city')),
                'venue_capacity': self.safe_int(raw_data.get('venue_capacity')),
                'external_id': self.safe_str(raw_data['external_id']),
                'data_source': self.source_name,
                'is_active': True,
            }
            
            logger.debug(f"Normalized team: {normalized['name']}")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing team data: {str(e)}")
            raise DataParsingError(f"Failed to normalize team: {str(e)}") from e
    
    def normalize_match(
        self,
        raw_data: Dict[str, Any],
        sport_id: int = 1,
        league_id: Optional[int] = None,
        home_team_id: Optional[int] = None,
        away_team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Normalize match data from Football API.
        
        Args:
            raw_data: Raw match data from Football API
            sport_id: Sport ID
            league_id: League ID in our database
            home_team_id: Home team ID in our database
            away_team_id: Away team ID in our database
            
        Returns:
            Normalized match data for database
        """
        try:
            # Validate required fields
            self.validate_required_fields(
                raw_data,
                ['external_id', 'match_date', 'status']
            )
            
            # Parse match date
            match_date = raw_data.get('match_date')
            if isinstance(match_date, str):
                match_date = self.parse_datetime(match_date)
            
            if not match_date:
                raise DataParsingError("Invalid match_date")
            
            normalized = {
                'sport_id': sport_id,
                'league_id': league_id,
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'match_date': match_date,
                'venue': self.safe_str(raw_data.get('venue')),
                'status': self.safe_str(raw_data['status'], 'scheduled'),
                'home_score': self.safe_int(raw_data.get('home_score')),
                'away_score': self.safe_int(raw_data.get('away_score')),
                'external_id': self.safe_str(raw_data['external_id']),
                'data_source': self.source_name,
            }
            
            # Add optional fields
            if 'referee' in raw_data:
                normalized['referee'] = self.safe_str(raw_data['referee'])
            
            if 'round' in raw_data:
                normalized['round'] = self.safe_str(raw_data['round'])
            
            logger.debug(f"Normalized match: {normalized['external_id']}")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing match data: {str(e)}")
            raise DataParsingError(f"Failed to normalize match: {str(e)}") from e
    
    def normalize_match_statistics(
        self,
        raw_stats: Dict[str, Any],
        match_id: int
    ) -> Dict[str, Any]:
        """
        Normalize match statistics.
        
        Args:
            raw_stats: Raw statistics from Football API
            match_id: Match ID in our database
            
        Returns:
            Normalized statistics for database
        """
        try:
            home_stats = raw_stats.get('home', {})
            away_stats = raw_stats.get('away', {})
            
            normalized = {
                'match_id': match_id,
                # Possession
                'home_possession': self.safe_float(home_stats.get('ball_possession')),
                'away_possession': self.safe_float(away_stats.get('ball_possession')),
                # Shots
                'home_shots_total': self.safe_int(home_stats.get('total_shots')),
                'away_shots_total': self.safe_int(away_stats.get('total_shots')),
                'home_shots_on_target': self.safe_int(home_stats.get('shots_on_goal')),
                'away_shots_on_target': self.safe_int(away_stats.get('shots_on_goal')),
                # Passes
                'home_passes_total': self.safe_int(home_stats.get('total_passes')),
                'away_passes_total': self.safe_int(away_stats.get('total_passes')),
                'home_passes_accurate': self.safe_int(home_stats.get('passes_accurate')),
                'away_passes_accurate': self.safe_int(away_stats.get('passes_accurate')),
                # Fouls and Cards
                'home_fouls': self.safe_int(home_stats.get('fouls')),
                'away_fouls': self.safe_int(away_stats.get('fouls')),
                'home_yellow_cards': self.safe_int(home_stats.get('yellow_cards')),
                'away_yellow_cards': self.safe_int(away_stats.get('yellow_cards')),
                'home_red_cards': self.safe_int(home_stats.get('red_cards')),
                'away_red_cards': self.safe_int(away_stats.get('red_cards')),
                # Corners and Offsides
                'home_corners': self.safe_int(home_stats.get('corner_kicks')),
                'away_corners': self.safe_int(away_stats.get('corner_kicks')),
                'home_offsides': self.safe_int(home_stats.get('offsides')),
                'away_offsides': self.safe_int(away_stats.get('offsides')),
            }
            
            logger.debug(f"Normalized statistics for match {match_id}")
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing match statistics: {str(e)}")
            raise DataParsingError(f"Failed to normalize statistics: {str(e)}") from e
