-- Fix foreign key constraint issue
-- Remove the constraint that references public.users table

-- Drop the problematic foreign key constraint
ALTER TABLE public.user_profiles 
DROP CONSTRAINT IF EXISTS user_profiles_user_uuid_fkey;

-- The user_profiles table should only reference auth.users via the trigger
-- No need for a foreign key constraint since Supabase Auth handles user creation
