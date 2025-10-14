#!/usr/bin/env python3
"""
Manual HerFoodCode User Journey Test
Simplified version for quick validation without browser automation
"""

import requests
import json
import time
from datetime import datetime

class ManualTestSuite:
    def __init__(self):
        self.frontend_url = "https://decodev1.vercel.app"
        self.backend_url = "https://api.decode-app.nl"
        self.timestamp = int(time.time())
        self.test_email = f"manual_test_{self.timestamp}@example.com"
        self.results = {}
        
    def run_tests(self):
        """Run manual tests"""
        print("🚀 Starting Manual HerFoodCode Test Suite")
        print(f"📧 Test email: {self.test_email}")
        print(f"🌐 Frontend: {self.frontend_url}")
        print(f"🔧 Backend: {self.backend_url}")
        print("="*60)
        
        # Test 1: Frontend availability
        self.test_frontend_availability()
        
        # Test 2: Backend health
        self.test_backend_health()
        
        # Test 3: Backend API endpoints
        self.test_backend_endpoints()
        
        # Test 4: CORS configuration
        self.test_cors_configuration()
        
        # Generate report
        self.generate_report()
        
    def test_frontend_availability(self):
        """Test if frontend is accessible"""
        print("\n1️⃣ Testing Frontend Availability...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Frontend is accessible")
                self.results["frontend_availability"] = True
                
                # Check if it's a React app
                if "react" in response.text.lower() or "next" in response.text.lower():
                    print("   ✅ React/Next.js app detected")
                else:
                    print("   ⚠️ React/Next.js not clearly detected")
            else:
                print(f"   ❌ Frontend returned {response.status_code}")
                self.results["frontend_availability"] = False
                
        except Exception as e:
            print(f"   ❌ Frontend test failed: {e}")
            self.results["frontend_availability"] = False
            
    def test_backend_health(self):
        """Test backend health endpoint"""
        print("\n2️⃣ Testing Backend Health...")
        
        try:
            health_url = f"{self.backend_url}/health"
            response = requests.get(health_url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health response: {health_data}")
                
                # Validate expected structure (flexible field names)
                if "status" in health_data and health_data["status"] == "healthy":
                    print("   ✅ Health response structure valid")
                    self.results["backend_health"] = True
                else:
                    print(f"   ⚠️ Health status not 'healthy'. Got: {health_data}")
                    self.results["backend_health"] = False
            else:
                print(f"   ❌ Backend health failed: {response.status_code}")
                self.results["backend_health"] = False
                
        except Exception as e:
            print(f"   ❌ Backend health test failed: {e}")
            self.results["backend_health"] = False
            
    def test_backend_endpoints(self):
        """Test various backend endpoints"""
        print("\n3️⃣ Testing Backend Endpoints...")
        
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/user/demo-user-123/streak", "User streak"),
            ("/user/demo-user-123/daily-progress", "Daily progress"),
            ("/recommend", "Recommendations")
        ]
        
        endpoint_results = {}
        
        for endpoint, description in endpoints_to_test:
            try:
                url = f"{self.backend_url}{endpoint}"
                
                if endpoint == "/recommend":
                    # POST request for recommendations
                    test_data = {
                        "profile": {
                            "name": "Test User",
                            "age": 28
                        },
                        "lastPeriod": {
                            "date": "2024-01-01",
                            "cycleLength": 28,
                            "hasPeriod": True
                        },
                        "symptoms": {
                            "selected": ["Cramps", "Bloating"],
                            "additional": "Test symptoms"
                        },
                        "dietaryPreferences": {
                            "selected": ["Vegetarian"],
                            "additional": "Test dietary preferences"
                        },
                        "consent": True,
                        "anonymous": False
                    }
                    response = requests.post(url, json=test_data, timeout=30)
                else:
                    # GET request for other endpoints
                    response = requests.get(url, timeout=10)
                    
                print(f"   {description}: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    print(f"   ✅ {description} working")
                    endpoint_results[endpoint] = True
                else:
                    print(f"   ⚠️ {description} returned {response.status_code}")
                    endpoint_results[endpoint] = False
                    
            except Exception as e:
                print(f"   ❌ {description} failed: {e}")
                endpoint_results[endpoint] = False
                
        # Overall endpoint success rate
        successful_endpoints = sum(1 for success in endpoint_results.values() if success)
        total_endpoints = len(endpoint_results)
        
        print(f"   📊 Endpoints: {successful_endpoints}/{total_endpoints} working")
        self.results["backend_endpoints"] = successful_endpoints >= total_endpoints * 0.8  # 80% success rate
        
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n4️⃣ Testing CORS Configuration...")
        
        try:
            # Test preflight request
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=10)
            print(f"   Preflight Status: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print(f"   CORS Headers: {cors_headers}")
            
            if cors_headers['Access-Control-Allow-Origin']:
                print("   ✅ CORS headers present")
                self.results["cors_configuration"] = True
            else:
                print("   ⚠️ CORS headers missing")
                self.results["cors_configuration"] = False
                
        except Exception as e:
            print(f"   ❌ CORS test failed: {e}")
            self.results["cors_configuration"] = False
            
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📊 MANUAL TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for success in self.results.values() if success)
        
        print(f"📈 Overall Score: {passed_tests}/{total_tests} tests passed")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name.replace('_', ' ').title()}: {status}")
            
        print("\n🎯 Next Steps:")
        if passed_tests == total_tests:
            print("  🎉 All manual tests passed! Ready for full user journey test.")
            print("  💡 Run: python test_user_journey.py for complete browser automation test")
        else:
            print("  ⚠️ Some tests failed. Check the issues above before proceeding.")
            print("  🔧 Fix backend/frontend issues, then re-run tests")
            
        print("\n📝 Manual Testing Instructions:")
        print("  1. Open browser and visit https://decodev1.vercel.app")
        print("  2. Try registering with a test email")
        print("  3. Check browser console for errors")
        print("  4. Verify localStorage contains auth tokens after login")
        print("  5. Test navigation between screens")
        print("  6. Try logging out and verify cleanup")
        
        print("\n" + "="*60)

def main():
    """Main execution"""
    test_suite = ManualTestSuite()
    test_suite.run_tests()

if __name__ == "__main__":
    main()
