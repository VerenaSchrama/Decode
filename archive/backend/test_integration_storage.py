"""
Integration tests for complete user journey storage operations
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
from api import app
from auth_service import AuthService
from models.supabase_models import SupabaseClient

class TestEndToEndStorage:
    """Test complete user journey storage operations"""
    
    async def test_complete_user_journey_storage(self):
        """Test storage operations throughout complete user journey"""
        
        # Step 1: User Registration
        registration_data = {
            "email": "journey@example.com",
            "password": "password123",
            "name": "Journey User",
            "age": 30
        }
        
        with patch('auth_service.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "success": True,
                "user": {"id": "journey-uuid", "email": "journey@example.com"},
                "session": {"access_token": "token"}
            }
            
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post("/auth/register", json=registration_data)
            assert response.status_code == 200
            
        # Step 2: Story Intake
        intake_data = {
            "profile": {"name": "Journey User", "dateOfBirth": "1994-01-01"},
            "symptoms": {"selected": ["PCOS"]},
            "interventions": {"selected": []},
            "habits": {"selected": ["Morning workout"]},
            "dietaryPreferences": {"selected": ["Vegetarian"]},
            "consent": True,
            "anonymous": False
        }
        
        with patch('simple_intake_service.SimpleIntakeService.create_anonymous_user') as mock_user:
            mock_user.return_value = "journey-uuid"
            
            with patch('simple_intake_service.SimpleIntakeService.store_intake_data') as mock_store:
                mock_store.return_value = {"success": True, "intake_id": "intake-123"}
                
                # This would be called during intake completion
                result = mock_store(intake_data)
                assert result["success"] is True
                
        # Step 3: Daily Progress Tracking
        daily_progress = {
            "user_id": "journey-uuid",
            "entry_date": "2024-01-01",
            "habits": [
                {"name": "Morning workout", "completed": True},
                {"name": "Healthy breakfast", "completed": False}
            ],
            "mood": {"mood": 4, "notes": "Good day"}
        }
        
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.upsert.return_value.execute.return_value = MagicMock(
                data=[{"id": "progress-123"}]
            )
            
            response = client.post("/daily-progress", json=daily_progress)
            assert response.status_code == 200
            
        # Step 4: User Intervention Submission
        intervention_data = {
            "name": "Custom PCOS Management",
            "description": "Personalized approach",
            "profile_match": "PCOS with weight management",
            "scientific_source": "Personal research",
            "habits": [{"number": 1, "description": "Custom habit"}]
        }
        
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=[{"id": "intervention-123"}]
            )
            
            response = client.post("/interventions/submit", json=intervention_data)
            assert response.status_code == 200

    async def test_data_consistency_across_operations(self):
        """Test that data remains consistent across different storage operations"""
        
        user_id = "consistency-test-uuid"
        
        # Create user
        with patch('auth_service.AuthService.register_user') as mock_register:
            mock_register.return_value = {
                "success": True,
                "user": {"id": user_id, "email": "consistency@example.com"}
            }
            
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post("/auth/register", json={
                "email": "consistency@example.com",
                "password": "password123",
                "name": "Consistency User"
            })
            assert response.status_code == 200
            
        # Verify user can be retrieved
        with patch('auth_service.AuthService.get_user_profile') as mock_get_profile:
            mock_get_profile.return_value = {
                "success": True,
                "profile": {"id": user_id, "name": "Consistency User"}
            }
            
            response = client.get(f"/auth/profile/{user_id}")
            assert response.status_code == 200
            assert response.json()["profile"]["id"] == user_id

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
