#!/usr/bin/env python3
"""
Database Schema Setup Script
Creates all tables in Supabase using the SQL schema file
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

def setup_database_schema():
    """Set up the database schema by executing the SQL file"""
    
    # Load environment variables
    load_dotenv()
    
    # Create Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    client: Client = create_client(supabase_url, supabase_key)
    
    # Read the SQL schema file
    schema_file = Path("supabase_schema.sql")
    if not schema_file.exists():
        print("❌ supabase_schema.sql file not found")
        return False
    
    with open(schema_file, 'r') as f:
        sql_content = f.read()
    
    print("🗄️  Setting up database schema...")
    print("📝 Executing SQL schema...")
    
    try:
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"   Executing statement {i}/{len(statements)}...")
                try:
                    # Execute each SQL statement
                    result = client.rpc('exec_sql', {'sql': statement})
                    print(f"   ✅ Statement {i} executed successfully")
                except Exception as e:
                    # Some statements might fail if tables already exist, that's okay
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"   ⚠️  Statement {i} skipped (already exists)")
                    else:
                        print(f"   ❌ Statement {i} failed: {str(e)}")
                        # Continue with other statements
        
        print("✅ Database schema setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema setup failed: {str(e)}")
        return False

def test_connection():
    """Test the database connection"""
    try:
        load_dotenv()
        client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
        
        # Try to query a simple table
        result = client.table('users').select('count').execute()
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Database Schema Setup")
    print("=" * 40)
    
    # First, let's try a different approach - use the Supabase dashboard
    print("📋 Manual Setup Required:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the contents of supabase_schema.sql")
    print("4. Execute the SQL")
    print("5. Run this script again to test")
    
    print("\n🔍 Testing connection...")
    if test_connection():
        print("\n🎉 Database is ready!")
    else:
        print("\n❌ Please set up the schema manually first")
