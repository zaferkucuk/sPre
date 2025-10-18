"""
Football API data fetcher.

This module implements a data fetcher for API-Football (RapidAPI).
Documentation: https://www.api-football.com/documentation-v3
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from django.conf import settings

from .base_fetcher import BaseFetcher
from apps.core.exceptions import DataFetchError, DataParsingError

logger = logging.getLogger(__name__)


class FootballAPIFetcher(BaseFetcher):
    """
    Data fetcher for API-Football service.
    
    Features:
    - Fetch leagues and competitions
    - Fetch teams and squads
    - Fetch fixtures (matches)
    - Fetch match details and statistics
    - Automatic caching
    - Rate limiting compliance
    
    Usage:
        fetcher = FootballAPIFetcher(api_key="your-key")
        leagues = fetcher.fetch_leagues(sport_id=1)
        matches = fetcher.fetch_matches(league_id=39)  # Premier League
    """
    
    # API-Football league IDs mapping
    LEAGUE_MAPPING = {
        'premier_league': 39,
        'la_liga': 140,
        'bundesliga': 78,
        'serie_a': 135,
        'ligue_1': 61,
        'champions_league': 2,
        'europa_league': 3,
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Football API fetcher.
        
        Args:
            api_key: API-Football API key (defaults to settings)
        """
        super().__init__(
            name="FootballAPI",
            base_url="https://v3.football.api-sports.io",
            rate_limit_calls=100,  # Free tier: 100 requests/day
            rate_limit_period=86400,  # 24 hours
            timeout=30
        )
        
        self.api_key = api_key or settings.FOOTBALL_API_KEY
        
        if not self.api_key:
            logger.warning("Football API key not configured")
        else:
            # Add API key to session headers
            self.session.headers.update({
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            })
            logger.info("Football API fetcher initialized with API key")
    
    def fetch_leagues(self, sport_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all football leagues.
        
        Args:
            sport_id: Sport ID (should be 1 for football)
            
        Returns:
            List of league dictionaries
            
        Example:
            >>> fetcher = FootballAPIFetcher()
            >>> leagues = fetcher.fetch_leagues(sport_id=1)
            >>> print(leagues[0]['name'])
            'Premier League'
        """
        # Check cache first
        cache_key = self._get_cache_key('leagues', sport_id)
        cached_data = self._get_cached(cache_key, ttl=86400)  # Cache for 24 hours
        
        if cached_data:
            return cached_data
        
        logger.info(f"Fetching leagues from Football API")
        
        try:
            # Fetch all leagues
            response = self._make_request(
                endpoint="/leagues",
                params={'current': 'true'}  # Only current season
            )
            
            if not response.get('response'):
                logger.warning("No leagues data in response")
                return []
            
            # Normalize data
            leagues = []
            for item in response['response']:
                league_data = item.get('league', {})
                country_data = item.get('country', {})
                seasons = item.get('seasons', [])
                
                # Get current season
                current_season = None
                for season in seasons:
                    if season.get('current', False):
                        current_season = season.get('year')
                        break
                
                leagues.append({
                    'external_id': str(league_data.get('id')),
                    'name': league_data.get('name'),
                    'country': country_data.get('name'),
                    'logo_url': league_data.get('logo'),
                    'season': str(current_season) if current_season else None,
                    'type': league_data.get('type'),  # League or Cup
                })
            
            # Cache the results
            self._set_cache(cache_key, leagues, ttl=86400)
            
            logger.info(f"Fetched {len(leagues)} leagues")
            return leagues
        
        except Exception as e:
            logger.error(f"Error fetching leagues: {str(e)}")
            raise DataFetchError(f"Failed to fetch leagues: {str(e)}") from e
    
    def fetch_teams(self, league_id: int, season: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch teams in a specific league.
        
        Args:
            league_id: External league ID from API-Football
            season: Season year (defaults to current year)
            
        Returns:
            List of team dictionaries
        """
        season = season or datetime.now().year
        
        # Check cache
        cache_key = self._get_cache_key(f'teams_league_{league_id}', season)
        cached_data = self._get_cached(cache_key, ttl=86400)
        
        if cached_data:
            return cached_data
        
        logger.info(f"Fetching teams for league {league_id}, season {season}")
        
        try:
            response = self._make_request(
                endpoint="/teams",
                params={
                    'league': league_id,
                    'season': season
                }
            )
            
            if not response.get('response'):
                logger.warning(f"No teams data for league {league_id}")
                return []
            
            # Normalize data
            teams = []
            for item in response['response']:
                team_data = item.get('team', {})
                venue_data = item.get('venue', {})
                
                teams.append({
                    'external_id': str(team_data.get('id')),
                    'name': team_data.get('name'),
                    'code': team_data.get('code'),
                    'country': team_data.get('country'),
                    'founded_year': team_data.get('founded'),
                    'logo_url': team_data.get('logo'),
                    'venue': venue_data.get('name'),
                    'venue_city': venue_data.get('city'),
                    'venue_capacity': venue_data.get('capacity'),
                })
            
            # Cache results
            self._set_cache(cache_key, teams, ttl=86400)
            
            logger.info(f"Fetched {len(teams)} teams")
            return teams
        
        except Exception as e:
            logger.error(f"Error fetching teams: {str(e)}")
            raise DataFetchError(f"Failed to fetch teams: {str(e)}") from e
    
    def fetch_matches(
        self,
        league_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        season: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch matches (fixtures) for a specific league.
        
        Args:
            league_id: External league ID
            from_date: Start date (defaults to today)
            to_date: End date (defaults to 30 days from now)
            season: Season year
            
        Returns:
            List of match dictionaries
        """
        from_date = from_date or datetime.now()
        to_date = to_date or (datetime.now() + timedelta(days=30))
        season = season or datetime.now().year
        
        # Check cache
        cache_key = self._get_cache_key(
            f'matches_league_{league_id}',
            f'{from_date.date()}_{to_date.date()}'
        )
        cached_data = self._get_cached(cache_key, ttl=3600)  # Cache for 1 hour
        
        if cached_data:
            return cached_data
        
        logger.info(
            f"Fetching matches for league {league_id} "
            f"from {from_date.date()} to {to_date.date()}"
        )
        
        try:
            response = self._make_request(
                endpoint="/fixtures",
                params={
                    'league': league_id,
                    'season': season,
                    'from': from_date.strftime('%Y-%m-%d'),
                    'to': to_date.strftime('%Y-%m-%d'),
                }
            )
            
            if not response.get('response'):
                logger.warning(f"No matches data for league {league_id}")
                return []
            
            # Normalize data
            matches = []
            for item in response['response']:
                fixture_data = item.get('fixture', {})
                league_data = item.get('league', {})
                teams_data = item.get('teams', {})
                goals_data = item.get('goals', {})
                score_data = item.get('score', {})
                
                # Parse match date
                match_date_str = fixture_data.get('date')
                match_date = None
                if match_date_str:
                    try:
                        match_date = datetime.fromisoformat(
                            match_date_str.replace('Z', '+00:00')
                        )
                    except (ValueError, AttributeError):
                        logger.warning(f"Invalid date format: {match_date_str}")
                
                # Determine status
                status_short = fixture_data.get('status', {}).get('short')
                if status_short in ['TBD', 'NS']:
                    status = 'scheduled'
                elif status_short in ['1H', '2H', 'HT', 'ET', 'P', 'LIVE']:
                    status = 'live'
                elif status_short in ['FT', 'AET', 'PEN']:
                    status = 'finished'
                else:
                    status = 'scheduled'
                
                matches.append({
                    'external_id': str(fixture_data.get('id')),
                    'home_team_external_id': str(teams_data.get('home', {}).get('id')),
                    'away_team_external_id': str(teams_data.get('away', {}).get('id')),
                    'home_team_name': teams_data.get('home', {}).get('name'),
                    'away_team_name': teams_data.get('away', {}).get('name'),
                    'match_date': match_date,
                    'venue': fixture_data.get('venue', {}).get('name'),
                    'venue_city': fixture_data.get('venue', {}).get('city'),
                    'status': status,
                    'home_score': goals_data.get('home'),
                    'away_score': goals_data.get('away'),
                    'halftime_home': score_data.get('halftime', {}).get('home'),
                    'halftime_away': score_data.get('halftime', {}).get('away'),
                    'fulltime_home': score_data.get('fulltime', {}).get('home'),
                    'fulltime_away': score_data.get('fulltime', {}).get('away'),
                    'referee': fixture_data.get('referee'),
                    'round': league_data.get('round'),
                })
            
            # Cache results
            self._set_cache(cache_key, matches, ttl=3600)
            
            logger.info(f"Fetched {len(matches)} matches")
            return matches
        
        except Exception as e:
            logger.error(f"Error fetching matches: {str(e)}")
            raise DataFetchError(f"Failed to fetch matches: {str(e)}") from e
    
    def fetch_match_details(self, match_id: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific match.
        
        Args:
            match_id: External match ID from API-Football
            
        Returns:
            Match details dictionary with statistics
        """
        # Check cache
        cache_key = self._get_cache_key('match_details', match_id)
        cached_data = self._get_cached(cache_key, ttl=1800)  # Cache for 30 minutes
        
        if cached_data:
            return cached_data
        
        logger.info(f"Fetching details for match {match_id}")
        
        try:
            # Fetch fixture details
            fixture_response = self._make_request(
                endpoint="/fixtures",
                params={'id': match_id}
            )
            
            # Fetch statistics
            stats_response = self._make_request(
                endpoint="/fixtures/statistics",
                params={'fixture': match_id}
            )
            
            if not fixture_response.get('response'):
                raise DataFetchError(f"Match {match_id} not found")
            
            fixture_data = fixture_response['response'][0]
            statistics = stats_response.get('response', [])
            
            # Normalize statistics
            normalized_stats = self._normalize_match_statistics(statistics)
            
            # Combine data
            match_details = {
                'external_id': match_id,
                'fixture_data': fixture_data,
                'statistics': normalized_stats,
            }
            
            # Cache results
            self._set_cache(cache_key, match_details, ttl=1800)
            
            logger.info(f"Fetched details for match {match_id}")
            return match_details
        
        except Exception as e:
            logger.error(f"Error fetching match details: {str(e)}")
            raise DataFetchError(f"Failed to fetch match details: {str(e)}") from e
    
    def _normalize_match_statistics(
        self,
        statistics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Normalize match statistics to a consistent format.
        
        Args:
            statistics: Raw statistics data from API
            
        Returns:
            Normalized statistics dictionary
        """
        normalized = {
            'home': {},
            'away': {}
        }
        
        for team_stats in statistics:
            team_name = team_stats.get('team', {}).get('name')
            is_home = team_stats.get('team', {}).get('id') == statistics[0].get('team', {}).get('id')
            key = 'home' if is_home else 'away'
            
            stats_dict = {}
            for stat in team_stats.get('statistics', []):
                stat_type = stat.get('type')
                stat_value = stat.get('value')
                
                if stat_type and stat_value is not None:
                    # Convert percentage strings to floats
                    if isinstance(stat_value, str) and '%' in stat_value:
                        try:
                            stat_value = float(stat_value.replace('%', ''))
                        except ValueError:
                            pass
                    
                    stats_dict[stat_type.lower().replace(' ', '_')] = stat_value
            
            normalized[key] = stats_dict
        
        return normalized
    
    def get_league_id(self, league_slug: str) -> Optional[int]:
        """
        Get API-Football league ID from slug.
        
        Args:
            league_slug: League slug (e.g., 'premier_league')
            
        Returns:
            League ID or None
        """
        return self.LEAGUE_MAPPING.get(league_slug)
