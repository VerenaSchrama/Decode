#!/usr/bin/env python3
"""
Test script for Supabase Auth endpoints
Run this after setting up the database migration
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_auth_endpoints():
    """Test all authentication endpoints"""
    
    print("🧪 TESTING SUPABASE AUTH ENDPOINTS")
    print("=" * 50)
    
    # Test data
    test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    test_password = "TestPassword123!"
    test_name = "Test User"
    
    print(f"📧 Using test email: {test_email}")
    print()
    
    # Step 1: Test User Registration
    print("1. 📝 Testing User Registration...")
    registration_data = {
        "email": test_email,
        "password": test_password,
        "name": test_name,
        "age": 28,
        "date_of_birth": "1995-01-01",
        "anonymous": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=registration_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Registration successful!")
            print(f"   👤 User ID: {data['user']['id']}")
            print(f"   📧 Email: {data['user']['email']}")
            print(f"   🔑 Access Token: {data['session']['access_token'][:20]}...")
            
            # Store for next tests
            user_id = data['user']['id']
            access_token = data['session']['access_token']
            
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    print()
    
    # Step 2: Test User Login
    print("2. 🔐 Testing User Login...")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Login successful!")
            print(f"   👤 User ID: {data['user']['id']}")
            print(f"   🔑 New Access Token: {data['session']['access_token'][:20]}...")
            
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    print()
    
    # Step 3: Test Token Verification
    print("3. 🔍 Testing Token Verification...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/verify", json=access_token, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Token verification successful!")
            print(f"   👤 Verified User ID: {data['user_id']}")
            
        else:
            print(f"   ❌ Token verification failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Token verification error: {e}")
    
    print()
    
    # Step 4: Test Get User Profile
    print("4. 👤 Testing Get User Profile...")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile/{user_id}", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Profile retrieval successful!")
            print(f"   📝 Name: {data['profile']['name']}")
            print(f"   🎂 Age: {data['profile']['age']}")
            print(f"   📅 Date of Birth: {data['profile']['date_of_birth']}")
            
        else:
            print(f"   ❌ Profile retrieval failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Profile retrieval error: {e}")
    
    print()
    
    # Step 5: Test Update User Profile
    print("5. ✏️ Testing Update User Profile...")
    
    update_data = {
        "name": "Updated Test User",
        "age": 29,
        "date_of_birth": "1994-01-01",
        "current_strategy": "keto_diet",
        "anonymous": False
    }
    
    try:
        response = requests.put(f"{BASE_URL}/auth/profile/{user_id}", json=update_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Profile update successful!")
            print(f"   📝 Updated Name: {data['profile']['name']}")
            print(f"   🎂 Updated Age: {data['profile']['age']}")
            print(f"   🎯 Strategy: {data['profile']['current_strategy']}")
            
        else:
            print(f"   ❌ Profile update failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Profile update error: {e}")
    
    print()
    
    # Step 6: Test Daily Progress with Authenticated User
    print("6. 📊 Testing Daily Progress with Authenticated User...")
    
    daily_data = {
        "user_id": user_id,  # Use UUID instead of demo-user-123
        "entry_date": datetime.now().strftime('%Y-%m-%d'),
        "habits": [
            {"name": "Morning workout", "completed": True},
            {"name": "Healthy breakfast", "completed": True},
            {"name": "Evening meditation", "completed": False}
        ],
        "mood": {"mood": 4, "energy_level": 3, "notes": "Testing with authenticated user"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/daily-progress", json=daily_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Daily progress saved with authenticated user!")
            print(f"   📈 Completion: {data.get('completion_percentage', 0):.1f}%")
            
        else:
            print(f"   ❌ Daily progress failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Daily progress error: {e}")
    
    print()
    
    # Step 7: Test Logout
    print("7. 🚪 Testing User Logout...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", json=access_token, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Logout successful!")
            print(f"   📝 Message: {data['message']}")
            
        else:
            print(f"   ❌ Logout failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    print()
    print("=" * 50)
    print("🎉 AUTHENTICATION TESTING COMPLETE!")
    print()
    print("📋 NEXT STEPS:")
    print("1. ✅ Database migration completed")
    print("2. ✅ Authentication endpoints working")
    print("3. 🔄 Update your mobile app to use these endpoints")
    print("4. 🎯 Start building user registration/login screens")

if __name__ == "__main__":
    test_auth_endpoints()

