#!/usr/bin/env python3
"""
Intervention Service - Event-Driven Completion Flow
Orchestrates intervention period completion with event-driven architecture
"""

from typing import Dict, Optional, Any
from datetime import datetime
import logging
from models import supabase_client
from services.event_bus import event_bus

logger = logging.getLogger(__name__)

class InterventionService:
    """Service for managing intervention periods with event-driven completion"""
    
    def __init__(self):
        self.supabase = supabase_client
    
    def complete_period(
        self, 
        period_id: str, 
        notes: Optional[str] = None,
        auto_completed: bool = False
    ) -> Dict[str, Any]:
        """
        Complete an intervention period with event-driven architecture
        
        Args:
            period_id: Intervention period ID
            notes: Optional completion notes
            auto_completed: Whether this was auto-completed by scheduler
            
        Returns:
            Result dictionary with success status
        """
        try:
            # 1. Check if already completed (prevent double completion)
            existing = self.supabase.client.table('intervention_periods')\
                .select('status, user_id, intervention_name')\
                .eq('id', period_id)\
                .single()\
                .execute()
            
            if not existing.data:
                return {
                    "success": False,
                    "error": "Intervention period not found"
                }
            
            if existing.data.get('status') == 'completed':
                logger.warning(f"⚠️ Intervention period {period_id} already completed")
                return {
                    "success": True,
                    "message": "Already completed",
                    "already_completed": True
                }
            
            # 2. Atomic update of intervention_periods table
            update_data = {
                "status": "completed",
                "actual_end_date": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if notes:
                update_data["notes"] = notes
            
            if auto_completed and not notes:
                update_data["notes"] = "Auto-completed: period expired"
            
            result = self.supabase.client.table('intervention_periods')\
                .update(update_data)\
                .eq('id', period_id)\
                .execute()
            
            if not result.data:
                raise Exception("Failed to update intervention period")
            
            logger.info(f"✅ Marked intervention period {period_id} as completed")
            
            # 3. Publish event for listeners
            event_data = {
                "period_id": period_id,
                "user_id": existing.data['user_id'],
                "intervention_name": existing.data.get('intervention_name', 'Unknown'),
                "notes": notes,
                "auto_completed": auto_completed,
                "completed_at": datetime.now().isoformat()
            }
            
            # Publish event (listeners handle side effects)
            event_results = event_bus.publish("intervention.completed", event_data)
            
            # 4. Return success with event processing results
            return {
                "success": True,
                "message": "Intervention period completed",
                "period_id": period_id,
                "event_results": event_results
            }
            
        except Exception as e:
            logger.error(f"❌ Error completing intervention period: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def mark_period_completed(
        self, 
        period_id: str, 
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Repository method: Mark period as completed in database
        Used internally by complete_period
        """
        update_data = {
            "status": "completed",
            "actual_end_date": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if notes:
            update_data["notes"] = notes
        
        result = self.supabase.client.table('intervention_periods')\
            .update(update_data)\
            .eq('id', period_id)\
            .execute()
        
        return result

# Global instance
intervention_service = InterventionService()

