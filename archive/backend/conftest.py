"""
Test configuration and fixtures for storage operations tests
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
import os
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    with patch('models.supabase_models.SupabaseClient') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_auth_service():
    """Mock authentication service for testing"""
    with patch('auth_service.AuthService') as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def test_data_dir():
    """Create temporary test data directory"""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ.update({
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "test-anon-key",
        "SUPABASE_SERVICE_ROLE_KEY": "test-service-key",
        "OPENAI_API_KEY": "test-openai-key"
    })
