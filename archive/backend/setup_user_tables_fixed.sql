-- Create user-specific tables for the health app
-- Run this in the Supabase SQL Editor

-- 1. Create user_habits table
CREATE TABLE IF NOT EXISTS user_habits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    habit_name VARCHAR(255) NOT NULL,
    habit_description TEXT,
    intervention_id INTEGER REFERENCES "InterventionsBASE"("Intervention_ID") ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- 2. Create user_interventions table
CREATE TABLE IF NOT EXISTS user_interventions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    profile_match TEXT NOT NULL,
    scientific_source TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    helpful_count INTEGER DEFAULT 0,
    total_tries INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_by VARCHAR(255),
    review_notes TEXT
);

-- 3. Create intervention_habits table (for user-generated interventions)
CREATE TABLE IF NOT EXISTS intervention_habits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    intervention_id UUID REFERENCES user_interventions(id) ON DELETE CASCADE,
    number INTEGER NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create daily_habit_entries table (for tracking daily progress)
CREATE TABLE IF NOT EXISTS daily_habit_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    habits_completed TEXT[], -- Array of habit names completed
    mood VARCHAR(50),
    notes TEXT,
    completion_percentage DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, entry_date)
);

-- 5. Create intervention_feedback table
CREATE TABLE IF NOT EXISTS intervention_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    intervention_id UUID REFERENCES user_interventions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    helpful BOOLEAN,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Update chat_messages table to match user_id type
-- First drop existing table if it exists and recreate with correct type
DROP TABLE IF EXISTS chat_messages CASCADE;
CREATE TABLE chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context_used JSONB
);

-- 7. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_habits_user_id ON user_habits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_habits_status ON user_habits(status);
CREATE INDEX IF NOT EXISTS idx_user_interventions_user_id ON user_interventions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interventions_status ON user_interventions(status);
CREATE INDEX IF NOT EXISTS idx_intervention_habits_intervention_id ON intervention_habits(intervention_id);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_id ON daily_habit_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_date ON daily_habit_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);

-- 8. Enable Row Level Security (RLS) for user data protection
ALTER TABLE user_habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interventions ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervention_habits ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_habit_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervention_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- 9. Create RLS policies (basic - users can only access their own data)
CREATE POLICY "Users can view their own habits" ON user_habits
    FOR SELECT USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can insert their own habits" ON user_habits
    FOR INSERT WITH CHECK (user_id = auth.uid()::integer);

CREATE POLICY "Users can update their own habits" ON user_habits
    FOR UPDATE USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can delete their own habits" ON user_habits
    FOR DELETE USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can view their own interventions" ON user_interventions
    FOR SELECT USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can insert their own interventions" ON user_interventions
    FOR INSERT WITH CHECK (user_id = auth.uid()::integer);

CREATE POLICY "Users can update their own interventions" ON user_interventions
    FOR UPDATE USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can view their own daily entries" ON daily_habit_entries
    FOR ALL USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can view their own chat messages" ON chat_messages
    FOR ALL USING (user_id = auth.uid()::integer);

-- 10. Allow public access to approved interventions (for browsing)
CREATE POLICY "Anyone can view approved interventions" ON user_interventions
    FOR SELECT USING (status = 'approved');

-- 11. Allow public access to intervention habits for approved interventions
CREATE POLICY "Anyone can view habits for approved interventions" ON intervention_habits
    FOR SELECT USING (intervention_id IN (
        SELECT id FROM user_interventions WHERE status = 'approved'
    ));

-- 12. Allow users to view feedback for their own interventions
CREATE POLICY "Users can view feedback for their interventions" ON intervention_feedback
    FOR SELECT USING (user_id = auth.uid()::integer);

CREATE POLICY "Users can insert feedback for their interventions" ON intervention_feedback
    FOR INSERT WITH CHECK (user_id = auth.uid()::integer);

-- 13. Allow users to view habits for their own interventions
CREATE POLICY "Users can view habits for their interventions" ON intervention_habits
    FOR SELECT USING (intervention_id IN (
        SELECT id FROM user_interventions WHERE user_id = auth.uid()::integer
    ));

CREATE POLICY "Users can insert habits for their interventions" ON intervention_habits
    FOR INSERT WITH CHECK (intervention_id IN (
        SELECT id FROM user_interventions WHERE user_id = auth.uid()::integer
    ));

