"""
Cycle Phase Management Service
Centralized cycle phase calculation and storage in Supabase
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from utils.cycle_calculator import calculate_cycle_phase as calc_phase


class CyclePhaseService:
    """Service for managing user cycle phases with Supabase storage"""
    
    def __init__(self):
        from models import supabase_client
        self.supabase = supabase_client
    
    async def get_current_phase(self, user_id: str) -> Dict:
        """
        Get cached cycle phase for user, recalculate if outdated
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with current_phase, days_since, cycle_length, last_updated
        """
        try:
            # Get stored cycle phase from Supabase
            result = self.supabase.client.table('cycle_phases')\
                .select('*')\
                .eq('user_id', user_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                phase_data = result.data[0]
                
                # Check if recalculation needed (older than 1 day or if phase has likely changed)
                days_since_last_update = (datetime.now() - datetime.fromisoformat(phase_data['last_updated'].replace('Z', '+00:00'))).days
                
                if days_since_last_update > 0 and phase_data.get('auto_recalculate', True):
                    # Recalculate phase
                    await self.update_cycle_phase(
                        user_id,
                        phase_data['last_period_date'],
                        phase_data['cycle_length']
                    )
                    # Re-fetch after update
                    result = self.supabase.client.table('cycle_phases')\
                        .select('*')\
                        .eq('user_id', user_id)\
                        .execute()
                    phase_data = result.data[0]
                
                return {
                    'success': True,
                    'current_phase': phase_data['current_phase'],
                    'days_since_period': phase_data['calculated_days_since'],
                    'cycle_length': phase_data['cycle_length'],
                    'last_period_date': phase_data['last_period_date'],
                    'last_updated': phase_data['last_updated']
                }
            else:
                return {
                    'success': False,
                    'message': 'No cycle phase data found for user'
                }
                
        except Exception as e:
            print(f"Error getting cycle phase: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_cycle_phase(
        self, 
        user_id: str, 
        last_period_date: str, 
        cycle_length: int,
        auto_recalculate: bool = True
    ) -> Dict:
        """
        Calculate and store cycle phase for user
        
        Args:
            user_id: User ID
            last_period_date: Date of last period (YYYY-MM-DD)
            cycle_length: Average cycle length in days
            auto_recalculate: Whether to automatically recalculate daily
            
        Returns:
            Dict with success status and calculated phase data
        """
        try:
            # Calculate phase using existing calculator
            phase_name, days_since_period = calc_phase(last_period_date, cycle_length)
            
            # Store in cycle_phases table (upsert)
            phase_data = {
                'user_id': user_id,
                'current_phase': phase_name.lower().replace(' phase', '').replace('phase', '').strip(),
                'cycle_length': cycle_length,
                'last_period_date': last_period_date,
                'calculated_days_since': days_since_period,
                'last_updated': datetime.now().isoformat(),
                'auto_recalculate': auto_recalculate
            }
            
            # Upsert to cycle_phases table
            result = self.supabase.client.table('cycle_phases')\
                .upsert(phase_data, { 'on_conflict': 'user_id' })\
                .execute()
            
            print(f"✅ Updated cycle phase for user {user_id}: {phase_name} (day {days_since_period})")
            
            return {
                'success': True,
                'current_phase': phase_data['current_phase'],
                'days_since_period': days_since_period,
                'cycle_length': cycle_length,
                'last_updated': phase_data['last_updated']
            }
            
        except Exception as e:
            print(f"Error updating cycle phase: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def recalculate_all_phases(self) -> Dict:
        """
        Recalculate cycle phases for all users with auto_recalculate=true
        Run this as a scheduled task daily at 00:01
        
        Returns:
            Dict with count of updated users
        """
        try:
            # Get all users with auto_recalculate enabled
            result = self.supabase.client.table('cycle_phases')\
                .select('user_id, last_period_date, cycle_length')\
                .eq('auto_recalculate', True)\
                .execute()
            
            updated_count = 0
            for user_phase in result.data:
                await self.update_cycle_phase(
                    user_phase['user_id'],
                    user_phase['last_period_date'],
                    user_phase['cycle_length']
                )
                updated_count += 1
            
            print(f"✅ Recalculated {updated_count} user cycle phases")
            
            return {
                'success': True,
                'updated_count': updated_count
            }
            
        except Exception as e:
            print(f"Error recalculating all phases: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_cycle_phase_service = None

def get_cycle_phase_service() -> CyclePhaseService:
    """Get singleton instance of CyclePhaseService"""
    global _cycle_phase_service
    if _cycle_phase_service is None:
        _cycle_phase_service = CyclePhaseService()
    return _cycle_phase_service

