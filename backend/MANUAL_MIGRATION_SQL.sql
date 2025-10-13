-- Manual Migration Script for Supabase SQL Editor
-- Run this in the Supabase SQL Editor to complete the migration

-- Step 1: Drop the existing foreign key constraint that points to users table
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_uuid_fkey;

-- Step 2: Drop the old user_id foreign key constraint
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_fkey;

-- Step 3: Drop the old unique constraint
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_entry_date_key;

-- Step 4: Update existing entries to use the demo user UUID
UPDATE daily_habit_entries 
SET user_uuid = '117e24ea-3562-45f2-9256-f1b032d0d86b'::UUID 
WHERE user_id = 1;

-- Step 5: Make user_uuid NOT NULL
ALTER TABLE daily_habit_entries ALTER COLUMN user_uuid SET NOT NULL;

-- Step 6: Add foreign key constraint to user_profiles (not users)
ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_fkey 
    FOREIGN KEY (user_uuid) REFERENCES user_profiles(user_uuid) ON DELETE CASCADE;

-- Step 7: Add unique constraint on user_uuid + entry_date
ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_entry_date_key 
    UNIQUE(user_uuid, entry_date);

-- Step 8: Drop the old user_id column
ALTER TABLE daily_habit_entries DROP COLUMN user_id;

-- Step 9: Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_uuid ON daily_habit_entries(user_uuid);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_entry_date ON daily_habit_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_date ON daily_habit_entries(user_uuid, entry_date);

-- Step 10: Verify the migration
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'daily_habit_entries' 
ORDER BY ordinal_position;
