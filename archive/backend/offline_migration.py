#!/usr/bin/env python3
"""
Offline migration script that updates the code to use new database structure
without requiring a live Supabase connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def update_intervention_matcher_offline():
    """Update the intervention matcher to use new database structure"""
    
    print("🔄 Updating intervention matcher for new database structure...")
    
    # Read current matcher file
    matcher_file = "interventions/matcher.py"
    
    if not os.path.exists(matcher_file):
        print(f"❌ Matcher file not found: {matcher_file}")
        return False
    
    with open(matcher_file, 'r') as f:
        content = f.read()
    
    # Create new matcher content for new database structure
    new_content = '''"""
Intervention matching functionality
Handles intervention recommendation using new InterventionsBASE and HabitsBASE tables
"""

import os
import json
import numpy as np
from typing import Dict, List
from sklearn.metrics.pairwise import cosine_similarity
from llm import get_embeddings
from models.supabase_models import supabase_client

class InterventionMatcher:
    """Singleton class for intervention matching with new database schema"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InterventionMatcher, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.embeddings = get_embeddings()
            self.interventions_data = self._load_interventions_from_db()
            self.profile_embeddings = self._get_or_compute_embeddings()
            self._initialized = True
            print("✅ InterventionMatcher singleton initialized with new schema data")
    
    def _load_interventions_from_db(self):
        """Load interventions and habits from new InterventionsBASE and HabitsBASE tables"""
        try:
            # Get all interventions with their habits
            result = supabase_client.get_all_interventions_with_habits()
            
            if not result:
                print("❌ No interventions found in new schema")
                return []
            
            print(f"✅ Loaded {len(result)} interventions from new schema")
            return result
            
        except Exception as e:
            print(f"❌ Failed to load interventions from new schema: {e}")
            return []
    
    def _get_or_compute_embeddings(self):
        """Get or compute embeddings for intervention profiles"""
        try:
            # Create embeddings for each intervention profile
            embeddings = []
            for intervention_data in self.interventions_data:
                intervention = intervention_data['intervention']
                # Use Clinical Background for matching
                profile_text = f"{intervention['Strategy Name']}: {intervention['Clinical Background']}"
                embedding = self.embeddings.embed_query(profile_text)
                embeddings.append(embedding)
            
            return np.array(embeddings)
            
        except Exception as e:
            print(f"❌ Failed to compute embeddings: {e}")
            return np.array([])
    
    def get_intervention_recommendation(self, user_input: str, min_similarity: float = 0.50) -> Dict:
        """Get single intervention recommendation based on user input"""
        try:
            if not self.interventions_data or len(self.profile_embeddings) == 0:
                return {
                    "error": "No intervention data available",
                    "recommended_intervention": None,
                    "similarity_score": 0.0
                }
            
            # Get user input embedding
            user_embedding = self.embeddings.embed_query(user_input)
            user_embedding = np.array(user_embedding).reshape(1, -1)
            
            # Calculate similarities
            similarities = cosine_similarity(user_embedding, self.profile_embeddings)[0]
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity < min_similarity:
                return {
                    "error": f"No suitable intervention found (best similarity: {best_similarity:.3f})",
                    "recommended_intervention": None,
                    "similarity_score": best_similarity
                }
            
            # Get the best intervention
            best_intervention_data = self.interventions_data[best_idx]
            best_intervention = best_intervention_data['intervention']
            best_habits = best_intervention_data['habits']
            
            # Format habits for response
            habit_descriptions = [habit['Habit Name'] for habit in best_habits]
            
            return {
                "intervention_id": best_intervention['Intervention_ID'],
                "intervention_name": best_intervention['Strategy Name'],
                "intervention_profile": best_intervention['Clinical Background'],
                "scientific_source": best_intervention['Show Sources'],
                "similarity_score": float(best_similarity),
                "habits": habit_descriptions,
                "category_strategy": best_intervention.get('Category Strategy', ''),
                "symptoms_match": best_intervention.get('Symtpoms match', ''),
                "persona_fit": best_intervention.get('Persona fit (prior)', ''),
                "dietary_fit": best_intervention.get('Dietary fit (prior)', ''),
                "movement_amount": best_intervention.get('Amount of movemen...', '')
            }
            
        except Exception as e:
            print(f"❌ Error in intervention recommendation: {e}")
            return {
                "error": f"Failed to get recommendation: {str(e)}",
                "recommended_intervention": None,
                "similarity_score": 0.0
            }
    
    def get_multiple_intervention_recommendations(self, user_input: str, min_similarity: float = 0.50, max_results: int = 3) -> Dict:
        """Get multiple intervention recommendations"""
        try:
            if not self.interventions_data or len(self.profile_embeddings) == 0:
                return {
                    "error": "No intervention data available",
                    "recommendations": []
                }
            
            # Get user input embedding
            user_embedding = self.embeddings.embed_query(user_input)
            user_embedding = np.array(user_embedding).reshape(1, -1)
            
            # Calculate similarities
            similarities = cosine_similarity(user_embedding, self.profile_embeddings)[0]
            
            # Get top matches
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            recommendations = []
            for idx in top_indices:
                similarity = similarities[idx]
                if similarity >= min_similarity:
                    intervention_data = self.interventions_data[idx]
                    intervention = intervention_data['intervention']
                    habits = intervention_data['habits']
                    habit_descriptions = [habit['Habit Name'] for habit in habits]
                    
                    recommendations.append({
                        "intervention_id": intervention['Intervention_ID'],
                        "intervention_name": intervention['Strategy Name'],
                        "intervention_profile": intervention['Clinical Background'],
                        "scientific_source": intervention['Show Sources'],
                        "similarity_score": float(similarity),
                        "habits": habit_descriptions,
                        "category_strategy": intervention.get('Category Strategy', ''),
                        "symptoms_match": intervention.get('Symtpoms match', ''),
                        "persona_fit": intervention.get('Persona fit (prior)', ''),
                        "dietary_fit": intervention.get('Dietary fit (prior)', ''),
                        "movement_amount": intervention.get('Amount of movemen...', '')
                    })
            
            return {
                "recommendations": recommendations,
                "total_found": len(recommendations),
                "min_similarity_used": min_similarity
            }
            
        except Exception as e:
            print(f"❌ Error in multiple intervention recommendations: {e}")
            return {
                "error": f"Failed to get recommendations: {str(e)}",
                "recommendations": []
            }
    
    def get_intervention_by_id(self, intervention_id: int) -> Dict:
        """Get specific intervention by ID"""
        try:
            result = supabase_client.get_intervention_with_habits(intervention_id)
            if not result:
                return {"error": "Intervention not found"}
            
            intervention = result['intervention']
            habits = result['habits']
            habit_descriptions = [habit['Habit Name'] for habit in habits]
            
            return {
                "intervention_id": intervention['Intervention_ID'],
                "intervention_name": intervention['Strategy Name'],
                "intervention_profile": intervention['Clinical Background'],
                "scientific_source": intervention['Show Sources'],
                "habits": habit_descriptions,
                "category_strategy": intervention.get('Category Strategy', ''),
                "symptoms_match": intervention.get('Symtpoms match', ''),
                "persona_fit": intervention.get('Persona fit (prior)', ''),
                "dietary_fit": intervention.get('Dietary fit (prior)', ''),
                "movement_amount": intervention.get('Amount of movemen...', '')
            }
            
        except Exception as e:
            print(f"❌ Error getting intervention by ID: {e}")
            return {"error": f"Failed to get intervention: {str(e)}"}

