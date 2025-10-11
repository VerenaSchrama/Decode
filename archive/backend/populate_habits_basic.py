#!/usr/bin/env python3
"""
Populate habits with basic columns only
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def populate_habits_basic():
    """Populate habits with basic columns only"""
    
    print("🚀 Populate Habits - Basic Columns")
    print("=" * 40)
    
    try:
        from models.supabase_models import supabase_client
        
        # Check if CSV file exists
        csv_file = "data/cleanup_backup/Interventions_with_Habits.csv"
        if not os.path.exists(csv_file):
            print(f"❌ CSV file not found: {csv_file}")
            return False
        
        # Load CSV data
        print("📊 Loading CSV data...")
        df = pd.read_csv(csv_file)
        print(f"✅ Loaded {len(df)} interventions from CSV")
        
        # Clear existing habits
        print("\n🧹 Clearing existing habits...")
        try:
            supabase_client.client.table('HabitsBASE').delete().neq('Habit_ID', 0).execute()
            print("✅ Cleared HabitsBASE table")
        except Exception as e:
            print(f"⚠️  Could not clear HabitsBASE: {e}")
        
        # Insert habits with basic columns only
        print("\n📝 Inserting habits with basic columns...")
        habits_data = []
        habit_id = 1
        
        for _, row in df.iterrows():
            intervention_id = int(row['Intervention_ID'])
            
            # Create habits for this intervention
            habit_columns = ['Habit 1', 'Habit 2', 'Habit 3', 'Habit 4', 'Habit 5']
            
            for habit_col in habit_columns:
                if pd.notna(row[habit_col]) and row[habit_col].strip():
                    habit = {
                        'Habit_ID': habit_id,
                        'Habit Name': row[habit_col]
                    }
                    habits_data.append(habit)
                    habit_id += 1
        
        # Insert habits
        habits_result = supabase_client.client.table('HabitsBASE').insert(habits_data).execute()
        print(f"✅ Inserted {len(habits_result.data)} habits")
        
        # Verify the data
        print("\n🔍 Verifying data...")
        
        # Check InterventionsBASE
        interventions_check = supabase_client.client.table('InterventionsBASE').select('count').execute()
        print(f"✅ InterventionsBASE: {interventions_check.count} records")
        
        # Check HabitsBASE
        habits_check = supabase_client.client.table('HabitsBASE').select('count').execute()
        print(f"✅ HabitsBASE: {habits_check.count} records")
        
        # Show sample data
        print("\n📋 Sample intervention:")
        sample_intervention = supabase_client.client.table('InterventionsBASE').select('*').limit(1).execute()
        if sample_intervention.data:
            for key, value in sample_intervention.data[0].items():
                print(f"  {key}: {str(value)[:50]}...")
        
        print("\n📋 Sample habit:")
        sample_habit = supabase_client.client.table('HabitsBASE').select('*').limit(1).execute()
        if sample_habit.data:
            for key, value in sample_habit.data[0].items():
                print(f"  {key}: {str(value)[:50]}...")
        
        print("\n🎉 Database population completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Populate Habits - Basic Columns")
    print("=" * 40)
    
    success = populate_habits_basic()
    
    if success:
        print("\n✅ Database population completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the intervention matcher")
        print("2. Test the API endpoints")
        print("3. Test the mobile app")
        
    else:
        print("\n❌ Database population failed!")
        print("Please check the errors above and try again.")

