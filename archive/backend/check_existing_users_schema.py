#!/usr/bin/env python3
"""
Check the existing users table schema to see what columns are available
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_existing_users_schema():
    """Check what columns exist in the users table"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Checking existing users table schema...")
    
    try:
        # Try to get table information by attempting a simple query
        print("📋 Attempting to query users table...")
        
        # Try different approaches to get schema info
        try:
            # Method 1: Try to select all columns
            result = supabase.table('users').select('*').limit(1).execute()
            print(f"✅ Query successful: {result}")
            
            if result.data:
                print("📋 Available columns:")
                for key in result.data[0].keys():
                    print(f"   - {key}")
            else:
                print("ℹ️  No data found, but table exists")
                
        except Exception as e:
            print(f"⚠️  Full query failed: {e}")
            
            # Method 2: Try to get just the ID column
            try:
                result = supabase.table('users').select('id').limit(1).execute()
                print(f"✅ ID column exists: {result}")
            except Exception as e2:
                print(f"❌ ID column query failed: {e2}")
                
                # Method 3: Try to get table info
                try:
                    result = supabase.table('users').select('*').limit(0).execute()
                    print(f"✅ Table exists but empty: {result}")
                except Exception as e3:
                    print(f"❌ Table doesn't exist or no access: {e3}")
            
    except Exception as e:
        print(f"❌ Error checking users schema: {e}")

if __name__ == "__main__":
    check_existing_users_schema()

