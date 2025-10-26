-- Add habit_entry_ids column to existing daily_moods table

ALTER TABLE public.daily_moods
ADD COLUMN IF NOT EXISTS habit_entry_ids UUID[];

COMMENT ON COLUMN public.daily_moods.habit_entry_ids IS 'Array of daily_habit_entries IDs tracked this day';

-- Verify the column was added
SELECT 
    'Column added successfully' as status,
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'daily_moods' 
AND column_name = 'habit_entry_ids';

