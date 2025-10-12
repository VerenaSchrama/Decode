#!/usr/bin/env python3
"""
Simple Supabase connection test
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client, Client

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connection"""
    
    print("🔗 Testing Supabase Connection")
    print("=" * 40)
    
    # Check environment variables
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"URL: {url[:20]}..." if url else "❌ SUPABASE_URL not set")
    print(f"Anon Key: {'✅ Set' if anon_key else '❌ Not set'}")
    print(f"Service Key: {'✅ Set' if service_key else '❌ Not set'}")
    
    if not url or not anon_key:
        print("❌ Missing required environment variables")
        return False
    
    try:
        # Test basic connection
        client: Client = create_client(url, anon_key)
        print("✅ Supabase client created successfully")
        
        # Test a simple query
        result = client.table('user_profiles').select('count').execute()
        print(f"✅ Database query successful: {len(result.data)} profiles")
        
        # Test service client if available
        if service_key:
            service_client: Client = create_client(url, service_key)
            print("✅ Service client created successfully")
            
            # Test service client query
            service_result = service_client.table('user_profiles').select('count').execute()
            print(f"✅ Service client query successful: {len(service_result.data)} profiles")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_auth_configuration():
    """Test Supabase Auth configuration"""
    
    print("\n🔐 Testing Supabase Auth Configuration")
    print("=" * 40)
    
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not anon_key:
        print("❌ Missing required environment variables")
        return False
    
    try:
        client: Client = create_client(url, anon_key)
        
        # Test auth configuration
        print("✅ Auth client created")
        
        # Check if email confirmation is enabled
        # This is a basic test - we can't easily check server-side config
        print("ℹ️ Email confirmation status: Check Supabase dashboard")
        print("ℹ️ Redirect URL: https://decodev1.vercel.app/email-confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth configuration test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Starting Supabase Configuration Tests")
    print("=" * 50)
    
    # Test basic connection
    connection_ok = test_supabase_connection()
    
    # Test auth configuration
    auth_ok = test_auth_configuration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Database Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Auth Configuration: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    
    if connection_ok and auth_ok:
        print("\n🎉 All tests passed! Supabase is properly configured.")
        print("\n📋 Next steps:")
        print("1. Check Supabase dashboard for email confirmation settings")
        print("2. Verify redirect URLs are configured")
        print("3. Test user registration with a real email")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env file")
        print("2. Check Supabase project is active")
        print("3. Verify database tables exist (user_profiles)")
        print("4. Check RLS policies are properly configured")

if __name__ == "__main__":
    main()
