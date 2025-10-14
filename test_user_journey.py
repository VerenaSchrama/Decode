#!/usr/bin/env python3
"""
HerFoodCode User Journey Test Suite
Simulates complete user flow: registration → login → data persistence → backend API interaction
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, expect
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HerFoodCodeTestSuite:
    def __init__(self):
        self.frontend_url = "https://decodev1.vercel.app"
        self.backend_url = "https://api.decode-app.nl"
        self.timestamp = int(time.time())
        self.test_email = f"testuser_{self.timestamp}@example.com"
        self.test_password = "HerFoodCode123!"
        self.test_age = 28
        self.results = {
            "registration": False,
            "auth_token_persisted": False,
            "backend_health": False,
            "user_data_persistence": False,
            "token_refresh": False,
            "logout_cleanup": False,
            "errors": []
        }
        
    async def run_full_journey(self):
        """Execute complete user journey test"""
        logger.info("🚀 Starting HerFoodCode User Journey Test Suite")
        logger.info(f"Test email: {self.test_email}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Set to True for CI
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 1️⃣ Visit frontend
                await self.step_1_visit_frontend(page)
                
                # 2️⃣ Register new user
                await self.step_2_register_user(page)
                
                # 3️⃣ Simulate email verification
                await self.step_3_simulate_verification(page)
                
                # 4️⃣ Verify session storage
                await self.step_4_verify_session_storage(page)
                
                # 5️⃣ Test backend health
                await self.step_5_test_backend_health()
                
                # 6️⃣ Test user data persistence
                await self.step_6_test_user_data_persistence()
                
                # 7️⃣ Simulate multi-day session
                await self.step_7_simulate_multi_day_session(page)
                
                # 8️⃣ Test logout cleanup
                await self.step_8_test_logout_cleanup(page)
                
            except Exception as e:
                logger.error(f"❌ Test failed: {e}")
                self.results["errors"].append(str(e))
            finally:
                await browser.close()
                
        # Generate final report
        self.generate_report()
        
    async def step_1_visit_frontend(self, page):
        """Step 1: Visit frontend and verify it loads"""
        logger.info("1️⃣ Visiting frontend...")
        
        try:
            await page.goto(self.frontend_url, timeout=30000)
            await page.wait_for_load_state('networkidle')
            
            # Check if we're on login/register screen
            login_button = await page.locator('text=Login').first
            register_button = await page.locator('text=Register').first
            
            if await login_button.is_visible() or await register_button.is_visible():
                logger.info("✅ Frontend loaded successfully - Auth screen visible")
                self.results["registration"] = True
            else:
                logger.warning("⚠️ Auth screen not immediately visible")
                
        except Exception as e:
            logger.error(f"❌ Frontend visit failed: {e}")
            self.results["errors"].append(f"Frontend visit: {e}")
            
    async def step_2_register_user(self, page):
        """Step 2: Register new user with realistic data"""
        logger.info("2️⃣ Registering new user...")
        
        try:
            # Click register button
            register_button = page.locator('text=Register').first
            await register_button.click()
            await page.wait_for_timeout(1000)
            
            # Fill registration form
            email_input = page.locator('input[type="email"]')
            password_input = page.locator('input[type="password"]').first
            age_input = page.locator('input[type="number"]')
            terms_checkbox = page.locator('input[type="checkbox"]')
            
            await email_input.fill(self.test_email)
            await password_input.fill(self.test_password)
            await age_input.fill(str(self.test_age))
            await terms_checkbox.check()
            
            # Submit registration
            submit_button = page.locator('button[type="submit"]')
            await submit_button.click()
            
            # Wait for registration response
            await page.wait_for_timeout(3000)
            
            # Check for success message or redirect
            success_indicators = [
                'text=Registration successful',
                'text=Check your email',
                'text=Email sent',
                'text=Verify your email'
            ]
            
            success_found = False
            for indicator in success_indicators:
                if await page.locator(indicator).is_visible():
                    logger.info(f"✅ Registration successful - {indicator}")
                    success_found = True
                    break
                    
            if not success_found:
                # Check for error messages
                error_elements = await page.locator('[class*="error"], [class*="Error"]').all()
                if error_elements:
                    for element in error_elements:
                        error_text = await element.text_content()
                        logger.warning(f"⚠️ Registration error: {error_text}")
                        
            self.results["registration"] = success_found
            
        except Exception as e:
            logger.error(f"❌ Registration failed: {e}")
            self.results["errors"].append(f"Registration: {e}")
            
    async def step_3_simulate_verification(self, page):
        """Step 3: Simulate email verification success"""
        logger.info("3️⃣ Simulating email verification...")
        
        try:
            # Look for verification-related elements
            verification_elements = [
                'text=Check your email',
                'text=Email verification',
                'text=Verify your account',
                'text=Confirmation sent'
            ]
            
            verification_found = False
            for element in verification_elements:
                if await page.locator(element).is_visible():
                    logger.info(f"✅ Email verification screen found: {element}")
                    verification_found = True
                    break
                    
            if verification_found:
                # Simulate clicking verification link or continue button
                continue_buttons = [
                    'text=Continue',
                    'text=Proceed',
                    'text=Next',
                    'text=Skip verification',
                    'button:has-text("Continue")'
                ]
                
                for button_text in continue_buttons:
                    button = page.locator(button_text).first
                    if await button.is_visible():
                        await button.click()
                        await page.wait_for_timeout(2000)
                        logger.info(f"✅ Clicked {button_text}")
                        break
                        
            # Wait for potential redirect to dashboard
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            logger.error(f"❌ Email verification simulation failed: {e}")
            self.results["errors"].append(f"Email verification: {e}")
            
    async def step_4_verify_session_storage(self, page):
        """Step 4: Verify Supabase session stored correctly"""
        logger.info("4️⃣ Verifying session storage...")
        
        try:
            # Check localStorage for Supabase auth token
            auth_data = await page.evaluate("""
                () => {
                    const keys = Object.keys(localStorage);
                    const authKeys = keys.filter(key => key.includes('supabase') || key.includes('auth'));
                    const authData = {};
                    
                    authKeys.forEach(key => {
                        authData[key] = localStorage.getItem(key);
                    });
                    
                    return {
                        authKeys: authKeys,
                        authData: authData,
                        allKeys: keys
                    };
                }
            """)
            
            logger.info(f"📦 LocalStorage keys: {auth_data['allKeys']}")
            logger.info(f"🔑 Auth keys found: {auth_data['authKeys']}")
            
            # Check for session data
            session_found = False
            for key, value in auth_data['authData'].items():
                if value:
                    try:
                        parsed_value = json.loads(value)
                        if isinstance(parsed_value, dict):
                            if 'access_token' in parsed_value or 'session' in parsed_value:
                                logger.info(f"✅ Session data found in {key}")
                                session_found = True
                                break
                    except json.JSONDecodeError:
                        continue
                        
            self.results["auth_token_persisted"] = session_found
            
            if not session_found:
                logger.warning("⚠️ No session data found in localStorage")
                
        except Exception as e:
            logger.error(f"❌ Session storage verification failed: {e}")
            self.results["errors"].append(f"Session storage: {e}")
            
    async def step_5_test_backend_health(self):
        """Step 5: Test backend health endpoint"""
        logger.info("5️⃣ Testing backend health...")
        
        try:
            # Test health endpoint
            health_url = f"{self.backend_url}/health"
            response = requests.get(health_url, timeout=10)
            
            logger.info(f"🏥 Health check - Status: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Backend health response: {health_data}")
                
                # Validate expected response structure
                expected_fields = ["message", "status", "rag_available"]
                if all(field in health_data for field in expected_fields):
                    logger.info("✅ Backend health response structure valid")
                    self.results["backend_health"] = True
                else:
                    logger.warning(f"⚠️ Missing expected fields. Got: {list(health_data.keys())}")
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Backend health test failed: {e}")
            self.results["errors"].append(f"Backend health: {e}")
            
    async def step_6_test_user_data_persistence(self):
        """Step 6: Test user data persistence"""
        logger.info("6️⃣ Testing user data persistence...")
        
        try:
            # Test data to post
            test_data = {
                "mood": "energized",
                "focus": "high", 
                "hydration": "good"
            }
            
            # POST user preferences
            preferences_url = f"{self.backend_url}/user/preferences"
            post_response = requests.post(preferences_url, json=test_data, timeout=10)
            
            logger.info(f"📝 POST preferences - Status: {post_response.status_code}")
            
            if post_response.status_code == 200:
                logger.info("✅ User preferences posted successfully")
                
                # GET user preferences to verify persistence
                get_response = requests.get(preferences_url, timeout=10)
                logger.info(f"📖 GET preferences - Status: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    retrieved_data = get_response.json()
                    logger.info(f"✅ Retrieved data: {retrieved_data}")
                    
                    # Check if data matches (allowing for additional fields)
                    data_matches = all(
                        retrieved_data.get(key) == value 
                        for key, value in test_data.items()
                    )
                    
                    if data_matches:
                        logger.info("✅ Data persistence verified")
                        self.results["user_data_persistence"] = True
                    else:
                        logger.warning("⚠️ Retrieved data doesn't match posted data")
                else:
                    logger.error(f"❌ GET preferences failed: {get_response.status_code}")
            else:
                logger.error(f"❌ POST preferences failed: {post_response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ User data persistence test failed: {e}")
            self.results["errors"].append(f"User data persistence: {e}")
            
    async def step_7_simulate_multi_day_session(self, page):
        """Step 7: Simulate multi-day session persistence"""
        logger.info("7️⃣ Simulating multi-day session...")
        
        try:
            # Simulate waiting 2 days by manipulating localStorage
            await page.evaluate("""
                () => {
                    // Simulate 2 days later by modifying token expiration
                    const keys = Object.keys(localStorage);
                    const authKeys = keys.filter(key => key.includes('supabase') || key.includes('auth'));
                    
                    authKeys.forEach(key => {
                        const value = localStorage.getItem(key);
                        if (value) {
                            try {
                                const parsed = JSON.parse(value);
                                if (parsed.expires_at) {
                                    // Set expiration to 2 days from now
                                    const twoDaysLater = Date.now() + (2 * 24 * 60 * 60 * 1000);
                                    parsed.expires_at = Math.floor(twoDaysLater / 1000);
                                    localStorage.setItem(key, JSON.stringify(parsed));
                                }
                            } catch (e) {
                                // Ignore non-JSON values
                            }
                        }
                    });
                }
            """)
            
            # Refresh page to test auto-login
            await page.reload()
            await page.wait_for_load_state('networkidle')
            
            # Check if user is still logged in
            login_elements = await page.locator('text=Login').all()
            register_elements = await page.locator('text=Register').all()
            
            if not login_elements and not register_elements:
                logger.info("✅ Auto-login successful - No auth screens visible")
                self.results["token_refresh"] = True
            else:
                logger.warning("⚠️ Auto-login failed - Auth screens still visible")
                
        except Exception as e:
            logger.error(f"❌ Multi-day session simulation failed: {e}")
            self.results["errors"].append(f"Multi-day session: {e}")
            
    async def step_8_test_logout_cleanup(self, page):
        """Step 8: Test logout and cleanup"""
        logger.info("8️⃣ Testing logout cleanup...")
        
        try:
            # Look for logout button
            logout_selectors = [
                'text=Logout',
                'text=Sign Out',
                'text=Log Out',
                'button:has-text("Logout")',
                'button:has-text("Sign Out")',
                '[data-testid="logout"]',
                '[aria-label*="logout" i]'
            ]
            
            logout_clicked = False
            for selector in logout_selectors:
                logout_button = page.locator(selector).first
                if await logout_button.is_visible():
                    await logout_button.click()
                    await page.wait_for_timeout(2000)
                    logger.info(f"✅ Logout clicked: {selector}")
                    logout_clicked = True
                    break
                    
            if not logout_clicked:
                # Try to find logout in menu or profile
                profile_selectors = [
                    'text=Profile',
                    'text=Account',
                    '[data-testid="profile"]',
                    '[aria-label*="profile" i]'
                ]
                
                for selector in profile_selectors:
                    profile_button = page.locator(selector).first
                    if await profile_button.is_visible():
                        await profile_button.click()
                        await page.wait_for_timeout(1000)
                        
                        # Look for logout in dropdown/menu
                        logout_in_menu = page.locator('text=Logout').first
                        if await logout_in_menu.is_visible():
                            await logout_in_menu.click()
                            await page.wait_for_timeout(2000)
                            logout_clicked = True
                            break
                            
            if logout_clicked:
                # Verify localStorage cleanup
                auth_data_after = await page.evaluate("""
                    () => {
                        const keys = Object.keys(localStorage);
                        const authKeys = keys.filter(key => key.includes('supabase') || key.includes('auth'));
                        return {
                            authKeys: authKeys,
                            allKeys: keys
                        };
                    }
                """)
                
                logger.info(f"📦 LocalStorage after logout: {auth_data_after['allKeys']}")
                
                if not auth_data_after['authKeys']:
                    logger.info("✅ Logout cleanup successful - No auth keys in localStorage")
                    self.results["logout_cleanup"] = True
                else:
                    logger.warning(f"⚠️ Auth keys still present after logout: {auth_data_after['authKeys']}")
            else:
                logger.warning("⚠️ Logout button not found")
                
        except Exception as e:
            logger.error(f"❌ Logout cleanup test failed: {e}")
            self.results["errors"].append(f"Logout cleanup: {e}")
            
    def generate_report(self):
        """Generate final test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 HERFOODCODE USER JOURNEY TEST REPORT")
        logger.info("="*60)
        
        total_tests = len([k for k in self.results.keys() if k != "errors"])
        passed_tests = sum(1 for k, v in self.results.items() if k != "errors" and v)
        
        logger.info(f"📈 Overall Score: {passed_tests}/{total_tests} tests passed")
        logger.info(f"📧 Test Email: {self.test_email}")
        logger.info(f"🌐 Frontend: {self.frontend_url}")
        logger.info(f"🔧 Backend: {self.backend_url}")
        
        logger.info("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            if test_name != "errors":
                status = "✅ PASS" if result else "❌ FAIL"
                logger.info(f"  {test_name.replace('_', ' ').title()}: {status}")
                
        if self.results["errors"]:
            logger.info(f"\n❌ Errors ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results["errors"], 1):
                logger.info(f"  {i}. {error}")
                
        # Validation metrics
        logger.info("\n🎯 Validation Metrics:")
        metrics = [
            ("Registration Success", self.results["registration"]),
            ("Auth Token Persisted", self.results["auth_token_persisted"]),
            ("Backend Health Check", self.results["backend_health"]),
            ("User Data Persistence", self.results["user_data_persistence"]),
            ("Token Refresh Logic", self.results["token_refresh"]),
            ("Logout Cleanup", self.results["logout_cleanup"])
        ]
        
        for metric, passed in metrics:
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {metric}")
            
        logger.info("\n" + "="*60)
        
        # Return results for programmatic use
        return self.results

async def main():
    """Main test execution"""
    test_suite = HerFoodCodeTestSuite()
    results = await test_suite.run_full_journey()
    
    # Exit with appropriate code
    total_tests = len([k for k in results.keys() if k != "errors"])
    passed_tests = sum(1 for k, v in results.items() if k != "errors" and v)
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed!")
        exit(0)
    else:
        logger.error(f"❌ {total_tests - passed_tests} tests failed")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
