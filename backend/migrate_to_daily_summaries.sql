-- Migration script to populate daily_summaries table with existing data
-- Run this after creating the daily_summaries table

-- Step 1: Populate daily_summaries with existing data from daily_habit_entries
INSERT INTO daily_summaries (
    user_id, 
    entry_date, 
    total_habits, 
    completed_habits, 
    completion_percentage,
    overall_mood,
    overall_notes,
    created_at,
    updated_at
)
SELECT 
    user_id,
    entry_date,
    COUNT(*) as total_habits,
    COUNT(*) FILTER (WHERE completed = true) as completed_habits,
    CASE 
        WHEN COUNT(*) > 0 THEN (COUNT(*) FILTER (WHERE completed = true)::FLOAT / COUNT(*)::FLOAT) * 100.0
        ELSE 0.0
    END as completion_percentage,
    -- Get the most recent mood and notes for this user/date
    (SELECT mood FROM daily_habit_entries d2 
     WHERE d2.user_id = d1.user_id 
       AND d2.entry_date = d1.entry_date 
       AND d2.mood IS NOT NULL
     ORDER BY created_at DESC LIMIT 1) as overall_mood,
    (SELECT notes FROM daily_habit_entries d2 
     WHERE d2.user_id = d1.user_id 
       AND d2.entry_date = d1.entry_date 
       AND d2.notes IS NOT NULL AND d2.notes != ''
     ORDER BY created_at DESC LIMIT 1) as overall_notes,
    MIN(created_at) as created_at,
    MAX(updated_at) as updated_at
FROM daily_habit_entries d1
GROUP BY user_id, entry_date
ON CONFLICT (user_id, entry_date) DO NOTHING;

-- Step 2: Verify the migration
SELECT 
    'Migration Summary' as info,
    COUNT(*) as total_summaries_created,
    COUNT(DISTINCT user_id) as unique_users,
    MIN(entry_date) as earliest_date,
    MAX(entry_date) as latest_date
FROM daily_summaries;

-- Step 3: Show sample data
SELECT 
    user_id,
    entry_date,
    total_habits,
    completed_habits,
    completion_percentage,
    overall_mood,
    created_at
FROM daily_summaries
ORDER BY user_id, entry_date DESC
LIMIT 10;

-- Step 4: Verify data consistency
SELECT 
    'Data Consistency Check' as check_type,
    COUNT(*) as daily_summaries_count,
    (SELECT COUNT(DISTINCT user_id, entry_date) FROM daily_habit_entries) as unique_user_dates_in_entries
FROM daily_summaries;
