#!/usr/bin/env python3
"""
Get exact column names from HabitsBASE table
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def get_table_columns(table_name):
    print(f"🔍 Getting columns for table: {table_name}")
    try:
        from models.supabase_models import supabase_client
        
        result = supabase_client.client.table(table_name).select('*').limit(1).execute()
        
        if result.data:
            print(f"✅ Found columns for {table_name}:")
            for key in result.data[0].keys():
                print(f"  - {key}")
            return list(result.data[0].keys())
        else:
            print(f"No data in {table_name} table to infer columns.")
            return []
    except Exception as e:
        print(f"❌ Error getting columns for {table_name}: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Getting Exact Column Names")
    print("=" * 40)
    
    # Get columns for both tables
    interventions_columns = get_table_columns('InterventionsBASE')
    habits_columns = get_table_columns('HabitsBASE')
    
    print(f"\n📊 Summary:")
    print(f"InterventionsBASE: {len(interventions_columns)} columns")
    print(f"HabitsBASE: {len(habits_columns)} columns")
    
    # Look for foreign key column
    print(f"\n🔗 Looking for foreign key column in HabitsBASE:")
    for col in habits_columns:
        if 'interventio' in col.lower() or 'intervention' in col.lower():
            print(f"  ✅ Found potential foreign key: {col}")
        elif 'connects' in col.lower():
            print(f"  ✅ Found potential foreign key: {col}")

