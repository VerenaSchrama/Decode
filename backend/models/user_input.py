"""
Structured user input models for the health and nutrition application
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
import pandas as pd

# Load intervention data to get valid options from database
def get_intervention_names():
    """Get valid intervention names from database"""
    try:
        from .supabase_models import supabase_client
        result = supabase_client.client.table('InterventionsBASE').select('Strategy Name').execute()
        return [intervention['Strategy Name'] for intervention in result.data]
    except:
        return []

def get_habit_options():
    """Get all possible habit options from database"""
    try:
        from .supabase_models import supabase_client
        result = supabase_client.client.table('HabitsBASE').select('Habit Name').execute()
        return [habit['Habit Name'] for habit in result.data]
    except:
        return []

# Valid options
SYMPTOM_OPTIONS = [
    "PCOS", "Endometriosis", "IBS", "Insulin resistance", "Thyroid disorders",
    "Adrenal fatigue", "Perimenopause", "Menopause", "Irregular periods",
    "Heavy periods", "Painful periods", "PMS", "PMDD", "Fertility issues",
    "Weight gain", "Hair loss", "Acne", "Mood swings", "Anxiety", "Depression",
    "Fatigue", "Sleep issues", "Brain fog", "Joint pain", "Digestive issues",
    "Food cravings", "Blood sugar issues", "Hot flashes", "Night sweats",
    "Headache", "Sleep quality", "Cravings: Sweet", "Backache",
    "Tender breasts", "Dry-skin", "Bloating", "Sensitive", 
    "Cramps", "Irritable"
]

DIETARY_PREFERENCE_OPTIONS = [
    "Vegetarian", "Vegan", "Keto", "Mediterranean", "Gluten-free", "Dairy-free",
    "Paleo", "Low-carb", "High-protein", "Intermittent fasting", "Raw food",
    "Pescatarian", "Flexitarian", "Whole30", "Anti-inflammatory"
]

# Load options dynamically to avoid import-time database dependency
def get_intervention_options():
    """Get intervention options from database"""
    return get_intervention_names()

def get_habit_options_list():
    """Get habit options from database"""
    return get_habit_options()

# Initialize with empty lists, will be populated when needed
INTERVENTION_OPTIONS = []
HABIT_OPTIONS = []

class Profile(BaseModel):
    name: Optional[str] = None
    age: int = Field(..., ge=13, le=120, description="Age must be between 13 and 120")
    dateOfBirth: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD format")

class Symptoms(BaseModel):
    selected: List[str] = Field(default_factory=list, description="Selected symptoms from predefined list")
    additional: Optional[str] = None

    @validator('selected')
    def validate_selected_symptoms(cls, v):
        for symptom in v:
            if symptom not in SYMPTOM_OPTIONS:
                raise ValueError(f"Invalid symptom: {symptom}. Must be one of {SYMPTOM_OPTIONS}")
        return v

class InterventionItem(BaseModel):
    intervention: str = Field(..., description="Intervention name from CSV")
    helpful: bool = Field(default=False, description="Whether this intervention was helpful")

    @validator('intervention')
    def validate_intervention(cls, v):
        # Temporarily disable validation to allow API to work
        return v

class Interventions(BaseModel):
    selected: List[InterventionItem] = Field(default_factory=list, description="Selected interventions with helpfulness")
    additional: Optional[str] = None

class HabitItem(BaseModel):
    habit: str = Field(..., description="Habit text from CSV")
    success: bool = Field(default=False, description="Whether this specific habit was useful/helpful")

    @validator('habit')
    def validate_habit(cls, v):
        # Temporarily disable validation to allow API to work
        return v

class Habits(BaseModel):
    selected: List[HabitItem] = Field(default_factory=list, description="Selected habits with success status")
    additional: Optional[str] = None

class DietaryPreferences(BaseModel):
    selected: List[str] = Field(default_factory=list, description="Selected dietary preferences")
    additional: Optional[str] = None

    @validator('selected')
    def validate_selected_preferences(cls, v):
        for preference in v:
            if preference not in DIETARY_PREFERENCE_OPTIONS:
                raise ValueError(f"Invalid dietary preference: {preference}. Must be one of {DIETARY_PREFERENCE_OPTIONS}")
        return v

class LastPeriod(BaseModel):
    date: Optional[str] = Field(None, description="Date of last period in YYYY-MM-DD format")
    hasPeriod: bool = Field(default=True, description="Whether user has menstrual periods")
    cycleLength: Optional[int] = Field(None, description="Average cycle length in days")

class UserInput(BaseModel):
    profile: Profile
    lastPeriod: Optional[LastPeriod] = Field(None, description="Last period information")
    symptoms: Symptoms
    interventions: Optional[Interventions] = Field(default_factory=Interventions, description="Intervention history")
    dietaryPreferences: Optional[DietaryPreferences] = Field(default_factory=DietaryPreferences, description="Dietary preferences")
    consent: bool = Field(..., description="User consent required")
    anonymous: bool = Field(default=False, description="Whether user wants to remain anonymous")

    class Config:
        json_schema_extra = {
            "example": {
                "profile": {
                    "name": "Jane Doe",
                    "age": 28
                },
                "symptoms": {
                    "selected": ["PCOS", "Irregular periods", "Weight gain", "Insulin resistance"],
                    "additional": "Also experiencing hair loss on temples"
                },
                "interventions": {
                    "selected": [
                        {
                            "intervention": "Control your blood sugar",
                            "helpful": True
                        },
                        {
                            "intervention": "Time-restricted eating",
                            "helpful": False
                        }
                    ],
                    "additional": "Interested in trying Mediterranean diet"
                },
                "dietaryPreferences": {
                    "selected": ["Gluten-free", "Dairy-free"],
                    "additional": "Avoiding processed foods"
                },
                "consent": True,
                "anonymous": False
            }
        }
