# Data Preservation and History Tracking

## Overview
This document explains how old and new interventions and habits are stored, and how both the system and users can look back at previous completed and abandoned interventions.

## Current Data Storage Structure

### 1. Intervention Periods (`intervention_periods` table)
**Status:** ✅ **FULLY PRESERVED**

All intervention periods are **never deleted**, only their status changes:
- `'active'` - Currently active intervention
- `'completed'` - Successfully completed intervention
- `'abandoned'` - User changed to a new intervention
- `'paused'` - Temporarily paused (if implemented)

**Fields preserved:**
- `id` - Unique period ID
- `user_id` - User who owns this period
- `intervention_name` - Name of the intervention
- `intervention_id` - Reference to InterventionsBASE
- `selected_habits` - Array of habit names tracked during this period
- `start_date` - When the period started
- `end_date` - Planned end date
- `actual_end_date` - When it actually ended (for completed/abandoned)
- `status` - Current status
- `cycle_phase` - Cycle phase when started
- `notes` - User/admin notes
- `created_at`, `updated_at` - Timestamps

**Querying History:**
```sql
-- Get all intervention periods for a user (all statuses)
SELECT * FROM intervention_periods 
WHERE user_id = 'user-id' 
ORDER BY start_date DESC;

-- Get only completed/abandoned periods
SELECT * FROM intervention_periods 
WHERE user_id = 'user-id' 
AND status IN ('completed', 'abandoned')
ORDER BY start_date DESC;
```

**API Endpoint:**
- `GET /intervention-periods/history` - Returns ALL periods (active, completed, abandoned)

### 2. Daily Progress Entries
**Status:** ✅ **FULLY PRESERVED AND LINKED**

All daily progress entries are preserved and linked to intervention periods:

**Tables:**
- `daily_habit_entries` - Individual habit completions
- `daily_summaries` - Daily completion summaries
- `daily_moods` - Daily mood entries

**Linking:**
- All three tables have `intervention_period_id` foreign key
- Links each entry to the specific intervention period it belongs to
- Allows querying: "What habits did the user complete during intervention period X?"

**Querying History:**
```sql
-- Get all daily progress for a specific intervention period
SELECT * FROM daily_habit_entries 
WHERE intervention_period_id = 'period-id'
ORDER BY entry_date DESC;

-- Get all daily progress for all abandoned/completed periods
SELECT dhe.*, ip.intervention_name, ip.status
FROM daily_habit_entries dhe
JOIN intervention_periods ip ON dhe.intervention_period_id = ip.id
WHERE ip.user_id = 'user-id'
AND ip.status IN ('completed', 'abandoned')
ORDER BY ip.start_date DESC, dhe.entry_date DESC;
```

### 3. User Habits (`user_habits` table)
**Status:** ⚠️ **PARTIALLY PRESERVED** (needs improvement)

**Current Implementation:**
- `user_habits` tracks which habits a user has ever tracked
- When resetting intervention, old habits are marked as `'completed'`
- New habits are created with status `'active'`

**Limitation:**
- `user_habits` table does NOT have `intervention_period_id` field
- Cannot directly query "which habits were tracked during period X"
- Must use `intervention_periods.selected_habits` array instead

**Current Query Method:**
```sql
-- Get habits for a specific intervention period
SELECT selected_habits 
FROM intervention_periods 
WHERE id = 'period-id';

-- Get all habits user has ever tracked (all periods)
SELECT DISTINCT habit_name, status, created_at, updated_at
FROM user_habits
WHERE user_id = 'user-id'
ORDER BY created_at DESC;
```

## Data Flow When Resetting Intervention

### Step 1: Mark Old Intervention as Abandoned
```sql
UPDATE intervention_periods
SET 
  status = 'abandoned',
  actual_end_date = NOW(),
  notes = 'Abandoned: User changed to new intervention'
WHERE id = 'old-period-id';
```
**Result:** Old period is preserved with status `'abandoned'`

### Step 2: Deactivate Old Habits
```sql
UPDATE user_habits
SET 
  status = 'completed',
  updated_at = NOW()
WHERE user_id = 'user-id'
AND habit_name IN ('habit1', 'habit2', ...);
```
**Result:** Old habits marked as `'completed'` but NOT deleted

### Step 3: Create New Intervention Period
```sql
INSERT INTO intervention_periods (
  id, user_id, intervention_name, selected_habits, 
  start_date, end_date, status, ...
) VALUES (...);
```
**Result:** New period created with status `'active'`

### Step 4: Create New User Habits
```sql
INSERT INTO user_habits (
  user_id, habit_name, habit_id, status, ...
) VALUES (...);
```
**Result:** New habits created with status `'active'`

## How to Query Historical Data

### For Users (Frontend)

#### 1. Get All Intervention History
```javascript
GET /intervention-periods/history
// Returns all periods: active, completed, abandoned
```

#### 2. Get Progress for Specific Period
```javascript
GET /intervention-periods/{period_id}/progress
// Returns metrics for that specific period
```

#### 3. Get Daily Progress History
```javascript
GET /user/{user_id}/daily-habits-history?start_date=...&end_date=...
// Returns daily entries with intervention_period_id
```

### For System/Backend

#### 1. Get All Periods for User
```python
periods = supabase.client.table('intervention_periods')\
    .select('*')\
    .eq('user_id', user_id)\
    .order('start_date', desc=True)\
    .execute()
```

#### 2. Get Daily Progress for Period
```python
progress = supabase.client.table('daily_habit_entries')\
    .select('*')\
    .eq('intervention_period_id', period_id)\
    .order('entry_date', desc=True)\
    .execute()
```

#### 3. Get Habits for Period
```python
period = supabase.client.table('intervention_periods')\
    .select('selected_habits')\
    .eq('id', period_id)\
    .single()\
    .execute()

habits = period.data['selected_habits']  # Array of habit names
```

## Recommended Improvements

### Option 1: Add `intervention_period_id` to `user_habits` (Recommended)
**Migration:**
```sql
ALTER TABLE user_habits
ADD COLUMN intervention_period_id UUID;

ALTER TABLE user_habits
ADD CONSTRAINT fk_user_habits_intervention_period
FOREIGN KEY (intervention_period_id) 
REFERENCES intervention_periods(id) 
ON DELETE SET NULL;

CREATE INDEX idx_user_habits_intervention_period_id 
ON user_habits(intervention_period_id);
```

**Benefits:**
- Direct query: "Get all habits for period X"
- Better data integrity
- Easier to track habit lifecycle per period

**Update Logic:**
- When creating new `user_habits`, set `intervention_period_id`
- When resetting, only deactivate habits with matching `intervention_period_id`

### Option 2: Keep Current Structure (Simpler)
**Use `intervention_periods.selected_habits` array:**
- Already contains all habit names for each period
- No schema changes needed
- Query habits via period's `selected_habits` field

## Summary

✅ **What's Preserved:**
- All intervention periods (never deleted, only status changes)
- All daily progress entries (linked via `intervention_period_id`)
- All user habits (status changes, never deleted)

✅ **What's Queryable:**
- All intervention periods via `/intervention-periods/history`
- Daily progress per period via `intervention_period_id`
- Habits per period via `intervention_periods.selected_habits`

⚠️ **Current Limitation:**
- `user_habits` doesn't have direct link to intervention periods
- Must use `intervention_periods.selected_habits` array to get habits per period

✅ **Solution:**
- Current implementation works for viewing history
- Optionally add `intervention_period_id` to `user_habits` for better querying

