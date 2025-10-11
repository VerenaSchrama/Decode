"""
Main RAG Pipeline Entry Point
Clean, modular interface for intervention recommendations
"""

from typing import Dict
from interventions.matcher import get_intervention_recommendation, get_multiple_intervention_recommendations
from interventions.inflo_context import get_intervention_with_inflo_context
from utils.helpers import clean_text
from utils.cycle_calculator import calculate_cycle_phase, format_cycle_info
from models import UserInput
from llm_explanations import generate_batch_explanations

def process_user_input(user_input: str) -> Dict:
    """
    Main function to process user input and return intervention recommendation
    
    Args:
        user_input: Raw text input from user describing their symptoms, goals, concerns
        
    Returns:
        Dictionary with intake summary, recommended intervention, and habits
    """
    if not user_input or not clean_text(user_input):
        return {
            "error": "Please provide some information about your symptoms, goals, or concerns"
        }
    
    # Get intervention recommendation with InFlo context
    try:
        result = get_intervention_with_inflo_context(user_input)
        
        # Format the response
        formatted_result = {
            "intake_summary": build_intake_summary(user_input),
            "recommended_intervention": result['intervention_name'],
            "intervention_id": result['intervention_id'],
            "scientific_reference": result['scientific_source'],
            "habits": [
                result['habits']['habit_1'],
                result['habits']['habit_2'],
                result['habits']['habit_3'],
                result['habits']['habit_4'],
                result['habits']['habit_5']
            ],
            "reasoning": f"Recommended based on {result['similarity_score']:.2f} similarity to intervention profile: {result['profile'][:100]}...",
            "similarity_score": result['similarity_score']
        }
        
        # Add InFlo context if available
        if 'additional_inflo_context' in result and result['additional_inflo_context'] != "InFlo book context not available":
            formatted_result["additional_inflo_context"] = result['additional_inflo_context']
        
        return formatted_result

    except Exception as e:
        return {
            "error": f"Error processing your request: {str(e)}",
            "intake_summary": build_intake_summary(user_input),
            "recommended_intervention": None,
            "intervention_id": None,
            "scientific_reference": None,
            "habits": [],
            "reasoning": "Error occurred during processing"
        }

