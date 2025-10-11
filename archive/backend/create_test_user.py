#!/usr/bin/env python3
"""
Create a test user in the database for testing purposes
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def create_test_user():
    """Create a test user in the database"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Creating test user...")
    
    try:
        # Check if user already exists
        result = supabase.table('users').select('*').eq('id', 1).execute()
        
        if result.data:
            print("✅ Test user already exists")
            print(f"   User: {result.data[0]}")
            return True
        
        # Create test user
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "hashed_password": "test_password_hash",
            "created_at": "2024-01-01T00:00:00Z",
            "current_strategy": "testing"
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            print("✅ Test user created successfully")
            print(f"   User: {result.data[0]}")
            return True
        else:
            print("❌ Failed to create test user")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == "__main__":
    create_test_user()

