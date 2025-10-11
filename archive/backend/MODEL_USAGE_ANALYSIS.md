# 📊 Model Usage Analysis

## 🎯 **How Each Model File is Used in the Codebase**

### **1. 📝 `models/user_input.py` - API Input Validation**

**Purpose:** Defines the structured input format for the API

**Used By:**
- `api.py` - Main API endpoint validation
- `rag_pipeline.py` - Processing structured user input
- `simple_intake_service.py` - Data collection service

**Key Components:**
```python
# Main input model
UserInput = {
    profile: Profile,
    symptoms: Symptoms,
    interventions: Interventions,
    habits: Habits,
    dietaryPreferences: DietaryPreferences,
    consent: bool,
    anonymous: bool
}

# Validation options
SYMPTOM_OPTIONS = ["PCOS", "Weight gain", ...]
INTERVENTION_OPTIONS = ["Control your blood sugar", ...]
HABIT_OPTIONS = ["Swap refined starches...", ...]
```

**Usage Examples:**
```python
# In api.py
from models import UserInput

@app.post("/recommend")
async def recommend_intervention(user_input: UserInput):
    # Validates input structure automatically
    result = process_structured_user_input(user_input)

# In rag_pipeline.py
def process_structured_user_input(user_input: UserInput) -> Dict:
    # Converts structured input to text for RAG processing
    text_input = build_text_from_structured_input(user_input)
```

---

### **2. 🗄️ `models/entities.py` - Data Entity Definitions**

**Purpose:** Defines core data entities with Pydantic validation

**Used By:**
- `models/__init__.py` - Exported for use throughout app
- `models/schemas.py` - Base for API request/response schemas
- `models/supabase_models.py` - Reference for database operations

**Key Components:**
```python
# Core entities
User, Intake, Intervention, Habit, UserHabit, CustomIntervention, IntakeRecommendation

# Each entity has:
- id: str (UUID)
- created_at: datetime
- updated_at: datetime
- Field validation and examples
```

**Usage Examples:**
```python
# In models/__init__.py
from .entities import User, Intake, Intervention, Habit, UserHabit, CustomIntervention, IntakeRecommendation

# In models/schemas.py
class UserCreate(BaseModel):
    name: Optional[str] = None
    age: int
    email: Optional[str] = None
    anonymous: bool = False

# In models/supabase_models.py
class SupabaseUser(BaseModel):
    id: str
    name: Optional[str] = None
    age: int
    # ... matches User entity structure
```

---

### **3. 📋 `models/schemas.py` - API Request/Response Schemas**

**Purpose:** Defines API request and response models

**Used By:**
- `models/__init__.py` - Exported for API use
- `api.py` - Response models (though currently using custom ones)

**Key Components:**
```python
# Request schemas
UserCreate, IntakeCreate, UserHabitCreate

# Response schemas  
UserResponse, IntakeResponse, InterventionResponse, HabitResponse

# Combined schemas
UserWithIntakes, IntakeWithRecommendation, InterventionWithHabits
```

**Usage Examples:**
```python
# In models/__init__.py
from .schemas import (
    UserCreate, UserResponse, IntakeCreate, IntakeResponse, 
    InterventionResponse, HabitResponse, UserHabitCreate, UserHabitResponse,
    UserWithIntakes, IntakeWithRecommendation, InterventionWithHabits, UserWithHabits
)

# In api.py (currently using custom InterventionResponse)
class InterventionResponse(BaseModel):
    intake_summary: str
    recommended_intervention: str
    # ... custom fields
```

---

### **4. 🗃️ `models/supabase_models.py` - Database Operations**

**Purpose:** Handles all Supabase database operations

**Used By:**
- `api.py` - Admin endpoints and data collection
- `simple_intake_service.py` - User data collection
- `test_supabase.py` - Testing Supabase integration
- `migrate_to_supabase.py` - Data migration

