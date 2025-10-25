"""
Supabase client wrapper with health app specific methods
Updated for new InterventionsBASE and HabitsBASE schema
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class SupabaseClient:
    """Supabase client wrapper with health app specific methods"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        # Use service role key for backend operations to bypass RLS
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
        
        # Log which key is being used
        if os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
            print("✅ Using service role key for Supabase client")
        else:
            print("⚠️ Using anon key for Supabase client (RLS may block operations)")
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]):
        """Create a new user"""
        return self.client.table('users').insert(user_data).execute()
    
    def get_user(self, user_id: str):
        """Get user by ID"""
        return self.client.table('users').select('*').eq('id', user_id).execute()
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]):
        """Update user data"""
        return self.client.table('users').update(user_data).eq('id', user_id).execute()
    
    # Intake operations
    def create_intake(self, intake_data: Dict[str, Any]):
        """Create intake session"""
        return self.client.table('intakes').insert(intake_data).execute()
    
    def get_user_intakes(self, user_id: str):
        """Get all intakes for a user"""
        return self.client.table('intakes').select('*').eq('user_id', user_id).execute()
    
    def get_intake(self, intake_id: str):
        """Get specific intake by ID"""
        return self.client.table('intakes').select('*').eq('id', intake_id).execute()
    
    # NEW: InterventionsBASE operations
    def get_interventions_base(self):
        """Get all interventions from InterventionsBASE table"""
        return self.client.table('InterventionsBASE').select('*').execute()
    
    def get_intervention_base(self, intervention_id: int):
        """Get specific intervention by Intervention_ID"""
        return self.client.table('InterventionsBASE').select('*').eq('Intervention_ID', intervention_id).execute()
    
    def get_interventions_by_symptoms(self, symptoms: List[str]):
        """Get interventions that match specific symptoms"""
        # This would need to be implemented based on your symptom matching logic
        return self.client.table('InterventionsBASE').select('*').execute()
    
    # NEW: HabitsBASE operations
    def get_habits_base(self):
        """Get all habits from HabitsBASE table"""
        return self.client.table('HabitsBASE').select('*').execute()
    
    def get_habits_by_intervention_base(self, intervention_id: int):
        """Get habits for specific intervention from HabitsBASE"""
        return self.client.table('HabitsBASE').select('*').eq('connects_intervention_id', intervention_id).execute()
    
    def get_daily_habit_entries(self, user_id: str, start_date: str, end_date: str):
        """Get daily habit entries for user"""
        return self.client.table('daily_habit_entries')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('entry_date', start_date)\
            .lte('entry_date', end_date)\
            .execute()
    
    def get_user_intervention_periods(self, user_id: str):
        """Get user's intervention periods"""
        return self.client.table('intervention_periods')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
    
    def create_intervention_period(self, period_data: Dict[str, Any]):
        """Create intervention period"""
        return self.client.table('intervention_periods').insert(period_data).execute()
    
    def get_user_habits(self, user_id: str):
        """Get user's habits"""
        return self.client.table('user_habits')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
    
    def get_user_interventions(self, user_id: str):
        """Get user's interventions"""
        return self.client.table('user_interventions')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
    
    
    def get_habits_by_intervention_name(self, strategy_name: str):
        """Get habits for an intervention by strategy name"""
        # First get the intervention ID
        intervention = self.client.table('InterventionsBASE').select('Intervention_ID').eq('strategy_name', strategy_name).execute()
        
        if not intervention.data:
            return []
        
        intervention_id = intervention.data[0]['Intervention_ID']
        return self.get_habits_by_intervention_base(intervention_id)
    
    # Combined operations for recommendations
    def get_intervention_with_habits(self, intervention_id: int):
        """Get intervention with all its habits"""
        intervention = self.get_intervention_base(intervention_id)
        if not intervention.data:
            return None
        
        habits = self.get_habits_by_intervention_base(intervention_id)
        
        return {
            'intervention': intervention.data[0],
            'habits': habits.data
        }
    
    def get_all_interventions_with_habits(self):
        """Get all interventions with their habits"""
        interventions = self.get_interventions_base()
        result = []
        
        for intervention in interventions.data:
            intervention_id = intervention['Intervention_ID']
            habits = self.get_habits_by_intervention_base(intervention_id)
            
            result.append({
                'intervention': intervention,
                'habits': habits.data
            })
        
        return result
    
    # Legacy operations (for backward compatibility)
    def get_interventions(self):
        """Legacy method - redirects to InterventionsBASE"""
        return self.get_interventions_base()
    
    def get_intervention(self, intervention_id: str):
        """Legacy method - redirects to InterventionsBASE"""
        try:
            intervention_id_int = int(intervention_id)
            return self.get_intervention_base(intervention_id_int)
        except ValueError:
            # If it's not an integer, try to find by name
            return self.client.table('InterventionsBASE').select('*').eq('Strategy Name', intervention_id).execute()
    
    def get_habits_by_intervention(self, intervention_id: str):
        """Legacy method - redirects to HabitsBASE"""
        try:
            intervention_id_int = int(intervention_id)
            return self.get_habits_by_intervention_base(intervention_id_int)
        except ValueError:
            # If it's not an integer, try to find by name
            return self.get_habits_by_intervention_name(intervention_id)
    
    def get_all_habits(self):
        """Legacy method - redirects to HabitsBASE"""
        return self.get_habits_base()
    
    # User-Habit operations (unchanged)
    def create_user_habit(self, user_habit_data: Dict[str, Any]):
        """Create user-habit relationship"""
        return self.client.table('user_habits').insert(user_habit_data).execute()
    
    def update_user_habit_success(self, user_habit_id: str, success: bool, notes: Optional[str] = None):
        """Update habit success status"""
        update_data = {'success': success, 'updated_at': datetime.now().isoformat()}
        if notes:
            update_data['additional_notes'] = notes
        return self.client.table('user_habits').update(update_data).eq('id', user_habit_id).execute()
    
    def get_user_habits(self, user_id: str):
        """Get all habits for a user with success status"""
        return self.client.table('user_habits').select('*').eq('user_id', user_id).execute()
    
    def get_successful_habits(self, user_id: str):
        """Get only successful habits for a user"""
        return self.client.table('user_habits').select('*').eq('user_id', user_id).eq('status', 'completed').execute()
    
    # Recommendation operations (unchanged)
    def create_recommendation(self, recommendation_data: Dict[str, Any]):
        """Create intake recommendation"""
        # Store recommendation data in the intakes table instead
        intake_id = recommendation_data.get('intake_id')
        if intake_id:
            return self.client.table('intakes').update({
                'recommendation_data': recommendation_data
            }).eq('id', intake_id).execute()
        else:
            raise ValueError("intake_id is required for recommendation storage")
    
    def get_user_recommendations(self, user_id: str):
        """Get all recommendations for a user"""
        return self.client.table('intakes').select('*').eq('user_id', user_id).execute()
    
    # Custom intervention operations (unchanged)
    def create_custom_intervention(self, intervention_data: Dict[str, Any]):
        """Create custom intervention"""
        return self.client.table('custom_interventions').insert(intervention_data).execute()
    
    def get_pending_custom_interventions(self):
        """Get pending custom interventions"""
        return self.client.table('custom_interventions').select('*').eq('status', 'pending').execute()

