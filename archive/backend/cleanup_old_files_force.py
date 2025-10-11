#!/usr/bin/env python3
"""
FORCE cleanup script - cleans up old files without database verification
Use this when you want to clean up files but can't verify database status
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def identify_files_to_delete_safe():
    """Identify files that can be safely deleted while preserving InFlo book vectorstore"""
    
    files_to_delete = []
    directories_to_delete = []
    
    # CSV files (after migration to database)
    csv_files = [
        "data/Interventions_with_Habits.csv",
        "data/Interventions_with_Habits_backup.csv"
    ]
    
    # JSON files (replaced by database)
    json_files = [
        "data/intervention_embeddings.json",  # Old intervention embeddings cache
        # Note: We keep chunks_AlisaVita.json as it's used by InFlo book vectorstore
    ]
    
    # OLD intervention vectorstore directories (NOT the InFlo book one)
    intervention_vectorstore_dirs = [
        "data/vectorstore/a8ecfef5-fb33-4bb2-9735-cdae1b01b063"  # This appears to be intervention-related
    ]
    
    # Check which files actually exist
    for file_path in csv_files + json_files:
        if os.path.exists(file_path):
            files_to_delete.append(file_path)
    
    for dir_path in intervention_vectorstore_dirs:
        if os.path.exists(dir_path):
            directories_to_delete.append(dir_path)
    
    return files_to_delete, directories_to_delete

def check_inflo_vectorstore_status():
    """Check if the InFlo book vectorstore is intact"""
    
    print("🔍 Checking InFlo book vectorstore status...")
    
    # Check if the main vectorstore directory exists
    main_vectorstore_path = "data/vectorstore/chroma"
    if not os.path.exists(main_vectorstore_path):
        print(f"❌ Main vectorstore directory missing: {main_vectorstore_path}")
        return False
    
    # Check if it has the expected structure
    expected_files = [
        "chroma.sqlite3",
        "74e63d79-1275-4585-9bef-4ff7ef971c7b/data_level0.bin",
        "74e63d79-1275-4585-9bef-4ff7ef971c7b/header.bin"
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = os.path.join(main_vectorstore_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Some InFlo vectorstore files missing: {missing_files}")
        return False
    
    print(f"✅ InFlo book vectorstore appears intact")
    return True

def create_cleanup_backup():
    """Create a backup of files before deletion"""
    
    backup_dir = "data/cleanup_backup"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_delete, directories_to_delete = identify_files_to_delete_safe()
    
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

def delete_old_files_safe():
    """Delete only the safe files, preserving InFlo book vectorstore"""
    
    files_to_delete, directories_to_delete = identify_files_to_delete_safe()
    
    print(f"\n🗑️  Deleting old files (preserving InFlo book vectorstore)...")
    
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

def verify_inflo_vectorstore_after_cleanup():
    """Verify that the InFlo book vectorstore still works after cleanup"""
    
    print(f"\n🧪 Testing InFlo book vectorstore after cleanup...")
    
    try:
        from retrievers.vectorstores import get_main_retriever, is_vectorstore_available
        
        if not is_vectorstore_available():
            print(f"❌ InFlo book vectorstore not available after cleanup!")
            return False
        
        retriever = get_main_retriever()
        if not retriever:
            print(f"❌ InFlo book retriever not available after cleanup!")
            return False
        
        # Test a simple query
        test_query = "menstrual cycle"
        docs = retriever.invoke(test_query)
        
        if docs and len(docs) > 0:
            print(f"✅ InFlo book vectorstore working! Found {len(docs)} documents for '{test_query}'")
            return True
        else:
            print(f"⚠️  InFlo book vectorstore returned no results for '{test_query}'")
            return False
            
    except Exception as e:
        print(f"❌ InFlo book vectorstore test failed: {e}")
        return False

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
    """Main force cleanup function"""
    
    print("🧹 FORCE Cleanup: Preserve InFlo Book Vectorstore")
    print("=" * 60)
    print("⚠️  WARNING: This will clean up files without database verification!")
    print("   Make sure you have run the database migration first.")
    
    # Check if InFlo vectorstore is intact
    print("\n🔍 Checking InFlo book vectorstore...")
    if not check_inflo_vectorstore_status():
        print("❌ InFlo book vectorstore is missing or corrupted!")
        print("   Please ensure the InFlo book vectorstore is properly built first.")
        return False
    
    print("✅ InFlo book vectorstore verified!")
    
    # Identify files to delete
    files_to_delete, directories_to_delete = identify_files_to_delete_safe()
    
    if not files_to_delete and not directories_to_delete:
        print("✅ No safe files found to clean up!")
        return True
    
    print(f"\n📋 Files to delete ({len(files_to_delete)} files):")
    for file_path in files_to_delete:
        print(f"   📄 {file_path}")
    
    print(f"\n📋 Directories to delete ({len(directories_to_delete)} directories):")
    for dir_path in directories_to_delete:
        print(f"   📁 {dir_path}")
    
    print(f"\n✅ Files that will be PRESERVED:")
    print(f"   📚 data/vectorstore/chroma/ (InFlo book vectorstore)")
    print(f"   📄 data/processed/chunks_AlisaVita.json (InFlo book chunks)")
    print(f"   📄 data/raw_book/InFloBook.pdf (Original PDF)")
    print(f"   📄 data/raw_book/InFloBook.txt (Extracted text)")
    print(f"   📄 data/inflo_phase_data.py (Phase data)")
    
    # Ask for confirmation
    print(f"\n⚠️  This will delete the above files while preserving InFlo book vectorstore!")
    print(f"   A backup will be created in data/cleanup_backup/")
    
    response = input("\nProceed with force cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    # Create backup
    create_cleanup_backup()
    
    # Delete files
    delete_old_files_safe()
    
    # Verify InFlo vectorstore still works
    if not verify_inflo_vectorstore_after_cleanup():
        print(f"\n❌ InFlo book vectorstore verification failed!")
        print(f"   You may need to restore from backup or rebuild the vectorstore")
        return False
    
    # Calculate space saved
    space_saved = calculate_space_saved()
    
    print(f"\n🎉 Force cleanup completed successfully!")
    print(f"\n📋 Summary:")
    print(f"   ✅ {len(files_to_delete)} files deleted")
    print(f"   ✅ {len(directories_to_delete)} directories deleted")
    print(f"   ✅ InFlo book vectorstore preserved and working")
    print(f"   💾 Space saved: {space_saved:.2f} MB")
    
    print(f"\n📋 What's preserved:")
    print(f"   📚 InFlo book vectorstore (for scientific context)")
    print(f"   📄 All InFlo book source files")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Run database migration: python complete_data_migration.py")
    print(f"   2. Test your API endpoints")
    print(f"   3. Test your mobile app")
    print(f"   4. Verify InFlo context is still working")
    print(f"   5. Remove backup directory if everything works: rm -rf data/cleanup_backup/")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)


