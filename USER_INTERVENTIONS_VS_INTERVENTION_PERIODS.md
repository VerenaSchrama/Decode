# `user_interventions` vs `intervention_periods` Tables

## Summary
These are **two different tables for different purposes**:

1. **`user_interventions`** - Stores user-generated/custom interventions (user-created content)
2. **`intervention_periods`** - Tracks when a user starts/uses an intervention (tracking/usage data)

## `user_interventions` Table

### Purpose
Stores **user-generated/custom interventions** that users create and submit for review.

### When It Gets Used
- **Only** when user creates a custom intervention via `/interventions/submit` endpoint
- Used in RAG pipeline to search for user-generated interventions when making recommendations
- Stored in vectorstore for semantic search

### Endpoints
- `POST /interventions/submit` - Submit a new user-generated intervention
- `GET /interventions/user/{user_id}` - Get all interventions created by a user

### Schema (from code)
```python
{
    "id": uuid,
    "user_id": int,
    "name": str,
    "description": str,
    "profile_match": str,
    "scientific_source": str,
    "status": "pending" | "reviewed" | "approved" | "rejected",
    "helpful_count": int,
    "total_tries": int,
    "created_at": timestamp,
    "updated_at": timestamp
}
```

### In Normal Flow
**Nothing gets stored to `user_interventions`** in the standard intake → recommendations → start intervention flow.

## `intervention_periods` Table

### Purpose
Tracks **when a user starts using an intervention** (whether from InterventionsBASE or a custom one).

### When It Gets Used
- When user clicks "Start My Journey" after selecting an intervention
- Tracks the period/duration of intervention usage
- Links to `intake_id` that generated the recommendation

### Endpoints
- `POST /intervention-periods/start` - Start tracking a new intervention period
- `GET /intervention-periods/active` - Get currently active intervention period
- `GET /intervention-periods/history` - Get all intervention periods for user
- `PUT /intervention-periods/{period_id}/complete` - Complete an intervention period

### Schema (from code)
```python
{
    "id": uuid,
    "user_id": uuid,
    "intake_id": uuid,
    "intervention_name": str,
    "intervention_id": int | None,  # From InterventionsBASE or user_interventions
    "selected_habits": List[str],
    "start_date": timestamp,
    "end_date": timestamp,  # Planned end date
    "actual_end_date": timestamp | None,
    "planned_duration_days": int,
    "status": "active" | "completed" | "paused" | "abandoned",
    "cycle_phase": str | None,
    "notes": str | None,
    "created_at": timestamp,
    "updated_at": timestamp
}
```

### In Normal Flow
**This is where interventions get stored** when user clicks "Start My Journey".

## Key Differences

| Feature | `user_interventions` | `intervention_periods` |
|---------|---------------------|----------------------|
| **Purpose** | User-generated content | Usage tracking |
| **Created when** | User submits custom intervention | User starts using intervention |
| **Contains** | Intervention definition | Period tracking data |
| **Used in** | RAG search, custom interventions | Active intervention queries, progress tracking |
| **Status** | pending/reviewed/approved/rejected | active/completed/paused/abandoned |
| **Links to** | `intervention_habits` table | `intake_id`, `user_habits`, daily progress |

## Answer to Your Question

**In the normal intake → recommendations → start intervention flow:**
- ✅ `intakes` table - stores intake data
- ✅ `intervention_periods` table - stores when user starts intervention
- ❌ `user_interventions` table - **NOT used** (only for custom interventions)

So yes, **nothing gets stored to `user_interventions`** in the standard flow. It's only used when users create their own custom interventions.

