from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class InterventionHabit(BaseModel):
    number: int
    description: str

class UserInterventionRequest(BaseModel):
    name: str
    description: str
    profile_match: str
    scientific_source: Optional[str] = None
    habits: List[InterventionHabit]

class UserInterventionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    profile_match: str
    scientific_source: Optional[str]
    habits: List[InterventionHabit]
    status: str
    helpful_count: int
    total_tries: int
    created_at: datetime
    updated_at: datetime

class InterventionFeedbackRequest(BaseModel):
    intervention_id: str
    helpful: bool
    feedback_text: Optional[str] = None

class InterventionFeedbackResponse(BaseModel):
    id: str
    intervention_id: str
    user_id: str
    helpful: bool
    feedback_text: Optional[str]
    created_at: datetime

class InterventionApprovalRequest(BaseModel):
    status: str  # "approved" or "rejected"
    approved_by: str
