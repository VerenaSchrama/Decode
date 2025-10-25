-- Supabase Database Updates Required
-- Run these commands in your Supabase SQL editor

-- 1. Remove foreign key constraint from profiles table to allow anonymous users
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;

-- 2. Remove foreign key constraint from intakes table to allow anonymous intake data
ALTER TABLE intakes DROP CONSTRAINT IF EXISTS fk_intakes_user;

-- 3. Add missing context column to custom_interventions table
ALTER TABLE custom_interventions 
ADD COLUMN IF NOT EXISTS context TEXT;

-- 4. Verify the changes
SELECT 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name IN ('profiles', 'intakes')
  AND kcu.column_name = 'user_id';

-- 5. Check custom_interventions table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'custom_interventions' 
ORDER BY ordinal_position;
