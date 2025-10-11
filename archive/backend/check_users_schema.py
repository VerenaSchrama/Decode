#!/usr/bin/env python3
"""
Check the actual schema of the users table
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_users_schema():
    """Check the actual schema of the users table"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Checking users table schema...")
    
    try:
        # Try to get a sample record to see the schema
        result = supabase.table('users').select('*').limit(1).execute()
        print(f"✅ Users table query result: {result}")
        
        if result.data:
            print("📋 Available columns:")
            for key in result.data[0].keys():
                print(f"   - {key}")
        else:
            print("ℹ️  No users found, but table exists")
            
        # Try to get table info
        print("\n🔄 Trying to get table info...")
        try:
            # This might not work with the anon key, but let's try
            info_result = supabase.table('users').select('*').limit(0).execute()
            print(f"✅ Table info query successful")
        except Exception as e:
            print(f"⚠️  Table info query failed: {e}")
            
    except Exception as e:
        print(f"❌ Error checking users schema: {e}")

if __name__ == "__main__":
    check_users_schema()

