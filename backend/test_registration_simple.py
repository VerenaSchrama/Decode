#!/usr/bin/env python3
"""
Simple user registration test with detailed error handling
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_service import auth_service, UserRegistration

# Load environment variables
load_dotenv()

async def test_simple_registration():
    """Test user registration with detailed error handling"""
    
    print("👤 Testing Simple User Registration")
    print("=" * 40)
    
    # Use a unique email for testing
    import time
    timestamp = int(time.time())
    test_email = f"test{timestamp}@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    
    print(f"📧 Test email: {test_email}")
    print(f"🔑 Test password: {test_password}")
    print(f"👤 Test name: {test_name}")
    
    try:
        # Create registration data
        registration_data = UserRegistration(
            email=test_email,
            password=test_password,
            name=test_name,
            age=25,
            anonymous=False
        )
        
        print("\n🔄 Attempting registration...")
        registration_result = await auth_service.register_user(registration_data)
        
        print("✅ Registration successful!")
        print(f"👤 User ID: {registration_result['user']['id']}")
        print(f"📧 Email: {registration_result['user']['email']}")
        print(f"📝 Message: {registration_result['message']}")
        print(f"🔐 Email confirmation required: {registration_result.get('email_confirmation_required', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Registration failed: {str(e)}")
        
        # Try to get more detailed error information
        try:
            # Test direct Supabase auth call
            print("\n🔍 Testing direct Supabase auth call...")
            client = auth_service.client
            
            # Try a simple signup
            auth_response = client.auth.sign_up({
                "email": test_email,
                "password": test_password
            })
            
            print(f"✅ Direct auth call successful: {auth_response.user is not None}")
            
        except Exception as direct_error:
            print(f"❌ Direct auth call failed: {str(direct_error)}")
            
            # Check if it's a specific Supabase error
            error_str = str(direct_error)
            if "Database error" in error_str:
                print("💡 This appears to be a database configuration issue")
                print("💡 Possible causes:")
                print("   - RLS policies blocking user creation")
                print("   - Missing database triggers")
                print("   - Incorrect table schema")
            elif "Email already registered" in error_str:
                print("💡 Email already exists - this is expected for duplicate tests")
            elif "Invalid email" in error_str:
                print("💡 Email format issue")
            else:
                print(f"💡 Unknown error: {error_str}")
        
        return False

async def test_existing_user():
    """Test registration with an existing user"""
    
    print("\n👥 Testing Registration with Existing User")
    print("=" * 40)
    
    # Use a known existing email
    existing_email = "test@example.com"
    
    try:
        registration_data = UserRegistration(
            email=existing_email,
            password="testpassword123",
            name="Test User",
            age=25,
            anonymous=False
        )
        
        print(f"📧 Attempting registration with existing email: {existing_email}")
        await auth_service.register_user(registration_data)
        print("❌ Registration succeeded unexpectedly")
        
    except Exception as e:
        print(f"✅ Registration correctly failed: {str(e)}")
        
        # Check if it's the expected error
        if "already exists" in str(e).lower():
            print("✅ Correctly detected existing user")
        else:
            print(f"⚠️ Unexpected error type: {str(e)}")

async def main():
    """Main test function"""
    
    print("🚀 Starting User Registration Tests")
    print("=" * 50)
    
    # Test 1: Simple registration
    success = await test_simple_registration()
    
    # Test 2: Existing user (if first test succeeded)
    if success:
        await test_existing_user()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Registration test completed successfully!")
        print("\n📧 Next steps:")
        print("1. Check your email for confirmation link")
        print("2. Click the confirmation link")
        print("3. Test login after confirmation")
    else:
        print("❌ Registration test failed")
        print("\n🔧 Troubleshooting:")
        print("1. Check Supabase dashboard for auth settings")
        print("2. Verify email confirmation is enabled")
        print("3. Check database schema and RLS policies")
        print("4. Verify redirect URLs are configured")

if __name__ == "__main__":
    asyncio.run(main())
