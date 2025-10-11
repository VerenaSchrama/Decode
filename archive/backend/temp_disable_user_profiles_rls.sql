-- Temporarily disable RLS on user_profiles table to get authentication working
-- This is a temporary solution for testing

-- Disable RLS on user_profiles only
ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;

-- Keep RLS enabled on other tables for security
-- ALTER TABLE daily_habit_entries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE intakes ENABLE ROW LEVEL SECURITY;

-- Verify RLS status
SELECT 
    schemaname, 
    tablename, 
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename IN ('user_profiles', 'daily_habit_entries', 'intakes')
ORDER BY tablename;

-- Show current policies
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    permissive, 
    roles, 
    cmd, 
    qual 
FROM pg_policies 
WHERE tablename IN ('user_profiles', 'daily_habit_entries', 'intakes')
ORDER BY tablename, policyname;
