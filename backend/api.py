"""
FastAPI service for HerFoodCode RAG Pipeline
Simple API that takes user input and returns intervention recommendations
"""

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Import structured input models
from models import UserInput
from auth_service import auth_service, UserRegistration, UserLogin, UserProfile
from models.user_interventions import (
    UserInterventionRequest, 
    UserInterventionResponse, 
    InterventionFeedbackRequest,
    InterventionFeedbackResponse,
    InterventionApprovalRequest
)

# Import RAG functions
from interventions.inflo_context import get_inflo_context
from rag_pipeline import process_structured_user_input
from llm import get_llm

class CustomInterventionValidationRequest(BaseModel):
    intervention: dict
    user_context: dict

class CustomInterventionValidationResponse(BaseModel):
    assessment: str
    recommendations: str
    scientific_basis: str
    safety_notes: str

load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="HerFoodCode RAG API",
    description="AI-powered intervention recommendations for women's health",
    version="2.0.0"
)

# Add CORS middleware
origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:8081",  # Expo development server
    "https://decodev1.vercel.app",  # Replace with your actual Vercel URL
    #"https://your-domain.com",  # Replace with your custom domain if you have one
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Response models
class Intervention(BaseModel):
    id: int
    name: str
    profile_match: str
    similarity_score: float
    scientific_source: str
    habits: List[dict]

class InterventionResponse(BaseModel):
    intake_summary: str
    interventions: List[Intervention]
    total_found: int
    min_similarity_used: float
    additional_inflo_context: Optional[str] = None
    data_collection: Optional[dict] = None
    cycle_phase: Optional[str] = None
    phase_info: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: str

# Chat models
class ChatMessage(BaseModel):
    id: str
    user_id: str
    message: str
    is_user: bool
    timestamp: str
    context_used: Optional[dict] = None

class ChatRequest(BaseModel):
    user_id: str
    message: str
    intake_data: Optional[dict] = None
    current_intervention: Optional[dict] = None
    selected_habits: Optional[List[str]] = None

class ChatResponse(BaseModel):
    message: str
    context_used: dict
    timestamp: str

# Import the RAG pipeline
try:
    from rag_pipeline import process_user_input, process_structured_user_input
    from interventions.matcher import InterventionMatcher
    RAG_AVAILABLE = True
    
    # Initialize singleton at startup (warm up the system)
    print("🔄 Initializing RAG pipeline...")
    matcher = InterventionMatcher()
    print("✅ RAG pipeline ready")
except Exception as e:
    print(f"Warning: RAG pipeline not available: {e}")
    RAG_AVAILABLE = False

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HerFoodCode RAG API is running",
        "status": "healthy",
        "rag_available": RAG_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "message": "HerFoodCode RAG API is running",
        "status": "healthy",
        "rag_available": RAG_AVAILABLE,
        "openai_api_key": "set" if os.getenv("OPENAI_API_KEY") else "not_set"
    }

@app.get("/user/{user_id}/insights")
async def get_user_insights(user_id: str):
    """
    Get insights about what has worked for a user
    
    This endpoint returns:
    - Total habits tried
    - Success rate
    - Personalized insights
    """
    try:
        from simple_intake_service import simple_intake_service
        insights = simple_intake_service.get_user_insights(user_id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting user insights: {str(e)}"
        )

@app.get("/user/{user_id}/habits")
async def get_user_previous_habits(user_id: str):
    """
    Get habits the user has previously tried
    
    This endpoint returns:
    - List of habits tried
    - Success status for each
    - When they were tried
    """
    try:
        from simple_intake_service import simple_intake_service
        habits = simple_intake_service.get_user_previous_habits(user_id)
        return {"user_id": user_id, "habits": habits}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting user habits: {str(e)}"
        )

@app.get("/admin/custom-interventions")
async def get_pending_custom_interventions():
    """
    Get all pending custom interventions for admin review
    
    This endpoint returns:
    - List of custom interventions awaiting review
    - User context and descriptions
    - Creation timestamps
    """
    try:
        from models import supabase_client
        custom_interventions = supabase_client.get_pending_custom_interventions()
        return {
            "total_pending": len(custom_interventions.data),
            "custom_interventions": custom_interventions.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting custom interventions: {str(e)}"
        )

@app.post("/admin/custom-interventions/{intervention_id}/review")
async def review_custom_intervention(
    intervention_id: str,
    status: str,
    reviewed_by: str,
    notes: Optional[str] = None
):
    """
    Review a custom intervention (admin only)
    
    Args:
        intervention_id: ID of the custom intervention
        status: New status (reviewed, approved, rejected)
        reviewed_by: Admin username who reviewed it
        notes: Optional admin notes
    """
    try:
        from models import supabase_client
        
        if status not in ['reviewed', 'approved', 'rejected']:
            raise HTTPException(
                status_code=400,
                detail="Status must be one of: reviewed, approved, rejected"
            )
        
        result = supabase_client.update_custom_intervention_status(
            intervention_id, status, reviewed_by, notes
        )
        
        return {
            "success": True,
            "message": f"Custom intervention {status} successfully",
            "intervention_id": intervention_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reviewing custom intervention: {str(e)}"
        )

@app.post("/recommend")
async def recommend_intervention(user_input: UserInput, authorization: str = Header(None)):
    """
    Get intervention recommendation based on structured user input
    
    Args:
        user_input: Structured user input with profile, symptoms, interventions, habits, dietary preferences
        
    Returns:
        Intervention recommendation with habits and scientific reference
    """
    if not RAG_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="RAG pipeline not available. Please check server logs."
        )
    
    # Validate that user has provided some input
    has_symptoms = user_input.symptoms.selected or user_input.symptoms.additional
    has_interventions = user_input.interventions.selected or user_input.interventions.additional
    
    if not has_symptoms and not has_interventions:
        raise HTTPException(
            status_code=400,
            detail="Please provide symptoms or intervention preferences"
        )
    
    if not user_input.consent:
        raise HTTPException(
            status_code=400,
            detail="User consent is required to process your request"
        )
    
    try:
        # Process structured user input through RAG pipeline
        result = process_structured_user_input(user_input)
        
        # Check if there's an error
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Collect user data in Supabase
        try:
            from simple_intake_service import simple_intake_service
            from auth_service import AuthService
            
            # Extract user ID from authentication token if provided
            user_id = None
            if authorization and authorization.startswith("Bearer "):
                try:
                    access_token = authorization.split(" ")[1]
                    auth_service = AuthService()
                    # Verify token and get user info
                    user_info = await auth_service.verify_token(access_token)
                    if user_info and user_info.get("user"):
                        user_id = user_info["user"]["id"]
                        print(f"✅ Authenticated user ID: {user_id}")
                    else:
                        print("⚠️  Token verification failed, using anonymous user")
                except Exception as e:
                    print(f"⚠️  Token verification error: {e}, using anonymous user")
            
            data_collection_result = simple_intake_service.process_intake_with_data_collection(
                user_input, 
                user_id=user_id,  # Use authenticated user ID or None for anonymous
                recommendation_data=result
            )
            result["data_collection"] = data_collection_result
            print("✅ Data collection completed successfully")
        except Exception as e:
            print(f"⚠️  Data collection failed: {e}")
            result["data_collection"] = {"message": "Data collection failed", "error": str(e)}
        
        # Validate required fields for new multiple-intervention format
        required_fields = ["intake_summary", "interventions"]
        
        for field in required_fields:
            if field not in result:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Missing required field: {field}"
                )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/interventions")
