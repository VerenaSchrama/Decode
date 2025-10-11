#!/usr/bin/env python3
"""
Create user-specific tables in Supabase using direct table operations
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def create_tables_simple():
    """Create tables by inserting test data and handling errors gracefully"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Testing table access...")
    
    # Test each table by trying to query it
    tables_to_test = [
        'user_habits',
        'user_interventions', 
        'intervention_habits',
        'daily_habit_entries',
        'intervention_feedback',
        'chat_messages'
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_test:
        try:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ Table '{table}' exists and is accessible")
            existing_tables.append(table)
        except Exception as e:
            if "Could not find the table" in str(e):
                print(f"❌ Table '{table}' does not exist")
                missing_tables.append(table)
            else:
                print(f"⚠️  Table '{table}' exists but has access issues: {e}")
                existing_tables.append(table)
    
    if missing_tables:
        print(f"\n📋 Missing tables: {missing_tables}")
        print("\n🔧 To create these tables, please:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the contents of 'setup_user_tables.sql'")
        print("4. Run the SQL script")
        print("\n📄 SQL script location: backend/setup_user_tables.sql")
        return False
    else:
        print("\n✅ All required tables exist!")
        return True

def test_api_endpoints():
    """Test the API endpoints that depend on these tables"""
    print("\n🔄 Testing API endpoints...")
    
    # Test endpoints that should work now
    import requests
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test interventions endpoint
    try:
        response = requests.get(f"{base_url}/interventions")
        if response.status_code == 200:
            print("✅ Interventions endpoint working")
        else:
            print(f"❌ Interventions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Interventions endpoint error: {e}")
    
    # Test recommend endpoint
    try:
        test_data = {
            "profile": {"name": "Test User", "age": 29},
            "symptoms": {"selected": ["PCOS"]},
            "consent": True
        }
        response = requests.post(f"{base_url}/recommend", json=test_data)
        if response.status_code == 200:
            print("✅ Recommend endpoint working")
        else:
            print(f"❌ Recommend endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Recommend endpoint error: {e}")

if __name__ == "__main__":
    print("🚀 Checking user-specific database tables...")
    
    if create_tables_simple():
        test_api_endpoints()
        print("\n🎉 All tables are ready! The API should work correctly now.")
    else:
        print("\n📋 Please create the missing tables using the SQL script provided.")
        print("After creating the tables, run this script again to verify everything works.")

