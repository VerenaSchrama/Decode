#!/usr/bin/env python3
"""
Test intervention submission with existing user
"""

import requests
import json

def test_intervention_submission():
    """Test intervention submission with existing user"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Intervention Submission with Existing User")
    print("=" * 60)
    
    # Test intervention submission with existing user ID
    print("\n1️⃣ Testing Intervention Submission")
    print("-" * 40)
    
    intervention_data = {
        "name": "PCOS-Friendly Smoothie Bowl",
        "description": "A nutrient-dense smoothie bowl specifically designed for PCOS management",
        "profile_match": "Women with PCOS who struggle with breakfast options",
        "scientific_source": "Based on research on PCOS and nutrient timing",
        "habits": [
            {
                "number": 1,
                "description": "Prepare smoothie base the night before"
            },
            {
                "number": 2,
                "description": "Add protein powder for blood sugar stability"
            },
            {
                "number": 3,
                "description": "Top with seeds for hormone balance"
            }
        ]
    }
    
    try:
        # Test with user_id=21 (existing user)
        response = requests.post(f"{base_url}/interventions/submit?user_id=21", json=intervention_data)
        
        if response.status_code == 200:
            intervention = response.json()
            print("✅ Intervention submission successful!")
            print(f"   Intervention ID: {intervention.get('id', 'N/A')}")
            print(f"   Status: {intervention.get('status', 'N/A')}")
            print(f"   Name: {intervention.get('name', 'N/A')}")
        else:
            print(f"❌ Intervention submission failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Intervention submission error: {e}")
    
    # Test user insights with existing user
    print("\n2️⃣ Testing User Insights with Existing User")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/user/21/insights")
        if response.status_code == 200:
            insights = response.json()
            print("✅ User insights working")
            print(f"   Total habits tried: {insights.get('total_habits_tried', 0)}")
            print(f"   Success rate: {insights.get('success_rate', 0)}%")
        else:
            print(f"❌ User insights failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User insights error: {e}")
    
    # Test user habits with existing user
    print("\n3️⃣ Testing User Habits with Existing User")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/user/21/habits")
        if response.status_code == 200:
            habits = response.json()
            print("✅ User habits working")
            print(f"   Habits found: {len(habits.get('habits', []))}")
        else:
            print(f"❌ User habits failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User habits error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Intervention Submission Test Complete!")

if __name__ == "__main__":
    test_intervention_submission()

