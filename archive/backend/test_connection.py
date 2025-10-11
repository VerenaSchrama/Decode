#!/usr/bin/env python3
"""
Test Supabase connection with detailed error reporting
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_supabase_connection():
    """Test Supabase connection with detailed error reporting"""
    
    print("🔍 Testing Supabase Connection")
    print("=" * 40)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {url}")
    print(f"SUPABASE_ANON_KEY: {key[:20]}..." if key else "None")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    # Test basic connection
    print("\n🔌 Testing Basic Connection:")
    try:
        from supabase import create_client, Client
        
        print("  - Creating Supabase client...")
        client: Client = create_client(url, key)
        print("  ✅ Client created successfully")
        
        # Test a simple query
        print("  - Testing simple query...")
        result = client.table('InterventionsBASE').select('count').execute()
        print(f"  ✅ Query successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        
        # Try to get more details
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        
        return False

def test_alternative_connection():
    """Test alternative connection methods"""
    
    print("\n🔄 Testing Alternative Connection Methods:")
    
    # Test 1: Direct HTTP request
    print("\n1. Testing direct HTTP request:")
    try:
        import requests
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        # Try to get table info
        response = requests.get(f"{url}/rest/v1/InterventionsBASE?select=count", headers=headers)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("  ✅ Direct HTTP request successful")
            return True
        else:
            print(f"  ❌ HTTP request failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ HTTP request error: {e}")
    
    # Test 2: Check if URL is accessible
    print("\n2. Testing URL accessibility:")
    try:
        import requests
        
        url = os.getenv("SUPABASE_URL")
        response = requests.get(url, timeout=10)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.text[:200]}...")
        
        if response.status_code in [200, 404, 405]:  # 404/405 are OK for root URL
            print("  ✅ URL is accessible")
            return True
        else:
            print(f"  ❌ URL not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ URL accessibility error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Supabase Connection Test")
    print("=" * 50)
    
    # Test 1: Basic connection
    success1 = test_supabase_connection()
    
    # Test 2: Alternative methods
    success2 = test_alternative_connection()
    
    print("\n📋 Summary:")
    print(f"Basic Connection: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"Alternative Methods: {'✅ Success' if success2 else '❌ Failed'}")
    
    if success1 or success2:
        print("\n🎉 Connection test completed successfully!")
    else:
        print("\n❌ All connection tests failed!")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check if Supabase project is active")
        print("2. Verify the URL is correct")
        print("3. Check if API key is valid")
        print("4. Check network/firewall settings")
        print("5. Try accessing Supabase dashboard in browser")

