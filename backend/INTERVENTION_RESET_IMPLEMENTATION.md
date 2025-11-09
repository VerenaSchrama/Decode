# Intervention Reset/Change Implementation

## Overview
This document describes the backend implementation for resetting/changing a user's active intervention period when they click "Change your intervention" in the Diary screen.

## Endpoints

### 1. Get All Interventions
**Endpoint:** `GET /interventions`
**Description:** Returns all interventions from the InterventionsBASE table
**Response:**
```json
{
  "interventions": [
    {
      "id": 1,
      "name": "Eat with your cycle",
      "profile": "Clinical background...",
      "scientific_source": "...",
      "category": "...",
      ...
    }
  ]
}
```

### 2. Get Habits for Intervention
**Endpoint:** `GET /habits/{intervention_id}`
**Description:** Returns all habits associated with a specific intervention
**Response:**
```json
{
  "habits": [
    {
      "id": 1,
      "name": "Phase-friendly snack",
      "description": "...",
      "why_it_works": "...",
      "in_practice": "..."
    }
  ]
}
```

### 3. Reset Intervention Period
**Endpoint:** `POST /intervention-periods/reset`
**Description:** Resets/changes the user's active intervention period

**Request Body:**
```json
{
  "intervention_id": 1,                    // Optional: ID from InterventionsBASE
  "intervention_name": "Eat with your cycle", // Required
  "selected_habits": [                      // Required: List of habit names
    "Phase-friendly snack",
    "Cook with your phase"
  ],
  "planned_duration_days": 30,              // Optional: Default 30
  "start_date": "2024-01-15T00:00:00Z",    // Optional: ISO format, defaults to now
  "cycle_phase": "follicular",              // Optional: Will be fetched if not provided
  "intake_id": "uuid"                       // Optional: Will reuse existing if not provided
}
```

**Response:**
```json
{
  "success": true,
  "period_id": "new-period-uuid",
  "message": "Successfully changed intervention from previous to Eat with your cycle",
  "old_period_abandoned": true
}
```

## Implementation Flow

### Step 1: Mark Old Intervention as Abandoned
- Finds the current active intervention period for the user
- Updates its status to `'abandoned'`
- Sets `actual_end_date` to current timestamp
- Adds a note: "Abandoned: User changed to new intervention"

### Step 2: Deactivate Old Habits
- Finds all `user_habits` associated with the old intervention's `selected_habits`
- Updates their status to `'completed'`
- Updates `updated_at` timestamp

### Step 3: Get or Create Intake ID
- If `intake_id` is provided, uses it
- Otherwise, gets the most recent intake for the user
- If no intake exists, creates a new one

### Step 4: Create New Intervention Period
- Reuses the existing `start_intervention_period` logic
- Creates new intervention period record
- Creates new `user_habits` entries for selected habits
- Sets status to `'active'`

## Service Method

### `InterventionPeriodService.reset_intervention_period()`

**Location:** `backend/intervention_period_service.py`

**Parameters:**
- `user_id: str` - User ID
- `intervention_id: Optional[int]` - Intervention ID from InterventionsBASE
- `intervention_name: str` - Name of the new intervention
- `selected_habits: List[str]` - List of habit names to track
- `planned_duration_days: int = 30` - Duration of the intervention period
- `start_date: Optional[str] = None` - Start date (ISO format)
- `cycle_phase: Optional[str] = None` - Current cycle phase
- `intake_id: Optional[str] = None` - Intake ID (reuse existing or create new)

**Returns:**
- `Dict[str, Any]` with `success`, `period_id`, `message`, and `old_period_abandoned` fields

## Frontend Integration Flow

1. **User clicks "Change your intervention" button**
   - Navigate to intervention selection screen

2. **Load all interventions**
   - Call `GET /interventions` to get all available interventions
   - Display in scrollable list

3. **User selects an intervention**
   - Call `GET /habits/{intervention_id}` to get associated habits
   - Display habits for selection

4. **User selects habits, start date, and duration**
   - Collect user selections

5. **Submit reset request**
   - Call `POST /intervention-periods/reset` with:
     - `intervention_id`
     - `intervention_name`
     - `selected_habits`
     - `planned_duration_days`
     - `start_date` (user-selected)
   - Backend automatically:
     - Abandons old intervention
     - Deactivates old habits
     - Creates new intervention period
     - Creates new user_habits

6. **Handle response**
   - Show success message
   - Refresh intervention data
   - Navigate back to Diary screen

## Error Handling

- **401 Unauthorized:** Invalid or missing authentication token
- **400 Bad Request:** Missing required fields (`intervention_name`, `selected_habits`)
- **500 Internal Server Error:** Database errors or other server issues

All errors are logged with full traceback for debugging.

## Data Preservation

### Intervention Periods
- **All intervention periods are preserved** - never deleted, only status changes
- Old periods are marked as `'abandoned'` (not `'completed'`) to distinguish user-initiated changes
- All periods can be queried via `GET /intervention-periods/history`

### Daily Progress
- **All daily progress entries are preserved** and linked to intervention periods
- `daily_habit_entries`, `daily_summaries`, and `daily_moods` have `intervention_period_id` foreign keys
- Can query: "What progress did the user make during intervention period X?"

### Habits
- **All habits are preserved** in `user_habits` table - never deleted
- Old habits are marked as `'completed'` (status change, not deletion)
- New habits are created with status `'active'`
- Habit names for each period are stored in `intervention_periods.selected_habits` array
- Can query habits for a period via: `intervention_periods.selected_habits`

### Historical Data Access
Both users and the system can always look back at:
- ✅ All intervention periods (active, completed, abandoned) via `/intervention-periods/history`
- ✅ All daily progress entries linked to specific periods via `intervention_period_id`
- ✅ All habits ever tracked (via `user_habits` table or `intervention_periods.selected_habits`)

## Notes

- The old intervention period is marked as `'abandoned'` (not `'completed'`) to distinguish user-initiated changes from natural completions
- Old habits are marked as `'completed'` to maintain history (they are NOT deleted)
- New habits are created with status `'active'`
- Cycle phase is automatically fetched if not provided
- Intake ID is reused from the most recent intake if not provided
- **No data is ever deleted** - only status fields are updated to preserve full history

