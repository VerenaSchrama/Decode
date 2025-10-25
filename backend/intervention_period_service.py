#!/usr/bin/env python3
"""
Intervention Period Tracking System
Tracks when users start interventions and their completion status
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

class InterventionPeriod(BaseModel):
    """Model for tracking intervention periods"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_uuid: str = Field(..., description="User UUID")
    intake_id: str = Field(..., description="Reference to intake that generated this intervention")
    intervention_name: str = Field(..., description="Name of the intervention")
    intervention_id: Optional[str] = Field(None, description="ID from InterventionsBASE table")
    selected_habits: List[str] = Field(default_factory=list, description="Habits selected by user")
    start_date: datetime = Field(default_factory=datetime.now, description="When intervention started")
    planned_end_date: Optional[datetime] = Field(None, description="Planned end date")
    actual_end_date: Optional[datetime] = Field(None, description="Actual completion date")
    status: str = Field(default="active", description="active, completed, paused, abandoned")
    cycle_phase_at_start: Optional[str] = Field(None, description="Cycle phase when started")
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Overall completion percentage")
    notes: Optional[str] = Field(None, description="User notes about the intervention")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class InterventionPeriodService:
    """Service for managing intervention periods"""
    
    def __init__(self):
        from models import supabase_client
        self.supabase = supabase_client
    
    def start_intervention_period(
        self, 
        user_uuid: str, 
        intake_id: str, 
        intervention_name: str,
        selected_habits: List[str],
        intervention_id: Optional[str] = None,
        planned_duration_days: int = 30,
        cycle_phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start tracking a new intervention period"""
        
        # Calculate planned end date
        planned_end_date = datetime.now() + timedelta(days=planned_duration_days)
        
        # Create intervention period record
        period_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_uuid,  # This matches the actual column name in the table
            "intake_id": intake_id,
            "intervention_name": intervention_name,
            "intervention_id": intervention_id,
            "selected_habits": selected_habits,
            "start_date": datetime.now().isoformat(),
            "planned_end_date": planned_end_date.isoformat(),
            "actual_end_date": None,
            "status": "active",
            "cycle_phase_at_start": cycle_phase,
            "completion_percentage": 0.0,
            "notes": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # Insert into intervention_periods table
            result = self.supabase.client.table('intervention_periods').insert(period_data).execute()
            
            if result.data:
                print(f"✅ Started intervention period: {intervention_name} for user {user_uuid}")
                return {
                    "success": True,
                    "period_id": result.data[0]['id'],
                    "message": f"Started tracking intervention: {intervention_name}"
                }
            else:
                raise Exception("Failed to insert intervention period")
                
        except Exception as e:
            print(f"❌ Error starting intervention period: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start intervention tracking"
            }
    
    def update_intervention_progress(
        self, 
        period_id: str, 
        completion_percentage: float,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update intervention progress"""
        
        update_data = {
            "completion_percentage": completion_percentage,
            "updated_at": datetime.now().isoformat()
        }
        
        if notes:
            update_data["notes"] = notes
        
        try:
            result = self.supabase.client.table('intervention_periods').update(update_data).eq('id', period_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": f"Updated progress to {completion_percentage}%"
                }
            else:
                raise Exception("Failed to update progress")
                
        except Exception as e:
            print(f"❌ Error updating progress: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_intervention_period(
        self, 
        period_id: str, 
        completion_percentage: float = 100.0,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark intervention period as completed"""
        
        update_data = {
            "status": "completed",
            "actual_end_date": datetime.now().isoformat(),
            "completion_percentage": completion_percentage,
            "updated_at": datetime.now().isoformat()
        }
        
        if notes:
            update_data["notes"] = notes
        
        try:
            result = self.supabase.client.table('intervention_periods').update(update_data).eq('id', period_id).execute()
            
            if result.data:
                print(f"✅ Completed intervention period: {period_id}")
                return {
                    "success": True,
                    "message": "Intervention period completed"
                }
            else:
                raise Exception("Failed to complete intervention")
                
        except Exception as e:
            print(f"❌ Error completing intervention: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_intervention_periods(self, user_uuid: str) -> Dict[str, Any]:
        """Get all intervention periods for a user"""
        
        try:
            result = self.supabase.client.table('intervention_periods').select('*').eq('user_id', user_uuid).order('created_at', desc=True).execute()
            
            return {
                "success": True,
                "periods": result.data,
                "count": len(result.data)
            }
            
        except Exception as e:
            print(f"❌ Error getting intervention periods: {e}")
            return {
                "success": False,
                "error": str(e),
                "periods": []
            }
    
    def get_active_intervention_period(self, user_uuid: str) -> Dict[str, Any]:
        """Get the currently active intervention period for a user"""
        
        try:
            result = self.supabase.client.table('intervention_periods').select('*').eq('user_id', user_uuid).eq('status', 'active').order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                return {
                    "success": True,
                    "period": result.data[0],
                    "found": True
                }
            else:
                return {
                    "success": True,
                    "period": None,
                    "found": False
                }
                
        except Exception as e:
            print(f"❌ Error getting active intervention: {e}")
            return {
                "success": False,
                "error": str(e),
                "period": None
            }

# Global instance
intervention_period_service = InterventionPeriodService()
