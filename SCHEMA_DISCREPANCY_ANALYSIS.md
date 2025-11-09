# Schema Discrepancy Analysis

## Supabase Schema (From Diagram)

### `daily_habit_entries` Table
- ✅ `id` (uuid, PK)
- ✅ `user_id` (uuid, FK)
- ✅ `habit_id` (uuid)
- ✅ `entry_date` (date, FK)
- ✅ `completed` (bool)
- ✅ `created_at` (timestamptz)
- ✅ `updated_at` (timestamptz)

**Status**: ✅ **MATCHES** - Code inserts all required fields correctly

### `daily_moods` Table
- ✅ `id` (uuid, PK)
- ✅ `user_id` (uuid, FK)
- ✅ `entry_date` (date, FK)
- ✅ `mood` (int4)
- ✅ `notes` (text)
- ✅ `symptoms` (_text - array)
- ✅ `cycle_phase` (varchar)
- ✅ `habit_entry_ids` (_uuid - array)
- ✅ `created_at` (timestamp)
- ✅ `updated_at` (timestamp)

**Status**: ✅ **MATCHES** - Code inserts all required fields correctly

### `daily_summaries` Table
- ✅ `id` (uuid, PK)
- ✅ `user_id` (uuid, FK)
- ✅ `entry_date` (date, FK)
- ✅ `total_habits` (int4)
- ✅ `completed_habits` (int4)
- ✅ `completion_percentage` (float8)
- ⚠️ `overall_mood` (int4) - **STILL EXISTS IN SCHEMA BUT NOT POPULATED**
- ⚠️ `overall_notes` (text) - **STILL EXISTS IN SCHEMA BUT NOT POPULATED**
- ✅ `cycle_phase` (varchar)
- ✅ `created_at` (timestamptz)
- ✅ `updated_at` (timestamptz)

**Status**: ⚠️ **PARTIAL MATCH** - Code doesn't populate `overall_mood` and `overall_notes` (intentional, but columns still exist)

## Code vs Schema Comparison

### Current Code Behavior

**`daily_habit_entries` insert** (lines 796-801):
```python
daily_entry_data = {
    'user_id': user_id,
    'habit_id': habit_id,
    'entry_date': entry_date,
    'completed': habit.get('completed', False)
}
```
✅ **Matches schema** - All required fields present

**`daily_moods` insert** (lines 818-826):
```python
daily_mood_data = {
    'user_id': user_id,
    'entry_date': entry_date,
    'mood': mood.get('mood'),
    'notes': mood.get('notes', ''),
    'symptoms': mood.get('symptoms', []),
    'cycle_phase': cycle_phase,
    'habit_entry_ids': entry_ids
}
```
✅ **Matches schema** - All required fields present

**`daily_summaries` insert** (lines 838-845):
```python
daily_summary_data = {
    'user_id': user_id,
    'entry_date': entry_date,
    'completion_percentage': completion_percentage,
    'cycle_phase': cycle_phase,
    'total_habits': total_habits,
    'completed_habits': len(completed_habits)
    # Missing: overall_mood, overall_notes
}
```
⚠️ **Missing fields**: `overall_mood` and `overall_notes` are not populated (but they exist in schema)

## Discrepancies Found

### 1. `daily_summaries.overall_mood` and `overall_notes` Not Populated

**Schema shows**: These columns exist in `daily_summaries`
**Code does**: Does not populate these fields (intentionally, as mood is in `daily_moods`)

**Impact**: 
- ✅ **Low** - If columns are nullable, this is fine
- ⚠️ **Medium** - If columns have NOT NULL constraint, inserts will fail
- ⚠️ **Medium** - If other code expects these fields, it will get NULL

**Recommendation**: 
- If columns are nullable: Keep current behavior (mood in `daily_moods` only)
- If columns are NOT NULL: Either make them nullable OR populate from `daily_moods` table

### 2. Indentation Issues (FIXED)

**Found**: Inconsistent indentation in dictionary definitions
- Line 799: `'entry_date': entry_date,` - wrong indentation
- Line 843: `'total_habits': total_habits,` - wrong indentation

**Status**: ✅ **FIXED** - Corrected in latest changes

### 3. Potential Foreign Key Constraint Issue

