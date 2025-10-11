-- Check the actual schema of daily_habit_entries table
-- Run this in Supabase SQL Editor first

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'daily_habit_entries'
AND table_schema = 'public'
ORDER BY ordinal_position;

