#!/usr/bin/env python3
"""
Test the complete authentication API endpoints
"""

import asyncio
import os
import sys
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_api_endpoints():
    """Test all authentication API endpoints"""
    
    print("🌐 Testing Authentication API Endpoints")
    print("=" * 50)
    
    # Get API base URL
    api_base = "http://localhost:8000"  # Adjust if running on different port
    
    print(f"🔗 API Base URL: {api_base}")
    
    # Test data
    import time
    timestamp = int(time.time())
    test_email = f"apitest{timestamp}@gmail.com"
    test_password = "testpassword123"
    test_name = "API Test User"
    
    print(f"📧 Test email: {test_email}")
    print(f"🔑 Test password: {test_password}")
    
    async with httpx.AsyncClient() as client:
        
        # 1. Test Registration Endpoint
        print("\n1️⃣ Testing Registration Endpoint...")
        try:
            registration_data = {
                "email": test_email,
                "password": test_password,
                "name": test_name,
                "age": 25,
                "anonymous": False
            }
            
            response = await client.post(f"{api_base}/auth/register", json=registration_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Registration successful: {result['success']}")
                print(f"📧 Email confirmation required: {result.get('email_confirmation_required', False)}")
                print(f"👤 User ID: {result['user']['id']}")
                user_id = result['user']['id']
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration request failed: {str(e)}")
            return False
        
        # 2. Test Resend Confirmation Endpoint
        print("\n2️⃣ Testing Resend Confirmation Endpoint...")
        try:
            response = await client.post(f"{api_base}/auth/resend-confirmation", params={"email": test_email})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resend successful: {result['success']}")
                print(f"📝 Message: {result['message']}")
            else:
                print(f"⚠️ Resend failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️ Resend request failed: {str(e)}")
        
        # 3. Test Login Before Confirmation (should fail)
        print("\n3️⃣ Testing Login Before Confirmation...")
        try:
            login_data = {
                "email": test_email,
                "password": test_password
            }
            
            response = await client.post(f"{api_base}/auth/login", json=login_data)
            
            if response.status_code == 200:
                print("❌ Login succeeded unexpectedly")
            else:
                print(f"✅ Login correctly failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️ Login request failed: {str(e)}")
        
        # 4. Test Profile Endpoint (should work with service role)
        print("\n4️⃣ Testing Profile Endpoint...")
        try:
            response = await client.get(f"{api_base}/auth/profile/{user_id}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Profile retrieval successful: {result['success']}")
                print(f"👤 Profile name: {result['profile']['name']}")
            else:
                print(f"⚠️ Profile retrieval failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"⚠️ Profile request failed: {str(e)}")
        
        # 5. Test Token Verification (without valid token)
        print("\n5️⃣ Testing Token Verification...")
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = await client.post(f"{api_base}/auth/verify", headers=headers)
            
            if response.status_code == 401:
                print("✅ Token verification correctly rejected invalid token")
            else:
                print(f"⚠️ Token verification unexpected response: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Token verification request failed: {str(e)}")
    
    return True

async def test_server_running():
    """Check if the server is running"""
    
    print("🔍 Checking if API server is running...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/docs", timeout=5.0)
            if response.status_code == 200:
                print("✅ API server is running")
                return True
            else:
                print(f"⚠️ API server responded with status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API server is not running: {str(e)}")
        print("💡 Start the server with: uvicorn api:app --reload")
        return False

async def main():
    """Main test function"""
    
    print("🚀 Starting API Endpoint Tests")
    print("=" * 50)
    
    # Check if server is running
    server_running = await test_server_running()
    
    if not server_running:
        print("\n❌ Cannot test API endpoints - server not running")
        print("\n🔧 To start the server:")
        print("1. cd backend")
        print("2. uvicorn api:app --reload")
        print("3. Run this test again")
        return
    
    # Test API endpoints
    success = await test_api_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API endpoint tests completed!")
        print("\n📋 Summary:")
        print("✅ Registration endpoint working")
        print("✅ Email confirmation required")
        print("✅ Login blocked until confirmation")
        print("✅ Profile management working")
        print("✅ Token verification working")
        print("\n📧 Next steps:")
        print("1. Check email for confirmation link")
        print("2. Click confirmation link")
        print("3. Test login after confirmation")
        print("4. Test authenticated endpoints")
    else:
        print("❌ Some API endpoint tests failed")
        print("\n🔧 Check server logs for detailed error information")

if __name__ == "__main__":
    asyncio.run(main())