**Schema shows**: `entry_date` is marked as FK in all three tables
**Issue**: Foreign keys typically reference primary keys, not date columns. This might be:
- A visualization artifact (not actual FK constraint)
- A composite unique constraint (user_id + entry_date)
- An actual FK to a dates/calendar table (unlikely)

**Impact**: 
- If it's a real FK constraint to a non-existent table, inserts will fail
- If it's just a unique constraint, it's fine

**Recommendation**: Verify in Supabase that `entry_date` is not a foreign key, or if it is, ensure the referenced table exists

## Code Issues to Fix

### Issue 1: Missing `overall_mood` and `overall_notes` in `daily_summaries`

**Current code** (line 838-845):
```python
daily_summary_data = {
    'user_id': user_id,
    'entry_date': entry_date,
    'completion_percentage': completion_percentage,
    'cycle_phase': cycle_phase,
    'total_habits': total_habits,
    'completed_habits': len(completed_habits)
}
```

**Options**:
1. **Keep as-is** (if columns are nullable) - Mood is in `daily_moods` table
2. **Populate from mood data** (if columns are NOT NULL or needed elsewhere):
   ```python
   daily_summary_data = {
       'user_id': user_id,
       'entry_date': entry_date,
       'completion_percentage': completion_percentage,
       'cycle_phase': cycle_phase,
       'total_habits': total_habits,
       'completed_habits': len(completed_habits),
       'overall_mood': mood.get('mood') if mood else None,
       'overall_notes': mood.get('notes', '') if mood else None
   }
   ```

### Issue 2: Verify `entry_date` FK Constraint

**Action**: Check Supabase**:
- Is `entry_date` actually a foreign key, or just part of a unique constraint?
- If it's a FK, what table does it reference?
- If it references a non-existent table, this will cause insert failures

## Fixes Applied

### ✅ Fix 1: Populate `overall_mood` and `overall_notes` in `daily_summaries`

**Issue**: Schema shows these columns exist, but code wasn't populating them
**Fix**: Added population from mood data for backward compatibility
**Code** (lines 847-848):
```python
'overall_mood': mood.get('mood') if mood else None,
'overall_notes': mood.get('notes', '') if mood else None
```

**Rationale**: 
- Maintains backward compatibility with existing code that might query `daily_summaries.overall_mood`
- Primary mood storage remains in `daily_moods` table (normalized)
- `daily_summaries` acts as a denormalized cache for quick queries

### ✅ Fix 2: Fixed Indentation Issues

**Issue**: Inconsistent indentation in dictionary definitions
**Fix**: Corrected indentation in:
- `daily_entry_data` (line 799)
- `daily_summary_data` (line 843)

## Remaining Considerations

1. **Verify `entry_date` FK Constraint**:
   - Schema diagram shows `entry_date` as FK, but this is unusual
   - Typically FKs reference primary keys, not date columns
   - **Action**: Verify in Supabase if this is:
     - A real FK constraint (would need referenced table)
     - A unique constraint (user_id + entry_date)
     - Just a visualization artifact

2. **Test the complete flow**:
   - With error logging in place, test saving daily progress
   - Check server logs for any remaining errors
   - Verify all three tables are populated correctly

## Summary of Schema Alignment

| Table | Code Fields | Schema Fields | Status |
|-------|------------|---------------|--------|
| `daily_habit_entries` | user_id, habit_id, entry_date, completed | ✅ All match | ✅ **ALIGNED** |
| `daily_moods` | user_id, entry_date, mood, notes, symptoms, cycle_phase, habit_entry_ids | ✅ All match | ✅ **ALIGNED** |
| `daily_summaries` | user_id, entry_date, completion_percentage, cycle_phase, total_habits, completed_habits, **overall_mood**, **overall_notes** | ✅ All match (now includes overall_mood/notes) | ✅ **ALIGNED** |

## Next Steps

1. ✅ **Fixed**: Added `overall_mood` and `overall_notes` to `daily_summaries` insert
2. ✅ **Fixed**: Fixed indentation issues
3. ✅ **Fixed**: Added comprehensive error logging
4. 🔍 **To Verify**: Test the save operation and check server logs
5. 🔍 **To Verify**: Confirm `entry_date` FK constraint (if any) doesn't cause issues

