-- Fix daily_habit_entries table to use user_uuid instead of user_id
-- This aligns with the authentication system that uses UUIDs

-- First, drop the existing foreign key constraint
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_fkey;

-- Drop the existing user_id column
ALTER TABLE daily_habit_entries DROP COLUMN IF EXISTS user_id;

-- Add new user_uuid column that references user_profiles
ALTER TABLE daily_habit_entries ADD COLUMN user_uuid UUID REFERENCES user_profiles(user_uuid) ON DELETE CASCADE;

-- Update the unique constraint to use user_uuid instead of user_id
ALTER TABLE daily_habit_entries DROP CONSTRAINT IF EXISTS daily_habit_entries_user_id_entry_date_key;
ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_entry_date_key UNIQUE(user_uuid, entry_date);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_uuid ON daily_habit_entries(user_uuid);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_entry_date ON daily_habit_entries(entry_date);
