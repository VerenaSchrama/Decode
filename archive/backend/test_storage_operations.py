"""
Comprehensive test suite for all storage operations in the HerFoodCode application
Tests database storage, vector stores, file storage, and mobile app storage
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path

# Test imports
from auth_service import AuthService, UserRegistration, UserLogin
from models.supabase_models import SupabaseClient
from api import app
from retrievers.vectorstores import initialize_vectorstore, get_main_retriever

class TestDatabaseStorage:
    """Test all database storage operations"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.fixture
    def supabase_client(self):
        return SupabaseClient()
    
    @pytest.fixture
    def sample_user_data(self):
        return {
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User",
            "age": 25,
            "anonymous": False
        }
    
    @pytest.fixture
    def sample_intake_data(self):
        return {
            "profile": {"name": "Test User", "dateOfBirth": "1995-01-01"},
            "symptoms": {"selected": ["PCOS"], "additional": ""},
            "interventions": {"selected": [], "additional": ""},
            "habits": {"selected": ["Morning workout"], "additional": ""},
            "dietaryPreferences": {"selected": ["Vegetarian"], "additional": ""},
            "consent": True,
            "anonymous": False
        }
    
    @pytest.fixture
    def sample_daily_progress(self):
        return {
            "user_id": "test-user-123",
            "entry_date": "2024-01-01",
            "habits": [
                {"name": "Morning workout", "completed": True},
                {"name": "Healthy breakfast", "completed": False}
            ],
            "mood": {"mood": 4, "notes": "Feeling good"}
        }

    # Authentication Storage Tests
    async def test_auth_user_creation(self, auth_service, sample_user_data):
        """Test user creation in auth.users table"""
        with patch.object(auth_service.client.auth, 'sign_up') as mock_signup:
            mock_signup.return_value = MagicMock(
                user=MagicMock(id="test-uuid-123", email="test@example.com"),
                session=MagicMock(access_token="test-token", refresh_token="refresh-token")
            )
            
            with patch.object(auth_service.service_client.table('user_profiles'), 'insert') as mock_insert:
                mock_insert.return_value.execute.return_value = MagicMock(data=[{"id": "test-uuid-123"}])
                
                result = await auth_service.register_user(UserRegistration(**sample_user_data))
                
                assert result["success"] is True
                assert result["user"]["email"] == "test@example.com"
                mock_signup.assert_called_once()
                mock_insert.assert_called_once()

    async def test_user_profile_creation(self, supabase_client):
        """Test user profile creation in user_profiles table"""
        profile_data = {
            "user_uuid": "test-uuid-123",
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "anonymous": False
        }
        
        with patch.object(supabase_client.client.table('user_profiles'), 'insert') as mock_insert:
            mock_insert.return_value.execute.return_value = MagicMock(data=[profile_data])
            
            result = supabase_client.create_user(profile_data)
            
            assert result.data[0] == profile_data
            mock_insert.assert_called_once_with(profile_data)

    async def test_intake_data_storage(self, supabase_client, sample_intake_data):
        """Test intake data storage in intakes table"""
        intake_data = {
            "user_id": "test-user-123",
            "intake_data": sample_intake_data,
            "created_at": datetime.now().isoformat()
        }
        
        with patch.object(supabase_client.client.table('intakes'), 'insert') as mock_insert:
            mock_insert.return_value.execute.return_value = MagicMock(data=[{"id": "intake-123"}])
            
            result = supabase_client.create_intake(intake_data)
            
            assert result.data[0]["id"] == "intake-123"
            mock_insert.assert_called_once_with(intake_data)

    async def test_daily_progress_storage(self, sample_daily_progress):
        """Test daily progress storage in daily_habit_entries table"""
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.upsert.return_value.execute.return_value = MagicMock(
                data=[{"id": "entry-123"}]
            )
            
            # Use TestClient for proper async testing
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post("/daily-progress", json=sample_daily_progress)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["entry_id"] == "entry-123"

    async def test_user_intervention_storage(self):
        """Test user intervention storage in user_interventions table"""
        intervention_data = {
            "name": "Test Intervention",
            "description": "Test description",
            "profile_match": "PCOS management",
            "scientific_source": "Test study",
            "habits": [{"number": 1, "description": "Test habit"}]
        }
        
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=[{"id": "intervention-123"}]
            )
            
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post("/interventions/submit", json=intervention_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Test Intervention"

    async def test_intervention_habits_storage(self):
        """Test intervention habits storage in intervention_habits table"""
        habits_data = [
            {"intervention_id": "intervention-123", "number": 1, "description": "Test habit 1"},
            {"intervention_id": "intervention-123", "number": 2, "description": "Test habit 2"}
        ]
        
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
                data=habits_data
            )
            
            # This would be called as part of intervention submission
            result = mock_supabase.client.table('intervention_habits').insert(habits_data).execute()
            
            assert len(result.data) == 2
            assert result.data[0]["description"] == "Test habit 1"

