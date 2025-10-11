#!/usr/bin/env python3
"""
Test mobile app directly
"""

import requests
import json

def test_mobile_app():
    """Test the mobile app directly"""
    
    print("🚀 Testing Mobile App Directly")
    print("=" * 60)
    
    # Test 1: Check if mobile app is accessible
    print("\n1️⃣ Checking Mobile App Accessibility")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Mobile app is accessible")
        else:
            print(f"❌ Mobile app not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mobile app not accessible: {e}")
        return False
    
    # Test 2: Check if backend API is accessible
    print("\n2️⃣ Checking Backend API Accessibility")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend API is accessible")
        else:
            print(f"❌ Backend API not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API not accessible: {e}")
        return False
    
    # Test 3: Test API endpoint with CORS
    print("\n3️⃣ Testing API Endpoint with CORS")
    print("-" * 40)
    
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
    
    try:
        response = requests.post(
            "http://localhost:8000/recommend",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working with CORS")
            print(f"   - Interventions: {len(data.get('interventions', []))}")
            print(f"   - Total found: {data.get('total_found', 0)}")
            return True
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API endpoint failed: {e}")
        return False

if __name__ == "__main__":
    test_mobile_app()

