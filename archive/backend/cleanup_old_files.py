#!/usr/bin/env python3
"""
Cleanup script to remove old CSV, JSON, and vectorstore files
that are no longer needed after migrating to Supabase database
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def identify_files_to_delete():
    """Identify all files that can be safely deleted"""
    
    files_to_delete = []
    directories_to_delete = []
    
    # CSV files (after migration to database)
    csv_files = [
        "data/Interventions_with_Habits.csv",
        "data/Interventions_with_Habits_backup.csv"  # Backup created during migration
    ]
    
    # JSON files (replaced by database)
    json_files = [
        "data/intervention_embeddings.json",  # Old embeddings cache
        "data/processed/chunks_AlisaVita.json"  # PDF chunks (if not needed)
    ]
    
    # Old vectorstore directories (replaced by database vectorstore)
    vectorstore_dirs = [
        "data/vectorstore/chroma",  # Old CSV-based vectorstore
        "data/vectorstore/a8ecfef5-fb33-4bb2-9735-cdae1b01b063"  # Old vectorstore collection
    ]
    
    # Old vectorstore files
    vectorstore_files = [
        "data/vectorstore/chroma.sqlite3"  # Old SQLite database
    ]
    
    # Check which files actually exist
    for file_path in csv_files + json_files + vectorstore_files:
        if os.path.exists(file_path):
            files_to_delete.append(file_path)
    
    for dir_path in vectorstore_dirs:
        if os.path.exists(dir_path):
            directories_to_delete.append(dir_path)
    
    return files_to_delete, directories_to_delete

def check_database_migration_status():
    """Check if the database migration has been completed successfully"""
    
    try:
        from models.supabase_models import supabase_client
        
        # Check if interventions table has data
        interventions_result = supabase_client.client.table('interventions').select('count').execute()
        interventions_count = interventions_result.count if hasattr(interventions_result, 'count') else len(interventions_result.data) if interventions_result.data else 0
        
        # Check if habits table has data
        habits_result = supabase_client.client.table('habits').select('count').execute()
        habits_count = habits_result.count if hasattr(habits_result, 'count') else len(habits_result.data) if habits_result.data else 0
        
        print(f"📊 Database status:")
        print(f"   Interventions: {interventions_count} records")
        print(f"   Habits: {habits_count} records")
        
        # Check if new database vectorstore exists
        new_vectorstore_path = "data/vectorstore/database_chroma"
        vectorstore_exists = os.path.exists(new_vectorstore_path)
        print(f"   New vectorstore: {'✅ Exists' if vectorstore_exists else '❌ Missing'}")
        
        return interventions_count > 0 and habits_count > 0 and vectorstore_exists
        
    except Exception as e:
        print(f"❌ Could not check database status: {e}")
        return False

def create_cleanup_backup():
    """Create a backup of files before deletion"""
    
    backup_dir = "data/cleanup_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_delete, directories_to_delete = identify_files_to_delete()
    
    print(f"💾 Creating backup in {backup_dir}...")
    
    # Backup files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"   📄 Backed up: {file_path}")
    
    # Backup directories
    for dir_path in directories_to_delete:
        if os.path.exists(dir_path):
            backup_path = os.path.join(backup_dir, os.path.basename(dir_path))
            shutil.copytree(dir_path, backup_path)
            print(f"   📁 Backed up: {dir_path}")
    
    print(f"✅ Backup created in {backup_dir}")

def delete_old_files():
    """Delete the old files and directories"""
    
    files_to_delete, directories_to_delete = identify_files_to_delete()
    
    print(f"\n🗑️  Deleting old files...")
    
    # Delete files
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"   ✅ Deleted file: {file_path}")
        except Exception as e:
            print(f"   ❌ Failed to delete {file_path}: {e}")
    
    # Delete directories
    for dir_path in directories_to_delete:
        try:
            shutil.rmtree(dir_path)
            print(f"   ✅ Deleted directory: {dir_path}")
        except Exception as e:
            print(f"   ❌ Failed to delete {dir_path}: {e}")

def update_code_references():
    """Update any remaining code references to old files"""
    
    print(f"\n📝 Updating code references...")
    
    # Files that might reference old paths
    files_to_update = [
        "interventions/matcher.py",
        "retrievers/vectorstores.py",
        "build_science_vectorstore.py"
    ]
    
    updates_made = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Update CSV references
                content = content.replace('data/Interventions_with_Habits.csv', 'data/cleanup_backup/Interventions_with_Habits.csv')
                content = content.replace('Interventions_with_Habits.csv', 'Interventions_with_Habits_backup.csv')
                
                # Update old vectorstore paths
                content = content.replace('data/vectorstore/chroma', 'data/vectorstore/database_chroma')
                content = content.replace('data/processed/chunks_AlisaVita.json', 'data/cleanup_backup/chunks_AlisaVita.json')
                
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    print(f"   ✅ Updated: {file_path}")
                    updates_made += 1
                else:
                    print(f"   ⚠️  No changes needed: {file_path}")
                    
            except Exception as e:
                print(f"   ❌ Failed to update {file_path}: {e}")
    
    print(f"📝 Updated {updates_made} files")

def verify_cleanup():
    """Verify that the cleanup was successful"""
    
    print(f"\n🔍 Verifying cleanup...")
    
    files_to_delete, directories_to_delete = identify_files_to_delete()
    
    still_exists = []
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            still_exists.append(file_path)
    
    for dir_path in directories_to_delete:
        if os.path.exists(dir_path):
            still_exists.append(dir_path)
    
    if still_exists:
        print(f"⚠️  Some files still exist:")
        for item in still_exists:
            print(f"   - {item}")
        return False
    else:
        print(f"✅ All old files successfully removed!")
        return True

def calculate_space_saved():
    """Calculate how much disk space was saved"""
    
    backup_dir = "data/cleanup_backup"
    if not os.path.exists(backup_dir):
        return 0
    
    total_size = 0
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    
    # Convert to MB
    size_mb = total_size / (1024 * 1024)
    return size_mb

def main():
    """Main cleanup function"""
    
    print("🧹 Cleanup Old Files: CSV → Database Migration")
    print("=" * 60)
    
    # Check if migration was completed
    print("🔍 Checking migration status...")
    if not check_database_migration_status():
        print("❌ Database migration not completed or failed!")
        print("Please run the migration first: python complete_data_migration.py")
        return False
    
    print("✅ Database migration verified!")
    
    # Identify files to delete
    files_to_delete, directories_to_delete = identify_files_to_delete()
    
    if not files_to_delete and not directories_to_delete:
        print("✅ No old files found to clean up!")
        return True
    
    print(f"\n📋 Files to delete ({len(files_to_delete)} files):")
    for file_path in files_to_delete:
        print(f"   📄 {file_path}")
    
    print(f"\n📋 Directories to delete ({len(directories_to_delete)} directories):")
    for dir_path in directories_to_delete:
        print(f"   📁 {dir_path}")
    
    # Ask for confirmation
    print(f"\n⚠️  This will permanently delete the above files and directories!")
    print(f"   A backup will be created in data/cleanup_backup/")
    
    response = input("\nProceed with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    # Create backup
    create_cleanup_backup()
    
    # Delete files
    delete_old_files()
    
    # Update code references
    update_code_references()
    
    # Verify cleanup
    if verify_cleanup():
        # Calculate space saved
        space_saved = calculate_space_saved()
        print(f"\n💾 Space saved: {space_saved:.2f} MB")
        
        print(f"\n🎉 Cleanup completed successfully!")
        print(f"\n📋 Summary:")
        print(f"   ✅ {len(files_to_delete)} files deleted")
        print(f"   ✅ {len(directories_to_delete)} directories deleted")
        print(f"   ✅ Code references updated")
        print(f"   ✅ Backup created in data/cleanup_backup/")
        print(f"   💾 Space saved: {space_saved:.2f} MB")
        
        print(f"\n📋 Next steps:")
        print(f"   1. Test your API endpoints")
        print(f"   2. Test your mobile app")
        print(f"   3. Remove backup directory if everything works: rm -rf data/cleanup_backup/")
        
        return True
    else:
        print(f"\n❌ Cleanup verification failed!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)


