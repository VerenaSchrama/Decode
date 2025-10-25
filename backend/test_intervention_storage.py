#!/usr/bin/env python3
"""
Test script to verify intervention storage during intake process
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_intervention_storage():
    """Test the complete intervention storage flow"""
    
    print("🧪 Testing Intervention Storage Flow")
    print("=" * 50)
    
    # Step 1: Create test user (if needed)
    print("Step 1: Creating test user...")
    try:
        register_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "profile": {
                "name": "Test User",
                "age": 25,
                "date_of_birth": "1999-01-01",
                "anonymous": False
            }
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ Test user created successfully")
            auth_data = response.json()
            access_token = auth_data.get("access_token")
            user_id = auth_data.get("user", {}).get("id")
        else:
            print(f"⚠️ User creation failed: {response.status_code}")
            print("Trying to login instead...")
            
            # Try to login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                auth_data = response.json()
                access_token = auth_data.get("access_token")
                user_id = auth_data.get("user", {}).get("id")
                print("✅ Login successful")
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Create test intake data
    print("\nStep 2: Creating test intake...")
    try:
        intake_data = {
            "profile": {
                "name": "Test User",
                "age": 25,
                "dateOfBirth": "1999-01-01"
            },
            "symptoms": {
                "selected": ["PCOS", "Irregular periods"],
                "additional": "Some additional symptoms"
            },
            "interventions": {
                "selected": [],
                "additional": ""
            },
            "habits": {
                "selected": [],
                "additional": ""
            },
            "dietaryPreferences": {
                "selected": ["Vegetarian"],
                "additional": ""
            },
            "lastPeriod": {
                "hasPeriod": True,
                "lastPeriodDate": "2024-01-01",
                "cycleLength": 28,
                "cyclePhase": "follicular"
            },
            "consent": True
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{BASE_URL}/recommend", json=intake_data, headers=headers)
        
        if response.status_code == 200:
            recommendations = response.json()
            print("✅ Intake processed successfully")
            print(f"📊 Found {len(recommendations.get('interventions', []))} interventions")
        else:
            print(f"❌ Intake failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Intake error: {e}")
        return False
    
    # Step 3: Start intervention period
    print("\nStep 3: Starting intervention period...")
    try:
        if recommendations.get('interventions'):
            intervention = recommendations['interventions'][0]  # Take first intervention
            
            period_data = {
                "intake_id": "test-intake-id",  # This would come from intake response
                "intervention_name": intervention.get('name', 'Test Intervention'),
                "selected_habits": [habit.get('description', '') for habit in intervention.get('habits', [])],
                "intervention_id": intervention.get('id'),
                "planned_duration_days": 30,
                "cycle_phase": "follicular"
            }
            
            response = requests.post(f"{BASE_URL}/intervention-periods/start", json=period_data, headers=headers)
            
            if response.status_code == 200:
                period_result = response.json()
                print("✅ Intervention period started successfully")
                print(f"📋 Period ID: {period_result.get('period_id')}")
            else:
                print(f"❌ Intervention period start failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print("❌ No interventions found in recommendations")
            return False
            
    except Exception as e:
        print(f"❌ Intervention period error: {e}")
        return False
    
    # Step 4: Verify intervention was stored
    print("\nStep 4: Verifying intervention storage...")
    try:
        response = requests.get(f"{BASE_URL}/intervention-periods/history", headers=headers)
        
        if response.status_code == 200:
            history = response.json()
            periods = history.get('periods', [])
            print(f"✅ Found {len(periods)} intervention periods")
            
            if periods:
                latest_period = periods[0]
                print(f"📋 Latest intervention: {latest_period.get('intervention_name')}")
                print(f"📅 Start date: {latest_period.get('start_date')}")
                print(f"📊 Status: {latest_period.get('status')}")
                print("✅ Intervention storage test PASSED!")
                return True
            else:
                print("❌ No intervention periods found")
                return False
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    success = test_intervention_storage()
    if success:
        print("\n🎉 All tests passed! Intervention storage is working correctly.")
    else:
        print("\n❌ Tests failed. Check the errors above.")
