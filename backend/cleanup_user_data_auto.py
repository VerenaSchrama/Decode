#!/usr/bin/env python3
"""
Non-interactive cleanup script to delete all user data from Supabase tables
Preserves static base tables (InterventionsBASE, HabitsBASE)
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class UserDataCleanup:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.url or not self.service_key:
            raise ValueError("Missing Supabase credentials in environment variables")
        
        # Use service role key to bypass RLS
        self.client = create_client(self.url, self.service_key)
        
        # Tables to clean (user data tables)
        self.user_tables = [
            'profiles',
            'intakes', 
            'user_interventions',
            'user_habits',
            'daily_habit_entries',
            'daily_summaries',
            'intervention_periods',
            'intervention_feedback',
            'intervention_habits',
            'custom_interventions',
            'chat_messages'
        ]
        
        # Tables to preserve (static base tables)
        self.preserve_tables = [
            'InterventionsBASE',
            'HabitsBASE'
        ]
    
    def get_table_counts(self):
        """Get current row counts for all tables"""
        print("\n📊 Current table counts:")
        counts = {}
        
        for table in self.user_tables + self.preserve_tables:
            try:
                result = self.client.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                counts[table] = count
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: Error - {e}")
                counts[table] = "Error"
        
        return counts
    
    def cleanup_user_data(self):
        """Delete all user data from specified tables"""
        print("\n🧹 Starting cleanup...")
        
        # Delete in reverse dependency order to avoid foreign key conflicts
        deletion_order = [
            'daily_habit_entries',
            'daily_summaries', 
            'intervention_feedback',
            'intervention_habits',
            'intervention_periods',
            'user_habits',
            'user_interventions',
            'custom_interventions',
            'chat_messages',
            'intakes',
            'profiles'
        ]
        
        deleted_counts = {}
        
        for table in deletion_order:
            if table not in self.user_tables:
                continue
                
            try:
                print(f"  Deleting from {table}...")
                
                # Get count before deletion
                count_result = self.client.table(table).select('*', count='exact').execute()
                before_count = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
                
                # Delete all rows
                delete_result = self.client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                
                deleted_counts[table] = before_count
                print(f"    ✅ Deleted {before_count} rows from {table}")
                
            except Exception as e:
                print(f"    ❌ Error deleting from {table}: {e}")
                deleted_counts[table] = f"Error: {e}"
        
        return deleted_counts
    
    def verify_cleanup(self):
        """Verify that cleanup was successful"""
        print("\n🔍 Verifying cleanup...")
        
        for table in self.user_tables:
            try:
                result = self.client.table(table).select('*', count='exact').execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                
                if count == 0:
                    print(f"  ✅ {table}: 0 rows (clean)")
                else:
                    print(f"  ⚠️  {table}: {count} rows remaining")
                    
            except Exception as e:
                print(f"  ❌ {table}: Error checking - {e}")
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🗑️  User Data Cleanup Script (Non-Interactive)")
        print("=" * 50)
        
        # Step 1: Show current state
        counts_before = self.get_table_counts()
        
        # Step 2: Perform cleanup (no confirmation needed)
        print("\n⚠️  WARNING: Deleting ALL user data!")
        deleted_counts = self.cleanup_user_data()
        
        # Step 3: Verify cleanup
        self.verify_cleanup()
        
        # Step 4: Summary
        print("\n📋 Cleanup Summary:")
        print("=" * 30)
        
        total_deleted = 0
        for table, count in deleted_counts.items():
            if isinstance(count, int):
                total_deleted += count
                print(f"  {table}: {count} rows deleted")
            else:
                print(f"  {table}: {count}")
        
        print(f"\n🎯 Total rows deleted: {total_deleted}")
        print("✅ Cleanup completed!")
        
        # Step 5: Show preserved tables
        print("\n📚 Preserved tables (unchanged):")
        for table in self.preserve_tables:
            count = counts_before.get(table, "Unknown")
            print(f"  {table}: {count} rows")

def main():
    try:
        cleanup = UserDataCleanup()
        cleanup.run_cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
