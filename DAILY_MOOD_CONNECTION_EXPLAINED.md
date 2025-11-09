# How Daily Mood Connects to Daily Habit Entries

## Overview
The `daily_moods` table connects to `daily_habit_entries` through an **array of UUIDs** stored in the `habit_entry_ids` field. This creates a one-to-many relationship where one mood entry links to all habit entries for that day.

---

## Connection Mechanism

### Schema Structure

**`daily_moods` table**:
- `habit_entry_ids` (type: `_uuid` - array of UUIDs)
- `user_id` (UUID)
- `entry_date` (DATE)
- `mood` (int4)
- `notes` (text)
- `symptoms` (array of text)
- `cycle_phase` (varchar)

**`daily_habit_entries` table**:
- `id` (UUID, primary key)
- `user_id` (UUID)
- `habit_id` (UUID, FK to `user_habits.id`)
- `entry_date` (DATE)
- `completed` (boolean)

### Relationship
```
daily_moods.habit_entry_ids[] → daily_habit_entries.id[]
```

**One mood entry** can reference **multiple habit entries** (all habits tracked on that day).

---

## How It Works in Code

### Step 1: Create Habit Entries and Collect IDs

**Location**: `backend/api.py` `/daily-progress` endpoint (lines 760-814)

```python
# Initialize array to collect entry IDs
entry_ids = []

# Loop through each habit
for habit in habits:
    habit_name = habit.get('habit', '')
    completed = habit.get('completed', False)
    
    # 1. Lookup or create user_habit
    user_habit = lookup_or_create_user_habit(habit_name)
    habit_id = user_habit.id
    
    # 2. Create daily_habit_entry
    daily_entry_data = {
        'user_id': user_id,
        'habit_id': habit_id,
        'entry_date': entry_date,
        'completed': completed
    }
    
    # 3. Insert and collect the ID
    result = supabase_client.client.table('daily_habit_entries').insert(daily_entry_data).execute()
    entry_id = result.data[0]['id']  # Get the UUID
    entry_ids.append(entry_id)  # ⭐ Collect ID for mood linking
```

**Example**:
```python
# After processing 3 habits:
entry_ids = [
    "550e8400-e29b-41d4-a716-446655440001",  # "Cook with your phase" entry
    "550e8400-e29b-41d4-a716-446655440002",  # "Seed rotation" entry
    "550e8400-e29b-41d4-a716-446655440003"   # "Phase-friendly snack" entry
]
```

### Step 2: Create Mood Entry with Habit Entry IDs

**Location**: `backend/api.py` `/daily-progress` endpoint (lines 816-835)

```python
# Create daily mood entry (stored separately from habit entries, linked via habit_entry_ids)
if mood:
    daily_mood_data = {
        'user_id': user_id,
        'entry_date': entry_date,
        'mood': mood.get('mood'),  # e.g., 3
        'notes': mood.get('notes', ''),
        'symptoms': mood.get('symptoms', []),  # e.g., ["Backache"]
        'cycle_phase': cycle_phase,
        'habit_entry_ids': entry_ids  # ⭐ Array of daily_habit_entries.id
    }
    
    supabase_client.client.table('daily_moods').upsert(
        daily_mood_data,
        { 'on_conflict': 'user_id,entry_date' }
    ).execute()
```

**Result in Database**:
```json
{
  "id": "mood-uuid-123",
  "user_id": "user-uuid-456",
  "entry_date": "2025-01-15",
  "mood": 3,
  "notes": "",
  "symptoms": ["Backache"],
  "cycle_phase": "follicular",
  "habit_entry_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003"
  ]
}
```

---

## Why This Design?

### 1. **One Mood Per Day, Multiple Habits Per Day**
- User tracks mood **once per day** (one `daily_moods` record)
- User tracks **multiple habits per day** (multiple `daily_habit_entries` records)
- The array links the single mood to all habit entries for that day

### 2. **Temporal Relationship**
- All entries share the same `entry_date`
- `habit_entry_ids` explicitly links which habit entries the mood applies to
- Useful if habits are tracked at different times or if mood is updated separately

### 3. **Data Integrity**
- If a habit entry is deleted, the mood entry still exists (with potentially stale IDs)
- If mood is updated, the `habit_entry_ids` array can be refreshed
- The `upsert` on `user_id,entry_date` ensures one mood entry per day

---

## Retrieving the Connection

### When Loading History

**Location**: `backend/api.py` `/user/{user_id}/daily-habits-history` (lines 1261-1280)

```python
# 1. Query daily_moods
moods_result = supabase_client.client.table('daily_moods')\
    .select('*')\
    .eq('user_id', user_id)\
    .gte('entry_date', start_date)\
    .lte('entry_date', end_date)\
    .execute()

# 2. Query daily_habit_entries
habit_entries_result = supabase_client.client.table('daily_habit_entries')\
    .select('*')\
    .eq('user_id', user_id)\
    .gte('entry_date', start_date)\
    .lte('entry_date', end_date)\
    .execute()

# 3. Group by date and link via habit_entry_ids
for mood_entry in moods_result.data:
    date = mood_entry['entry_date']
    habit_entry_ids = mood_entry.get('habit_entry_ids', [])
    
    # Find matching habit entries
    matching_entries = [
        entry for entry in habit_entries_result.data
        if entry['id'] in habit_entry_ids
    ]
    
    # Combine for display
    combined_data = {
        'date': date,
        'mood': mood_entry,
        'habits': matching_entries
    }
```

### Current Implementation (Simplified)

**Note**: The current code actually groups by `entry_date` rather than using `habit_entry_ids` directly:

