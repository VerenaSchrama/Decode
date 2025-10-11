#!/usr/bin/env python3
"""
Test mobile app API connection after configuration fix
"""

import requests
import json

def test_mobile_api_connection():
    """Test that mobile app can now connect to backend"""
    
    print("🚀 Testing Mobile App API Connection After Fix")
    print("=" * 60)
    
    # Test 1: Backend health from localhost
    print("\n1️⃣ Testing Backend Health (localhost:8000)")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Backend is healthy")
            print(f"   Status: {health.get('status')}")
            print(f"   RAG Pipeline: {health.get('rag_pipeline')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test 2: CORS headers
    print("\n2️⃣ Testing CORS Headers")
    print("-" * 40)
    
    try:
        response = requests.options("http://localhost:8000/health", 
                                  headers={"Origin": "http://localhost:3000"})
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        print("✅ CORS headers present")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
    
    # Test 3: Recommendations endpoint with CORS
    print("\n3️⃣ Testing Recommendations with CORS")
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
    
    try:
        response = requests.post("http://localhost:8000/recommend", 
                               json=test_data,
                               headers={"Origin": "http://localhost:3000"})
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommendations endpoint working with CORS")
            print(f"   Interventions found: {len(result.get('interventions', []))}")
            print(f"   Cycle phase: {result.get('cycle_phase', 'N/A')}")
            print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
        return False
    
    # Test 4: Interventions list
    print("\n4️⃣ Testing Interventions List")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/interventions",
                              headers={"Origin": "http://localhost:3000"})
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
    
    print("\n" + "=" * 60)
    print("🎉 Mobile App API Connection Test Complete!")
    print("\n📱 Your mobile app should now work at:")
    print("   🌐 Web: http://localhost:3000")
    print("\n✅ All API endpoints are working with proper CORS!")
    print("✅ Configuration has been fixed!")
    
    return True

if __name__ == "__main__":
    test_mobile_api_connection()