class TestVectorStoreStorage:
    """Test vector store operations"""
    
    def test_vectorstore_creation(self):
        """Test ChromaDB vector store creation and persistence"""
        with patch('build_science_vectorstore.OpenAIEmbeddings') as mock_embeddings:
            with patch('build_science_vectorstore.Chroma.from_documents') as mock_chroma:
                mock_vectorstore = MagicMock()
                mock_chroma.return_value = mock_vectorstore
                
                # Test vector store creation
                from build_science_vectorstore import build_science_vectorstore
                build_science_vectorstore()
                
                mock_chroma.assert_called_once()
                mock_vectorstore.persist.assert_called_once()

    def test_database_vectorstore_creation(self):
        """Test database-based vector store creation"""
        with patch('build_database_vectorstore.supabase_client') as mock_supabase:
            with patch('build_database_vectorstore.Chroma.from_documents') as mock_chroma:
                mock_supabase.client.table.return_value.select.return_value.execute.return_value = MagicMock(
                    data=[{"id": "1", "name": "Test Intervention", "description": "Test"}]
                )
                
                mock_vectorstore = MagicMock()
                mock_chroma.return_value = mock_vectorstore
                
                from build_database_vectorstore import build_interventions_vectorstore
                build_interventions_vectorstore()
                
                mock_chroma.assert_called_once()
                mock_vectorstore.persist.assert_called_once()

    def test_vectorstore_persistence(self):
        """Test vector store file persistence"""
        vectorstore_path = Path("data/vectorstore/chroma")
        
        # Test that vector store directory exists and contains expected files
        assert vectorstore_path.exists()
        
        # Check for ChromaDB files
        chroma_files = list(vectorstore_path.glob("*.sqlite3"))
        assert len(chroma_files) > 0, "ChromaDB SQLite file should exist"

    def test_vectorstore_retrieval(self):
        """Test vector store retrieval operations"""
        with patch('retrievers.vectorstores.initialize_vectorstore') as mock_init:
            mock_retriever = MagicMock()
            mock_init.return_value = True
            
            with patch('retrievers.vectorstores.get_main_retriever') as mock_get_retriever:
                mock_get_retriever.return_value = mock_retriever
                
                # Test retrieval
                retriever = get_main_retriever()
                assert retriever is not None

class TestFileStorage:
    """Test file system storage operations"""
    
    def test_file_chunk_storage(self):
        """Test PDF chunk storage as JSON file"""
        chunks_path = Path("data/processed/chunks_AlisaVita.json")
        
        if chunks_path.exists():
            with open(chunks_path, 'r') as f:
                chunks = json.load(f)
            
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            assert all(isinstance(chunk, str) for chunk in chunks)

    def test_vectorstore_file_structure(self):
        """Test vector store file structure"""
        vectorstore_path = Path("data/vectorstore/chroma")
        
        assert vectorstore_path.exists()
        
        # Check for ChromaDB collection directory
        collection_dirs = [d for d in vectorstore_path.iterdir() if d.is_dir()]
        assert len(collection_dirs) > 0, "Should have at least one collection directory"

