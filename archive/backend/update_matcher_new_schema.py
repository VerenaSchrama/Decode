#!/usr/bin/env python3
"""
Update intervention matcher to work with new InterventionsBASE and HabitsBASE schema
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def update_intervention_matcher():
    """Update the intervention matcher to use new database schema"""
    
    print("🔄 Updating intervention matcher for new schema...")
    
    # Read current matcher file
    matcher_file = "interventions/matcher.py"
    
    if not os.path.exists(matcher_file):
        print(f"❌ Matcher file not found: {matcher_file}")
        return False
    
    with open(matcher_file, 'r') as f:
        content = f.read()
    
    # Create new matcher content for new schema
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

if __name__ == "__main__":
    print("🚀 Updating Intervention Matcher for New Schema")
    print("=" * 50)
    
    success = update_intervention_matcher()
    
    if success:
        print("✅ Intervention matcher updated successfully!")
        print("📋 Next steps:")
        print("1. Update API endpoints")
        print("2. Test the complete system")
    else:
        print("❌ Failed to update intervention matcher!")