```python
# Current implementation groups by date (simpler, but less explicit)
moods_by_date = {}
for mood_entry in moods_result.data:
    date = mood_entry['entry_date']
    moods_by_date[date] = {
        'mood': mood_entry.get('mood'),
        'symptoms': mood_entry.get('symptoms', []),
        'notes': mood_entry.get('notes', ''),
        'date': date
    }

# Then combines with habit entries grouped by date
for summary in daily_summaries:
    date = summary['entry_date']
    habits = habits_by_date.get(date, [])  # Grouped by date
    mood = moods_by_date.get(date)  # Grouped by date
```

**Why this works**: Since all entries for the same day share the same `entry_date`, grouping by date is sufficient. However, `habit_entry_ids` provides an **explicit link** that could be used for:
- Validation (ensuring mood links to correct entries)
- Edge cases (if entries have different dates)
- Future features (linking mood to specific habits)

---

## Visual Representation

### Data Structure

```
┌─────────────────────────────────────┐
│ daily_moods                         │
├─────────────────────────────────────┤
│ id: "mood-123"                      │
│ user_id: "user-456"                 │
│ entry_date: "2025-01-15"            │
│ mood: 3                             │
│ symptoms: ["Backache"]              │
│ habit_entry_ids: [                  │  ← Array of UUIDs
│   "entry-001",                      │
│   "entry-002",                      │
│   "entry-003"                       │
│ ]                                   │
└─────────────────────────────────────┘
         │
         │ habit_entry_ids[0] → ┌──────────────────────────┐
         │ habit_entry_ids[1] → │ daily_habit_entries      │
         │ habit_entry_ids[2] → │                          │
         └─────────────────────┤ id: "entry-001"          │
                                │ habit_id: "habit-abc"    │
                                │ entry_date: "2025-01-15" │
                                │ completed: true          │
                                ├──────────────────────────┤
                                │ id: "entry-002"          │
                                │ habit_id: "habit-def"    │
                                │ entry_date: "2025-01-15" │
                                │ completed: true          │
                                ├──────────────────────────┤
                                │ id: "entry-003"          │
                                │ habit_id: "habit-ghi"    │
                                │ entry_date: "2025-01-15" │
                                │ completed: false         │
                                └──────────────────────────┘
```

### Relationship Flow

```
User saves daily progress
        ↓
Create daily_habit_entry #1 → ID: "entry-001" ┐
Create daily_habit_entry #2 → ID: "entry-002" ├─→ entry_ids = ["entry-001", "entry-002", "entry-003"]
Create daily_habit_entry #3 → ID: "entry-003" ┘
        ↓
Create daily_mood
  habit_entry_ids = ["entry-001", "entry-002", "entry-003"]
        ↓
Result: One mood entry linked to three habit entries
```

---

## Key Points

### 1. **One-to-Many Relationship**
- **One** `daily_moods` entry
- **Many** `daily_habit_entries` (referenced via array)

### 2. **Bidirectional Link**
- **Forward**: `daily_moods.habit_entry_ids[]` → `daily_habit_entries.id[]`
- **Reverse**: Can query `daily_habit_entries` WHERE `id IN (habit_entry_ids)`

### 3. **Temporal Grouping**
- All entries share the same `entry_date`
- Current code groups by date (simpler)
- `habit_entry_ids` provides explicit link (more robust)

### 4. **Upsert Behavior**
- Mood entry uses `UPSERT` with `on_conflict: user_id,entry_date`
- If user updates mood for the same day, `habit_entry_ids` array is updated
- This ensures `habit_entry_ids` always reflects current habit entries

---

## Example Query: Get Mood with All Habit Entries

```python
# Get mood entry
mood = daily_moods WHERE user_id = ? AND entry_date = ?

# Get all habit entries for that day
habit_entry_ids = mood.habit_entry_ids
habit_entries = daily_habit_entries WHERE id IN (habit_entry_ids)

# Result: Complete picture of that day
{
    'date': '2025-01-15',
    'mood': 3,
    'symptoms': ['Backache'],
    'habits': [
        {'habit_name': 'Cook with your phase', 'completed': True},
        {'habit_name': 'Seed rotation', 'completed': True},
        {'habit_name': 'Phase-friendly snack', 'completed': False}
    ]
}
```

---

## Current vs. Potential Usage

### Current Implementation
- **Groups by `entry_date`** (simpler, works because all entries share same date)
- `habit_entry_ids` is populated but not actively used for retrieval
- Still useful for data integrity and future features

### Potential Enhanced Usage
- **Use `habit_entry_ids` for explicit linking**:
  ```python
  # More explicit: filter habit entries by IDs
  matching_entries = [
      entry for entry in all_habit_entries
      if entry['id'] in mood_entry['habit_entry_ids']
  ]
  ```
- **Validation**: Ensure mood entry's `habit_entry_ids` match actual entries
- **Edge cases**: Handle cases where entries might have different dates
- **Audit trail**: Track which specific habit entries the mood applies to

---

## Summary

**Connection Type**: One-to-Many (Array of Foreign Keys)

**Field**: `daily_moods.habit_entry_ids` (array of UUIDs)

**Links To**: `daily_habit_entries.id` (one UUID per habit entry)

**Purpose**: 
- Links one mood entry to all habit entries tracked on that day
- Provides explicit relationship (not just temporal via `entry_date`)
- Enables future features like mood-to-specific-habits linking

**Current Usage**: 
- Populated when saving daily progress
- Used implicitly via date grouping in history retrieval
- Available for explicit linking if needed

