"""
Hybrid data schemas combining Pydantic models with proper entity relationships
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# Base schema with common fields
class BaseSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

# Request/Response schemas for API
class UserCreate(BaseModel):
    name: Optional[str] = None
    age: int = Field(..., ge=13, le=120)
    email: Optional[str] = None
    anonymous: bool = False

class UserResponse(BaseSchema):
    name: Optional[str] = None
    age: int
    email: Optional[str] = None
    anonymous: bool

class IntakeCreate(BaseModel):
    user_id: str
    symptoms: List[str] = []
    additional_symptoms: Optional[str] = None
    dietary_preferences: List[str] = []
    additional_dietary_preferences: Optional[str] = None
    consent: bool

class IntakeResponse(BaseSchema):
    user_id: str
    symptoms: List[str]
    additional_symptoms: Optional[str] = None
    dietary_preferences: List[str]
    additional_dietary_preferences: Optional[str] = None
    consent: bool

class InterventionResponse(BaseSchema):
    name: str
    profile: str
    scientific_source: str

class HabitResponse(BaseSchema):
    name: str
    intervention_id: str
    scientific_source: str

class UserHabitCreate(BaseModel):
    user_id: str
    habit_id: str
    success: bool = False
    additional_notes: Optional[str] = None

class UserHabitResponse(BaseSchema):
    user_id: str
    habit_id: str
    success: bool
    additional_notes: Optional[str] = None

# Complete response schemas with relationships
class UserWithIntakes(UserResponse):
    intakes: List[IntakeResponse] = []

class IntakeWithRecommendation(IntakeResponse):
    recommendation: Optional[InterventionResponse] = None

class InterventionWithHabits(InterventionResponse):
    habits: List[HabitResponse] = []

class UserWithHabits(UserResponse):
    habits: List[UserHabitResponse] = []
