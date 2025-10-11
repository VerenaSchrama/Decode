#!/usr/bin/env python3
"""
Test inserting into users table to discover the schema
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def test_users_insert():
    """Test inserting into users table to discover schema"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Testing users table insert to discover schema...")
    
    # Test 1: Try minimal insert with just ID
    print("\n1️⃣ Testing minimal insert...")
    try:
        result = supabase.table('users').insert({'id': 1}).execute()
        print(f"✅ Minimal insert successful: {result}")
    except Exception as e:
        print(f"❌ Minimal insert failed: {e}")
    
    # Test 2: Try with common user fields
    print("\n2️⃣ Testing with common fields...")
    try:
        result = supabase.table('users').insert({
            'id': 2,
            'email': 'test@example.com'
        }).execute()
        print(f"✅ Email insert successful: {result}")
    except Exception as e:
        print(f"❌ Email insert failed: {e}")
    
    # Test 3: Try with auth-related fields
    print("\n3️⃣ Testing with auth fields...")
    try:
        result = supabase.table('users').insert({
            'id': 3,
            'email': 'test2@example.com',
            'hashed_password': 'test_hash'
        }).execute()
        print(f"✅ Auth insert successful: {result}")
    except Exception as e:
        print(f"❌ Auth insert failed: {e}")
    
    # Test 4: Try to get the actual table schema
    print("\n4️⃣ Trying to get table schema...")
    try:
        # This might work to get column info
        result = supabase.table('users').select('*').limit(0).execute()
        print(f"✅ Schema query result: {result}")
        
        # Try to get column names from the response
        if hasattr(result, 'data') and result.data is not None:
            print("📋 Columns from empty query:")
            # This won't work with empty data, but let's try
        else:
            print("ℹ️  No column info available from empty query")
            
    except Exception as e:
        print(f"❌ Schema query failed: {e}")

if __name__ == "__main__":
    test_users_insert()