async def list_interventions():
    """List all available interventions"""
    try:
        from models import supabase_client
        
        # Get interventions from database
        result = supabase_client.client.table('InterventionsBASE').select('*').execute()
        
        interventions = []
        for intervention in result.data:
            interventions.append({
                "id": intervention['Intervention_ID'],
                "name": intervention['strategy_name'],
                "profile": intervention['clinical_background'],
                "scientific_source": intervention.get('show_sources', ''),
                "category": intervention.get('category_strategy', ''),
                "symptoms_match": intervention.get('symptoms_match', ''),
                "persona_fit": intervention.get('persona_fit_prior', ''),
                "dietary_fit": intervention.get('dietary_fit_prior', ''),
                "movement_amount": intervention.get('amount_of_movement_prior', '')
            })
        
        return {"interventions": interventions}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading interventions: {str(e)}"
        )

@app.get("/habits/{intervention_id}")
async def get_habits_for_intervention(intervention_id: int):
    """Get habits for specific intervention"""
    try:
        from models import supabase_client
        
        result = supabase_client.client.table('HabitsBASE')\
            .select('*')\
            .eq('connects_intervention_id', intervention_id)\
            .execute()
        
        habits = []
        for habit in result.data:
            habits.append({
                "id": habit['Habit_ID'],
                "name": habit['habit_name'],
                "description": habit['what_will_you_be_doing'],
                "why_it_works": habit['why_does_it_work'],
                "in_practice": habit['what_does_that_look_like_in_practice']
            })
        
        return {"habits": habits}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading habits: {str(e)}"
        )

@app.post("/intervention-period")
async def create_intervention_period(period_data: dict):
    """Store user's intervention period selection"""
    try:
        from models import supabase_client
        # Store intervention period data
        result = supabase_client.create_intervention_period(period_data)
        return {"success": True, "period_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/phase-habits")
