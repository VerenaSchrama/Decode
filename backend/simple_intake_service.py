"""
Simple intake service for collecting user data during recommendations
"""

from typing import Dict, List, Optional
import time
import os
from supabase import create_client, Client
from models import supabase_client, UserInput

class SimpleIntakeService:
    """Service for collecting user data during intake process"""
    
    def __init__(self):
        self.supabase = supabase_client
        
        # Create service role client for bypassing RLS
        self.service_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if self.service_url and self.service_key:
            self.service_client: Client = create_client(self.service_url, self.service_key)
            print(f"✅ Service role client created successfully")
        else:
            print("⚠️ Service role key not found, using regular client")
            print(f"   Service URL: {self.service_url}")
            print(f"   Service Key: {'Set' if self.service_key else 'Not set'}")
            self.service_client = self.supabase.client
    
    def process_intake_with_data_collection(
        self, 
        user_input: UserInput, 
        user_id: Optional[str] = None,
        recommendation_data: Optional[Dict] = None
    ) -> Dict:
        """
        Process user intake and collect data about what they've tried
        
        Args:
            user_input: Structured user input with habits they've tried
            user_id: Optional user ID (if None, creates anonymous user)
            
        Returns:
            Dictionary with recommendation and data collection status
        """
        
        # Create user if not provided
        print(f"🔍 DEBUG: user_id = {user_id} (type: {type(user_id)})")
        if not user_id:
            print(f"⚠️ No user_id provided, creating anonymous user")
            user_id = self._create_anonymous_user(user_input)
            print(f"🔍 DEBUG: After _create_anonymous_user, user_id = {user_id}")
        else:
            print(f"✅ Using provided user_id: {user_id}")
        
        # Create intake record - store all data in JSONB format
        intake_data = {
            'user_id': user_id,  # Use user_id to match database schema
            'intake_data': {
                'profile': {
                    'name': user_input.profile.name,
                    'age': user_input.profile.age,
                    'date_of_birth': user_input.profile.dateOfBirth
                },
                'symptoms': {
                    'selected': user_input.symptoms.selected,
                    'additional': user_input.symptoms.additional
                },
                'interventions': {
                    'selected': [
                        {
                            'intervention': item.intervention,
                            'helpful': item.helpful
                        } for item in user_input.interventions.selected
                    ] if user_input.interventions and user_input.interventions.selected else [],
                    'additional': user_input.interventions.additional if user_input.interventions else None
                },
                'habits': {
                    'selected': [],
                    'additional': None
                },
                'dietary_preferences': {
                    'selected': user_input.dietaryPreferences.selected if user_input.dietaryPreferences else [],
                    'additional': user_input.dietaryPreferences.additional if user_input.dietaryPreferences else None
                },
                'last_period': {
                    'date': user_input.lastPeriod.date if user_input.lastPeriod else None,
                    'has_period': user_input.lastPeriod.hasPeriod if user_input.lastPeriod else True,
                    'cycle_length': user_input.lastPeriod.cycleLength if user_input.lastPeriod else None
                },
                'consent': user_input.consent,
                'anonymous': user_input.anonymous
            }
        }
        
        # Use service client to bypass RLS
        print(f"🔍 DEBUG: Using service client for intake insert")
        print(f"🔍 DEBUG: Service client type: {type(self.service_client)}")
        print(f"🔍 DEBUG: Complete intake_data structure:")
        print(f"   - Profile: {intake_data['intake_data']['profile']}")
        print(f"   - Symptoms: {intake_data['intake_data']['symptoms']}")
        print(f"   - Interventions: {intake_data['intake_data']['interventions']}")
        print(f"   - Habits: {intake_data['intake_data']['habits']}")
        print(f"   - Dietary Preferences: {intake_data['intake_data']['dietary_preferences']}")
        print(f"   - Last Period: {intake_data['intake_data']['last_period']}")
        print(f"   - Consent: {intake_data['intake_data']['consent']}")
        print(f"   - Anonymous: {intake_data['intake_data']['anonymous']}")
        
        intake_result = self.service_client.table('intakes').insert(intake_data).execute()
        print(f"🔍 DEBUG: Intake insert result: {intake_result}")
        intake_id = intake_result.data[0]['id']
        
        # Process interventions they've already tried
        if user_input.interventions.selected:
            self._process_previous_interventions(user_id, intake_id, user_input.interventions.selected)
        
        # Process custom interventions they mentioned
        if user_input.interventions.additional:
            self._process_custom_interventions(user_id, intake_id, user_input.interventions.additional)
        
        # Store recommendation data if provided
        if recommendation_data:
            self._store_recommendation(intake_id, recommendation_data)
        
        return {
            "user_id": user_id,
            "intake_id": intake_id,
            "data_collected": True,
            "message": "User data collected successfully"
        }
    
    def _create_anonymous_user(self, user_input: UserInput) -> str:
        """Create an anonymous user for data collection"""
        
        # For authenticated users, we should use their actual user ID
        # For anonymous users, we'll create a temporary user record
        try:
            # Check if demo user exists in profiles table
            demo_user_id = '6ec2305f-0c72-4fea-9f61-f67e5b12e012'  # Real user UUID from profiles table
            
            # Verify the demo user exists in profiles table
            result = self.service_client.table('profiles').select('user_id').eq('user_id', demo_user_id).execute()
            
            if result.data and len(result.data) > 0:
                print(f"✅ Using existing demo user for anonymous intake: {demo_user_id}")
                return demo_user_id
            else:
                print(f"⚠️ Demo user not found in profiles table, creating temporary profile")
                # Create a temporary profile for anonymous user
                profile_data = {
                    'user_id': demo_user_id,
                    'date_of_birth': user_input.profile.dateOfBirth,
                    'dietary_preferences': user_input.dietaryPreferences.selected if user_input.dietaryPreferences else [],
                    'cycle_length': user_input.lastPeriod.cycleLength if user_input.lastPeriod else None,
                    'consent': True,
                    'anonymous': True
                }
                
                profile_result = self.service_client.table('profiles').insert(profile_data).execute()
                if profile_result.data:
                    print(f"✅ Created temporary profile for anonymous user: {demo_user_id}")
                    return demo_user_id
                else:
                    raise Exception("Failed to create temporary profile")
                    
        except Exception as e:
            print(f"❌ Error creating anonymous user: {e}")
            # Fallback to demo user ID even if profile creation fails
            return demo_user_id
    
    def _process_previous_interventions(self, user_id: str, intake_id: str, interventions: List) -> None:
        """Process interventions the user has already tried"""
        
        # Get all available interventions from database
        all_interventions = self.supabase.get_interventions()
        intervention_name_to_id = {intervention['name']: intervention['id'] for intervention in all_interventions.data}
        
        # Create user-intervention relationships for interventions they've tried
        for intervention_item in interventions:
            # Handle both dict and InterventionItem object formats
            if hasattr(intervention_item, 'intervention'):
                intervention_name = intervention_item.intervention
                helpful = intervention_item.helpful
            else:
                intervention_name = intervention_item['intervention']
                helpful = intervention_item['helpful']
            
            # Find the intervention ID
            intervention_id = intervention_name_to_id.get(intervention_name)
            
            if intervention_id:
                # Store as custom intervention with helpfulness tracking
                custom_intervention_data = {
                    'user_id': user_id,  # Use user_id to match database schema
                    'intake_id': intake_id,  # Link to the intake
                    'intervention_name': intervention_name,
                    'description': f"Previously tried intervention: {intervention_name}",
                    'context': f"User reported this intervention was {'helpful' if helpful else 'not helpful'}",
                    'status': 'reviewed'  # Mark as reviewed since it's from our predefined list
                }
                
                try:
                    self.supabase.create_custom_intervention(custom_intervention_data)
                    print(f"✅ Stored previous intervention: {intervention_name} (helpful: {helpful})")
                except Exception as e:
                    print(f"⚠️ Could not store previous intervention {intervention_name}: {e}")
                    # Continue execution even if custom intervention storage fails
            else:
                print(f"⚠️ Intervention not found in database: {intervention_name}")
    
    def _process_custom_interventions(self, user_id: str, intake_id: str, additional_interventions: str) -> None:
        """Process custom interventions mentioned by the user"""
        
        # Create custom intervention record
        custom_intervention_data = {
            'user_id': user_id,  # Use user_id to match database schema
            'intake_id': intake_id,
            'intervention_name': additional_interventions,
            'description': f"User mentioned: {additional_interventions}",
            'context': f"Additional intervention interest from intake",
            'status': 'pending'
        }
        
        try:
            self.supabase.create_custom_intervention(custom_intervention_data)
        except Exception as e:
            print(f"⚠️ Could not create custom intervention: {e}")
            # Continue execution even if custom intervention storage fails
    
    def _store_recommendation(self, intake_id: str, recommendation_data: Dict) -> None:
        """Store the recommendation data for this intake"""
        
        # Extract recommendation details
        intervention_name = recommendation_data.get('recommended_intervention')
        similarity_score = recommendation_data.get('similarity_score', 0.0)
        reasoning = recommendation_data.get('reasoning', '')
        
        # Find the intervention ID by name
        intervention_id = None
        if intervention_name:
            interventions = self.supabase.get_interventions()
            for intervention in interventions.data:
                if intervention['name'] == intervention_name:
                    intervention_id = intervention['id']
                    break
        
        if intervention_id:
            recommendation_record = {
                'intake_id': intake_id,
                'intervention_id': intervention_id,
                'similarity_score': similarity_score,
                'reasoning': reasoning
            }
            
            try:
                self.supabase.create_recommendation(recommendation_record)
                print(f"✅ Stored recommendation for intake {intake_id}")
            except Exception as e:
                print(f"Warning: Could not store recommendation: {e}")
        else:
            print(f"Warning: Could not find intervention ID for: {intervention_name}")
        
        # Store recommended habits
        self._store_recommended_habits(intake_id, recommendation_data.get('habits', []))
    
    def _store_recommended_habits(self, intake_id: str, recommended_habits: List[str]) -> None:
        """Store the recommended habits for this intake"""
        
        # Get all available habits to find their IDs
        all_habits = self.supabase.get_all_habits()
        habit_name_to_id = {habit['name']: habit['id'] for habit in all_habits.data}
        
        for i, habit_name in enumerate(recommended_habits, 1):
            habit_id = habit_name_to_id.get(habit_name)
            
            if habit_id:
                recommended_habit_record = {
                    'intake_id': intake_id,
                    'habit_id': habit_id,
                    'habit_name': habit_name,
                    'habit_order': i
                }
                
                try:
                    # TODO: Implement create_recommended_habit method
                    # self.supabase.create_recommended_habit(recommended_habit_record)
                    print(f"✅ Would store recommended habit {i}: {habit_name[:50]}...")
                except Exception as e:
                    print(f"⚠️ Could not store recommended habit: {e}")
            else:
                print(f"Warning: Could not find habit ID for: {habit_name[:50]}...")
    
    def get_user_previous_habits(self, user_id: str) -> List[Dict]:
        """Get habits the user has previously tried"""
        
        user_habits = self.supabase.get_user_habits(user_id)
        
        return [
            {
                "habit_name": uh['habits']['name'],
                "success": uh['success'],
                "notes": uh['additional_notes'],
                "tried_at": uh['created_at']
            }
            for uh in user_habits.data
        ]
    
    def get_user_insights(self, user_id: str) -> Dict:
        """Get insights about what has worked for the user"""
        
        user_habits = self.supabase.get_user_habits(user_id)
        
        if not user_habits.data:
            return {
                "total_habits_tried": 0,
                "successful_habits": 0,
                "success_rate": 0.0,
                "insights": []
            }
        
        total_habits = len(user_habits.data)
        successful_habits = sum(1 for uh in user_habits.data if uh.get('status') == 'completed')
        success_rate = successful_habits / total_habits if total_habits > 0 else 0
        
        # Generate insights
        insights = []
        if success_rate > 0.8:
            insights.append("You've had great success with most habits you've tried!")
        elif success_rate > 0.5:
            insights.append("You're making good progress with your habits.")
        else:
            insights.append("Consider trying simpler habits or breaking them into smaller steps.")
        
        return {
            "total_habits_tried": total_habits,
            "successful_habits": successful_habits,
            "success_rate": success_rate,
            "insights": insights
        }

# Global service instance
simple_intake_service = SimpleIntakeService()
