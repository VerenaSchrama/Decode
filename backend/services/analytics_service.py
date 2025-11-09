#!/usr/bin/env python3
"""
Analytics Service - Listener for Intervention Completion Events
Generates completion summaries with mood tracking analytics
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import uuid
from models import supabase_client

logger = logging.getLogger(__name__)

def generate_completion_summary(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Event listener: Generate analytics summary when intervention completes
    
    Calculates:
    - Habit adherence rate (% of days completed)
    - Average mood score
    - Mood trend (improved/declined/stable)
    - Streaks and missed days
    
    Args:
        event_data: Event payload with period_id, user_id, etc.
        
    Returns:
        Result dictionary with summary data
    """
    period_id = event_data.get('period_id')
    user_id = event_data.get('user_id')
    
    if not period_id or not user_id:
        logger.error("❌ Missing period_id or user_id in event data")
        return {"success": False, "error": "Missing required fields"}
    
    try:
        # 1. Get intervention period details
        period_result = supabase_client.client.table('intervention_periods')\
            .select('start_date, end_date, selected_habits')\
            .eq('id', period_id)\
            .single()\
            .execute()
        
        if not period_result.data:
            logger.warning(f"⚠️ Intervention period {period_id} not found")
            return {"success": False, "error": "Period not found"}
        
        period_data = period_result.data
        start_date = datetime.fromisoformat(period_data['start_date'].replace('Z', '+00:00')).date()
        end_date = period_data.get('end_date')
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        else:
            end_date = datetime.now().date()
        
        selected_habits = period_data.get('selected_habits', [])
        total_habits = len(selected_habits)
        
        # 2. Get daily summaries for the period
        # Try to use intervention_period_id for accurate filtering, fall back to date filtering
        try:
            summaries_result = supabase_client.client.table('daily_summaries')\
                .select('entry_date, completion_percentage, total_habits, completed_habits')\
                .eq('user_id', user_id)\
                .eq('intervention_period_id', period_id)\
                .order('entry_date', desc=False)\
                .execute()
            
            # If no results with intervention_period_id, fall back to date filtering
            if not summaries_result.data:
                summaries_result = supabase_client.client.table('daily_summaries')\
                    .select('entry_date, completion_percentage, total_habits, completed_habits')\
                    .eq('user_id', user_id)\
                    .gte('entry_date', start_date.isoformat())\
                    .lte('entry_date', end_date.isoformat())\
                    .order('entry_date', desc=False)\
                    .execute()
        except Exception as e:
            # Column might not exist yet, fall back to date filtering
            logger.warning(f"⚠️ intervention_period_id column may not exist, using date filtering: {e}")
            summaries_result = supabase_client.client.table('daily_summaries')\
                .select('entry_date, completion_percentage, total_habits, completed_habits')\
                .eq('user_id', user_id)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=False)\
                .execute()
        
        summaries = summaries_result.data if summaries_result.data else []
        
        # 3. Get mood data for the period
        # Try to use intervention_period_id for accurate filtering, fall back to date filtering
        try:
            moods_result = supabase_client.client.table('daily_moods')\
                .select('entry_date, mood')\
                .eq('user_id', user_id)\
                .eq('intervention_period_id', period_id)\
                .order('entry_date', desc=False)\
                .execute()
            
            if not moods_result.data:
                moods_result = supabase_client.client.table('daily_moods')\
                    .select('entry_date, mood')\
                    .eq('user_id', user_id)\
                    .gte('entry_date', start_date.isoformat())\
                    .lte('entry_date', end_date.isoformat())\
                    .order('entry_date', desc=False)\
                    .execute()
        except Exception as e:
            # Column might not exist yet, fall back to date filtering
            logger.warning(f"⚠️ intervention_period_id column may not exist, using date filtering: {e}")
            moods_result = supabase_client.client.table('daily_moods')\
                .select('entry_date, mood')\
                .eq('user_id', user_id)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=False)\
                .execute()
        
        moods = moods_result.data if moods_result.data else []
        moods_by_date = {m['entry_date']: m.get('mood') for m in moods if m.get('mood') is not None}
        
        # 4. Calculate adherence metrics
        total_days = (end_date - start_date).days + 1
        tracked_days = len(summaries)
        
        if tracked_days == 0:
            adherence_rate = 0.0
            avg_completion = 0.0
        else:
            # Calculate average completion percentage
            completion_percentages = [s.get('completion_percentage', 0) for s in summaries if s.get('completion_percentage') is not None]
            avg_completion = sum(completion_percentages) / len(completion_percentages) if completion_percentages else 0.0
            
            # Adherence = (days tracked / total days) * (average completion / 100)
            adherence_rate = (tracked_days / total_days) * (avg_completion / 100) if total_days > 0 else 0.0
        
        # 5. Calculate mood metrics
        mood_values = [mood for mood in moods_by_date.values() if mood is not None]
        avg_mood = sum(mood_values) / len(mood_values) if mood_values else None
        
        # Calculate mood trend (compare first half vs second half)
        mood_trend = "stable"
        if len(mood_values) >= 4:
            mid_point = len(mood_values) // 2
            first_half_avg = sum(mood_values[:mid_point]) / mid_point
            second_half_avg = sum(mood_values[mid_point:]) / len(mood_values[mid_point:])
            
            if second_half_avg > first_half_avg + 0.3:
                mood_trend = "improved"
            elif second_half_avg < first_half_avg - 0.3:
                mood_trend = "declined"
            else:
                mood_trend = "stable"
        
        # 6. Calculate streaks
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        for summary in sorted(summaries, key=lambda x: x['entry_date'], reverse=True):
            completion = summary.get('completion_percentage', 0)
            if completion >= 80:
                temp_streak += 1
                if current_streak == 0:
                    current_streak = temp_streak
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0
        
        # 7. Calculate missed days
        tracked_dates = {s['entry_date'] for s in summaries}
        all_dates = set()
        current = start_date
        while current <= end_date:
            all_dates.add(current.isoformat())
            current += timedelta(days=1)
        missed_days = len(all_dates - tracked_dates)
        
        # 8. Build summary JSON
        summary_json = {
            "total_days": total_days,
            "tracked_days": tracked_days,
            "missed_days": missed_days,
            "total_habits": total_habits,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_percentages": completion_percentages,
            "mood_values": mood_values
        }
        
        # 9. Store completion summary
        summary_data = {
            "id": str(uuid.uuid4()),
            "intervention_period_id": period_id,
            "user_id": user_id,
            "adherence_rate": round(adherence_rate * 100, 2),  # Store as percentage
            "average_mood": round(avg_mood, 2) if avg_mood else None,
            "mood_trend": mood_trend,
            "summary_json": summary_json,
            "created_at": datetime.now().isoformat()
        }
        
        # Insert into completion_summaries table
        # Note: Table may need to be created via migration
        try:
            summary_result = supabase_client.client.table('completion_summaries')\
                .insert(summary_data)\
                .execute()
            
            logger.info(f"✅ Generated completion summary for period {period_id}")
            
            return {
                "success": True,
                "summary_id": summary_data['id'],
                "adherence_rate": adherence_rate,
                "average_mood": avg_mood,
                "mood_trend": mood_trend,
                "tracked_days": tracked_days,
                "total_days": total_days
            }
        except Exception as insert_error:
            # If table doesn't exist, log warning but don't fail
            logger.warning(f"⚠️ Could not insert completion summary (table may not exist): {insert_error}")
            logger.warning("   Summary data calculated but not stored")
            return {
                "success": True,
                "warning": "Summary calculated but not stored (table missing)",
                "adherence_rate": adherence_rate,
                "average_mood": avg_mood,
                "mood_trend": mood_trend
            }
        
    except Exception as e:
        logger.error(f"❌ Error generating completion summary: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

