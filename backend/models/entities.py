"""
Data entity models with primary keys for the health and nutrition application
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# Base entity with common fields
class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class User(BaseEntity):
    """User entity with profile information"""
    name: Optional[str] = None
    age: int = Field(..., ge=13, le=120, description="Age must be between 13 and 120")
    email: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Jane Doe",
                "age": 28,
                "email": "jane@example.com",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class Intake(BaseEntity):
    """Intake entity representing a user's health assessment"""
    user_id: str = Field(..., description="Reference to User entity")
    symptoms: List[str] = Field(default_factory=list, description="Selected symptoms")
    additional_symptoms: Optional[str] = None
    dietary_preferences: List[str] = Field(default_factory=list, description="Dietary preferences")
    additional_dietary_preferences: Optional[str] = None
    consent: bool = Field(..., description="User consent for data processing")
    date_of_birth: Optional[str] = Field(None, description="User date of birth (YYYY-MM-DD format)")
    last_period_date: Optional[str] = Field(None, description="Date of last menstrual period (YYYY-MM-DD format)")
    has_period: bool = Field(default=True, description="Whether user has menstrual periods")
    cycle_length: Optional[int] = Field(None, description="Average cycle length in days")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "symptoms": ["PCOS", "Irregular periods", "Weight gain"],
                "additional_symptoms": "Also experiencing hair loss",
                "dietary_preferences": ["Gluten-free", "Dairy-free"],
                "additional_dietary_preferences": "Avoiding processed foods",
                "consent": True,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class Intervention(BaseEntity):
    """Intervention entity from the CSV data"""
    name: str = Field(..., description="Intervention name")
    profile: str = Field(..., description="Target profile description")
    scientific_source: str = Field(..., description="Scientific reference URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "Control your blood sugar",
                "profile": "Woman with PCOS, insulin resistance, irregular cycles...",
                "scientific_source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11339140/",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class Habit(BaseEntity):
    """Habit entity representing individual habits"""
    name: str = Field(..., description="Habit name/description")
    intervention_id: str = Field(..., description="Reference to Intervention entity")
    scientific_source: str = Field(..., description="Scientific reference for this habit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc12345-e89b-12d3-a456-426614174003",
                "name": "Swap refined starches for low-GI carbs (oats, barley, legumes)",
                "intervention_id": "789e0123-e89b-12d3-a456-426614174002",
                "scientific_source": "PMC11339140",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class UserHabit(BaseEntity):
    """Junction entity for user-habit relationships with success tracking"""
    user_id: str = Field(..., description="Reference to User entity")
    habit_id: str = Field(..., description="Reference to Habit entity")
    success: bool = Field(default=False, description="Whether this habit was successful for the user")
    additional_notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "def67890-e89b-12d3-a456-426614174004",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "habit_id": "abc12345-e89b-12d3-a456-426614174003",
                "success": True,
                "additional_notes": "This habit really helped with my energy levels",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class CustomIntervention(BaseEntity):
    """Custom intervention entity for user-defined interventions"""
    user_id: str = Field(..., description="Reference to User entity")
    intake_id: str = Field(..., description="Reference to Intake entity")
    intervention_name: str = Field(..., description="Name of the custom intervention")
    description: Optional[str] = None
    context: Optional[str] = Field(None, description="Additional context from user input")
    status: str = Field(default="pending", description="Review status: pending, reviewed, approved, rejected")
    reviewed_by: Optional[str] = Field(None, description="Admin who reviewed it")
    reviewed_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, description="Admin notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ghi09876-e89b-12d3-a456-426614174005",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "intake_id": "456e7890-e89b-12d3-a456-426614174001",
                "intervention_name": "Intermittent fasting with 16:8 ratio",
                "description": "User mentioned trying 16:8 intermittent fasting",
                "context": "User said this helped with PCOS symptoms and weight management",
                "status": "pending",
                "reviewed_by": None,
                "reviewed_at": None,
                "notes": None,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }

class IntakeRecommendation(BaseEntity):
    """Recommendation entity linking intake to intervention"""
    intake_id: str = Field(..., description="Reference to Intake entity")
    intervention_id: str = Field(..., description="Reference to Intervention entity")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    reasoning: str = Field(..., description="Reasoning for this recommendation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ghi09876-e89b-12d3-a456-426614174005",
                "intake_id": "456e7890-e89b-12d3-a456-426614174001",
                "intervention_id": "789e0123-e89b-12d3-a456-426614174002",
                "similarity_score": 0.90,
                "reasoning": "Recommended based on 0.90 similarity to intervention profile...",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
