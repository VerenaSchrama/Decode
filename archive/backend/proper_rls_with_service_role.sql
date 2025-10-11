-- Proper RLS implementation with service role access
-- This allows the trigger to work while restricting normal users

-- First, drop any existing policies
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
DROP POLICY IF EXISTS "System can create profiles" ON user_profiles;
DROP POLICY IF EXISTS "System can create profiles during registration" ON user_profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;

-- Enable RLS on user_profiles table
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 1. Allow service role to insert profiles (for triggers)
CREATE POLICY "Service role can insert profiles"
  ON user_profiles
  FOR INSERT
  TO service_role
  WITH CHECK (true);

-- 2. Allow service role to update profiles (for triggers)
CREATE POLICY "Service role can update profiles"
  ON user_profiles
  FOR UPDATE
  TO service_role
  USING (true);

-- 3. Allow service role to select profiles (for triggers)
CREATE POLICY "Service role can select profiles"
  ON user_profiles
  FOR SELECT
  TO service_role
  USING (true);

-- 4. Allow authenticated users to view their own profile
CREATE POLICY "Users can view their own profile"
  ON user_profiles
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_uuid);

-- 5. Allow authenticated users to insert their own profile
CREATE POLICY "Users can insert their own profile"
  ON user_profiles
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_uuid);

-- 6. Allow authenticated users to update their own profile
CREATE POLICY "Users can update their own profile"
  ON user_profiles
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_uuid);

-- Verify the policies were created
SELECT 
    schemaname, 
    tablename, 
    policyname, 
    permissive, 
    roles, 
    cmd, 
    qual 
FROM pg_policies 
WHERE tablename = 'user_profiles'
ORDER BY policyname;

-- Test that RLS is enabled
SELECT 
    'RLS Status' as test_type,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE tablename = 'user_profiles';

-- Show current user roles for testing
SELECT 
    'Current User Context' as test_type,
    auth.uid() as current_user_id,
    auth.role() as current_role;
