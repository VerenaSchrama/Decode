"""
LLM-Generated Explanations for Intervention Recommendations
Generates personalized "why" explanations for each recommended intervention
"""

from typing import Dict, List
from llm import get_llm
from models import UserInput

def generate_intervention_explanation(
    user_input: UserInput, 
    intervention: Dict, 
    similarity_score: float
) -> str:
    """
    Generate a personalized explanation for why an intervention was recommended
    
    Args:
        user_input: User's structured input data
        intervention: Intervention data from database
        similarity_score: Similarity score between user and intervention
        
    Returns:
        Personalized explanation string
    """
    try:
        llm = get_llm()
        
        # Build user context
        user_context = _build_user_context(user_input)
        
        # Build intervention context
        intervention_context = _build_intervention_context(intervention, similarity_score)
        
        # Create the prompt
        prompt = f"""
You are a knowledgeable nutritionist and women's health expert. Generate a personalized, empathetic explanation for why this specific intervention was recommended for this user.

USER PROFILE:
{user_context}

RECOMMENDED INTERVENTION:
{intervention_context}

TASK:
Write a warm, personalized explanation (2-3 sentences) that:
1. Acknowledges the user's specific symptoms/challenges
2. Explains why this intervention is particularly suitable for them
3. Connects their symptoms to the intervention's benefits
4. Uses encouraging, supportive language
5. Mentions the high match percentage naturally

TONE:
- Warm and empathetic
- Professional but conversational
- Encouraging and supportive
- Specific to their situation
- Avoid medical jargon

FORMAT:
Write as if you're speaking directly to the user, starting with "This intervention is perfect for you because..."

EXAMPLE:
"This intervention is perfect for you because your PCOS symptoms and insulin resistance directly align with how this approach stabilizes blood sugar and reduces androgen levels. With an 85% match to your profile, it specifically targets the hormonal imbalances you're experiencing while supporting sustainable weight management."

Generate the explanation:
"""

        # Get LLM response
        response = llm.invoke(prompt)
        
        # Extract the explanation (remove any extra formatting)
        explanation = response.content.strip()
        
        # Clean up the response
        if explanation.startswith('"') and explanation.endswith('"'):
            explanation = explanation[1:-1]
        
        return explanation
        
    except Exception as e:
        print(f"Error generating explanation: {e}")
        # Fallback explanation
        return f"This intervention matches your profile with {similarity_score:.0%} compatibility, specifically targeting your symptoms and goals."

def _build_user_context(user_input: UserInput) -> str:
    """Build user context for LLM prompt"""
    context_parts = []
    
    # Basic info
    if user_input.profile.name:
        context_parts.append(f"Name: {user_input.profile.name}")
    context_parts.append(f"Age: {user_input.profile.age}")
    
    # Symptoms
    if user_input.symptoms.selected:
        context_parts.append(f"Primary symptoms: {', '.join(user_input.symptoms.selected)}")
    if user_input.symptoms.additional:
        context_parts.append(f"Additional symptoms: {user_input.symptoms.additional}")
    
    # Previous interventions
    if user_input.interventions.selected:
        tried_interventions = [item.intervention for item in user_input.interventions.selected]
        context_parts.append(f"Previously tried: {', '.join(tried_interventions)}")
    
    # Dietary preferences
    if user_input.dietaryPreferences.selected:
        context_parts.append(f"Dietary preferences: {', '.join(user_input.dietaryPreferences.selected)}")
    
    # Cycle info
    if user_input.lastPeriod and user_input.lastPeriod.hasPeriod:
        context_parts.append("Has regular menstrual cycle")
    elif user_input.lastPeriod and not user_input.lastPeriod.hasPeriod:
        context_parts.append("Does not have regular menstrual cycle")
    
    return "\n".join(context_parts)

def _build_intervention_context(intervention: Dict, similarity_score: float) -> str:
    """Build intervention context for LLM prompt"""
    context_parts = []
    
    context_parts.append(f"Intervention: {intervention.get('intervention_name', 'Unknown')}")
    context_parts.append(f"Match score: {similarity_score:.0%}")
    
    if intervention.get('intervention_profile'):
        context_parts.append(f"Description: {intervention['intervention_profile']}")
    
    if intervention.get('symptoms_match'):
        context_parts.append(f"Targets symptoms: {intervention['symptoms_match']}")
    
    if intervention.get('persona_fit'):
        context_parts.append(f"Best for: {intervention['persona_fit']}")
    
    if intervention.get('dietary_fit'):
        context_parts.append(f"Dietary fit: {intervention['dietary_fit']}")
    
    return "\n".join(context_parts)

def generate_batch_explanations(
    user_input: UserInput, 
    interventions: List[Dict]
) -> List[str]:
    """
    Generate explanations for multiple interventions efficiently
    
    Args:
        user_input: User's structured input data
        interventions: List of intervention dictionaries
        
    Returns:
        List of explanation strings
    """
    explanations = []
    
    for intervention in interventions:
        similarity_score = intervention.get('similarity_score', 0.0)
        explanation = generate_intervention_explanation(user_input, intervention, similarity_score)
        explanations.append(explanation)
    
    return explanations

