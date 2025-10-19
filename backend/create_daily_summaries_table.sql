-- Create daily_summaries table to store overall daily completion data
-- This replaces storing completion_percentage in each individual habit entry

-- Step 1: Create the daily_summaries table
CREATE TABLE IF NOT EXISTS daily_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    total_habits INTEGER NOT NULL DEFAULT 0,
    completed_habits INTEGER NOT NULL DEFAULT 0,
    completion_percentage FLOAT NOT NULL DEFAULT 0.0 CHECK (completion_percentage >= 0.0 AND completion_percentage <= 100.0),
    overall_mood INTEGER CHECK (overall_mood >= 1 AND overall_mood <= 10),
    overall_notes TEXT,
    cycle_phase VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one summary per user per day
    UNIQUE(user_id, entry_date)
);

-- Step 2: Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_daily_summaries_user_id ON daily_summaries(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_entry_date ON daily_summaries(entry_date);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_user_date ON daily_summaries(user_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_daily_summaries_completion ON daily_summaries(completion_percentage);

-- Step 3: Add RLS (Row Level Security) policies
ALTER TABLE daily_summaries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own daily summaries
CREATE POLICY "Users can view own daily summaries" ON daily_summaries
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- Policy: Users can insert their own daily summaries
CREATE POLICY "Users can insert own daily summaries" ON daily_summaries
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- Policy: Users can update their own daily summaries
CREATE POLICY "Users can update own daily summaries" ON daily_summaries
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Policy: Users can delete their own daily summaries
CREATE POLICY "Users can delete own daily summaries" ON daily_summaries
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Step 4: Create a function to automatically update daily summaries
CREATE OR REPLACE FUNCTION update_daily_summary()
RETURNS TRIGGER AS $$
DECLARE
    user_uuid UUID;
    entry_date_val DATE;
    total_count INTEGER;
    completed_count INTEGER;
    completion_pct FLOAT;
    overall_mood_val INTEGER;
    overall_notes_val TEXT;
BEGIN
    -- Get the user_id and entry_date from the trigger
    IF TG_OP = 'DELETE' THEN
        user_uuid := OLD.user_id;
        entry_date_val := OLD.entry_date;
    ELSE
        user_uuid := NEW.user_id;
        entry_date_val := NEW.entry_date;
    END IF;
    
    -- Count total and completed habits for this user on this date
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE completed = true)
    INTO total_count, completed_count
    FROM daily_habit_entries 
    WHERE user_id = user_uuid AND entry_date = entry_date_val;
    
    -- Calculate completion percentage
    completion_pct := CASE 
        WHEN total_count > 0 THEN (completed_count::FLOAT / total_count::FLOAT) * 100.0
        ELSE 0.0
    END;
    
    -- Get overall mood and notes (use the most recent entry's mood/notes)
    SELECT mood, notes
    INTO overall_mood_val, overall_notes_val
    FROM daily_habit_entries 
    WHERE user_id = user_uuid 
      AND entry_date = entry_date_val 
      AND mood IS NOT NULL
    ORDER BY created_at DESC
    LIMIT 1;
    
    -- Insert or update daily summary
    INSERT INTO daily_summaries (
        user_id, entry_date, total_habits, completed_habits, 
        completion_percentage, overall_mood, overall_notes, updated_at
    ) VALUES (
        user_uuid, entry_date_val, total_count, completed_count,
        completion_pct, overall_mood_val, overall_notes_val, NOW()
    )
    ON CONFLICT (user_id, entry_date) 
    DO UPDATE SET
        total_habits = EXCLUDED.total_habits,
        completed_habits = EXCLUDED.completed_habits,
        completion_percentage = EXCLUDED.completion_percentage,
        overall_mood = EXCLUDED.overall_mood,
        overall_notes = EXCLUDED.overall_notes,
        updated_at = NOW();
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Step 5: Create triggers to automatically update daily summaries
CREATE TRIGGER trigger_update_daily_summary_insert
    AFTER INSERT ON daily_habit_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_daily_summary();

CREATE TRIGGER trigger_update_daily_summary_update
    AFTER UPDATE ON daily_habit_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_daily_summary();

CREATE TRIGGER trigger_update_daily_summary_delete
    AFTER DELETE ON daily_habit_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_daily_summary();

-- Step 6: Verify table creation
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'daily_summaries' 
  AND table_schema = 'public'
ORDER BY ordinal_position;

-- Step 7: Show table structure
\d daily_summaries;
