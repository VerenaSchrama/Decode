"""
Migration script to populate Supabase with data from CSV files
"""

import pandas as pd
import os
from models.supabase_models import supabase_client
from dotenv import load_dotenv

load_dotenv()

def migrate_interventions_and_habits():
    """Migrate interventions and habits from CSV to Supabase"""
    
    # Read the CSV file
    csv_path = "data/Interventions_with_Habits.csv"
    df = pd.read_csv(csv_path)
    
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
    interventions_result = supabase_client.client.table('interventions').insert(interventions).execute()
    print(f"✅ Inserted {len(interventions_result.data)} interventions")
    
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
    habits_result = supabase_client.client.table('habits').insert(habits).execute()
    print(f"✅ Inserted {len(habits_result.data)} habits")
    
    print("🎉 Migration completed successfully!")
    return interventions_result.data, habits_result.data

def verify_migration():
    """Verify that the migration was successful"""
    
    print("\n🔍 Verifying migration...")
    
    # Check interventions
    interventions = supabase_client.get_interventions()
    print(f"📊 Total interventions in Supabase: {len(interventions.data)}")
    
    # Check habits
    habits = supabase_client.get_all_habits()
    print(f"📊 Total habits in Supabase: {len(habits.data)}")
    
    # Show sample data
    if interventions.data:
        print(f"\n📋 Sample intervention: {interventions.data[0]['name']}")
    
    if habits.data:
        print(f"📋 Sample habit: {habits.data[0]['name'][:50]}...")
    
    print("✅ Verification completed!")

def create_sample_user():
    """Create a sample user for testing"""
    
    print("\n👤 Creating sample user...")
    
    user_data = {
        'name': 'Test User',
        'age': 28,
        'email': 'test@example.com',
        'anonymous': False
    }
    
    result = supabase_client.create_user(user_data)
    print(f"✅ Created user: {result.data[0]['id']}")
    return result.data[0]

if __name__ == "__main__":
    try:
        # Migrate data
        interventions, habits = migrate_interventions_and_habits()
        
        # Verify migration
        verify_migration()
        
        # Create sample user
        sample_user = create_sample_user()
        
        print("\n🎉 Setup completed! You can now use Supabase with your health app.")
        print(f"📧 Sample user email: {sample_user['email']}")
        print(f"🆔 Sample user ID: {sample_user['id']}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("Please check your Supabase credentials and try again.")
