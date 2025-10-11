#!/usr/bin/env python3
"""
Simple population script using exact column names from database schema
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def populate_simple():
    """Populate tables with simple data"""
    
    print("🚀 Simple Database Population")
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
        
        # Try to insert one intervention first to test
        print("\n🧪 Testing with one intervention...")
        
        # Use the exact column names from your database schema
        test_intervention = {
            'Intervention_ID': 1,
            'Strategy Name': 'Control your blood sugar',
            'Clinical Background': 'Woman with PCOS, insulin resistance, irregular or absent cycles, fatigue, mood swings, weight struggles, or afternoon energy crashes.',
            'What will you be doi...': 'Follow the blood sugar control approach',
            'Show Sources': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11339140/',
            'Downloadable Sources': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11339140/',
            'Category Strategy': 'Blood Sugar Control',
            'Symtpoms match': 'PCOS, Weight gain, Irregular cycles',
            'Persona fit (prior)': 'Woman with PCOS, insulin resistance...',
            'Dietary fit (prior)': 'Flexible dietary approach',
            'Amount of movemen...': 'Moderate activity level'
        }
        
        try:
            result = supabase_client.client.table('InterventionsBASE').insert([test_intervention]).execute()
            print(f"✅ Test insert successful: {len(result.data)} records")
            
            # Now insert all interventions
            print("\n📝 Inserting all interventions...")
            interventions_data = []
            
            for _, row in df.iterrows():
                intervention = {
                    'Intervention_ID': int(row['Intervention_ID']),
                    'Strategy Name': row['Intervention'],
                    'Clinical Background': row['Profile'],
                    'What will you be doi...': f"Follow the {row['Intervention']} approach",
                    'Show Sources': row['Scientific Source'],
                    'Downloadable Sources': row['Scientific Source'],
                    'Category Strategy': 'Nutritional Intervention',
                    'Symtpoms match': 'PCOS, Weight gain, Irregular cycles',
                    'Persona fit (prior)': row['Profile'][:100] + "...",
                    'Dietary fit (prior)': 'Flexible dietary approach',
                    'Amount of movemen...': 'Moderate activity level'
                }
                interventions_data.append(intervention)
            
            # Insert all interventions
            interventions_result = supabase_client.client.table('InterventionsBASE').insert(interventions_data).execute()
            print(f"✅ Inserted {len(interventions_result.data)} interventions")
            
            # Now insert habits
            print("\n📝 Inserting habits...")
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
            
            print("\n🎉 Database population completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Insert failed: {e}")
            
            # Try to get the actual table schema
            print("\n🔍 Trying to get table schema...")
            try:
                # Try a simple select to see what columns exist
                result = supabase_client.client.table('InterventionsBASE').select('*').limit(0).execute()
                print("Table exists but no data")
            except Exception as e2:
                print(f"Schema error: {e2}")
            
            return False
        
    except Exception as e:
        print(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple Database Population")
    print("=" * 40)
    
    success = populate_simple()
    
    if success:
        print("\n✅ Database population completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the intervention matcher")
        print("2. Test the API endpoints")
        print("3. Test the mobile app")
        
    else:
        print("\n❌ Database population failed!")
        print("Please check the errors above and try again.")

