#!/usr/bin/env python3
"""
Check the current state of the Supabase database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def check_database_status():
    """Check the current state of all database tables"""
    
    print("🔍 Checking Current Database Status")
    print("=" * 50)
    
    try:
        from models.supabase_models import supabase_client
        
        # Check InterventionsBASE table
        print("\n📊 InterventionsBASE Table:")
        try:
            interventions_base = supabase_client.get_interventions_base()
            print(f"✅ Records: {len(interventions_base.data)}")
            
            if interventions_base.data:
                print("📋 Sample records:")
                for i, intervention in enumerate(interventions_base.data[:3]):
                    print(f"  {i+1}. ID: {intervention.get('Intervention_ID')} - {intervention.get('Strategy Name', 'N/A')}")
        except Exception as e:
            print(f"❌ Error accessing InterventionsBASE: {e}")
        
        # Check HabitsBASE table
        print("\n📊 HabitsBASE Table:")
        try:
            habits_base = supabase_client.get_habits_base()
            print(f"✅ Records: {len(habits_base.data)}")
            
            if habits_base.data:
                print("📋 Sample records:")
                for i, habit in enumerate(habits_base.data[:3]):
                    print(f"  {i+1}. ID: {habit.get('Habit_ID')} - {habit.get('Habit Name', 'N/A')}")
        except Exception as e:
            print(f"❌ Error accessing HabitsBASE: {e}")
        
        # Check old interventions table (if exists)
        print("\n📊 Old Interventions Table:")
        try:
            old_interventions = supabase_client.client.table('interventions').select('*').execute()
            print(f"✅ Records: {len(old_interventions.data)}")
        except Exception as e:
            print(f"❌ Error accessing old interventions table: {e}")
        
        # Check old habits table (if exists)
        print("\n📊 Old Habits Table:")
        try:
            old_habits = supabase_client.client.table('habits').select('*').execute()
            print(f"✅ Records: {len(old_habits.data)}")
        except Exception as e:
            print(f"❌ Error accessing old habits table: {e}")
        
        # Check relationships
        print("\n🔗 Relationships:")
        try:
            interventions_with_habits = supabase_client.get_all_interventions_with_habits()
            print(f"✅ Interventions with habits: {len(interventions_with_habits)}")
            
            for intervention_data in interventions_with_habits[:3]:
                intervention = intervention_data['intervention']
                habits = intervention_data['habits']
                print(f"  - {intervention.get('Strategy Name', 'N/A')}: {len(habits)} habits")
        except Exception as e:
            print(f"❌ Error checking relationships: {e}")
        
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    check_database_status()


