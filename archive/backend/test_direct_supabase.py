#!/usr/bin/env python3
"""
Test Supabase Auth directly without our API wrapper
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_direct_supabase_auth():
    """Test Supabase Auth directly"""
    
    print("🧪 TESTING SUPABASE AUTH DIRECTLY")
    print("=" * 50)
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"📡 Supabase URL: {url[:50]}...")
    print(f"🔑 Using key: {key[:20]}...")
    
    supabase: Client = create_client(url, key)
    
    # Test 1: Try to sign up with a simple email
    print("\n1. Testing direct signup...")
    try:
        auth_response = supabase.auth.sign_up({
            "email": "test@test.com",
            "password": "password123"
        })
        
        print(f"   Response: {auth_response}")
        
        if auth_response.user:
            print("   ✅ Direct signup successful!")
            print(f"   👤 User ID: {auth_response.user.id}")
            print(f"   📧 Email: {auth_response.user.email}")
        else:
            print("   ❌ Direct signup failed")
            
    except Exception as e:
        print(f"   ❌ Direct signup error: {e}")
    
    # Test 2: Try to sign in
    print("\n2. Testing direct signin...")
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": "test@test.com",
            "password": "password123"
        })
        
        if auth_response.user:
            print("   ✅ Direct signin successful!")
            print(f"   👤 User ID: {auth_response.user.id}")
        else:
            print("   ❌ Direct signin failed")
            
    except Exception as e:
        print(f"   ❌ Direct signin error: {e}")
    
    # Test 3: Check if we can access the auth schema
    print("\n3. Testing auth schema access...")
    try:
        # Try to query auth.users through a function
        result = supabase.rpc('get_auth_users').execute()
        print(f"   ✅ Auth schema accessible: {result}")
    except Exception as e:
        print(f"   ❌ Auth schema error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIRECT SUPABASE TEST COMPLETE!")

if __name__ == "__main__":
    test_direct_supabase_auth()

