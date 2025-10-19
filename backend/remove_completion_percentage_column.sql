-- Remove completion_percentage column from daily_habit_entries table
-- This column was incorrectly storing the overall day's completion percentage
-- in each individual habit entry, which is redundant and logically wrong.

-- Step 1: Drop the completion_percentage column
ALTER TABLE daily_habit_entries DROP COLUMN IF EXISTS completion_percentage;

-- Step 2: Verify the column has been removed
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'daily_habit_entries' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Step 3: Show the updated table structure
\d daily_habit_entries;
