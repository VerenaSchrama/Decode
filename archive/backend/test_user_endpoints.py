#!/usr/bin/env python3
"""
Test all user-specific API endpoints after database setup
"""

import requests
import json
from datetime import datetime, date

def test_all_endpoints():
    """Test all API endpoints systematically"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing all API endpoints...")
    print("=" * 50)
    
    # Test 1: Health endpoint
    print("\n1️⃣ Testing Health Endpoint")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ GET /health - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ GET /health - Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ GET /health - Error: {e}")
    
    # Test 2: Interventions endpoint
    print("\n2️⃣ Testing Interventions Endpoint")
    try:
        response = requests.get(f"{base_url}/interventions")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET /interventions - Working ({len(data.get('interventions', []))} interventions)")
        else:
            print(f"❌ GET /interventions - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET /interventions - Error: {e}")
    
    # Test 3: Recommend endpoint (minimal)
    print("\n3️⃣ Testing Recommend Endpoint (Minimal)")
    try:
        test_data = {
            "profile": {"name": "Test User", "age": 29},
            "symptoms": {"selected": ["PCOS"]},
            "consent": True
        }
        response = requests.post(f"{base_url}/recommend", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /recommend - Working ({len(data.get('interventions', []))} recommendations)")
        else:
            print(f"❌ POST /recommend - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ POST /recommend - Error: {e}")
    
    # Test 4: Recommend endpoint (full)
    print("\n4️⃣ Testing Recommend Endpoint (Full)")
    try:
        test_data = {
            "profile": {
                "name": "Test User",
                "age": 29,
                "dateOfBirth": "1995-01-01"
            },
            "lastPeriod": {
                "hasPeriod": True,
                "date": "2024-01-01",
                "cycleLength": 28
            },
            "symptoms": {
                "selected": ["PCOS", "Weight gain"],
                "additional": "Irregular cycles"
            },
            "interventions": {
                "selected": [{"intervention": "Control your bloodsugar", "helpful": False}],
                "additional": "Diet changes"
            },
            "dietaryPreferences": {
                "selected": ["Vegetarian"],
                "additional": "No dairy"
            },
            "consent": True
        }
        response = requests.post(f"{base_url}/recommend", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ POST /recommend (full) - Working ({len(data.get('interventions', []))} recommendations)")
            if 'cycle_phase' in data:
                print(f"   Cycle phase: {data['cycle_phase']}")
        else:
            print(f"❌ POST /recommend (full) - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ POST /recommend (full) - Error: {e}")
    
    # Test 5: User insights endpoint
    print("\n5️⃣ Testing User Insights Endpoint")
    user_id = "1"  # Use integer user_id
    try:
        response = requests.get(f"{base_url}/user/{user_id}/insights")
        if response.status_code == 200:
            print(f"✅ GET /user/{user_id}/insights - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ GET /user/{user_id}/insights - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET /user/{user_id}/insights - Error: {e}")
    
    # Test 6: User habits endpoint
    print("\n6️⃣ Testing User Habits Endpoint")
    try:
        response = requests.get(f"{base_url}/user/{user_id}/habits")
        if response.status_code == 200:
            print(f"✅ GET /user/{user_id}/habits - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ GET /user/{user_id}/habits - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET /user/{user_id}/habits - Error: {e}")
    
    # Test 7: Intervention submission endpoint
    print("\n7️⃣ Testing Intervention Submission Endpoint")
    try:
        test_data = {
            "name": "Test Intervention",
            "description": "A test intervention for PCOS",
            "profile_match": "Women with PCOS and weight issues",
            "scientific_source": "Test scientific basis",
            "habits": [
                {
                    "number": 1,
                    "description": "Replace high-carb foods with low-carb alternatives"
                }
            ]
        }
        response = requests.post(f"{base_url}/interventions/submit", json=test_data)
        if response.status_code == 200:
            print("✅ POST /interventions/submit - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ POST /interventions/submit - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ POST /interventions/submit - Error: {e}")
    
    # Test 8: Daily progress endpoint
    print("\n8️⃣ Testing Daily Progress Endpoint")
    try:
        test_data = {
            "user_id": 1,  # Use integer user_id
            "date": str(date.today()),
            "habits_completed": ["Low-carb swap", "Add fat"],
            "mood": "good",
            "notes": "Feeling better today"
        }
        response = requests.post(f"{base_url}/daily-progress", json=test_data)
        if response.status_code == 200:
            print("✅ POST /daily-progress - Working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ POST /daily-progress - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ POST /daily-progress - Error: {e}")
    
    # Test 9: Chat message endpoint
    print("\n9️⃣ Testing Chat Message Endpoint")
    try:
        test_data = {
            "user_id": 1,  # Use integer user_id
            "message": "Hello, I have PCOS and want to know about diet recommendations"
        }
        response = requests.post(f"{base_url}/chat/message", json=test_data)
        if response.status_code == 200:
            print("✅ POST /chat/message - Working")
            data = response.json()
            print(f"   Message length: {len(data.get('message', ''))}")
        else:
            print(f"❌ POST /chat/message - Failed ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ POST /chat/message - Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API endpoint testing complete!")

if __name__ == "__main__":
    test_all_endpoints()
