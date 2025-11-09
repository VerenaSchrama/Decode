# Complete Habit Data Flow Through User Journey

## Overview
This document traces how habits flow through the entire user journey, from initial intake to daily tracking and history retrieval.

---

## Phase 1: Intake & Recommendation (Initial Habit Discovery)

### 1.1 User Completes Intake
**Location**: `mobile/src/screens/StoryIntakeScreen.tsx` → `backend/api.py` `/recommend`

**Flow**:
1. User fills out intake form (symptoms, interventions, dietary preferences, cycle info)
2. Frontend sends `UserInput` to `/recommend` endpoint
3. Backend processes through RAG pipeline
4. Returns intervention recommendations with associated habits

**Data Structure**:
```typescript
// Frontend sends
{
  symptoms: {...},
  interventions: {...},
  habits: {...},  // User's previous habits (optional)
  dietaryPreferences: {...},
  lastPeriod: {...}
}

// Backend returns
{
  interventions: [
    {
      id: 1,
      name: "Control your blood sugar",
      habits: [
        "Cook with your phase",
        "Seed rotation",
        "Phase-friendly snack"
      ]
    }
  ]
}
```

**Storage**: 
- Intake data stored in `intakes` table
- Recommendation data stored in `intakes.recommendation_data` (JSONB)

---

## Phase 2: Intervention Selection & Habit Activation

### 2.1 User Selects Intervention
**Location**: `mobile/src/navigation/AppNavigator.tsx` → `backend/api.py` `/intervention-periods/start`

**Flow**:
1. User views recommended interventions
2. User selects an intervention (e.g., "Control your blood sugar")
3. User selects start date and duration
4. Frontend extracts habits from selected intervention
5. Frontend calls `/intervention-periods/start` with:
   ```typescript
   {
     intake_id: "...",
     intervention_name: "Control your blood sugar",
     selected_habits: ["Cook with your phase", "Seed rotation", "Phase-friendly snack"],
     intervention_id: 1,
     planned_duration_days: 30,
     start_date: "2025-01-15"
   }
   ```

### 2.2 Backend Creates Intervention Period
**Location**: `backend/intervention_period_service.py` → `start_intervention_period()`

**Flow**:
1. **Creates `intervention_periods` record**:
   ```python
   {
     'id': uuid,
     'user_id': user_id,
     'intake_id': intake_id,
     'intervention_name': "Control your blood sugar",
     'selected_habits': ["Cook with your phase", "Seed rotation", ...],  # Array of habit names
     'start_date': "2025-01-15",
     'status': 'active',
     'cycle_phase': 'follicular'
   }
   ```
   **Table**: `intervention_periods`
   **Key Field**: `selected_habits` (array of habit name strings)

2. **Creates `user_habits` records** (one per selected habit):
   ```python
   for habit_name in selected_habits:
       # Look up habit_id from HabitsBASE
       habit_id = habit_name_to_id[habit_name]
       
       # Check if user_habit already exists
       if not exists:
           # Create new user_habit
           {
             'user_id': user_id,
             'habit_name': "Cook with your phase",
             'habit_id': habit_id,  # From HabitsBASE.Habit_ID
             'habit_description': "Daily habit: Cook with your phase",
             'status': 'active'
           }
   ```
   **Table**: `user_habits`
   **Key Fields**: 
   - `habit_name` (string) - e.g., "Cook with your phase"
   - `habit_id` (integer) - Reference to `HabitsBASE.Habit_ID`
   - `status` - 'active', 'completed', 'paused', etc.

**Important**: 
- `intervention_periods.selected_habits` stores habit **names** (strings)
- `user_habits` stores both **name** and **ID** (for reference to HabitsBASE)
- If `user_habit` already exists, it's not recreated (prevents duplicates)

---

## Phase 3: Daily Habits Screen Load

### 3.1 Frontend Loads Active Habits
**Location**: `mobile/src/screens/DailyHabitsScreen.tsx` → `loadActiveHabits()`

**Flow**:
1. Component mounts
2. Checks `AppStateContext` for `selectedHabits` (preferred source)
3. Falls back to route params if not in context
4. Last resort: Calls `/user/{user_id}/active-habits` API

### 3.2 Backend Returns Active Habits
**Location**: `backend/api.py` `/user/{user_id}/active-habits`

**Flow**:
1. Queries `user_habits` table:
   ```python
   SELECT id, habit_name, habit_description, status, created_at
   FROM user_habits
   WHERE user_id = ? AND status = 'active'
   ORDER BY created_at ASC
   ```

