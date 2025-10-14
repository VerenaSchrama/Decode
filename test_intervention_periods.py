#!/usr/bin/env python3
"""
Test Intervention Period Tracking System
Tests the complete flow from intake to intervention period tracking
"""

import requests
import json
import time
from datetime import datetime

class InterventionPeriodTest:
    def __init__(self):
        self.backend_url = "https://api.decode-app.nl"
        self.test_email = f"test_intervention_{int(time.time())}@example.com"
        self.test_password = "TestPassword123!"
        self.access_token = None
        self.user_id = None
        self.intake_id = None
        
    def run_complete_test(self):
        """Run complete intervention period tracking test"""
        print("🚀 Starting Intervention Period Tracking Test")
        print(f"📧 Test email: {self.test_email}")
        print("="*60)
        
        # Step 1: Register user
        self.test_user_registration()
        
        # Step 2: Login user
        self.test_user_login()
        
        # Step 3: Complete intake and get recommendations
        self.test_intake_and_recommendations()
        
        # Step 4: Start intervention period
        self.test_start_intervention_period()
        
        # Step 5: Check active intervention
        self.test_get_active_intervention()
        
        # Step 6: Complete intervention
        self.test_complete_intervention()
        
        # Step 7: Check intervention history
        self.test_get_intervention_history()
        
        print("\n" + "="*60)
        print("📊 INTERVENTION PERIOD TRACKING TEST COMPLETE")
        print("="*60)
        
    def test_user_registration(self):
        """Test user registration"""
        print("\n1️⃣ Testing User Registration...")
        
        try:
            reg_data = {
                "email": self.test_email,
                "password": self.test_password,
                "age": 28,
                "name": "Test User"
            }
            
            response = requests.post(f"{self.backend_url}/auth/register", json=reg_data, timeout=15)
            print(f"   Registration Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("   ✅ User registration successful")
            else:
                print(f"   ❌ Registration failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            
    def test_user_login(self):
        """Test user login"""
        print("\n2️⃣ Testing User Login...")
        
        try:
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = requests.post(f"{self.backend_url}/auth/login", json=login_data, timeout=15)
            print(f"   Login Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                login_result = response.json()
                self.access_token = login_result.get("access_token")
                self.user_id = login_result.get("user", {}).get("id")
                print(f"   ✅ Login successful - User ID: {self.user_id}")
            else:
                print(f"   ❌ Login failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            
    def test_intake_and_recommendations(self):
        """Test intake completion and recommendations"""
        print("\n3️⃣ Testing Intake and Recommendations...")
        
        try:
            intake_data = {
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
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"{self.backend_url}/recommend", json=intake_data, headers=headers, timeout=30)
            print(f"   Recommendations Status: {response.status_code}")
            
            if response.status_code == 200:
                rec_result = response.json()
                print("   ✅ Recommendations generated successfully")
                
                # Extract intake ID from data collection result
                if "data_collection" in rec_result:
                    data_collection = rec_result["data_collection"]
                    self.intake_id = data_collection.get("intake_id")
                    print(f"   📝 Intake ID: {self.intake_id}")
                    
                # Extract intervention data
                if "interventions" in rec_result and rec_result["interventions"]:
                    self.test_intervention = rec_result["interventions"][0]
                    print(f"   🎯 Test intervention: {self.test_intervention.get('name', 'Unknown')}")
                else:
                    print("   ⚠️ No interventions in response")
            else:
                print(f"   ❌ Recommendations failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Intake error: {e}")
            
    def test_start_intervention_period(self):
        """Test starting intervention period tracking"""
        print("\n4️⃣ Testing Start Intervention Period...")
        
        try:
            if not self.intake_id or not hasattr(self, 'test_intervention'):
                print("   ⚠️ Skipping - no intake ID or intervention data")
                return
                
            start_data = {
                "intake_id": self.intake_id,
                "intervention_name": self.test_intervention.get("name", "Test Intervention"),
                "selected_habits": [habit.get("description", f"Habit {i}") for i, habit in enumerate(self.test_intervention.get("habits", []))],
                "intervention_id": self.test_intervention.get("id"),
                "planned_duration_days": 30,
                "cycle_phase": "follicular"
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"{self.backend_url}/intervention-periods/start", json=start_data, headers=headers, timeout=15)
            print(f"   Start Period Status: {response.status_code}")
            
            if response.status_code == 200:
                start_result = response.json()
                self.period_id = start_result.get("period_id")
                print(f"   ✅ Intervention period started - Period ID: {self.period_id}")
            else:
                print(f"   ❌ Start period failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Start period error: {e}")
            
    def test_get_active_intervention(self):
        """Test getting active intervention"""
        print("\n5️⃣ Testing Get Active Intervention...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.backend_url}/intervention-periods/active", headers=headers, timeout=15)
            print(f"   Get Active Status: {response.status_code}")
            
            if response.status_code == 200:
                active_result = response.json()
                if active_result.get("found"):
                    period = active_result.get("period")
                    print(f"   ✅ Active intervention found: {period.get('intervention_name', 'Unknown')}")
                    print(f"   📊 Status: {period.get('status', 'Unknown')}")
                    print(f"   📅 Start Date: {period.get('start_date', 'Unknown')}")
                else:
                    print("   ⚠️ No active intervention found")
            else:
                print(f"   ❌ Get active failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Get active error: {e}")
            
    def test_complete_intervention(self):
        """Test completing intervention"""
        print("\n6️⃣ Testing Complete Intervention...")
        
        try:
            if not hasattr(self, 'period_id'):
                print("   ⚠️ Skipping - no period ID")
                return
                
            complete_data = {
                "completion_percentage": 85.0,
                "notes": "Test completion - 85% completed"
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.put(f"{self.backend_url}/intervention-periods/{self.period_id}/complete", json=complete_data, headers=headers, timeout=15)
            print(f"   Complete Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Intervention completed successfully")
            else:
                print(f"   ❌ Complete failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Complete error: {e}")
            
    def test_get_intervention_history(self):
        """Test getting intervention history"""
        print("\n7️⃣ Testing Get Intervention History...")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{self.backend_url}/intervention-periods/history", headers=headers, timeout=15)
            print(f"   History Status: {response.status_code}")
            
            if response.status_code == 200:
                history_result = response.json()
                periods = history_result.get("periods", [])
                count = history_result.get("count", 0)
                print(f"   ✅ Intervention history retrieved - {count} periods")
                
                for i, period in enumerate(periods):
                    print(f"   📋 Period {i+1}: {period.get('intervention_name', 'Unknown')} - {period.get('status', 'Unknown')}")
            else:
                print(f"   ❌ History failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ History error: {e}")

def main():
    """Main test execution"""
    test_suite = InterventionPeriodTest()
    test_suite.run_complete_test()

if __name__ == "__main__":
    main()
