#!/usr/bin/env python3
"""
Simple check of the current database state
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def check_database_simple():
    """Simple check of database tables"""
    
    print("🔍 Simple Database Check")
    print("=" * 30)
    
    try:
        from models.supabase_models import supabase_client
        
        # Check InterventionsBASE table directly
        print("\n📊 InterventionsBASE Table:")
        try:
            result = supabase_client.client.table('InterventionsBASE').select('*').execute()
            print(f"✅ Records: {len(result.data)}")
            
            if result.data:
                print("📋 Sample records:")
                for i, intervention in enumerate(result.data[:3]):
                    print(f"  {i+1}. ID: {intervention.get('Intervention_ID')} - {intervention.get('Strategy Name', 'N/A')}")
        except Exception as e:
            print(f"❌ Error accessing InterventionsBASE: {e}")
        
        # Check HabitsBASE table directly
        print("\n📊 HabitsBASE Table:")
        try:
            result = supabase_client.client.table('HabitsBASE').select('*').execute()
            print(f"✅ Records: {len(result.data)}")
            
            if result.data:
                print("📋 Sample records:")
                for i, habit in enumerate(result.data[:3]):
                    print(f"  {i+1}. ID: {habit.get('Habit_ID')} - {habit.get('Habit Name', 'N/A')}")
        except Exception as e:
            print(f"❌ Error accessing HabitsBASE: {e}")
        
        # Check old interventions table
        print("\n📊 Old Interventions Table:")
        try:
            result = supabase_client.client.table('interventions').select('*').execute()
            print(f"✅ Records: {len(result.data)}")
        except Exception as e:
            print(f"❌ Error accessing old interventions table: {e}")
        
        # Check old habits table
        print("\n📊 Old Habits Table:")
        try:
            result = supabase_client.client.table('habits').select('*').execute()
            print(f"✅ Records: {len(result.data)}")
        except Exception as e:
            print(f"❌ Error accessing old habits table: {e}")
        
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("This might be due to missing environment variables or network issues.")

if __name__ == "__main__":
    check_database_simple()


