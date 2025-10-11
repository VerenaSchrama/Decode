#!/usr/bin/env python3
"""
Update intervention matcher to use database instead of CSV
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.supabase_models import supabase_client

load_dotenv()

def update_intervention_matcher():
    """Update the intervention matcher to use database data"""
    
    print("🔄 Updating intervention matcher...")
    
    # Read current matcher file
    matcher_file = "interventions/matcher.py"
    
    if not os.path.exists(matcher_file):
        print(f"❌ Matcher file not found: {matcher_file}")
        return False
    
    with open(matcher_file, 'r') as f:
        content = f.read()
    
    # Create new matcher content that uses database
    new_content = '''"""
Intervention matching functionality
Handles intervention recommendation using database data and vectorstore
"""

import os
import json
import numpy as np
from typing import Dict, List
from sklearn.metrics.pairwise import cosine_similarity
from llm import get_embeddings
from models.supabase_models import supabase_client

class InterventionMatcher:
    """Singleton class for intervention matching with database data"""
    
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
            print("✅ InterventionMatcher singleton initialized with database data")
    
    def _load_interventions_from_db(self):
        """Load interventions and habits from database"""
        try:
            # Get interventions with their habits
            result = supabase_client.client.table('interventions').select('*, habits(*)').execute()
            
            if not result.data:
                print("❌ No interventions found in database")
                return []
            
            print(f"✅ Loaded {len(result.data)} interventions from database")
            return result.data
            
        except Exception as e:
            print(f"❌ Failed to load interventions from database: {e}")
            return []
    
    def _get_or_compute_embeddings(self):
        """Get or compute embeddings for intervention profiles"""
        try:
            # Create embeddings for each intervention profile
            embeddings = []
            for intervention in self.interventions_data:
                profile_text = f"{intervention['name']}: {intervention['profile']}"
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
            best_intervention = self.interventions_data[best_idx]
            
            # Get habits for this intervention
            habits = best_intervention.get('habits', [])
            habit_descriptions = [habit['name'] for habit in habits]
            
            return {
                "recommended_intervention": best_intervention['name'],
                "intervention_profile": best_intervention['profile'],
                "scientific_source": best_intervention['scientific_source'],
                "similarity_score": float(best_similarity),
                "habits": habit_descriptions,
                "intervention_id": best_intervention['id']
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
                    intervention = self.interventions_data[idx]
                    habits = intervention.get('habits', [])
                    habit_descriptions = [habit['name'] for habit in habits]
                    
                    recommendations.append({
                        "intervention_name": intervention['name'],
                        "intervention_profile": intervention['profile'],
                        "scientific_source": intervention['scientific_source'],
                        "similarity_score": float(similarity),
                        "habits": habit_descriptions,
                        "intervention_id": intervention['id']
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

# Global instance
intervention_matcher = InterventionMatcher()

def get_intervention_recommendation(user_input: str, min_similarity: float = 0.50) -> Dict:
    """Get single intervention recommendation"""
    return intervention_matcher.get_intervention_recommendation(user_input, min_similarity)

def get_multiple_intervention_recommendations(user_input: str, min_similarity: float = 0.50, max_results: int = 3) -> Dict:
    """Get multiple intervention recommendations"""
    return intervention_matcher.get_multiple_intervention_recommendations(user_input, min_similarity, max_results)

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
    print("🚀 Updating Intervention Matcher")
    print("=" * 40)
    
    success = update_intervention_matcher()
    
    if success:
        print("✅ Intervention matcher updated successfully!")
    else:
        print("❌ Failed to update intervention matcher!")