2. **Fallback Logic** (if no active habits found):
   - Checks `intervention_periods` for active period with `selected_habits`
   - If found, attempts to reactivate existing `user_habits`:
     - Updates `status` to 'active' for existing habits
     - Creates missing `user_habits` from `selected_habits` array

3. Returns:
   ```json
   {
     "user_id": "...",
     "habits": [
       {
         "id": "uuid",
         "habit_name": "Cook with your phase",
         "habit_description": "Daily habit: Cook with your phase",
         "status": "active"
       }
     ],
     "count": 3
   }
   ```

**Frontend State**:
```typescript
const [habitProgress, setHabitProgress] = useState<HabitProgress[]>(
  habits.map(habit => ({ 
    habit: habit.habit_name,  // e.g., "Cook with your phase"
    completed: false 
  }))
);
```

---

## Phase 4: Daily Habit Tracking

### 4.1 User Toggles Habits
**Location**: `mobile/src/screens/DailyHabitsScreen.tsx` → `toggleHabit()`

**Flow**:
1. User taps habit card
2. `toggleHabit(habit)` updates local state:
   ```typescript
   setHabitProgress(prev => 
     prev.map(h => 
       h.habit === habit 
         ? { ...h, completed: !h.completed }
         : h
     )
   );
   ```
3. **Note**: Progress is NOT saved automatically - user must click "Save Today's Progress"

### 4.2 User Saves Daily Progress
**Location**: `mobile/src/screens/DailyHabitsScreen.tsx` → `saveProgressToAPI()`

**Frontend Request**:
```typescript
await apiService.saveDailyProgress({
  user_id: user?.id,
  entry_date: "2025-01-15",  // YYYY-MM-DD
  habits: [
    { habit: "Cook with your phase", completed: true },
    { habit: "Seed rotation", completed: true },
    { habit: "Phase-friendly snack", completed: false }
  ],
  mood: {
    mood: 3,
    symptoms: ["Backache"],
    notes: "",
    date: "2025-01-15"
  },
  cycle_phase: "follicular"
});
```

### 4.3 Backend Processes Daily Progress
**Location**: `backend/api.py` `/daily-progress`

**Step-by-Step Processing**:

#### Step 1: Verify Authentication & Check Duplicates
```python
# Verify token and get user_id
# Check if entry already exists for this date
existing = daily_summaries WHERE user_id = ? AND entry_date = ?
if exists:
    raise HTTPException(400, "Already tracked for this date")
```

#### Step 2: Process Each Habit
```python
for habit in habits:
    habit_name = habit.get('habit')  # e.g., "Cook with your phase"
    completed = habit.get('completed', False)
    
    # 1. Look up or create user_habit
    user_habit = user_habits WHERE user_id = ? AND habit_name = ?
    if not exists:
        # Create new user_habit
        user_habit = {
            'user_id': user_id,
            'habit_name': habit_name,
            'habit_description': f"Daily habit: {habit_name}",
            'status': 'active'
        }
        INSERT INTO user_habits
    
    # 2. Get habit_id from user_habit
    habit_id = user_habit.id  # UUID from user_habits table
    
    # 3. Create daily_habit_entry
    daily_entry = {
        'user_id': user_id,
        'habit_id': habit_id,  # FK to user_habits.id
        'entry_date': "2025-01-15",
        'completed': completed  # true/false
    }
    INSERT INTO daily_habit_entries
    entry_ids.append(entry_id)  # Collect IDs for mood linking
```

**Table**: `daily_habit_entries`
**Key Fields**:
- `habit_id` (UUID) - References `user_habits.id` (NOT HabitsBASE)
- `entry_date` (DATE)
- `completed` (BOOLEAN)

#### Step 3: Create Mood Entry
```python
if mood:
    daily_mood = {
        'user_id': user_id,
        'entry_date': "2025-01-15",
        'mood': 3,
        'notes': "",
        'symptoms': ["Backache"],
        'cycle_phase': "follicular",
        'habit_entry_ids': entry_ids  # Array of daily_habit_entries.id
    }
    UPSERT INTO daily_moods (on_conflict: user_id, entry_date)
```

**Table**: `daily_moods`
**Key Field**: `habit_entry_ids` (array of UUIDs) - Links to `daily_habit_entries.id`

