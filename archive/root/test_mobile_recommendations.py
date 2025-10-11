#!/usr/bin/env python3
"""
Test mobile app recommendations API call
"""

import requests
import json

def test_mobile_recommendations():
    """Test the mobile app recommendations API call"""
    
    print("🚀 Testing Mobile App Recommendations API Call")
    print("=" * 60)
    
    # Test data that matches the mobile app format
    test_data = {
        "profile": {
            "name": "Test User",
            "age": 28,
            "dateOfBirth": "1996-01-01"
        },
        "lastPeriod": {
            "date": "2024-01-15",
            "hasPeriod": True,
            "cycleLength": 28
        },
        "symptoms": {
            "selected": ["PCOS", "Weight gain"],
            "additional": "Testing from mobile browser"
        },
        "interventions": {
            "selected": [],
            "additional": ""
        },
        "dietaryPreferences": {
            "selected": ["Vegetarian"],
            "additional": "No dairy"
        },
        "consent": True,
        "anonymous": False
    }
    
    print("\n1️⃣ Sending API Request")
    print("-" * 40)
    print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/recommend",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response successful!")
            print(f"📋 Response structure:")
            print(f"   - intake_summary: {len(data.get('intake_summary', ''))} chars")
            print(f"   - interventions: {len(data.get('interventions', []))} items")
            print(f"   - total_found: {data.get('total_found', 0)}")
            print(f"   - min_similarity_used: {data.get('min_similarity_used', 0)}")
            
            if data.get('interventions'):
                print(f"\n📋 First intervention structure:")
                first_intervention = data['interventions'][0]
                print(f"   - intervention_id: {first_intervention.get('intervention_id')}")
                print(f"   - intervention_name: {first_intervention.get('intervention_name')}")
                print(f"   - intervention_profile: {len(first_intervention.get('intervention_profile', ''))} chars")
                print(f"   - similarity_score: {first_intervention.get('similarity_score')}")
                print(f"   - habits: {len(first_intervention.get('habits', []))} items")
                print(f"   - scientific_source: {first_intervention.get('scientific_source')}")
                
                print(f"\n📋 All intervention field names:")
                for key in first_intervention.keys():
                    print(f"   - {key}")
            
            return True
        else:
            print(f"❌ API Response failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return False

if __name__ == "__main__":
    test_mobile_recommendations()

