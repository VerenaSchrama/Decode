#!/usr/bin/env python3
"""
Create user-specific tables in Supabase for user habits and interventions
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def create_user_tables():
    """Create user_habits and user_interventions tables in Supabase"""
    
    # Initialize Supabase client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials")
        return False
    
    supabase: Client = create_client(url, key)
    
    print("🔄 Creating user-specific tables...")
    
    # SQL commands to create the tables
    sql_commands = [
        # Create user_habits table
        """
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
        """,
        
        # Create user_interventions table
        """
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
        """,
        
        # Create intervention_habits table (for user-generated interventions)
        """
        CREATE TABLE IF NOT EXISTS intervention_habits (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            intervention_id UUID REFERENCES user_interventions(id) ON DELETE CASCADE,
            number INTEGER NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create daily_habit_entries table (for tracking daily progress)
        """
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
        """,
        
        # Create intervention_feedback table
        """
        CREATE TABLE IF NOT EXISTS intervention_feedback (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            intervention_id UUID REFERENCES user_interventions(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            helpful BOOLEAN,
            comments TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Create chat_messages table
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID NOT NULL,
            message TEXT NOT NULL,
            is_user BOOLEAN NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            context_used JSONB
        );
        """,
        
        # Create indexes for better performance
        """
        CREATE INDEX IF NOT EXISTS idx_user_habits_user_id ON user_habits(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_habits_status ON user_habits(status);
        CREATE INDEX IF NOT EXISTS idx_user_interventions_user_id ON user_interventions(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_interventions_status ON user_interventions(status);
        CREATE INDEX IF NOT EXISTS idx_intervention_habits_intervention_id ON intervention_habits(intervention_id);
        CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_id ON daily_habit_entries(user_id);
        CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_date ON daily_habit_entries(entry_date);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
        """,
        
        # Enable Row Level Security (RLS) for user data protection
        """
        ALTER TABLE user_habits ENABLE ROW LEVEL SECURITY;
        ALTER TABLE user_interventions ENABLE ROW LEVEL SECURITY;
        ALTER TABLE intervention_habits ENABLE ROW LEVEL SECURITY;
        ALTER TABLE daily_habit_entries ENABLE ROW LEVEL SECURITY;
        ALTER TABLE intervention_feedback ENABLE ROW LEVEL SECURITY;
        ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
        """,
        
        # Create RLS policies (basic - users can only access their own data)
        """
        CREATE POLICY "Users can view their own habits" ON user_habits
            FOR SELECT USING (user_id = auth.uid()::integer);
        
        CREATE POLICY "Users can insert their own habits" ON user_habits
            FOR INSERT WITH CHECK (user_id = auth.uid()::integer);
        
        CREATE POLICY "Users can update their own habits" ON user_habits
            FOR UPDATE USING (user_id = auth.uid()::integer);
        
        CREATE POLICY "Users can delete their own habits" ON user_habits
            FOR DELETE USING (user_id = auth.uid()::integer);
        """,
        
        """
        CREATE POLICY "Users can view their own interventions" ON user_interventions
            FOR SELECT USING (user_id = auth.uid()::integer);
        
        CREATE POLICY "Users can insert their own interventions" ON user_interventions
            FOR INSERT WITH CHECK (user_id = auth.uid()::integer);
        
        CREATE POLICY "Users can update their own interventions" ON user_interventions
            FOR UPDATE USING (user_id = auth.uid()::integer);
        """,
        
        """
        CREATE POLICY "Users can view their own daily entries" ON daily_habit_entries
            FOR ALL USING (user_id = auth.uid()::integer);
        """,
        
        """
        CREATE POLICY "Users can view their own chat messages" ON chat_messages
            FOR ALL USING (user_id = auth.uid());
        """,
        
        # Allow public access to approved interventions (for browsing)
        """
        CREATE POLICY "Anyone can view approved interventions" ON user_interventions
            FOR SELECT USING (status = 'approved');
        """,
        
        # Allow public access to intervention habits for approved interventions
        """
        CREATE POLICY "Anyone can view habits for approved interventions" ON intervention_habits
            FOR SELECT USING (intervention_id IN (
                SELECT id FROM user_interventions WHERE status = 'approved'
            ));
        """
    ]
    
    try:
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            print(f"🔄 Executing command {i}/{len(sql_commands)}...")
            result = supabase.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Command {i} executed successfully")
        
        print("\n✅ All user-specific tables created successfully!")
        print("\n📋 Created tables:")
        print("  - user_habits: User's personal habit tracking")
        print("  - user_interventions: User-generated interventions")
        print("  - intervention_habits: Habits for user-generated interventions")
        print("  - daily_habit_entries: Daily progress tracking")
        print("  - intervention_feedback: User feedback on interventions")
        print("  - chat_messages: Chat history storage")
        
        print("\n🔒 Security features enabled:")
        print("  - Row Level Security (RLS) enabled for all tables")
        print("  - Users can only access their own data")
        print("  - Approved interventions are publicly viewable")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def test_tables():
    """Test that the tables were created successfully"""
    print("\n🔄 Testing table creation...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Test each table
        tables_to_test = [
            'user_habits',
            'user_interventions', 
            'intervention_habits',
            'daily_habit_entries',
            'intervention_feedback',
            'chat_messages'
        ]
        
        for table in tables_to_test:
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ Table '{table}' is accessible")
        
        print("\n✅ All tables are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing tables: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating user-specific database tables...")
    
    if create_user_tables():
        test_tables()
        print("\n🎉 Database setup complete! The following API endpoints should now work:")
        print("  - GET /user/{user_id}/insights")
        print("  - GET /user/{user_id}/habits") 
        print("  - POST /interventions/submit")
        print("  - POST /daily-progress")
        print("  - GET /user/{user_id}/daily-progress")
        print("  - POST /chat/message")
        print("  - GET /chat/history/{user_id}")
    else:
        print("\n❌ Database setup failed. Please check your Supabase credentials and try again.")

