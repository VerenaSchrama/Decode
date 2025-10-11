"""
InFlo Phase-Aware Habits Algorithm
Combines intervention goals with cycle phase for personalized habit recommendations
"""

from typing import Dict, List, Optional
from data.inflo_phase_data import (
    get_phase_data, 
    get_phase_habits, 
    get_phase_info, 
    get_phase_foods, 
    get_phase_cooking_methods
)

def get_phase_aware_habits(intervention_name: str, cycle_phase: str, base_habits: List[str]) -> Dict:
    """
    Generate phase-aware habits using InFlo book data
    
    Args:
        intervention_name: Name of the recommended intervention
        cycle_phase: Current cycle phase (follicular, ovulatory, luteal, menstrual)
        base_habits: Original habits from intervention matching
        
    Returns:
        Dictionary with phase-aware habits and context
    """
    if cycle_phase not in ["follicular", "ovulatory", "luteal", "menstrual"]:
        return {
            "habits": base_habits,
            "phase_info": None,
            "phase_context": "Cycle phase information not available",
            "cooking_methods": [],
            "recommended_foods": {},
            "inflo_enhanced": False
        }
    
    # Map intervention names to InFlo habit categories
    intervention_mapping = {
        "Control your blood sugar": "blood_sugar",
        "Mediterranean Diet": "mediterranean", 
        "Boost your fiber intake": "fiber",
        "Less or no dairy": "dairy_free",
        "Cut out or decrease stimulants": "stimulant_reduction",
        "Time-restricted eating": "time_restricted",
        "High-protein diet": "high_protein",
        "Eat with your cycle": "cycle_syncing"
    }
    
    # Get the appropriate habit category
    habit_category = intervention_mapping.get(intervention_name, "blood_sugar")
    
    # Get phase-specific habits
    phase_habits = get_phase_habits(cycle_phase, habit_category)
    
    # If no phase-specific habits found, fall back to base habits
    if not phase_habits:
        phase_habits = base_habits
    
    # Get additional phase information
    phase_info = get_phase_info(cycle_phase)
    phase_foods = get_phase_foods(cycle_phase)
    cooking_methods = get_phase_cooking_methods(cycle_phase)
    
    # Create phase context
    phase_context = f"These habits are optimized for your {phase_info.get('name', cycle_phase)} - {phase_info.get('description', '')}"
    
    return {
        "habits": phase_habits,
        "phase_info": phase_info,
        "phase_context": phase_context,
        "cooking_methods": cooking_methods,
        "recommended_foods": phase_foods,
        "inflo_enhanced": True
    }

def enhance_recommendation_with_inflo(recommendation: Dict, cycle_phase: str) -> Dict:
    """
    Enhance existing recommendation with InFlo phase-aware data
    
    Args:
        recommendation: Existing recommendation dictionary
        cycle_phase: Current cycle phase
        
    Returns:
        Enhanced recommendation with phase-aware data
    """
    intervention_name = recommendation.get("recommended_intervention", "")
    base_habits = recommendation.get("habits", [])
    
    # Get phase-aware habits
    inflo_data = get_phase_aware_habits(intervention_name, cycle_phase, base_habits)
    
    # Update recommendation with phase-aware data
    enhanced_recommendation = recommendation.copy()
    enhanced_recommendation.update({
        "habits": inflo_data["habits"],
        "cycle_phase": cycle_phase,
        "phase_info": inflo_data["phase_info"],
        "phase_context": inflo_data["phase_context"],
        "cooking_methods": inflo_data["cooking_methods"],
        "recommended_foods": inflo_data["recommended_foods"],
        "inflo_enhanced": inflo_data["inflo_enhanced"]
    })
    
    return enhanced_recommendation

def get_phase_specific_habits_for_intervention(intervention_name: str, cycle_phase: str) -> List[str]:
    """
    Get phase-specific habits for a specific intervention and cycle phase
    
    Args:
        intervention_name: Name of the intervention
        cycle_phase: Current cycle phase
        
    Returns:
        List of phase-specific habits
    """
    inflo_data = get_phase_aware_habits(intervention_name, cycle_phase, [])
    return inflo_data["habits"]

def get_phase_context(cycle_phase: str) -> Dict:
    """
    Get comprehensive phase context information
    
    Args:
        cycle_phase: Current cycle phase
        
    Returns:
        Dictionary with phase context information
    """
    phase_info = get_phase_info(cycle_phase)
    phase_foods = get_phase_foods(cycle_phase)
    cooking_methods = get_phase_cooking_methods(cycle_phase)
    
    return {
        "phase_info": phase_info,
        "recommended_foods": phase_foods,
        "cooking_methods": cooking_methods,
    }
