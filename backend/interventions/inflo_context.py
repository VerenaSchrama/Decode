"""
InFlo context enrichment
Handles adding InFlo book context to intervention recommendations
"""

from retrievers.vectorstores import get_main_retriever, is_vectorstore_available
from utils.helpers import format_docs

def get_inflo_context(user_input: str) -> str:
    """Get relevant context from InFlo book based on user input"""
    if not is_vectorstore_available():
        return "InFlo book context not available"
    
    try:
        retriever = get_main_retriever()
        docs = retriever.invoke(user_input)
        return format_docs(docs)
    except Exception as e:
        print(f"Error retrieving InFlo context: {e}")
        return "InFlo book context not available"

def get_intervention_with_inflo_context(user_input: str) -> dict:
    """
    Get intervention recommendation enhanced with InFlo book context
    
    Args:
        user_input: Raw text input from user describing their symptoms, goals, concerns
        
    Returns:
        Dictionary with intervention, habits, and additional InFlo context
    """
    from interventions.matcher import get_intervention_recommendation
    
    # Get base intervention recommendation
    intervention = get_intervention_recommendation(user_input)
    
    # Get additional context from InFlo book
    inflo_context = get_inflo_context(user_input)
    
    # Add InFlo context to the result
    intervention['additional_inflo_context'] = inflo_context
    
    return intervention

def enrich_intervention_with_context(intervention_data: dict, user_input: str) -> dict:
    """
    Enrich existing intervention data with InFlo book context
    
    Args:
        intervention_data: Existing intervention recommendation data
        user_input: User input for context retrieval
        
    Returns:
        Enriched intervention data with InFlo context
    """
    inflo_context = get_inflo_context(user_input)
    
    # Add context to existing data
    enriched_data = intervention_data.copy()
    enriched_data['additional_inflo_context'] = inflo_context
    
    return enriched_data
