#!/usr/bin/env python3
"""
Supabase Setup Script for HFC App
This script helps you set up your Supabase database with the correct schema
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("📝 Please create a .env file with your Supabase credentials:")
        print("   Copy .env.example to .env and fill in your values")
        return False
    
    load_dotenv()
    
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("📝 Please update your .env file with the missing values")
        return False
    
    print("✅ .env file found with all required variables")
    return True

def test_supabase_connection():
    """Test connection to Supabase"""
    try:
        from models import supabase_client
        
        print("🔌 Testing Supabase connection...")
        
        # Test basic connection by getting interventions
        result = supabase_client.get_interventions()
        
        if result.data is not None:
            print("✅ Successfully connected to Supabase!")
            print(f"📊 Found {len(result.data)} interventions in database")
            return True
        else:
            print("❌ Connection failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def run_database_migration():
    """Run the database migration to create tables"""
    try:
        print("🗄️  Running database migration...")
        
        # Import and run migration
        from migrate_to_supabase import main as run_migration
        run_migration()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 HFC App Supabase Setup")
    print("=" * 40)
    
    # Step 1: Check environment file
    if not check_env_file():
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Supabase credentials")
        print("3. Run this script again")
        return False
    
    # Step 2: Test connection
    if not test_supabase_connection():
        print("\n📋 Next steps:")
        print("1. Check your Supabase URL and API key")
        print("2. Make sure your Supabase project is running")
        print("3. Run this script again")
        return False
    
    # Step 3: Run migration
    print("\n🗄️  Setting up database schema...")
    if not run_database_migration():
        print("\n❌ Setup failed during migration")
        return False
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\n📋 What was created:")
    print("   ✅ Database tables with proper schema")
    print("   ✅ Row Level Security (RLS) policies")
    print("   ✅ Initial data (interventions and habits)")
    print("   ✅ Custom intervention tracking")
    
    print("\n🚀 You can now run your API server:")
    print("   python3 api.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
