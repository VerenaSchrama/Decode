#!/usr/bin/env python3
"""
Intervention Scheduler - Auto-complete expired intervention periods
Runs daily to check for and auto-complete expired periods
"""

from typing import List, Dict, Any
from datetime import datetime, date
import logging
from models import supabase_client
from services.intervention_service import intervention_service

logger = logging.getLogger(__name__)

async def auto_complete_expired_periods() -> Dict[str, Any]:
    """
    Auto-complete intervention periods that have passed their end_date (planned end date)
    
    Returns:
        Dictionary with completion results
    """
    try:
        today = date.today()
        logger.info(f"🔄 Checking for expired intervention periods (today: {today})")
        
        # Find all active periods past their end_date (planned end date)
        expired_result = supabase_client.client.table('intervention_periods')\
            .select('id, user_id, intervention_name, end_date')\
            .eq('status', 'active')\
            .lte('end_date', today.isoformat())\
            .execute()
        
        expired_periods = expired_result.data if expired_result.data else []
        
        if not expired_periods:
            logger.info("✅ No expired intervention periods found")
            return {
                "success": True,
                "expired_count": 0,
                "completed_count": 0,
                "periods": []
            }
        
        logger.info(f"📋 Found {len(expired_periods)} expired intervention periods")
        
        completed_periods = []
        failed_periods = []
        
        for period in expired_periods:
            period_id = period['id']
            intervention_name = period.get('intervention_name', 'Unknown')
            
            try:
                # Auto-complete the period
                result = intervention_service.complete_period(
                    period_id=period_id,
                    notes="Auto-completed: period expired",
                    auto_completed=True
                )
                
                if result.get('success'):
                    completed_periods.append({
                        "period_id": period_id,
                        "intervention_name": intervention_name
                    })
                    logger.info(f"✅ Auto-completed period: {intervention_name} ({period_id})")
                else:
                    failed_periods.append({
                        "period_id": period_id,
                        "error": result.get('error', 'Unknown error')
                    })
                    logger.error(f"❌ Failed to auto-complete period {period_id}: {result.get('error')}")
                    
            except Exception as e:
                failed_periods.append({
                    "period_id": period_id,
                    "error": str(e)
                })
                logger.error(f"❌ Exception auto-completing period {period_id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"✅ Auto-completion complete: {len(completed_periods)} succeeded, {len(failed_periods)} failed")
        
        return {
            "success": True,
            "expired_count": len(expired_periods),
            "completed_count": len(completed_periods),
            "failed_count": len(failed_periods),
            "completed_periods": completed_periods,
            "failed_periods": failed_periods
        }
        
    except Exception as e:
        logger.error(f"❌ Error in auto_complete_expired_periods: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

