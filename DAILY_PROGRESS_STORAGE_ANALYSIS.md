# Daily Progress Storage Analysis

## Problem
Habits progress is not being stored in the database when users save their daily progress.

## Data Flow Analysis

### 1. Frontend → Backend Request

**Frontend sends** (`mobile/src/screens/DailyHabitsScreen.tsx`):
```typescript
{
  user_id: string,
  entry_date: string,  // YYYY-MM-DD format
  habits: [
    {
      habit: string,        // e.g., "Cook with your phase"
      completed: boolean,   // true/false
      notes?: string        // Optional
    }
  ],
  mood?: {
    mood: number,           // 1-5
    symptoms: string[],
    notes: string,
    date: string
  },
  cycle_phase?: string      // e.g., "follicular"
}
```

**Example request:**
```json
{
  "user_id": "abc123",
  "entry_date": "2025-11-05",
  "habits": [
    { "habit": "Cook with your phase", "completed": true },
    { "habit": "Seed rotation", "completed": true },
    { "habit": "Phase-friendly snack", "completed": true }
  ],
  "mood": {
    "mood": 3,
    "symptoms": ["Backache"],
    "notes": "",
    "date": "2025-11-05"
  },
  "cycle_phase": "follicular"
}
```

### 2. Backend Processing (`backend/api.py` `/daily-progress`)

**Backend receives:**
- `request.get('habits', [])` - Array of habit objects
- For each habit:
  - `habit.get('habit', '')` - Extracts habit name ✓
  - `habit.get('completed', False)` - Extracts completion status ✓

**Backend creates:**
1. **`user_habits` record** (if doesn't exist):
   ```python
   {
     'user_id': user_id,
     'habit_name': habit_name,  # e.g., "Cook with your phase"
     'habit_description': f"Daily habit: {habit_name}",
     'status': 'active'
   }
   ```

2. **`daily_habit_entries` record**:
   ```python
   {
     'user_id': user_id,
     'habit_id': habit_id,      # From user_habits.id
     'entry_date': entry_date,  # YYYY-MM-DD
     'completed': boolean      # From habit.get('completed', False)
   }
   ```

### 3. Expected Supabase Schema

**`daily_habit_entries` table should have:**
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to profiles)
- `habit_id` (UUID, foreign key to user_habits.id)
- `entry_date` (DATE)
- `completed` (BOOLEAN)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**`user_habits` table should have:**
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to profiles)
- `habit_name` (TEXT)
- `habit_description` (TEXT)
- `status` (TEXT) - e.g., "active"
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Potential Issues Identified

### Issue 1: Missing Error Handling (FIXED)
- **Problem**: Database insert errors were being silently ignored
- **Fix**: Added try/except blocks with detailed error logging for:
  - `user_habits` creation
  - `daily_habit_entries` creation
  - `daily_moods` creation
  - `daily_summaries` creation

### Issue 2: Indentation Issues (FIXED)
- **Problem**: Inconsistent indentation in dictionary definitions could cause parsing issues
- **Fix**: Fixed indentation in:
  - `user_habit_data` dictionary (line 775-780)
  - `daily_entry_data` dictionary (line 786-791)
  - `daily_mood_data` dictionary (line 799-807)
  - `daily_summary_data` dictionary (line 814-821)

### Issue 3: Missing Validation
- **Problem**: No validation that `habit_id` exists before creating `daily_habit_entry`
- **Fix**: Added check after `user_habit` lookup/creation to ensure it exists before proceeding

### Issue 4: Silent Failures
- **Problem**: If one habit fails to save, the loop continues but no error is reported
- **Fix**: Added error logging and continue statements to skip failed habits while logging errors

## Debugging Steps Added

The code now logs:
- ✅ Success: `"✅ Created user_habit: {habit_name} for user {user_id}"`
- ✅ Success: `"✅ Created daily_habit_entry: {entry_id} for habit '{habit_name}' (completed: {completed})"`
- ❌ Error: `"❌ ERROR creating user_habit '{habit_name}': {e}"`
- ❌ Error: `"❌ ERROR creating daily_habit_entry for '{habit_name}': {e}"`
- ⚠️ Warning: `"⚠️ No user_habit found for '{habit_name}' after lookup/creation, skipping"`

## Next Steps to Debug

1. **Check server logs** when saving daily progress to see:
   - Which habits are being processed
   - Which inserts succeed/fail
   - What error messages appear

2. **Verify Supabase table schema**:
   - Check if `daily_habit_entries` table has all required columns
   - Verify foreign key constraints are correct
   - Check RLS (Row Level Security) policies allow inserts

3. **Test with a single habit**:
   - Try saving just one habit to isolate the issue
   - Check if the problem is with specific habits or all habits

4. **Verify `user_habits` table**:
   - Check if `user_habits` records are being created successfully
   - Verify the `id` field is being returned correctly

## Field Mapping Summary

| Frontend Field | Backend Processing | Supabase Table | Supabase Field |
|---------------|-------------------|----------------|----------------|
| `habits[].habit` | `habit_name` | `user_habits` | `habit_name` |
| `habits[].completed` | `completed` | `daily_habit_entries` | `completed` |
| `user_id` | `user_id` | `user_habits`, `daily_habit_entries` | `user_id` |
| `entry_date` | `entry_date` | `daily_habit_entries` | `entry_date` |
| N/A | `habit_id` (from `user_habits.id`) | `daily_habit_entries` | `habit_id` |

## Expected Behavior

1. Frontend sends request with habits array
2. Backend loops through each habit:
   - Looks up or creates `user_habit` record
   - Gets `habit_id` from `user_habits.id`
   - Creates `daily_habit_entry` with `habit_id`, `user_id`, `entry_date`, `completed`
3. Backend creates `daily_mood` entry (if mood provided)
4. Backend creates `daily_summary` entry
5. Backend returns success with `entry_ids` array

## Current Status

✅ **Fixed:**
- Added comprehensive error logging
- Fixed indentation issues
- Added validation checks
- Improved error handling
- Added auth token setup in DailyHabitsScreen (similar to NutritionistChatScreen)

🔍 **To Verify:**
- Check server logs for actual error messages
- Verify Supabase table schema matches expectations
- Test with actual API calls to see what errors occur

## Additional Fixes Applied

### Fix 5: Auth Token Setup
- **Problem**: `DailyHabitsScreen` wasn't explicitly setting the auth token in `apiService` before making API calls
- **Fix**: Added `useEffect` to set `apiService.setAuthToken(session.access_token)` when session changes
- **Location**: `mobile/src/screens/DailyHabitsScreen.tsx` lines 321-327

## Testing Checklist

When testing, check server logs for:
1. ✅ `"✅ Created user_habit: {habit_name} for user {user_id}"` - Confirms user_habit creation
2. ✅ `"✅ Created daily_habit_entry: {entry_id} for habit '{habit_name}' (completed: {completed})"` - Confirms daily_habit_entry creation
3. ❌ Any `"❌ ERROR creating..."` messages - These will show what's failing
4. ⚠️ Any `"⚠️ No user_habit found..."` messages - Indicates lookup issues

## Common Issues to Check

1. **RLS (Row Level Security) Policies**: Supabase might be blocking inserts due to RLS policies
2. **Foreign Key Constraints**: `habit_id` must reference a valid `user_habits.id`
3. **Missing Columns**: Verify `daily_habit_entries` table has all required columns
4. **Data Type Mismatches**: Ensure `entry_date` is DATE type, `completed` is BOOLEAN
5. **Authentication**: Verify the Authorization header is being sent correctly

