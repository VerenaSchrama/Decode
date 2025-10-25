-- Fix anonymous user support by making foreign key constraints nullable
-- This allows anonymous users to store intake data without requiring auth.users

-- First, check current constraints
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

-- Option 1: Make user_id nullable in profiles table (if not already)
-- ALTER TABLE profiles ALTER COLUMN user_id DROP NOT NULL;

-- Option 2: Remove foreign key constraint from profiles table
-- ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;

-- Option 3: Remove foreign key constraint from intakes table  
-- ALTER TABLE intakes DROP CONSTRAINT IF EXISTS fk_intakes_user;

-- For now, let's use Option 3 - remove the foreign key constraint from intakes
-- This allows anonymous users to store intake data without requiring a profile
ALTER TABLE intakes DROP CONSTRAINT IF EXISTS fk_intakes_user;

-- Verify the constraint is removed
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
  AND tc.table_name = 'intakes'
  AND kcu.column_name = 'user_id';
