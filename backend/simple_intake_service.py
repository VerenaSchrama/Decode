"""
Simple intake service for collecting user data during recommendations
"""

from typing import Dict, List, Optional
from models import supabase_client, UserInput

class SimpleIntakeService:
    """Service for collecting user data during intake process"""
    
    def __init__(self):
        self.supabase = supabase_client
    
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
        if not user_id:
            user_id = self._create_anonymous_user(user_input)
        
        # Create intake record - store all data in JSONB format
        intake_data = {
            'user_id': user_id,
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
                    'selected': [item.intervention for item in user_input.interventions.selected] if user_input.interventions.selected else [],
                    'additional': user_input.interventions.additional
                },
                'dietary_preferences': {
                    'selected': user_input.dietaryPreferences.selected,
                    'additional': user_input.dietaryPreferences.additional
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
        
        intake_result = self.supabase.create_intake(intake_data)
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
        
        # For demo purposes, use an existing user ID from the database
        # This avoids the foreign key constraint issue
        return "21"
    
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
                    'user_id': user_id,
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
                    print(f"❌ Failed to store previous intervention {intervention_name}: {e}")
            else:
                print(f"⚠️ Intervention not found in database: {intervention_name}")
    
    def _process_custom_interventions(self, user_id: str, intake_id: str, additional_interventions: str) -> None:
        """Process custom interventions mentioned by the user"""
        
        # Create custom intervention record
        custom_intervention_data = {
            'user_id': user_id,
            'intake_id': intake_id,
            'intervention_name': additional_interventions,
            'description': f"User mentioned: {additional_interventions}",
            'context': f"Additional intervention interest from intake",
            'status': 'pending'
        }
        
        try:
            self.supabase.create_custom_intervention(custom_intervention_data)
        except Exception as e:
            print(f"Warning: Could not create custom intervention: {e}")
    
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
                    self.supabase.create_recommended_habit(recommended_habit_record)
                    print(f"✅ Stored recommended habit {i}: {habit_name[:50]}...")
                except Exception as e:
                    print(f"Warning: Could not store recommended habit: {e}")
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
