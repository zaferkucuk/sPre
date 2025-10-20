"""
Transform API-Football responses to Django model instances.

This utility handles the conversion between API data formats
and our database models, ensuring data consistency.
"""

from typing import Dict, Optional
from datetime import datetime
from django.utils import timezone
from apps.matches.models import TeamStatistics, Fixture, Team, League, Season
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    Transforms API-Football data to database models.
    
    Handles:
    - API response parsing
    - Data validation
    - Model field mapping
    """
    
    @staticmethod
    def transform_standing_to_statistics(
        standing_data: Dict,
        team: Team,
        season: Season
    ) -> Dict:
        """
        Transform standings API response to TeamStatistics fields.
        
        Args:
            standing_data: Single team standing from API
            team: Team model instance
            season: Season model instance
        
        Returns:
            Dict ready for TeamStatistics.objects.update_or_create()
        """
        try:
            all_stats = standing_data['all']
            home_stats = standing_data['home']
            away_stats = standing_data['away']
            
            return {
                # Match statistics
                'matches_played': all_stats['played'],
                'wins': all_stats['win'],
                'draws': all_stats['draw'],
                'losses': all_stats['lose'],
                'goals_for': all_stats['goals']['for'],
                'goals_against': all_stats['goals']['against'],
                'points': standing_data['points'],
                
                # Home statistics
                'home_matches': home_stats['played'],
                'home_wins': home_stats['win'],
                'home_draws': home_stats['draw'],
                'home_losses': home_stats['lose'],
                'home_goals_for': home_stats['goals']['for'],
                'home_goals_against': home_stats['goals']['against'],
                
                # Away statistics
                'away_matches': away_stats['played'],
                'away_wins': away_stats['win'],
                'away_draws': away_stats['draw'],
                'away_losses': away_stats['lose'],
                'away_goals_for': away_stats['goals']['for'],
                'away_goals_against': away_stats['goals']['against'],
                
                # Form
                'form': standing_data.get('form', '')[:5],  # Last 5 matches
                
                # Metadata
                'data_source': 'api-football',
                'is_active': True
            }
            
        except (KeyError, TypeError) as e:
            logger.error(f"Error transforming standing data: {e}")
            return {}
    
    @staticmethod
    def transform_fixture_to_model(
        fixture_data: Dict,
        league: League,
        season: Season
    ) -> Optional[Dict]:
        """
        Transform fixture API response to Fixture model fields.
        
        Args:
            fixture_data: Single fixture from API
            league: League model instance
            season: Season model instance
        
        Returns:
            Dict ready for Fixture.objects.update_or_create() or None
        """
        try:
            fixture_info = fixture_data['fixture']
            teams_info = fixture_data['teams']
            goals_info = fixture_data['goals']
            score_info = fixture_data['score']
            
            # Get teams from database
            try:
                home_team = Team.objects.get(
                    external_id=str(teams_info['home']['id'])
                )
                away_team = Team.objects.get(
                    external_id=str(teams_info['away']['id'])
                )
            except Team.DoesNotExist:
                logger.warning(
                    f"Teams not found for fixture {fixture_info['id']}"
                )
                return None
            
            # Parse match date
            match_date = datetime.fromisoformat(
                fixture_info['date'].replace('Z', '+00:00')
            )
            
            # Map status
            status_map = {
                'TBD': 'SCHEDULED',
                'NS': 'SCHEDULED',
                'LIVE': 'IN_PLAY',
                '1H': 'IN_PLAY',
                'HT': 'IN_PLAY',
                '2H': 'IN_PLAY',
                'ET': 'IN_PLAY',
                'P': 'IN_PLAY',
                'FT': 'FINISHED',
                'AET': 'FINISHED',
                'PEN': 'FINISHED',
                'PST': 'POSTPONED',
                'CANC': 'CANCELLED',
                'ABD': 'CANCELLED',
                'AWA': 'CANCELLED',
                'WO': 'FINISHED',
            }
            
            api_status = fixture_info['status']['short']
            status = status_map.get(api_status, 'SCHEDULED')
            
            return {
                'league': league,
                'season': season,
                'home_team': home_team,
                'away_team': away_team,
                'match_date': match_date,
                'round': fixture_info.get('round', ''),
                'venue': fixture_info.get('venue', {}).get('name', ''),
                'status': status,
                'home_score': goals_info.get('home'),
                'away_score': goals_info.get('away'),
                'home_halftime_score': score_info.get('halftime', {}).get('home'),
                'away_halftime_score': score_info.get('halftime', {}).get('away'),
                'api_fixture_id': str(fixture_info['id'])
            }
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Error transforming fixture data: {e}")
            return None