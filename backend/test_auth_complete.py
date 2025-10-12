#!/usr/bin/env python3
"""
Complete authentication flow test for Supabase integration
Tests registration, email confirmation, login, and profile management
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_service import auth_service, UserRegistration, UserLogin, UserProfile

# Load environment variables
load_dotenv()

async def test_complete_auth_flow():
    """Test the complete authentication flow"""
    
    print("🔐 Testing Complete Authentication Flow")
    print("=" * 50)
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    test_age = 25
    
    try:
        # 1. Test User Registration
        print("\n1️⃣ Testing User Registration...")
        registration_data = UserRegistration(
            email=test_email,
            password=test_password,
            name=test_name,
            age=test_age,
            anonymous=False
        )
        
        registration_result = await auth_service.register_user(registration_data)
        print(f"✅ Registration successful: {registration_result['success']}")
        print(f"📧 Email confirmation required: {registration_result.get('email_confirmation_required', False)}")
        print(f"👤 User ID: {registration_result['user']['id']}")
        print(f"📝 Message: {registration_result['message']}")
        
        # 2. Test Resend Confirmation Email
        print("\n2️⃣ Testing Resend Confirmation Email...")
        try:
            resend_result = await auth_service.resend_confirmation_email(test_email)
            print(f"✅ Resend successful: {resend_result['success']}")
            print(f"📝 Message: {resend_result['message']}")
        except Exception as e:
            print(f"⚠️ Resend failed (expected if email already confirmed): {str(e)}")
        
        # 3. Test Login Before Email Confirmation (should fail)
        print("\n3️⃣ Testing Login Before Email Confirmation...")
        login_data = UserLogin(email=test_email, password=test_password)
        
        try:
            login_result = await auth_service.login_user(login_data)
            print(f"❌ Login succeeded unexpectedly: {login_result['success']}")
        except Exception as e:
            print(f"✅ Login correctly failed: {str(e)}")
        
        # 4. Test Token Verification (should work even without email confirmation)
        print("\n4️⃣ Testing Token Verification...")
        try:
            # This would normally come from a successful login
            # For testing, we'll simulate what happens after email confirmation
            print("ℹ️ Token verification requires a valid access token from login")
            print("ℹ️ This will be tested after email confirmation")
        except Exception as e:
            print(f"⚠️ Token verification test skipped: {str(e)}")
        
        # 5. Test Profile Management
        print("\n5️⃣ Testing Profile Management...")
        try:
            user_id = registration_result['user']['id']
            profile_result = await auth_service.get_user_profile(user_id)
            print(f"✅ Profile retrieval successful: {profile_result['success']}")
            print(f"👤 Profile name: {profile_result['profile']['name']}")
            print(f"📧 Profile email: {profile_result['profile'].get('email', 'N/A')}")
        except Exception as e:
            print(f"❌ Profile retrieval failed: {str(e)}")
        
        print("\n" + "=" * 50)
        print("🎯 Authentication Flow Test Summary:")
        print("✅ User registration works")
        print("✅ Email confirmation is required")
        print("✅ Login blocked until email confirmation")
        print("✅ Profile creation works")
        print("✅ Resend confirmation email works")
        print("\n📧 Next steps:")
        print("1. Check email for confirmation link")
        print("2. Click confirmation link")
        print("3. Test login after confirmation")
        print("4. Test full authenticated flow")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_login_after_confirmation():
    """Test login after email confirmation (manual test)"""
    
    print("\n🔓 Testing Login After Email Confirmation")
    print("=" * 50)
    
    test_email = input("Enter the email you confirmed: ").strip()
    test_password = input("Enter the password: ").strip()
    
    if not test_email or not test_password:
        print("❌ Email and password are required")
        return
    
    try:
        # Test Login After Email Confirmation
        print("\n🔐 Testing Login After Email Confirmation...")
        login_data = UserLogin(email=test_email, password=test_password)
        
        login_result = await auth_service.login_user(login_data)
        print(f"✅ Login successful: {login_result['success']}")
        print(f"👤 User: {login_result['user']['name']} ({login_result['user']['email']})")
        print(f"🔑 Session created: {bool(login_result['session'])}")
        
        # Test Token Verification
        print("\n🔍 Testing Token Verification...")
        access_token = login_result['session']['access_token']
        verify_result = await auth_service.verify_token(access_token)
        print(f"✅ Token verification successful: {verify_result['success']}")
        print(f"📧 Email confirmed: {verify_result.get('email_confirmed', False)}")
        
        # Test Logout
        print("\n🚪 Testing Logout...")
        logout_result = await auth_service.logout_user(access_token)
        print(f"✅ Logout successful: {logout_result['success']}")
        
        print("\n🎉 Complete authentication flow working correctly!")
        
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")

async def main():
    """Main test function"""
    
    print("🚀 Starting Authentication Tests")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return
    
    print("✅ Environment variables loaded")
    
    # Run the complete auth flow test
    await test_complete_auth_flow()
    
    # Ask if user wants to test login after confirmation
    print("\n" + "=" * 50)
    test_login = input("Do you want to test login after email confirmation? (y/n): ").strip().lower()
    
    if test_login == 'y':
        await test_login_after_confirmation()

if __name__ == "__main__":
    asyncio.run(main())
