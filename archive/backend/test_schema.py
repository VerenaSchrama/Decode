#!/usr/bin/env python3
"""
Test script to discover the actual database schema
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_schema():
    """Test different column combinations to find the correct schema"""
    
    print("🔍 Testing Database Schema")
    print("=" * 40)
    
    try:
        from models.supabase_models import supabase_client
        
        # Test 1: Minimal columns
        print("\n🧪 Test 1: Minimal columns")
        try:
            test_data = {
                'Intervention_ID': 999,
                'Strategy Name': 'Test Intervention'
            }
            result = supabase_client.client.table('InterventionsBASE').insert([test_data]).execute()
            print("✅ Minimal columns work")
            print("Columns that work: Intervention_ID, Strategy Name")
        except Exception as e:
            print(f"❌ Minimal columns failed: {e}")
        
        # Test 2: Add Clinical Background
        print("\n🧪 Test 2: Add Clinical Background")
        try:
            test_data = {
                'Intervention_ID': 998,
                'Strategy Name': 'Test Intervention 2',
                'Clinical Background': 'Test background'
            }
            result = supabase_client.client.table('InterventionsBASE').insert([test_data]).execute()
            print("✅ Clinical Background works")
        except Exception as e:
            print(f"❌ Clinical Background failed: {e}")
        
        # Test 3: Add more columns one by one
        columns_to_test = [
            'What will you be doi...',
            'Show Sources',
            'Downloadable Sources',
            'Category Strategy',
            'Symtpoms match',
            'Persona fit (prior)',
            'Dietary fit (prior)',
            'Amount of movemen...',
            'Amount of movement',
            'Movement Amount',
            'Movement_Amount'
        ]
        
        working_columns = ['Intervention_ID', 'Strategy Name', 'Clinical Background']
        
        for col in columns_to_test:
            print(f"\n🧪 Testing column: {col}")
            try:
                test_data = {
                    'Intervention_ID': 997,
                    'Strategy Name': 'Test Intervention 3',
                    'Clinical Background': 'Test background',
                    col: 'Test value'
                }
                result = supabase_client.client.table('InterventionsBASE').insert([test_data]).execute()
                print(f"✅ {col} works")
                working_columns.append(col)
            except Exception as e:
                print(f"❌ {col} failed: {e}")
        
        print(f"\n📋 Working columns: {working_columns}")
        
        # Test HabitsBASE
        print("\n🧪 Testing HabitsBASE schema")
        try:
            test_habit = {
                'Habit_ID': 999,
                'Connects Interventio...': 999,
                'Habit Name': 'Test Habit'
            }
            result = supabase_client.client.table('HabitsBASE').insert([test_habit]).execute()
            print("✅ Basic habit columns work")
        except Exception as e:
            print(f"❌ Basic habit columns failed: {e}")
        
        return working_columns
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("🚀 Database Schema Discovery")
    print("=" * 40)
    
    working_columns = test_schema()
    
    if working_columns:
        print(f"\n✅ Found working columns: {working_columns}")
    else:
        print("\n❌ Could not determine working columns")