def process_structured_user_input(user_input: UserInput) -> Dict:
    """
    Process structured user input and return intervention recommendation
    
    Args:
        user_input: Structured UserInput object with profile, symptoms, interventions, etc.
        
    Returns:
        Dictionary with intake summary, recommended intervention, and habits
    """
    print(f"🔍 DEBUG: process_structured_user_input called with user_input: {user_input}")
    print(f"🔍 DEBUG: user_input.profile: {user_input.profile}")
    print(f"🔍 DEBUG: user_input.profile.name: {user_input.profile.name}")
    
    # Build comprehensive text input from structured data
    text_input = build_text_from_structured_input(user_input)
    
    if not text_input or not clean_text(text_input):
        return {
            "error": "Please provide some information about your symptoms, goals, or concerns"
        }
    
    # Get multiple intervention recommendations
    try:
        print(f"🔍 DEBUG: Getting multiple interventions for text: {text_input[:100]}...")
        # Get multiple interventions with similarity >= 0.50
        multiple_result = get_multiple_intervention_recommendations(text_input, min_similarity=0.50, max_results=3)
        print(f"🔍 DEBUG: Multiple result: {multiple_result}")
        
        if not multiple_result['recommendations']:
            return {
                "error": "No interventions found with sufficient similarity to your profile. Please try providing more detailed information about your symptoms and goals.",
                "intake_summary": build_intake_summary(user_input)
            }
        
        # Generate personalized explanations for each intervention
        print("🔍 DEBUG: Generating explanations for interventions...")
        explanations = generate_batch_explanations(user_input, multiple_result['recommendations'])
        print(f"🔍 DEBUG: Generated {len(explanations)} explanations")
        
        # Add explanations to each intervention
        for i, intervention in enumerate(multiple_result['recommendations']):
            if i < len(explanations):
                intervention['why_recommended'] = explanations[i]
            else:
                intervention['why_recommended'] = f"This intervention matches your profile with {intervention.get('similarity_score', 0):.0%} compatibility."
        
        # Format the response with multiple interventions
        formatted_result = {
            "intake_summary": build_intake_summary(user_input),
            "interventions": multiple_result['recommendations'],
            "total_found": multiple_result['total_found'],
            "min_similarity_used": multiple_result['min_similarity_used']
        }
        
        # Calculate cycle phase for each intervention
        cycle_phase = None
        print(f"Debug: lastPeriod data: {user_input.lastPeriod}")
        if (user_input.lastPeriod and 
            user_input.lastPeriod.hasPeriod and 
            user_input.lastPeriod.date and 
            user_input.lastPeriod.cycleLength):
            try:
                print(f"Debug: Calculating cycle phase for date {user_input.lastPeriod.date}, length {user_input.lastPeriod.cycleLength}")
                phase, days_since = calculate_cycle_phase(
                    user_input.lastPeriod.date, 
                    user_input.lastPeriod.cycleLength
                )
                print(f"Debug: Calculated phase: {phase}, days_since: {days_since}")
                # Convert phase name to lowercase and remove 'phase' suffix
                cycle_phase = phase.lower().replace(' ', '-').replace('phase', '').strip()
                if cycle_phase.endswith('-'):
                    cycle_phase = cycle_phase[:-1]
                # Map to InFlo phase names
                phase_mapping = {
                    'follicular-': 'follicular',
                    'ovulation-': 'ovulatory', 
                    'luteal-': 'luteal',
                    'menstrual-': 'menstrual',
                    'pre-menstrual-': 'luteal'
                }
                cycle_phase = phase_mapping.get(cycle_phase, cycle_phase)
                print(f"Debug: Final cycle_phase: {cycle_phase}")
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not calculate cycle phase: {e}")
        else:
            print("Debug: No cycle data available for phase calculation")
        
        # Add cycle phase information to the result
        if cycle_phase:
            formatted_result["cycle_phase"] = cycle_phase
            # Get phase info for display
            try:
                from data.inflo_phase_data import get_phase_data
                phase_data = get_phase_data(cycle_phase)
                print(f"Debug: Phase data for {cycle_phase}: {phase_data}")
                if phase_data and "phase_info" in phase_data:
                    formatted_result["phase_info"] = {
                        "name": phase_data["phase_info"]["name"],
                        "description": phase_data["phase_info"]["description"],
                        "duration": phase_data["phase_info"]["duration"],
                        "energy_level": phase_data["phase_info"]["energy_level"],
                        "hormonal_focus": phase_data["phase_info"]["hormonal_focus"]
                    }
                    print(f"Debug: Added phase_info to result")
                else:
                    print(f"Debug: No phase_info found for {cycle_phase}")
            except Exception as e:
                print(f"Debug: Error getting phase data: {e}")
                # Don't fail the whole request for phase data issues
        
        print(f"Debug: Final result keys: {list(formatted_result.keys())}")
        return formatted_result
        
    except Exception as e:
        return {
            "error": f"Error processing your request: {str(e)}",
            "intake_summary": build_intake_summary(user_input),
            "interventions": [],
            "total_found": 0
        }

