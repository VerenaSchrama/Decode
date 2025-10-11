#!/usr/bin/env python3
"""
Preview what files will be deleted during cleanup
Shows you exactly what will be removed before running the actual cleanup
"""

import os
from pathlib import Path

def preview_files_to_delete():
    """Preview all files that will be deleted"""
    
    print("🔍 Preview: Files to be deleted during cleanup")
    print("=" * 60)
    
    files_to_delete = []
    directories_to_delete = []
    
    # CSV files (after migration to database)
    csv_files = [
        "data/Interventions_with_Habits.csv",
        "data/Interventions_with_Habits_backup.csv"
    ]
    
    # JSON files (replaced by database)
    json_files = [
        "data/intervention_embeddings.json",
        "data/processed/chunks_AlisaVita.json"
    ]
    
    # Old vectorstore directories (replaced by database vectorstore)
    vectorstore_dirs = [
        "data/vectorstore/chroma",
        "data/vectorstore/a8ecfef5-fb33-4bb2-9735-cdae1b01b063"
    ]
    
    # Old vectorstore files
    vectorstore_files = [
        "data/vectorstore/chroma.sqlite3"
    ]
    
    # Check which files actually exist and get their sizes
    total_size = 0
    
    print("📄 Files to delete:")
    for file_path in csv_files + json_files + vectorstore_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            total_size += size
            files_to_delete.append(file_path)
            print(f"   ✅ {file_path} ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ {file_path} (not found)")
    
    print(f"\n📁 Directories to delete:")
    for dir_path in vectorstore_dirs:
        if os.path.exists(dir_path):
            # Calculate directory size
            dir_size = 0
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    dir_size += os.path.getsize(file_path)
            
            dir_size_mb = dir_size / (1024 * 1024)
            total_size += dir_size
            directories_to_delete.append(dir_path)
            print(f"   ✅ {dir_path} ({dir_size_mb:.2f} MB)")
        else:
            print(f"   ❌ {dir_path} (not found)")
    
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n📊 Summary:")
    print(f"   Files to delete: {len(files_to_delete)}")
    print(f"   Directories to delete: {len(directories_to_delete)}")
    print(f"   Total space to be freed: {total_size_mb:.2f} MB")
    
    # Check if new database vectorstore exists
    new_vectorstore_path = "data/vectorstore/database_chroma"
    if os.path.exists(new_vectorstore_path):
        print(f"\n✅ New database vectorstore exists: {new_vectorstore_path}")
    else:
        print(f"\n❌ New database vectorstore missing: {new_vectorstore_path}")
        print(f"   Run the migration first: python complete_data_migration.py")
    
    return files_to_delete, directories_to_delete, total_size_mb

def check_database_status():
    """Check if database has the migrated data"""
    
    print(f"\n🔍 Database Status Check:")
    print("=" * 30)
    
    try:
        from models.supabase_models import supabase_client
        
        # Check interventions
        interventions_result = supabase_client.client.table('interventions').select('count').execute()
        interventions_count = interventions_result.count if hasattr(interventions_result, 'count') else len(interventions_result.data) if interventions_result.data else 0
        print(f"   Interventions: {interventions_count} records")
        
        # Check habits
        habits_result = supabase_client.client.table('habits').select('count').execute()
        habits_count = habits_result.count if hasattr(habits_result, 'count') else len(habits_result.data) if habits_result.data else 0
        print(f"   Habits: {habits_count} records")
        
        if interventions_count > 0 and habits_count > 0:
            print(f"   ✅ Database migration successful!")
            return True
        else:
            print(f"   ❌ Database migration incomplete!")
            return False
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return False

def show_what_will_be_kept():
    """Show what files will be kept"""
    
    print(f"\n📋 Files that will be KEPT:")
    print("=" * 30)
    
    files_to_keep = [
        "data/raw_book/InFloBook.pdf",  # Original PDF
        "data/raw_book/InFloBook.txt",  # Extracted text
        "data/inflo_phase_data.py",     # Phase data (still needed)
        "data/vectorstore/database_chroma/",  # New database vectorstore
    ]
    
    for file_path in files_to_keep:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (not found)")

if __name__ == "__main__":
    print("🔍 Cleanup Preview")
    print("=" * 20)
    
    # Check database status first
    db_ready = check_database_status()
    
    if not db_ready:
        print(f"\n❌ Cannot proceed with cleanup - database migration not complete!")
        print(f"   Please run: python complete_data_migration.py")
        exit(1)
    
    # Preview files to delete
    files_to_delete, directories_to_delete, space_to_free = preview_files_to_delete()
    
    # Show what will be kept
    show_what_will_be_kept()
    
    if files_to_delete or directories_to_delete:
        print(f"\n🚀 Ready to clean up!")
        print(f"   Run: python cleanup_old_files.py")
    else:
        print(f"\n✅ No files to clean up!")


