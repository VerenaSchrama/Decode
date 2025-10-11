#!/usr/bin/env python3
"""
Populate InterventionsBASE and HabitsBASE tables from CSV data
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def populate_new_tables():
    """Populate new tables from CSV data"""
    
    print("🚀 Populating New Database Tables")
    print("=" * 50)
    
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
        
        # Clear existing data
        print("\n🧹 Clearing existing data...")
        try:
            supabase_client.client.table('HabitsBASE').delete().neq('Habit_ID', 0).execute()
            print("✅ Cleared HabitsBASE table")
        except Exception as e:
            print(f"⚠️  Could not clear HabitsBASE: {e}")
        
        try:
            supabase_client.client.table('InterventionsBASE').delete().neq('Intervention_ID', 0).execute()
            print("✅ Cleared InterventionsBASE table")
        except Exception as e:
            print(f"⚠️  Could not clear InterventionsBASE: {e}")
        
        # Populate InterventionsBASE
        print("\n📝 Populating InterventionsBASE...")
        interventions_data = []
        
        for _, row in df.iterrows():
            intervention = {
                'Intervention_ID': int(row['Intervention_ID']),
                'Strategy Name': row['Intervention'],
                'Clinical Background': row['Profile'],
                'What will you be doi...': f"Follow the {row['Intervention']} approach",
                'Show Sources': row['Scientific Source'],
                'Downloadable Sources': row['Scientific Source'],
                'Category Strategy': 'Nutritional Intervention',  # Default category
                'Symtpoms match': 'PCOS, Weight gain, Irregular cycles',  # Default symptoms
                'Persona fit (prior)': row['Profile'][:100] + "...",  # Truncated profile
                'Dietary fit (prior)': 'Flexible dietary approach',
                'Amount of movemen...': 'Moderate activity level'
            }
            interventions_data.append(intervention)
        
        # Insert interventions
        interventions_result = supabase_client.client.table('InterventionsBASE').insert(interventions_data).execute()
        print(f"✅ Inserted {len(interventions_result.data)} interventions")
        
        # Populate HabitsBASE
        print("\n📝 Populating HabitsBASE...")
        habits_data = []
        
        for _, row in df.iterrows():
            intervention_id = int(row['Intervention_ID'])
            
            # Create habits for this intervention
            habit_columns = ['Habit 1', 'Habit 2', 'Habit 3', 'Habit 4', 'Habit 5']
            habit_id = 1
            
            for habit_col in habit_columns:
                if pd.notna(row[habit_col]) and row[habit_col].strip():
                    habit = {
                        'Habit_ID': habit_id,
                        'Connects Interventio...': intervention_id,
                        'Habit Name': row[habit_col],
                        'What will you be doing': row[habit_col],
                        'Why does it work': f"Based on scientific evidence from {row['Scientific Source']}",
                        'What does that look l...': f"Practical implementation: {row[habit_col]}"
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
        
        # Check relationships
        print("\n🔗 Checking relationships...")
        for intervention in interventions_result.data:
            intervention_id = intervention['Intervention_ID']
            habits_for_intervention = supabase_client.client.table('HabitsBASE').select('*').eq('Connects Interventio...', intervention_id).execute()
            print(f"  📋 {intervention['Strategy Name']}: {len(habits_for_intervention.data)} habits")
        
        print("\n🎉 Database population completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Populate New Database Tables")
    print("=" * 40)
    
    success = populate_new_tables()
    
    if success:
        print("\n✅ Database population completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the intervention matcher")
        print("2. Test the API endpoints")
        print("3. Test the mobile app")
        
    else:
        print("\n❌ Database population failed!")
        print("Please check the errors above and try again.")