# Global instance
supabase_client = SupabaseClient()

# Pydantic models for the new schema
class InterventionsBase(BaseModel):
    Intervention_ID: int
    Strategy_Name: str
    Clinical_Background: str
    What_will_you_be_doing: str
    Show_Sources: str
    Downloadable_Sources: str
    Category_Strategy: str
    Symptoms_match: str
    Persona_fit_prior: str
    Dietary_fit_prior: str
    Amount_of_movement: str

class HabitsBase(BaseModel):
    Habit_ID: int
    Connects_Intervention_ID: int
    Habit_Name: str
    What_will_you_be_doing: str
    Why_does_it_work: str
    What_does_that_look_like: str

# Legacy models (for backward compatibility)
class SupabaseIntervention(BaseModel):
    id: str
    name: str
    profile: str
    scientific_source: str
    created_at: datetime
    updated_at: datetime

class SupabaseHabit(BaseModel):
    id: str
    name: str
    intervention_id: str
    scientific_source: str
    created_at: datetime
    updated_at: datetime

class SupabaseUserHabit(BaseModel):
    id: str
    user_id: str
    habit_id: str
    success: bool
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Additional models for compatibility
class SupabaseUser(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime

class SupabaseIntake(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

class SupabaseRecommendation(BaseModel):
    id: str
    user_id: str
    intervention_id: str
    created_at: datetime
    updated_at: datetime

# Conversion functions for compatibility
def convert_user_input_to_supabase(user_input):
    """Convert user input to Supabase format"""
    return {
        "profile": user_input.profile.dict() if hasattr(user_input, 'profile') else {},
        "symptoms": user_input.symptoms.dict() if hasattr(user_input, 'symptoms') else {},
        "interventions": user_input.interventions.dict() if hasattr(user_input, 'interventions') else {},
        "habits": user_input.habits.dict() if hasattr(user_input, 'habits') else {},
        "dietary_preferences": user_input.dietaryPreferences.dict() if hasattr(user_input, 'dietaryPreferences') else {},
        "consent": getattr(user_input, 'consent', False),
    }

def convert_habits_to_supabase(habits):
    """Convert habits to Supabase format"""
    return [habit.dict() if hasattr(habit, 'dict') else habit for habit in habits]