class TestConcurrentStorage:
    """Test concurrent storage operations"""
    
    async def test_concurrent_user_creation(self, auth_service):
        """Test concurrent user creation doesn't cause conflicts"""
        user_data_1 = UserRegistration(
            email="user1@example.com",
            password="password123",
            name="User 1"
        )
        user_data_2 = UserRegistration(
            email="user2@example.com", 
            password="password123",
            name="User 2"
        )
        
        with patch.object(auth_service.client.auth, 'sign_up') as mock_signup:
            mock_signup.return_value = MagicMock(
                user=MagicMock(id="test-uuid", email="test@example.com"),
                session=MagicMock(access_token="test-token")
            )
            
            with patch.object(auth_service.service_client.table('user_profiles'), 'insert') as mock_insert:
                mock_insert.return_value.execute.return_value = MagicMock(data=[{"id": "test-uuid"}])
                
                # Run concurrent registrations
                tasks = [
                    auth_service.register_user(user_data_1),
                    auth_service.register_user(user_data_2)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Both should succeed
                assert all(isinstance(result, dict) for result in results)
                assert all(result.get("success") for result in results)

    async def test_concurrent_daily_progress(self, sample_daily_progress):
        """Test concurrent daily progress storage"""
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.return_value.upsert.return_value.execute.return_value = MagicMock(
                data=[{"id": "entry-123"}]
            )
            
            # Create multiple concurrent requests
            from fastapi.testclient import TestClient
            client = TestClient(app)
            
            tasks = []
            for i in range(5):
                progress_data = sample_daily_progress.copy()
                progress_data["user_id"] = f"user-{i}"
                tasks.append(
                    client.post("/daily-progress", json=progress_data)
                )
            
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            assert all(response.status_code == 200 for response in responses)

class TestDataValidation:
    """Test data validation and schema consistency"""
    
    def test_user_profile_schema_validation(self):
        """Test user profile data schema validation"""
        from models.entities import User
        
        # Valid user data
        valid_user_data = {
            "id": "test-uuid-123",
            "name": "Test User",
            "email": "test@example.com",
            "age": 25,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user = User(**valid_user_data)
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        
        # Invalid user data should raise validation error
        with pytest.raises(ValueError):
            invalid_user_data = valid_user_data.copy()
            invalid_user_data["email"] = "invalid-email"
            User(**invalid_user_data)

    def test_daily_progress_schema_validation(self):
        """Test daily progress data schema validation"""
        from models.entities import DailyHabitEntry
        
        valid_entry_data = {
            "id": "entry-123",
            "user_id": "user-123",
            "entry_date": "2024-01-01",
            "habits_completed": ["Morning workout"],
            "mood": 4,
            "notes": "Feeling good",
            "created_at": datetime.now()
        }
        
        entry = DailyHabitEntry(**valid_entry_data)
        assert entry.user_id == "user-123"
        assert len(entry.habits_completed) == 1

class TestErrorHandling:
    """Test error handling in storage operations"""
    
    async def test_database_connection_error(self):
        """Test handling of database connection errors"""
        with patch('api.supabase_client') as mock_supabase:
            mock_supabase.client.table.side_effect = Exception("Database connection failed")
            
            from fastapi.testclient import TestClient
            client = TestClient(app)
            response = client.post("/daily-progress", json={"user_id": "test"})
            
            assert response.status_code == 500
            assert "Error saving daily progress" in response.json()["detail"]

    def test_vectorstore_initialization_error(self):
        """Test handling of vector store initialization errors"""
        with patch('retrievers.vectorstores.get_embeddings') as mock_embeddings:
            mock_embeddings.side_effect = Exception("OpenAI API error")
            
            result = initialize_vectorstore()
            
            assert result is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
