"""
Cycle phase calculation utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple


def calculate_cycle_phase(last_period_date: str, cycle_length: int, current_date: Optional[datetime] = None) -> Tuple[str, int]:
    """
    Calculate the current cycle phase based on last period date and cycle length.
    
    Args:
        last_period_date: Date of last period in YYYY-MM-DD format
        cycle_length: Average cycle length in days
        current_date: Current date (defaults to now)
        
    Returns:
        Tuple of (phase_name, days_since_period)
    """
    if current_date is None:
        current_date = datetime.now()
    
    # Parse last period date
    last_period = datetime.strptime(last_period_date, '%Y-%m-%d')
    
    # Calculate days since last period
    days_since_period = (current_date - last_period).days
    
    # Handle case where current date is before last period (shouldn't happen in practice)
    if days_since_period < 0:
        return "Unknown", 0
    
    # Calculate phase based on cycle length
    if days_since_period <= 5:
        phase = "Menstrual Phase"
    elif days_since_period <= 13:
        phase = "Follicular Phase"
    elif days_since_period <= 16:
        phase = "Ovulation Phase"
    elif days_since_period <= cycle_length - 5:
        phase = "Luteal Phase"
    else:
        phase = "Pre-Menstrual Phase"
    
    return phase, days_since_period


def get_cycle_phase_description(phase: str) -> str:
    """
    Get a description of the cycle phase.
    
    Args:
        phase: The cycle phase name
        
    Returns:
        Description of the phase
    """
    descriptions = {
        "Menstrual Phase": "Your period is active. Focus on rest, iron-rich foods, and gentle movement.",
        "Follicular Phase": "Your body is preparing for ovulation. Energy levels are rising - great time for new habits!",
        "Ovulation Phase": "Peak fertility and energy. Perfect time for challenging activities and social engagement.",
        "Luteal Phase": "Progesterone is rising. Focus on stress management and comfort foods.",
        "Pre-Menstrual Phase": "Hormones are shifting. Prioritize self-care and be gentle with yourself."
    }
    
    return descriptions.get(phase, "Cycle phase information not available.")


def format_cycle_info(phase: str, days_since_period: int, cycle_length: int) -> str:
    """
    Format cycle information for display.
    
    Args:
        phase: Current cycle phase
        days_since_period: Days since last period
        cycle_length: Average cycle length
        
    Returns:
        Formatted cycle information string
    """
    if days_since_period == 0:
        return f"Currently in {phase} (Day 1 of cycle)"
    elif days_since_period < cycle_length:
        days_until_next = cycle_length - days_since_period
        return f"Currently in {phase} (Day {days_since_period + 1} of {cycle_length}, {days_until_next} days until next period)"
    else:
        return f"Currently in {phase} (Day {days_since_period + 1}, cycle may be irregular)"


