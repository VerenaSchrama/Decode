-- Setup Supabase Auth for HerFoodCode App
-- Run this in the Supabase SQL Editor

-- 1. Enable Supabase Auth (if not already enabled)
-- This is usually done in the Supabase dashboard under Authentication

-- 2. Create user profiles table that extends auth.users
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    name VARCHAR(255),
    age INTEGER,
    date_of_birth DATE,
    current_strategy VARCHAR(255),
    anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Enable RLS on user_profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 4. Create RLS policies for user_profiles
-- Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 5. Update daily_habit_entries to use UUID user_id
-- First, add a new column for UUID user_id
ALTER TABLE daily_habit_entries 
ADD COLUMN IF NOT EXISTS user_uuid UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 6. Update intakes table to use UUID user_id
ALTER TABLE intakes 
ADD COLUMN IF NOT EXISTS user_uuid UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- 7. Update RLS policies for daily_habit_entries
DROP POLICY IF EXISTS "Allow all operations on daily_habit_entries" ON daily_habit_entries;
ALTER TABLE daily_habit_entries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own daily entries" ON daily_habit_entries
    FOR SELECT USING (auth.uid() = user_uuid);

CREATE POLICY "Users can insert own daily entries" ON daily_habit_entries
    FOR INSERT WITH CHECK (auth.uid() = user_uuid);

CREATE POLICY "Users can update own daily entries" ON daily_habit_entries
    FOR UPDATE USING (auth.uid() = user_uuid);

-- 8. Update RLS policies for intakes
DROP POLICY IF EXISTS "Allow all operations on intakes" ON intakes;
ALTER TABLE intakes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own intakes" ON intakes
    FOR SELECT USING (auth.uid() = user_uuid);

CREATE POLICY "Users can insert own intakes" ON intakes
    FOR INSERT WITH CHECK (auth.uid() = user_uuid);

CREATE POLICY "Users can update own intakes" ON intakes
    FOR UPDATE USING (auth.uid() = user_uuid);

-- 9. Create function to automatically create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, name, anonymous)
    VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'name', 'User'), false);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. Create trigger to call the function
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 11. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON public.user_profiles TO anon, authenticated;
GRANT ALL ON public.daily_habit_entries TO anon, authenticated;
GRANT ALL ON public.intakes TO anon, authenticated;

-- 12. Refresh schema cache
NOTIFY pgrst, 'reload schema';
