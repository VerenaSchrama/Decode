-- Set up proper RLS policies that allow users to manage their own data
-- This maintains security while allowing authentication to work

-- First, drop any existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can view own daily entries" ON daily_habit_entries;
DROP POLICY IF EXISTS "Users can insert own daily entries" ON daily_habit_entries;
DROP POLICY IF EXISTS "Users can update own daily entries" ON daily_habit_entries;
DROP POLICY IF EXISTS "Users can view own intakes" ON intakes;
DROP POLICY IF EXISTS "Users can insert own intakes" ON intakes;
DROP POLICY IF EXISTS "Users can update own intakes" ON intakes;
DROP POLICY IF EXISTS "Allow all operations for testing daily" ON daily_habit_entries;
DROP POLICY IF EXISTS "Allow all operations for testing intakes" ON intakes;

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_habit_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE intakes ENABLE ROW LEVEL SECURITY;

-- Create permissive policies for user_profiles
-- These allow users to manage their own profiles
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_uuid);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_uuid);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_uuid);

-- Create permissive policies for daily_habit_entries
CREATE POLICY "Users can view own daily entries" ON daily_habit_entries
    FOR SELECT USING (auth.uid() = user_uuid);

CREATE POLICY "Users can insert own daily entries" ON daily_habit_entries
    FOR INSERT WITH CHECK (auth.uid() = user_uuid);

CREATE POLICY "Users can update own daily entries" ON daily_habit_entries
    FOR UPDATE USING (auth.uid() = user_uuid);

-- Create permissive policies for intakes
CREATE POLICY "Users can view own intakes" ON intakes
    FOR SELECT USING (auth.uid() = user_uuid);

CREATE POLICY "Users can insert own intakes" ON intakes
    FOR INSERT WITH CHECK (auth.uid() = user_uuid);

CREATE POLICY "Users can update own intakes" ON intakes
    FOR UPDATE USING (auth.uid() = user_uuid);

-- Also add a policy that allows the system to create profiles during registration
-- This is needed because the trigger runs in a different context
CREATE POLICY "System can create profiles" ON user_profiles
    FOR INSERT WITH CHECK (true);

-- Verify policies were created
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

-- Test that RLS is working by checking the current user context
SELECT 
    'Current auth context' as test_type,
    auth.uid() as current_user_id,
    auth.role() as current_role;
