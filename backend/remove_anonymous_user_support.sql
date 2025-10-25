-- Remove Anonymous User Support - All Users Must Be Authenticated
-- Run these commands in your Supabase SQL editor

-- 1. Remove foreign key constraints that prevent anonymous users
-- (These are no longer needed since we don't support anonymous users)
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;
ALTER TABLE intakes DROP CONSTRAINT IF EXISTS fk_intakes_user;

-- 2. Add missing context column to custom_interventions table
ALTER TABLE custom_interventions 
ADD COLUMN IF NOT EXISTS context TEXT;

-- 3. Remove anonymous column from profiles table (if it exists)
ALTER TABLE profiles DROP COLUMN IF EXISTS anonymous;

-- 4. Remove anonymous column from intakes table (if it exists)
ALTER TABLE intakes DROP COLUMN IF EXISTS anonymous;

-- 5. Add foreign key constraints back (now that all users are authenticated)
-- This ensures data integrity for authenticated users
ALTER TABLE profiles 
ADD CONSTRAINT profiles_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE intakes 
ADD CONSTRAINT fk_intakes_user 
FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE;

-- 6. Verify the changes
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

-- 7. Check custom_interventions table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'custom_interventions' 
ORDER BY ordinal_position;

-- 8. Verify anonymous columns are removed
SELECT column_name 
FROM information_schema.columns 
WHERE table_name IN ('profiles', 'intakes') 
  AND column_name = 'anonymous';
