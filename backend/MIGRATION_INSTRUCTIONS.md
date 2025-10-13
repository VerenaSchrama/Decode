# Migration Instructions: Daily Habit Entries to User Profiles

## 🎯 Goal
Migrate `daily_habit_entries` table to use `user_uuid` referencing `user_profiles` table instead of `user_id` referencing `users` table. This aligns with Supabase Auth which stores users in `user_profiles`.

## 📋 Current Status
- ✅ Demo user created in `user_profiles` table (UUID: `117e24ea-3562-45f2-9256-f1b032d0d86b`)
- ✅ API endpoints updated to use `user_uuid`
- ⚠️ Database schema migration pending (requires manual SQL execution)

## 🔧 Manual Migration Steps

### Step 1: Run SQL Migration
Execute the SQL script in **Supabase SQL Editor**:

```sql
-- File: backend/MANUAL_MIGRATION_SQL.sql
-- Run this entire script in Supabase SQL Editor

-- Step 1: Drop existing foreign key constraints
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_uuid_fkey;
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_fkey;
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_entry_date_key;

-- Step 2: Update existing entries to use demo UUID
UPDATE daily_habit_entries 
SET user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'::UUID 
WHERE user_id = 1;

-- Step 3: Make user_uuid NOT NULL
ALTER TABLE daily_habit_entries ALTER COLUMN user_uuid SET NOT NULL;

-- Step 4: Add foreign key constraint to user_profiles
ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_fkey 
    FOREIGN KEY (user_uuid) REFERENCES user_profiles(user_uuid) ON DELETE CASCADE;

-- Step 5: Add unique constraint
ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_entry_date_key 
    UNIQUE(user_uuid, entry_date);

-- Step 6: Drop old user_id column
ALTER TABLE daily_habit_entries DROP COLUMN user_id;

-- Step 7: Add indexes
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_uuid ON daily_habit_entries(user_uuid);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_entry_date ON daily_habit_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_date ON daily_habit_entries(user_uuid, entry_date);
```

### Step 2: Verify Migration
After running the SQL, verify the migration:

```sql
-- Check table structure
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'daily_habit_entries' 
ORDER BY ordinal_position;

-- Check foreign key constraints
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'daily_habit_entries';
```

### Step 3: Test API Endpoints
After migration, test the endpoints:

```bash
# Test save daily progress
curl -X POST http://localhost:8000/daily-progress \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-123",
    "entry_date": "2025-10-13",
    "habits": [
      {"habit": "Exercise", "completed": true, "notes": "Test"},
      {"habit": "Meditation", "completed": false, "notes": ""}
    ],
    "mood": {"mood": 8, "notes": "Great!"}
  }'

# Test get daily progress
curl http://localhost:8000/user/demo-user-123/daily-progress?days=7

# Test streak
curl http://localhost:8000/user/demo-user-123/streak
```

## 🎉 Expected Results

After migration:
- ✅ `daily_habit_entries` uses `user_uuid` referencing `user_profiles`
- ✅ All API endpoints work with UUID-based user identification
- ✅ New user registrations will automatically work with daily progress tracking
- ✅ No more foreign key constraint violations

## 🔄 Next Steps

1. **Run the SQL migration** in Supabase SQL Editor
2. **Test the API endpoints** to ensure they work
3. **Update authentication flow** to use actual user UUIDs instead of demo UUID
4. **Remove demo user** from `users` table (optional cleanup)

## 📊 Schema Comparison

### Before Migration:
```sql
daily_habit_entries.user_id INTEGER REFERENCES users(id)
```

### After Migration:
```sql
daily_habit_entries.user_uuid UUID REFERENCES user_profiles(user_uuid)
```

This aligns perfectly with Supabase Auth's user storage pattern!
