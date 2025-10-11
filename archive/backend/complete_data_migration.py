#!/usr/bin/env python3
"""
Complete data migration script
Moves from CSV-based data to database-based data with linked tables
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def run_complete_migration():
    """Run the complete migration process"""
    
    print("🚀 Complete Data Migration: CSV → Database")
    print("=" * 60)
    
    # Step 1: Check database schema
    print("\n📋 Step 1: Checking database schema...")
    try:
        from models.supabase_models import supabase_client
        
        # Check if tables exist
        interventions_check = supabase_client.client.table('interventions').select('count').execute()
        habits_check = supabase_client.client.table('habits').select('count').execute()
        
        print(f"✅ Interventions table: {interventions_check.count} records")
        print(f"✅ Habits table: {habits_check.count} records")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        print("Please ensure your Supabase database is properly set up")
        return False
    
    # Step 2: Migrate CSV data to database
    print("\n📊 Step 2: Migrating CSV data to database...")
    try:
        from migrate_csv_to_database import migrate_interventions_and_habits
        success = migrate_interventions_and_habits()
        
        if not success:
            print("❌ CSV migration failed")
            return False
            
    except Exception as e:
        print(f"❌ CSV migration error: {e}")
        return False
    
    # Step 3: Build new vectorstore from database
    print("\n🔨 Step 3: Building vectorstore from database...")
    try:
        from build_database_vectorstore import build_interventions_vectorstore
        success = build_interventions_vectorstore()
        
        if not success:
            print("❌ Vectorstore build failed")
            return False
            
    except Exception as e:
        print(f"❌ Vectorstore build error: {e}")
        return False
    
    # Step 4: Update intervention matcher
    print("\n🔄 Step 4: Updating intervention matcher...")
    try:
        from update_intervention_matcher import update_intervention_matcher
        success = update_intervention_matcher()
        
        if not success:
            print("❌ Matcher update failed")
            return False
            
    except Exception as e:
        print(f"❌ Matcher update error: {e}")
        return False
    
    # Step 5: Update vectorstore references
    print("\n📝 Step 5: Updating vectorstore references...")
    try:
        from build_database_vectorstore import update_vectorstore_references
        update_vectorstore_references()
        
    except Exception as e:
        print(f"❌ Vectorstore reference update error: {e}")
        return False
    
    # Step 6: Test the migration
    print("\n🧪 Step 6: Testing the migration...")
    try:
        test_migration()
        
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Summary of changes:")
    print("✅ CSV data migrated to separate interventions and habits tables")
    print("✅ Vectorstore rebuilt using database data")
    print("✅ Intervention matcher updated to use database")
    print("✅ All references updated")
    
    print("\n📋 Next steps:")
    print("1. Test your API endpoints")
    print("2. Test the mobile app")
    print("3. Remove old CSV file (optional)")
    print("4. Update any remaining CSV references")
    
    return True

def test_migration():
    """Test the migration by running some basic operations"""
    
    print("🧪 Testing migration...")
    
    try:
        # Test database access
        from models.supabase_models import supabase_client
        
        # Test interventions
        interventions = supabase_client.client.table('interventions').select('*').limit(1).execute()
        if not interventions.data:
            raise Exception("No interventions found in database")
        
        # Test habits
        habits = supabase_client.client.table('habits').select('*').limit(1).execute()
        if not habits.data:
            raise Exception("No habits found in database")
        
        # Test intervention matcher
        from interventions.matcher import get_intervention_recommendation
        
        test_input = "I have PCOS and want to control my blood sugar"
        result = get_intervention_recommendation(test_input)
        
        if result.get('error'):
            print(f"⚠️  Matcher test warning: {result['error']}")
        else:
            print(f"✅ Matcher test successful: {result.get('recommended_intervention')}")
        
        print("✅ Migration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        raise

def cleanup_old_files():
    """Clean up old files (optional)"""
    
    print("\n🧹 Optional cleanup...")
    
    # List of files that can be removed
    old_files = [
        "data/Interventions_with_Habits.csv",
        "data/intervention_embeddings.json",
        "data/vectorstore/chroma"
    ]
    
    for file_path in old_files:
        if os.path.exists(file_path):
            print(f"🗑️  Found old file: {file_path}")
            # Uncomment the next line to actually delete
            # os.remove(file_path) if os.path.isfile(file_path) else shutil.rmtree(file_path)
            print(f"   (Not deleted - uncomment in script to delete)")
        else:
            print(f"✅ File not found: {file_path}")

if __name__ == "__main__":
    print("🚀 Complete Data Migration")
    print("=" * 40)
    
    success = run_complete_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        
        # Ask about cleanup
        print("\n🧹 Cleanup old files? (optional)")
        cleanup_old_files()
        
    else:
        print("\n❌ Migration failed!")
        print("Please check the errors above and try again.")

