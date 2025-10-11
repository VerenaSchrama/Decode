#!/usr/bin/env python3
"""
Test mobile app connection to backend
"""

import requests
import json

def test_mobile_connection():
    """Test that mobile app can connect to backend"""
    
    print("🚀 Testing Mobile App Connection to Backend")
    print("=" * 60)
    
    # Test backend health
    print("\n1️⃣ Testing Backend Health")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {health.get('status')}")
            print(f"   RAG Pipeline: {health.get('rag_pipeline')}")
            print(f"   OpenAI API: {health.get('openai_api_key')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test recommendations endpoint
    print("\n2️⃣ Testing Recommendations Endpoint")
    print("-" * 40)
    
    test_data = {
        "profile": {
            "name": "Mobile Test User",
            "age": 25,
            "dateOfBirth": "1999-01-01"
        },
        "lastPeriod": {
            "date": "2024-01-10",
            "hasPeriod": True,
            "cycleLength": 30
        },
        "symptoms": {
            "selected": ["PCOS", "Weight gain"],
            "additional": "Testing from mobile"
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
    
    try:
        response = requests.post("http://localhost:8000/recommend", json=test_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommendations endpoint working")
            print(f"   Interventions found: {len(result.get('interventions', []))}")
            print(f"   Cycle phase: {result.get('cycle_phase', 'N/A')}")
            print(f"   Intake summary length: {len(result.get('intake_summary', ''))}")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
        return False
    
    # Test interventions list
    print("\n3️⃣ Testing Interventions List")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/interventions")
        if response.status_code == 200:
            interventions = response.json()
            print("✅ Interventions list working")
            print(f"   Total interventions: {len(interventions.get('interventions', []))}")
        else:
            print(f"❌ Interventions list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Interventions list error: {e}")
        return False
    
    # Test user insights
    print("\n4️⃣ Testing User Insights")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/user/21/insights")
        if response.status_code == 200:
            insights = response.json()
            print("✅ User insights working")
            print(f"   Total habits tried: {insights.get('total_habits_tried', 0)}")
            print(f"   Success rate: {insights.get('success_rate', 0)}%")
        else:
            print(f"❌ User insights failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User insights error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Mobile App Connection Test Complete!")
    print("\n📱 Your mobile app should now work at:")
    print("   🌐 Web: http://localhost:3000")
    print("   📱 Mobile: Scan QR code in terminal")
    print("\n✅ All backend endpoints are working!")
    
    return True

if __name__ == "__main__":
    test_mobile_connection()

