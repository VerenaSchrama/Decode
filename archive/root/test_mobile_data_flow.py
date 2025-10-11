#!/usr/bin/env python3
"""
Test mobile app data flow and transformation
"""

import requests
import json

def test_mobile_data_flow():
    """Test the complete mobile app data flow"""
    
    print("🚀 Testing Mobile App Data Flow")
    print("=" * 60)
    
    # Simulate the exact data structure that the mobile app sends
    mobile_intake_data = {
        "profile": {
            "name": "Test User",
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
    
    print("\n1️⃣ Mobile App Intake Data")
    print("-" * 40)
    print(f"📱 Mobile intake data: {json.dumps(mobile_intake_data, indent=2)}")
    
    # Transform to API format (as done in mobile app)
    calculated_age = 28  # Simulate age calculation
    api_request_data = {
        "profile": {
            "name": mobile_intake_data["profile"]["name"],
            "age": calculated_age,
        },
        "lastPeriod": mobile_intake_data["lastPeriod"],
        "symptoms": mobile_intake_data["symptoms"],
        "interventions": mobile_intake_data["interventions"],
        "dietaryPreferences": mobile_intake_data["dietaryPreferences"],
        "consent": mobile_intake_data["consent"],
    }
    
    print("\n2️⃣ API Request Data")
    print("-" * 40)
    print(f"📤 API request: {json.dumps(api_request_data, indent=2)}")
    
    # Make API call
    print("\n3️⃣ Making API Call")
    print("-" * 40)
    
    try:
        response = requests.post(
            "http://localhost:8000/recommend",
            json=api_request_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            api_response = response.json()
            print("✅ API Response successful!")
            
            # Simulate mobile app transformation
            print("\n4️⃣ Mobile App Data Transformation")
            print("-" * 40)
            
            if api_response.get('interventions') and isinstance(api_response['interventions'], list):
                transformed_data = {
                    **api_response,
                    "interventions": [
                        {
                            "id": intervention["intervention_id"],
                            "name": intervention["intervention_name"],
                            "profile_match": intervention["intervention_profile"],
                            "similarity_score": intervention["similarity_score"],
                            "scientific_source": intervention["scientific_source"],
                            "habits": [
                                {
                                    "number": index + 1,
                                    "description": habit
                                }
                                for index, habit in enumerate(intervention.get("habits", []))
                            ]
                        }
                        for intervention in api_response["interventions"]
                    ]
                }
                
                print("✅ Data transformation successful!")
                print(f"📋 Transformed data structure:")
                print(f"   - intake_summary: {len(transformed_data.get('intake_summary', ''))} chars")
                print(f"   - interventions: {len(transformed_data.get('interventions', []))} items")
                print(f"   - total_found: {transformed_data.get('total_found', 0)}")
                
                if transformed_data.get('interventions'):
                    first_intervention = transformed_data['interventions'][0]
                    print(f"\n📋 First transformed intervention:")
                    print(f"   - id: {first_intervention.get('id')}")
                    print(f"   - name: {first_intervention.get('name')}")
                    print(f"   - profile_match: {len(first_intervention.get('profile_match', ''))} chars")
                    print(f"   - similarity_score: {first_intervention.get('similarity_score')}")
                    print(f"   - habits: {len(first_intervention.get('habits', []))} items")
                    
                    print(f"\n📋 All transformed intervention field names:")
                    for key in first_intervention.keys():
                        print(f"   - {key}")
                
                return True
            else:
                print("❌ No interventions in API response")
                return False
        else:
            print(f"❌ API Response failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API Request failed: {e}")
        return False

if __name__ == "__main__":
    test_mobile_data_flow()

