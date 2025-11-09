#!/usr/bin/env python3
"""
Integration tests for intervention completion flow
Tests event-driven architecture, habit updates, analytics, and notifications
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import uuid

# Test imports
from services.intervention_service import intervention_service
from services.habit_service import complete_related_habits
from services.analytics_service import generate_completion_summary
from services.notification_service import send_completion_notification
from services.event_bus import event_bus
from services.intervention_scheduler import auto_complete_expired_periods


class TestInterventionCompletion:
    """Test suite for intervention completion flow"""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        return mock_client, mock_table
    
    def test_complete_period_prevents_double_completion(self, mock_supabase):
        """Test that completing an already-completed period returns early"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Period already completed
        mock_table.eq.return_value.single.return_value.execute.return_value.data = {
            'status': 'completed',
            'user_id': 'user123',
            'intervention_name': 'Test Intervention'
        }
        
        with patch('services.intervention_service.supabase_client.client', mock_client):
            result = intervention_service.complete_period('period123')
            
            assert result['success'] is True
            assert result.get('already_completed') is True
            assert 'Already completed' in result.get('message', '')
    
    def test_complete_period_updates_status(self, mock_supabase):
        """Test that complete_period updates intervention_periods table"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Active period
        select_mock = Mock()
        select_mock.eq.return_value.single.return_value.execute.return_value.data = {
            'status': 'active',
            'user_id': 'user123',
            'intervention_name': 'Test Intervention'
        }
        
        # Mock: Update succeeds
        update_mock = Mock()
        update_mock.eq.return_value.execute.return_value.data = [{'id': 'period123'}]
        
        mock_client.table.side_effect = lambda table: {
            'intervention_periods': select_mock if table == 'intervention_periods' else update_mock
        }[table]
        
        with patch('services.intervention_service.supabase_client.client', mock_client):
            with patch('services.event_bus.event_bus.publish', return_value=[]):
                result = intervention_service.complete_period('period123')
                
                assert result['success'] is True
                assert 'completed' in result.get('message', '').lower()
    
    def test_habit_completion_listener_updates_habits(self, mock_supabase):
        """Test that habit completion listener updates user_habits"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Get period with selected_habits
        period_mock = Mock()
        period_mock.eq.return_value.single.return_value.execute.return_value.data = {
            'selected_habits': ['Habit 1', 'Habit 2']
        }
        
        # Mock: Update habits
        habit_update_mock = Mock()
        habit_update_mock.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {'id': 'habit1'}, {'id': 'habit2'}
        ]
        
        mock_client.table.side_effect = lambda table: {
            'intervention_periods': period_mock,
            'user_habits': habit_update_mock
        }[table]
        
        event_data = {
            'period_id': 'period123',
            'user_id': 'user123'
        }
        
        with patch('services.habit_service.supabase_client.client', mock_client):
            result = complete_related_habits(event_data)
            
            assert result['success'] is True
            assert result.get('updated_habits_count') == 2
    
    def test_analytics_generation_calculates_metrics(self, mock_supabase):
        """Test that analytics service calculates adherence and mood metrics"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Get period
        period_mock = Mock()
        period_mock.eq.return_value.single.return_value.execute.return_value.data = {
            'start_date': (date.today() - timedelta(days=30)).isoformat(),
            'end_date': date.today().isoformat(),
            'selected_habits': ['Habit 1']
        }
        
        # Mock: Get summaries
        summaries_mock = Mock()
        summaries_mock.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = [
            {'entry_date': (date.today() - timedelta(days=i)).isoformat(), 
             'completion_percentage': 80, 'total_habits': 1, 'completed_habits': 1}
            for i in range(20)  # 20 tracked days
        ]
        
        # Mock: Get moods
        moods_mock = Mock()
        moods_mock.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = [
            {'entry_date': (date.today() - timedelta(days=i)).isoformat(), 'mood': 4}
            for i in range(20)
        ]
        
        # Mock: Insert summary (may fail if table doesn't exist)
        insert_mock = Mock()
        insert_mock.execute.side_effect = Exception("Table doesn't exist")
        
        def table_side_effect(table_name):
            if table_name == 'intervention_periods':
                return period_mock
            elif table_name == 'daily_summaries':
                return summaries_mock
            elif table_name == 'daily_moods':
                return moods_mock
            elif table_name == 'completion_summaries':
                return insert_mock
            return Mock()
        
        mock_client.table.side_effect = table_side_effect
        
        event_data = {
            'period_id': 'period123',
            'user_id': 'user123'
        }
        
        with patch('services.analytics_service.supabase_client.client', mock_client):
            result = generate_completion_summary(event_data)
            
            # Should succeed even if table doesn't exist (graceful degradation)
            assert result['success'] is True
            assert 'adherence_rate' in result
            assert 'average_mood' in result
    
    def test_notification_service_creates_notification(self, mock_supabase):
        """Test that notification service creates notification record"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Insert notification
        insert_mock = Mock()
        insert_mock.execute.return_value.data = [{'id': 'notif123'}]
        
        mock_client.table.return_value = insert_mock
        
        event_data = {
            'user_id': 'user123',
            'intervention_name': 'Test Intervention',
            'period_id': 'period123',
            'auto_completed': False
        }
        
        with patch('services.notification_service.supabase_client.client', mock_client):
            result = send_completion_notification(event_data)
            
            assert result['success'] is True
            assert 'notification' in result
            assert 'Intervention Completed' in result['notification']['title']
    
    def test_auto_completion_finds_expired_periods(self, mock_supabase):
        """Test that auto-completion scheduler finds and completes expired periods"""
        mock_client, mock_table = mock_supabase
        
        # Mock: Find expired periods
        expired_mock = Mock()
        expired_mock.eq.return_value.lte.return_value.execute.return_value.data = [
            {
                'id': 'period1',
                'user_id': 'user123',
                'intervention_name': 'Expired Intervention',
                'end_date': (date.today() - timedelta(days=1)).isoformat()
            }
        ]
        
        mock_client.table.return_value = expired_mock
        
        with patch('services.intervention_scheduler.supabase_client.client', mock_client):
            with patch('services.intervention_service.intervention_service.complete_period') as complete_mock:
                complete_mock.return_value = {'success': True, 'message': 'Completed'}
                
                result = await auto_complete_expired_periods()
                
                assert result['success'] is True
                assert result['expired_count'] == 1
                assert complete_mock.called


class TestEventBus:
    """Test event bus functionality"""
    
    def test_event_subscription(self):
        """Test that handlers can subscribe to events"""
        handler_called = []
        
        def test_handler(event_data):
            handler_called.append(event_data)
        
        event_bus.subscribe("test.event", test_handler)
        event_bus.publish("test.event", {"test": "data"})
        
        assert len(handler_called) == 1
        assert handler_called[0]["test"] == "data"
    
    def test_event_handlers_continue_on_error(self):
        """Test that one handler failure doesn't stop others"""
        results = []
        
        def failing_handler(event_data):
            raise Exception("Handler failed")
        
        def succeeding_handler(event_data):
            results.append("success")
        
        event_bus.subscribe("test.error", failing_handler)
        event_bus.subscribe("test.error", succeeding_handler)
        
        event_results = event_bus.publish("test.error", {})
        
        # Both handlers should be called
        assert len(event_results) == 2
        assert results == ["success"]  # Succeeding handler executed
        assert any(not r['success'] for r in event_results)  # One failed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

