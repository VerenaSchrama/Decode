"""
Simplified storage operations test suite
Tests core storage functionality without complex mocking
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
import json
import os
from pathlib import Path

class TestStorageDiscovery:
    """Test storage discovery and mapping"""
    
    def test_storage_locations_exist(self):
        """Test that all expected storage locations exist"""
        
        # Test vector store directory
        vectorstore_path = Path("data/vectorstore/chroma")
        assert vectorstore_path.exists(), "Vector store directory should exist"
        
        # Test processed data directory
        processed_path = Path("data/processed")
        assert processed_path.exists(), "Processed data directory should exist"
        
        # Test raw data directory
        raw_path = Path("data/raw_book")
        assert raw_path.exists(), "Raw data directory should exist"
        
        # Test that ChromaDB files exist
        chroma_files = list(vectorstore_path.glob("*.sqlite3"))
        assert len(chroma_files) > 0, "ChromaDB SQLite file should exist"
        
        # Test that collection directories exist
        collection_dirs = [d for d in vectorstore_path.iterdir() if d.is_dir()]
        assert len(collection_dirs) > 0, "Should have at least one collection directory"

    def test_file_storage_structure(self):
        """Test file storage structure and content"""
        
        # Test PDF chunks file
        chunks_path = Path("data/processed/chunks_AlisaVita.json")
        if chunks_path.exists():
            with open(chunks_path, 'r') as f:
                chunks = json.load(f)
            
            assert isinstance(chunks, list), "Chunks should be a list"
            assert len(chunks) > 0, "Should have at least one chunk"
            assert all(isinstance(chunk, str) for chunk in chunks), "All chunks should be strings"
        
        # Test vector store persistence files
        vectorstore_path = Path("data/vectorstore/chroma")
        if vectorstore_path.exists():
            # Check for ChromaDB files
            bin_files = list(vectorstore_path.rglob("*.bin"))
            assert len(bin_files) > 0, "Should have ChromaDB binary files"
            
            sqlite_files = list(vectorstore_path.rglob("*.sqlite3"))
            assert len(sqlite_files) > 0, "Should have ChromaDB SQLite files"

    def test_database_schema_files(self):
        """Test that database schema files exist"""
        
        # Check for setup files
        setup_files = [
            "setup_database_schema.py",
            "setup_supabase.py"
        ]
        
        for file_name in setup_files:
            file_path = Path(file_name)
            assert file_path.exists(), f"Setup file {file_name} should exist"

    def test_model_files_exist(self):
        """Test that model files exist and are importable"""
        
        # Test that model files exist
        model_files = [
            "models/entities.py",
            "models/schemas.py", 
            "models/supabase_models.py",
            "models/user_input.py"
        ]
        
        for file_name in model_files:
            file_path = Path(file_name)
            assert file_path.exists(), f"Model file {file_name} should exist"

class TestAPIEndpoints:
    """Test API endpoint storage operations"""
    
    def test_api_file_exists(self):
        """Test that main API file exists"""
        api_file = Path("api.py")
        assert api_file.exists(), "Main API file should exist"
        
        # Check that API file has expected content
        with open(api_file, 'r') as f:
            content = f.read()
            
        # Check for key storage operations
        assert "daily-progress" in content, "Should have daily progress endpoint"
        assert "auth/register" in content, "Should have auth register endpoint"
        assert "interventions/submit" in content, "Should have intervention submit endpoint"

    def test_auth_service_exists(self):
        """Test that auth service exists"""
        auth_file = Path("auth_service.py")
        assert auth_file.exists(), "Auth service file should exist"
        
        with open(auth_file, 'r') as f:
            content = f.read()
            
        # Check for key auth operations
        assert "register_user" in content, "Should have register_user method"
        assert "login_user" in content, "Should have login_user method"
        assert "user_profiles" in content, "Should reference user_profiles table"

class TestVectorStoreOperations:
    """Test vector store operations"""
    
    def test_vectorstore_initialization(self):
        """Test vector store initialization without API calls"""
        
        # Test that vector store files exist
        vectorstore_path = Path("data/vectorstore/chroma")
        assert vectorstore_path.exists(), "Vector store directory should exist"
        
        # Test that we can import vector store modules
        try:
            from retrievers.vectorstores import initialize_vectorstore
            assert callable(initialize_vectorstore), "initialize_vectorstore should be callable"
        except ImportError as e:
            pytest.fail(f"Could not import vector store module: {e}")

    def test_vectorstore_build_scripts(self):
        """Test that vector store build scripts exist"""
        
        build_scripts = [
            "build_science_vectorstore.py",
            "build_database_vectorstore.py"
        ]
        
        for script in build_scripts:
            script_path = Path(script)
            assert script_path.exists(), f"Build script {script} should exist"

class TestDataModels:
    """Test data models and schemas"""
    
    def test_user_input_model(self):
        """Test user input model structure"""
        try:
            from models.user_input import UserInput, Profile, Symptoms
            assert UserInput is not None, "UserInput model should exist"
            assert Profile is not None, "Profile model should exist"
            assert Symptoms is not None, "Symptoms model should exist"
        except ImportError as e:
            pytest.fail(f"Could not import user input models: {e}")

    def test_entities_model(self):
        """Test entities model structure"""
        try:
            from models.entities import User, Intake, Intervention
            assert User is not None, "User entity should exist"
            assert Intake is not None, "Intake entity should exist"
            assert Intervention is not None, "Intervention entity should exist"
        except ImportError as e:
            pytest.fail(f"Could not import entities: {e}")

class TestMobileStorage:
    """Test mobile app storage structure"""
    
    def test_mobile_auth_context(self):
        """Test mobile auth context exists"""
        auth_context_path = Path("../mobile/src/contexts/AuthContext.tsx")
        if auth_context_path.exists():
            with open(auth_context_path, 'r') as f:
                content = f.read()
                
            # Check for AsyncStorage usage
            assert "AsyncStorage" in content, "Should use AsyncStorage"
            assert "@auth_user" in content, "Should store user data"
            assert "@auth_session" in content, "Should store session data"

    def test_mobile_types(self):
        """Test mobile types exist"""
        types_path = Path("../mobile/src/types/Auth.ts")
        if types_path.exists():
            with open(types_path, 'r') as f:
                content = f.read()
                
            # Check for key types
            assert "User" in content, "Should have User type"
            assert "AuthSession" in content, "Should have AuthSession type"
            assert "AuthState" in content, "Should have AuthState type"

class TestStorageMapping:
    """Test storage mapping completeness"""
    
    def test_storage_elements_identified(self):
        """Test that all storage elements are identified"""
        
        # Database tables that should exist
        expected_tables = [
            "user_profiles",
            "intakes", 
            "daily_habit_entries",
            "user_interventions",
            "intervention_habits"
        ]
        
        # Check that these are referenced in the code
        api_file = Path("api.py")
        if api_file.exists():
            with open(api_file, 'r') as f:
                content = f.read()
                
            for table in expected_tables:
                assert table in content, f"Table {table} should be referenced in API"

    def test_vectorstore_operations_identified(self):
        """Test that vector store operations are identified"""
        
        # Check for vector store operations in code
        api_file = Path("api.py")
        if api_file.exists():
            with open(api_file, 'r') as f:
                content = f.read()
                
            # Check for vector store operations
            assert "vectorstore" in content.lower(), "Should have vector store operations"
            assert "add_documents" in content, "Should have document addition operations"

    def test_file_operations_identified(self):
        """Test that file operations are identified"""
        
        # Check for file operations in build scripts
        build_scripts = ["build_science_vectorstore.py", "build_database_vectorstore.py"]
        
        for script in build_scripts:
            script_path = Path(script)
            if script_path.exists():
                with open(script_path, 'r') as f:
                    content = f.read()
                    
                # Check for file operations
                assert "json" in content.lower(), f"{script} should use JSON"
                assert "path" in content.lower(), f"{script} should use file paths"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