# Global instance
intervention_matcher = InterventionMatcher()

def get_intervention_recommendation(user_input: str, min_similarity: float = 0.50) -> Dict:
    """Get single intervention recommendation"""
    return intervention_matcher.get_intervention_recommendation(user_input, min_similarity)

def get_multiple_intervention_recommendations(user_input: str, min_similarity: float = 0.50, max_results: int = 3) -> Dict:
    """Get multiple intervention recommendations"""
    return intervention_matcher.get_multiple_intervention_recommendations(user_input, min_similarity, max_results)

def get_intervention_by_id(intervention_id: int) -> Dict:
    """Get specific intervention by ID"""
    return intervention_matcher.get_intervention_by_id(intervention_id)

def _get_user_interventions(user_input: str, min_similarity: float = 0.5, max_results: int = 3) -> list:
    """Get user-generated interventions from vectorstore"""
    try:
        from retrievers.vectorstores import get_user_interventions_vectorstore
        
        # Get user interventions vectorstore
        user_vectorstore = get_user_interventions_vectorstore()
        
        # Search for similar interventions
        results = user_vectorstore.similarity_search_with_score(user_input, k=max_results)
        
        interventions = []
        for doc, score in results:
            if score >= min_similarity:
                # Get full intervention data from database
                intervention_id = doc.metadata.get('intervention_id')
                if intervention_id:
                    try:
                        intervention_result = supabase_client.client.table('user_interventions').select('*').eq('id', intervention_id).execute()
                        if intervention_result.data:
                            intervention = intervention_result.data[0]
                            interventions.append({
                                "intervention_name": intervention['name'],
                                "intervention_profile": intervention['description'],
                                "scientific_source": intervention['scientific_source'],
                                "similarity_score": float(score),
                                "intervention_id": intervention['id'],
                                "type": "user_generated"
                            })
                    except Exception as e:
                        print(f"Warning: Could not fetch intervention {intervention_id}: {e}")
        
        return interventions
        
    except Exception as e:
        print(f"Error getting user interventions: {e}")
        return []
