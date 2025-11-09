# Intake & Intervention Storage Issue Analysis

## Problem
Nothing is stored in Supabase after "starting journey" - no intervention periods or user_habits are created.

## Console Log Analysis

From the logs provided:
1. ✅ User is authenticated (`d8b8e28d-1b1c-4e5b-a350-205aee02aaf8`)
2. ✅ Session data is loaded with:
   - `intake_data` - exists
   - `current_intervention` - exists
   - `selected_habits: Array(4)` - 4 habits exist
3. ❌ **NO log showing "📤 Starting intervention period with request:"**
4. ❌ **NO API call to `/intervention-periods/start`**

## Root Cause Analysis

### Missing API Call
The console logs show that `handleInterventionSelected` in `AppNavigator.tsx` is **never being called**. This means:

1. **The period selection modal might not be completing properly**
   - User clicks "Start with this intervention" → `setShowPeriodSelection(true)`
   - `InterventionPeriodScreen` modal is shown
   - User selects period → `handlePeriodSelected` should call `onInterventionSelected`
   - But this callback chain might be broken

2. **OR user is navigating directly to main app**
   - User might be skipping the intervention selection flow
   - Session restoration loads old habits but no new intervention period is created

### Flow Breakdown

**Expected Flow:**
1. User completes intake → `/recommend` endpoint → stores intake, returns `intake_id`
2. User views recommendations → selects intervention
3. User clicks "Start with this intervention" → period selection modal
4. User selects period → `handlePeriodSelected` → `onInterventionSelected` → `handleInterventionSelected`
5. `handleInterventionSelected` → calls `/intervention-periods/start` API
6. Backend creates `intervention_periods` record and `user_habits` records

**Actual Flow (from logs):**
1. ✅ User logs in
2. ✅ Session data restored (has habits, intervention, intake_data)
3. ❌ **No intervention period creation API call**

## Potential Issues

### Issue 1: Period Selection Modal Not Completing
- The `InterventionPeriodScreen` modal might not be calling the callback
- Check if `onPeriodSelected` prop is properly passed to `InterventionPeriodScreen`

### Issue 2: Missing Intake ID
- `handleInterventionSelected` checks for `intake_id` and shows alert if missing
- But no alert was shown in logs, so `intake_id` might exist
- However, the API call still isn't being made

### Issue 3: Silent Failure
- The API call might be failing silently
- Error handling might be swallowing the error
- Need to check network tab for failed requests

## Solutions

### Solution 1: Add Comprehensive Logging
Add logging at every step of the flow to identify where it breaks:

```typescript
// In RecommendationsScreen.tsx
const handlePeriodSelected = (periodData) => {
  console.log('🎯 handlePeriodSelected called:', periodData);
  setShowPeriodSelection(false);
  if (onInterventionSelected) {
    console.log('✅ Calling onInterventionSelected callback');
    onInterventionSelected(periodData.intervention, {...});
  } else {
    console.error('❌ onInterventionSelected callback is missing!');
  }
};
```

### Solution 2: Verify Period Selection Modal
Check if `InterventionPeriodScreen` is properly receiving and calling the callback.

### Solution 3: Check Network Requests
Look for:
- Failed POST requests to `/intervention-periods/start`
- 401/403 errors (authentication issues)
- 400 errors (missing required fields)
- 500 errors (backend errors)

### Solution 4: Verify Intake Storage
Check if intake is actually being stored:
- Look for POST to `/recommend` endpoint
- Verify `intake_id` is returned and stored
- Check Supabase `intakes` table

## Next Steps

1. **Add logging** to trace the entire flow
2. **Check network tab** for API calls
3. **Verify Supabase** - check if intake exists but intervention_period doesn't
4. **Test the flow manually** - go through each step and verify callbacks

