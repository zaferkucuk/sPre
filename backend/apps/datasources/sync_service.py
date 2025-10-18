"""
Data synchronization service.

This module manages the synchronization of data from external sources
to the Supabase database.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from apps.core.services import SupabaseService
from apps.core.exceptions import DataFetchError, DataParsingError
from .fetchers import FootballAPIFetcher
from .normalizers import FootballNormalizer

logger = logging.getLogger(__name__)


class DataSyncService:
    """
    Service for synchronizing external data to database.
    
    This service coordinates:
    - Fetching data from external APIs
    - Normalizing data to database schema
    - Upserting data to Supabase
    - Tracking sync status
    - Handling conflicts and errors
    
    Usage:
        sync_service = DataSyncService()
        result = sync_service.sync_leagues(sport_id=1)
        print(f"Synced {result['created']} leagues")
    """
    
    def __init__(self):
        """
        Initialize the sync service.
        """
        self.supabase = SupabaseService()
        self.fetcher = FootballAPIFetcher()
        self.normalizer = FootballNormalizer()
        logger.info("DataSyncService initialized")
    
    def sync_leagues(self, sport_id: int = 1) -> Dict[str, Any]:
        """
        Sync leagues from external API to database.
        
        Args:
            sport_id: Sport ID to sync leagues for
            
        Returns:
            Dictionary with sync results
        """
        logger.info(f"Starting league sync for sport {sport_id}")
        
        result = {
            'success': False,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Fetch leagues from API
            raw_leagues = self.fetcher.fetch_leagues(sport_id=sport_id)
            logger.info(f"Fetched {len(raw_leagues)} leagues from API")
            
            # Process each league
            for raw_league in raw_leagues:
                try:
                    # Normalize data
                    normalized = self.normalizer.normalize_league(
                        raw_league,
                        sport_id=sport_id
                    )
                    
                    # Check if league exists
                    existing = self._find_league_by_external_id(
                        normalized['external_id']
                    )
                    
                    if existing:
                        # Update existing league
                        self._update_league(existing['id'], normalized)
                        result['updated'] += 1
                        logger.debug(f"Updated league: {normalized['name']}")
                    else:
                        # Create new league
                        self._create_league(normalized)
                        result['created'] += 1
                        logger.debug(f"Created league: {normalized['name']}")
                
                except Exception as e:
                    result['errors'] += 1
                    error_msg = f"Error processing league: {str(e)}"
                    result['error_messages'].append(error_msg)
                    logger.error(error_msg)
            
            result['success'] = result['errors'] == 0
            
            # Log sync result
            self._log_sync(
                data_type='leagues',
                total_records=len(raw_leagues),
                successful_records=result['created'] + result['updated'],
                failed_records=result['errors']
            )
            
            logger.info(
                f"League sync completed: "
                f"created={result['created']}, "
                f"updated={result['updated']}, "
                f"errors={result['errors']}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"League sync failed: {str(e)}")
            result['error_messages'].append(str(e))
            return result
    
    def sync_teams(
        self,
        league_external_id: str,
        sport_id: int = 1
    ) -> Dict[str, Any]:
        """
        Sync teams for a specific league.
        
        Args:
            league_external_id: External ID of the league
            sport_id: Sport ID
            
        Returns:
            Sync result dictionary
        """
        logger.info(f"Starting team sync for league {league_external_id}")
        
        result = {
            'success': False,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Find league in database
            league = self._find_league_by_external_id(league_external_id)
            
            if not league:
                raise DataFetchError(f"League {league_external_id} not found in database")
            
            league_id = league['id']
            
            # Fetch teams from API
            raw_teams = self.fetcher.fetch_teams(league_id=int(league_external_id))
            logger.info(f"Fetched {len(raw_teams)} teams from API")
            
            # Process each team
            for raw_team in raw_teams:
                try:
                    # Normalize data
                    normalized = self.normalizer.normalize_team(
                        raw_team,
                        sport_id=sport_id,
                        league_id=league_id
                    )
                    
                    # Check if team exists
                    existing = self._find_team_by_external_id(
                        normalized['external_id']
                    )
                    
                    if existing:
                        # Update existing team
                        self._update_team(existing['id'], normalized)
                        result['updated'] += 1
                        logger.debug(f"Updated team: {normalized['name']}")
                    else:
                        # Create new team
                        self._create_team(normalized)
                        result['created'] += 1
                        logger.debug(f"Created team: {normalized['name']}")
                
                except Exception as e:
                    result['errors'] += 1
                    error_msg = f"Error processing team: {str(e)}"
                    result['error_messages'].append(error_msg)
                    logger.error(error_msg)
            
            result['success'] = result['errors'] == 0
            
            # Log sync
            self._log_sync(
                data_type='teams',
                total_records=len(raw_teams),
                successful_records=result['created'] + result['updated'],
                failed_records=result['errors']
            )
            
            logger.info(
                f"Team sync completed: "
                f"created={result['created']}, "
                f"updated={result['updated']}, "
                f"errors={result['errors']}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Team sync failed: {str(e)}")
            result['error_messages'].append(str(e))
            return result
    
    def sync_matches(
        self,
        league_external_id: str,
        days_ahead: int = 30,
        sport_id: int = 1
    ) -> Dict[str, Any]:
        """
        Sync upcoming matches for a specific league.
        
        Args:
            league_external_id: External ID of the league
            days_ahead: Number of days ahead to fetch
            sport_id: Sport ID
            
        Returns:
            Sync result dictionary
        """
        logger.info(f"Starting match sync for league {league_external_id}")
        
        result = {
            'success': False,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            # Find league in database
            league = self._find_league_by_external_id(league_external_id)
            
            if not league:
                raise DataFetchError(f"League {league_external_id} not found")
            
            league_id = league['id']
            
            # Fetch matches from API
            from_date = datetime.now()
            to_date = from_date + timedelta(days=days_ahead)
            
            raw_matches = self.fetcher.fetch_matches(
                league_id=int(league_external_id),
                from_date=from_date,
                to_date=to_date
            )
            
            logger.info(f"Fetched {len(raw_matches)} matches from API")
            
            # Process each match
            for raw_match in raw_matches:
                try:
                    # Find teams in database
                    home_team = self._find_team_by_external_id(
                        raw_match['home_team_external_id']
                    )
                    away_team = self._find_team_by_external_id(
                        raw_match['away_team_external_id']
                    )
                    
                    if not home_team or not away_team:
                        result['skipped'] += 1
                        logger.warning(
                            f"Skipping match: teams not found in database"
                        )
                        continue
                    
                    # Normalize data
                    normalized = self.normalizer.normalize_match(
                        raw_match,
                        sport_id=sport_id,
                        league_id=league_id,
                        home_team_id=home_team['id'],
                        away_team_id=away_team['id']
                    )
                    
                    # Check if match exists
                    existing = self._find_match_by_external_id(
                        normalized['external_id']
                    )
                    
                    if existing:
                        # Update existing match
                        self._update_match(existing['id'], normalized)
                        result['updated'] += 1
                        logger.debug(f"Updated match: {normalized['external_id']}")
                    else:
                        # Create new match
                        self._create_match(normalized)
                        result['created'] += 1
                        logger.debug(f"Created match: {normalized['external_id']}")
                
                except Exception as e:
                    result['errors'] += 1
                    error_msg = f"Error processing match: {str(e)}"
                    result['error_messages'].append(error_msg)
                    logger.error(error_msg)
            
            result['success'] = result['errors'] == 0
            
            # Log sync
            self._log_sync(
                data_type='matches',
                total_records=len(raw_matches),
                successful_records=result['created'] + result['updated'],
                failed_records=result['errors']
            )
            
            logger.info(
                f"Match sync completed: "
                f"created={result['created']}, "
                f"updated={result['updated']}, "
                f"errors={result['errors']}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Match sync failed: {str(e)}")
            result['error_messages'].append(str(e))
            return result
    
    def full_sync(self, league_external_id: str) -> Dict[str, Any]:
        """
        Perform full sync for a league: teams and matches.
        
        Args:
            league_external_id: External league ID
            
        Returns:
            Combined sync results
        """
        logger.info(f"Starting full sync for league {league_external_id}")
        
        results = {
            'teams': None,
            'matches': None,
            'success': False
        }
        
        try:
            # Sync teams first
            results['teams'] = self.sync_teams(league_external_id)
            
            # Then sync matches
            results['matches'] = self.sync_matches(league_external_id)
            
            # Overall success
            results['success'] = (
                results['teams']['success'] and 
                results['matches']['success']
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Full sync failed: {str(e)}")
            return results
    
    # Helper methods for database operations
    
    def _find_league_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Find league by external ID."""
        try:
            response = self.supabase.client.table('leagues').select('*').eq(
                'external_id', external_id
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding league: {str(e)}")
            return None
    
    def _create_league(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new league in database."""
        response = self.supabase.client.table('leagues').insert(data).execute()
        return response.data[0]
    
    def _update_league(self, league_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing league."""
        data.pop('id', None)
        data['updated_at'] = datetime.now().isoformat()
        response = self.supabase.client.table('leagues').update(data).eq('id', league_id).execute()
        return response.data[0]
    
    def _find_team_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Find team by external ID."""
        try:
            response = self.supabase.client.table('teams').select('*').eq(
                'external_id', external_id
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding team: {str(e)}")
            return None
    
    def _create_team(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new team in database."""
        response = self.supabase.client.table('teams').insert(data).execute()
        return response.data[0]
    
    def _update_team(self, team_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing team."""
        data.pop('id', None)
        data['updated_at'] = datetime.now().isoformat()
        response = self.supabase.client.table('teams').update(data).eq('id', team_id).execute()
        return response.data[0]
    
    def _find_match_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Find match by external ID."""
        try:
            response = self.supabase.client.table('matches').select('*').eq(
                'external_id', external_id
            ).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error finding match: {str(e)}")
            return None
    
    def _create_match(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new match in database."""
        response = self.supabase.client.table('matches').insert(data).execute()
        return response.data[0]
    
    def _update_match(self, match_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing match."""
        data.pop('id', None)
        data['updated_at'] = datetime.now().isoformat()
        response = self.supabase.client.table('matches').update(data).eq('id', match_id).execute()
        return response.data[0]
    
    def _log_sync(
        self,
        data_type: str,
        total_records: int,
        successful_records: int,
        failed_records: int
    ) -> None:
        """
        Log sync operation to database.
        
        Args:
            data_type: Type of data synced
            total_records: Total records processed
            successful_records: Successfully synced records
            failed_records: Failed records
        """
        try:
            log_data = {
                'data_source': 'FootballAPI',
                'data_type': data_type,
                'total_records': total_records,
                'successful_records': successful_records,
                'failed_records': failed_records,
                'sync_status': 'completed' if failed_records == 0 else 'completed_with_errors',
                'synced_at': datetime.now().isoformat()
            }
            
            self.supabase.client.table('sync_logs').insert(log_data).execute()
            logger.debug(f"Logged sync operation for {data_type}")
        
        except Exception as e:
            logger.error(f"Failed to log sync operation: {str(e)}")
    
    def get_sync_status(self, data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get sync operation history.
        
        Args:
            data_type: Filter by data type (leagues, teams, matches)
            
        Returns:
            List of sync log entries
        """
        try:
            query = self.supabase.client.table('sync_logs').select('*')
            
            if data_type:
                query = query.eq('data_type', data_type)
            
            response = query.order('synced_at', desc=True).limit(50).execute()
            return response.data
        
        except Exception as e:
            logger.error(f"Error fetching sync status: {str(e)}")
            return []
    
    def cleanup(self) -> None:
        """
        Cleanup resources.
        """
        self.fetcher.close()
        logger.info("DataSyncService cleanup completed")
