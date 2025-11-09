# What Type is `daily_moods.habit_entry_ids`?

## PostgreSQL Data Type

**Type**: `_uuid` (PostgreSQL array of UUIDs)

In PostgreSQL:
- `uuid` = single UUID value
- `_uuid` = array of UUIDs (the `_` prefix indicates array type)

**Schema Definition**:
```sql
habit_entry_ids _uuid  -- Array of UUIDs
```

---

## In Python Code

**Type**: `list[str]` (Python list of UUID strings)

**How it's created**:
```python
# Initialize as Python list
entry_ids = []  # Type: list[str]

# Append UUID strings as habit entries are created
for habit in habits:
    result = supabase_client.client.table('daily_habit_entries').insert(...).execute()
    entry_id = result.data[0]['id']  # UUID string from database
    entry_ids.append(entry_id)  # Add to list

# Example result:
entry_ids = [
    "550e8400-e29b-41d4-a716-446655440001",  # str
    "550e8400-e29b-41d4-a716-446655440002",  # str
    "550e8400-e29b-41d4-a716-446655440003"   # str
]
```

**How it's used**:
```python
daily_mood_data = {
    'habit_entry_ids': entry_ids  # Python list → automatically converted to PostgreSQL array
}
```

**Supabase Client Conversion**:
- The Supabase Python client automatically converts Python `list` to PostgreSQL `_uuid` array
- No manual conversion needed

---

## In TypeScript/JavaScript (Frontend)

**Type**: `string[]` (array of UUID strings)

**If retrieved from API**:
```typescript
interface DailyMood {
  id: string;
  user_id: string;
  entry_date: string;
  mood: number;
  notes: string;
  symptoms: string[];
  cycle_phase: string;
  habit_entry_ids: string[];  // Array of UUID strings
}
```

**Example**:
```typescript
const moodEntry: DailyMood = {
  habit_entry_ids: [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440003"
  ]
};
```

---

## In JSON/API Response

**Type**: JSON array of strings

**Example JSON**:
```json
{
  "id": "mood-uuid-123",
  "user_id": "user-uuid-456",
  "entry_date": "2025-01-15",
  "mood": 3,
  "habit_entry_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003"
  ]
}
```

---

## Summary by Context

| Context | Type | Example |
|---------|------|---------|
| **PostgreSQL Schema** | `_uuid` (array of UUIDs) | `_uuid` |
| **Python Code** | `list[str]` | `["uuid1", "uuid2", "uuid3"]` |
| **TypeScript/JavaScript** | `string[]` | `["uuid1", "uuid2", "uuid3"]` |
| **JSON/API** | Array of strings | `["uuid1", "uuid2", "uuid3"]` |
| **Supabase Client** | Automatically converts `list` ↔ `_uuid` | No manual conversion needed |

---

## Key Points

1. **PostgreSQL Type**: `_uuid` (array type, indicated by `_` prefix)
2. **Python Type**: `list[str]` (list of UUID strings)
3. **Conversion**: Automatic via Supabase client
4. **Contents**: Array of UUID strings that reference `daily_habit_entries.id`
5. **Can be empty**: `[]` if no habits were tracked that day
6. **Can have duplicates**: Though unlikely in practice

---

## Example Usage in Code

### Python (Backend)
```python
# Create as Python list
entry_ids = []
entry_ids.append("uuid-1")
entry_ids.append("uuid-2")

# Pass to Supabase (auto-converted to _uuid array)
daily_mood_data = {
    'habit_entry_ids': entry_ids  # list[str] → _uuid
}
```

### TypeScript (Frontend)
```typescript
// Receive from API
const mood = await fetch('/daily-moods/...');
const habitEntryIds: string[] = mood.habit_entry_ids;

// Use for filtering
const matchingEntries = habitEntries.filter(
    entry => habitEntryIds.includes(entry.id)
);
```

---

## PostgreSQL Array Operations

If querying directly in PostgreSQL:

```sql
-- Check if array contains a specific UUID
SELECT * FROM daily_moods 
WHERE '550e8400-e29b-41d4-a716-446655440001' = ANY(habit_entry_ids);

-- Get array length
SELECT array_length(habit_entry_ids, 1) FROM daily_moods;

-- Unnest array to get individual IDs
SELECT unnest(habit_entry_ids) FROM daily_moods;
```

---

## Important Notes

1. **Not a Foreign Key Constraint**: 
   - `habit_entry_ids` is an array field, not a foreign key
   - PostgreSQL doesn't support array foreign keys directly
   - Referential integrity must be maintained in application code

2. **Order Matters** (potentially):
   - Arrays preserve order
   - Current code doesn't rely on order, but it's preserved

3. **Null Handling**:
   - Can be `NULL` if no mood was tracked
   - Can be `[]` (empty array) if mood tracked but no habits

4. **Size Limit**:
   - PostgreSQL arrays can be large, but practical limit depends on use case
   - Typically 3-10 habit entries per day