#### Step 4: Create Daily Summary
```python
daily_summary = {
    'user_id': user_id,
    'entry_date': "2025-01-15",
    'completion_percentage': 66.67,  # 2/3 habits completed
    'cycle_phase': "follicular",
    'total_habits': 3,
    'completed_habits': 2,
    'overall_mood': 3,  # From mood data (for backward compatibility)
    'overall_notes': ""  # From mood data (for backward compatibility)
}
INSERT INTO daily_summaries
```

**Table**: `daily_summaries`
**Purpose**: Aggregated daily statistics (denormalized for quick queries)

---

## Phase 5: History & Analytics Retrieval

### 5.1 Load Daily Habits History
**Location**: `mobile/src/screens/DailyHabitsScreen.tsx` → `loadDailyHabitsHistory()`

**Frontend Request**:
```typescript
DailyProgressAPI.getDailyHabitsHistory(userId, 30)  // Last 30 days
```

**Backend**: `backend/api.py` `/user/{user_id}/daily-habits-history`

**Backend Processing**:
1. **Query `daily_summaries`**:
   ```python
   SELECT * FROM daily_summaries
   WHERE user_id = ? 
     AND entry_date >= start_date 
     AND entry_date <= end_date
   ORDER BY entry_date DESC
   ```

2. **Query `daily_habit_entries`**:
   ```python
   SELECT * FROM daily_habit_entries
   WHERE user_id = ? 
     AND entry_date >= start_date 
     AND entry_date <= end_date
   ORDER BY entry_date DESC
   ```

3. **Join with `user_habits` to get habit names**:
   ```python
   for entry in daily_habit_entries:
       habit_id = entry.habit_id
       # Look up habit_name from user_habits
       habit = user_habits WHERE id = habit_id
       habit_name = habit.habit_name
   ```

4. **Query `daily_moods`**:
   ```python
   SELECT * FROM daily_moods
   WHERE user_id = ? 
     AND entry_date >= start_date 
     AND entry_date <= end_date
   ```

5. **Combine Data**:
   ```python
   for summary in daily_summaries:
       date = summary.entry_date
       habits = daily_habit_entries[date]  # Grouped by date
       mood = daily_moods[date]
       
       history_entry = {
           'date': date,
           'habits': [
               {
                   'habit_name': "Cook with your phase",  # From user_habits
                   'completed': true  # From daily_habit_entries
               }
           ],
           'mood': mood,
           'completion_percentage': summary.completion_percentage
       }
   ```

**Frontend Display**:
- Shows history entries with habit completion status
- Displays mood and symptoms
- Shows completion percentage per day

---

## Data Relationships Summary

### Table Relationships

```
HabitsBASE (Master Habit Catalog)
    ↓ (Habit_ID)
user_habits (User's Active Habits)
    ↓ (id → habit_id)
daily_habit_entries (Daily Tracking)
    ↓ (id → habit_entry_ids[])
daily_moods (Daily Mood Data)
    ↑ (entry_date)
daily_summaries (Daily Aggregates)
```

### Key Relationships

1. **`user_habits.habit_id`** → `HabitsBASE.Habit_ID`
   - Links user's habits to master catalog
   - Used when creating `user_habits` from `selected_habits`

2. **`daily_habit_entries.habit_id`** → `user_habits.id`
   - Links daily entries to user's active habits
   - **NOT** directly to `HabitsBASE` (goes through `user_habits`)

3. **`daily_moods.habit_entry_ids`** → `daily_habit_entries.id[]`
   - Links mood entry to all habit entries for that day
   - Array of UUIDs

4. **All tables linked by**:
   - `user_id` (UUID)
   - `entry_date` (DATE) - for daily data

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: INTAKE & RECOMMENDATION                            │
└─────────────────────────────────────────────────────────────┘
User Input → /recommend → RAG Pipeline
                              ↓
                    Interventions with Habits
                              ↓
                    Stored in: intakes.recommendation_data

┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: INTERVENTION SELECTION                             │
└─────────────────────────────────────────────────────────────┘
User Selects Intervention
        ↓
/intervention-periods/start
        ↓
┌───────────────────────┐
│ intervention_periods  │  ← Stores selected_habits (array)
│ - selected_habits[]   │
│ - status: 'active'    │
└───────────────────────┘
        ↓
┌───────────────────────┐
│ user_habits           │  ← One record per habit
│ - habit_name          │
│ - habit_id (FK)       │  → HabitsBASE.Habit_ID
│ - status: 'active'    │
└───────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: DAILY HABITS SCREEN                                 │
└─────────────────────────────────────────────────────────────┘
Screen Loads
        ↓
/user/{user_id}/active-habits
        ↓
