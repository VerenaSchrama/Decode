"""
Data models for the health and nutrition application
"""

# Legacy input models (for API compatibility)
from .user_input import UserInput, Profile, Symptoms, Interventions, Habits, HabitItem, DietaryPreferences
from .user_input import SYMPTOM_OPTIONS, DIETARY_PREFERENCE_OPTIONS, INTERVENTION_OPTIONS, HABIT_OPTIONS

# Pydantic entity models (for validation and serialization)
from .entities import User, Intake, Intervention, Habit, UserHabit, CustomIntervention, IntakeRecommendation
from .schemas import (
    UserCreate, UserResponse, IntakeCreate, IntakeResponse, 
    InterventionResponse, HabitResponse, UserHabitCreate, UserHabitResponse,
    UserWithIntakes, IntakeWithRecommendation, InterventionWithHabits, UserWithHabits
)

# Supabase models
from .supabase_models import (
    SupabaseClient, supabase_client,
    SupabaseUser, SupabaseIntake, SupabaseIntervention, 
    SupabaseHabit, SupabaseUserHabit, SupabaseRecommendation,
    convert_user_input_to_supabase, convert_habits_to_supabase
)

__all__ = [
    # Legacy input models (for API compatibility)
    "UserInput", "Profile", "Symptoms", "Interventions", "Habits", "HabitItem", "DietaryPreferences",
    "SYMPTOM_OPTIONS", "DIETARY_PREFERENCE_OPTIONS", "INTERVENTION_OPTIONS", "HABIT_OPTIONS",
    
    # Pydantic entity models (for validation and serialization)
    "User", "Intake", "Intervention", "Habit", "UserHabit", "CustomIntervention", "IntakeRecommendation",
    
    # Schema models (for API requests/responses)
    "UserCreate", "UserResponse", "IntakeCreate", "IntakeResponse",
    "InterventionResponse", "HabitResponse", "UserHabitCreate", "UserHabitResponse",
    "UserWithIntakes", "IntakeWithRecommendation", "InterventionWithHabits", "UserWithHabits",
    
    # Supabase models (for database operations)
    "SupabaseClient", "supabase_client",
    "SupabaseUser", "SupabaseIntake", "SupabaseIntervention", 
    "SupabaseHabit", "SupabaseUserHabit", "SupabaseRecommendation",
    "convert_user_input_to_supabase", "convert_habits_to_supabase"
]
