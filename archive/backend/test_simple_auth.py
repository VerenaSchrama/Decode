#!/usr/bin/env python3
"""
Simple authentication test to debug the issue
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_simple_auth():
    """Test authentication with simpler approach"""
    
    print("🧪 SIMPLE AUTHENTICATION TEST")
    print("=" * 40)
    
    # Test 1: Try with a very simple email
    print("1. Testing with simple email...")
    simple_email = "test@test.com"
    
    registration_data = {
        "email": simple_email,
        "password": "password123",
        "name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=registration_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Registration successful!")
            return True
        else:
            print("   ❌ Registration failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Check Supabase connection
    print("2. Testing Supabase connection...")
    try:
        from models import supabase_client
        
        # Try a simple query
        result = supabase_client.client.table('user_profiles').select('*').limit(1).execute()
        print(f"   ✅ Supabase connection working")
        print(f"   📊 User profiles count: {len(result.data)}")
        
    except Exception as e:
        print(f"   ❌ Supabase connection error: {e}")
    
    print()
    
    # Test 3: Check if we can access auth.users through Supabase
    print("3. Testing Supabase Auth directly...")
    try:
        from models import supabase_client
        
        # Try to sign up directly with Supabase
        auth_response = supabase_client.client.auth.sign_up({
            "email": "direct@test.com",
            "password": "password123"
        })
        
        if auth_response.user:
            print("   ✅ Direct Supabase Auth signup working!")
            print(f"   👤 User ID: {auth_response.user.id}")
        else:
            print("   ❌ Direct Supabase Auth signup failed")
            print(f"   📝 Response: {auth_response}")
            
    except Exception as e:
        print(f"   ❌ Direct Supabase Auth error: {e}")
    
    print()
    print("=" * 40)
    print("🎯 SIMPLE TEST COMPLETE!")

if __name__ == "__main__":
    test_simple_auth()