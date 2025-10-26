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
    """Model for tracking intervention periods - aligned with Supabase schema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User ID from profiles table")
    intake_id: str = Field(..., description="Reference to intake that generated this intervention")
    intervention_name: str = Field(..., description="Name of the intervention")
    intervention_id: Optional[str] = Field(None, description="ID from InterventionsBASE table")
    selected_habits: List[str] = Field(default_factory=list, description="Habits selected by user")
    start_date: datetime = Field(default_factory=datetime.now, description="When intervention started")
    end_date: Optional[datetime] = Field(None, description="Planned end date (maps to 'end_date' in DB)")
    actual_end_date: Optional[datetime] = Field(None, description="Actual completion date")
    status: str = Field(default="active", description="active, completed, paused, abandoned")
    cycle_phase: Optional[str] = Field(None, description="Cycle phase when started (maps to 'cycle_phase' in DB)")
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
        user_id: str, 
        intake_id: str, 
        intervention_name: str,
        selected_habits: List[str],
        intervention_id: Optional[str] = None,
        planned_duration_days: int = 30,
        cycle_phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start tracking a new intervention period"""
        
        # Calculate planned end date
        end_date_dt = datetime.now() + timedelta(days=planned_duration_days)
        
        # Create intervention period record - aligned with Supabase schema
        period_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "intake_id": intake_id,
            "intervention_name": intervention_name,  # Now properly mapped to DB column
            "intervention_id": intervention_id,
            "selected_habits": selected_habits,  # Now properly mapped to JSONB column
            "start_date": datetime.now().isoformat(),
            "end_date": end_date_dt.isoformat(),  # Maps to 'end_date' in DB (not 'planned_end_date')
            "planned_duration_days": planned_duration_days,  # Additional field for tracking
            "actual_end_date": None,
            "status": "active",
            "cycle_phase": cycle_phase,  # Maps to 'cycle_phase' in DB (not 'cycle_phase_at_start')
            "notes": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # Insert into intervention_periods table
            result = self.supabase.client.table('intervention_periods').insert(period_data).execute()
            
            if result.data:
                print(f"✅ Started intervention period: {intervention_name} for user {user_id}")
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
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update intervention progress"""
        
        update_data = {
            "updated_at": datetime.now().isoformat()
        }
        
        if notes:
            update_data["notes"] = notes
        
        try:
            result = self.supabase.client.table('intervention_periods').update(update_data).eq('id', period_id).execute()
            
            if result.data:
                return {
                    "success": True,
                    "message": f"Updated progress"
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
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark intervention period as completed"""
        
        update_data = {
            "status": "completed",
            "actual_end_date": datetime.now().isoformat(),
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
    
    def get_user_intervention_periods(self, user_id: str) -> Dict[str, Any]:
        """Get all intervention periods for a user"""
        
        try:
            result = self.supabase.client.table('intervention_periods').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            
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
    
    def get_active_intervention_period(self, user_id: str) -> Dict[str, Any]:
        """Get the currently active intervention period for a user"""
        
        try:
            result = self.supabase.client.table('intervention_periods').select('*').eq('user_id', user_id).eq('status', 'active').order('created_at', desc=True).limit(1).execute()
            
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
