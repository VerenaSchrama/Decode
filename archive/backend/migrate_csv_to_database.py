#!/usr/bin/env python3
"""
Migration script to move from CSV-based data to database-based data
Splits Interventions_with_Habits.csv into separate interventions and habits tables
"""

import pandas as pd
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from models.supabase_models import supabase_client

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def clear_existing_data():
    """Clear existing interventions and habits data"""
    print("🗑️  Clearing existing data...")
    
    try:
        # Delete habits first (due to foreign key constraint)
        habits_result = supabase_client.client.table('habits').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Deleted existing habits")
        
        # Delete interventions
        interventions_result = supabase_client.client.table('interventions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print(f"✅ Deleted existing interventions")
        
    except Exception as e:
        print(f"⚠️  Error clearing data (might be empty): {e}")

def migrate_interventions_and_habits():
    """Migrate interventions and habits from CSV to separate database tables"""
    
    # Read the CSV file
    csv_path = "data/Interventions_with_Habits.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    print(f"📊 Loaded CSV with {len(df)} interventions")
    
    # Clear existing data
    clear_existing_data()
    
    print("🔄 Starting migration of interventions and habits...")
    
    # Migrate interventions
    interventions = []
    for _, row in df.iterrows():
        intervention_data = {
            'name': row['Intervention'],
            'profile': row['Profile'],
            'scientific_source': row['Scientific Source']
        }
        interventions.append(intervention_data)
    
    # Insert interventions
    print(f"📝 Inserting {len(interventions)} interventions...")
    try:
        interventions_result = supabase_client.client.table('interventions').insert(interventions).execute()
        print(f"✅ Inserted {len(interventions_result.data)} interventions")
    except Exception as e:
        print(f"❌ Failed to insert interventions: {e}")
        return False
    
    # Get the inserted interventions to map names to IDs
    interventions_map = {}
    for intervention in interventions_result.data:
        interventions_map[intervention['name']] = intervention['id']
    
    # Migrate habits
    habits = []
    habit_columns = ['Habit 1', 'Habit 2', 'Habit 3', 'Habit 4', 'Habit 5']
    
    for _, row in df.iterrows():
        intervention_id = interventions_map[row['Intervention']]
        
        for i, habit_col in enumerate(habit_columns, 1):
            if pd.notna(row[habit_col]) and row[habit_col].strip():
                habit_data = {
                    'name': row[habit_col],
                    'intervention_id': intervention_id,
                    'scientific_source': row['Scientific Source']
                }
                habits.append(habit_data)
                print(f"  📝 Added habit {i}: {row[habit_col][:50]}...")
    
    # Insert habits
    print(f"📝 Inserting {len(habits)} habits...")
    try:
        habits_result = supabase_client.client.table('habits').insert(habits).execute()
        print(f"✅ Inserted {len(habits_result.data)} habits")
    except Exception as e:
        print(f"❌ Failed to insert habits: {e}")
        return False
    
    # Verify the migration
    print("\n🔍 Verifying migration...")
    try:
        # Check interventions
        interventions_check = supabase_client.client.table('interventions').select('*').execute()
        print(f"✅ Interventions in database: {len(interventions_check.data)}")
        
        # Check habits
        habits_check = supabase_client.client.table('habits').select('*').execute()
        print(f"✅ Habits in database: {len(habits_check.data)}")
        
        # Check relationships
        for intervention in interventions_check.data:
            intervention_habits = supabase_client.client.table('habits').select('*').eq('intervention_id', intervention['id']).execute()
            print(f"  📋 {intervention['name']}: {len(intervention_habits.data)} habits")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    print("\n🎉 Migration completed successfully!")
    return True

def backup_csv():
    """Create a backup of the original CSV"""
    csv_path = "data/Interventions_with_Habits.csv"
    backup_path = "data/Interventions_with_Habits_backup.csv"
    
    if os.path.exists(csv_path):
        import shutil
        shutil.copy2(csv_path, backup_path)
        print(f"💾 Created backup: {backup_path}")

if __name__ == "__main__":
    print("🚀 CSV to Database Migration")
    print("=" * 50)
    
    # Create backup
    backup_csv()
    
    # Run migration
    success = migrate_interventions_and_habits()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📋 Next steps:")
        print("1. Update vectorstore to use database data")
        print("2. Update code references to use database instead of CSV")
        print("3. Test the complete system")
    else:
        print("\n❌ Migration failed!")
        print("Please check the errors above and try again.")
