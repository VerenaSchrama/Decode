#!/usr/bin/env python3
"""
Check existing users in the database
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_users():
    """Check existing users in the database"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Checking existing users...")
    
    try:
        # Get all users
        result = supabase.table('users').select('*').execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} users:")
            for user in result.data:
                print(f"   ID: {user['id']}, Email: {user['email']}")
            return result.data[0]['id']  # Return first user's ID
        else:
            print("❌ No users found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return None

if __name__ == "__main__":
    user_id = check_users()
    if user_id:
        print(f"\n✅ Use user_id: {user_id} for testing")
    else:
        print("\n❌ No users available for testing")

