#!/usr/bin/env python3
"""
Test script for intervention completion flow
Tests the event-driven completion system end-to-end
"""

import asyncio
import sys
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def test_completion_flow():
    """Test the complete intervention completion flow"""
    
    print("🧪 Testing Intervention Completion Flow\n")
    print("=" * 60)
    
    # Import services
    from models import supabase_client
    from services.intervention_service import intervention_service
    from services.event_bus import event_bus
    
    # Step 1: Find or create a test intervention period
    print("\n📋 Step 1: Finding test intervention period...")
    
    # Get a test user (or use a known user_id)
    test_user_id = None
    
    # Try to find an active intervention period
    try:
        periods_result = supabase_client.client.table('intervention_periods')\
            .select('id, user_id, intervention_name, status, selected_habits, start_date, end_date')\
            .eq('status', 'active')\
            .limit(1)\
            .execute()
        
        if periods_result.data and len(periods_result.data) > 0:
            test_period = periods_result.data[0]
            test_period_id = test_period['id']
            test_user_id = test_period['user_id']
            print(f"✅ Found active intervention period:")
            print(f"   Period ID: {test_period_id}")
            print(f"   User ID: {test_user_id}")
            print(f"   Intervention: {test_period.get('intervention_name', 'Unknown')}")
            print(f"   Habits: {len(test_period.get('selected_habits', []))} habits")
            print(f"   Start Date: {test_period.get('start_date')}")
            print(f"   End Date: {test_period.get('end_date')}")
        else:
            print("⚠️ No active intervention periods found")
            print("   Creating a test period...")
            
            # Create a test period
            test_user_id = input("Enter a test user_id (or press Enter to skip): ").strip()
            if not test_user_id:
                print("❌ Cannot create test period without user_id")
                return
            
            # Create test period
            test_period_data = {
                "user_id": test_user_id,
                "intake_id": str(uuid.uuid4()),
                "intervention_name": "Test Intervention",
                "selected_habits": ["Test Habit 1", "Test Habit 2"],
                "start_date": (date.today() - timedelta(days=30)).isoformat(),
                "end_date": date.today().isoformat(),
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            create_result = supabase_client.client.table('intervention_periods')\
                .insert(test_period_data)\
                .execute()
            
            if create_result.data:
                test_period_id = create_result.data[0]['id']
                print(f"✅ Created test period: {test_period_id}")
            else:
                print("❌ Failed to create test period")
                return
    except Exception as e:
        print(f"❌ Error finding/creating test period: {e}")
        return
    
    # Step 2: Check current state
    print("\n📊 Step 2: Checking current state...")
    
    # Check intervention period status
    period_check = supabase_client.client.table('intervention_periods')\
        .select('status, actual_end_date')\
        .eq('id', test_period_id)\
        .single()\
        .execute()
    
    print(f"   Period Status: {period_check.data.get('status')}")
    print(f"   Actual End Date: {period_check.data.get('actual_end_date') or 'Not set'}")
    
    # Check user_habits status
    habits_check = supabase_client.client.table('user_habits')\
        .select('habit_name, status')\
        .eq('user_id', test_user_id)\
        .in_('habit_name', test_period.get('selected_habits', []))\
        .execute()
    
    print(f"   User Habits Status:")
    for habit in (habits_check.data or []):
        print(f"     - {habit.get('habit_name')}: {habit.get('status')}")
    
    # Step 3: Complete the intervention period
    print("\n🎯 Step 3: Completing intervention period...")
    
    completion_result = intervention_service.complete_period(
        period_id=test_period_id,
        notes="Test completion from script",
        auto_completed=False
    )
    
    print(f"   Result: {completion_result.get('success')}")
    print(f"   Message: {completion_result.get('message')}")
    
    if not completion_result.get('success'):
        print(f"   ❌ Error: {completion_result.get('error')}")
        return
    
    # Step 4: Verify event results
    print("\n📡 Step 4: Verifying event listeners executed...")
    
    event_results = completion_result.get('event_results', [])
    print(f"   Total listeners executed: {len(event_results)}")
    
    for result in event_results:
        handler_name = result.get('handler', 'Unknown')
        success = result.get('success', False)
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {handler_name}: {'Success' if success else 'Failed'}")
        if not success:
            print(f"      Error: {result.get('error', 'Unknown error')}")
    
    # Step 5: Verify database updates
    print("\n🔍 Step 5: Verifying database updates...")
    
    # Check intervention_periods
    period_after = supabase_client.client.table('intervention_periods')\
        .select('status, actual_end_date, notes')\
        .eq('id', test_period_id)\
        .single()\
        .execute()
    
    period_data = period_after.data
    print(f"   Intervention Period:")
    print(f"     Status: {period_data.get('status')} {'✅' if period_data.get('status') == 'completed' else '❌'}")
    print(f"     Actual End Date: {period_data.get('actual_end_date') or 'Not set'} {'✅' if period_data.get('actual_end_date') else '❌'}")
    print(f"     Notes: {period_data.get('notes', 'None')}")
    
    # Check user_habits
    habits_after = supabase_client.client.table('user_habits')\
        .select('habit_name, status')\
        .eq('user_id', test_user_id)\
        .in_('habit_name', test_period.get('selected_habits', []))\
        .execute()
    
    print(f"   User Habits:")
    all_completed = True
    for habit in (habits_after.data or []):
        status = habit.get('status')
        is_completed = status == 'completed'
        all_completed = all_completed and is_completed
        print(f"     - {habit.get('habit_name')}: {status} {'✅' if is_completed else '❌'}")
    
    if all_completed and habits_after.data:
        print(f"   ✅ All habits marked as completed")
    elif habits_after.data:
        print(f"   ⚠️ Some habits not marked as completed")
    else:
        print(f"   ⚠️ No habits found to update")
    
    # Check completion_summaries
    print(f"   Completion Summary:")
    try:
        summary_result = supabase_client.client.table('completion_summaries')\
            .select('*')\
            .eq('intervention_period_id', test_period_id)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if summary_result.data:
            summary = summary_result.data[0]
            print(f"     ✅ Summary created:")
            print(f"       Adherence Rate: {summary.get('adherence_rate')}%")
            print(f"       Average Mood: {summary.get('average_mood')}")
            print(f"       Mood Trend: {summary.get('mood_trend')}")
        else:
            print(f"     ⚠️ No summary found (table may not exist)")
    except Exception as e:
        print(f"     ⚠️ Could not check summary: {e}")
    
    # Check notifications
    print(f"   Notification:")
    try:
        notif_result = supabase_client.client.table('notifications')\
            .select('*')\
            .eq('user_id', test_user_id)\
            .eq('type', 'intervention_completed')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if notif_result.data:
            notif = notif_result.data[0]
            print(f"     ✅ Notification created:")
            print(f"       Title: {notif.get('title')}")
            print(f"       Read: {notif.get('read')}")
        else:
            print(f"     ⚠️ No notification found (table may not exist)")
    except Exception as e:
        print(f"     ⚠️ Could not check notification: {e}")
    
    # Step 6: Test double completion prevention
    print("\n🛡️ Step 6: Testing double completion prevention...")
    
    double_result = intervention_service.complete_period(
        period_id=test_period_id,
        notes="Attempting to complete again"
    )
    
    if double_result.get('already_completed'):
        print(f"   ✅ Double completion prevented: {double_result.get('message')}")
    else:
        print(f"   ❌ Double completion not prevented!")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    checks = {
        "Period marked completed": period_data.get('status') == 'completed',
        "Actual end date set": period_data.get('actual_end_date') is not None,
        "Habits updated": all_completed if habits_after.data else False,
        "Events fired": len(event_results) >= 3,
        "Double completion prevented": double_result.get('already_completed', False)
    }
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {check_name}")
    
    all_passed = all(checks.values())
    print(f"\n{'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    import uuid
    result = asyncio.run(test_completion_flow())
    sys.exit(0 if result else 1)