def build_text_from_structured_input(user_input: UserInput) -> str:
    """
    Build comprehensive text input from structured user data for RAG processing
    
    Args:
        user_input: Structured UserInput object
        
    Returns:
        Formatted text string for RAG processing
    """
    parts = []
    
    # Profile information
    if user_input.profile.name:
        parts.append(f"Name: {user_input.profile.name}")
    parts.append(f"Age: {user_input.profile.age}")
    
    # Symptoms
    if user_input.symptoms.selected:
        parts.append(f"Symptoms: {', '.join(user_input.symptoms.selected)}")
    if user_input.symptoms.additional:
        parts.append(f"Additional symptoms: {user_input.symptoms.additional}")
    
    # Interventions
    if user_input.interventions.selected:
        intervention_texts = []
        helpful_interventions = []
        for intervention_item in user_input.interventions.selected:
            intervention_texts.append(intervention_item.intervention)
            if intervention_item.helpful:
                helpful_interventions.append(intervention_item.intervention)
        
        parts.append(f"Tried interventions: {', '.join(intervention_texts)}")
        if helpful_interventions:
            parts.append(f"Helpful interventions: {', '.join(helpful_interventions)}")
    
    if user_input.interventions.additional:
        parts.append(f"Additional intervention interests: {user_input.interventions.additional}")
    
    # Dietary preferences
    if user_input.dietaryPreferences.selected:
        parts.append(f"Dietary preferences: {', '.join(user_input.dietaryPreferences.selected)}")
    if user_input.dietaryPreferences.additional:
        parts.append(f"Additional dietary preferences: {user_input.dietaryPreferences.additional}")
    
    return " | ".join(parts)

def build_intake_summary(user_input: UserInput) -> str:
    """
    Build a warm, welcoming profile summary like a nutritional coach would write
    
    Args:
        user_input: Structured UserInput object
        
    Returns:
        Warm, personalized profile summary string with HTML bold tags for intake variables
    """
    name = user_input.profile.name if user_input.profile.name else "there"
    
    # Start with a warm greeting
    summary_parts = [f"Hi {name}! I'm so glad you've taken this step towards better health."]
    
    # Acknowledge their challenges with empathy
    if user_input.symptoms.selected:
        symptom_list = ', '.join([f"<b>{symptom}</b>" for symptom in user_input.symptoms.selected])
        summary_parts.append(f"I can see you're navigating {symptom_list} - I know these can feel overwhelming, but you're not alone in this journey.")
    
    # Acknowledge their efforts if they've tried interventions
    if user_input.interventions.selected:
        intervention_names = [f"<b>{item.intervention}</b>" for item in user_input.interventions.selected]
        summary_parts.append(f"I appreciate that you've already explored {', '.join(intervention_names)} - every step you've taken matters.")
    
    # Acknowledge their dietary preferences with encouragement
    if user_input.dietaryPreferences.selected:
        dietary_prefs = ', '.join([f"<b>{pref}</b>" for pref in user_input.dietaryPreferences.selected])
        summary_parts.append(f"Your {dietary_prefs} approach shows real commitment to nourishing your body well.")
    
    # Add cycle awareness if applicable
    if user_input.lastPeriod:
        if not user_input.lastPeriod.hasPeriod:
            summary_parts.append("I understand that menstrual cycles aren't part of your experience, and that's completely valid - we'll focus on optimizing your overall hormonal health.")
        elif (user_input.lastPeriod.hasPeriod and 
              user_input.lastPeriod.date and 
              user_input.lastPeriod.cycleLength):
            try:
                phase, days_since = calculate_cycle_phase(
                    user_input.lastPeriod.date, 
                    user_input.lastPeriod.cycleLength
                )
                cycle_info = format_cycle_info(phase, days_since, user_input.lastPeriod.cycleLength)
                # Extract just the phase name for bolding
                phase_name = phase.replace(' Phase', '').replace(' phase', '')
                cycle_info_bold = cycle_info.lower().replace(phase_name.lower(), f"<b>{phase_name.lower()}</b>")
                summary_parts.append(f"Based on your cycle timing, {cycle_info_bold} - this gives us valuable insight into your current hormonal landscape.")
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not calculate cycle phase: {e}")
    
    # End with encouragement
    summary_parts.append("Together, we'll create a personalized approach that honors your unique needs and helps you feel your absolute best.")
    
    return " ".join(summary_parts)

def test_pipeline():
    """Test the pipeline with sample input"""
    test_input = "I have PCOS, irregular periods, and I'm struggling with weight gain. I want to manage my hormones naturally and lose weight. I'm also dealing with insulin resistance and fatigue."
    
    print("Testing RAG Pipeline...")
    print(f"Input: {test_input}")
    print("\nProcessing...")
    
    result = process_user_input(test_input)
    
    print("\nResult:")
    print("=" * 50)
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    test_pipeline()