**Key Components:**
```python
# Supabase client
class SupabaseClient:
    # User operations
    create_user(), get_user(), update_user()
    
    # Intake operations  
    create_intake(), get_user_intakes(), get_intake()
    
    # Intervention operations
    get_interventions(), get_intervention()
    
    # Habit operations
    get_habits_by_intervention(), get_all_habits()
    
    # Custom intervention operations
    create_custom_intervention(), get_pending_custom_interventions()
    
    # User-habit operations
    create_user_habit(), update_user_habit_success()

# Pydantic models for Supabase data
SupabaseUser, SupabaseIntake, SupabaseIntervention, etc.
```

**Usage Examples:**
```python
# In api.py
from models import supabase_client

@app.get("/admin/custom-interventions")
async def get_pending_custom_interventions():
    custom_interventions = supabase_client.get_pending_custom_interventions()
    return {"custom_interventions": custom_interventions.data}

# In simple_intake_service.py
from models import supabase_client, UserInput

def process_intake_with_data_collection(user_input: UserInput, user_id: str):
    # Create intake record
    intake_result = self.supabase.create_intake(intake_data)
    
    # Process custom interventions
    if user_input.interventions.additional:
        self._process_custom_interventions(user_id, intake_id, user_input.interventions.additional)
```

---

### **5. 📦 `models/__init__.py` - Central Export Hub**

**Purpose:** Centralizes all model imports and exports

**Used By:**
- All other files that need models
- Provides clean import interface

**Key Components:**
```python
# Legacy input models (for API compatibility)
from .user_input import UserInput, Profile, Symptoms, Interventions, Habits, HabitItem, DietaryPreferences
from .user_input import SYMPTOM_OPTIONS, DIETARY_PREFERENCE_OPTIONS, INTERVENTION_OPTIONS, HABIT_OPTIONS

# Pydantic entity models (for validation and serialization)
from .entities import User, Intake, Intervention, Habit, UserHabit, CustomIntervention, IntakeRecommendation

# Schema models (for API requests/responses)
from .schemas import UserCreate, UserResponse, IntakeCreate, IntakeResponse, ...

# Supabase models (for database operations)
from .supabase_models import SupabaseClient, supabase_client, ...
```

**Usage Examples:**
```python
# In api.py
from models import UserInput  # Clean import

# In simple_intake_service.py  
from models import supabase_client, UserInput  # Multiple imports

# In rag_pipeline.py
from models import UserInput  # Simple import
```

---

## 🔄 **Data Flow Through Models**

### **1. API Request Flow:**
```
User Input → user_input.py (validation) → rag_pipeline.py (processing) → api.py (response)
```

### **2. Data Collection Flow:**
```
User Input → user_input.py (validation) → simple_intake_service.py (collection) → supabase_models.py (storage)
```

### **3. Database Operations Flow:**
```
API Request → supabase_models.py (operations) → Supabase Database → Response
```

---

## 📊 **Model Usage Summary**

| Model File | Primary Use | Used By | Key Features |
|------------|-------------|---------|--------------|
| `user_input.py` | API validation | api.py, rag_pipeline.py, simple_intake_service.py | Input structure, validation options |
| `entities.py` | Data definitions | All other model files | Core entities, Pydantic validation |
| `schemas.py` | API schemas | models/__init__.py | Request/response models |
| `supabase_models.py` | Database ops | api.py, simple_intake_service.py, test_supabase.py | CRUD operations, Supabase client |
| `__init__.py` | Export hub | All files | Centralized imports |

---

## 💡 **Key Insights**

### **✅ Well-Organized:**
- Clear separation of concerns
- Each model file has a specific purpose
- Clean import structure through `__init__.py`

### **🔄 Good Data Flow:**
- Input validation → Processing → Storage
- Models support both API and database operations
- Flexible architecture for future extensions

### **📈 Usage Patterns:**
- `user_input.py` - Most used (API validation)
- `supabase_models.py` - Database operations
- `entities.py` - Foundation for all other models
- `schemas.py` - Currently underutilized (could replace custom API models)

This architecture provides a solid foundation for your health app with clear separation between input validation, data processing, and database operations! 🚀
