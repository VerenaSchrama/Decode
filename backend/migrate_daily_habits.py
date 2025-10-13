#!/usr/bin/env python3
"""
Migration script to update daily_habit_entries table to use user_uuid referencing user_profiles
This aligns with Supabase Auth which stores users in user_profiles table
"""

import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

def migrate_daily_habits_to_user_profiles():
    """Migrate daily_habit_entries to use user_uuid referencing user_profiles"""
    
    load_dotenv()
    
    # Create service client to bypass RLS
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials")
        return False
    
    service_client = create_client(supabase_url, service_key)
    
    try:
        print("🔄 Starting migration to user_profiles schema...")
        
        # Step 1: Get the demo user UUID
        demo_user = service_client.table('user_profiles').select('*').eq('email', 'demo@example.com').execute()
        if not demo_user.data:
            print("❌ Demo user not found in user_profiles")
            return False
        
        demo_uuid = demo_user.data[0]['user_uuid']
        print(f"✅ Found demo user UUID: {demo_uuid}")
        
        # Step 2: Add user_uuid column to daily_habit_entries (if not exists)
        print("Step 2: Adding user_uuid column...")
        try:
            # Try to add the column
            service_client.rpc('exec_sql', {'sql': 'ALTER TABLE daily_habit_entries ADD COLUMN user_uuid UUID'}).execute()
            print("✅ Added user_uuid column")
        except Exception as e:
            if "already exists" in str(e) or "duplicate column" in str(e):
                print("✅ user_uuid column already exists")
            else:
                print(f"⚠️ Column add error (may already exist): {e}")
        
        # Step 3: Update existing entries to use demo UUID
        print("Step 3: Updating existing entries...")
        existing_entries = service_client.table('daily_habit_entries').select('*').is_('user_uuid', 'null').execute()
        print(f"Found {len(existing_entries.data)} entries to update")
        
        for entry in existing_entries.data:
            update_result = service_client.table('daily_habit_entries').update({
                'user_uuid': demo_uuid
            }).eq('id', entry['id']).execute()
            print(f"✅ Updated entry {entry['id']}")
        
        # Step 4: Make user_uuid NOT NULL
        print("Step 4: Making user_uuid NOT NULL...")
        try:
            service_client.rpc('exec_sql', {'sql': 'ALTER TABLE daily_habit_entries ALTER COLUMN user_uuid SET NOT NULL'}).execute()
            print("✅ Made user_uuid NOT NULL")
        except Exception as e:
            print(f"⚠️ NOT NULL constraint error: {e}")
        
        # Step 5: Add foreign key constraint
        print("Step 5: Adding foreign key constraint...")
        try:
            service_client.rpc('exec_sql', {'sql': 'ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_fkey FOREIGN KEY (user_uuid) REFERENCES user_profiles(user_uuid) ON DELETE CASCADE'}).execute()
            print("✅ Added foreign key constraint")
        except Exception as e:
            if "already exists" in str(e):
                print("✅ Foreign key constraint already exists")
            else:
                print(f"⚠️ Foreign key error: {e}")
        
        # Step 6: Add unique constraint
        print("Step 6: Adding unique constraint...")
        try:
            service_client.rpc('exec_sql', {'sql': 'ALTER TABLE daily_habit_entries ADD CONSTRAINT daily_habit_entries_user_uuid_entry_date_key UNIQUE(user_uuid, entry_date)'}).execute()
            print("✅ Added unique constraint")
        except Exception as e:
            if "already exists" in str(e):
                print("✅ Unique constraint already exists")
            else:
                print(f"⚠️ Unique constraint error: {e}")
        
        # Step 7: Drop old user_id column
        print("Step 7: Dropping old user_id column...")
        try:
            service_client.rpc('exec_sql', {'sql': 'ALTER TABLE daily_habit_entries DROP COLUMN user_id'}).execute()
            print("✅ Dropped user_id column")
        except Exception as e:
            print(f"⚠️ Drop column error: {e}")
        
        # Step 8: Add indexes
        print("Step 8: Adding indexes...")
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_uuid ON daily_habit_entries(user_uuid)',
            'CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_entry_date ON daily_habit_entries(entry_date)',
            'CREATE INDEX IF NOT EXISTS idx_daily_habit_entries_user_date ON daily_habit_entries(user_uuid, entry_date)'
        ]
        
        for index_sql in indexes:
            try:
                service_client.rpc('exec_sql', {'sql': index_sql}).execute()
                print(f"✅ Added index: {index_sql.split()[-1]}")
            except Exception as e:
                print(f"⚠️ Index error: {e}")
        
        print("\n🎉 Migration completed successfully!")
        print(f"Demo UUID: {demo_uuid}")
        
        # Verify the migration
        print("\n🔍 Verifying migration...")
        test_entries = service_client.table('daily_habit_entries').select('*').limit(3).execute()
        print(f"Sample entries after migration: {test_entries.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrate_daily_habits_to_user_profiles()