Query: user_habits WHERE status = 'active'
        ↓
Returns: [{ habit_name, habit_description, status }]
        ↓
Frontend State: habitProgress = [{ habit, completed: false }]

┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: DAILY TRACKING                                      │
└─────────────────────────────────────────────────────────────┘
User Toggles Habits (Local State Only)
        ↓
User Clicks "Save Today's Progress"
        ↓
/daily-progress POST
        ↓
For each habit:
  1. Lookup/Create user_habit (by habit_name)
  2. Get habit_id from user_habit
  3. Create daily_habit_entry
        ↓
┌───────────────────────┐
│ daily_habit_entries   │  ← One per habit per day
│ - habit_id (FK)       │  → user_habits.id
│ - entry_date          │
│ - completed           │
└───────────────────────┘
        ↓
┌───────────────────────┐
│ daily_moods           │  ← One per day
│ - habit_entry_ids[]   │  → daily_habit_entries.id[]
│ - mood, notes, etc.   │
└───────────────────────┘
        ↓
┌───────────────────────┐
│ daily_summaries       │  ← One per day
│ - completion_percent  │
│ - total_habits        │
│ - overall_mood        │  ← Denormalized from daily_moods
└───────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: HISTORY RETRIEVAL                                   │
└─────────────────────────────────────────────────────────────┘
/user/{user_id}/daily-habits-history
        ↓
Query: daily_summaries + daily_habit_entries + daily_moods
        ↓
Join: daily_habit_entries.habit_id → user_habits.id
        ↓
Get: habit_name from user_habits
        ↓
Return: Combined history with habit names and completion status
```

---

## Important Notes

### 1. Habit Name vs Habit ID
- **`intervention_periods.selected_habits`**: Stores habit **names** (strings)
- **`user_habits.habit_name`**: Stores habit **name** (string)
- **`user_habits.habit_id`**: Stores reference to `HabitsBASE.Habit_ID` (integer)
- **`daily_habit_entries.habit_id`**: Stores reference to `user_habits.id` (UUID)

### 2. Habit Lookup Chain
When displaying history:
```
daily_habit_entries.habit_id 
  → user_habits.id 
  → user_habits.habit_name
```

### 3. Duplicate Prevention
- `user_habits`: Checked before creation (by `user_id` + `habit_name`)
- `daily_habit_entries`: One entry per habit per day (enforced by checking `daily_summaries`)

### 4. Fallback Logic
- If `user_habits` missing but `intervention_periods.selected_habits` exists:
  - Backend attempts to reactivate/create `user_habits` from `selected_habits`
  - This handles edge cases where habits weren't created initially

### 5. State Management
- **Frontend**: Uses `AppStateContext` to store `selectedHabits` globally
- **Backend**: `user_habits` table is source of truth for active habits
- **Daily Progress**: Stored in `daily_habit_entries` with reference to `user_habits.id`

---

## Potential Issues & Solutions

### Issue 1: Habit Name Mismatch
**Problem**: If habit name changes in `HabitsBASE`, `user_habits.habit_name` might be stale
**Solution**: `user_habits.habit_name` is the source of truth for display (not looked up from `HabitsBASE`)

### Issue 2: Missing user_habits
**Problem**: If `user_habits` don't exist when saving daily progress
**Solution**: Code creates `user_habit` on-the-fly if it doesn't exist (line 774-787 in `api.py`)

### Issue 3: Orphaned daily_habit_entries
**Problem**: If `user_habit` is deleted, `daily_habit_entries` still reference it
**Solution**: History retrieval looks up `habit_name` from `user_habits` (line 1247-1254 in `api.py`)

---

## Summary

**Habit Journey**:
1. **Discovery**: Intake → Recommendations → Habits shown
2. **Activation**: User selects intervention → `intervention_periods` + `user_habits` created
3. **Display**: Daily Habits Screen loads → Queries `user_habits` for active habits
4. **Tracking**: User toggles habits → Saves → Creates `daily_habit_entries` + `daily_moods` + `daily_summaries`
5. **History**: User views history → Joins `daily_habit_entries` with `user_habits` to get habit names

**Key Tables**:
- `intervention_periods`: Stores which habits user selected (array of names)
- `user_habits`: Stores user's active habits (one record per habit)
- `daily_habit_entries`: Stores daily completion status (one per habit per day)
- `daily_moods`: Stores daily mood (linked to habit entries via IDs)
- `daily_summaries`: Stores daily aggregates (denormalized for quick queries)

