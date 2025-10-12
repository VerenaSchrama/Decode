#!/usr/bin/env python3
"""
Test registration with real email domain
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

async def test_real_email_registration():
    """Test registration with a real email domain"""
    
    print("📧 Testing Registration with Real Email Domain")
    print("=" * 50)
    
    # Use a real email domain
    import time
    timestamp = int(time.time())
    test_email = f"test{timestamp}@gmail.com"  # Use Gmail domain
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
        error_str = str(e)
        if "Database error" in error_str:
            print("💡 Database error - this might be an RLS policy issue")
        elif "Email already registered" in error_str:
            print("💡 Email already exists")
        elif "Invalid email" in error_str:
            print("💡 Email validation failed")
        elif "Password should be at least" in error_str:
            print("💡 Password validation failed")
        else:
            print(f"💡 Unknown error: {error_str}")
        
        return False

async def test_different_email_domains():
    """Test with different email domains to see which ones work"""
    
    print("\n🌐 Testing Different Email Domains")
    print("=" * 40)
    
    domains = [
        "gmail.com",
        "yahoo.com", 
        "outlook.com",
        "hotmail.com",
        "test.com",  # This might be blocked
        "example.org"  # This might be blocked
    ]
    
    import time
    timestamp = int(time.time())
    
    for domain in domains:
        test_email = f"test{timestamp}@{domain}"
        print(f"\n📧 Testing: {test_email}")
        
        try:
            registration_data = UserRegistration(
                email=test_email,
                password="testpassword123",
                name="Test User",
                age=25,
                anonymous=False
            )
            
            registration_result = await auth_service.register_user(registration_data)
            print(f"✅ SUCCESS with {domain}")
            return True
            
        except Exception as e:
            error_str = str(e)
            if "Invalid email" in error_str:
                print(f"❌ BLOCKED: {domain} - Invalid email")
            elif "Database error" in error_str:
                print(f"⚠️ DATABASE ERROR: {domain} - {error_str}")
            else:
                print(f"❌ FAILED: {domain} - {error_str}")
        
        timestamp += 1  # Use different timestamp for each test
    
    return False

async def main():
    """Main test function"""
    
    print("🚀 Starting Email Domain Tests")
    print("=" * 50)
    
    # Test with Gmail first
    success = await test_real_email_registration()
    
    if not success:
        # Try different domains
        success = await test_different_email_domains()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Registration test completed successfully!")
        print("\n📧 Next steps:")
        print("1. Check your email for confirmation link")
        print("2. Click the confirmation link")
        print("3. Test login after confirmation")
    else:
        print("❌ All registration tests failed")
        print("\n🔧 Troubleshooting:")
        print("1. Check Supabase dashboard for email validation settings")
        print("2. Verify email confirmation is enabled")
        print("3. Check if email domains are whitelisted/blacklisted")
        print("4. Verify database schema and RLS policies")

if __name__ == "__main__":
    asyncio.run(main())
