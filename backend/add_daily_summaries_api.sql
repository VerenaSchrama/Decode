-- SQL to add new API endpoints for daily_summaries table
-- This file documents the new endpoints that should be added to api.py

-- New API Endpoints to Add:

-- 1. GET /user/{user_id}/daily-summaries?days=7
--    Returns daily summaries for the last N days
--    Replaces the need to calculate completion_percentage on-the-fly

-- 2. GET /user/{user_id}/daily-summary/{date}
--    Returns specific day's summary
--    Useful for detailed daily analysis

-- 3. POST /daily-summaries/upsert
--    Manually upsert a daily summary (if needed)
--    Useful for data correction or manual entry

-- Example queries these endpoints would use:

-- Query 1: Get daily summaries for last N days
/*
SELECT 
    ds.*,
    p.name as user_name
FROM daily_summaries ds
JOIN profiles p ON ds.user_id = p.user_id
WHERE ds.user_id = $1
  AND ds.entry_date >= CURRENT_DATE - INTERVAL '$2 days'
ORDER BY ds.entry_date DESC;
*/

-- Query 2: Get specific day's summary
/*
SELECT 
    ds.*,
    p.name as user_name
FROM daily_summaries ds
JOIN profiles p ON ds.user_id = p.user_id
WHERE ds.user_id = $1
  AND ds.entry_date = $2;
*/

-- Query 3: Get completion trends over time
/*
SELECT 
    entry_date,
    completion_percentage,
    total_habits,
    completed_habits,
    overall_mood
FROM daily_summaries
WHERE user_id = $1
  AND entry_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY entry_date ASC;
*/

-- Query 4: Get user's best and worst days
/*
SELECT 
    'Best Day' as day_type,
    entry_date,
    completion_percentage,
    overall_mood
FROM daily_summaries
WHERE user_id = $1
ORDER BY completion_percentage DESC, overall_mood DESC
LIMIT 1

UNION ALL

SELECT 
    'Worst Day' as day_type,
    entry_date,
    completion_percentage,
    overall_mood
FROM daily_summaries
WHERE user_id = $1
ORDER BY completion_percentage ASC, overall_mood ASC
LIMIT 1;
*/
