#!/usr/bin/env python3
"""
Migration script to populate the new InterventionsBASE and HabitsBASE tables
from the existing interventions and habits tables
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.supabase_models import supabase_client

load_dotenv()

def migrate_to_new_schema():
    """Migrate from old schema to new InterventionsBASE and HabitsBASE tables"""
    
    print("🔄 Migrating to new InterventionsBASE and HabitsBASE schema...")
    
    try:
        # Get existing interventions data
        print("📊 Loading existing interventions...")
        interventions_result = supabase_client.client.table('interventions').select('*').execute()
        
        if not interventions_result.data:
            print("❌ No interventions found in existing table")
            return False
        
        print(f"✅ Found {len(interventions_result.data)} interventions")
        
        # Get existing habits data
        print("📊 Loading existing habits...")
        habits_result = supabase_client.client.table('habits').select('*').execute()
        
        if not habits_result.data:
            print("❌ No habits found in existing table")
            return False
        
        print(f"✅ Found {len(habits_result.data)} habits")
        
        # Migrate interventions to InterventionsBASE
        print("\n📝 Migrating interventions to InterventionsBASE...")
        interventions_base_data = []
        
        for intervention in interventions_result.data:
            # Map old schema to new schema
            intervention_base = {
                'Strategy Name': intervention['name'],
                'Clinical Background': intervention['profile'],
                'What will you be doi...': f"Follow the {intervention['name']} approach",
                'Show Sources': intervention['scientific_source'],
                'Downloadable Sources': intervention['scientific_source'],
                'Category Strategy': 'Nutritional Intervention',  # Default category
                'Symtpoms match': 'PCOS, Weight gain, Irregular cycles',  # Default symptoms
                'Persona fit (prior)': intervention['profile'][:100] + "...",  # Truncated profile
                'Dietary fit (prior)': 'Flexible dietary approach',
                'Amount of movemen...': 'Moderate activity level'
            }
            interventions_base_data.append(intervention_base)
        
        # Insert into InterventionsBASE table
        try:
            interventions_base_result = supabase_client.client.table('InterventionsBASE').insert(interventions_base_data).execute()
            print(f"✅ Inserted {len(interventions_base_result.data)} interventions into InterventionsBASE")
        except Exception as e:
            print(f"❌ Failed to insert into InterventionsBASE: {e}")
            return False
        
        # Create mapping from old intervention IDs to new Intervention_IDs
        intervention_id_mapping = {}
        for i, old_intervention in enumerate(interventions_result.data):
            new_intervention_id = interventions_base_result.data[i]['Intervention_ID']
            old_intervention_id = old_intervention['id']
            intervention_id_mapping[old_intervention_id] = new_intervention_id
        
        # Migrate habits to HabitsBASE
        print("\n📝 Migrating habits to HabitsBASE...")
        habits_base_data = []
        
        for habit in habits_result.data:
            # Get the new intervention ID
            old_intervention_id = habit['intervention_id']
            new_intervention_id = intervention_id_mapping.get(old_intervention_id)
            
            if not new_intervention_id:
                print(f"⚠️  Could not find mapping for intervention {old_intervention_id}")
                continue
            
            # Map old schema to new schema
            habit_base = {
                'Connects Interventio...': new_intervention_id,  # Foreign key
                'Habit Name': habit['name'],
                'What will you be doing': habit['name'],
                'Why does it work': f"Based on scientific evidence from {habit['scientific_source']}",
                'What does that look l...': f"Practical implementation: {habit['name']}"
            }
            habits_base_data.append(habit_base)
        
        # Insert into HabitsBASE table
        try:
            habits_base_result = supabase_client.client.table('HabitsBASE').insert(habits_base_data).execute()
            print(f"✅ Inserted {len(habits_base_result.data)} habits into HabitsBASE")
        except Exception as e:
            print(f"❌ Failed to insert into HabitsBASE: {e}")
            return False
        
        # Verify the migration
        print("\n🔍 Verifying migration...")
        
        # Check InterventionsBASE
        interventions_base_check = supabase_client.client.table('InterventionsBASE').select('count').execute()
        print(f"✅ InterventionsBASE: {interventions_base_check.count} records")
        
        # Check HabitsBASE
        habits_base_check = supabase_client.client.table('HabitsBASE').select('count').execute()
        print(f"✅ HabitsBASE: {habits_base_check.count} records")
        
        # Check relationships
        for intervention in interventions_base_result.data:
            intervention_id = intervention['Intervention_ID']
            habits_for_intervention = supabase_client.client.table('HabitsBASE').select('*').eq('Connects Interventio...', intervention_id).execute()
            print(f"  📋 {intervention['Strategy Name']}: {len(habits_for_intervention.data)} habits")
        
        print("\n🎉 Migration to new schema completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_new_schema_tables():
    """Create the new InterventionsBASE and HabitsBASE tables if they don't exist"""
    
    print("🏗️  Creating new schema tables...")
    
    # SQL to create the tables
    create_interventions_sql = """
    CREATE TABLE IF NOT EXISTS "InterventionsBASE" (
        "Intervention_ID" int8 NOT NULL PRIMARY KEY,
        "Strategy Name" text,
        "Clinical Background" text,
        "What will you be doi..." text,
        "Show Sources" text,
        "Downloadable Sources" text,
        "Category Strategy" text,
        "Symtpoms match" text,
        "Persona fit (prior)" text,
        "Dietary fit (prior)" text,
        "Amount of movemen..." text
    );
    """
    
    create_habits_sql = """
    CREATE TABLE IF NOT EXISTS "HabitsBASE" (
        "Habit_ID" int8 NOT NULL PRIMARY KEY,
        "Connects Interventio..." int8,
        "Habit Name" text,
        "What will you be doing" text,
        "Why does it work" text,
        "What does that look l..." text,
        FOREIGN KEY ("Connects Interventio...") REFERENCES "InterventionsBASE"("Intervention_ID")
    );
    """
    
    try:
        # Execute the SQL
        supabase_client.client.rpc('exec_sql', {'sql': create_interventions_sql}).execute()
        print("✅ Created InterventionsBASE table")
        
        supabase_client.client.rpc('exec_sql', {'sql': create_habits_sql}).execute()
        print("✅ Created HabitsBASE table")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        print("Please create the tables manually in your Supabase dashboard")
        return False

if __name__ == "__main__":
    print("🚀 Migration to New Database Schema")
    print("=" * 50)
    
    # Create tables first
    if not create_new_schema_tables():
        print("❌ Failed to create tables. Please create them manually.")
        exit(1)
    
    # Run migration
    success = migrate_to_new_schema()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📋 Next steps:")
        print("1. Update Supabase models to work with new tables")
        print("2. Update intervention matcher")
        print("3. Update API endpoints")
        print("4. Test the complete system")
    else:
        print("\n❌ Migration failed!")
        print("Please check the errors above and try again.")


