#!/usr/bin/env python3
"""
Populate database with minimal working columns
"""

import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def populate_minimal():
    """Populate tables with minimal working columns"""
    
    print("🚀 Minimal Database Population")
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
        
        # Clear existing data first
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
        
        # Test with minimal columns first
        print("\n🧪 Testing minimal columns...")
        test_intervention = {
            'Intervention_ID': 1,
            'Strategy Name': 'Control your blood sugar',
            'Clinical Background': 'Woman with PCOS, insulin resistance, irregular or absent cycles, fatigue, mood swings, weight struggles, or afternoon energy crashes.'
        }
        
        try:
            result = supabase_client.client.table('InterventionsBASE').insert([test_intervention]).execute()
            print("✅ Minimal columns work!")
            
            # Now insert all interventions with minimal columns
            print("\n📝 Inserting all interventions with minimal columns...")
            interventions_data = []
            
            for _, row in df.iterrows():
                intervention = {
                    'Intervention_ID': int(row['Intervention_ID']),
                    'Strategy Name': row['Intervention'],
                    'Clinical Background': row['Profile']
                }
                interventions_data.append(intervention)
            
            # Insert all interventions
            interventions_result = supabase_client.client.table('InterventionsBASE').insert(interventions_data).execute()
            print(f"✅ Inserted {len(interventions_result.data)} interventions")
            
            # Now try to add more columns one by one
            print("\n🔧 Trying to add additional columns...")
            
            # Test additional columns
            additional_columns = {
                'Show Sources': 'Scientific Source',
                'Downloadable Sources': 'Scientific Source',
                'Category Strategy': 'Nutritional Intervention',
                'Symtpoms match': 'PCOS, Weight gain, Irregular cycles',
                'Persona fit (prior)': lambda x: x['Profile'][:100] + "...",
                'Dietary fit (prior)': 'Flexible dietary approach'
            }
            
            working_additional_columns = {}
            
            for col_name, col_value in additional_columns.items():
                print(f"  Testing column: {col_name}")
                try:
                    test_data = {
                        'Intervention_ID': 999,
                        'Strategy Name': 'Test',
                        'Clinical Background': 'Test',
                        col_name: col_value if isinstance(col_value, str) else col_value({'Profile': 'Test profile'})
                    }
                    result = supabase_client.client.table('InterventionsBASE').insert([test_data]).execute()
                    print(f"    ✅ {col_name} works")
                    working_additional_columns[col_name] = col_value
                except Exception as e:
                    print(f"    ❌ {col_name} failed: {e}")
            
            # Update existing interventions with working additional columns
            if working_additional_columns:
                print(f"\n📝 Updating interventions with {len(working_additional_columns)} additional columns...")
                
                for intervention in interventions_result.data:
                    intervention_id = intervention['Intervention_ID']
                    update_data = {}
                    
                    for col_name, col_value in working_additional_columns.items():
                        if col_name == 'Show Sources' or col_name == 'Downloadable Sources':
                            update_data[col_name] = df[df['Intervention_ID'] == intervention_id]['Scientific Source'].iloc[0]
                        elif col_name == 'Persona fit (prior)':
                            update_data[col_name] = df[df['Intervention_ID'] == intervention_id]['Profile'].iloc[0][:100] + "..."
                        else:
                            update_data[col_name] = col_value
                    
                    try:
                        supabase_client.client.table('InterventionsBASE').update(update_data).eq('Intervention_ID', intervention_id).execute()
                    except Exception as e:
                        print(f"    ⚠️  Could not update intervention {intervention_id}: {e}")
            
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
                            'Habit Name': row[habit_col]
                        }
                        
                        # Try to add the foreign key column with different possible names
                        foreign_key_names = [
                            'Connects Interventio...',
                            'Connects Intervention',
                            'Intervention_ID',
                            'intervention_id'
                        ]
                        
                        for fk_name in foreign_key_names:
                            try:
                                habit[fk_name] = intervention_id
                                break
                            except:
                                pass
                        
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
            sample = supabase_client.client.table('InterventionsBASE').select('*').limit(1).execute()
            if sample.data:
                for key, value in sample.data[0].items():
                    print(f"  {key}: {str(value)[:50]}...")
            
            print("\n🎉 Database population completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Population failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Minimal Database Population")
    print("=" * 40)
    
    success = populate_minimal()
    
    if success:
        print("\n✅ Database population completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test the intervention matcher")
        print("2. Test the API endpoints")
        print("3. Test the mobile app")
        
    else:
        print("\n❌ Database population failed!")
        print("Please check the errors above and try again.")

