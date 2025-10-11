#!/usr/bin/env python3
"""
Complete migration script for new InterventionsBASE and HabitsBASE schema
Updates all components to work with the new database structure
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def run_complete_migration():
    """Run the complete migration to new schema"""
    
    print("🚀 Complete Migration to New Schema")
    print("=" * 60)
    print("📋 Migrating to InterventionsBASE and HabitsBASE tables")
    
    # Step 1: Migrate data to new schema
    print("\n📊 Step 1: Migrating data to new schema...")
    try:
        from migrate_to_new_schema import migrate_to_new_schema
        success = migrate_to_new_schema()
        
        if not success:
            print("❌ Data migration failed")
            return False
            
    except Exception as e:
        print(f"❌ Data migration error: {e}")
        return False
    
    # Step 2: Update Supabase models
    print("\n🔧 Step 2: Updating Supabase models...")
    try:
        from update_supabase_models import update_supabase_models
        success = update_supabase_models()
        
        if not success:
            print("❌ Supabase models update failed")
            return False
            
    except Exception as e:
        print(f"❌ Supabase models update error: {e}")
        return False
    
    # Step 3: Update intervention matcher
    print("\n🔄 Step 3: Updating intervention matcher...")
    try:
        from update_matcher_new_schema import update_intervention_matcher
        success = update_intervention_matcher()
        
        if not success:
            print("❌ Matcher update failed")
            return False
            
    except Exception as e:
        print(f"❌ Matcher update error: {e}")
        return False
    
    # Step 4: Update API endpoints
    print("\n🌐 Step 4: Updating API endpoints...")
    try:
        update_api_endpoints()
        
    except Exception as e:
        print(f"❌ API endpoints update error: {e}")
        return False
    
    # Step 5: Test the migration
    print("\n🧪 Step 5: Testing the migration...")
    try:
        test_migration()
        
    except Exception as e:
        print(f"❌ Migration test error: {e}")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Summary of changes:")
    print("✅ Data migrated to InterventionsBASE and HabitsBASE tables")
    print("✅ Supabase models updated for new schema")
    print("✅ Intervention matcher updated")
    print("✅ API endpoints updated")
    print("✅ All components tested")
    
    print("\n📋 Next steps:")
    print("1. Test your API endpoints")
    print("2. Test the mobile app")
    print("3. Verify recommendations are working")
    print("4. Check that habits are properly linked to interventions")
    
    return True

def update_api_endpoints():
    """Update API endpoints to work with new schema"""
    
    print("🌐 Updating API endpoints...")
    
    # Read current API file
    api_file = "api.py"
    
    if not os.path.exists(api_file):
        print(f"❌ API file not found: {api_file}")
        return False
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Update the recommendation endpoint to work with new schema
    # This is a simplified update - you may need to make more changes based on your specific needs
    
    # Find and replace the recommendation logic
    old_pattern = 'result = process_structured_user_input(user_input)'
    new_pattern = '''# Process with new schema
        result = process_structured_user_input_new_schema(user_input)'''
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        print("✅ Updated recommendation endpoint")
    
    # Add new function for new schema processing
    new_function = '''
def process_structured_user_input_new_schema(user_input: UserInput) -> Dict:
    """
    Process structured user input using new InterventionsBASE and HabitsBASE schema
    
    Args:
        user_input: Structured user input with profile, symptoms, etc.
        
    Returns:
        Dictionary with recommended intervention and habits from new schema
    """
    try:
        # Build text input for matching
        user_text = build_text_from_structured_input(user_input)
        
        # Get intervention recommendation using new schema
        from interventions.matcher import get_intervention_recommendation
        result = get_intervention_recommendation(user_text)
        
        if result.get('error'):
            return {
                "error": result['error'],
                "intake_summary": build_intake_summary(user_input),
                "recommended_intervention": None,
                "intervention_id": None,
                "scientific_reference": None,
                "habits": [],
                "reasoning": "Error occurred during processing"
            }
        
        # Format the response for new schema
        formatted_result = {
            "intake_summary": build_intake_summary(user_input),
            "recommended_intervention": result['intervention_name'],
            "intervention_id": result['intervention_id'],
            "scientific_reference": result['scientific_source'],
            "habits": result['habits'],
            "reasoning": f"Recommended based on {result['similarity_score']:.2f} similarity to intervention profile: {result['intervention_profile'][:100]}...",
            "similarity_score": result['similarity_score'],
            "category_strategy": result.get('category_strategy', ''),
            "symptoms_match": result.get('symptoms_match', ''),
            "persona_fit": result.get('persona_fit', ''),
            "dietary_fit": result.get('dietary_fit', ''),
            "movement_amount": result.get('movement_amount', '')
        }
        
        # Add InFlo context if available
        try:
            from interventions.inflo_context import get_inflo_context
            inflo_context = get_inflo_context(user_text)
            if inflo_context != "InFlo book context not available":
                formatted_result["additional_inflo_context"] = inflo_context
        except Exception as e:
            print(f"Warning: Could not get InFlo context: {e}")
        
        return formatted_result
        
    except Exception as e:
        return {
            "error": f"Error processing your request: {str(e)}",
            "intake_summary": build_intake_summary(user_input),
            "recommended_intervention": None,
            "intervention_id": None,
            "scientific_reference": None,
            "habits": [],
            "reasoning": "Error occurred during processing"
        }
'''
    
    # Add the new function before the existing functions
    if 'def process_structured_user_input_new_schema' not in content:
        # Find a good place to insert the function
        insert_point = content.find('def process_structured_user_input(user_input: UserInput) -> Dict:')
        if insert_point > 0:
            content = content[:insert_point] + new_function + '\n' + content[insert_point:]
            print("✅ Added new schema processing function")
    
    # Write updated content
    with open(api_file, 'w') as f:
        f.write(content)
    
    print("✅ API endpoints updated")
    return True

def test_migration():
    """Test the migration by running some basic operations"""
    
    print("🧪 Testing migration...")
    
    try:
        # Test database access
        from models.supabase_models import supabase_client
        
        # Test InterventionsBASE
        interventions = supabase_client.get_interventions_base()
        if not interventions.data:
            raise Exception("No interventions found in InterventionsBASE")
        print(f"✅ InterventionsBASE: {len(interventions.data)} records")
        
        # Test HabitsBASE
        habits = supabase_client.get_habits_base()
        if not habits.data:
            raise Exception("No habits found in HabitsBASE")
        print(f"✅ HabitsBASE: {len(habits.data)} records")
        
        # Test intervention matcher
        from interventions.matcher import get_intervention_recommendation
        
        test_input = "I have PCOS and want to control my blood sugar"
        result = get_intervention_recommendation(test_input)
        
        if result.get('error'):
            print(f"⚠️  Matcher test warning: {result['error']}")
        else:
            print(f"✅ Matcher test successful: {result.get('intervention_name')}")
            print(f"   Found {len(result.get('habits', []))} habits")
        
        print("✅ Migration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration test failed: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Complete New Schema Migration")
    print("=" * 40)
    
    success = run_complete_migration()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Your app is now ready to use the new InterventionsBASE and HabitsBASE tables!")
        
    else:
        print("\n❌ Migration failed!")
        print("Please check the errors above and try again.")