async def get_phase_aware_habits(
    user_id: str,
    cycle_phase: str,
    intervention_name: str
):
    """
    Get phase-aware habits for a specific cycle phase and intervention
    
    Args:
        user_id: User ID
        cycle_phase: Current cycle phase (follicular, ovulatory, luteal, menstrual)
        intervention_name: Name of the intervention
        
    Returns:
        Phase-aware habits and context information
    """
    try:
        from interventions.inflo_phase_habits import get_phase_aware_habits, get_phase_context
        
        # Get phase-aware habits
        phase_data = get_phase_aware_habits(intervention_name, cycle_phase, [])
        
        # Get additional phase context
        phase_context = get_phase_context(cycle_phase)
        
        return {
            "user_id": user_id,
            "cycle_phase": cycle_phase,
            "intervention_name": intervention_name,
            "habits": phase_data["habits"],
            "phase_info": phase_data["phase_info"],
            "phase_context": phase_data["phase_context"],
            "cooking_methods": phase_data["cooking_methods"],
            "recommended_foods": phase_data["recommended_foods"],
            "inflo_enhanced": phase_data["inflo_enhanced"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting phase habits: {str(e)}"
        )

# Global variable to track demo user daily progress (simple in-memory approach)
demo_user_tracked_dates = set()

@app.get("/user/{user_id}/daily-progress/{date}/status")
async def get_daily_progress_status(user_id: str, date: str):
    """
    Check if user has already tracked progress for a specific date
    
    Args:
        user_id: User ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        Status indicating if the date is already tracked
    """
    try:
        from models import supabase_client
        from datetime import datetime
        
        # Map user_id to user_uuid
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            db_user_uuid = user_id
        
        # For demo users, use a simple in-memory approach
        if user_id == 'demo-user-123':
            # Check our global tracking set
            is_tracked = date in demo_user_tracked_dates
            print(f"DEBUG: Demo user status check for {date}: is_tracked={is_tracked}")
        else:
            # For authenticated users, use the normal approach
            result = supabase_client.client.table('daily_summaries')\
                .select('id, entry_date, created_at')\
                .eq('user_id', db_user_uuid)\
                .eq('entry_date', date)\
                .execute()
            
            is_tracked = len(result.data) > 0
            
            # If no daily_summaries found, check daily_habit_entries as fallback
            if not is_tracked:
                try:
                    habit_result = supabase_client.client.table('daily_habit_entries')\
                        .select('id, entry_date')\
                        .eq('user_id', db_user_uuid)\
                        .eq('entry_date', date)\
                        .execute()
                    
                    is_tracked = len(habit_result.data) > 0
                    print(f"DEBUG: Fallback check in daily_habit_entries found {len(habit_result.data)} entries")
                except Exception as e:
                    print(f"DEBUG: Fallback check failed: {e}")
        
        print(f"DEBUG: Status check for {date}: is_tracked={is_tracked}")
        
        return {
            "success": True,
            "date": date,
            "is_tracked": is_tracked,
            "can_track": not is_tracked,
            "message": "Already tracked for this date" if is_tracked else "Can track for this date"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking daily progress status: {str(e)}"
        )

@app.post("/daily-progress")
async def save_daily_progress(request: dict, authorization: str = Header(None)):
    """
    Save daily habit and mood progress
    
    Args:
        user_id: User ID (can be demo-user-123 for testing)
        entry_date: Date in YYYY-MM-DD format
        habits: Array of habit objects with completion status
        mood: Mood entry object (optional)
        cycle_phase: Current cycle phase (optional)
        
    Returns:
        Success status and entry ID
    """
    try:
        from models import supabase_client
        import uuid
        from datetime import datetime
        
        user_id = request.get('user_id', 'demo-user-123')
        entry_date = request.get('entry_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Map user_id to user_uuid for database operations
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            db_user_uuid = user_id
        
        # Check if user has already tracked progress for this date
        if user_id == 'demo-user-123':
            # For demo users, check our global tracking set
            if entry_date in demo_user_tracked_dates:
                raise HTTPException(
                    status_code=400,
                    detail=f"Daily progress already tracked for {entry_date}. Only one entry per day is allowed."
                )
        else:
            # For authenticated users, check the database
            try:
                existing_result = supabase_client.client.table('daily_summaries')\
                    .select('id, entry_date')\
                    .eq('user_id', db_user_uuid)\
                    .eq('entry_date', entry_date)\
                    .execute()
                
                if len(existing_result.data) > 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Daily progress already tracked for {entry_date}. Only one entry per day is allowed."
                    )
            except HTTPException:
                raise
            except Exception as e:
                print(f"Warning: Could not check existing entries: {e}")
                # Continue with save operation if check fails
        habits = request.get('habits', [])
        mood = request.get('mood', None)
        cycle_phase = request.get('cycle_phase', 'follicular')
        
        # Calculate completion statistics
        completed_habits = [h for h in habits if h.get('completed', False)]
        total_habits = len(habits)
        completion_percentage = (len(completed_habits) / total_habits * 100) if total_habits > 0 else 0
        
        print(f"DEBUG: Processing {total_habits} habits, {len(completed_habits)} completed")
        print(f"DEBUG: Completed habits: {[h.get('habit', 'NO_HABIT_FIELD') for h in completed_habits]}")
        
        # Prepare data for database
        entry_data = {
            'user_id': user_id,
            'entry_date': entry_date,
            'habits': habits,
            'mood': mood,
            'cycle_phase': cycle_phase,
            'completed_count': len(completed_habits),
            'total_habits': total_habits,
            'completion_percentage': completion_percentage,
            'created_at': datetime.now().isoformat()
        }
        
        # Use the db_user_uuid we already determined above
        print(f"DEBUG: Using db_user_uuid: {db_user_uuid} for user_id: {user_id}")
        
        # NEW SCHEMA: Create individual entries for each habit
        entry_ids = []
        
        # Handle habit creation differently for demo vs authenticated users
        for habit in habits:
            habit_name = habit.get('habit', '')
            if not habit_name:
                continue
            
            if user_id == 'demo-user-123':
                # For demo users, we'll use a simplified approach
                # that doesn't require the user_habits table foreign key constraint
                # We'll create a temporary habit_id for demo users
                habit_id = f"demo-{habit_name.replace(' ', '-').lower()}"
                print(f"DEBUG: Using demo habit_id: {habit_id}")
            else:
                # For authenticated users, use the normal user_habits table
                # Check if user_habit exists, if not create it
                user_habit_result = supabase_client.client.table('user_habits')\
                    .select('id')\
                    .eq('user_id', db_user_uuid)\
                    .eq('habit_name', habit_name)\
                    .execute()
                
                if not user_habit_result.data:
                    # Create new user_habit
                    user_habit_data = {
                        'user_id': db_user_uuid,
                        'habit_name': habit_name,
                        'habit_description': f"Daily habit: {habit_name}",
                        'status': 'active'
                    }
                    user_habit_result = supabase_client.client.table('user_habits').insert(user_habit_data).execute()
                
                habit_id = user_habit_result.data[0]['id']
            
            if user_id == 'demo-user-123':
                # For demo users, we'll store data in a simplified way
                # that doesn't require foreign key constraints
                # We'll just track the entry locally and return success
                entry_id = f"demo-{entry_date}-{habit_id}"
                entry_ids.append(entry_id)
                print(f"DEBUG: Demo user entry created: {entry_id}")
                
                # Add to our global tracking set
                demo_user_tracked_dates.add(entry_date)
                print(f"DEBUG: Added {entry_date} to demo user tracked dates")
                
                # Store demo user data in daily_habit_entries table for status checking
                try:
                    daily_entry_data = {
                        'user_id': db_user_uuid,
                        'habit_id': habit_id,
                        'entry_date': entry_date,
                        'completed': habit.get('completed', False),
                        'mood': mood.get('mood') if mood else None,
                        'notes': mood.get('notes', '') if mood else ''
                    }
                    entry_result = supabase_client.client.table('daily_habit_entries').insert(daily_entry_data).execute()
                    print(f"DEBUG: Demo user daily entry stored: {entry_result.data}")
                except Exception as e:
                    print(f"DEBUG: Could not store daily entry for demo user: {e}")
                    # Continue without failing the main operation
                
                # Also create a daily_summaries entry for demo users to enable status checking
                try:
                    daily_summary_data = {
                        'user_id': db_user_uuid,
                        'entry_date': entry_date,
                        'completion_percentage': completion_percentage,
                        'mood': mood.get('mood') if mood else None,
                        'notes': mood.get('notes', '') if mood else '',
                        'cycle_phase': cycle_phase,
                        'total_habits': total_habits,
                        'completed_habits': len(completed_habits)
                    }
                    summary_result = supabase_client.client.table('daily_summaries').insert(daily_summary_data).execute()
                    print(f"DEBUG: Demo user daily summary created: {summary_result.data}")
                except Exception as e:
                    print(f"DEBUG: Could not create daily summary for demo user: {e}")
                    # Continue without failing the main operation
            else:
                # For authenticated users, use the normal daily_habit_entries table
                daily_entry_data = {
                    'user_id': db_user_uuid,
                    'habit_id': habit_id,
                    'entry_date': entry_date,
                    'completed': habit.get('completed', False),
                    'mood': mood.get('mood') if mood else None,
                    'notes': mood.get('notes', '') if mood else ''
                }
                
                try:
                    # Try to insert new entry
                    result = supabase_client.client.table('daily_habit_entries').insert(daily_entry_data).execute()
                    entry_ids.append(result.data[0]['id'])
                except Exception as e:
                    if 'duplicate key value violates unique constraint' in str(e):
                        # Update existing entry
                        result = supabase_client.client.table('daily_habit_entries').update({
                            'completed': daily_entry_data['completed'],
                            'mood': daily_entry_data['mood'],
                            'notes': daily_entry_data['notes'],
                            'updated_at': datetime.now().isoformat()
                        }).eq('user_id', db_user_uuid).eq('habit_id', habit_id).eq('entry_date', entry_date).execute()
                        entry_ids.append(result.data[0]['id'] if result.data else str(uuid.uuid4()))
                    else:
                        raise e
        
        print(f"DEBUG: Created/updated {len(entry_ids)} daily habit entries")
        
        return {
            "success": True,
            "entry_id": entry_ids[0] if entry_ids else str(uuid.uuid4()),
            "completion_percentage": completion_percentage,
            "completed_habits": len(completed_habits),
            "total_habits": total_habits
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving daily progress: {str(e)}"
        )

@app.get("/user/{user_id}/daily-progress")
async def get_daily_progress(user_id: str, days: int = 7):
    """
    Get user's daily progress for the last N days
    
    Args:
        user_id: User ID
        days: Number of days to retrieve (default: 7)
        
    Returns:
        Array of daily progress entries
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        import uuid
        import hashlib
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily entries using user_id
        try:
            result = supabase_client.client.table('daily_habit_entries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            entries = result.data
        except Exception as db_error:
            # If database fails due to RLS or other issues, return empty data
            print(f"Database query failed (RLS or other issue): {db_error}")
            entries = []
        
        return {
            "success": True,
            "user_id": user_id,
            "entries": entries,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting daily progress: {str(e)}"
        )

@app.get("/user/{user_id}/daily-summaries")
async def get_daily_summaries(user_id: str, days: int = 7):
    """
    Get user's daily summaries for the last N days from daily_summaries table
    
    Args:
        user_id: User ID
        days: Number of days to retrieve (default: 7)
        
    Returns:
        Array of daily summary entries with completion percentages
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily summaries
        try:
            result = supabase_client.client.table('daily_summaries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            summaries = result.data
        except Exception as db_error:
            # If database fails due to RLS or other issues, return empty data
            print(f"Database query failed (RLS or other issue): {db_error}")
            summaries = []
        
        return {
            "success": True,
            "user_id": user_id,
            "summaries": summaries,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting daily summaries: {str(e)}"
        )

@app.get("/user/{user_id}/daily-summary/{date}")
async def get_daily_summary(user_id: str, date: str):
    """
    Get specific day's summary from daily_summaries table
    
    Args:
        user_id: User ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        Daily summary for the specific date
    """
    try:
        from models import supabase_client
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Query specific day's summary
        try:
            result = supabase_client.client.table('daily_summaries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .eq('entry_date', date)\
                .execute()
            
            if result.data:
                summary = result.data[0]
            else:
                summary = None
                
        except Exception as db_error:
            print(f"Database query failed (RLS or other issue): {db_error}")
            summary = None
        
        return {
            "success": True,
            "user_id": user_id,
            "date": date,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting daily summary: {str(e)}"
        )

@app.get("/user/{user_id}/analytics")
async def get_user_analytics(user_id: str, days: int = 30):
    """
    Get user analytics and trends from daily_summaries table
    
    Args:
        user_id: User ID
        days: Number of days to analyze (default: 30)
        
    Returns:
        Analytics data including trends, best/worst days, averages
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily summaries for analytics
        try:
            result = supabase_client.client.table('daily_summaries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            summaries = result.data
        except Exception as db_error:
            print(f"Database query failed (RLS or other issue): {db_error}")
            summaries = []
        
        # Calculate analytics
        if summaries:
            completion_percentages = [s['completion_percentage'] for s in summaries if s['completion_percentage'] is not None]
            moods = [s['overall_mood'] for s in summaries if s['overall_mood'] is not None]
            
            # Basic statistics
            avg_completion = sum(completion_percentages) / len(completion_percentages) if completion_percentages else 0
            avg_mood = sum(moods) / len(moods) if moods else 0
            
            # Best and worst days
            best_day = max(summaries, key=lambda x: x['completion_percentage']) if summaries else None
            worst_day = min(summaries, key=lambda x: x['completion_percentage']) if summaries else None
            
            # Streak calculation (consecutive days with >80% completion)
            current_streak = 0
            for summary in sorted(summaries, key=lambda x: x['entry_date'], reverse=True):
                if summary['completion_percentage'] >= 80:
                    current_streak += 1
                else:
                    break
            
            # Weekly trends (last 4 weeks)
            weekly_trends = []
            for i in range(4):
                week_start = end_date - timedelta(days=(i+1)*7-1)
                week_end = end_date - timedelta(days=i*7)
                week_summaries = [s for s in summaries if week_start <= datetime.fromisoformat(s['entry_date']).date() <= week_end]
                if week_summaries:
                    week_avg = sum(s['completion_percentage'] for s in week_summaries) / len(week_summaries)
                    weekly_trends.append({
                        'week': f"Week {4-i}",
                        'start_date': week_start.isoformat(),
                        'end_date': week_end.isoformat(),
                        'avg_completion': round(week_avg, 1),
                        'days_tracked': len(week_summaries)
                    })
            
        else:
            avg_completion = 0
            avg_mood = 0
            best_day = None
            worst_day = None
            current_streak = 0
            weekly_trends = []
        
        return {
            "success": True,
            "user_id": user_id,
            "analytics": {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_analyzed": len(summaries)
                },
                "averages": {
                    "completion_percentage": round(avg_completion, 1),
                    "mood": round(avg_mood, 1)
                },
                "streaks": {
                    "current_streak": current_streak
                },
                "best_day": {
                    "date": best_day['entry_date'] if best_day else None,
                    "completion_percentage": best_day['completion_percentage'] if best_day else None,
                    "mood": best_day['overall_mood'] if best_day else None
                },
                "worst_day": {
                    "date": worst_day['entry_date'] if worst_day else None,
                    "completion_percentage": worst_day['completion_percentage'] if worst_day else None,
                    "mood": worst_day['overall_mood'] if worst_day else None
                },
                "weekly_trends": weekly_trends
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user analytics: {str(e)}"
        )

@app.get("/user/{user_id}/daily-habits-history")
async def get_daily_habits_history(user_id: str, days: int = 30):
    """
    Get daily habits history optimized for the daily habits screen UI
    
    This endpoint joins daily_summaries with daily_habit_entries to provide
    complete historical data including individual habit completion status.
    
    Args:
        user_id: User ID
        days: Number of days to retrieve (default: 30)
        
    Returns:
        Array of daily entries with habit details, mood, and completion data
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily summaries with habit details
        try:
            # First get daily summaries
            summaries_result = supabase_client.client.table('daily_summaries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            summaries = summaries_result.data
            
            # Get individual habit entries for each day
            habit_entries_result = supabase_client.client.table('daily_habit_entries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            habit_entries = habit_entries_result.data
            
        except Exception as db_error:
            print(f"Database query failed (RLS or other issue): {db_error}")
            summaries = []
            habit_entries = []
        
        # Group habit entries by date
        habits_by_date = {}
        for entry in habit_entries:
            date = entry['entry_date']
            if date not in habits_by_date:
                habits_by_date[date] = []
            
            # Get habit name from user_habits table
            habit_name = entry.get('habit_name', 'Unknown Habit')
            if not habit_name or habit_name == 'Unknown Habit':
                # Try to get habit name from the habit_id if available
                try:
                    if entry.get('habit_id'):
                        habit_result = supabase_client.client.table('user_habits')\
                            .select('habit_name')\
                            .eq('id', entry['habit_id'])\
                            .execute()
                        if habit_result.data:
                            habit_name = habit_result.data[0]['habit_name']
                except:
                    pass
            
            habits_by_date[date].append({
                'habit_name': habit_name,
                'completed': entry.get('completed', False),
                'mood': entry.get('mood'),
                'notes': entry.get('notes', '')
            })
        
        # Combine summaries with habit details
        history_entries = []
        for summary in summaries:
            date = summary['entry_date']
            habits = habits_by_date.get(date, [])
            
            # Get mood data from the most recent habit entry with mood
            mood_data = None
            for habit in habits:
                if habit.get('mood') is not None:
                    mood_data = {
                        'mood': habit['mood'],
                        'symptoms': [],  # We don't store symptoms in individual entries
                        'notes': habit.get('notes', ''),
                        'date': date
                    }
                    break
            
            # If no mood in habit entries, use summary mood
            if not mood_data and summary.get('overall_mood'):
                mood_data = {
                    'mood': summary['overall_mood'],
                    'symptoms': [],
                    'notes': summary.get('overall_notes', ''),
                    'date': date
                }
            
            history_entry = {
                'id': summary['id'],
                'date': date,
                'total_habits': summary['total_habits'],
                'completed_habits': summary['completed_habits'],
                'completion_percentage': summary['completion_percentage'],
                'mood': mood_data,
                'habits': habits,
                'created_at': summary['created_at'],
                'updated_at': summary['updated_at']
            }
            
            history_entries.append(history_entry)
        
        return {
            "success": True,
            "user_id": user_id,
            "entries": history_entries,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "total_entries": len(history_entries)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting daily habits history: {str(e)}"
        )

@app.get("/user/{user_id}/streak")
async def get_habit_streak(user_id: str):
    """
    Get user's current habit streak
    
    Args:
        user_id: User ID
        
    Returns:
        Current streak information
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        import uuid
        import hashlib
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        # Get recent daily summaries for streak calculation
        try:
            result = supabase_client.client.table('daily_summaries')\
                .select('entry_date, completion_percentage')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', (datetime.now().date() - timedelta(days=30)).isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            summaries = result.data
        except Exception as db_error:
            # If database fails due to RLS or other issues, return 0 streak
            print(f"Database query failed (RLS or other issue): {db_error}")
            summaries = []
        
        # Calculate streak using pre-calculated completion percentages
        streak = 0
        current_date = datetime.now().date()
        
        for summary in summaries:
            entry_date = datetime.fromisoformat(summary['entry_date']).date()
            completion_pct = summary.get('completion_percentage', 0)
            
            # Check if this is today or yesterday
            if entry_date == current_date or entry_date == current_date - timedelta(days=1):
                if completion_pct >= 50:  # Consider 50%+ as a successful day
                    streak += 1
                    current_date = entry_date
                else:
                    break
            else:
                break
        
        return {
            "success": True,
            "user_id": str(user_id),
            "current_streak": streak,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting habit streak: {str(e)}"
        )

@app.post("/chat/message")
async def send_chat_message(request: ChatRequest):
    """
    Send a message to the nutritionist chat and get a RAG-based response
    
    Args:
        request: Chat request with user message and context
        
    Returns:
        AI nutritionist response with context information
    """
    try:
        if not RAG_AVAILABLE:
            raise HTTPException(status_code=503, detail="RAG pipeline not available")
        
        # Debug: Log what data we're receiving
        print(f"Chat request data: {request.intake_data}")
        print(f"Current intervention: {request.current_intervention}")
        print(f"Selected habits: {request.selected_habits}")
        
        # Calculate current cycle phase if intake data includes period info
        cycle_phase_info = None
        if request.intake_data and request.intake_data.get('lastPeriod'):
            last_period = request.intake_data['lastPeriod']
            if last_period.get('hasPeriod') and last_period.get('date') and last_period.get('cycleLength'):
                try:
                    from utils.cycle_calculator import calculate_cycle_phase
                    phase_name, days_since_period = calculate_cycle_phase(
                        last_period['date'],
                        last_period['cycleLength']
                    )
                    cycle_phase_info = {
                        'phase': phase_name,
                        'day': days_since_period,
                        'description': f"You are currently on day {days_since_period} of your cycle in the {phase_name} phase"
                    }
                    print(f"Calculated cycle phase: {cycle_phase_info}")
                except Exception as e:
                    print(f"Error calculating cycle phase: {e}")
        
        # Build user context for the chat
        user_context = build_user_context(
            request.intake_data,
            request.current_intervention,
            request.selected_habits,
            cycle_phase_info
        )
        
        print(f"Built user context: {user_context}")
        
        # Get RAG response using the existing pipeline
        from interventions.inflo_context import get_inflo_context
        inflo_context = get_inflo_context(request.message)
        
        # Create enhanced prompt with user context
        enhanced_prompt = f"""
        You are a knowledgeable nutritionist and women's health expert specializing in cycle-aware nutrition and wellness. You have access to scientific research and evidence-based practices on women's health interventions.

        USER CONTEXT:
        {user_context}

        SCIENTIFIC EVIDENCE:
        {inflo_context if inflo_context else "No specific scientific evidence found for this query."}

        USER QUESTION: {request.message}

        INSTRUCTIONS:
        - Provide a concrete, actionable answer based on the scientific evidence above
        - Give specific recommendations (foods, timing, habits) rather than general advice
        - If the user asks about symptoms, provide specific solutions and foods to try
        - If asking about nutrition, give specific meal suggestions and timing
        - If asking about cycle phases, explain what to do during their specific phase
        - Keep responses conversational but evidence-based
        - If no relevant evidence is found, ask for more specific details about their situation
        - Always end with a specific next step they can take today
        - Refer to "science" or "scientific research" instead of mentioning any specific books or sources

        Please provide a helpful, evidence-based response as a nutritionist would. Use the user's context to personalize your advice. Keep responses conversational but professional.
        """
        
        # Use LLM to generate a more conversational and actionable response
        from llm import get_llm
        llm = get_llm()
        
        
        try:
            llm_response = llm.invoke(enhanced_prompt)
            response_message = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
        except Exception as e:
            print(f"LLM error: {e}")
            # Fallback to simple response if LLM fails
            response_message = f"""Based on your profile and the scientific literature, here's my advice:

{inflo_context if inflo_context else "I'd be happy to help you with your nutrition and health questions. Could you tell me more about what specific aspect you'd like guidance on?"}

Remember, I'm here to support your health journey with evidence-based recommendations tailored to your unique needs."""

        # Store the chat message in database
        message_id = str(uuid.uuid4())
        user_timestamp = datetime.now().isoformat()
        
        # Generate a consistent UUID for the user_id (hash-based for demo purposes)
        import hashlib
        user_uuid = str(uuid.UUID(hashlib.md5(request.user_id.encode()).hexdigest()[:32]))
        
        # Store user message
        user_message = {
            "id": message_id,
            "user_id": user_uuid,
            "message": request.message,
            "is_user": True,
            "timestamp": user_timestamp,
            "context_used": user_context
        }
        
        # Store AI response (with slightly later timestamp to ensure correct order)
        ai_message_id = str(uuid.uuid4())
        ai_timestamp = datetime.now().isoformat()
        ai_message = {
            "id": ai_message_id,
            "user_id": user_uuid,
            "message": response_message,
            "is_user": False,
            "timestamp": ai_timestamp,
            "context_used": {"inflo_context": inflo_context}
        }
        
        # Store messages in Supabase
        try:
            from models import supabase_client
            result = supabase_client.client.table('chat_messages').insert([user_message, ai_message]).execute()
            print(f"Successfully stored chat messages: {len(result.data)} messages")
        except Exception as e:
            print(f"Warning: Could not store chat messages: {e}")
            print(f"User message: {user_message}")
            print(f"AI message: {ai_message}")
            # Continue without storing if table doesn't exist
        
        return ChatResponse(
            message=response_message,
            context_used={"user_context": user_context, "inflo_context": inflo_context},
            timestamp=ai_timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Get chat history for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages
    """
    try:
        from models import supabase_client
        # Generate the same UUID for the user_id
        import hashlib
        user_uuid = str(uuid.UUID(hashlib.md5(user_id.encode()).hexdigest()[:32]))
        print(f"Looking for chat history for user_id: {user_id}, UUID: {user_uuid}")
        
        result = supabase_client.client.table('chat_messages')\
            .select('*')\
            .eq('user_id', user_uuid)\
            .order('timestamp', desc=False)\
            .limit(limit)\
            .execute()
        
        print(f"Found {len(result.data)} messages for user {user_id}")
        return {"messages": result.data}
    except Exception as e:
        # Return empty history if table doesn't exist
        print(f"Warning: Could not retrieve chat history: {e}")
        return {"messages": []}

def build_user_context(intake_data: Optional[dict], current_intervention: Optional[dict], selected_habits: Optional[List[str]], cycle_phase_info: Optional[dict] = None) -> str:
    """Build user context string for chat personalization"""
    context_parts = []
    
    if intake_data:
        context_parts.append("INTAKE PROFILE:")
        
        # Handle direct fields (flat structure)
        if intake_data.get('name'):
            context_parts.append(f"- Name: {intake_data['name']}")
        if intake_data.get('age'):
            context_parts.append(f"- Age: {intake_data['age']}")
        
        # Handle nested profile structure
        if intake_data.get('profile'):
            profile = intake_data['profile']
            if profile.get('name'):
                context_parts.append(f"- Name: {profile['name']}")
            if profile.get('age'):
                context_parts.append(f"- Age: {profile['age']}")
        
        # Handle symptoms (could be array or nested)
        symptoms = intake_data.get('symptoms')
        if symptoms:
            if isinstance(symptoms, list):
                context_parts.append(f"- Symptoms: {', '.join(symptoms)}")
            elif isinstance(symptoms, dict) and symptoms.get('selected'):
                context_parts.append(f"- Symptoms: {', '.join(symptoms['selected'])}")
        
        # Handle interventions (could be array or nested)
        interventions = intake_data.get('interventions')
        if interventions:
            if isinstance(interventions, list):
                context_parts.append(f"- Previous interventions: {', '.join(interventions)}")
            elif isinstance(interventions, dict) and interventions.get('selected'):
                intervention_list = [item.get('intervention', item) if isinstance(item, dict) else item for item in interventions['selected']]
                context_parts.append(f"- Previous interventions: {', '.join(intervention_list)}")
        
        # Handle dietary preferences (could be array or nested)
        dietary_prefs = intake_data.get('dietaryPreferences')
        if dietary_prefs:
            if isinstance(dietary_prefs, list):
                context_parts.append(f"- Dietary preferences: {', '.join(dietary_prefs)}")
            elif isinstance(dietary_prefs, dict) and dietary_prefs.get('selected'):
                context_parts.append(f"- Dietary preferences: {', '.join(dietary_prefs['selected'])}")
        
        # Handle last period info
        last_period = intake_data.get('lastPeriod')
        if last_period:
            if isinstance(last_period, dict):
                if last_period.get('hasPeriod'):
                    context_parts.append(f"- Has menstrual cycle: Yes")
                    if last_period.get('cycleLength'):
                        context_parts.append(f"- Cycle length: {last_period['cycleLength']} days")
                    if last_period.get('date') or last_period.get('lastPeriodDate'):
                        date = last_period.get('date') or last_period.get('lastPeriodDate')
                        context_parts.append(f"- Last period: {date}")
                else:
                    context_parts.append(f"- Has menstrual cycle: No")
        
        # Add current cycle phase if calculated
        if cycle_phase_info:
            context_parts.append(f"- Current cycle phase: {cycle_phase_info.get('phase', 'Unknown')}")
            if cycle_phase_info.get('day'):
                context_parts.append(f"- Day in cycle: {cycle_phase_info['day']}")
            if cycle_phase_info.get('description'):
                context_parts.append(f"- Phase description: {cycle_phase_info['description']}")
    
    if current_intervention:
        if isinstance(current_intervention, dict):
            context_parts.append(f"\nCURRENT INTERVENTION: {current_intervention.get('name', 'Unknown')}")
            if current_intervention.get('habits'):
                habits = [habit.get('description', habit) if isinstance(habit, dict) else habit for habit in current_intervention['habits']]
                context_parts.append(f"- Intervention habits: {', '.join(habits[:3])}...")
        else:
            context_parts.append(f"\nCURRENT INTERVENTION: {current_intervention}")
    
    if selected_habits:
        context_parts.append(f"\nSELECTED HABITS: {', '.join(selected_habits)}")
    
    return "\n".join(context_parts) if context_parts else "No specific user context available."

# ============================================================================
# INTERVENTION PERIOD TRACKING ENDPOINTS
# ============================================================================

@app.post("/intervention-periods/start")
async def start_intervention_period(
    request: dict,
    authorization: str = Header(None)
):
    """Start tracking a new intervention period"""
    try:
        from intervention_period_service import intervention_period_service
        from auth_service import AuthService
        
        # Extract user ID from authentication token
        user_uuid = None
        if authorization and authorization.startswith("Bearer "):
            try:
                access_token = authorization.split(" ")[1]
                auth_service = AuthService()
                user_info = await auth_service.verify_token(access_token)
                if user_info and user_info.get("user"):
                    user_uuid = user_info["user"]["id"]
                    print(f"✅ Starting intervention for authenticated user: {user_uuid}")
                else:
                    print("⚠️ Token verification failed")
                    raise HTTPException(status_code=401, detail="Invalid authentication token")
            except Exception as e:
                print(f"❌ Token verification error: {e}")
                raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            raise HTTPException(status_code=401, detail="Authentication token required")
        
        # Extract data from request
        intake_id = request.get("intake_id")
        intervention_name = request.get("intervention_name")
        selected_habits = request.get("selected_habits", [])
        intervention_id = request.get("intervention_id")
        planned_duration_days = request.get("planned_duration_days", 30)
        cycle_phase = request.get("cycle_phase")
        
        if not intake_id or not intervention_name:
            raise HTTPException(status_code=400, detail="intake_id and intervention_name are required")
        
        # Start intervention period
        result = intervention_period_service.start_intervention_period(
            user_uuid=user_uuid,
            intake_id=intake_id,
            intervention_name=intervention_name,
            selected_habits=selected_habits,
            intervention_id=intervention_id,
            planned_duration_days=planned_duration_days,
            cycle_phase=cycle_phase
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to start intervention period"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error starting intervention period: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/intervention-periods/active")
async def get_active_intervention_period(authorization: str = Header(None)):
    """Get the currently active intervention period for the user"""
    try:
        from intervention_period_service import intervention_period_service
        from auth_service import AuthService
        
        # Extract user ID from authentication token
        user_uuid = None
        if authorization and authorization.startswith("Bearer "):
            try:
                access_token = authorization.split(" ")[1]
                auth_service = AuthService()
                user_info = await auth_service.verify_token(access_token)
                if user_info and user_info.get("user"):
                    user_uuid = user_info["user"]["id"]
                else:
                    raise HTTPException(status_code=401, detail="Invalid authentication token")
            except Exception as e:
                raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            raise HTTPException(status_code=401, detail="Authentication token required")
        
        # Get active intervention period
        result = intervention_period_service.get_active_intervention_period(user_uuid)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get active intervention"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting active intervention: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/intervention-periods/history")
async def get_intervention_periods_history(authorization: str = Header(None)):
    """Get all intervention periods for the user"""
    try:
        from intervention_period_service import intervention_period_service
        from auth_service import AuthService
        
        # Extract user ID from authentication token
        user_uuid = None
        if authorization and authorization.startswith("Bearer "):
            try:
                access_token = authorization.split(" ")[1]
                auth_service = AuthService()
                user_info = await auth_service.verify_token(access_token)
                if user_info and user_info.get("user"):
                    user_uuid = user_info["user"]["id"]
                else:
                    raise HTTPException(status_code=401, detail="Invalid authentication token")
            except Exception as e:
                raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            raise HTTPException(status_code=401, detail="Authentication token required")
        
        # Get intervention periods history
        result = intervention_period_service.get_user_intervention_periods(user_uuid)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get intervention history"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting intervention history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/intervention-periods/{period_id}/complete")
async def complete_intervention_period(
    period_id: str,
    request: dict,
    authorization: str = Header(None)
):
    """Mark an intervention period as completed"""
    try:
        from intervention_period_service import intervention_period_service
        
        # Extract completion data
        completion_percentage = request.get("completion_percentage", 100.0)
        notes = request.get("notes")
        
        # Complete intervention period
        result = intervention_period_service.complete_intervention_period(
            period_id=period_id,
            completion_percentage=completion_percentage,
            notes=notes
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to complete intervention"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error completing intervention: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# USER INTERVENTION ENDPOINTS
# ============================================================================

@app.post("/interventions/submit", response_model=UserInterventionResponse)
async def submit_user_intervention(
    intervention: UserInterventionRequest,
    user_id: int = 1
):
    """Submit a new user-generated intervention for review"""
    try:
        from models import supabase_client
        # Generate intervention ID
        intervention_id = str(uuid.uuid4())
        
        # Prepare intervention data
        intervention_data = {
            "id": intervention_id,
            "user_id": user_id,
            "name": intervention.name,
            "description": intervention.description,
            "profile_match": intervention.profile_match,
            "scientific_source": intervention.scientific_source,
            "status": "pending",
            "helpful_count": 0,
            "total_tries": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store intervention in Supabase
        result = supabase_client.client.table('user_interventions').insert(intervention_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store intervention")
        
        # Store habits
        habits_data = []
        for habit in intervention.habits:
            habit_data = {
                "intervention_id": intervention_id,
                "number": habit.number,
                "description": habit.description
            }
            habits_data.append(habit_data)
        
        if habits_data:
            habits_result = supabase_client.client.table('intervention_habits').insert(habits_data).execute()
            if not habits_result.data:
                print(f"Warning: Failed to store habits for intervention {intervention_id}")
        
        # Add to ChromaDB vectorstore for immediate search
        try:
            from retrievers.vectorstores import get_user_interventions_vectorstore
            vectorstore = get_user_interventions_vectorstore()
            
            # Create document for vectorstore
            doc_content = f"{intervention.name}: {intervention.profile_match}"
            doc_metadata = {
                "intervention_id": intervention_id,
                "name": intervention.name,
                "user_id": user_id,
                "status": "pending",
                "type": "user_generated"
            }
            
            vectorstore.add_documents([{
                "content": doc_content,
                "metadata": doc_metadata
            }])
            
            print(f"✅ Added user intervention to vectorstore: {intervention.name}")
        except Exception as e:
            print(f"⚠️ Failed to add to vectorstore: {e}")
        
        # Return response
        response_data = intervention_data.copy()
        response_data["user_id"] = str(user_id)  # Convert to string for response
        response_data["habits"] = [{"number": h.number, "description": h.description} for h in intervention.habits]
        
        return UserInterventionResponse(**response_data)
        
    except Exception as e:
        print(f"Error submitting intervention: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit intervention: {str(e)}")

@app.get("/interventions/user/{user_id}", response_model=List[UserInterventionResponse])
async def get_user_interventions(user_id: str):
    """Get all interventions created by a specific user"""
    try:
        from models import supabase_client
        result = supabase_client.client.table('user_interventions')\
            .select('*, intervention_habits(*)')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        
        if not result.data:
            return []
        
        interventions = []
        for item in result.data:
            # Format habits
            habits = []
            if item.get('intervention_habits'):
                for habit in item['intervention_habits']:
                    habits.append({
                        "number": habit['number'],
                        "description": habit['description']
                    })
            
            intervention_data = {
                "id": item['id'],
                "user_id": item['user_id'],
                "name": item['name'],
                "description": item['description'],
                "profile_match": item['profile_match'],
                "scientific_source": item['scientific_source'],
                "status": item['status'],
                "helpful_count": item['helpful_count'],
                "total_tries": item['total_tries'],
                "created_at": item['created_at'],
                "updated_at": item['updated_at'],
                "habits": habits
            }
            interventions.append(UserInterventionResponse(**intervention_data))
        
        return interventions
        
    except Exception as e:
        print(f"Error getting user interventions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user interventions: {str(e)}")

@app.get("/user/{user_id}/session-data")
async def get_user_session_data(user_id: str):
    """
    Get complete user session data for app restoration
    
    This endpoint retrieves all necessary data to restore a user's session:
    - Latest intake data
    - Current intervention period
    - Selected habits
    - Daily progress history
    
    Args:
        user_id: User ID
        
    Returns:
        Complete session data for frontend restoration
    """
    try:
        from models import supabase_client
        from datetime import datetime, timedelta
        
        # Map user_id to user_uuid (after migration)
        demo_user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'  # Demo user UUID
        
        if user_id == 'demo-user-123':
            db_user_uuid = demo_user_uuid
        else:
            # For authenticated users, use their actual UUID
            # Real users send their actual UUID as user_id
            db_user_uuid = user_id
        
        session_data = {
            "user_id": user_id,
            "intake_data": None,
            "current_intervention": None,
            "selected_habits": [],
            "daily_progress": [],
            "intervention_periods": []
        }
        
        # 1. Get latest intake data
        try:
            intake_result = supabase_client.client.table('intakes')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if intake_result.data:
                intake = intake_result.data[0]
                session_data["intake_data"] = {
                    "id": intake['id'],
                    "profile": intake['intake_data'].get('profile', {}),
                    "lastPeriod": intake['intake_data'].get('last_period', {}),
                    "symptoms": intake['intake_data'].get('symptoms', {}),
                    "interventions": intake['intake_data'].get('interventions', {}),
                    "habits": intake['intake_data'].get('habits', {}),
                    "dietaryPreferences": intake['intake_data'].get('dietary_preferences', {}),
                    "created_at": intake['created_at']
                }
        except Exception as e:
            print(f"Error getting intake data: {e}")
        
        # 2. Get current intervention period
        try:
            period_result = supabase_client.client.table('intervention_periods')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .eq('status', 'active')\
                .order('start_date', desc=True)\
                .limit(1)\
                .execute()
            
            if period_result.data:
                period = period_result.data[0]
                session_data["current_intervention"] = {
                    "id": period['intervention_id'],
                    "name": period['intervention_name'],
                    "start_date": period['start_date'],
                    "planned_end_date": period['planned_end_date'],
                    "cycle_phase_at_start": period['cycle_phase_at_start'],
                    "completion_percentage": period['completion_percentage']
                }
                session_data["selected_habits"] = period.get('selected_habits', [])
        except Exception as e:
            print(f"Error getting intervention period: {e}")
        
        # 3. Get recent daily progress (last 7 days)
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            progress_result = supabase_client.client.table('daily_habit_entries')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .gte('entry_date', start_date.isoformat())\
                .lte('entry_date', end_date.isoformat())\
                .order('entry_date', desc=True)\
                .execute()
            
            session_data["daily_progress"] = progress_result.data or []
        except Exception as e:
            print(f"Error getting daily progress: {e}")
        
        # 4. Get all intervention periods for history
        try:
            periods_result = supabase_client.client.table('intervention_periods')\
                .select('*')\
                .eq('user_id', db_user_uuid)\
                .order('start_date', desc=True)\
                .execute()
            
            session_data["intervention_periods"] = periods_result.data or []
        except Exception as e:
            print(f"Error getting intervention periods: {e}")
        
        return {
            "success": True,
            "session_data": session_data
        }
        
    except Exception as e:
        print(f"Error getting user session data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user session data: {str(e)}"
        )

@app.get("/interventions/approved", response_model=List[UserInterventionResponse])
async def get_approved_interventions():
    """Get all approved user-generated interventions"""
    try:
        from models import supabase_client
        result = supabase_client.client.table('user_interventions')\
            .select('*, intervention_habits(*)')\
            .eq('status', 'approved')\
            .order('helpful_count', desc=True)\
            .execute()
        
        if not result.data:
            return []
        
        interventions = []
        for item in result.data:
            # Format habits
            habits = []
            if item.get('intervention_habits'):
                for habit in item['intervention_habits']:
                    habits.append({
                        "number": habit['number'],
                        "description": habit['description']
                    })
            
            intervention_data = {
                "id": item['id'],
                "user_id": item['user_id'],
                "name": item['name'],
                "description": item['description'],
                "profile_match": item['profile_match'],
                "scientific_source": item['scientific_source'],
                "status": item['status'],
                "helpful_count": item['helpful_count'],
                "total_tries": item['total_tries'],
                "created_at": item['created_at'],
                "updated_at": item['updated_at'],
                "habits": habits
            }
            interventions.append(UserInterventionResponse(**intervention_data))
        
        return interventions
        
    except Exception as e:
        print(f"Error getting approved interventions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get approved interventions: {str(e)}")

@app.post("/interventions/{intervention_id}/feedback", response_model=InterventionFeedbackResponse)
async def submit_intervention_feedback(
    intervention_id: str,
    feedback: InterventionFeedbackRequest,
    user_id: str = "demo-user"
):
    """Submit feedback for a user-generated intervention"""
    try:
        from models import supabase_client
        feedback_data = {
            "id": str(uuid.uuid4()),
            "intervention_id": intervention_id,
            "user_id": user_id,
            "helpful": feedback.helpful,
            "feedback_text": feedback.feedback_text,
            "created_at": datetime.now().isoformat()
        }
        
        # Store feedback
        result = supabase_client.client.table('intervention_feedback').insert(feedback_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store feedback")
        
        # Update intervention statistics
        update_data = {}
        if feedback.helpful:
            update_data["helpful_count"] = "helpful_count + 1"
        update_data["total_tries"] = "total_tries + 1"
        update_data["updated_at"] = datetime.now().isoformat()
        
        supabase_client.client.table('user_interventions')\
            .update(update_data)\
            .eq('id', intervention_id)\
            .execute()
        
        return InterventionFeedbackResponse(**feedback_data)
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.post("/interventions/{intervention_id}/approve")
async def approve_intervention(
    intervention_id: str,
    approval: InterventionApprovalRequest
):
    """Approve or reject a user-generated intervention (admin only)"""
    try:
        from models import supabase_client
        update_data = {
            "status": approval.status,
            "approved_by": approval.approved_by,
            "approved_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase_client.client.table('user_interventions')\
            .update(update_data)\
            .eq('id', intervention_id)\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Intervention not found")
        
        # If approved, ensure it's in the vectorstore
        if approval.status == "approved":
            try:
                from retrievers.vectorstores import get_user_interventions_vectorstore
                vectorstore = get_user_interventions_vectorstore()
                
                # Get intervention details
                intervention_result = supabase_client.client.table('user_interventions')\
                    .select('*')\
                    .eq('id', intervention_id)\
                    .execute()
                
                if intervention_result.data:
                    intervention = intervention_result.data[0]
                    doc_content = f"{intervention['name']}: {intervention['profile_match']}"
                    doc_metadata = {
                        "intervention_id": intervention_id,
                        "name": intervention['name'],
                        "user_id": intervention['user_id'],
                        "status": "approved",
                        "type": "user_generated"
                    }
                    
                    vectorstore.add_documents([{
                        "content": doc_content,
                        "metadata": doc_metadata
                    }])
                    
                    print(f"✅ Added approved intervention to vectorstore: {intervention['name']}")
            except Exception as e:
                print(f"⚠️ Failed to add approved intervention to vectorstore: {e}")
        
        return {"message": f"Intervention {approval.status} successfully"}
        
    except Exception as e:
        print(f"Error approving intervention: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve intervention: {str(e)}")

@app.post("/interventions/validate-custom", response_model=CustomInterventionValidationResponse)
async def validate_custom_intervention(request: CustomInterventionValidationRequest):
    """Validate a custom intervention using RAG pipeline"""
    try:
        # Build user context for RAG
        user_context = build_user_context(request.user_context, None, [])
        
        # Create intervention description for RAG
        intervention_desc = f"""
        Custom Intervention: {request.intervention['name']}
        Description: {request.intervention['description']}
        Habits: {', '.join(request.intervention['habits'])}
        Duration: {request.intervention['trial_period_days']} days
        Start Date: {request.intervention['start_date']}
        """
        
        # Get relevant scientific context
        inflo_context = get_inflo_context(intervention_desc)
        
        # Create RAG prompt for validation
        validation_prompt = f"""
        You are a women's health nutrition expert. Analyze this custom intervention proposal and provide scientific validation.

        USER CONTEXT:
        {user_context}

        INTERVENTION PROPOSAL:
        {intervention_desc}

        SCIENTIFIC CONTEXT:
        {inflo_context}

        Please provide:
        1. Scientific assessment of the intervention's potential effectiveness
        2. Specific recommendations for improvement
        3. Scientific basis for your assessment
        4. Any safety considerations

        Focus on evidence-based nutrition science and women's health research.
        """
        
        # Get LLM response
        llm = get_llm()
        response = llm.invoke(validation_prompt)
        
        # Parse response (simplified - in production, you'd want more sophisticated parsing)
        assessment = response.content if hasattr(response, 'content') else str(response)
        
        # Extract key components (simplified parsing)
        recommendations = "Consider consulting with a healthcare provider before starting this intervention."
        scientific_basis = "Based on current research in women's health and nutrition science."
        safety_notes = "Monitor your body's response and adjust as needed."
        
        return CustomInterventionValidationResponse(
            assessment=assessment,
            recommendations=recommendations,
            scientific_basis=scientific_basis,
            safety_notes=safety_notes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating intervention: {str(e)}")

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register")
async def register_user(user_data: UserRegistration):
    """
    Register a new user with email and password
    
    Args:
        user_data: User registration data (email, password, name, etc.)
        
    Returns:
        User data and session information
    """
    return await auth_service.register_user(user_data)

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    """
    Login user with email and password
    
    Args:
        login_data: User login credentials
        
    Returns:
        User data and session information
    """
    return await auth_service.login_user(login_data)

@app.post("/auth/logout")
async def logout_user(access_token: str):
    """
    Logout user and invalidate session
    
    Args:
        access_token: User's access token
        
    Returns:
        Logout confirmation
    """
    return await auth_service.logout_user(access_token)

@app.get("/auth/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user profile by ID
    
    Args:
        user_id: User's UUID
        
    Returns:
        User profile data
    """
    return await auth_service.get_user_profile(user_id)

@app.put("/auth/profile/{user_id}")
async def update_user_profile(user_id: str, profile_data: UserProfile):
    """
    Update user profile
    
    Args:
        user_id: User's UUID
        profile_data: Updated profile data
        
    Returns:
        Updated profile data
    """
    return await auth_service.update_user_profile(user_id, profile_data)

@app.post("/auth/resend-confirmation")
async def resend_confirmation_email(email: str):
    """
    Resend email confirmation for a user
    
    Args:
        email: User's email address
        
    Returns:
        Confirmation email status
    """
    return await auth_service.resend_confirmation_email(email)

@app.post("/auth/verify")
async def verify_token(authorization: str = Header(None)):
    """
    Verify user's access token
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Token verification result
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    access_token = authorization.split(" ")[1]
    return await auth_service.verify_token(access_token)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
