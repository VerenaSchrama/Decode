#!/usr/bin/env python3
"""
Notification Service - Listener for Intervention Completion Events
Sends notifications when intervention periods complete
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def send_completion_notification(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Event listener: Send notification when intervention completes
    
    Args:
        event_data: Event payload with period_id, user_id, intervention_name, etc.
        
    Returns:
        Result dictionary
    """
    user_id = event_data.get('user_id')
    intervention_name = event_data.get('intervention_name', 'intervention')
    period_id = event_data.get('period_id')
    auto_completed = event_data.get('auto_completed', False)
    
    if not user_id:
        logger.error("❌ Missing user_id in event data")
        return {"success": False, "error": "Missing user_id"}
    
    try:
        # Build notification payload
        notification = {
            "type": "intervention_completed",
            "title": "Intervention Completed 🎉" if not auto_completed else "Intervention Period Ended",
            "body": f"You've completed your {intervention_name} journey!" if not auto_completed else f"Your {intervention_name} period has ended.",
            "data": {
                "period_id": period_id,
                "intervention_name": intervention_name,
                "auto_completed": auto_completed
            }
        }
        
        # TODO: Integrate with actual notification service
        # For now, we'll log it and potentially store in a notifications table
        # Options:
        # 1. Store in notifications table for in-app notifications
        # 2. Send push notification via FCM/APNS
        # 3. Send email notification
        
        logger.info(f"📬 Notification prepared for user {user_id}: {notification['title']}")
        
        # Store notification in database (if notifications table exists)
        try:
            from models import supabase_client
            from datetime import datetime
            import uuid
            
            notification_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": notification["type"],
                "title": notification["title"],
                "body": notification["body"],
                "data": notification["data"],
                "read": False,
                "created_at": datetime.now().isoformat()
            }
            
            # Try to insert (table may not exist yet)
            supabase_client.client.table('notifications')\
                .insert(notification_record)\
                .execute()
            
            logger.info(f"✅ Stored notification for user {user_id}")
        except Exception as store_error:
            # Table may not exist - that's okay for now
            logger.warning(f"⚠️ Could not store notification (table may not exist): {store_error}")
        
        return {
            "success": True,
            "notification": notification
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending completion notification: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

