-- Create daily_moods table to store mood information separately
-- This eliminates duplication and improves data normalization

CREATE TABLE IF NOT EXISTS public.daily_moods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(user_id),
    entry_date DATE NOT NULL,
    mood INTEGER,  -- 1-5 scale or emoji index
    notes TEXT,
    symptoms TEXT[],  -- Array of symptoms
    cycle_phase VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure only one mood entry per user per day
    UNIQUE(user_id, entry_date)
);

-- Add comment for documentation
COMMENT ON TABLE public.daily_moods IS 'Stores daily mood and symptom data, one entry per user per day';
COMMENT ON COLUMN public.daily_moods.user_id IS 'Foreign key to profiles table';
COMMENT ON COLUMN public.daily_moods.entry_date IS 'Date of the mood entry';
COMMENT ON COLUMN public.daily_moods.mood IS 'Mood rating (1-5 scale)';
COMMENT ON COLUMN public.daily_moods.symptoms IS 'Array of symptoms experienced';
COMMENT ON COLUMN public.daily_moods.cycle_phase IS 'Menstrual cycle phase at time of entry';

-- Create index for efficient queries by user and date
CREATE INDEX IF NOT EXISTS idx_daily_moods_user_date 
    ON public.daily_moods(user_id, entry_date DESC);

-- Drop mood-related columns from daily_habit_entries table
ALTER TABLE public.daily_habit_entries 
    DROP COLUMN IF EXISTS mood,
    DROP COLUMN IF EXISTS notes;

-- Add comment explaining the change
COMMENT ON TABLE public.daily_habit_entries IS 'Tracks individual habit completion. Mood data is now stored in daily_moods table.';

-- Refresh the PostgREST schema cache so it recognizes the changes
NOTIFY pgrst, 'reload schema';

-- Verify the changes
SELECT 
    'daily_moods table created' as status,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'daily_moods';

SELECT 
    'daily_habit_entries updated' as status,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'daily_habit_entries' 
AND column_name IN ('mood', 'notes');

