-- Query to get mood data for a specific daily_habit_entry
-- Given a habit entry ID, find the mood entry that links to it

-- Example: Get mood for a specific habit entry
SELECT 
    dhe.id as habit_entry_id,
    dhe.habit_id,
    dhe.completed,
    dhe.entry_date,
    dm.id as mood_id,
    dm.mood,
    dm.notes as mood_notes,
    dm.symptoms,
    dm.cycle_phase
FROM daily_habit_entries dhe
LEFT JOIN daily_moods dm 
    ON dm.user_id = dhe.user_id 
    AND dm.entry_date = dhe.entry_date
    AND dhe.id = ANY(dm.habit_entry_ids)
WHERE dhe.id = 'YOUR_HABIT_ENTRY_ID_HERE';

-- Or get all habit entries with their mood for a specific user and date
SELECT 
    dhe.id as habit_entry_id,
    dhe.habit_id,
    dhe.completed,
    dhe.entry_date,
    dm.mood,
    dm.symptoms,
    dm.cycle_phase
FROM daily_habit_entries dhe
LEFT JOIN daily_moods dm 
    ON dm.user_id = dhe.user_id 
    AND dm.entry_date = dhe.entry_date
WHERE dhe.user_id = 'YOUR_USER_ID_HERE'
    AND dhe.entry_date = '2025-01-15';  -- Replace with your date