'''
    
    # Write updated content
    with open(matcher_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {matcher_file}")
    return True

def update_supabase_models_offline():
    """Update Supabase models for new schema"""
    
    print("🔄 Updating Supabase models for new schema...")
    
    # Read current models file
    models_file = "models/supabase_models.py"
    
    if not os.path.exists(models_file):
        print(f"❌ Models file not found: {models_file}")
        return False
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Create new models content
    new_content = '''"""
Supabase client wrapper with health app specific methods
Updated for new InterventionsBASE and HabitsBASE schema
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Supabase client wrapper with health app specific methods"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        self.client: Client = create_client(self.url, self.key)
    
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
        """Get all habits for a specific intervention from HabitsBASE"""
        return self.client.table('HabitsBASE').select('*').eq('Connects Interventio...', intervention_id).execute()
    
    def get_habits_by_intervention_name(self, strategy_name: str):
        """Get habits for an intervention by strategy name"""
        # First get the intervention ID
        intervention = self.client.table('InterventionsBASE').select('Intervention_ID').eq('Strategy Name', strategy_name).execute()
        
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
        return self.client.table('user_habits').select('*, habits(*)').eq('user_id', user_id).execute()
    
    def get_successful_habits(self, user_id: str):
        """Get only successful habits for a user"""
        return self.client.table('user_habits').select('*, habits(*)').eq('user_id', user_id).eq('success', True).execute()
    
    # Recommendation operations (unchanged)
    def create_recommendation(self, recommendation_data: Dict[str, Any]):
        """Create intake recommendation"""
        return self.client.table('intake_recommendations').insert(recommendation_data).execute()
    
    def get_user_recommendations(self, user_id: str):
        """Get all recommendations for a user"""
        return self.client.table('intake_recommendations').select('*').eq('user_id', user_id).execute()
    
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
'''
    
    # Write updated content
    with open(models_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated {models_file}")
    return True

def run_offline_migration():
    """Run the offline migration"""
    
    print("🚀 Offline Migration to New Database Schema")
    print("=" * 60)
    print("📋 Updating code to use InterventionsBASE and HabitsBASE tables")
    
    # Step 1: Update Supabase models
    print("\n🔧 Step 1: Updating Supabase models...")
    try:
        success = update_supabase_models_offline()
        if not success:
            print("❌ Supabase models update failed")
            return False
    except Exception as e:
        print(f"❌ Supabase models update error: {e}")
        return False
    
    # Step 2: Update intervention matcher
    print("\n🔄 Step 2: Updating intervention matcher...")
    try:
        success = update_intervention_matcher_offline()
        if not success:
            print("❌ Matcher update failed")
            return False
    except Exception as e:
        print(f"❌ Matcher update error: {e}")
        return False
    
    print("\n🎉 Offline migration completed successfully!")
    print("\n📋 Summary of changes:")
    print("✅ Supabase models updated for new schema")
    print("✅ Intervention matcher updated")
    print("✅ Code now uses InterventionsBASE and HabitsBASE tables")
    
    print("\n📋 Next steps:")
    print("1. Test your API endpoints")
    print("2. Test the mobile app")
    print("3. Verify recommendations are working with new data")
    print("4. Check that habits are properly linked to interventions")
    
    return True

if __name__ == "__main__":
    print("🚀 Offline Migration to New Schema")
    print("=" * 40)
    
    success = run_offline_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Your app is now ready to use the new InterventionsBASE and HabitsBASE tables!")
        
    else:
        print("\n❌ Migration failed!")
        print("Please check the errors above and try again.")


