#!/usr/bin/env python3
"""
Check current database state to see if migration was run
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_database_state():
    """Check if the migration was run"""
    
    print("🔍 CHECKING DATABASE STATE")
    print("=" * 40)
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    try:
        # Check if user_profiles table exists
        print("1. Checking user_profiles table...")
        try:
            result = supabase.table('user_profiles').select('*').limit(1).execute()
            print("   ✅ user_profiles table exists")
        except Exception as e:
            print(f"   ❌ user_profiles table missing: {e}")
            return False
        
        # Check if daily_habit_entries has user_uuid column
        print("2. Checking daily_habit_entries table structure...")
        try:
            result = supabase.table('daily_habit_entries').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                if 'user_uuid' in columns:
                    print("   ✅ user_uuid column exists in daily_habit_entries")
                else:
                    print("   ❌ user_uuid column missing in daily_habit_entries")
                    print(f"   📋 Available columns: {columns}")
            else:
                print("   ⚠️  No data to check columns")
        except Exception as e:
            print(f"   ❌ Error checking daily_habit_entries: {e}")
        
        # Check if intakes has user_uuid column
        print("3. Checking intakes table structure...")
        try:
            result = supabase.table('intakes').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                if 'user_uuid' in columns:
                    print("   ✅ user_uuid column exists in intakes")
                else:
                    print("   ❌ user_uuid column missing in intakes")
                    print(f"   📋 Available columns: {columns}")
            else:
                print("   ⚠️  No data to check columns")
        except Exception as e:
            print(f"   ❌ Error checking intakes: {e}")
        
        # Check auth.users table (this should exist by default)
        print("4. Checking auth.users table...")
        try:
            # Try to access auth.users through a function or RPC
            result = supabase.rpc('get_auth_users_count').execute()
            print("   ✅ auth.users table accessible")
        except Exception as e:
            print(f"   ⚠️  Cannot directly access auth.users: {e}")
            print("   ℹ️  This is normal - auth.users is managed by Supabase")
        
        print("\n" + "=" * 40)
        print("🎯 DIAGNOSIS COMPLETE!")
        print("\n📋 NEXT STEPS:")
        print("1. If user_profiles table is missing → Run the SQL migration")
        print("2. If user_uuid columns are missing → Run the SQL migration")
        print("3. If everything exists → Check Supabase Auth settings")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    check_database_state()

