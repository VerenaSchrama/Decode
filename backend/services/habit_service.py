#!/usr/bin/env python3
"""
Habit Service - Listener for Intervention Completion Events
Updates user_habits when intervention period completes
"""

from typing import Dict, Any
from datetime import datetime
import logging
from models import supabase_client

logger = logging.getLogger(__name__)

def complete_related_habits(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Event listener: Update user_habits status when intervention completes
    
    Args:
        event_data: Event payload with period_id, user_id, etc.
        
    Returns:
        Result dictionary
    """
    period_id = event_data.get('period_id')
    user_id = event_data.get('user_id')
    
    if not period_id or not user_id:
        logger.error("❌ Missing period_id or user_id in event data")
        return {"success": False, "error": "Missing required fields"}
    
    try:
        # Get the intervention period to find associated habits
        period_result = supabase_client.client.table('intervention_periods')\
            .select('selected_habits')\
            .eq('id', period_id)\
            .single()\
            .execute()
        
        if not period_result.data:
            logger.warning(f"⚠️ Intervention period {period_id} not found")
            return {"success": False, "error": "Period not found"}
        
        selected_habits = period_result.data.get('selected_habits', [])
        
        if not selected_habits:
            logger.info(f"ℹ️ No selected_habits for period {period_id}, skipping habit update")
            return {"success": True, "message": "No habits to update"}
        
        # Update user_habits by matching habit names
        # Note: We use habit_name because intervention_periods stores names, not IDs
        updated_count = 0
        
        for habit_name in selected_habits:
            try:
                update_result = supabase_client.client.table('user_habits')\
                    .update({
                        'status': 'completed',
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('user_id', user_id)\
                    .eq('habit_name', habit_name)\
                    .eq('status', 'active')\
                    .execute()
                
                if update_result.data:
                    updated_count += len(update_result.data)
                    logger.info(f"✅ Updated habit '{habit_name}' to completed")
            except Exception as habit_error:
                logger.error(f"❌ Error updating habit '{habit_name}': {habit_error}")
                # Continue with other habits
        
        logger.info(f"✅ Updated {updated_count} habits to completed status")
        
        return {
            "success": True,
            "updated_habits_count": updated_count,
            "total_habits": len(selected_habits)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in complete_related_habits: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

