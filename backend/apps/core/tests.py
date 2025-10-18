"""
Tests for core application.

This module contains unit tests for core services, utilities,
and helper functions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase

from apps.core.services import SupabaseClient, SupabaseService, get_supabase_client
from apps.core.exceptions import (
    SupabaseConnectionError,
    SupabaseConfigurationError,
    ResourceNotFoundError,
)


class SupabaseClientTests(TestCase):
    """
    Test cases for SupabaseClient.
    """
    
    @patch('apps.core.services.supabase_client.create_client')
    def test_client_singleton(self, mock_create_client):
        """
        Test that SupabaseClient follows singleton pattern.
        """
        mock_create_client.return_value = Mock()
        
        client1 = SupabaseClient()
        client2 = SupabaseClient()
        
        # Should be the same instance
        self.assertIs(client1, client2)
        
        # create_client should only be called once
        self.assertEqual(mock_create_client.call_count, 1)
    
    @patch('apps.core.services.supabase_client.settings')
    def test_missing_configuration(self, mock_settings):
        """
        Test that missing configuration raises error.
        """
        # Clear singleton instance for this test
        SupabaseClient._instance = None
        SupabaseClient._client = None
        
        mock_settings.SUPABASE_URL = ''
        mock_settings.SUPABASE_ANON_KEY = ''
        
        with self.assertRaises(SupabaseConfigurationError):
            SupabaseClient()
    
    @patch('apps.core.services.supabase_client.create_client')
    @patch('apps.core.services.supabase_client.settings')
    def test_health_check_success(self, mock_settings, mock_create_client):
        """
        Test successful health check.
        """
        # Setup
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_ANON_KEY = 'test-key'
        
        mock_client = Mock()
        mock_table = Mock()
        mock_table.select.return_value.limit.return_value.execute.return_value = Mock(data=[{'id': 1}])
        mock_client.table.return_value = mock_table
        mock_create_client.return_value = mock_client
        
        # Clear singleton
        SupabaseClient._instance = None
        SupabaseClient._client = None
        
        client = SupabaseClient()
        result = client.health_check()
        
        self.assertTrue(result)
    
    @patch('apps.core.services.supabase_client.create_client')
    @patch('apps.core.services.supabase_client.settings')
    def test_health_check_failure(self, mock_settings, mock_create_client):
        """
        Test failed health check.
        """
        # Setup
        mock_settings.SUPABASE_URL = 'https://test.supabase.co'
        mock_settings.SUPABASE_ANON_KEY = 'test-key'
        
        mock_client = Mock()
        mock_client.table.side_effect = Exception("Connection failed")
        mock_create_client.return_value = mock_client
        
        # Clear singleton
        SupabaseClient._instance = None
        SupabaseClient._client = None
        
        client = SupabaseClient()
        result = client.health_check()
        
        self.assertFalse(result)


class SupabaseServiceTests(TestCase):
    """
    Test cases for SupabaseService.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        """
        self.service = SupabaseService()
        self.mock_client = Mock()
        self.service.client = self.mock_client
    
    def test_get_all_sports(self):
        """
        Test getting all sports.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'name': 'Football', 'is_active': True},
            {'id': 2, 'name': 'Basketball', 'is_active': True},
        ]
        
        self.mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        # Execute
        sports = self.service.get_all_sports()
        
        # Assert
        self.assertEqual(len(sports), 2)
        self.assertEqual(sports[0]['name'], 'Football')
    
    def test_get_sport_by_id_not_found(self):
        """
        Test getting a sport that doesn't exist.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.data = []
        
        self.mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Execute & Assert
        with self.assertRaises(ResourceNotFoundError):
            self.service.get_sport_by_id(999)
    
    def test_get_leagues_by_sport(self):
        """
        Test getting leagues for a specific sport.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'name': 'Premier League', 'sport_id': 1},
            {'id': 2, 'name': 'La Liga', 'sport_id': 1},
        ]
        
        self.mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        
        # Execute
        leagues = self.service.get_leagues_by_sport(sport_id=1)
        
        # Assert
        self.assertEqual(len(leagues), 2)
        self.assertEqual(leagues[0]['name'], 'Premier League')
    
    def test_search_teams(self):
        """
        Test searching teams by name.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'name': 'Manchester United'},
            {'id': 2, 'name': 'Manchester City'},
        ]
        
        self.mock_client.table.return_value.select.return_value.ilike.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
        
        # Execute
        teams = self.service.search_teams('Manchester')
        
        # Assert
        self.assertEqual(len(teams), 2)
        self.assertTrue('Manchester' in teams[0]['name'])
    
    def test_create_prediction(self):
        """
        Test creating a new prediction.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [{
            'id': 1,
            'user_id': 'user-123',
            'match_id': 1,
            'predicted_winner': 'home',
            'confidence_score': 0.85,
        }]
        
        self.mock_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        # Execute
        prediction = self.service.create_prediction(
            user_id='user-123',
            match_id=1,
            predicted_winner='home',
            confidence_score=0.85
        )
        
        # Assert
        self.assertEqual(prediction['user_id'], 'user-123')
        self.assertEqual(prediction['predicted_winner'], 'home')
    
    def test_health_check(self):
        """
        Test service health check.
        """
        self.mock_client.health_check.return_value = True
        
        health_status = self.service.health_check()
        
        self.assertEqual(health_status['status'], 'healthy')
        self.assertEqual(health_status['service'], 'supabase')


class DecoratorsTests(TestCase):
    """
    Test cases for utility decorators.
    """
    
    def test_handle_supabase_errors(self):
        """
        Test Supabase error handling decorator.
        """
        from apps.core.decorators import handle_supabase_errors
        from apps.core.exceptions import SupabaseQueryError
        
        @handle_supabase_errors
        def failing_function():
            raise Exception("Database error")
        
        with self.assertRaises(SupabaseQueryError):
            failing_function()
    
    def test_log_execution_time(self):
        """
        Test execution time logging decorator.
        """
        from apps.core.decorators import log_execution_time
        import time
        
        @log_execution_time
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")
    
    def test_retry_on_failure(self):
        """
        Test retry decorator.
        """
        from apps.core.decorators import retry_on_failure
        
        counter = {'calls': 0}
        
        @retry_on_failure(max_attempts=3, delay=0.01)
        def flaky_function():
            counter['calls'] += 1
            if counter['calls'] < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = flaky_function()
        
        self.assertEqual(result, "success")
        self.assertEqual(counter['calls'], 3)


class ExceptionsTests(TestCase):
    """
    Test cases for custom exceptions.
    """
    
    def test_base_exception(self):
        """
        Test BaseAppException.
        """
        from apps.core.exceptions import BaseAppException
        
        exc = BaseAppException("Test error", code="TEST_ERROR")
        
        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.code, "TEST_ERROR")
        self.assertEqual(str(exc), "[TEST_ERROR] Test error")
    
    def test_resource_not_found_error(self):
        """
        Test ResourceNotFoundError.
        """
        from apps.core.exceptions import ResourceNotFoundError
        
        exc = ResourceNotFoundError("User not found")
        
        self.assertIn("User not found", str(exc))
        self.assertIsInstance(exc, Exception)
